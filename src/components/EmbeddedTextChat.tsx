import React, { useState, useEffect, useRef } from 'react';
import { Button } from './ui/button';
import { Textarea } from './ui/textarea';
import { ScrollArea } from './ui/scroll-area';
import { Badge } from './ui/badge';
import { Send, Mic, MicOff, Volume2, User, Bot } from 'lucide-react';
import { mediaApi, InterviewMessage, MediaItem } from '../services/api';

interface EmbeddedTextChatProps {
  media: MediaItem;
  tag: string;
  model?: string;
  onMessagesChange?: (messages: InterviewMessage[]) => void;
}

export const EmbeddedTextChat: React.FC<EmbeddedTextChatProps> = ({ media, tag, model = 'gpt-4o-mini', onMessagesChange }) => {
  const [messages, setMessages] = useState<InterviewMessage[]>([]);
  const [currentInput, setCurrentInput] = useState('');
  const [isLoading, setIsLoading] = useState(false);
  const [isStarted, setIsStarted] = useState(false);
  const [isListening, setIsListening] = useState(false);
  const [isVoiceSupported, setIsVoiceSupported] = useState(false);
  const [isSpeaking, setIsSpeaking] = useState(false);
  const [autoSpeak, setAutoSpeak] = useState(true);
  const recognitionRef = useRef<any>(null);
  const speechRef = useRef<any>(null);

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
        setCurrentInput(prev => prev ? `${prev} ${transcript}` : transcript);
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
      if (speechRef.current) {
        window.speechSynthesis.cancel();
      }
    };
  }, []);

  // Notify parent when messages change
  useEffect(() => {
    onMessagesChange?.(messages);
  }, [messages, onMessagesChange]);

  // Start conversation automatically when tag changes
  useEffect(() => {
    if (!isStarted && tag) {
      startInterview();
    }
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [tag]);

  // Auto-speak the latest AI response
  useEffect(() => {
    if (messages.length > 0 && autoSpeak) {
      const lastMessage = messages[messages.length - 1];
      if (lastMessage.role === 'assistant' && lastMessage.content && !isLoading) {
        const timer = setTimeout(() => {
          speakText(lastMessage.content);
        }, 500);
        return () => clearTimeout(timer);
      }
    }
  }, [messages, autoSpeak, isLoading]);

  const startInterview = async () => {
    if (isStarted) return;
    
    setIsLoading(true);
    try {
      // Use the same API as the avatar mode - generate initial summary
      const response = await mediaApi.generatePhotographerSummary(tag, model);
      const initialMessage: InterviewMessage = {
        role: 'assistant',
        content: response.summary
      };
      setMessages([initialMessage]);
      setIsStarted(true);
    } catch (error) {
      console.error('Failed to start conversation:', error);
    } finally {
      setIsLoading(false);
    }
  };

  const sendMessage = async () => {
    if (!currentInput.trim() || isLoading) return;

    const userInput = currentInput.trim();
    setCurrentInput('');
    setIsLoading(true);

    try {
      // Add user message to conversation
      const userMessage: InterviewMessage = {
        role: 'user',
        content: userInput
      };
      
      // Convert messages to conversation history format
      const conversationHistory = messages.map(msg => ({
        role: msg.role,
        content: msg.content
      }));
      
      // Use the same API as the avatar mode
      const response = await mediaApi.generatePhotographerConversation(tag, userInput, conversationHistory, model);
      
      // Add AI response
      const aiMessage: InterviewMessage = {
        role: 'assistant',
        content: response.summary
      };
      
      setMessages(prev => [...prev, userMessage, aiMessage]);
    } catch (error) {
      console.error('Failed to send message:', error);
      setCurrentInput(userInput);
    } finally {
      setIsLoading(false);
    }
  };

  const handleKeyPress = (e: React.KeyboardEvent) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault();
      sendMessage();
    }
  };

  const toggleVoiceInput = () => {
    if (!recognitionRef.current) return;

    if (isListening) {
      recognitionRef.current.stop();
    } else {
      recognitionRef.current.start();
    }
  };

  const speakText = (text: string) => {
    if ('speechSynthesis' in window) {
      window.speechSynthesis.cancel();
      
      const utterance = new SpeechSynthesisUtterance(text);
      utterance.lang = 'en-US';
      utterance.rate = 0.9;
      
      utterance.onstart = () => setIsSpeaking(true);
      utterance.onend = () => setIsSpeaking(false);
      utterance.onerror = () => setIsSpeaking(false);
      
      speechRef.current = utterance;
      window.speechSynthesis.speak(utterance);
    }
  };

  const stopSpeaking = () => {
    if ('speechSynthesis' in window) {
      window.speechSynthesis.cancel();
      setIsSpeaking(false);
    }
  };

  return (
    <div className="space-y-4">
      {/* Chat Messages */}
      <ScrollArea className="h-48 w-full border rounded-md p-4 bg-background">
        <div className="space-y-3">
          {!isStarted ? (
            <div className="text-center py-8 text-muted-foreground">
              <Bot className="h-8 w-8 mx-auto mb-2" />
              <p className="text-sm">Loading conversation about your {tag} photos...</p>
            </div>
          ) : (
            messages.map((message, index) => (
              <div
                key={index}
                className={`flex ${
                  message.role === 'user' ? 'justify-end' : 'justify-start'
                }`}
              >
                <div
                  className={`max-w-[80%] rounded-lg px-3 py-2 text-sm ${
                    message.role === 'user'
                      ? 'bg-primary text-primary-foreground'
                      : 'bg-muted'
                  }`}
                >
                  <div className="flex items-center gap-2 mb-1">
                    <Badge variant="secondary" className="text-xs">
                      {message.role === 'user' ? (
                        <>
                          <User className="h-3 w-3 mr-1" />
                          You
                        </>
                      ) : (
                        <>
                          <Bot className="h-3 w-3 mr-1" />
                          AI
                        </>
                      )}
                    </Badge>
                    {message.role === 'assistant' && message.content && (
                      <Button
                        variant="ghost"
                        size="sm"
                        onClick={() => isSpeaking ? stopSpeaking() : speakText(message.content)}
                        className="h-5 w-5 p-0 hover:bg-muted"
                        title={isSpeaking ? "Stop speaking" : "Hear this message"}
                      >
                        <Volume2 className={`h-3 w-3 ${isSpeaking ? 'text-primary animate-pulse' : ''}`} />
                      </Button>
                    )}
                  </div>
                  <div className="whitespace-pre-wrap">
                    {Array.isArray(message.content) 
                      ? message.content.find(part => part.type === 'text')?.text || '[No text content]'
                      : message.content
                    }
                  </div>
                </div>
              </div>
            ))
          )}
          {isLoading && (
            <div className="flex justify-start">
              <div className="bg-muted rounded-lg px-3 py-2">
                <div className="flex items-center gap-2">
                  <Badge variant="secondary" className="text-xs">
                    <Bot className="h-3 w-3 mr-1" />
                    AI
                  </Badge>
                  <div className="flex space-x-1">
                    <div className="w-2 h-2 bg-muted-foreground rounded-full animate-bounce"></div>
                    <div className="w-2 h-2 bg-muted-foreground rounded-full animate-bounce" style={{ animationDelay: '0.1s' }}></div>
                    <div className="w-2 h-2 bg-muted-foreground rounded-full animate-bounce" style={{ animationDelay: '0.2s' }}></div>
                  </div>
                </div>
              </div>
            </div>
          )}
        </div>
      </ScrollArea>
      
      {/* Input Area */}
      <div className="space-y-2">
        <div className="flex gap-2">
          <Textarea
            value={currentInput}
            onChange={(e) => setCurrentInput(e.target.value)}
            onKeyPress={handleKeyPress}
            placeholder={`Ask about your ${tag} photos, memories, or start a conversation...`}
            className="flex-1"
            disabled={isLoading}
            rows={2}
          />
          {isVoiceSupported && (
            <Button
              onClick={toggleVoiceInput}
              disabled={isLoading}
              variant={isListening ? "destructive" : "outline"}
              size="sm"
              title={isListening ? "Stop voice input" : "Start voice input"}
              className="min-w-[48px]"
            >
              {isListening ? <MicOff className="h-4 w-4" /> : <Mic className="h-4 w-4" />}
            </Button>
          )}
          <Button
            onClick={sendMessage}
            disabled={isLoading || !currentInput.trim()}
            size="sm"
            title="Send message"
          >
            <Send className="h-4 w-4" />
          </Button>
        </div>
        
        {/* Status and Controls */}
        <div className="flex items-center justify-between text-xs text-muted-foreground">
          <div className="flex items-center gap-4">
            {isListening && (
              <div className="flex items-center gap-2">
                <div className="flex space-x-1">
                  <div className="w-2 h-2 bg-red-500 rounded-full animate-bounce"></div>
                  <div className="w-2 h-2 bg-red-500 rounded-full animate-bounce" style={{ animationDelay: '0.1s' }}></div>
                  <div className="w-2 h-2 bg-red-500 rounded-full animate-bounce" style={{ animationDelay: '0.2s' }}></div>
                </div>
                Listening...
              </div>
            )}
            {isSpeaking && (
              <div className="flex items-center gap-2">
                <div className="flex space-x-1">
                  <div className="w-2 h-2 bg-blue-500 rounded-full animate-bounce"></div>
                  <div className="w-2 h-2 bg-blue-500 rounded-full animate-bounce" style={{ animationDelay: '0.1s' }}></div>
                  <div className="w-2 h-2 bg-blue-500 rounded-full animate-bounce" style={{ animationDelay: '0.2s' }}></div>
                </div>
                Speaking...
              </div>
            )}
          </div>
          <label className="flex items-center gap-2 cursor-pointer">
            <input
              type="checkbox"
              checked={autoSpeak}
              onChange={(e) => setAutoSpeak(e.target.checked)}
              className="w-3 h-3 cursor-pointer"
            />
            Auto-speak AI responses
          </label>
        </div>
      </div>
    </div>
  );
}; 