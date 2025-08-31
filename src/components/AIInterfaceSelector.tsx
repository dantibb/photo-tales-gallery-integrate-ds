import React, { useState } from 'react';
import { Button } from './ui/button';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from './ui/card';
import { Badge } from './ui/badge';
import { Bot, User, Video, MessageSquare, Settings, Zap, Brain } from 'lucide-react';

export type AIInterfaceMode = 'avatar' | 'text';
export type AIModel = 'gpt-4o-mini' | 'gpt-4o' | 'gpt-4-turbo';

interface AIInterfaceSelectorProps {
  currentMode: AIInterfaceMode;
  currentModel: AIModel;
  onModeChange: (mode: AIInterfaceMode) => void;
  onModelChange: (model: AIModel) => void;
  onClose: () => void;
}

export const AIInterfaceSelector: React.FC<AIInterfaceSelectorProps> = ({
  currentMode,
  currentModel,
  onModeChange,
  onModelChange,
  onClose
}) => {
  const [isOpen, setIsOpen] = useState(false);
  const [activeTab, setActiveTab] = useState<'interface' | 'model'>('interface');

  const modes = [
    {
      id: 'avatar' as AIInterfaceMode,
      name: 'Anam Avatar',
      description: 'Interactive AI avatar with voice and visual responses',
      icon: Video,
      features: ['Voice interaction', 'Visual avatar', 'Real-time responses', 'Advanced AI personality'],
      color: 'bg-blue-500'
    },
    {
      id: 'text' as AIInterfaceMode,
      name: 'Text Chat',
      description: 'Simple text-based AI conversation interface',
      icon: MessageSquare,
      features: ['Text-based chat', 'Voice input support', 'Text-to-speech', 'Lightweight interface'],
      color: 'bg-green-500'
    }
  ];

  const models = [
    {
      id: 'gpt-4o-mini' as AIModel,
      name: 'GPT-4o Mini',
      description: 'Fast and cost-effective AI model',
      icon: Bot,
      features: ['Fast responses', 'Cost-effective', 'Good for most tasks'],
      color: 'bg-green-500',
      cost: 'Low'
    },
    {
      id: 'gpt-4o' as AIModel,
      name: 'GPT-4o',
      description: 'Advanced AI model with better reasoning',
      icon: Brain,
      features: ['Better reasoning', 'More nuanced responses', 'Higher quality'],
      color: 'bg-blue-500',
      cost: 'Medium'
    },
    {
      id: 'gpt-4-turbo' as AIModel,
      name: 'GPT-4 Turbo',
      description: 'Latest and most powerful AI model',
      icon: Zap,
      features: ['Best performance', 'Latest capabilities', 'Highest quality'],
      color: 'bg-purple-500',
      cost: 'High'
    }
  ];

  const handleModeSelect = (mode: AIInterfaceMode) => {
    onModeChange(mode);
    setIsOpen(false);
  };

  const handleModelSelect = (model: AIModel) => {
    onModelChange(model);
    setIsOpen(false);
  };

  const currentModeData = modes.find(m => m.id === currentMode);
  const currentModelData = models.find(m => m.id === currentModel);

  return (
    <div className="relative">
      <Button
        variant="outline"
        size="sm"
        onClick={() => setIsOpen(!isOpen)}
        className="flex items-center gap-2"
      >
        <Settings className="h-4 w-4" />
        {currentModeData?.name} + {currentModelData?.name}
      </Button>

      {isOpen && (
        <div className="absolute top-full left-0 mt-2 z-50 w-96">
          <Card className="shadow-lg border-2">
            <CardHeader className="pb-3">
              <CardTitle className="text-lg">AI Configuration</CardTitle>
              <CardDescription>
                Choose your interface and AI model
              </CardDescription>
            </CardHeader>
            <CardContent className="space-y-4">
              {/* Tab Navigation */}
              <div className="flex border-b">
                <button
                  className={`px-4 py-2 text-sm font-medium border-b-2 transition-colors ${
                    activeTab === 'interface'
                      ? 'border-primary text-primary'
                      : 'border-transparent text-muted-foreground hover:text-foreground'
                  }`}
                  onClick={() => setActiveTab('interface')}
                >
                  Interface
                </button>
                <button
                  className={`px-4 py-2 text-sm font-medium border-b-2 transition-colors ${
                    activeTab === 'model'
                      ? 'border-primary text-primary'
                      : 'border-transparent text-muted-foreground hover:text-foreground'
                  }`}
                  onClick={() => setActiveTab('model')}
                >
                  AI Model
                </button>
              </div>

              {/* Interface Selection */}
              {activeTab === 'interface' && (
                <div className="space-y-3">
                  {modes.map((mode) => {
                    const Icon = mode.icon;
                    const isSelected = mode.id === currentMode;
                    
                    return (
                      <div
                        key={mode.id}
                        className={`p-4 rounded-lg border-2 cursor-pointer transition-all hover:shadow-md ${
                          isSelected 
                            ? 'border-primary bg-primary/5' 
                            : 'border-muted hover:border-primary/50'
                        }`}
                        onClick={() => handleModeSelect(mode.id)}
                      >
                        <div className="flex items-start gap-3">
                          <div className={`p-2 rounded-lg ${mode.color} text-white`}>
                            <Icon className="h-5 w-5" />
                          </div>
                          <div className="flex-1">
                            <div className="flex items-center gap-2 mb-1">
                              <h3 className="font-semibold text-sm">{mode.name}</h3>
                              {isSelected && (
                                <Badge variant="secondary" className="text-xs">
                                  Current
                                </Badge>
                              )}
                            </div>
                            <p className="text-xs text-muted-foreground mb-2">
                              {mode.description}
                            </p>
                            <div className="space-y-1">
                              {mode.features.map((feature, index) => (
                                <div key={index} className="flex items-center gap-1 text-xs text-muted-foreground">
                                  <div className="w-1 h-1 bg-muted-foreground rounded-full"></div>
                                  {feature}
                                </div>
                              ))}
                            </div>
                          </div>
                        </div>
                      </div>
                    );
                  })}
                </div>
              )}

              {/* Model Selection */}
              {activeTab === 'model' && (
                <div className="space-y-3">
                  {models.map((model) => {
                    const Icon = model.icon;
                    const isSelected = model.id === currentModel;
                    
                    return (
                      <div
                        key={model.id}
                        className={`p-4 rounded-lg border-2 cursor-pointer transition-all hover:shadow-md ${
                          isSelected 
                            ? 'border-primary bg-primary/5' 
                            : 'border-muted hover:border-primary/50'
                        }`}
                        onClick={() => handleModelSelect(model.id)}
                      >
                        <div className="flex items-start gap-3">
                          <div className={`p-2 rounded-lg ${model.color} text-white`}>
                            <Icon className="h-5 w-5" />
                          </div>
                          <div className="flex-1">
                            <div className="flex items-center gap-2 mb-1">
                              <h3 className="font-semibold text-sm">{model.name}</h3>
                              {isSelected && (
                                <Badge variant="secondary" className="text-xs">
                                  Current
                                </Badge>
                              )}
                              <Badge variant="outline" className="text-xs">
                                {model.cost}
                              </Badge>
                            </div>
                            <p className="text-xs text-muted-foreground mb-2">
                              {model.description}
                            </p>
                            <div className="space-y-1">
                              {model.features.map((feature, index) => (
                                <div key={index} className="flex items-center gap-1 text-xs text-muted-foreground">
                                  <div className="w-1 h-1 bg-muted-foreground rounded-full"></div>
                                  {feature}
                                </div>
                              ))}
                            </div>
                          </div>
                        </div>
                      </div>
                    );
                  })}
                </div>
              )}
            </CardContent>
          </Card>
        </div>
      )}

      {/* Backdrop to close when clicking outside */}
      {isOpen && (
        <div 
          className="fixed inset-0 z-40" 
          onClick={() => setIsOpen(false)}
        />
      )}
    </div>
  );
}; 