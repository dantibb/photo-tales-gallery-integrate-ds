import { useState, useEffect } from "react";
import { Badge } from "@/components/ui/badge";
import { Card } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { mediaApi } from "../services/api";
import { MediaItem } from "../types/photo.types";
import { TagEditor } from "./TagEditor";
import { Tag, AlertCircle, FileX, Mic } from "lucide-react";

interface PhotoCardProps {
  media: MediaItem;
  onClick: () => void;
  size?: 'sm' | 'md' | 'lg' | 'xl';
  onTagsUpdated?: () => void;
  onFileMissing?: (mediaId: string) => void;
  onFileLoadError?: (mediaId: string) => void;
  onFileLoadSuccess?: (mediaId: string) => void;
}

export function PhotoCard({ media, onClick, size = 'sm', onTagsUpdated, onFileMissing, onFileLoadError, onFileLoadSuccess }: PhotoCardProps) {
  const [imageUrl, setImageUrl] = useState<string | null>(null);
  const [isLoading, setIsLoading] = useState(true);
  const [loadError, setLoadError] = useState(false);
  const [isHovered, setIsHovered] = useState(false);

  useEffect(() => {
    let isMounted = true;
    setImageUrl(null);
    setLoadError(false);
    
    // Check if this is a transcript placeholder (no media preview needed)
    const isTranscriptPlaceholder = media.metadata?.type === 'transcript_placeholder';
    
    if (isTranscriptPlaceholder) {
      // For transcripts, skip media preview loading
      if (isMounted) {
        setIsLoading(false);
        setLoadError(false);
        onFileLoadSuccess?.(media.id);
      }
      return;
    }
    
    const loadWithRetry = async (retries = 3, delay = 500) => {
      setIsLoading(true);
      for (let attempt = 1; attempt <= retries; attempt++) {
        try {
          const previewUrl = await mediaApi.getMediaPreview(media.id);
          if (isMounted) {
            setImageUrl(previewUrl);
            setIsLoading(false);
            setLoadError(false);
            onFileLoadSuccess?.(media.id);
          }
          return;
        } catch (error) {
          console.error(`Failed to load image for ${media.id}:`, error);
          if (attempt === retries) {
            if (isMounted) {
              setImageUrl(null);
              setIsLoading(false);
              setLoadError(true);
              onFileLoadError?.(media.id);
            }
          } else {
            await new Promise(res => setTimeout(res, delay));
          }
        }
      }
    };
    loadWithRetry();
    return () => { isMounted = false; };
  }, [media.id]);

  // Use tags from database or extract from description/filename
  const getTags = () => {
    if (media.tags && media.tags.length > 0) {
      return media.tags;
    }
    // Fallback: extract tags from description or filename
    const text = `${media.description || ''} ${media.filename || ''}`.toLowerCase();
    const words = text.split(/\s+/).filter(word => word.length > 2);
    return [...new Set(words)].slice(0, 5); // Limit to 5 unique tags
  };

  const tags = getTags();

  // Map size to minHeight and width for masonry effect
  const sizeStyles = {
    sm: { width: '100%' },
    md: { width: '100%' },
    lg: { width: '100%' },
    xl: { width: '100%' },
  };

  const handleFileMissing = () => {
    if (onFileMissing) {
      onFileMissing(media.id);
    }
  };

  return (
    <Card 
      className="group cursor-pointer overflow-hidden bg-gradient-card border-border/50 hover:border-primary/30 transition-all duration-300 hover:shadow-glow animate-fade-in"
      onClick={onClick}
      onMouseEnter={() => setIsHovered(true)}
      onMouseLeave={() => setIsHovered(false)}
      style={sizeStyles[size]}
    >
      <div className="relative aspect-[4/3] overflow-hidden">
        {/* Check if this is a transcript placeholder */}
        {media.metadata?.type === 'transcript_placeholder' ? (
          // Transcript card - show text content instead of image
          <div className="w-full h-full bg-gradient-to-br from-blue-50 to-indigo-100 dark:from-blue-950/50 dark:to-indigo-900/50 flex flex-col items-center justify-center p-4 text-center">
            <div className="w-12 h-12 bg-blue-500/20 rounded-full flex items-center justify-center mb-3">
              <Mic className="h-6 w-6 text-blue-600 dark:text-blue-400" />
            </div>
            <h3 className="font-semibold text-sm text-blue-900 dark:text-blue-100 mb-2 line-clamp-2">
              {media.title || media.description || 'Transcript'}
            </h3>
            <p className="text-xs text-blue-700 dark:text-blue-300 line-clamp-3">
              {media.metadata?.content_preview || 'Interview transcript'}
            </p>
          </div>
        ) : (
          // Regular media card
          <>
            {isLoading ? (
              <div className="w-full h-full bg-muted flex items-center justify-center">
                <div className="text-muted-foreground">Loading...</div>
              </div>
            ) : imageUrl ? (
              <img
                src={imageUrl}
                alt={media.filename}
                className="w-full h-full object-cover transition-transform duration-300 group-hover:scale-105"
                loading="lazy"
              />
            ) : loadError ? (
              <div className="w-full h-full bg-muted flex flex-col items-center justify-center p-4">
                <FileX className="h-8 w-8 text-muted-foreground mb-2" />
                <div className="text-muted-foreground text-sm text-center mb-2">
                  File not found
                </div>
                <div className="text-xs text-muted-foreground text-center mb-3">
                  {media.filename}
                </div>
                {onFileMissing && (
                  <Button 
                    variant="outline" 
                    size="sm" 
                    onClick={(e) => {
                      e.stopPropagation();
                      handleFileMissing();
                    }}
                    className="text-xs"
                  >
                    Remove from database
                  </Button>
                )}
              </div>
            ) : (
              <div className="w-full h-full bg-muted flex items-center justify-center">
                <div className="text-muted-foreground">No image</div>
              </div>
            )}
          </>
        )}

        {/* Tags overlay */}
        {tags.length > 0 && !loadError && (
          <div className="absolute top-2 left-2 flex flex-wrap gap-1 max-w-[calc(100%-1rem)]">
            {tags.slice(0, 3).map((tag, index) => (
              <Badge 
                key={index} 
                variant="secondary" 
                className="text-xs px-1.5 py-0.5 bg-black/50 text-white border-0"
              >
                {tag}
              </Badge>
            ))}
            {tags.length > 3 && (
              <Badge 
                variant="secondary" 
                className="text-xs px-1.5 py-0.5 bg-black/50 text-white border-0"
              >
                +{tags.length - 3}
              </Badge>
            )}
          </div>
        )}

        {/* Hover overlay */}
        {isHovered && !loadError && (
          <div className="absolute inset-0 bg-black/20 flex items-center justify-center opacity-0 group-hover:opacity-100 transition-opacity duration-200">
            <div className="bg-black/70 text-white px-3 py-1.5 rounded-md text-sm">
              Click to view
            </div>
          </div>
        )}
      </div>

      {/* Card footer */}
      <div className="p-3">
        <div className="flex items-center justify-between mb-2">
          <h3 className="font-medium text-sm truncate flex-1">
            {media.title || media.filename}
          </h3>
          <div className="opacity-0 group-hover:opacity-100 transition-opacity">
            <TagEditor 
              media={media} 
              onTagsUpdated={onTagsUpdated}
            />
          </div>
        </div>
        
        {media.summary && (
          <p className="text-xs text-muted-foreground line-clamp-2">
            {media.summary}
          </p>
        )}
      </div>
    </Card>
  );
}