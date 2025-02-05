import tkinter as tk
from tkinter import scrolledtext, messagebox
from typing import Optional
import re

class StyleConverter:
    @staticmethod
    def to_allman(code: str) -> str:
        """Convert code from K&R style to Allman style while preserving exact indentation."""
        try:
            lines = code.split('\n')
            formatted_lines = []
            
            for i, line in enumerate(lines):
                indent = len(line) - len(line.lstrip())
                stripped = line.lstrip()
                
                if stripped.endswith('{'):
                    base_line = line.rstrip()[:-1].rstrip()
                    if base_line:
                        formatted_lines.append(base_line)
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

    @staticmethod
    def remove_single_line_comments(code: str) -> str:
        """Remove all single-line comments (//) from the code."""
        try:
            # Split into lines to handle each line separately
            lines = code.split('\n')
            result_lines = []
            
            for line in lines:
                # Find position of // that isn't inside a string
                in_string = False
                string_char = None
                i = 0
                while i < len(line):
                    if line[i] in '"\'':
                        if not in_string:
                            in_string = True
                            string_char = line[i]
                        elif string_char == line[i]:
                            in_string = False
                    elif line[i:i+2] == '//' and not in_string:
                        line = line[:i].rstrip()
                        break
                    i += 1
                result_lines.append(line)
            
            return '\n'.join(result_lines)
        except Exception as e:
            raise ValueError(f"Error removing single-line comments: {str(e)}")

    @staticmethod
    def remove_multi_line_comments(code: str) -> str:
        """Remove all multi-line comments (/* ... */) from the code."""
        try:
            # Use regex to remove multi-line comments while preserving newlines
            pattern = r'/\*.*?\*/'
            result = re.sub(pattern, '', code, flags=re.DOTALL)
            return result
        except Exception as e:
            raise ValueError(f"Error removing multi-line comments: {str(e)}")

    @staticmethod
    def remove_all_comments(code: str) -> str:
        """Remove both single-line and multi-line comments from the code."""
        try:
            # First remove multi-line comments, then single-line comments
            code = StyleConverter.remove_multi_line_comments(code)
            code = StyleConverter.remove_single_line_comments(code)
            return code
        except Exception as e:
            raise ValueError(f"Error removing all comments: {str(e)}")

    @staticmethod
    def remove_braces_single_statements(code: str) -> str:
        """Remove curly braces from single non-blocking statements."""
        try:
            lines = code.split('\n')
            result_lines = []
            i = 0
            
            while i < len(lines):
                current_line = lines[i].rstrip()
                
                # Check for control statements (if, for, while) followed by braces
                if re.search(r'\b(if|for|while)\s*\([^)]*\)', current_line):
                    # Handle K&R style (brace on same line)
                    if current_line.rstrip().endswith('{'):
                        base_line = current_line.rstrip()[:-1].rstrip()
                        
                        # Collect all lines between braces
                        body_lines = []
                        brace_count = 1
                        j = i + 1
                        
                        while j < len(lines) and brace_count > 0:
                            line = lines[j]
                            if '{' in line:
                                brace_count += 1
                            if '}' in line:
                                brace_count -= 1
                            if brace_count > 0:
                                body_lines.append(line)
                            j += 1
                        
                        # If there's only one non-comment statement
                        code_lines = [line for line in body_lines if not line.strip().startswith('//') 
                                    and not line.strip().startswith('/*') 
                                    and not line.strip().startswith('*')
                                    and line.strip()]
                        
                        if len(code_lines) == 1:
                            result_lines.append(base_line)
                            result_lines.append(code_lines[0])
                            i = j  # Skip to after the closing brace
                            continue
                            
                    # Handle Allman style (brace on next line)
                    elif i + 1 < len(lines) and lines[i + 1].strip() == '{':
                        # Get the indentation of the control statement
                        base_indent = len(current_line) - len(current_line.lstrip())
                        
                        # Skip the opening brace line
                        i += 1
                        
                        # Collect all lines between braces
                        body_lines = []
                        brace_count = 1
                        j = i + 1
                        
                        while j < len(lines) and brace_count > 0:
                            line = lines[j]
                            if '{' in line:
                                brace_count += 1
                            if '}' in line:
                                brace_count -= 1
                            if brace_count > 0:
                                body_lines.append(line)
                            j += 1
                        
                        # If there's only one non-comment statement
                        code_lines = [line for line in body_lines if not line.strip().startswith('//') 
                                    and not line.strip().startswith('/*') 
                                    and not line.strip().startswith('*')
                                    and line.strip()]
                        
                        if len(code_lines) == 1:
                            result_lines.append(current_line)
                            result_lines.append(code_lines[0])
                            i = j  # Skip to after the closing brace
                            continue
                
                result_lines.append(current_line)
                i += 1
            
            return '\n'.join(result_lines)
            
        except Exception as e:
            raise ValueError(f"Error removing braces: {str(e)}")

class StyleConverterGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("Code Style Converter")
        self.root.geometry("800x600")
        
        # Create main frame
        main_frame = tk.Frame(root, padx=10, pady=10)
        main_frame.pack(fill=tk.BOTH, expand=True)
        
        # Create widgets
        tk.Label(main_frame, text="Input Code:").pack(anchor=tk.W)
        
        self.input_text = scrolledtext.ScrolledText(
            main_frame, width=80, height=15, wrap=tk.NONE,
            font=('Courier', 10)
        )
        self.input_text.pack(fill=tk.BOTH, expand=True)
        
        # Style conversion buttons frame
        style_button_frame = tk.Frame(main_frame)
        style_button_frame.pack(pady=5)
        
        tk.Button(style_button_frame, text="Convert to Allman", 
                command=self.convert_to_allman).pack(side=tk.LEFT, padx=5)
        tk.Button(style_button_frame, text="Convert to K&R", 
                command=self.convert_to_knr).pack(side=tk.LEFT, padx=5)

        # Brace removal frame
        brace_frame = tk.Frame(main_frame)
        brace_frame.pack(pady=5)
        
        tk.Button(brace_frame, text="Remove Single Statement Braces", 
                command=self.remove_single_braces).pack(side=tk.LEFT, padx=5)

        # Comment removal buttons frame
        comment_button_frame = tk.Frame(main_frame)
        comment_button_frame.pack(pady=5)
        
        tk.Button(comment_button_frame, text="Remove Single-Line Comments", 
                command=self.remove_single_comments).pack(side=tk.LEFT, padx=5)
        tk.Button(comment_button_frame, text="Remove Multi-Line Comments", 
                command=self.remove_multi_comments).pack(side=tk.LEFT, padx=5)
        tk.Button(comment_button_frame, text="Remove All Comments", 
                command=self.remove_all_comments).pack(side=tk.LEFT, padx=5)

        # Utility buttons frame
        util_button_frame = tk.Frame(main_frame)
        util_button_frame.pack(pady=5)
        
        tk.Button(util_button_frame, text="Clear All", 
                command=self.clear_all).pack(side=tk.LEFT, padx=5)
        tk.Button(util_button_frame, text="Copy Output", 
                command=self.copy_output).pack(side=tk.LEFT, padx=5)
        
        tk.Label(main_frame, text="Output Code:").pack(anchor=tk.W)
        
        self.output_text = scrolledtext.ScrolledText(
            main_frame, width=80, height=15, wrap=tk.NONE,
            font=('Courier', 10), state='disabled'
        )
        self.output_text.pack(fill=tk.BOTH, expand=True)
        
        # Bind keyboard shortcuts
        self.root.bind('<Control-a>', lambda e: self.convert_to_allman())
        self.root.bind('<Control-k>', lambda e: self.convert_to_knr())
        self.root.bind('<Control-l>', lambda e: self.clear_all())
        self.root.bind('<Control-c>', lambda e: self.copy_output())
        self.root.bind('<Control-s>', lambda e: self.remove_single_comments())
        self.root.bind('<Control-m>', lambda e: self.remove_multi_comments())
        self.root.bind('<Control-r>', lambda e: self.remove_all_comments())
        self.root.bind('<Control-b>', lambda e: self.remove_single_braces())
    
    def set_output_text(self, text: str):
        """Helper method to set text in the read-only output widget."""
        self.output_text.config(state='normal')
        self.output_text.delete("1.0", tk.END)
        self.output_text.insert("1.0", text)
        self.output_text.config(state='disabled')
    
    def convert_to_allman(self):
        """Convert input code to Allman style."""
        try:
            input_code = self.input_text.get("1.0", tk.END)
            output_code = StyleConverter.to_allman(input_code)
            self.set_output_text(output_code)
        except Exception as e:
            messagebox.showerror("Error", str(e))
    
    def convert_to_knr(self):
        """Convert input code to K&R style."""
        try:
            input_code = self.input_text.get("1.0", tk.END)
            output_code = StyleConverter.to_knr(input_code)
            self.set_output_text(output_code)
        except Exception as e:
            messagebox.showerror("Error", str(e))
    
    def remove_single_comments(self):
        """Remove single-line comments from the code."""
        try:
            input_code = self.input_text.get("1.0", tk.END)
            output_code = StyleConverter.remove_single_line_comments(input_code)
            self.set_output_text(output_code)
        except Exception as e:
            messagebox.showerror("Error", str(e))

    def remove_multi_comments(self):
        """Remove multi-line comments from the code."""
        try:
            input_code = self.input_text.get("1.0", tk.END)
            output_code = StyleConverter.remove_multi_line_comments(input_code)
            self.set_output_text(output_code)
        except Exception as e:
            messagebox.showerror("Error", str(e))

    def remove_all_comments(self):
        """Remove all comments from the code."""
        try:
            input_code = self.input_text.get("1.0", tk.END)
            output_code = StyleConverter.remove_all_comments(input_code)
            self.set_output_text(output_code)
        except Exception as e:
            messagebox.showerror("Error", str(e))
    
    def remove_single_braces(self):
        """Remove curly braces from single non-blocking statements."""
        try:
            input_code = self.input_text.get("1.0", tk.END)
            output_code = StyleConverter.remove_braces_single_statements(input_code)
            self.set_output_text(output_code)
        except Exception as e:
            messagebox.showerror("Error", str(e))
    
    def clear_all(self):
        """Clear both input and output text areas."""
        self.input_text.delete("1.0", tk.END)
        self.set_output_text("")
        
    def copy_output(self):
        """Copy output text to clipboard."""
        output_code = self.output_text.get("1.0", tk.END).rstrip()
        self.root.clipboard_clear()
        self.root.clipboard_append(output_code)

def main():
    root = tk.Tk()
    app = StyleConverterGUI(root)
    root.mainloop()

if __name__ == "__main__":
    main()
