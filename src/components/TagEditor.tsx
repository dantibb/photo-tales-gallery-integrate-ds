import React, { useState } from 'react';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Badge } from '@/components/ui/badge';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Dialog, DialogContent, DialogHeader, DialogTitle, DialogTrigger, DialogDescription } from '@/components/ui/dialog';
import { X, Plus, Tag } from 'lucide-react';
import { mediaApi } from '../services/api';
import { MediaItem } from '../types/photo.types';

interface TagEditorProps {
  media: MediaItem;
  onTagsUpdated?: () => void;
}

export function TagEditor({ media, onTagsUpdated }: TagEditorProps) {
  const [isOpen, setIsOpen] = useState(false);
  const [newTag, setNewTag] = useState('');
  const [isLoading, setIsLoading] = useState(false);
  const [currentTags, setCurrentTags] = useState<string[]>(media.tags || []);

  const handleAddTag = async () => {
    if (!newTag.trim()) return;
    
    const tagToAdd = newTag.trim().toLowerCase();
    if (currentTags.includes(tagToAdd)) {
      setNewTag('');
      return;
    }

    setIsLoading(true);
    try {
      const updatedTags = [...currentTags, tagToAdd];
      await mediaApi.updateTags(media.id, updatedTags);
      setCurrentTags(updatedTags);
      setNewTag('');
      onTagsUpdated?.();
    } catch (error) {
      console.error('Failed to add tag:', error);
    } finally {
      setIsLoading(false);
    }
  };

  const handleRemoveTag = async (tagToRemove: string) => {
    setIsLoading(true);
    try {
      const updatedTags = currentTags.filter(tag => tag !== tagToRemove);
      await mediaApi.updateTags(media.id, updatedTags);
      setCurrentTags(updatedTags);
      onTagsUpdated?.();
    } catch (error) {
      console.error('Failed to remove tag:', error);
    } finally {
      setIsLoading(false);
    }
  };

  const handleKeyPress = (e: React.KeyboardEvent) => {
    if (e.key === 'Enter') {
      handleAddTag();
    }
  };

  return (
    <Dialog open={isOpen} onOpenChange={setIsOpen}>
      <DialogTrigger asChild>
        <Button variant="outline" size="sm" className="h-8 px-2">
          <Tag className="h-4 w-4 mr-1" />
          Edit Tags
        </Button>
      </DialogTrigger>
      <DialogContent className="sm:max-w-md">
        <DialogHeader>
          <DialogTitle>Edit Tags for {media.filename}</DialogTitle>
          <DialogDescription>
            Add or remove tags to help organize and find your photos.
          </DialogDescription>
        </DialogHeader>
        <div className="space-y-4">
          {/* Current Tags */}
          <div>
            <h4 className="text-sm font-medium mb-2">Current Tags</h4>
            <div className="flex flex-wrap gap-2">
              {currentTags.length === 0 ? (
                <p className="text-sm text-muted-foreground">No tags yet</p>
              ) : (
                currentTags.map((tag) => (
                  <Badge key={tag} variant="secondary" className="flex items-center gap-1">
                    {tag}
                    <button
                      onClick={() => handleRemoveTag(tag)}
                      disabled={isLoading}
                      className="ml-1 hover:text-destructive"
                    >
                      <X className="h-3 w-3" />
                    </button>
                  </Badge>
                ))
              )}
            </div>
          </div>

          {/* Add New Tag */}
          <div>
            <h4 className="text-sm font-medium mb-2">Add New Tag</h4>
            <div className="flex gap-2">
              <Input
                value={newTag}
                onChange={(e) => setNewTag(e.target.value)}
                onKeyPress={handleKeyPress}
                placeholder="Enter tag name..."
                disabled={isLoading}
                className="flex-1"
              />
              <Button
                onClick={handleAddTag}
                disabled={!newTag.trim() || isLoading}
                size="sm"
              >
                <Plus className="h-4 w-4" />
              </Button>
            </div>
          </div>

          {/* Quick Add Suggestions */}
          <div>
            <h4 className="text-sm font-medium mb-2">Quick Add</h4>
            <div className="flex flex-wrap gap-2">
              {['Family', 'Vacation', 'Work', 'Hobby', 'Travel', 'Food', 'Nature', 'City'].map((suggestion) => (
                <Button
                  key={suggestion}
                  variant="outline"
                  size="sm"
                  onClick={() => {
                    setNewTag(suggestion.toLowerCase());
                    handleAddTag();
                  }}
                  disabled={currentTags.includes(suggestion.toLowerCase()) || isLoading}
                >
                  {suggestion}
                </Button>
              ))}
            </div>
          </div>
        </div>
      </DialogContent>
    </Dialog>
  );
} 