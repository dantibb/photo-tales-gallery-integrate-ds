
# AI Interface Selection Feature

## Overview

The photo gallery now supports two different AI interaction modes:

1. **Anam Avatar Mode** - Interactive AI avatar with voice and visual responses
2. **Text Chat Mode** - Simple text-based AI conversation interface

## Features

### Anam Avatar Mode
- Interactive AI avatar with voice responses
- Visual avatar that responds to conversations
- Real-time voice interaction
- Advanced AI personality with custom prompts
- Integrated with anam.ai SDK
- Uses photographer conversation API

### Text Chat Mode
- Text-based chat interface
- Voice input support (speech recognition)
- Text-to-speech for AI responses
- Lightweight and fast interface
- **Same AI backend and prompts as avatar mode**
- Uses photographer conversation API
- **Automatically starts conversation when tag is selected**
- **All AI responses appear in chat conversation area**

## Usage

### Switching Between Modes
1. Look for the "AI Mode" button in the top controls of the photo gallery
2. Click the button to open the mode selector
3. Choose between "Anam Avatar" or "Text Chat"
4. Your preference is automatically saved and will be remembered

### Starting AI Conversations
- **Avatar Mode**: Click the microphone icon on any photo to start an AI interview in a modal
- **Text Mode**: Automatically starts conversation when a tag is selected, with all AI responses appearing in the chat area

### Features in Both Modes
- Voice input support (where supported by browser)
- Text-to-speech for AI responses
- Auto-speak toggle for AI responses
- Save conversation history
- Generate summaries and tags from conversations

## Technical Details

### Components
- `AIInterfaceSelector.tsx` - Mode selection interface
- `EmbeddedTextChat.tsx` - Embedded text chat interface for main view
- `AITextInterface.tsx` - Text-only AI chat interface (modal version)
- `AIInterview.tsx` - Avatar-based AI interview interface
- `AnamAvatar.tsx` - Anam.ai avatar integration

### State Management
- AI interface mode preference is stored in localStorage
- Mode selection affects both the summary card and interview modal
- Avatar is only active when in avatar mode
- Text mode shows embedded chat interface in main view when tag is selected
- Individual photo interview buttons only show in avatar mode
- Both modes use the same photographer conversation API for consistent AI responses

### Browser Compatibility
- Voice input: Chrome, Edge, Safari
- Text-to-speech: All modern browsers
- Anam avatar: Requires JavaScript and WebRTC support

## Configuration

The default mode is "avatar" but users can change this preference at any time. The selection is persisted across browser sessions. 