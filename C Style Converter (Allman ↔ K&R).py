import tkinter as tk
from tkinter import ttk, scrolledtext, messagebox
import re
from typing import Optional
import json
import os

class StyleConverter:
    @staticmethod
    def to_allman(code: str) -> str:
        """Convert code from K&R style to Allman style while preserving exact indentation."""
        try:
            lines = code.split('\n')
            formatted_lines = []
            
            for i, line in enumerate(lines):
                # Get the original indentation
                indent = len(line) - len(line.lstrip())
                stripped = line.lstrip()
                
                # If this line ends with '{', add it as a new line with original indent + 8
                if stripped.endswith('{'):
                    # Add the current line without the {
                    base_line = line.rstrip()[:-1].rstrip()
                    if base_line:  # Only add if there's content
                        formatted_lines.append(base_line)
                    # Add the { on a new line with same indent
                    formatted_lines.append(' ' * indent + '{')
                else:
                    formatted_lines.append(line)
                    
            return '\n'.join(formatted_lines)
            
        except Exception as e:
            raise ValueError(f"Error converting to Allman style: {str(e)}")

    @staticmethod
    def to_knr(code: str) -> str:
        """Convert code from Allman style to K&R style."""
        try:
            lines = code.split('\n')
            formatted_lines = []
            skip_next = False
            
            for i, line in enumerate(lines):
                if skip_next:
                    skip_next = False
                    continue
                    
                stripped = line.lstrip()
                
                # If next line is just a '{', combine them
                if (i < len(lines) - 1 and 
                    lines[i + 1].strip() == '{'):
                    formatted_lines.append(line.rstrip() + ' {')
                    skip_next = True
                else:
                    formatted_lines.append(line)
            
            return '\n'.join(formatted_lines)
            
        except Exception as e:
            raise ValueError(f"Error converting to K&R style: {str(e)}")

    @staticmethod
    def to_knr(code: str) -> str:
        """Convert code from Allman style to K&R style.
        
        Args:
            code (str): Input code in Allman style
            
        Returns:
            str: Converted code in K&R style
        """
        try:
            lines = code.split('\n')
            formatted_lines = []
            skip_next = False
            in_multiline_comment = False
            
            for i, line in enumerate(lines):
                if skip_next:
                    skip_next = False
                    continue
                
                # Handle multi-line comments
                if '/*' in line:
                    in_multiline_comment = True
                if '*/' in line:
                    in_multiline_comment = False
                    
                stripped = line.lstrip()
                
                # If next line is just an opening brace (and not in comment), combine them
                if (i < len(lines) - 1 and 
                    lines[i + 1].strip() == '{' and 
                    not in_multiline_comment):
                    formatted_lines.append(line.rstrip() + ' {')
                    skip_next = True
                else:
                    formatted_lines.append(line)
            
            return '\n'.join(formatted_lines)
        except Exception as e:
            raise ValueError(f"Error converting to K&R style: {str(e)}")

class StyleConverterGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("Code Style Converter")
        self.root.geometry("800x600")
        
        # Load preferences
        self.preferences = self.load_preferences()
        
        # Create main frame with theme
        style = ttk.Style()
        self.current_theme = self.preferences.get('theme', 'default')
        if self.current_theme != 'default':
            style.theme_use(self.current_theme)
            
        main_frame = ttk.Frame(root, padding="10")
        main_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        # Configure grid weights
        root.columnconfigure(0, weight=1)
        root.rowconfigure(0, weight=1)
        main_frame.columnconfigure(1, weight=1)
        main_frame.rowconfigure(1, weight=1)
        main_frame.rowconfigure(4, weight=1)
        
        # Menu bar
        self.create_menu()
        
        # Create widgets
        ttk.Label(main_frame, text="Input Code:").grid(row=0, column=0, columnspan=2, sticky=tk.W)
        
        self.input_text = scrolledtext.ScrolledText(
            main_frame, width=80, height=15, wrap=tk.NONE,
            font=self.preferences.get('font', ('Courier', 10))
        )
        self.input_text.grid(row=1, column=0, columnspan=2, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        # Add horizontal scrollbar for input
        input_hscrollbar = ttk.Scrollbar(main_frame, orient=tk.HORIZONTAL, command=self.input_text.xview)
        input_hscrollbar.grid(row=2, column=0, columnspan=2, sticky=(tk.W, tk.E))
        self.input_text.configure(xscrollcommand=input_hscrollbar.set)
        
        # Buttons frame
        button_frame = ttk.Frame(main_frame)
        button_frame.grid(row=3, column=0, columnspan=2, pady=10)
        
        ttk.Button(button_frame, text="Convert to Allman", 
                  command=self.convert_to_allman).grid(row=0, column=0, padx=5)
        ttk.Button(button_frame, text="Convert to K&R", 
                  command=self.convert_to_knr).grid(row=0, column=1, padx=5)
        ttk.Button(button_frame, text="Clear All", 
                  command=self.clear_all).grid(row=0, column=2, padx=5)
        ttk.Button(button_frame, text="Copy Output", 
                  command=self.copy_output).grid(row=0, column=3, padx=5)
        
        ttk.Label(main_frame, text="Output Code:").grid(row=4, column=0, columnspan=2, sticky=tk.W)
        
        self.output_text = scrolledtext.ScrolledText(
            main_frame, width=80, height=15, wrap=tk.NONE,
            font=self.preferences.get('font', ('Courier', 10))
        )
        self.output_text.grid(row=5, column=0, columnspan=2, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        # Add horizontal scrollbar for output
        output_hscrollbar = ttk.Scrollbar(main_frame, orient=tk.HORIZONTAL, command=self.output_text.xview)
        output_hscrollbar.grid(row=6, column=0, columnspan=2, sticky=(tk.W, tk.E))
        self.output_text.configure(xscrollcommand=output_hscrollbar.set)
        
        # Status bar
        self.status_var = tk.StringVar()
        self.status_bar = ttk.Label(main_frame, textvariable=self.status_var, relief=tk.SUNKEN)
        self.status_bar.grid(row=7, column=0, columnspan=2, sticky=(tk.W, tk.E))
        
        # Bind keyboard shortcuts
        self.root.bind('<Control-a>', lambda e: self.convert_to_allman())
        self.root.bind('<Control-k>', lambda e: self.convert_to_knr())
        self.root.bind('<Control-l>', lambda e: self.clear_all())
        self.root.bind('<Control-c>', lambda e: self.copy_output())
        
        # Set initial status
        self.status_var.set("Ready")

    def create_menu(self):
        menubar = tk.Menu(self.root)
        self.root.config(menu=menubar)
        
        # File menu
        file_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="File", menu=file_menu)
        file_menu.add_command(label="New", command=self.clear_all, accelerator="Ctrl+L")
        file_menu.add_command(label="Open...", command=self.open_file)
        file_menu.add_command(label="Save Output As...", command=self.save_output)
        file_menu.add_separator()
        file_menu.add_command(label="Exit", command=self.root.quit)
        
        # Edit menu
        edit_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="Edit", menu=edit_menu)
        edit_menu.add_command(label="Copy Output", command=self.copy_output, accelerator="Ctrl+C")
        edit_menu.add_separator()
        edit_menu.add_command(label="Convert to Allman", command=self.convert_to_allman, accelerator="Ctrl+A")
        edit_menu.add_command(label="Convert to K&R", command=self.convert_to_knr, accelerator="Ctrl+K")
        
        # View menu
        view_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="View", menu=view_menu)
        
        # Theme submenu
        theme_menu = tk.Menu(view_menu, tearoff=0)
        view_menu.add_cascade(label="Theme", menu=theme_menu)
        
        # Add available themes
        style = ttk.Style()
        for theme in style.theme_names():
            theme_menu.add_radiobutton(
                label=theme,
                variable=tk.StringVar(value=self.current_theme),
                value=theme,
                command=lambda t=theme: self.change_theme(t)
            )
    
    def load_preferences(self) -> dict:
        """Load user preferences from JSON file."""
        try:
            if os.path.exists('preferences.json'):
                with open('preferences.json', 'r') as f:
                    return json.load(f)
        except Exception as e:
            print(f"Error loading preferences: {e}")
        return {}
    
    def save_preferences(self):
        """Save user preferences to JSON file."""
        try:
            with open('preferences.json', 'w') as f:
                json.dump(self.preferences, f)
        except Exception as e:
            print(f"Error saving preferences: {e}")
    
    def change_theme(self, theme_name: str):
        """Change the application theme."""
        try:
            style = ttk.Style()
            style.theme_use(theme_name)
            self.current_theme = theme_name
            self.preferences['theme'] = theme_name
            self.save_preferences()
            self.status_var.set(f"Theme changed to {theme_name}")
        except Exception as e:
            self.status_var.set(f"Error changing theme: {str(e)}")
    
    def convert_to_allman(self):
        """Convert input code to Allman style."""
        try:
            input_code = self.input_text.get("1.0", tk.END)
            output_code = StyleConverter.to_allman(input_code)
            self.output_text.delete("1.0", tk.END)
            self.output_text.insert("1.0", output_code)
            self.status_var.set("Successfully converted to Allman style")
        except Exception as e:
            self.status_var.set(f"Error: {str(e)}")
            messagebox.showerror("Error", str(e))
    
    def convert_to_knr(self):
        """Convert input code to K&R style."""
        try:
            input_code = self.input_text.get("1.0", tk.END)
            output_code = StyleConverter.to_knr(input_code)
            self.output_text.delete("1.0", tk.END)
            self.output_text.insert("1.0", output_code)
            self.status_var.set("Successfully converted to K&R style")
        except Exception as e:
            self.status_var.set(f"Error: {str(e)}")
            messagebox.showerror("Error", str(e))
    
    def clear_all(self):
        """Clear both input and output text areas."""
        self.input_text.delete("1.0", tk.END)
        self.output_text.delete("1.0", tk.END)
        self.status_var.set("Cleared all text")
    
    def copy_output(self):
        """Copy output text to clipboard."""
        output_code = self.output_text.get("1.0", tk.END).rstrip()
        self.root.clipboard_clear()
        self.root.clipboard_append(output_code)
        self.status_var.set("Output copied to clipboard")
    
    def open_file(self):
        """Open a file and load its contents into the input text area."""
        from tkinter import filedialog
        
        file_path = filedialog.askopenfilename(
            filetypes=[
                ("All Files", "*.*"),
                ("Text Files", "*.txt"),
                ("Python Files", "*.py"),
                ("C/C++ Files", "*.c;*.cpp;*.h;*.hpp"),
                ("Java Files", "*.java")
            ]
        )
        
        if file_path:
            try:
                with open(file_path, 'r') as f:
                    content = f.read()
                self.input_text.delete("1.0", tk.END)
                self.input_text.insert("1.0", content)
                self.status_var.set(f"Opened file: {file_path}")
            except Exception as e:
                self.status_var.set(f"Error opening file: {str(e)}")
                messagebox.showerror("Error", f"Could not open file: {str(e)}")
    
    def save_output(self):
        """Save the output text to a file."""
        from tkinter import filedialog
        
        file_path = filedialog.asksaveasfilename(
            defaultextension=".txt",
            filetypes=[
                ("All Files", "*.*"),
                ("Text Files", "*.txt"),
                ("Python Files", "*.py"),
                ("C/C++ Files", "*.c;*.cpp;*.h;*.hpp"),
                ("Java Files", "*.java")
            ]
        )
        
        if file_path:
            try:
                content = self.output_text.get("1.0", tk.END)
                with open(file_path, 'w') as f:
                    f.write(content)
                self.status_var.set(f"Saved output to: {file_path}")
            except Exception as e:
                self.status_var.set(f"Error saving file: {str(e)}")
                messagebox.showerror("Error", f"Could not save file: {str(e)}")

