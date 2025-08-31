import { useState, useEffect } from "react";
import { Badge } from "@/components/ui/badge";
import { Button } from "@/components/ui/button";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Separator } from "@/components/ui/separator";
import { Eye, Camera, Calendar, MapPin, Settings, FileText, ExternalLink } from "lucide-react";
import { mediaApi, MediaItem } from "../services/api";

interface MetadataPanelProps {
  media: MediaItem;
}

interface FormattedMetadata {
  file_info: Record<string, string>;
  camera_info: Record<string, string>;
  capture_info: Record<string, string>;
  technical_info: Record<string, string>;
  gps_info: Record<string, string>;
  other_info: Record<string, string>;
}

export function MetadataPanel({ media }: MetadataPanelProps) {
  const [metadata, setMetadata] = useState<any>(null);
  const [formattedMetadata, setFormattedMetadata] = useState<FormattedMetadata | null>(null);
  const [summary, setSummary] = useState<string>("");
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    if (media) {
      loadMetadata();
    }
  }, [media]);

  const loadMetadata = async () => {
    if (!media.id) return;
    
    setIsLoading(true);
    setError(null);
    
    try {
      const result = await mediaApi.getMetadata(media.id);
      setMetadata(result.raw_metadata);
      setFormattedMetadata(result.formatted_metadata);
      setSummary(result.summary);
    } catch (error) {
      console.error('Failed to load metadata:', error);
      setError('Failed to load metadata');
    } finally {
      setIsLoading(false);
    }
  };

  const handleRefreshMetadata = async () => {
    if (!media.id) return;
    
    setIsLoading(true);
    setError(null);
    
    try {
      await mediaApi.refreshMetadata(media.id);
      // Reload metadata after refresh
      await loadMetadata();
    } catch (error) {
      console.error('Failed to refresh metadata:', error);
      setError('Failed to refresh metadata');
    } finally {
      setIsLoading(false);
    }
  };

  const renderMetadataSection = (
    title: string,
    data: Record<string, string>,
    icon: React.ReactNode
  ) => {
    if (!data || Object.keys(data).length === 0) return null;

    return (
      <Card className="mb-4">
        <CardHeader className="pb-2">
          <CardTitle className="text-sm font-semibold flex items-center gap-2">
            {icon}
            {title}
          </CardTitle>
        </CardHeader>
        <CardContent className="pt-0">
          <div className="space-y-2">
            {Object.entries(data).map(([key, value]) => (
              <div key={key} className="flex justify-between items-start text-xs">
                <span className="font-medium text-muted-foreground">{key}:</span>
                <span className="text-right max-w-[60%] break-words">
                  {key === 'Google Maps' ? (
                    <a 
                      href={value} 
                      target="_blank" 
                      rel="noopener noreferrer"
                      className="text-primary hover:underline flex items-center gap-1"
                    >
                      Open Map
                      <ExternalLink className="h-3 w-3" />
                    </a>
                  ) : (
                    value
                  )}
                </span>
              </div>
            ))}
          </div>
        </CardContent>
      </Card>
    );
  };

  if (isLoading) {
    return (
      <div className="flex items-center justify-center h-32">
        <div className="text-muted-foreground">Loading metadata...</div>
      </div>
    );
  }

  if (error) {
    return (
      <div className="flex flex-col items-center justify-center h-32 space-y-2">
        <div className="text-muted-foreground">{error}</div>
        <div className="flex gap-2">
          <Button variant="outline" size="sm" onClick={loadMetadata}>
            Retry
          </Button>
          <Button variant="outline" size="sm" onClick={handleRefreshMetadata}>
            Extract Metadata
          </Button>
        </div>
      </div>
    );
  }

  if (!formattedMetadata) {
    return (
      <div className="flex flex-col items-center justify-center h-32 space-y-2">
        <div className="text-muted-foreground">No metadata available</div>
        <div className="text-xs text-muted-foreground text-center">
          This image doesn't contain metadata or metadata extraction failed.
        </div>
        <Button variant="outline" size="sm" onClick={handleRefreshMetadata}>
          Extract Metadata
        </Button>
      </div>
    );
  }

  return (
    <div className="space-y-4">
      {/* Summary */}
      {summary && (
        <Card>
          <CardHeader className="pb-2">
            <CardTitle className="text-sm font-semibold flex items-center gap-2">
              <Eye className="h-4 w-4" />
              Summary
            </CardTitle>
          </CardHeader>
          <CardContent className="pt-0">
            <p className="text-sm text-muted-foreground">{summary}</p>
          </CardContent>
        </Card>
      )}

      {/* File Information */}
      {renderMetadataSection("File Information", formattedMetadata.file_info, <FileText className="h-4 w-4" />)}

      {/* Camera Information */}
      {renderMetadataSection("Camera Information", formattedMetadata.camera_info, <Camera className="h-4 w-4" />)}

      {/* Capture Information */}
      {renderMetadataSection("Capture Information", formattedMetadata.capture_info, <Calendar className="h-4 w-4" />)}

      {/* Technical Information */}
      {renderMetadataSection("Technical Information", formattedMetadata.technical_info, <Settings className="h-4 w-4" />)}

      {/* GPS Information */}
      {renderMetadataSection("GPS Information", formattedMetadata.gps_info, <MapPin className="h-4 w-4" />)}

      {/* Other Information */}
      {renderMetadataSection("Other Information", formattedMetadata.other_info, <FileText className="h-4 w-4" />)}
    </div>
  );
} 