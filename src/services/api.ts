const API_BASE_URL = 'http://localhost:8080/api';

export interface MediaItem {
  id: string;
  file_path: string;
  filename: string;
  title?: string;
  summary?: string;
  tags?: string[];
  file_size?: number;
  file_type?: string;
  created_at: string;
  updated_at: string;
  contexts?: Context[];
  image_metadata?: any;
}

export interface Context {
  id: string;
  text: string;
  context_type?: string;
  created_at: string;
}

export interface InterviewMessage {
  role: 'system' | 'user' | 'assistant';
  content?: string;
  type?: 'text' | 'image_url';
  data?: string; // for image base64 or URL
}

export interface InterviewResponse {
  media_id: string;
  ai_question: string;
  messages: InterviewMessage[];
}

export interface SaveInterviewRequest {
  messages: InterviewMessage[];
}

// Media API
export const mediaApi = {
  async listMedia(): Promise<MediaItem[]> {
    console.log('Fetching from:', `${API_BASE_URL}/media`);
    const response = await fetch(`${API_BASE_URL}/media`);
    console.log('Response status:', response.status);
    console.log('Response headers:', response.headers);
    if (!response.ok) {
      throw new Error(`Failed to fetch media: ${response.status} ${response.statusText}`);
    }
    const data = await response.json();
    console.log('Response data:', data);
    return data;
  },

  async getMediaItem(id: string): Promise<MediaItem> {
    const response = await fetch(`${API_BASE_URL}/media/${id}`);
    if (!response.ok) {
      throw new Error('Failed to fetch media item');
    }
    return response.json();
  },

  async getMediaPreview(id: string): Promise<string> {
    const response = await fetch(`${API_BASE_URL}/media/${id}/preview`);
    if (!response.ok) {
      throw new Error('Failed to fetch media preview');
    }
    const blob = await response.blob();
    return URL.createObjectURL(blob);
  },

  async updateTitle(id: string, title: string): Promise<void> {
    const response = await fetch(`${API_BASE_URL}/media/${id}/title`, {
      method: 'PUT',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({ title }),
    });
    if (!response.ok) {
      throw new Error('Failed to update title');
    }
  },

  async updateSummary(id: string, summary: string): Promise<void> {
    const response = await fetch(`${API_BASE_URL}/media/${id}/summary`, {
      method: 'PUT',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({ summary }),
    });
    if (!response.ok) {
      throw new Error('Failed to update summary');
    }
  },

  async updateTags(id: string, tags: string[]): Promise<void> {
    const response = await fetch(`${API_BASE_URL}/media/${id}/tags`, {
      method: 'PUT',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify(tags),
    });
    if (!response.ok) {
      throw new Error('Failed to update tags');
    }
  },

  async deleteMediaItem(id: string): Promise<void> {
    const response = await fetch(`${API_BASE_URL}/media/${id}`, {
      method: 'DELETE',
    });
    if (!response.ok) {
      throw new Error('Failed to delete media item');
    }
  },

  async cleanupMissingFiles(): Promise<{
    deleted_count: number;
    missing_files: string[];
  }> {
    const response = await fetch(`${API_BASE_URL}/media/cleanup-missing`, {
      method: 'POST',
    });
    if (!response.ok) {
      throw new Error('Failed to cleanup missing files');
    }
    return response.json();
  },

  async clearAllData(id: string): Promise<void> {
    const response = await fetch(`${API_BASE_URL}/media/${id}/clear-all`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
    });
    if (!response.ok) {
      throw new Error('Failed to clear all data');
    }
  },

  async generateSummary(id: string): Promise<{
    summary: string;
    title: string;
    summary_text: string;
  }> {
    const response = await fetch(`${API_BASE_URL}/media/${id}/generate-summary`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({}),
    });
    if (!response.ok) {
      throw new Error('Failed to generate summary');
    }
    return response.json();
  },

  async generateTags(id: string): Promise<{
    tags: string[];
    message: string;
  }> {
    const response = await fetch(`${API_BASE_URL}/media/${id}/generate-tags`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
    });
    if (!response.ok) {
      throw new Error('Failed to generate tags');
    }
    return response.json();
  },

  async getMetadata(id: string): Promise<{
    success: boolean;
    raw_metadata: any;
    formatted_metadata: any;
    summary: string;
  }> {
    const response = await fetch(`${API_BASE_URL}/media/${id}/metadata`);
    if (!response.ok) {
      throw new Error('Failed to fetch metadata');
    }
    return response.json();
  },

  async refreshMetadata(id: string): Promise<{
    success: boolean;
    message: string;
  }> {
    const response = await fetch(`${API_BASE_URL}/media/${id}/refresh-metadata`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
    });
    if (!response.ok) {
      throw new Error('Failed to refresh metadata');
    }
    return response.json();
  },

  async generatePhotographerSummary(tag: string, model?: string): Promise<{ summary: string; photo_count: number; tag: string }> {
    const response = await fetch(`${API_BASE_URL}/ai-photographer/summary`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({ tag, model }),
    });

    if (!response.ok) {
      throw new Error(`Failed to generate photographer summary: ${response.statusText}`);
    }

    return response.json();
  },

  async generatePhotographerConversation(tag: string, userMessage: string, conversationHistory?: any[], model?: string): Promise<{ summary: string; tag: string; photo_count: number }> {
    const response = await fetch(`${API_BASE_URL}/generate-photographer-summary`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({ 
        tag, 
        userMessage, 
        conversationHistory: conversationHistory || [],
        model
      }),
    });

    if (!response.ok) {
      throw new Error(`Failed to generate photographer conversation: ${response.statusText}`);
    }

    return response.json();
  },

  async generateYearTags(): Promise<{ updated_count: number; updated_items: any[]; message: string }> {
    const response = await fetch(`${API_BASE_URL}/media/generate-year-tags`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
    });
    if (!response.ok) {
      throw new Error('Failed to generate year tags');
    }
    return response.json();
  },

  async uploadMedia(files: File[], mediaFileDetails?: { name: string; description: string }): Promise<{ message: string; uploaded_items: MediaItem[]; media_file_name?: string; media_file_description?: string }> {
    const formData = new FormData();
    files.forEach(file => {
      formData.append('files', file);
    });

    if (mediaFileDetails) {
      formData.append('media_file_name', mediaFileDetails.name);
      formData.append('media_file_description', mediaFileDetails.description);
    }

    const response = await fetch(`${API_BASE_URL}/media/upload`, {
      method: 'POST',
      body: formData,
    });
    
    if (!response.ok) {
      throw new Error('Failed to upload media files');
    }
    
    return response.json();
  },
};

