import React, { useState, useRef } from 'react';
import { Button } from './ui/button';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from './ui/card';
import { Badge } from './ui/badge';
import { Progress } from './ui/progress';
import { ScrollArea } from './ui/scroll-area';
import { 
  Upload, 
  X, 
  MessageCircle, 
  CheckCircle, 
  AlertCircle, 
  Camera,
  Plus,
  Save
} from 'lucide-react';
import { mediaApi, MediaItem } from '../services/api';
import { AIInterview } from './AIInterview';

interface AddEventProps {
  onClose: () => void;
  onEventAdded?: () => void;
}

interface UploadedFile {
  file: File;
  preview: string;
  status: 'pending' | 'uploading' | 'uploaded' | 'error';
  mediaItem?: MediaItem;
  error?: string;
}

export const AddEvent: React.FC<AddEventProps> = ({ onClose, onEventAdded }) => {
  const [uploadedFiles, setUploadedFiles] = useState<UploadedFile[]>([]);
  const [isUploading, setIsUploading] = useState(false);
  const [uploadProgress, setUploadProgress] = useState(0);
  const [selectedMediaItem, setSelectedMediaItem] = useState<MediaItem | null>(null);
  const [showInterview, setShowInterview] = useState(false);
  const [interviewMessages, setInterviewMessages] = useState<any[]>([]);
  const fileInputRef = useRef<HTMLInputElement>(null);

  const handleFileSelect = (event: React.ChangeEvent<HTMLInputElement>) => {
    const files = Array.from(event.target.files || []);
    const imageFiles = files.filter(file => file.type.startsWith('image/'));
    
    const newUploadedFiles: UploadedFile[] = imageFiles.map(file => ({
      file,
      preview: URL.createObjectURL(file),
      status: 'pending'
    }));
    
    setUploadedFiles(prev => [...prev, ...newUploadedFiles]);
  };

  const handleUpload = async () => {
    if (uploadedFiles.length === 0) return;
    
    setIsUploading(true);
    setUploadProgress(0);
    
    try {
      const files = uploadedFiles.map(uf => uf.file);
      const result = await mediaApi.uploadMedia(files);
      
      // Update the uploaded files with their media items
      const updatedFiles = uploadedFiles.map((uploadedFile, index) => {
        const mediaItem = result.uploaded_items[index];
        return {
          ...uploadedFile,
          status: mediaItem ? 'uploaded' : 'error',
          mediaItem,
          error: mediaItem ? undefined : 'Failed to upload'
        };
      });
      
      setUploadedFiles(updatedFiles);
      setUploadProgress(100);
      
      // Auto-select the first uploaded item for interview
      const firstUploaded = updatedFiles.find(uf => uf.status === 'uploaded');
      if (firstUploaded?.mediaItem) {
        setSelectedMediaItem(firstUploaded.mediaItem);
        setShowInterview(true);
      }
      
    } catch (error) {
      console.error('Upload failed:', error);
      setUploadedFiles(prev => prev.map(uf => ({
        ...uf,
        status: 'error',
        error: 'Upload failed'
      })));
    } finally {
      setIsUploading(false);
    }
  };

  const removeFile = (index: number) => {
    setUploadedFiles(prev => {
      const newFiles = [...prev];
      const removedFile = newFiles[index];
      if (removedFile.preview) {
        URL.revokeObjectURL(removedFile.preview);
      }
      newFiles.splice(index, 1);
      return newFiles;
    });
  };

  const handleInterviewSave = () => {
    setShowInterview(false);
    setSelectedMediaItem(null);
    // Refresh the gallery
    onEventAdded?.();
  };

  const handleInterviewClose = () => {
    setShowInterview(false);
    setSelectedMediaItem(null);
  };

  const getStatusIcon = (status: UploadedFile['status']) => {
    switch (status) {
      case 'pending':
        return <Camera className="h-4 w-4 text-muted-foreground" />;
      case 'uploading':
        return <Upload className="h-4 w-4 text-blue-500 animate-pulse" />;
      case 'uploaded':
        return <CheckCircle className="h-4 w-4 text-green-500" />;
      case 'error':
        return <AlertCircle className="h-4 w-4 text-red-500" />;
    }
  };

  const getStatusText = (status: UploadedFile['status']) => {
    switch (status) {
      case 'pending':
        return 'Pending';
      case 'uploading':
        return 'Uploading...';
      case 'uploaded':
        return 'Uploaded';
      case 'error':
        return 'Error';
    }
  };

  const pendingFiles = uploadedFiles.filter(uf => uf.status === 'pending');
  const uploadedItems = uploadedFiles.filter(uf => uf.status === 'uploaded');

  return (
    <div className="fixed inset-0 bg-black/50 flex items-center justify-center z-50 p-4">
      <Card className="w-full max-w-4xl max-h-[90vh] overflow-hidden">
        <CardHeader>
          <div className="flex items-center justify-between">
            <div>
              <CardTitle className="flex items-center gap-2">
                <Plus className="h-5 w-5" />
                Add New Event
              </CardTitle>
              <CardDescription>
                Upload photos and gather context using AI interview
              </CardDescription>
            </div>
            <Button variant="outline" size="sm" onClick={onClose}>
              <X className="h-4 w-4" />
            </Button>
          </div>
        </CardHeader>
        
        <CardContent className="space-y-6">
          {!showInterview ? (
            <>
              {/* File Upload Section */}
              <div className="space-y-4">
                <div className="flex items-center justify-between">
                  <h3 className="text-lg font-semibold">Upload Photos</h3>
                  <Button
                    onClick={() => fileInputRef.current?.click()}
                    disabled={isUploading}
                    variant="outline"
                  >
                    <Upload className="h-4 w-4 mr-2" />
                    Select Photos
                  </Button>
                </div>
                
                <input
                  ref={fileInputRef}
                  type="file"
                  multiple
                  accept="image/*"
                  onChange={handleFileSelect}
                  className="hidden"
                />
                
                {uploadedFiles.length > 0 && (
                  <div className="space-y-4">
                    <div className="flex items-center justify-between">
                      <span className="text-sm text-muted-foreground">
                        {uploadedFiles.length} photo(s) selected
                      </span>
                      <Button
                        onClick={handleUpload}
                        disabled={isUploading || pendingFiles.length === 0}
                        className="ml-auto"
                      >
                        {isUploading ? 'Uploading...' : 'Upload Photos'}
                      </Button>
                    </div>
                    
                    {isUploading && (
                      <div className="space-y-2">
                        <div className="flex justify-between text-sm">
                          <span>Uploading photos...</span>
                          <span>{uploadProgress}%</span>
                        </div>
                        <Progress value={uploadProgress} />
                      </div>
                    )}
                    
                    <ScrollArea className="h-64">
                      <div className="grid grid-cols-2 md:grid-cols-3 lg:grid-cols-4 gap-4">
                        {uploadedFiles.map((uploadedFile, index) => (
                          <div
                            key={index}
                            className="relative group border rounded-lg overflow-hidden bg-muted"
                          >
                            <img
                              src={uploadedFile.preview}
                              alt={uploadedFile.file.name}
                              className="w-full h-32 object-cover"
                            />
                            <div className="absolute inset-0 bg-black/50 opacity-0 group-hover:opacity-100 transition-opacity flex items-center justify-center">
                              <Button
                                variant="destructive"
                                size="sm"
                                onClick={() => removeFile(index)}
                                className="h-8 w-8 p-0"
                              >
                                <X className="h-4 w-4" />
                              </Button>
                            </div>
                            <div className="p-2">
                              <div className="flex items-center gap-2 mb-1">
                                {getStatusIcon(uploadedFile.status)}
                                <Badge variant={uploadedFile.status === 'error' ? 'destructive' : 'secondary'}>
                                  {getStatusText(uploadedFile.status)}
                                </Badge>
                              </div>
                              <p className="text-xs text-muted-foreground truncate">
                                {uploadedFile.file.name}
                              </p>
                              {uploadedFile.error && (
                                <p className="text-xs text-red-500">
                                  {uploadedFile.error}
                                </p>
                              )}
                            </div>
                          </div>
                        ))}
                      </div>
                    </ScrollArea>
                  </div>
                )}
              </div>
              
              {/* Uploaded Items Section */}
              {uploadedItems.length > 0 && (
                <div className="space-y-4">
                  <div className="flex items-center justify-between">
                    <h3 className="text-lg font-semibold">Uploaded Photos</h3>
                    <Badge variant="secondary">
                      {uploadedItems.length} uploaded
                    </Badge>
                  </div>
                  
                  <div className="grid grid-cols-2 md:grid-cols-3 lg:grid-cols-4 gap-4">
                    {uploadedItems.map((uploadedFile, index) => (
                      <div
                        key={index}
                        className="relative group border rounded-lg overflow-hidden cursor-pointer hover:ring-2 hover:ring-primary transition-all"
                        onClick={() => {
                          if (uploadedFile.mediaItem) {
                            setSelectedMediaItem(uploadedFile.mediaItem);
                            setShowInterview(true);
                          }
                        }}
                      >
                        <img
                          src={uploadedFile.preview}
                          alt={uploadedFile.mediaItem?.filename || uploadedFile.file.name}
                          className="w-full h-32 object-cover"
                        />
                        <div className="absolute inset-0 bg-black/50 opacity-0 group-hover:opacity-100 transition-opacity flex items-center justify-center">
                          <Button variant="secondary" size="sm">
                            <MessageCircle className="h-4 w-4 mr-2" />
                            Add Context
                          </Button>
                        </div>
                        <div className="p-2">
                          <p className="text-xs text-muted-foreground truncate">
                            {uploadedFile.mediaItem?.filename || uploadedFile.file.name}
                          </p>
                        </div>
                      </div>
                    ))}
                  </div>
                  
                  <div className="flex justify-end gap-2">
                    <Button variant="outline" onClick={onClose}>
                      Done
                    </Button>
                    <Button onClick={() => onEventAdded?.()}>
                      <Save className="h-4 w-4 mr-2" />
                      Save Event
                    </Button>
                  </div>
                </div>
              )}
            </>
          ) : (
            /* AI Interview Section */
            <div className="space-y-4">
              <div className="flex items-center justify-between">
                <h3 className="text-lg font-semibold">Add Context with AI Interview</h3>
                <Button variant="outline" size="sm" onClick={handleInterviewClose}>
                  <X className="h-4 w-4" />
                </Button>
              </div>
              
              {selectedMediaItem && (
                <div className="flex gap-4">
                  <div className="w-32 h-32 flex-shrink-0">
                    <img
                      src={`http://localhost:5001/api/media/${selectedMediaItem.id}/preview`}
                      alt={selectedMediaItem.filename}
                      className="w-full h-full object-cover rounded-lg"
                    />
                  </div>
                  <div className="flex-1">
                    <AIInterview
                      media={selectedMediaItem}
                      onClose={handleInterviewClose}
                      onSave={handleInterviewSave}
                      onMessagesChange={setInterviewMessages}
                    />
                  </div>
                </div>
              )}
            </div>
          )}
        </CardContent>
      </Card>
    </div>
  );
};
