# GoPirate

A multiplayer battle game with an integrated chat system and customer service chatbot.

## Features

- **JJK Battle Game**: A turn-based multiplayer battle system featuring characters from Jujutsu Kaisen
  - Character selection system
  - Combat mechanics including attack, defend, and special abilities
  - Status effects (poison, stun, defense boost)
  - Turn-based battle system

- **Chat System**
  - Real-time multiplayer chat
  - System messages for player joins/leaves
  - Color-coded messages for different users

- **Customer Service Chatbot**
  - AI-powered responses
  - Help system
  - Assist players with mid-game question
  - Update unknown-queries to provide enhanced updates in the future

## Requirements

```bash
pip install tkinter
pip install socket
pip install threading
pip install json
pip install typing
```

## Project Structure

```
GoPirate/
├── GoPirate_GUI/
│   ├── chat_client.py          # Main client application
│   ├── chat_server.py          # Server application
│   └── network_manager.py      # Network handling
├── Chat_Bot/
│   └── chat_bot.py        # Chatbot implementation
├── JJK_Game/
│   ├── battle_manager.py       # Game logic
│   └── character_factory.py    # Character creation
├── GUI_Chat/
|   ├── chat_client.py      # Reference chat application
|   └── chat_server.py      # Reference server application
├── README.md
├── uml_diagram.wsd       # UML class diagram
├── uml_diagram_qr_code.png         # QR-code for the UML diagram
├── uml_diagram.png         # UML diagram image
└──
```

## How to Run

1. Start the server:
```bash
python GoPirate_GUI/chat_server.py
```

2. Start the client(s):
```bash
python GoPirate_GUI/chat_client.py
```

3. Enter your name when prompted and connect to the server

4. Once 2-5 players have joined, the "host" client can press start game

## Game Instructions

1. **Character Selection**
   - Choose from: Gojo, Sukuna, Megumi, Nanami, or Nobara
   - Each character has unique abilities

2. **Combat**
   - Players take turns performing actions
   - Available actions: Attack, Defend, Special
   - Use the chat to communicate with other players

3. **Special Abilities**
   - Gojo: Domain Expansion
   - Sukuna: Malevolent Shrine
   - Megumi: Divine Dogs
   - Nanami: Ratio Technique
   - Nobara: Straw Doll Technique

## Additional Features

1. **Real-time Status Updates**
   - HP display
   - Status effects visualization
   - Turn order tracking

2. **Enhanced UI**
   - Color-coded messages
   - Scrollable chat and game logs
   - Intuitive control buttons

3. **Error Handling**
   - Connection management
   - Invalid input protection
   - Graceful disconnection handling