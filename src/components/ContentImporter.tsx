import React, { useState } from 'react';
import { Button } from './ui/button';
import { Input } from './ui/input';
import { Textarea } from './ui/textarea';
import { Label } from './ui/label';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from './ui/card';
import { Tabs, TabsContent, TabsList, TabsTrigger } from './ui/tabs';
import { Badge } from './ui/badge';
import { Loader2, Globe, FileText, CheckCircle, AlertCircle, ExternalLink } from 'lucide-react';
import { useToast } from '../hooks/use-toast';

interface ImportResult {
  id: string;
  title: string;
  url?: string;
  content_length: number;
  metadata: any;
  message: string;
}

interface ContentImporterProps {
  onContentImported?: () => void;
}

export function ContentImporter({ onContentImported }: ContentImporterProps) {
  const [activeTab, setActiveTab] = useState('website');
  const [isImporting, setIsImporting] = useState(false);
  const [importResult, setImportResult] = useState<ImportResult | null>(null);
  const [error, setError] = useState<string | null>(null);
  
  // Website import state
  const [websiteUrl, setWebsiteUrl] = useState('');
  const [customTitle, setCustomTitle] = useState('');
  
  // Transcript import state
  const [transcriptTitle, setTranscriptTitle] = useState('');
  const [transcriptContent, setTranscriptContent] = useState('');
  const [transcriptMetadata, setTranscriptMetadata] = useState({
    people: '',
    locations: '',
    date: '',
    tags: ''
  });
  
  const { toast } = useToast();

  const handleWebsiteImport = async () => {
    if (!websiteUrl.trim()) {
      setError('Please enter a website URL');
      return;
    }

    setIsImporting(true);
    setError(null);
    setImportResult(null);

    try {
      const response = await fetch('http://localhost:8080/api/website/import', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          url: websiteUrl.trim(),
          title: customTitle.trim() || undefined
        }),
      });

      const data = await response.json();

      if (response.ok) {
        setImportResult(data);
        toast({
          title: "Success!",
          description: data.message,
        });
        
        // Call callback to refresh content
        if (onContentImported) {
          onContentImported();
        }
        
        // Reset form
        setWebsiteUrl('');
        setCustomTitle('');
      } else {
        setError(data.error || 'Failed to import website');
        toast({
          title: "Error",
          description: data.error || 'Failed to import website',
          variant: "destructive",
        });
      }
    } catch (err) {
      setError('Network error occurred');
      toast({
        title: "Error",
        description: 'Network error occurred',
        variant: "destructive",
      });
    } finally {
      setIsImporting(false);
    }
  };

  const handleTranscriptAdd = async () => {
    if (!transcriptTitle.trim() || !transcriptContent.trim()) {
      setError('Please enter both title and content');
      return;
    }

    setIsImporting(true);
    setError(null);
    setImportResult(null);

    try {
      // Build metadata from form fields
      const metadata: any = {};
      if (transcriptMetadata.people) {
        metadata.people = transcriptMetadata.people.split(',').map(p => p.trim());
      }
      if (transcriptMetadata.locations) {
        metadata.locations = transcriptMetadata.locations.split(',').map(l => l.trim());
      }
      if (transcriptMetadata.date) {
        metadata.date = transcriptMetadata.date;
      }
      if (transcriptMetadata.tags) {
        metadata.tags = transcriptMetadata.tags.split(',').map(t => t.trim());
      }

      // Use the simplified content endpoint
      const response = await fetch('http://localhost:8080/api/content/add', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          title: transcriptTitle.trim(),
          content: transcriptContent.trim(),
          type: 'transcript', // Specify this is a transcript
          metadata
        }),
      });

      const data = await response.json();

      if (response.ok) {
        setImportResult(data);
        toast({
          title: "Success!",
          description: data.message,
        });
        
        // Call callback to refresh content
        if (onContentImported) {
          onContentImported();
        }
        
        // Reset form
        setTranscriptTitle('');
        setTranscriptContent('');
        setTranscriptMetadata({
          people: '',
          locations: '',
          date: '',
          tags: ''
        });
      } else {
        setError(data.error || 'Failed to add transcript');
        toast({
          title: "Error",
          description: data.error || 'Failed to add transcript',
          variant: "destructive",
        });
      }
    } catch (err) {
      setError('Network error occurred');
      toast({
        title: "Error",
        description: 'Network error occurred',
        variant: "destructive",
      });
    } finally {
      setIsImporting(false);
    }
  };

  const resetForm = () => {
    setImportResult(null);
    setError(null);
    setWebsiteUrl('');
    setCustomTitle('');
    setTranscriptTitle('');
    setTranscriptContent('');
    setTranscriptMetadata({
      people: '',
      locations: '',
      date: '',
      tags: ''
    });
  };

  return (
    <div className="max-w-4xl mx-auto p-6 space-y-6">
      <div className="text-center">
        <h1 className="text-3xl font-bold text-gray-900 mb-2">Content Importer</h1>
        <p className="text-gray-600">
          Import website content and add large text documents like interview transcripts
        </p>
      </div>

      <Tabs value={activeTab} onValueChange={setActiveTab} className="w-full">
        <TabsList className="grid w-full grid-cols-2">
          <TabsTrigger value="website" className="flex items-center gap-2">
            <Globe className="w-4 h-4" />
            Website Import
          </TabsTrigger>
          <TabsTrigger value="transcript" className="flex items-center gap-2">
            <FileText className="w-4 h-4" />
            Transcript
          </TabsTrigger>
        </TabsList>

        <TabsContent value="website" className="space-y-4">
          <Card>
            <CardHeader>
              <CardTitle className="flex items-center gap-2">
                <Globe className="w-5 h-5" />
                Import Website Content
              </CardTitle>
              <CardDescription>
                Enter a website URL to automatically extract and import its content
              </CardDescription>
            </CardHeader>
            <CardContent className="space-y-4">
              <div className="space-y-2">
                <Label htmlFor="website-url">Website URL *</Label>
                <Input
                  id="website-url"
                  type="url"
                  placeholder="https://example.com/article"
                  value={websiteUrl}
                  onChange={(e) => setWebsiteUrl(e.target.value)}
                  disabled={isImporting}
                />
              </div>
              
              <div className="space-y-2">
                <Label htmlFor="custom-title">Custom Title (Optional)</Label>
                <Input
                  id="custom-title"
                  placeholder="Leave empty to use website's title"
                  value={customTitle}
                  onChange={(e) => setCustomTitle(e.target.value)}
                  disabled={isImporting}
                />
              </div>

              <Button 
                onClick={handleWebsiteImport} 
                disabled={isImporting || !websiteUrl.trim()}
                className="w-full"
              >
                {isImporting ? (
                  <>
                    <Loader2 className="w-4 h-4 mr-2 animate-spin" />
                    Importing...
                  </>
                ) : (
                  <>
                    <Globe className="w-4 h-4 mr-2" />
                    Import Website
                  </>
                )}
              </Button>
            </CardContent>
          </Card>
        </TabsContent>

        <TabsContent value="transcript" className="space-y-4">
          <Card>
            <CardHeader>
              <CardTitle className="flex items-center gap-2">
                <FileText className="w-5 h-5" />
                Add Transcript
              </CardTitle>
              <CardDescription>
                Add a large text document like an interview transcript with metadata
              </CardDescription>
            </CardHeader>
            <CardContent className="space-y-4">
              <div className="space-y-2">
                <Label htmlFor="transcript-title">Title *</Label>
                <Input
                  id="transcript-title"
                  placeholder="e.g., Interview with John about Paris Trip"
                  value={transcriptTitle}
                  onChange={(e) => setTranscriptTitle(e.target.value)}
                  disabled={isImporting}
                />
              </div>

              <div className="space-y-2">
                <Label htmlFor="transcript-content">Content *</Label>
                <Textarea
                  id="transcript-content"
                  placeholder="Paste your transcript content here..."
                  value={transcriptContent}
                  onChange={(e) => setTranscriptContent(e.target.value)}
                  disabled={isImporting}
                  rows={10}
                  className="min-h-[200px]"
                />
                <div className="text-sm text-gray-500">
                  Content length: {transcriptContent.length} characters
                </div>
              </div>

              <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                <div className="space-y-2">
                  <Label htmlFor="people">People (comma-separated)</Label>
                  <Input
                    id="people"
                    placeholder="John, Sarah, Emma"
                    value={transcriptMetadata.people}
                    onChange={(e) => setTranscriptMetadata(prev => ({ ...prev, people: e.target.value }))}
                    disabled={isImporting}
                  />
                </div>

                <div className="space-y-2">
                  <Label htmlFor="locations">Locations (comma-separated)</Label>
                  <Input
                    id="locations"
                    placeholder="Paris, Eiffel Tower"
                    value={transcriptMetadata.locations}
                    onChange={(e) => setTranscriptMetadata(prev => ({ ...prev, locations: e.target.value }))}
                    disabled={isImporting}
                  />
                </div>

                <div className="space-y-2">
                  <Label htmlFor="date">Date</Label>
                  <Input
                    id="date"
                    type="date"
                    value={transcriptMetadata.date}
                    onChange={(e) => setTranscriptMetadata(prev => ({ ...prev, date: e.target.value }))}
                    disabled={isImporting}
                  />
                </div>

                <div className="space-y-2">
                  <Label htmlFor="tags">Tags (comma-separated)</Label>
                  <Input
                    id="tags"
                    placeholder="vacation, family, interview"
                    value={transcriptMetadata.tags}
                    onChange={(e) => setTranscriptMetadata(prev => ({ ...prev, tags: e.target.value }))}
                    disabled={isImporting}
                  />
                </div>
              </div>

              <Button 
                onClick={handleTranscriptAdd} 
                disabled={isImporting || !transcriptTitle.trim() || !transcriptContent.trim()}
                className="w-full"
              >
                {isImporting ? (
                  <>
                    <Loader2 className="w-4 h-4 mr-2 animate-spin" />
                    Adding...
                  </>
                ) : (
                  <>
                    <FileText className="w-4 h-4 mr-2" />
                    Add Transcript
                  </>
                )}
              </Button>
            </CardContent>
          </Card>
        </TabsContent>
      </Tabs>

      {/* Error Display */}
      {error && (
        <Card className="border-red-200 bg-red-50">
          <CardContent className="pt-6">
            <div className="flex items-center gap-2 text-red-700">
              <AlertCircle className="w-5 h-5" />
              <span className="font-medium">Error: {error}</span>
            </div>
          </CardContent>
        </Card>
      )}

      {/* Success Result Display */}
      {importResult && (
        <Card className="border-green-200 bg-green-50">
          <CardHeader>
            <CardTitle className="flex items-center gap-2 text-green-700">
              <CheckCircle className="w-5 h-5" />
              Import Successful!
            </CardTitle>
          </CardHeader>
          <CardContent className="space-y-4">
            <div className="space-y-2">
              <div className="flex items-center justify-between">
                <span className="font-medium">Title:</span>
                <span>{importResult.title}</span>
              </div>
              {importResult.url && (
                <div className="flex items-center justify-between">
                  <span className="font-medium">URL:</span>
                  <a 
                    href={importResult.url} 
                    target="_blank" 
                    rel="noopener noreferrer"
                    className="text-blue-600 hover:text-blue-800 flex items-center gap-1"
                  >
                    {importResult.url}
                    <ExternalLink className="w-3 h-3" />
                  </a>
                </div>
              )}
              <div className="flex items-center justify-between">
                <span className="font-medium">Content Length:</span>
                <span>{importResult.content_length.toLocaleString()} characters</span>
              </div>
              <div className="flex items-center justify-between">
                <span className="font-medium">Document ID:</span>
                <Badge variant="secondary" className="font-mono text-xs">
                  {importResult.id}
                </Badge>
              </div>
            </div>

            {Object.keys(importResult.metadata).length > 0 && (
              <div className="space-y-2">
                <span className="font-medium">Metadata:</span>
                <div className="bg-white p-3 rounded border">
                  <pre className="text-xs text-gray-700 overflow-x-auto">
                    {JSON.stringify(importResult.metadata, null, 2)}
                  </pre>
                </div>
              </div>
            )}

            <div className="flex gap-2">
              <Button onClick={resetForm} variant="outline" className="flex-1">
                Import Another
              </Button>
              <Button onClick={() => setImportResult(null)} variant="outline" className="flex-1">
                Close
              </Button>
            </div>
          </CardContent>
        </Card>
      )}
    </div>
  );
}