def create_help_window(self):
    """Create a help window with keyboard shortcuts and usage information."""
    help_window = tk.Toplevel(self.root)
    help_window.title("Help")
    help_window.geometry("400x300")
    
    help_text = """
    Keyboard Shortcuts:
    • Ctrl+A: Convert to Allman style
    • Ctrl+K: Convert to K&R style
    • Ctrl+L: Clear all text
    • Ctrl+C: Copy output to clipboard
    
    Usage:
    1. Enter or paste code in the input text area
    2. Click 'Convert to Allman' or 'Convert to K&R' to change the brace style
    3. The converted code will appear in the output text area
    4. Use 'Copy Output' to copy the result to clipboard
    
    File Operations:
    • Use File > Open to load code from a file
    • Use File > Save Output As to save the converted code
    
    Themes:
    • Change the application theme via View > Theme
    """
    
    text_widget = scrolledtext.ScrolledText(
        help_window, wrap=tk.WORD, font=('TkDefaultFont', 10)
    )
    text_widget.pack(expand=True, fill='both', padx=10, pady=10)
    text_widget.insert('1.0', help_text)
    text_widget.configure(state='disabled')

def main():
    root = tk.Tk()
    app = StyleConverterGUI(root)
    root.mainloop()

if __name__ == "__main__":
    main()