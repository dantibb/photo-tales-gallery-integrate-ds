import React, { useState, useEffect } from 'react';
import { Button } from './ui/button';
import { Textarea } from './ui/textarea';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from './ui/card';
import { ScrollArea } from './ui/scroll-area';
import { Badge } from './ui/badge';
import { Plus, Edit, Trash2, Save, X } from 'lucide-react';
import { contextsApi, Context, MediaItem } from '../services/api';

interface ContextPanelProps {
  media: MediaItem;
  onUpdate?: () => void;
}

export const ContextPanel: React.FC<ContextPanelProps> = ({ media, onUpdate }) => {
  const [contexts, setContexts] = useState<Context[]>([]);
  const [isLoading, setIsLoading] = useState(false);
  const [isAdding, setIsAdding] = useState(false);
  const [newContext, setNewContext] = useState('');
  const [editingId, setEditingId] = useState<string | null>(null);
  const [editText, setEditText] = useState('');

  useEffect(() => {
    loadContexts();
  }, [media.id]);

  const loadContexts = async () => {
    setIsLoading(true);
    try {
      const data = await contextsApi.getContexts(media.id);
      setContexts(data);
    } catch (error) {
      console.error('Failed to load contexts:', error);
    } finally {
      setIsLoading(false);
    }
  };

  const addContext = async () => {
    if (!newContext.trim()) return;

    setIsLoading(true);
    try {
      await contextsApi.addContext(media.id, newContext.trim());
      setNewContext('');
      setIsAdding(false);
      await loadContexts();
      onUpdate?.();
    } catch (error) {
      console.error('Failed to add context:', error);
    } finally {
      setIsLoading(false);
    }
  };

  const updateContext = async (contextId: string) => {
    if (!editText.trim()) return;

    setIsLoading(true);
    try {
      await contextsApi.updateContext(media.id, contextId, editText.trim());
      setEditingId(null);
      setEditText('');
      await loadContexts();
      onUpdate?.();
    } catch (error) {
      console.error('Failed to update context:', error);
    } finally {
      setIsLoading(false);
    }
  };

  const deleteContext = async (contextId: string) => {
    if (!confirm('Are you sure you want to delete this context?')) return;

    setIsLoading(true);
    try {
      await contextsApi.deleteContext(media.id, contextId);
      await loadContexts();
      onUpdate?.();
    } catch (error) {
      console.error('Failed to delete context:', error);
    } finally {
      setIsLoading(false);
    }
  };

  const startEdit = (context: Context) => {
    setEditingId(context.id);
    setEditText(context.text);
  };

  const cancelEdit = () => {
    setEditingId(null);
    setEditText('');
  };

  return (
    <Card>
      <CardHeader>
        <div className="flex items-center justify-between">
          <div>
            <CardTitle>Context & Notes</CardTitle>
            <CardDescription>
              Add context and notes about this image
            </CardDescription>
          </div>
          <Button
            size="sm"
            onClick={() => setIsAdding(true)}
            disabled={isLoading}
          >
            <Plus className="h-4 w-4 mr-1" />
            Add Context
          </Button>
        </div>
      </CardHeader>
      <CardContent>
        {isAdding && (
          <div className="mb-4 p-4 border rounded-lg">
            <Textarea
              value={newContext}
              onChange={(e) => setNewContext(e.target.value)}
              placeholder="Add context about this image..."
              className="mb-2"
              rows={3}
            />
            <div className="flex gap-2">
              <Button
                size="sm"
                onClick={addContext}
                disabled={isLoading || !newContext.trim()}
              >
                <Save className="h-4 w-4 mr-1" />
                Save
              </Button>
              <Button
                variant="outline"
                size="sm"
                onClick={() => {
                  setIsAdding(false);
                  setNewContext('');
                }}
                disabled={isLoading}
              >
                <X className="h-4 w-4 mr-1" />
                Cancel
              </Button>
            </div>
          </div>
        )}

        <ScrollArea className="h-64">
          {isLoading ? (
            <div className="text-center py-8 text-muted-foreground">
              Loading contexts...
            </div>
          ) : contexts.length === 0 ? (
            <div className="text-center py-8 text-muted-foreground">
              No contexts yet. Add some context to get started.
            </div>
          ) : (
            <div className="space-y-3">
              {contexts.map((context) => (
                <div key={context.id} className="border rounded-lg p-3">
                  {editingId === context.id ? (
                    <div>
                      <Textarea
                        value={editText}
                        onChange={(e) => setEditText(e.target.value)}
                        className="mb-2"
                        rows={3}
                      />
                      <div className="flex gap-2">
                        <Button
                          size="sm"
                          onClick={() => updateContext(context.id)}
                          disabled={isLoading || !editText.trim()}
                        >
                          <Save className="h-4 w-4 mr-1" />
                          Save
                        </Button>
                        <Button
                          variant="outline"
                          size="sm"
                          onClick={cancelEdit}
                          disabled={isLoading}
                        >
                          <X className="h-4 w-4 mr-1" />
                          Cancel
                        </Button>
                      </div>
                    </div>
                  ) : (
                    <div>
                      <div className="flex items-start justify-between mb-2">
                        <div className="flex items-center gap-2">
                          {context.context_type && (
                            <Badge variant="secondary" className="text-xs">
                              {context.context_type}
                            </Badge>
                          )}
                          <span className="text-xs text-muted-foreground">
                            {new Date(context.created_at).toLocaleDateString()}
                          </span>
                        </div>
                        <div className="flex gap-1">
                          <Button
                            variant="ghost"
                            size="sm"
                            onClick={() => startEdit(context)}
                            disabled={isLoading}
                          >
                            <Edit className="h-3 w-3" />
                          </Button>
                          <Button
                            variant="ghost"
                            size="sm"
                            onClick={() => deleteContext(context.id)}
                            disabled={isLoading}
                          >
                            <Trash2 className="h-3 w-3" />
                          </Button>
                        </div>
                      </div>
                      <div className="whitespace-pre-wrap text-sm">
                        {context.text}
                      </div>
                    </div>
                  )}
                </div>
              ))}
            </div>
          )}
        </ScrollArea>
      </CardContent>
    </Card>
  );
}; 