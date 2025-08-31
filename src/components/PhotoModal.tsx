import { useState, useEffect } from "react";
import { Badge } from "@/components/ui/badge";
import { Button } from "@/components/ui/button";
import { Dialog, DialogContent, DialogHeader, DialogTitle, DialogDescription } from "@/components/ui/dialog";
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs";
import { Input } from "@/components/ui/input";
import { Textarea } from "@/components/ui/textarea";
import { X, Calendar, Eye, MessageCircle, FileText, Edit, Save, X as XIcon, Trash2, Sparkles } from "lucide-react";
import { mediaApi, MediaItem } from "../services/api";
import { AIInterview } from "./AIInterview";
import { ContextPanel } from "./ContextPanel";
import { MetadataPanel } from "./MetadataPanel";

interface PhotoModalProps {
  mediaId: string | null;
  isOpen: boolean;
  onClose: () => void;
}

export function PhotoModal({ mediaId, isOpen, onClose }: PhotoModalProps) {
  const [media, setMedia] = useState<MediaItem | null>(null);
  const [imageUrl, setImageUrl] = useState<string | null>(null);
  const [isLoading, setIsLoading] = useState(false);
  const [activeTab, setActiveTab] = useState("details");
  const [isEditing, setIsEditing] = useState(false);
  const [editTitle, setEditTitle] = useState("");
  const [editSummary, setEditSummary] = useState("");
  const [editTags, setEditTags] = useState("");
  const [aiMessages, setAiMessages] = useState<any[]>([]);

  useEffect(() => {
    if (mediaId && isOpen) {
      loadMedia();
    }
  }, [mediaId, isOpen]);

  const loadMedia = async () => {
    if (!mediaId) return;
    
    setIsLoading(true);
    try {
      const mediaData = await mediaApi.getMediaItem(mediaId);
      setMedia(mediaData);
      
      // Load image preview
      const previewUrl = await mediaApi.getMediaPreview(mediaId);
      setImageUrl(previewUrl);
    } catch (error) {
      console.error('Failed to load media:', error);
    } finally {
      setIsLoading(false);
    }
  };

  const handleContextUpdate = () => {
    // Refresh media data when context is updated
    loadMedia();
  };

  const handleSaveEdits = async () => {
    if (!media) return;
    
    try {
      // Save all changes
      await Promise.all([
        mediaApi.updateTitle(media.id, editTitle),
        mediaApi.updateSummary(media.id, editSummary),
        mediaApi.updateTags(media.id, editTags.split(',').map(tag => tag.trim()).filter(tag => tag.length > 0))
      ]);
      
      // Refresh media data
      await loadMedia();
      setIsEditing(false);
    } catch (error) {
      console.error('Failed to save edits:', error);
    }
  };

  const handleStartEdit = () => {
    if (!media) return;
    setEditTitle(media.title || media.filename);
    setEditSummary(media.summary || '');
    setEditTags(media.tags ? media.tags.join(', ') : '');
    setIsEditing(true);
  };

  const handleCancelEdit = () => {
    setIsEditing(false);
  };

  const handleClearAll = async () => {
    if (!media) return;
    
    const confirmed = confirm(
      "Are you sure you want to clear all title, tags, summary, and context for this photo? This action cannot be undone."
    );
    
    if (!confirmed) return;
    
    try {
      await mediaApi.clearAllData(media.id);
      // Refresh media data
      await loadMedia();
    } catch (error) {
      console.error('Failed to clear data:', error);
    }
  };

  const handleGenerateSummary = async () => {
    if (!media) return;
    
    try {
      // Generate summary using only user context and metadata (no AI chat messages)
      const result = await mediaApi.generateSummary(media.id);
      
      // Update the media data with the new summary
      await loadMedia();
      
      // Show success message or update UI
      console.log('Summary generated successfully:', result);
    } catch (error) {
      console.error('Failed to generate summary:', error);
    }
  };

  const handleGenerateTags = async () => {
    if (!media) return;
    
    try {
      const result = await mediaApi.generateTags(media.id);
      
      // Update the media data with the new tags
      await loadMedia();
      
      // Show success message or update UI
      console.log('Tags generated successfully:', result);
    } catch (error) {
      console.error('Failed to generate tags:', error);
    }
  };

  const getMetadataSummary = () => {
    if (!media.image_metadata) return null;
    
    const metadata = media.image_metadata;
    const summary = [];
    
    // Camera info
    if (metadata.exif_data?.Make) {
      const make = metadata.exif_data.Make;
      const model = metadata.exif_data.Model || '';
      summary.push(`${make} ${model}`.trim());
    }
    
    // Date
    for (const dateTag of ['DateTimeOriginal', 'DateTime', 'DateTimeDigitized']) {
      if (metadata.exif_data?.[dateTag]) {
        summary.push(metadata.exif_data[dateTag]);
        break;
      }
    }
    
    // Technical details
    if (metadata.exif_data?.ExposureTime) {
      summary.push(`Exposure: ${metadata.exif_data.ExposureTime}`);
    }
    
    if (metadata.exif_data?.FNumber) {
      summary.push(`f/${metadata.exif_data.FNumber}`);
    }
    
    if (metadata.exif_data?.ISOSpeedRatings) {
      summary.push(`ISO ${metadata.exif_data.ISOSpeedRatings}`);
    }
    
    // GPS
    if (metadata.gps_data && Object.keys(metadata.gps_data).length > 0) {
      summary.push('GPS Available');
    }
    
    return summary.length > 0 ? summary.join(' | ') : null;
  };

  if (!media) return null;

  return (
    <Dialog open={isOpen} onOpenChange={onClose}>
      <DialogContent className="max-w-[85vw] w-full max-h-[85vh] bg-card border-border/50 p-0 animate-scale-in">
        <div className="flex flex-col h-full">
          <DialogHeader className="flex-shrink-0 flex-row items-center justify-between p-6 pb-0">
            <DialogTitle className="text-2xl font-bold text-foreground pr-8">
              {media.title || media.filename}
            </DialogTitle>
            <DialogDescription className="sr-only">
              Photo details and editing interface
            </DialogDescription>
            <div className="flex items-center gap-2">
              {!isEditing && (
                <>
                  <Button
                    variant="ghost"
                    size="icon"
                    onClick={handleGenerateSummary}
                    className="h-8 w-8 hover:bg-primary hover:text-primary-foreground"
                    title="Generate AI Summary"
                  >
                    <Sparkles className="h-4 w-4" />
                  </Button>
                  <Button
                    variant="ghost"
                    size="icon"
                    onClick={handleClearAll}
                    className="h-8 w-8 hover:bg-destructive hover:text-destructive-foreground"
                    title="Clear all data"
                  >
                    <Trash2 className="h-4 w-4" />
                  </Button>
                  <Button
                    variant="ghost"
                    size="icon"
                    onClick={handleStartEdit}
                    className="h-8 w-8 hover:bg-secondary"
                  >
                    <Edit className="h-4 w-4" />
                  </Button>
                </>
              )}
              <Button
                variant="ghost"
                size="icon"
                onClick={onClose}
                className="h-8 w-8 hover:bg-secondary"
              >
                <X className="h-4 w-4" />
              </Button>
            </div>
          </DialogHeader>
          
          <div className="flex-1 flex flex-col lg:flex-row gap-4 p-4 min-h-0">
            <div className="flex-1 min-h-0 flex items-center justify-center bg-secondary/30 rounded-lg overflow-hidden">
              {isLoading ? (
                <div className="text-center text-muted-foreground">
                  Loading image...
                </div>
              ) : imageUrl ? (
                <div className="flex items-center justify-center w-full h-full p-2">
                  <img
                    src={imageUrl}
                    alt={media.filename}
                    className="max-w-full max-h-full object-contain"
                    style={{ 
                      maxHeight: '60vh',
                      maxWidth: 'calc(85vw - 500px)'
                    }}
                  />
                </div>
              ) : (
                <div className="text-center text-muted-foreground">
                  Failed to load image
                </div>
              )}
            </div>
            
            <div className="lg:w-80 xl:w-96 min-h-0 flex flex-col">
              <Tabs value={activeTab} onValueChange={setActiveTab} className="h-full flex flex-col">
                <TabsList className="flex-shrink-0 grid w-full grid-cols-4">
                  <TabsTrigger value="details" className="flex items-center gap-2">
                    <FileText className="h-4 w-4" />
                    Details
                  </TabsTrigger>
                  <TabsTrigger value="context" className="flex items-center gap-2">
                    <FileText className="h-4 w-4" />
                    Context
                  </TabsTrigger>
                  <TabsTrigger value="interview" className="flex items-center gap-2">
                    <MessageCircle className="h-4 w-4" />
                    AI Chat
                  </TabsTrigger>
                  <TabsTrigger value="metadata" className="flex items-center gap-2">
                    <Eye className="h-4 w-4" />
                    Metadata
                  </TabsTrigger>
                </TabsList>
                
                <div className="flex-1 min-h-0 overflow-hidden">
                  <TabsContent value="details" className="h-full mt-0">
                    <div className="h-full overflow-y-auto space-y-4 p-4">
                      {isEditing ? (
                        <>
                          <div>
                            <h3 className="text-sm font-semibold mb-1 text-foreground">Title</h3>
                            <Input
                              value={editTitle}
                              onChange={(e) => setEditTitle(e.target.value)}
                              placeholder="Enter title..."
                              className="w-full text-sm"
                            />
                          </div>
                          
                          <div>
                            <h3 className="text-sm font-semibold mb-1 text-foreground">Summary</h3>
                            <Textarea
                              value={editSummary}
                              onChange={(e) => setEditSummary(e.target.value)}
                              placeholder="Enter summary..."
                              className="w-full text-sm"
                              rows={4}
                            />
                          </div>
                          
                          <div>
                            <h3 className="text-lg font-semibold mb-2 text-foreground">Tags</h3>
                            <Input
                              value={editTags}
                              onChange={(e) => setEditTags(e.target.value)}
                              placeholder="Enter tags separated by commas..."
                              className="w-full"
                            />
                            <p className="text-xs text-muted-foreground mt-1">
                              Separate tags with commas (e.g., nature, landscape, sunset)
                            </p>
                          </div>
                          
                          <div className="flex gap-2 pt-4">
                            <Button onClick={handleSaveEdits} className="flex items-center gap-2">
                              <Save className="h-4 w-4" />
                              Save Changes
                            </Button>
                            <Button variant="outline" onClick={handleCancelEdit} className="flex items-center gap-2">
                              <XIcon className="h-4 w-4" />
                              Cancel
                            </Button>
                          </div>
                        </>
                      ) : (
                        <>
                          <div>
                            <h3 className="text-sm font-semibold mb-1 text-foreground">Title</h3>
                            <p className="text-muted-foreground text-xs leading-relaxed line-clamp-2">
                              {media.title || media.filename || "No title available"}
                            </p>
                          </div>
                          
                          <div>
                            <h3 className="text-sm font-semibold mb-1 text-foreground">Summary</h3>
                            <p className="text-muted-foreground text-xs leading-relaxed line-clamp-4">
                              {media.summary || "No summary available"}
                            </p>
                          </div>
                          
                          <div>
                            <div className="flex items-center justify-between mb-1">
                              <h3 className="text-sm font-semibold text-foreground">Tags</h3>
                              <Button
                                variant="ghost"
                                size="sm"
                                onClick={handleGenerateTags}
                                className="h-6 px-2 text-xs hover:bg-primary hover:text-primary-foreground"
                                title="Generate AI Tags"
                              >
                                <Sparkles className="h-3 w-3 mr-1" />
                                Generate
                              </Button>
                            </div>
                            <div className="flex flex-wrap gap-1">
                              {media.tags && media.tags.length > 0 ? (
                                media.tags.map((tag, index) => (
                                  <Badge key={index} variant="secondary" className="text-xs px-1 py-0">
                                    {tag}
                                  </Badge>
                                ))
                              ) : (
                                <p className="text-muted-foreground text-xs">No tags available</p>
                              )}
                            </div>
                          </div>
                        </>
                      )}
                      
                      <div>
                        <h3 className="text-sm font-semibold mb-1 text-foreground">File Information</h3>
                        <div className="space-y-1 text-xs text-muted-foreground">
                          <div className="flex items-center gap-1">
                            <FileText className="h-3 w-3" />
                            <span>{media.filename}</span>
                          </div>
                          <div className="flex items-center gap-1">
                            <Calendar className="h-3 w-3" />
                            <span>Created: {new Date(media.created_at).toLocaleDateString()}</span>
                          </div>
                          <div className="flex items-center gap-1">
                            <Calendar className="h-3 w-3" />
                            <span>Updated: {new Date(media.updated_at).toLocaleDateString()}</span>
                          </div>
                          {getMetadataSummary() && (
                            <div className="flex items-start gap-1 mt-2 pt-2 border-t border-border/50">
                              <Eye className="h-3 w-3 mt-0.5 flex-shrink-0" />
                              <span className="leading-relaxed">{getMetadataSummary()}</span>
                              <Button
                                variant="ghost"
                                size="sm"
                                onClick={() => setActiveTab("metadata")}
                                className="h-4 px-1 text-xs hover:bg-primary hover:text-primary-foreground ml-auto"
                                title="View full metadata"
                              >
                                View All
                              </Button>
                            </div>
                          )}
                        </div>
                      </div>
                    </div>
                  </TabsContent>
                  
                  <TabsContent value="context" className="h-full mt-0 overflow-hidden">
                    <div className="h-full overflow-y-auto">
                      <ContextPanel media={media} onUpdate={handleContextUpdate} />
                    </div>
                  </TabsContent>
                  
                  <TabsContent value="interview" className="h-full mt-0 overflow-hidden">
                    <div className="h-full overflow-y-auto">
                      <AIInterview 
                        media={media} 
                        onClose={() => setActiveTab("details")}
                        onSave={handleContextUpdate}
                        onMessagesChange={setAiMessages}
                      />
                    </div>
                  </TabsContent>
                  
                  <TabsContent value="metadata" className="h-full mt-0 overflow-hidden">
                    <div className="h-full overflow-y-auto p-4">
                      <MetadataPanel media={media} />
                    </div>
                  </TabsContent>
                </div>
              </Tabs>
            </div>
          </div>
        </div>
      </DialogContent>
    </Dialog>
  );
}