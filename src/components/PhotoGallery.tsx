import { useState, useMemo, useEffect } from "react";
import { PhotoCard } from "./PhotoCard";
import { PhotoModal } from "./PhotoModal";
import { SearchBar } from "./SearchBar";
import { ThemeToggle } from "./ThemeToggle";
import { DebugWindow } from "./DebugWindow";
import { Button } from "@/components/ui/button";
import { Badge } from "@/components/ui/badge";
import { ScrollArea } from "@/components/ui/scroll-area";
import { Separator } from "@/components/ui/separator";
import { Card, CardContent } from "@/components/ui/card";
import { Textarea } from "@/components/ui/textarea";
import { Grid, LayoutGrid, RefreshCw, X, User, Sparkles, Loader2, Bug, BarChart2, ChevronLeft, ChevronRight, Mic, MoreVertical, MessageSquare, Send, Plus, Globe, FileText } from "lucide-react";
import { mediaApi, contextsApi } from "../services/api";
import { MediaItem } from "../types/photo.types";
import { AIInterview } from "./AIInterview";
import { AITextInterface } from "./AITextInterface";
import { EmbeddedTextChat } from "./EmbeddedTextChat";
import { AIInterfaceSelector, AIInterfaceMode, AIModel } from "./AIInterfaceSelector";
import { useToast } from "../hooks/use-toast";
import { DropdownMenu, DropdownMenuTrigger, DropdownMenuContent, DropdownMenuItem } from "@/components/ui/dropdown-menu";
import React, { useRef } from "react";
import { AnamAvatar } from "./AnamAvatar";
import { AddMediaFile } from "./AddMediaFile";
import { ContentImporter } from "./ContentImporter";

// TalkingHead component: simple SVG with animated mouth
const TalkingHead: React.FC = () => (
  <img src="/placeholder_avatar_man.png" alt="Avatar" width={60} height={60} style={{ borderRadius: '50%', objectFit: 'cover' }} />
);

