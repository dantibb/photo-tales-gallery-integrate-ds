import React, { useState, useRef, useEffect } from 'react';
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
  Save,
  Mic,
  MicOff,
  Volume2,
  Loader2,
  Clock
} from 'lucide-react';
import { mediaApi, MediaItem } from '../services/api';
import { AIInterview } from './AIInterview';
import { Input } from './ui/input';
import { Textarea } from './ui/textarea';
import { Label } from './ui/label';

interface AddMediaFileProps {
  onClose: () => void;
  onMediaFileAdded?: () => void;
}

interface UploadedFile {
  file: File;
  preview: string;
  status: 'pending' | 'uploading' | 'uploaded' | 'error';
  mediaItem?: MediaItem;
  error?: string;
}

interface MediaFileDetails {
  name: string;
  description: string;
}

export const AddMediaFile: React.FC<AddMediaFileProps> = ({ onClose, onMediaFileAdded }) => {
  const [uploadedFiles, setUploadedFiles] = useState<UploadedFile[]>([]);
  const [isUploading, setIsUploading] = useState(false);
  const [uploadProgress, setUploadProgress] = useState(0);
  const [selectedMediaItem, setSelectedMediaItem] = useState<MediaItem | null>(null);
  const [showInterview, setShowInterview] = useState(false);
  const [interviewMessages, setInterviewMessages] = useState<any[]>([]);
  const [mediaFileDetails, setMediaFileDetails] = useState<MediaFileDetails>({
    name: '',
    description: ''
  });
  const [isListening, setIsListening] = useState(false);
  const [isVoiceSupported, setIsVoiceSupported] = useState(false);
  const fileInputRef = useRef<HTMLInputElement>(null);
  const recognitionRef = useRef<any>(null);

  // Initialize speech recognition
  useEffect(() => {
    const SpeechRecognition = (window as any).SpeechRecognition || (window as any).webkitSpeechRecognition;
    if (SpeechRecognition) {
      setIsVoiceSupported(true);
      recognitionRef.current = new SpeechRecognition();
      recognitionRef.current.continuous = false;
      recognitionRef.current.interimResults = false;
      recognitionRef.current.lang = 'en-US';

      recognitionRef.current.onstart = () => {
        setIsListening(true);
      };

      recognitionRef.current.onend = () => {
        setIsListening(false);
      };

      recognitionRef.current.onresult = (event: any) => {
        const transcript = event.results[0][0].transcript;
        setMediaFileDetails(prev => ({
          ...prev,
          description: prev.description ? `${prev.description} ${transcript}` : transcript
        }));
      };

      recognitionRef.current.onerror = (event: any) => {
        console.error('Speech recognition error:', event.error);
        setIsListening(false);
      };
    }
  }, []);

  // Cleanup speech recognition on unmount
  useEffect(() => {
    return () => {
      if (recognitionRef.current) {
        recognitionRef.current.stop();
      }
    };
  }, []);

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
      const result = await mediaApi.uploadMedia(files, mediaFileDetails);
      
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
    const fileToRemove = uploadedFiles[index];
    if (fileToRemove.preview) {
      URL.revokeObjectURL(fileToRemove.preview);
    }
    setUploadedFiles(prev => prev.filter((_, i) => i !== index));
  };

  const startVoiceInput = () => {
    if (recognitionRef.current) {
      recognitionRef.current.start();
    }
  };

  const stopVoiceInput = () => {
    if (recognitionRef.current) {
      recognitionRef.current.stop();
    }
  };

  const handleInterviewClose = () => {
    setShowInterview(false);
    setSelectedMediaItem(null);
    if (onMediaFileAdded) {
      onMediaFileAdded();
    }
  };

  return (
    <div className="fixed inset-0 bg-black/50 flex items-center justify-center z-50">
      <Card className="w-full max-w-4xl max-h-[90vh] overflow-hidden">
        <CardHeader className="bg-gradient-to-r from-blue-600 to-purple-600 text-white">
          <div className="flex items-center justify-between">
            <div>
              <CardTitle className="text-2xl">Add Media File</CardTitle>
              <CardDescription className="text-blue-100">
                Upload photos and add context for your memories
              </CardDescription>
            </div>
            <Button
              variant="ghost"
              size="sm"
              onClick={onClose}
              className="text-white hover:bg-white/20"
            >
              <X className="h-5 w-5" />
            </Button>
          </div>
        </CardHeader>

        <CardContent className="p-6">
          <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
            {/* Left side - File upload */}
            <div className="space-y-4">
              <div>
                <Label htmlFor="media-file-name">Media File Name</Label>
                <Input
                  id="media-file-name"
                  placeholder="e.g., Beach Vacation 2023"
                  value={mediaFileDetails.name}
                  onChange={(e) => setMediaFileDetails(prev => ({ ...prev, name: e.target.value }))}
                />
              </div>

              <div>
                <Label htmlFor="media-file-description">Description</Label>
                <div className="relative">
                  <Textarea
                    id="media-file-description"
                    placeholder="Describe this media file, people, location, memories..."
                    value={mediaFileDetails.description}
                    onChange={(e) => setMediaFileDetails(prev => ({ ...prev, description: e.target.value }))}
                    rows={4}
                  />
                  {isVoiceSupported && (
                    <Button
                      type="button"
                      variant="ghost"
                      size="sm"
                      onClick={isListening ? stopVoiceInput : startVoiceInput}
                      className="absolute right-2 top-2 text-gray-500 hover:text-gray-700"
                    >
                      {isListening ? <MicOff className="h-4 w-4" /> : <Mic className="h-4 w-4" />}
                    </Button>
                  )}
                </div>
                {isListening && (
                  <div className="flex items-center gap-2 mt-2 text-sm text-blue-600">
                    <div className="w-2 h-2 bg-blue-600 rounded-full animate-pulse"></div>
                    Listening... Speak now
                  </div>
                )}
              </div>

              <div>
                <Label>Select Photos</Label>
                <div className="border-2 border-dashed border-gray-300 rounded-lg p-6 text-center hover:border-gray-400 transition-colors">
                  <input
                    ref={fileInputRef}
                    type="file"
                    multiple
                    accept="image/*"
                    onChange={handleFileSelect}
                    className="hidden"
                  />
                  <Button
                    variant="outline"
                    onClick={() => fileInputRef.current?.click()}
                    className="w-full"
                  >
                    <Camera className="h-4 w-4 mr-2" />
                    Choose Photos
                  </Button>
                  <p className="text-sm text-gray-500 mt-2">
                    Select one or more image files
                  </p>
                </div>
              </div>

              {uploadedFiles.length > 0 && (
                <div>
                  <Label>Selected Files ({uploadedFiles.length})</Label>
                  <ScrollArea className="h-32">
                    <div className="space-y-2">
                      {uploadedFiles.map((file, index) => (
                        <div key={index} className="flex items-center gap-2 p-2 border rounded">
                          <img
                            src={file.preview}
                            alt="Preview"
                            className="w-12 h-12 object-cover rounded"
                          />
                          <div className="flex-1 min-w-0">
                            <p className="text-sm font-medium truncate">{file.file.name}</p>
                            <p className="text-xs text-gray-500">
                              {(file.file.size / 1024 / 1024).toFixed(2)} MB
                            </p>
                          </div>
                          <Button
                            variant="ghost"
                            size="sm"
                            onClick={() => removeFile(index)}
                            className="text-red-500 hover:text-red-700"
                          >
                            <X className="h-4 w-4" />
                          </Button>
                        </div>
                      ))}
                    </div>
                  </ScrollArea>
                </div>
              )}

              <Button
                onClick={handleUpload}
                disabled={uploadedFiles.length === 0 || isUploading}
                className="w-full"
              >
                {isUploading ? (
                  <>
                    <Loader2 className="h-4 w-4 mr-2 animate-spin" />
                    Uploading...
                  </>
                ) : (
                  <>
                    <Upload className="h-4 w-4 mr-2" />
                    Upload Media Files
                  </>
                )}
              </Button>

              {isUploading && (
                <div className="space-y-2">
                  <div className="flex justify-between text-sm">
                    <span>Progress</span>
                    <span>{uploadProgress}%</span>
                  </div>
                  <Progress value={uploadProgress} />
                </div>
              )}
            </div>

            {/* Right side - Preview and status */}
            <div className="space-y-4">
              <div>
                <Label>Upload Status</Label>
                <div className="space-y-2">
                  {uploadedFiles.map((file, index) => (
                    <div key={index} className="flex items-center gap-2 p-2 border rounded">
                      <div className="w-8 h-8 rounded-full flex items-center justify-center">
                        {file.status === 'pending' && <Clock className="h-4 w-4 text-gray-400" />}
                        {file.status === 'uploading' && <Loader2 className="h-4 w-4 text-blue-500 animate-spin" />}
                        {file.status === 'uploaded' && <CheckCircle className="h-4 w-4 text-green-500" />}
                        {file.status === 'error' && <AlertCircle className="h-4 w-4 text-red-500" />}
                      </div>
                      <div className="flex-1 min-w-0">
                        <p className="text-sm font-medium truncate">{file.file.name}</p>
                        <p className="text-xs text-gray-500">
                          {file.status === 'uploaded' && file.mediaItem ? (
                            <span className="text-green-600">✓ Uploaded successfully</span>
                          ) : file.status === 'error' ? (
                            <span className="text-red-600">{file.error}</span>
                          ) : (
                            file.status
                          )}
                        </p>
                      </div>
                    </div>
                  ))}
                </div>
              </div>

              {uploadedFiles.some(f => f.status === 'uploaded') && (
                <div className="p-4 bg-green-50 border border-green-200 rounded-lg">
                  <div className="flex items-center gap-2 text-green-800">
                    <CheckCircle className="h-5 w-5" />
                    <span className="font-medium">Upload Complete!</span>
                  </div>
                  <p className="text-sm text-green-700 mt-1">
                    Your media files have been uploaded successfully. You can now start an AI interview to add more context.
                  </p>
                </div>
              )}
            </div>
          </div>
        </CardContent>
      </Card>

      {/* AI Interview Modal */}
      {showInterview && selectedMediaItem && (
        <AIInterview
          mediaItem={selectedMediaItem}
          onClose={handleInterviewClose}
          initialMessages={interviewMessages}
        />
      )}
    </div>
  );
};
