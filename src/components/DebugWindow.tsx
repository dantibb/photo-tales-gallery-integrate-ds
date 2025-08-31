import React, { useState, useEffect } from 'react';
import { Button } from './ui/button';
import { Card, CardContent, CardHeader, CardTitle } from './ui/card';
import { ScrollArea } from './ui/scroll-area';
import { Badge } from './ui/badge';
import { X, ChevronDown, ChevronUp, Copy, Trash2 } from 'lucide-react';

interface DebugEntry {
  id: string;
  timestamp: string;
  type: 'summary' | 'interview' | 'tagging' | 'tag-question';
  title: string;
  prompt: string;
  response?: string;
}

interface DebugWindowProps {
  isOpen: boolean;
  onClose: () => void;
}

export const DebugWindow: React.FC<DebugWindowProps> = ({ isOpen, onClose }) => {
  const [debugEntries, setDebugEntries] = useState<DebugEntry[]>([]);
  const [isCollapsed, setIsCollapsed] = useState(false);

  // Listen for debug messages from the backend
  useEffect(() => {
    const handleDebugMessage = (event: MessageEvent) => {
      if (event.data.type === 'debug_prompt') {
        const newEntry: DebugEntry = {
          id: Date.now().toString(),
          timestamp: new Date().toLocaleTimeString(),
          type: event.data.promptType || 'summary',
          title: event.data.title || 'OpenAI API Call',
          prompt: event.data.prompt || '',
          response: event.data.response
        };
        
        setDebugEntries(prev => [newEntry, ...prev.slice(0, 49)]); // Keep last 50 entries
      }
    };

    // Listen for debug data from API responses
    const originalFetch = window.fetch;
    window.fetch = async (...args) => {
      const response = await originalFetch(...args);
      
      // Clone the response to read it
      const clonedResponse = response.clone();
      
      try {
        const data = await clonedResponse.json();
        if (data.debug) {
          const newEntry: DebugEntry = {
            id: Date.now().toString(),
            timestamp: new Date().toLocaleTimeString(),
            type: data.debug.prompt_type || 'summary',
            title: `OpenAI API Call - ${(data.debug.prompt_type || 'summary').toUpperCase()}`,
            prompt: data.debug.prompt || '',
            response: data.debug.response || ''
          };
          
          setDebugEntries(prev => [newEntry, ...prev.slice(0, 49)]);
        }
      } catch (error) {
        // Not JSON or no debug data, continue normally
      }
      
      return response;
    };

    return () => {
      window.fetch = originalFetch;
    };
  }, []);

  const copyToClipboard = (text: string) => {
    navigator.clipboard.writeText(text);
  };

  const clearEntries = () => {
    setDebugEntries([]);
  };

  const getTypeColor = (type: string) => {
    switch (type) {
      case 'summary': return 'bg-blue-500';
      case 'interview': return 'bg-green-500';
      case 'tagging': return 'bg-purple-500';
      case 'tag-question': return 'bg-orange-500';
      default: return 'bg-gray-500';
    }
  };

  if (!isOpen) return null;

  return (
    <div className="fixed bottom-4 right-4 z-50 w-96">
      <Card className="shadow-lg border-2 border-dashed border-orange-300">
        <CardHeader className="pb-2">
          <div className="flex items-center justify-between">
            <CardTitle className="text-sm font-bold flex items-center gap-2">
              <span className="text-orange-600">🔍</span>
              Debug Window
              <Badge variant="secondary" className="text-xs">
                {debugEntries.length}
              </Badge>
            </CardTitle>
            <div className="flex items-center gap-1">
              <Button
                variant="ghost"
                size="sm"
                onClick={() => setIsCollapsed(!isCollapsed)}
                className="h-6 w-6 p-0"
              >
                {isCollapsed ? <ChevronUp className="h-3 w-3" /> : <ChevronDown className="h-3 w-3" />}
              </Button>
              <Button
                variant="ghost"
                size="sm"
                onClick={clearEntries}
                className="h-6 w-6 p-0 text-red-500 hover:text-red-700"
                title="Clear all entries"
              >
                <Trash2 className="h-3 w-3" />
              </Button>
              <Button
                variant="ghost"
                size="sm"
                onClick={onClose}
                className="h-6 w-6 p-0"
              >
                <X className="h-3 w-3" />
              </Button>
            </div>
          </div>
        </CardHeader>
        
        {!isCollapsed && (
          <CardContent className="pt-0">
            <ScrollArea className="h-64">
              <div className="space-y-2">
                {debugEntries.length === 0 ? (
                  <div className="text-center text-muted-foreground text-sm py-8">
                    No debug entries yet.
                    <br />
                    <span className="text-xs">AI calls will appear here...</span>
                  </div>
                ) : (
                  debugEntries.map((entry) => (
                    <div key={entry.id} className="border rounded-lg p-3 bg-muted/30">
                      <div className="flex items-center justify-between mb-2">
                        <div className="flex items-center gap-2">
                          <div className={`w-2 h-2 rounded-full ${getTypeColor(entry.type)}`} />
                          <span className="text-xs font-medium">{entry.title}</span>
                        </div>
                        <div className="flex items-center gap-1">
                          <span className="text-xs text-muted-foreground">{entry.timestamp}</span>
                          <Button
                            variant="ghost"
                            size="sm"
                            onClick={() => copyToClipboard(entry.prompt)}
                            className="h-5 w-5 p-0"
                            title="Copy prompt"
                          >
                            <Copy className="h-3 w-3" />
                          </Button>
                        </div>
                      </div>
                      
                      <div className="space-y-2">
                        <div>
                          <div className="text-xs font-semibold text-muted-foreground mb-1">PROMPT:</div>
                          <div className="text-xs bg-background border rounded p-2 font-mono whitespace-pre-wrap max-h-32 overflow-y-auto">
                            {entry.prompt}
                          </div>
                        </div>
                        
                        {entry.response && (
                          <div>
                            <div className="text-xs font-semibold text-muted-foreground mb-1">RESPONSE:</div>
                            <div className="text-xs bg-background border rounded p-2 font-mono whitespace-pre-wrap max-h-24 overflow-y-auto">
                              {entry.response}
                            </div>
                          </div>
                        )}
                      </div>
                    </div>
                  ))
                )}
              </div>
            </ScrollArea>
          </CardContent>
        )}
      </Card>
    </div>
  );
}; 