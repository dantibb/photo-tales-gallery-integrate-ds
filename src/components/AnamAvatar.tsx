import React, { useEffect, useRef, useState } from 'react';

interface AnamAvatarProps {
  isActive?: boolean;
  className?: string;
  style?: React.CSSProperties;
  currentTag?: string;
}

export const AnamAvatar: React.FC<AnamAvatarProps> = ({ 
  isActive = false, 
  className = '', 
  style = {},
  currentTag = 'memories'
}) => {
  console.log('AnamAvatar props:', { isActive, className, style });
  const videoRef = useRef<HTMLVideoElement>(null);
  const [isConnected, setIsConnected] = useState(false);
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    console.log('AnamAvatar useEffect triggered:', { isActive, hasVideoRef: !!videoRef.current });
    if (!isActive || !videoRef.current) {
      console.log('AnamAvatar: Not initializing - not active or no video ref');
      return;
    }

    let anamClient: any = null;

    const initializeAnam = async () => {
      try {
        console.log('AnamAvatar: Starting initialization...');
        setIsLoading(true);
        setError(null);

        // Dynamic import of the Anam SDK
        const { createClient } = await import('https://esm.sh/@anam-ai/js-sdk@latest');

        // API key - you may want to move this to environment variables
        const API_KEY = "MTAwNTkwY2QtZDAzYS00YzBiLWE4NjItOTNkMTc2ZjM0NDcwOjk1ZVphVmpidmJaWER3WTA4am50MG9uU28xQVB5TkJBRHpGTzlUTkhhK0E9";

        // Create session token with custom LLM configuration
        const response = await fetch("https://api.anam.ai/v1/auth/session-token", {
          method: "POST",
          headers: {
            "Content-Type": "application/json",
            Authorization: `Bearer ${API_KEY}`,
          },
          body: JSON.stringify({
            personaConfig: {
              name: "Richard",
              avatarId: "19d18eb0-5346-4d50-a77f-26b3723ed79d",
              voiceId: "e9104cf7-d163-4f89-b01a-311f2e8943d0",
              // Use custom LLM instead of Anam's default
              llmId: "CUSTOMER_CLIENT_V1",
              systemPrompt: "You are Richard, a helpful AI assistant who can reminisce about photos and memories. Keep responses concise and engaging.",
            },
          }),
        });

        if (!response.ok) {
          throw new Error('Failed to create session token');
        }

        const data = await response.json();
        const sessionToken = data.sessionToken;

        // Create Anam client and stream to video element
        console.log('AnamAvatar: Creating client and streaming...');
        anamClient = createClient(sessionToken);
        await anamClient.streamToVideoElement("anam-avatar-video");
        
        // Custom LLM handler that integrates with your existing backend
        const handleUserMessage = async (messageHistory: any[]) => {
          if (!anamClient || messageHistory.length === 0) return;
          
          // Only respond to user messages
          const lastMessage = messageHistory[messageHistory.length - 1];
          if (lastMessage.role !== 'user') return;

          try {
            console.log('AnamAvatar: Processing user message:', lastMessage.content);
            
            // Use the currentTag prop passed from the parent component
            const tagToUse = currentTag;
            
            // Call your existing backend API to generate a response
            const response = await fetch('http://localhost:5001/api/generate-photographer-summary', {
              method: 'POST',
              headers: {
                'Content-Type': 'application/json',
              },
              body: JSON.stringify({
                tag: tagToUse,
                userMessage: lastMessage.content,
                conversationHistory: messageHistory
              }),
            });

            if (!response.ok) {
              throw new Error('Failed to get AI response');
            }

            const result = await response.json();
            
            // Create a streaming talk session
            const talkStream = anamClient.createTalkMessageStream();
            
            // Stream the response to the avatar
            if (result.summary && talkStream.isActive()) {
              talkStream.streamMessageChunk(result.summary, false);
              talkStream.endMessage();
            }
            
          } catch (error) {
            console.error('AnamAvatar: Custom LLM error:', error);
            if (anamClient) {
              anamClient.talk("I'm sorry, I encountered an error while processing your request. Please try again.");
            }
          }
        };
        
        // Set up custom LLM event listeners
        anamClient.addListener('MESSAGE_HISTORY_UPDATED', handleUserMessage);
        
        console.log('AnamAvatar: Successfully connected!');
        setIsConnected(true);
        setIsLoading(false);
      } catch (err) {
        console.error('AnamAvatar: Failed to initialize Anam:', err);
        setError(err instanceof Error ? err.message : 'Failed to connect');
        setIsLoading(false);
      }
    };

    initializeAnam();

    // Cleanup function
    return () => {
      console.log('AnamAvatar: Cleanup function called');
      if (anamClient) {
        try {
          anamClient.disconnect?.();
          console.log('AnamAvatar: Disconnected client');
        } catch (err) {
          console.error('AnamAvatar: Error disconnecting Anam client:', err);
        }
      }
      setIsConnected(false);
    };
  }, [isActive]);

  // Show nothing when not active or if there's an error
  if (!isActive || error) {
    console.log('AnamAvatar: Not active or error', { isActive, error });
    return null;
  }

  return (
    <div className={`relative ${className}`} style={style}>
      <video
        ref={videoRef}
        id="anam-avatar-video"
        autoPlay
        playsInline
        style={{
          borderRadius: '50%',
          objectFit: 'cover',
          width: '100%',
          height: '100%',
          backgroundColor: '#f7f7f7'
        }}
      />
      {isLoading && (
        <div className="absolute inset-0 flex items-center justify-center bg-black bg-opacity-50 rounded-full">
          <div className="animate-spin rounded-full h-6 w-6 border-b-2 border-white"></div>
        </div>
      )}
      {isConnected && (
        <div className="absolute -bottom-1 -right-1 w-3 h-3 bg-green-500 rounded-full border-2 border-white"></div>
      )}
    </div>
  );
}; 