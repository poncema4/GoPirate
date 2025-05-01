import tkinter as tk
from tkinter import scrolledtext
from client_connection import ClientConnection

class MultiplayerFrame(tk.Frame):
    def __init__(self, master):
        super().__init__(master, relief=tk.RAISED, borderwidth=1)
        self.client = ClientConnection()
        self.setup_ui()
        
    def setup_ui(self):
        # Chat title
        tk.Label(self, text="Multiplayer Chat", font=('Arial', 12, 'bold')).pack(pady=5)
        
        # Chat display
        self.chat_display = scrolledtext.ScrolledText(self, height=30, width=40)
        self.chat_display.pack(padx=5, pady=5)
        
        # Input area
        self.input_area = tk.Entry(self)
        self.input_area.pack(fill=tk.X, padx=5, pady=5)
        self.input_area.bind('<Return>', lambda e: self.send_message())
        
        # Send button
        tk.Button(self, text="Send", command=self.send_message).pack(pady=5)
        
        # Start receiving messages
        self.start_receiving()
        
    def send_message(self):
        message = self.input_area.get().strip()
        if not message:
            return
            
        self.client.send_message(message)
        self.input_area.delete(0, tk.END)
        
    def start_receiving(self):
        def update_chat():
            messages = self.client.get_new_messages()
            for msg in messages:
                self.chat_display.insert(tk.END, f"{msg}\n")
                self.chat_display.see(tk.END)
            self.after(100, update_chat)
        
        update_chat()
