# Photo Tales Gallery

A modern photo gallery application with AI-powered interview capabilities and voice interaction features.

## Features

### 🎤 Voice Input for AI Chat
- **Voice Recognition**: Speak your responses to the AI interviewer using your microphone
- **Text-to-Speech**: Hear AI responses read aloud automatically
- **Auto-Speak**: Toggle automatic speech synthesis for AI responses
- **Visual Feedback**: Real-time indicators for listening and speaking states
- **Browser Support**: Works in Chrome, Edge, Safari, and other modern browsers

### 🖼️ Photo Management
- Upload and organize photos with metadata
- AI-powered image analysis and tagging
- Context and description management
- Search and filter capabilities

### 🤖 AI Interview System
- Interactive conversations about your photos
- AI-generated questions and insights
- Save conversations as context for future reference
- Voice-enabled interactions

### 📝 Enhanced AI Summaries
- **Comprehensive Summaries**: AI generates detailed, context-aware summaries that scale with available information
- **Smart Length**: Summaries automatically adjust length based on context and conversation depth
- **Rich Details**: Include setting, atmosphere, personal memories, and interesting stories
- **First-Person Voice**: Written in the photographer's own style and voice

## Voice Features Usage

### Starting Voice Input
1. Click the microphone button next to the text input field
2. Speak your response clearly
3. The recognized text will appear in the input field
4. Click "Send" or press Enter to submit

### Hearing AI Responses
- **Auto-Speak**: Enable the "Auto-speak AI responses" checkbox to hear responses automatically
- **Manual Play**: Click the speaker icon next to any AI message to hear it
- **Stop Speaking**: Click the speaker icon again while speaking to stop

### Browser Compatibility
Voice input requires a modern browser with Web Speech API support:
- ✅ Chrome (recommended)
- ✅ Edge
- ✅ Safari
- ❌ Firefox (limited support)

## Getting Started

### Prerequisites
- Node.js 18+ 
- Python 3.8+ (for backend)
- Modern web browser with microphone access

### Installation

1. **Frontend Setup**
```bash
npm install
npm run dev
```

2. **Backend Setup**
```bash
cd backend
pip install -r requirements.txt
python main.py
```

3. **Environment Configuration**
```bash
cp backend/config.env.example backend/config.env
# Edit config.env with your OpenAI API key and other settings
```

### Usage

1. Start both frontend and backend servers
2. Open the application in your browser
3. Grant microphone permissions when prompted
4. Upload photos and start AI interviews
5. Use voice input for natural conversations

## Voice Input Tips

- **Clear Speech**: Speak clearly and at a normal pace
- **Quiet Environment**: Minimize background noise for better recognition
- **Browser Permissions**: Allow microphone access when prompted
- **Language**: Currently supports English (en-US)
- **Punctuation**: The AI will add appropriate punctuation to your speech

## Technical Details

### Voice Recognition
- Uses Web Speech API (SpeechRecognition)
- Supports continuous speech recognition
- Automatic language detection (en-US)
- Error handling and fallback options

### Text-to-Speech
- Uses Web Speech API (SpeechSynthesis)
- Configurable speech rate and language
- Automatic speech cancellation for new responses
- Visual feedback during speech synthesis

### AI Summary Generation
- **Context-Aware**: Incorporates all available context and conversation history
- **Adaptive Length**: Scales summary length based on available information
- **Rich Content**: Includes setting, atmosphere, personal memories, and stories
- **Voice Matching**: Maintains the photographer's personal style and tone

### Privacy & Security
- Voice processing happens locally in the browser
- No voice data is sent to external servers
- Microphone access is optional and can be revoked
- All voice features can be disabled

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Test voice features in multiple browsers
5. Submit a pull request

## License

This project is licensed under the MIT License.
