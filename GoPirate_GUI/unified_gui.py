import tkinter as tk
from game_frame import GameFrame
from chatbot_frame import ChatbotFrame
from multiplayer_frame import MultiplayerFrame

class UnifiedGUI:
    def __init__(self):
        self.root = tk.Tk()
        self.root.title("GoPirate Unified Interface")
        self.setup_ui()
        
    def setup_ui(self):
        # Create main container
        main_container = tk.Frame(self.root)
        main_container.pack(expand=True, fill=tk.BOTH, padx=5, pady=5)
        
        # Create left panel for game and chatbot
        left_panel = tk.Frame(main_container)
        left_panel.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        
        # Add game frame
        game_frame = GameFrame(left_panel)
        game_frame.pack(fill=tk.BOTH, expand=True, pady=(0, 5))
        
        # Add chatbot frame
        chatbot_frame = ChatbotFrame(left_panel)
        chatbot_frame.pack(fill=tk.BOTH, expand=True)
        
        # Add multiplayer chat frame on right
        multiplayer_frame = MultiplayerFrame(main_container)
        multiplayer_frame.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True, padx=(5, 0))
        
    def run(self):
        self.root.mainloop()

if __name__ == "__main__":
    app = UnifiedGUI()
    app.run()