// Contexts API
export const contextsApi = {
  async getContexts(mediaId: string): Promise<Context[]> {
    const response = await fetch(`${API_BASE_URL}/media/${mediaId}/contexts`);
    if (!response.ok) {
      throw new Error('Failed to fetch contexts');
    }
    return response.json();
  },

  async addContext(mediaId: string, text: string): Promise<{ id: string }> {
    const response = await fetch(`${API_BASE_URL}/media/${mediaId}/contexts`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({ text }),
    });
    if (!response.ok) {
      throw new Error('Failed to add context');
    }
    return response.json();
  },

  async updateContext(mediaId: string, contextId: string, text: string): Promise<void> {
    const response = await fetch(`${API_BASE_URL}/media/${mediaId}/contexts/${contextId}`, {
      method: 'PUT',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({ text }),
    });
    if (!response.ok) {
      throw new Error('Failed to update context');
    }
  },

  async deleteContext(mediaId: string, contextId: string): Promise<void> {
    const response = await fetch(`${API_BASE_URL}/media/${mediaId}/contexts/${contextId}`, {
      method: 'DELETE',
    });
    if (!response.ok) {
      throw new Error('Failed to delete context');
    }
  },
};

// Interview API
export const interviewApi = {
  async startInterview(mediaId: string): Promise<InterviewResponse> {
    const response = await fetch(`${API_BASE_URL}/media/${mediaId}/interview/start`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
    });
    if (!response.ok) {
      throw new Error('Failed to start interview');
    }
    return response.json();
  },

  async chatInterview(mediaId: string, userText: string, messages: InterviewMessage[]): Promise<InterviewResponse> {
    const response = await fetch(`${API_BASE_URL}/media/${mediaId}/interview/chat`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({ user_text: userText, messages }),
    });
    if (!response.ok) {
      throw new Error('Failed to continue interview');
    }
    return response.json();
  },

  async saveInterview(mediaId: string, messages: InterviewMessage[]): Promise<{ context_id: string }> {
    const response = await fetch(`${API_BASE_URL}/media/${mediaId}/interview/save`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({ messages }),
    });
    if (!response.ok) {
      throw new Error('Failed to save interview');
    }
    return response.json();
  },
}; 