export function PhotoGallery() {
  const [mediaItems, setMediaItems] = useState<MediaItem[]>([]);
  const [selectedMediaId, setSelectedMediaId] = useState<string | null>(null);
  const [isModalOpen, setIsModalOpen] = useState(false);
  const [viewMode, setViewMode] = useState<'grid' | 'masonry'>('grid');
  const [isLoading, setIsLoading] = useState(false);
  const [filters, setFilters] = useState({
    searchQuery: "",
    selectedTags: [],
  });
  
  // AI Photographer state
  const [aiSummary, setAiSummary] = useState<string>("");
  const [aiPhotoCount, setAiPhotoCount] = useState<number>(0);
  const [isGeneratingSummary, setIsGeneratingSummary] = useState(false);

  // Debug state
  const [isDebugOpen, setIsDebugOpen] = useState(false);

  // Interview state
  const [interviewMediaId, setInterviewMediaId] = useState<string | null>(null);
  const [aiInterfaceMode, setAiInterfaceMode] = useState<AIInterfaceMode>(() => {
    // Load saved preference from localStorage
    const saved = localStorage.getItem('ai-interface-mode');
    return (saved as AIInterfaceMode) || 'avatar';
  });
  const [aiModel, setAiModel] = useState<AIModel>(() => {
    // Load saved preference from localStorage
    const saved = localStorage.getItem('ai-model');
    return (saved as AIModel) || 'gpt-4o-mini';
  });

  // Dashboard state
  const [isDashboardOpen, setIsDashboardOpen] = useState(false);
  const [dashboardData, setDashboardData] = useState<{ tag: string; wordCount: number }[]>([]);
  const [isDashboardLoading, setIsDashboardLoading] = useState(false);

  // Debug logging for modal state
  useEffect(() => {
    console.log('🎭 Modal state changed:', { selectedMediaId, isModalOpen });
  }, [selectedMediaId, isModalOpen]);

  const { toast } = useToast();
  const [isGeneratingYearTags, setIsGeneratingYearTags] = useState(false);
  const [talking, setTalking] = useState(false);
  const [missingFiles, setMissingFiles] = useState<Set<string>>(new Set());
  const [showAddMediaFile, setShowAddMediaFile] = useState(false);
  const [showContentImporter, setShowContentImporter] = useState(false);
  const [enhancedSearchResults, setEnhancedSearchResults] = useState<any[]>([]);
  const [isEnhancedSearching, setIsEnhancedSearching] = useState(false);

  // Save AI interface mode preference
  const handleAiInterfaceModeChange = (mode: AIInterfaceMode) => {
    setAiInterfaceMode(mode);
    localStorage.setItem('ai-interface-mode', mode);
  };

  // Save AI model preference
  const handleAiModelChange = (model: AIModel) => {
    setAiModel(model);
    localStorage.setItem('ai-model', model);
  };

  // Enhanced search across all content types
  const performEnhancedSearch = async (query: string) => {
    if (!query.trim()) {
      setEnhancedSearchResults([]);
      return;
    }

    setIsEnhancedSearching(true);
    try {
              const response = await fetch('http://localhost:8080/api/documents/search', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          query: query.trim(),
          limit: 10
        }),
      });

      if (response.ok) {
        const data = await response.json();
        setEnhancedSearchResults(data.results || []);
      } else {
        setEnhancedSearchResults([]);
      }
    } catch (error) {
      console.error('Enhanced search failed:', error);
      setEnhancedSearchResults([]);
    } finally {
      setIsEnhancedSearching(false);
    }
  };

  useEffect(() => {
    console.log('Talking effect triggered:', { isGeneratingSummary, aiSummary: !!aiSummary });
    if (isGeneratingSummary || aiSummary) {
      // Keep talking active when generating OR when we have a summary
      console.log('Setting talking to true (generating or has summary)');
      setTalking(true);
    } else {
      console.log('Setting talking to false (no generation, no summary)');
      setTalking(false);
    }
  }, [aiSummary, isGeneratingSummary]);

  // Enhanced search effect
  useEffect(() => {
    const timeoutId = setTimeout(() => {
      performEnhancedSearch(filters.searchQuery);
    }, 300); // Debounce search

    return () => clearTimeout(timeoutId);
  }, [filters.searchQuery]);

  // Debug logging
  useEffect(() => {
    console.log('PhotoGallery state:', { 
      isGeneratingSummary, 
      aiSummary: !!aiSummary, 
      talking,
      selectedTags: filters.selectedTags 
    });
  }, [isGeneratingSummary, aiSummary, talking, filters.selectedTags]);

  // More detailed logging for talking state changes
  useEffect(() => {
    console.log('Talking state changed:', talking);
  }, [talking]);

  // Log when summary generation starts/stops
  useEffect(() => {
    console.log('Summary generation state changed:', isGeneratingSummary);
  }, [isGeneratingSummary]);

  const loadMediaItems = async () => {
    console.log('=== loadMediaItems called ===');
    setIsLoading(true);
    try {
      console.log('Loading media items...');
      console.log('Calling mediaApi.listMedia()...');
      const items = await mediaApi.listMedia();
      console.log('API response received:', items);
      console.log('Loaded media items:', items.length, items);
      setMediaItems(items);
      console.log('State updated with mediaItems:', items.length);
    } catch (error) {
      console.error('Failed to load media items:', error);
      console.error('Error details:', error);
      // Show error to user
      alert(`Failed to load photos: ${error}`);
    } finally {
      setIsLoading(false);
      console.log('Loading finished');
    }
  };

  // Load media items on initial mount
  useEffect(() => {
    loadMediaItems();
  }, []);

  // When switching to masonry mode, fetch contexts for all visible media items
  useEffect(() => {
    if (viewMode !== 'masonry' || mediaItems.length === 0) return;
    // Only fetch if not already present
    const itemsNeedingContexts = mediaItems.filter(item => !item.contexts);
    if (itemsNeedingContexts.length === 0) return;
    Promise.all(
      itemsNeedingContexts.map(async (item) => {
        try {
          const contexts = await contextsApi.getContexts(item.id);
          return { ...item, contexts };
        } catch {
          return { ...item, contexts: [] };
        }
      })
    ).then((updatedItems) => {
      // Merge updated items into mediaItems
      setMediaItems((prev) =>
        prev.map((item) => {
          const updated = updatedItems.find((u) => u.id === item.id);
          return updated ? updated : item;
        })
      );
    });
  }, [viewMode, mediaItems]);

  // Generate AI summary when tags change
  useEffect(() => {
    console.log('Tags changed, selectedTags:', filters.selectedTags);
    if (filters.selectedTags.length === 1) {
      // Only generate summary for single tag selection
      console.log('Generating summary for tag:', filters.selectedTags[0]);
      generateAISummary(filters.selectedTags[0]);
    } else {
      // Clear summary when no tags or multiple tags selected
      console.log('Clearing summary - no tags or multiple tags selected');
      setAiSummary("");
      setAiPhotoCount(0);
    }
  }, [filters.selectedTags]);

  // Dashboard logic: fetch and aggregate context word counts by tag
  const loadDashboardData = async () => {
    setIsDashboardLoading(true);
    try {
      const items = await mediaApi.listMedia();
      // Map: tag -> total word count
      const tagWordCounts: Record<string, number> = {};
      // For each media item, fetch its contexts
      await Promise.all(
        items.map(async (item) => {
          const tags = item.tags || [];
          if (tags.length === 0) return;
          let contexts = item.contexts;
          if (!contexts) {
            try {
              contexts = await contextsApi.getContexts(item.id);
            } catch {
              contexts = [];
            }
          }
          const totalWords = (contexts || []).reduce((sum, ctx) => sum + (ctx.text?.split(/\s+/).length || 0), 0);
          tags.forEach(tag => {
            tagWordCounts[tag] = (tagWordCounts[tag] || 0) + totalWords;
          });
        })
      );
      // Convert to array and sort descending
      const data = Object.entries(tagWordCounts)
        .map(([tag, wordCount]) => ({ tag, wordCount }))
        .sort((a, b) => b.wordCount - a.wordCount);
      setDashboardData(data);
    } finally {
      setIsDashboardLoading(false);
    }
  };

  const generateAISummary = async (tag: string) => {
    console.log('generateAISummary called with tag:', tag);
    setIsGeneratingSummary(true);
    setAiSummary("");
    try {
      console.log('Calling mediaApi.generatePhotographerSummary...');
      const result = await mediaApi.generatePhotographerSummary(tag);
      console.log('Summary result:', result);
      setAiSummary(result.summary);
      setAiPhotoCount(result.photo_count);
    } catch (error) {
      console.error('Failed to generate AI summary:', error);
      setAiSummary("Sorry, I couldn't generate a summary for this tag.");
    } finally {
      console.log('Setting isGeneratingSummary to false');
      setIsGeneratingSummary(false);
    }
  };

  const allTags = useMemo(() => {
    const tagCounts = new Map<string, number>();
    mediaItems.forEach(item => {
      if (item.tags && Array.isArray(item.tags)) {
        item.tags.forEach(tag => {
          tagCounts.set(tag, (tagCounts.get(tag) || 0) + 1);
        });
      }
    });
    return Array.from(tagCounts.entries())
      .sort((a, b) => b[1] - a[1]) // Sort by count descending
      .map(([tag]) => tag);
  }, [mediaItems]);

  const filteredMedia = useMemo(() => {
    const filtered = mediaItems.filter(item => {
      const matchesSearch = filters.searchQuery === "" || 
        item.filename.toLowerCase().includes(filters.searchQuery.toLowerCase()) ||
        (item.description?.toLowerCase().includes(filters.searchQuery.toLowerCase())) ||
        (item.title && item.title.toLowerCase().includes(filters.searchQuery.toLowerCase()));
      
      const matchesTags = filters.selectedTags.length === 0 ||
        filters.selectedTags.some(tag => {
          return item.tags && item.tags.includes(tag);
        });
      
      return matchesSearch && matchesTags;
    });

    // Sort so that missing files appear at the bottom
    return filtered.sort((a, b) => {
      const aMissing = missingFiles.has(a.id);
      const bMissing = missingFiles.has(b.id);
      
      if (aMissing && !bMissing) return 1;  // a goes to bottom
      if (!aMissing && bMissing) return -1; // b goes to bottom
      return 0; // keep original order for both missing or both present
    });
  }, [mediaItems, filters, missingFiles]);

  const handleMediaClick = (mediaId: string) => {
    console.log('🖱️ PhotoCard clicked!', { mediaId });
    setSelectedMediaId(mediaId);
    setIsModalOpen(true);
    console.log('📊 Modal state set:', { selectedMediaId: mediaId, isModalOpen: true });
  };

  const handleMemoryToggle = (tag: string) => {
    setFilters(prev => ({
      ...prev,
      selectedTags: prev.selectedTags.includes(tag)
        ? [] // Deselect if already selected
        : [tag] // Select only this memory (single selection)
    }));
  };

  // Handler to delete a tag from all media items
  const handleDeleteTag = async (tagToDelete: string) => {
    if (!window.confirm(`Delete the tag '${tagToDelete}' from all photos?`)) return;
    // Find all media items with this tag
    const itemsWithTag = mediaItems.filter(item => item.tags && item.tags.includes(tagToDelete));
    await Promise.all(
      itemsWithTag.map(async (item) => {
        const newTags = (item.tags || []).filter(tag => tag !== tagToDelete);
        await mediaApi.updateTags(item.id, newTags);
      })
    );
    // Reload media items to reflect changes
    await loadMediaItems();
  };

  // Handler for generating year tags
  const handleGenerateYearTags = async () => {
    setIsGeneratingYearTags(true);
    try {
      const result = await mediaApi.generateYearTags();
      toast({
        title: "Year Tags Generated",
        description: result.message,
        variant: "default",
      });
      // Optionally reload media items to reflect new tags
      await loadMediaItems();
    } catch (error: any) {
      toast({
        title: "Failed to generate year tags",
        description: error?.message || String(error),
        variant: "destructive",
      });
    } finally {
      setIsGeneratingYearTags(false);
    }
  };

  // Handler for missing files
  const handleFileMissing = async (mediaId: string) => {
    try {
      await mediaApi.deleteMediaItem(mediaId);
      toast({
        title: "File removed",
        description: "Missing file has been removed from the database",
      });
      await loadMediaItems(); // Refresh the list
    } catch (error) {
      console.error('Failed to delete missing file:', error);
      toast({
        title: "Error",
        description: "Failed to remove missing file from database",
        variant: "destructive",
      });
    }
  };

  const handleCleanupMissingFiles = async () => {
    try {
      const result = await mediaApi.cleanupMissingFiles();
      toast({
        title: "Cleanup completed",
        description: `Removed ${result.deleted_count} missing files from database`,
      });
      await loadMediaItems(); // Refresh the list
    } catch (error) {
      console.error('Failed to cleanup missing files:', error);
      toast({
        title: "Error",
        description: "Failed to cleanup missing files",
        variant: "destructive",
      });
    }
  };

  const handleFileLoadError = (mediaId: string) => {
    setMissingFiles(prev => new Set([...prev, mediaId]));
  };

  const handleFileLoadSuccess = (mediaId: string) => {
    setMissingFiles(prev => {
      const newSet = new Set(prev);
      newSet.delete(mediaId);
      return newSet;
    });
  };

  const gridClasses = viewMode === 'masonry'
    ? (filters.selectedTags.length > 0
        ? "columns-1 sm:columns-2 md:columns-3 lg:columns-4 xl:columns-4 gap-4 space-y-4"
        : "columns-1 sm:columns-2 lg:columns-2 xl:columns-2 gap-4 space-y-4")
    : (filters.selectedTags.length > 0
        ? "grid grid-cols-1 sm:grid-cols-2 md:grid-cols-3 lg:grid-cols-4 xl:grid-cols-4 gap-6"
        : "grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-2 xl:grid-cols-2 gap-6");

  // Add a helper to map word count to size class
  function getSizeClass(wordCount: number): 'sm' | 'md' | 'lg' | 'xl' {
    if (wordCount > 100) return 'xl';
    if (wordCount > 50) return 'lg';
    if (wordCount > 20) return 'md';
    return 'sm';
  }

  // Add this debug section right before the return statement
  console.log('=== RENDERING ===');
  console.log('mediaItems state:', mediaItems);
  console.log('mediaItems length:', mediaItems.length);
  console.log('isLoading:', isLoading);
  console.log('selectedMediaId:', selectedMediaId);

  return (
    <div className="min-h-screen bg-background flex">
      {/* Left Sidebar */}
      <div className="w-80 bg-muted/30 flex flex-col relative">
        {/* Sidebar Header */}
        <div className="p-6 border-b flex items-center justify-between">
          <div className="flex items-center gap-2">
            <img src="/iMirrorlogo.png" alt="iMirror logo" style={{ height: 120, width: 120, objectFit: 'contain', border: 'none' }} />
            <div style={{ width: 24 }} />
            <ThemeToggle />
          </div>
          <Button
            variant="ghost"
            size="icon"
            className="ml-2"
            title={isDashboardOpen ? 'Hide Dashboard' : 'Show Dashboard'}
            onClick={() => {
              setIsDashboardOpen((open) => {
                if (!open) loadDashboardData();
                return !open;
              });
            }}
          >
            {isDashboardOpen ? <ChevronLeft className="h-5 w-5" /> : <BarChart2 className="h-5 w-5" />}
          </Button>
        </div>
        {/* Dashboard Sidebar Panel */}
        {isDashboardOpen && (
          <div className="absolute top-0 left-80 z-30 h-full w-80 bg-white border-l shadow-lg flex flex-col animate-fade-in">
            <div className="flex items-center justify-between p-4 border-b">
              <h2 className="text-lg font-bold flex items-center gap-2">
                <BarChart2 className="h-5 w-5 text-primary" />
                Tag Context Word Count
              </h2>
              <Button
                variant="ghost"
                size="icon"
                onClick={() => setIsDashboardOpen(false)}
                title="Minimize Dashboard"
              >
                <ChevronRight className="h-5 w-5" />
              </Button>
            </div>
            <div className="flex-1 overflow-y-auto p-4">
              {isDashboardLoading ? (
                <div className="flex items-center justify-center h-32 text-muted-foreground">
                  <Loader2 className="h-6 w-6 animate-spin mr-2" /> Loading...
                </div>
              ) : dashboardData.length === 0 ? (
                <div className="text-muted-foreground text-center">No tag data available.</div>
              ) : (
                <table className="w-full text-sm">
                  <thead>
                    <tr className="border-b">
                      <th className="text-left py-1">Tag</th>
                      <th className="text-right py-1">Context Words</th>
                    </tr>
                  </thead>
                  <tbody>
                    {dashboardData.map(({ tag, wordCount }) => (
                      <tr key={tag} className="border-b last:border-b-0">
                        <td className="py-1 pr-2">{tag}</td>
                        <td className="py-1 text-right font-mono">{wordCount}</td>
                      </tr>
                    ))}
                  </tbody>
                </table>
              )}
            </div>
          </div>
        )}
        {/* Search Bar */}
        <div className="p-6 border-b">
          <SearchBar
            value={filters.searchQuery}
            onChange={(value) => setFilters(prev => ({ ...prev, searchQuery: value }))}
          />
          
          {/* Enhanced Search Results */}
          {filters.searchQuery && enhancedSearchResults.length > 0 && (
            <div className="mt-4 p-4 bg-blue-50 dark:bg-blue-950/20 rounded-lg border">
              <h3 className="text-sm font-medium text-blue-900 dark:text-blue-100 mb-3 flex items-center gap-2">
                <FileText className="h-4 w-4" />
                Found {enhancedSearchResults.length} related documents
              </h3>
              <div className="space-y-2">
                {enhancedSearchResults.map((doc, index) => (
                  <div key={doc.id} className="p-3 bg-white dark:bg-gray-800 rounded border">
                    <div className="flex items-start justify-between">
                      <div className="flex-1">
                        <h4 className="font-medium text-sm">{doc.title}</h4>
                        <p className="text-xs text-muted-foreground mt-1">
                          Type: {doc.type} • {doc.content.length} characters
                        </p>
                        <p className="text-xs text-muted-foreground mt-1">
                          {doc.content.substring(0, 150)}...
                        </p>
                      </div>
                      <Badge variant="secondary" className="text-xs">
                        {doc.type}
                      </Badge>
                    </div>
                  </div>
                ))}
              </div>
            </div>
          )}
        </div>

        {/* Tags Section */}
        <div className="flex-1 overflow-hidden">
          <div className="p-6">
            <div className="flex items-center justify-between mb-4">
              <h3 className="font-semibold text-sm">Memories</h3>
              {filters.selectedTags.length > 0 && (
                <Button
                  variant="ghost"
                  size="sm"
                  onClick={() => setFilters(prev => ({ ...prev, selectedTags: [] }))}
                  className="h-6 px-2 text-xs"
                >
                  Clear all
                </Button>
              )}
            </div>

            {/* Selected Memory */}
            {filters.selectedTags.length > 0 && (
              <div className="mb-4">
                <div className="flex flex-wrap gap-2">
                  {filters.selectedTags.map(tag => (
                    <Badge
                      key={tag}
                      variant="secondary"
                      className="flex items-center gap-1 cursor-pointer hover:bg-destructive hover:text-destructive-foreground"
                      onClick={() => handleMemoryToggle(tag)}
                    >
                      {tag}
                      <X className="h-3 w-3" />
                    </Badge>
                  ))}
                </div>
                <Separator className="my-4" />
              </div>
            )}

            {/* All Memories */}
            <ScrollArea className="h-[calc(100vh-400px)]">
              <div className="space-y-2">
                {allTags.map(tag => (
                  <div
                    key={tag}
                    className={`flex items-center justify-between p-2 rounded-md cursor-pointer transition-colors ${
                      filters.selectedTags.includes(tag)
                        ? 'bg-primary text-primary-foreground'
                        : 'hover:bg-muted'
                    }`}
                    onClick={() => handleMemoryToggle(tag)}
                  >
                    <span className="text-sm">{tag}</span>
                    <div className="flex items-center gap-1">
                      <Badge variant="outline" className="text-xs">
                        {mediaItems.filter(item => item.tags && item.tags.includes(tag)).length}
                      </Badge>
                      <Button
                        variant="ghost"
                        size="icon"
                        className="p-1 h-5 w-5 text-destructive hover:bg-destructive/10"
                        title={`Delete tag '${tag}' from all photos`}
                        onClick={e => {
                          e.stopPropagation();
                          handleDeleteTag(tag);
                        }}
                      >
                        <X className="h-3 w-3" />
                      </Button>
                    </div>
                  </div>
                ))}
              </div>
            </ScrollArea>
          </div>
        </div>
      </div>

      {/* Main Content */}
      <div className="flex-1 overflow-auto">
        <div className="p-6">
          <div className="w-full flex justify-end mb-4">
            <div className="w-full flex justify-center mb-4">
              <img src="/imirrorheader.png" alt="iMirror header" style={{ width: '100%', maxWidth: '960px', display: 'block' }} />
            </div>
          </div>
          
          {/* Navigation Bar */}
          <div className="w-full flex justify-center mb-6">
            <div className="flex items-center gap-4 bg-white dark:bg-gray-800 rounded-lg shadow-sm border p-2">
              <Button
                variant="ghost"
                className="flex items-center gap-2"
                onClick={() => setShowContentImporter(true)}
              >
                <Globe className="h-4 w-4" />
                Import Content
              </Button>
              <Button
                variant="ghost"
                className="flex items-center gap-2"
                onClick={() => setShowAddMediaFile(true)}
              >
                <Plus className="h-4 w-4" />
                Add Media File
              </Button>
              <Button
                variant="ghost"
                className="flex items-center gap-2"
                onClick={() => setIsDebugOpen(true)}
              >
                <Bug className="h-4 w-4" />
                Debug
              </Button>
            </div>
          </div>
          {/* AI Interface */}
          {filters.selectedTags.length === 1 && (
            <Card className="mb-6">
              {aiInterfaceMode === 'avatar' ? (
                /* Avatar Mode */
                <CardContent className="p-0">
                  <div style={{ display: "flex", alignItems: "center", minHeight: 120 }}>
                    {/* Avatar on the left, vertically centered */}
                    <div style={{ display: "flex", paddingLeft: 16 }}>
                      <AnamAvatar
                        isActive={talking && aiInterfaceMode === 'avatar'}
                        currentTag={filters.selectedTags[0]}
                        style={{
                          height: "100%",
                          width: "auto",
                          maxWidth: 240,
                          borderRadius: "0 0.5rem 0.5rem 0",
                          background: "#f7f7f7"
                        }}
                      />
                    </div>
                    {/* Text content on the right */}
                    <div style={{ flex: 1, padding: 24 }}>
                      <h3 className="font-semibold text-sm flex items-center gap-2">
                        About my {filters.selectedTags[0]} memory ({aiPhotoCount} photos)
                        <Sparkles className="h-4 w-4 text-primary" />
                      </h3>
                      {isGeneratingSummary ? (
                        <div className="flex items-center gap-2 text-sm text-muted-foreground" style={{ marginTop: 8 }}>
                          <Loader2 className="h-4 w-4 animate-spin" />
                          Thinking about my photos...
                        </div>
                      ) : aiSummary ? (
                        <p className="text-sm leading-relaxed whitespace-pre-line" style={{ marginTop: 8 }}>
                          {aiSummary}
                        </p>
                      ) : null}
                    </div>
                  </div>
                </CardContent>
              ) : (
                /* Text Mode - Show full chat interface */
                <div className="p-6">
                  <div className="mb-4">
                    <h3 className="font-semibold text-sm flex items-center gap-2 mb-2">
                      Chat about my {filters.selectedTags[0]} memory ({aiPhotoCount} photos)
                      <Sparkles className="h-4 w-4 text-primary" />
                    </h3>
                  </div>
                  
                  {/* Text Chat Interface */}
                  <EmbeddedTextChat 
                    media={mediaItems.find(m => m.tags?.includes(filters.selectedTags[0])) || mediaItems[0]}
                    tag={filters.selectedTags[0]}
                    model={aiModel}
                    onMessagesChange={(messages) => {
                      // Handle messages if needed
                      console.log('Chat messages updated:', messages);
                    }}
                  />
                </div>
              )}
            </Card>
          )}

          {/* Controls */}
          <div className="mb-6 flex items-center justify-between">
            <div>
              <p className="text-muted-foreground">
                {isLoading ? 'Loading...' : `Showing ${filteredMedia.length} of ${mediaItems.length} photos`}
              </p>
            </div>
            <div className="flex items-center gap-2">
              <Button
                onClick={() => setShowAddMediaFile(true)}
                className="flex items-center gap-2"
              >
                <Plus className="h-4 w-4" />
                Add Media File
              </Button>
              <AIInterfaceSelector
                currentMode={aiInterfaceMode}
                currentModel={aiModel}
                onModeChange={handleAiInterfaceModeChange}
                onModelChange={handleAiModelChange}
                onClose={() => {}}
              />
              <Button
                variant="outline"
                size="sm"
                onClick={loadMediaItems}
                disabled={isLoading}
                className="flex items-center gap-2"
              >
                <RefreshCw className={`h-4 w-4 ${isLoading ? 'animate-spin' : ''}`} />
                Refresh
              </Button>
              <DropdownMenu>
                <DropdownMenuTrigger asChild>
                  <Button variant="outline" size="icon" className="ml-2">
                    <MoreVertical className="h-5 w-5" />
                  </Button>
                </DropdownMenuTrigger>
                <DropdownMenuContent align="end">
                  <DropdownMenuItem onClick={() => setViewMode('grid')}>
                    <Grid className="h-4 w-4 mr-2" /> Grid
                  </DropdownMenuItem>
                  <DropdownMenuItem onClick={() => setViewMode('masonry')}>
                    <LayoutGrid className="h-4 w-4 mr-2" /> Masonry
                  </DropdownMenuItem>
                  <DropdownMenuItem onClick={() => setIsDebugOpen(!isDebugOpen)}>
                    <Bug className="h-4 w-4 mr-2" /> Debug
                  </DropdownMenuItem>
                  <DropdownMenuItem onClick={handleGenerateYearTags} disabled={isGeneratingYearTags}>
                    {isGeneratingYearTags ? (
                      <Loader2 className="animate-spin h-4 w-4 mr-2" />
                    ) : (
                      <Sparkles className="h-4 w-4 mr-2" />
                    )}
                    Generate Year Tags
                  </DropdownMenuItem>
                  <DropdownMenuItem onClick={handleCleanupMissingFiles}>
                    <X className="h-4 w-4 mr-2" />
                    Cleanup Missing Files
                  </DropdownMenuItem>
                </DropdownMenuContent>
              </DropdownMenu>
            </div>
          </div>

          {/* Photo Grid */}
          {isLoading ? (
            <div className="text-center py-12">
              <RefreshCw className="h-8 w-8 mx-auto mb-4 animate-spin text-muted-foreground" />
              <p className="text-muted-foreground">Loading photos...</p>
            </div>
          ) : (
            <div className={gridClasses}>
              {/* Add this debug section */}
              <div className="text-xs text-gray-500 mb-2 p-2 bg-gray-100 rounded">
                Debug: Rendering {filteredMedia.length} photo cards from {mediaItems.length} total items
              </div>
              
              {filteredMedia.map((item) => {
                console.log('Rendering photo card:', item.id, item.title, item.file_path);
                const contexts = item.contexts || [];
                const wordCount = contexts.reduce((sum, ctx) => sum + (ctx.text?.split(/\s+/).length || 0), 0);
                const size = getSizeClass(wordCount);
                // Map size to minHeight
                const minHeight =
                  size === 'xl' ? 960 :
                  size === 'lg' ? 760 :
                  size === 'md' ? 600 :
                  440;
                return (
                  <div
                    key={item.id}
                    className={viewMode === 'masonry' ? 'break-inside-avoid mb-4' : ''}
                    style={
                      viewMode === 'masonry'
                        ? { minHeight, maxWidth: '100%' }
                        : undefined
                    }
                  >
                    <div className="relative">
                      <PhotoCard
                        media={item}
                        onClick={() => handleMediaClick(item.id)}
                        size={size}
                        onTagsUpdated={loadMediaItems}
                        onFileMissing={handleFileMissing}
                        onFileLoadError={handleFileLoadError}
                        onFileLoadSuccess={handleFileLoadSuccess}
                      />
                      {!filters.selectedTags.length && aiInterfaceMode === 'avatar' && (
                        <button
                          className="absolute top-2 right-2 z-10 bg-primary text-primary-foreground rounded px-2 py-1 text-xs shadow hover:bg-primary/80 transition"
                          title="Start AI Interview"
                          onClick={e => {
                            e.stopPropagation();
                            setInterviewMediaId(item.id);
                          }}
                        >
                          <Mic className="h-4 w-4" />
                        </button>
                      )}
                    </div>
                  </div>
                );
              })}
            </div>
          )}

          {/* Empty state */}
          {!isLoading && filteredMedia.length === 0 && (
            <div className="text-center py-12">
              <p className="text-muted-foreground text-lg mb-4">
                {mediaItems.length === 0 ? 'No photos available' : 'No photos found matching your criteria'}
              </p>
              {mediaItems.length > 0 && (
                <Button
                  variant="outline"
                  onClick={() => setFilters({ searchQuery: "", selectedTags: [] })}
                >
                  Clear Filters
                </Button>
              )}
            </div>
          )}
        </div>
      </div>

      {/* Photo Modal */}
      <PhotoModal
        key={`modal-${selectedMediaId}-${isModalOpen}`}
        mediaId={selectedMediaId}
        isOpen={isModalOpen}
        onClose={() => {
          console.log('🚪 Closing modal');
          setIsModalOpen(false);
          setSelectedMediaId(null);
        }}
      />

      {/* AI Interview Modal */}
      {interviewMediaId && (
        <div className="fixed inset-0 z-50 flex items-center justify-center bg-black/40">
          {aiInterfaceMode === 'avatar' ? (
            <AIInterview
              media={mediaItems.find(m => m.id === interviewMediaId)!}
              onClose={() => setInterviewMediaId(null)}
            />
          ) : (
            <AITextInterface
              media={mediaItems.find(m => m.id === interviewMediaId)!}
              onClose={() => setInterviewMediaId(null)}
            />
          )}
        </div>
      )}

      {/* Add Event Modal */}
      {showAddMediaFile && (
        <AddMediaFile
          onClose={() => setShowAddMediaFile(false)}
          onMediaFileAdded={() => {
            setShowAddMediaFile(false);
            loadMediaItems();
          }}
        />
      )}

      {/* Content Importer Modal */}
      {showContentImporter && (
        <div className="fixed inset-0 z-50 flex items-center justify-center bg-black/40 p-4">
          <div className="bg-white dark:bg-gray-900 rounded-lg shadow-xl max-w-6xl w-full max-h-[90vh] overflow-hidden">
            <div className="flex items-center justify-between p-6 border-b">
              <h2 className="text-xl font-semibold">Content Importer</h2>
              <Button
                variant="ghost"
                size="sm"
                onClick={() => setShowContentImporter(false)}
              >
                <X className="h-4 w-4" />
              </Button>
            </div>
            <div className="overflow-auto max-h-[calc(90vh-120px)]">
              <ContentImporter onContentImported={() => {
                setShowContentImporter(false);
                loadMediaItems();
              }} />
            </div>
          </div>
        </div>
      )}

      {/* Debug Window */}
      <DebugWindow 
        isOpen={isDebugOpen} 
        onClose={() => setIsDebugOpen(false)} 
      />
    </div>
  );
}