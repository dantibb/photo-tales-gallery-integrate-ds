import React, { useState, useEffect, useRef } from 'react';
import { Button } from './ui/button';
import { Textarea } from './ui/textarea';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from './ui/card';
import { ScrollArea } from './ui/scroll-area';
import { Badge } from './ui/badge';
import { MessageCircle, Send, Save, RotateCcw, Mic, MicOff, Volume2 } from 'lucide-react';
import { interviewApi, InterviewMessage, MediaItem } from '../services/api';
import { mediaApi } from '../services/api';

interface AIInterviewProps {
  media: MediaItem;
  onClose: () => void;
  onSave?: () => void;
  onMessagesChange?: (messages: InterviewMessage[]) => void;
}

export const AIInterview: React.FC<AIInterviewProps> = ({ media, onClose, onSave, onMessagesChange }) => {
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

  // Auto-speak the latest AI response
  useEffect(() => {
    if (messages.length > 0 && autoSpeak) {
      const lastMessage = messages[messages.length - 1];
      if (lastMessage.role === 'assistant' && lastMessage.content && !isLoading) {
        // Small delay to ensure the message is fully rendered
        const timer = setTimeout(() => {
          speakText(lastMessage.content);
        }, 500);
        return () => clearTimeout(timer);
      }
    }
  }, [messages, autoSpeak, isLoading]);

  // Start interview automatically on mount or when media changes
  useEffect(() => {
    if (!isStarted && media?.id) {
      startInterview();
    }
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [media?.id]);

  const startInterview = async () => {
    setIsLoading(true);
    try {
      const response = await interviewApi.startInterview(media.id);
      // Filter out system message and first user message, keep only AI responses
      const filteredMessages = response.messages.filter(msg => 
        msg.role === 'assistant' || 
        (msg.role === 'user' && msg !== response.messages[1]) // Exclude the first user message
      );
      setMessages(filteredMessages);
      setIsStarted(true);
    } catch (error) {
      console.error('Failed to start interview:', error);
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
      const response = await interviewApi.chatInterview(media.id, userInput, messages);
      // Filter out system messages from the response
      const filteredMessages = response.messages.filter(msg => msg.role !== 'system');
      setMessages(filteredMessages);
    } catch (error) {
      console.error('Failed to send message:', error);
      // If the request failed, add the user message back to the input
      setCurrentInput(userInput);
    } finally {
      setIsLoading(false);
    }
  };

  const saveInterview = async () => {
    if (messages.length === 0) return;

    setIsLoading(true);
    try {
      await interviewApi.saveInterview(media.id, messages);
      // After saving, auto-generate summary and tags
      try {
        await mediaApi.generateSummary(media.id);
      } catch (err) {
        console.error('Failed to auto-generate summary:', err);
      }
      try {
        await mediaApi.generateTags(media.id);
      } catch (err) {
        console.error('Failed to auto-generate tags:', err);
      }
      onSave?.();
      onClose();
    } catch (error) {
      console.error('Failed to save interview:', error);
    } finally {
      setIsLoading(false);
    }
  };

  const resetInterview = () => {
    setMessages([]);
    setIsStarted(false);
    setCurrentInput('');
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
      // Stop any current speech
      window.speechSynthesis.cancel();
      
      const utterance = new SpeechSynthesisUtterance(text);
      utterance.lang = 'en-US';
      utterance.rate = 0.9; // Slightly slower for better comprehension
      
      utterance.onstart = () => {
        setIsSpeaking(true);
      };
      
      utterance.onend = () => {
        setIsSpeaking(false);
      };
      
      utterance.onerror = () => {
        setIsSpeaking(false);
      };
      
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
    <Card className="w-full max-w-2xl mx-auto">
      <CardHeader>
        <div className="flex items-center justify-between">
          <div>
            <CardTitle className="flex items-center gap-2">
              <MessageCircle className="h-5 w-5" />
              AI Interview
            </CardTitle>
            <CardDescription>
              Have a conversation with AI about this image
            </CardDescription>
          </div>
          <div className="flex gap-2">
            {isStarted && (
              <>
                <Button
                  variant="outline"
                  size="sm"
                  onClick={resetInterview}
                  disabled={isLoading}
                >
                  <RotateCcw className="h-4 w-4 mr-1" />
                  Reset
                </Button>
                <Button
                  size="sm"
                  onClick={saveInterview}
                  disabled={isLoading || messages.length === 0}
                >
                  <Save className="h-4 w-4 mr-1" />
                  Save
                </Button>
              </>
            )}
            <Button variant="outline" size="sm" onClick={onClose}>
              Close
            </Button>
          </div>
        </div>
      </CardHeader>
      <CardContent>
        {!isStarted ? (
          <div className="text-center py-8">
            <MessageCircle className="h-12 w-12 mx-auto mb-4 text-muted-foreground" />
            <h3 className="text-lg font-semibold mb-2">Start AI Interview</h3>
            <p className="text-muted-foreground mb-4">
              Begin a conversation with AI about this image. The AI will ask questions and help you explore the image's details.
            </p>
            <Button onClick={startInterview} disabled={isLoading}>
              {isLoading ? 'Starting...' : 'Start Interview'}
            </Button>
          </div>
        ) : (
          <div className="space-y-4">
            <ScrollArea className="h-64 w-full border rounded-md p-4">
              <div className="space-y-4">
                {messages.map((message, index) => (
                  <div
                    key={index}
                    className={`flex ${
                      message.role === 'user' ? 'justify-end' : 'justify-start'
                    }`}
                  >
                    <div
                      className={`max-w-[80%] rounded-lg px-4 py-2 ${
                        message.role === 'user'
                          ? 'bg-primary text-primary-foreground'
                          : 'bg-muted'
                      }`}
                    >
                      <div className="flex items-center gap-2 mb-1">
                        <Badge variant="secondary" className="text-xs">
                          {message.role === 'user' ? 'You' : 'AI'}
                        </Badge>
                        {message.role === 'assistant' && message.content && (
                          <Button
                            variant="ghost"
                            size="sm"
                            onClick={() => isSpeaking ? stopSpeaking() : speakText(message.content)}
                            className="h-6 w-6 p-0 hover:bg-muted"
                            title={isSpeaking ? "Stop speaking" : "Hear this message"}
                          >
                            <Volume2 className={`h-3 w-3 ${isSpeaking ? 'text-primary animate-pulse' : ''}`} />
                          </Button>
                        )}
                      </div>
                      {message.type === 'image_url' && message.data ? (
                        <img
                          src={`data:image/jpeg;base64,${message.data}`}
                          alt="AI generated or referenced"
                          className="max-w-full max-h-64 rounded shadow border my-2"
                        />
                      ) : message.content ? (
                        <div className="whitespace-pre-wrap">
                          {Array.isArray(message.content) 
                            ? message.content.find(part => part.type === 'text')?.text || '[No text content]'
                            : message.content
                          }
                        </div>
                      ) : (
                        <div className="italic text-muted-foreground">[Unknown message type]</div>
                      )}
                    </div>
                  </div>
                ))}
                {isLoading && (
                  <div className="flex justify-start">
                    <div className="bg-muted rounded-lg px-4 py-2">
                      <div className="flex items-center gap-2">
                        <Badge variant="secondary" className="text-xs">
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
            
            <div className="flex gap-2">
              <Textarea
                value={currentInput}
                onChange={(e) => setCurrentInput(e.target.value)}
                onKeyPress={handleKeyPress}
                placeholder="Type your response or use voice input..."
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
                  title={isListening ? "Stop voice input" : "Start voice input (speak your response)"}
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
            {!isVoiceSupported && (
              <div className="text-xs text-muted-foreground mb-2">
                💡 Voice input is not supported in this browser. Try Chrome, Edge, or Safari for voice features.
              </div>
            )}
            <div className="flex items-center justify-between">
              {isListening && (
                <div className="text-sm text-muted-foreground flex items-center gap-2">
                  <div className="flex space-x-1">
                    <div className="w-2 h-2 bg-red-500 rounded-full animate-bounce"></div>
                    <div className="w-2 h-2 bg-red-500 rounded-full animate-bounce" style={{ animationDelay: '0.1s' }}></div>
                    <div className="w-2 h-2 bg-red-500 rounded-full animate-bounce" style={{ animationDelay: '0.2s' }}></div>
                  </div>
                  Listening... Speak now
                </div>
              )}
              {isSpeaking && (
                <div className="text-sm text-muted-foreground flex items-center gap-2">
                  <div className="flex space-x-1">
                    <div className="w-2 h-2 bg-blue-500 rounded-full animate-bounce"></div>
                    <div className="w-2 h-2 bg-blue-500 rounded-full animate-bounce" style={{ animationDelay: '0.1s' }}></div>
                    <div className="w-2 h-2 bg-blue-500 rounded-full animate-bounce" style={{ animationDelay: '0.2s' }}></div>
                  </div>
                  Speaking...
                </div>
              )}
              <div className="flex items-center gap-2 ml-auto">
                <label className="text-sm text-muted-foreground flex items-center gap-2 cursor-pointer">
                  <input
                    type="checkbox"
                    checked={autoSpeak}
                    onChange={(e) => setAutoSpeak(e.target.checked)}
                    className="w-4 h-4 cursor-pointer"
                  />
                  Auto-speak AI responses
                </label>
              </div>
            </div>
          </div>
        )}
      </CardContent>
    </Card>
  );
}; 