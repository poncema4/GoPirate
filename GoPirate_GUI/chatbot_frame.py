import tkinter as tk
from tkinter import scrolledtext
import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from Chat_Bot.chat_bot import Chatbot

class ChatbotFrame(tk.Frame):
    def __init__(self, master):
        super().__init__(master, relief=tk.RAISED, borderwidth=1)
        self.chatbot = Chatbot()
        self.setup_ui()
        
    def setup_ui(self):
        # Chatbot title
        tk.Label(self, text="Customer Service Bot", font=('Arial', 12, 'bold')).pack(pady=5)
        
        # Chat display area
        self.chat_display = scrolledtext.ScrolledText(self, height=20, width=60)
        self.chat_display.pack(padx=5, pady=5)
        
        # Input area
        self.input_area = tk.Entry(self)
        self.input_area.pack(fill=tk.X, padx=5, pady=5)
        self.input_area.bind('<Return>', lambda e: self.send_message())
        
        # Send button
        tk.Button(self, text="Send", command=self.send_message).pack(pady=5)
        
        # Initial message
        self.chat_display.insert(tk.END, "Welcome to PirateEase Chatbot!\nType 'help' for assistance or 'bye' to exit.\n\n")
        self.chat_display.see(tk.END)
        
    def send_message(self):
        message = self.input_area.get().strip()
        if not message:
            return
            
        # Display user message
        self.chat_display.insert(tk.END, f"User: {message}\n")
        
        # Get chatbot response
        response = self.chatbot.process_query(message)
        self.chat_display.insert(tk.END, f"Chatbot: {response}\n\n")
        
        # Clear input and scroll to bottom
        self.input_area.delete(0, tk.END)
        self.chat_display.see(tk.END)
