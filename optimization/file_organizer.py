import tkinter as tk
from tkinter import ttk, messagebox, filedialog
import json
import os
import shutil
from datetime import datetime
import mimetypes
from typing import Dict, List, Tuple
import logging

class FileOrganizerGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("Desktop File Organizer")
        self.root.geometry("1200x800")
        
        # Configure logging
        logging.basicConfig(
            filename='file_organizer.log',
            level=logging.INFO,
            format='%(asctime)s - %(levelname)s - %(message)s'
        )
        
        # Default configuration for file organization
        self.default_config = {
            "categories": {
                "Development": [".py", ".java", ".cpp", ".h", ".cs", ".js", ".html", ".css"],
                "Documents": [".pdf", ".doc", ".docx", ".txt", ".xlsx", ".ppt", ".pptx"],
                "Images": [".jpg", ".jpeg", ".png", ".gif", ".bmp", ".svg"],
                "Videos": [".mp4", ".avi", ".mov", ".wmv", ".flv", ".mkv"],
                "Utilities": [".exe", ".msi", ".bat", ".cmd"],
                "Archives": [".zip", ".rar", ".7z", ".tar", ".gz"]
            }
        }
        
        self.load_config()
        self.create_gui()
        
    def load_config(self):
        """Load or create configuration file"""
        try:
            with open('organizer_config.json', 'r') as f:
                self.config = json.load(f)
        except FileNotFoundError:
            self.config = self.default_config
            with open('organizer_config.json', 'w') as f:
                json.dump(self.config, f, indent=4)
                
    def create_gui(self):
        """Create the main GUI elements"""
        # Create main frames
        self.top_frame = ttk.Frame(self.root)
        self.top_frame.pack(fill=tk.X, padx=5, pady=5)
        
        self.main_frame = ttk.Frame(self.root)
        self.main_frame.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        # Source directory selection
        ttk.Label(self.top_frame, text="Source Directory:").pack(side=tk.LEFT, padx=5)
        self.source_path = tk.StringVar()
        ttk.Entry(self.top_frame, textvariable=self.source_path, width=50).pack(side=tk.LEFT, padx=5)
        ttk.Button(self.top_frame, text="Browse", command=self.browse_source).pack(side=tk.LEFT, padx=5)
        
        # Create treeview for file preview
        self.create_treeview()
        
        # Create buttons frame
        self.buttons_frame = ttk.Frame(self.root)
        self.buttons_frame.pack(fill=tk.X, padx=5, pady=5)
        
        ttk.Button(self.buttons_frame, text="Analyze", command=self.analyze_directory).pack(side=tk.LEFT, padx=5)
        ttk.Button(self.buttons_frame, text="Apply Changes", command=self.apply_changes).pack(side=tk.LEFT, padx=5)
        
    def create_treeview(self):
        """Create the treeview for displaying files and their proposed moves"""
        # Create treeview with scrollbar
        self.tree_frame = ttk.Frame(self.main_frame)
        self.tree_frame.pack(fill=tk.BOTH, expand=True)
        
        self.treeview = ttk.Treeview(self.tree_frame, columns=("Current Location", "New Location", "Status"))
        self.treeview.heading("#0", text="File Name")
        self.treeview.heading("Current Location", text="Current Location")
        self.treeview.heading("New Location", text="Proposed Location")
        self.treeview.heading("Status", text="Status")
        
        # Configure column widths
        self.treeview.column("#0", width=200)
        self.treeview.column("Current Location", width=300)
        self.treeview.column("New Location", width=300)
        self.treeview.column("Status", width=100)
        
        # Add scrollbar
        scrollbar = ttk.Scrollbar(self.tree_frame, orient="vertical", command=self.treeview.yview)
        self.treeview.configure(yscrollcommand=scrollbar.set)
        
        self.treeview.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
    def browse_source(self):
        """Open directory browser dialog"""
        directory = filedialog.askdirectory()
        if directory:
            self.source_path.set(directory)
            
    def get_category(self, file_path: str) -> str:
        """Determine the category for a file based on its extension"""
        _, ext = os.path.splitext(file_path)
        ext = ext.lower()
        
        for category, extensions in self.config["categories"].items():
            if ext in extensions:
                return category
                
        return "Others"
        
    def analyze_directory(self):
        """Analyze the source directory and show proposed changes"""
        source_dir = self.source_path.get()
        if not source_dir or not os.path.exists(source_dir):
            messagebox.showerror("Error", "Please select a valid source directory")
            return
            
        # Clear current items
        for item in self.treeview.get_children():
            self.treeview.delete(item)
            
        # Walk through directory
        for root, _, files in os.walk(source_dir):
            for file in files:
                current_path = os.path.join(root, file)
                category = self.get_category(file)
                new_path = os.path.join(source_dir, category, file)
                
                # Add to treeview
                self.treeview.insert("", "end", text=file,
                                   values=(current_path, new_path, "Pending"))
                
    def apply_changes(self):
        """Apply the proposed changes with user confirmation"""
        if not self.treeview.get_children():
            messagebox.showinfo("Info", "No changes to apply")
            return
            
        if not messagebox.askyesno("Confirm", "Are you sure you want to apply these changes?"):
            return
            
        source_dir = self.source_path.get()
        
        # Process each file
        for item in self.treeview.get_children():
            current_path = self.treeview.item(item)["values"][0]
            new_path = self.treeview.item(item)["values"][1]
            
            try:
                # Create category directory if it doesn't exist
                os.makedirs(os.path.dirname(new_path), exist_ok=True)
                
                # Move file
                shutil.move(current_path, new_path)
                
                # Update status
                self.treeview.set(item, "Status", "Done")
                logging.info(f"Moved {current_path} to {new_path}")
                
            except Exception as e:
                self.treeview.set(item, "Status", "Failed")
                logging.error(f"Error moving {current_path}: {str(e)}")
                
        messagebox.showinfo("Success", "File organization completed")

def main():
    root = tk.Tk()
    app = FileOrganizerGUI(root)
    root.mainloop()

if __name__ == "__main__":
    main()
