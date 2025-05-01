import sys
import os
sys.path.append(os.path.dirname(__file__))

import tkinter as tk
from tkinter import ttk, scrolledtext
from network_manager import NetworkManager
import threading

class UnifiedServer:
    def __init__(self):
        self.root = tk.Tk()
        self.root.title("GoPirate Server")
        
        # Create network manager first
        self.network_manager = NetworkManager()
        
        # Then setup UI
        self.setup_ui()
        
    def setup_ui(self):
        # Create server log display
        self.log_display = scrolledtext.ScrolledText(self.root)
        self.log_display.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # Add server status label
        self.status_label = ttk.Label(self.root, text="Server Running...")
        self.status_label.pack(pady=5)
        
        # Start server in separate thread
        threading.Thread(target=self.network_manager.run, daemon=True).start()
        
    def log_message(self, message: str):
        self.log_display.configure(state='normal')
        self.log_display.insert(tk.END, f"{message}\n")
        self.log_display.configure(state='disabled')
        self.log_display.see(tk.END)
        
    def run(self):
        self.root.mainloop()

if __name__ == "__main__":
    server = UnifiedServer()
    server.run()