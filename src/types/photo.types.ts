export interface Photo {
  id: string;
  src: string;
  title: string;
  summary: string;
  tags: string[];
  width: number;
  height: number;
  createdAt: string;
}

export interface MediaItem {
  id: string;
  file_path: string;
  filename: string;
  title?: string;
  summary?: string;
  description?: string;
  tags?: string[];
  file_size?: number;
  file_type?: string;
  created_at: string;
  updated_at: string;
  contexts?: Context[];
  metadata?: Record<string, any>;
}

export interface Context {
  id: string;
  text: string;
  context_type?: string;
  created_at: string;
  updated_at?: string;
}

export interface PhotoFilters {
  searchQuery: string;
  selectedTags: string[];
}