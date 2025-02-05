import tkinter as tk
from tkinter import scrolledtext, messagebox, ttk
from typing import Optional, Tuple, List, Callable
import threading
import re

class StyleConverter:
    @staticmethod
    def is_brace_in_code(line: str, pos: int) -> bool:
        """
        Check if a brace at given position is in actual code (not in string/comment).
        
        Args:
            line: The line of code to check
            pos: Position of the brace in the line
            
        Returns:
            bool: True if brace is in code, False if in string or comment
        """
        in_string = False
        string_char = None
        i = 0
        while i < pos:
            if line[i] in '"\'':
                if not in_string:
                    in_string = True
                    string_char = line[i]
                elif string_char == line[i]:
                    in_string = False
            elif line[i:i+2] == '//' and not in_string:
                return False
            i += 1
        return not in_string

    @staticmethod
    def find_matching_brace(lines: List[str], start_line: int, start_pos: int) -> Tuple[int, int]:
        """
        Find the matching closing brace for an opening brace.
        
        Args:
            lines: List of code lines
            start_line: Line number where search begins
            start_pos: Position in start_line where search begins
            
        Returns:
            Tuple[int, int]: Line number and position of matching brace
        """
        brace_count = 1
        current_line = start_line
        current_pos = start_pos + 1

        while current_line < len(lines):
            line = lines[current_line]
            while current_pos < len(line):
                if StyleConverter.is_brace_in_code(line, current_pos):
                    if line[current_pos] == '{':
                        brace_count += 1
                    elif line[current_pos] == '}':
                        brace_count -= 1
                        if brace_count == 0:
                            return current_line, current_pos
                current_pos += 1
            current_line += 1
            current_pos = 0

        raise ValueError("No matching brace found")

    @staticmethod
    def to_allman(code: str) -> str:
        """
        Convert code to Allman style while preserving indentation and handling comments.
        
        Args:
            code: Input code string
            
        Returns:
            str: Code formatted in Allman style
        """
        try:
            lines = code.split('\n')
            formatted_lines = []
            i = 0
            
            while i < len(lines):
                line = lines[i]
                indent = len(line) - len(line.lstrip())
                stripped = line.lstrip()
                
                # Handle control statements without braces
                if (re.search(r'\b(if|for|while)\s*\([^)]*\)', stripped) and 
                    not stripped.endswith('{') and 
                    (i + 1 >= len(lines) or not lines[i + 1].strip() == '{')):
                    formatted_lines.append(line)
                    if i + 1 < len(lines):
                        formatted_lines.append(lines[i + 1])
                    i += 2
                    continue
                
                # Handle lines ending with braces
                if stripped.endswith('{'):
                    base_line = line.rstrip()[:-1].rstrip()
                    if base_line:
                        formatted_lines.append(base_line)
                    formatted_lines.append(' ' * indent + '{')
                else:
                    formatted_lines.append(line)
                i += 1
                
            return '\n'.join(formatted_lines)
            
        except Exception as e:
            raise ValueError(f"Error converting to Allman style: {str(e)}")

    @staticmethod
    def to_knr(code: str) -> str:
        """
        Convert code to K&R style while preserving indentation and handling comments.
        
        Args:
            code: Input code string
            
        Returns:
            str: Code formatted in K&R style
        """
        try:
            lines = code.split('\n')
            formatted_lines = []
            skip_next = False
            in_multiline_comment = False
            i = 0
            
            while i < len(lines):
                if skip_next:
                    skip_next = False
                    i += 1
                    continue
                
                line = lines[i]
                
                # Track multi-line comment status
                if '/*' in line and StyleConverter.is_brace_in_code(line, line.index('/*')):
                    in_multiline_comment = True
                if '*/' in line:
                    in_multiline_comment = False
                
                # If next line is just an opening brace and not in comment
                if (i < len(lines) - 1 and 
                    lines[i + 1].strip() == '{' and 
                    not in_multiline_comment):
                    formatted_lines.append(line.rstrip() + ' {')
                    skip_next = True
                else:
                    formatted_lines.append(line)
                
                i += 1
            
            return '\n'.join(formatted_lines)
            
        except Exception as e:
            raise ValueError(f"Error converting to K&R style: {str(e)}")

    @staticmethod
    def remove_single_line_comments(code: str) -> str:
        """
        Remove all single-line comments (//) while preserving string literals.
        
        Args:
            code: Input code string
            
        Returns:
            str: Code with single-line comments removed
        """
        try:
            lines = code.split('\n')
            result_lines = []
            
            for line in lines:
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
        """
        Remove all multi-line comments (/* ... */) using a state machine approach.
        
        Args:
            code: Input code string
            
        Returns:
            str: Code with multi-line comments removed
        """
        try:
            result = []
            in_comment = False
            in_string = False
            string_char = None
            i = 0
            
            while i < len(code):
                if not in_comment and code[i] in '"\'':
                    if not in_string:
                        in_string = True
                        string_char = code[i]
                        result.append(code[i])
                    elif string_char == code[i]:
                        in_string = False
                        result.append(code[i])
                elif not in_string:
                    if not in_comment and code[i:i+2] == '/*':
                        in_comment = True
                        i += 1
                    elif in_comment and code[i:i+2] == '*/':
                        in_comment = False
                        i += 1
                    elif not in_comment:
                        result.append(code[i])
                else:
                    if not in_comment:
                        result.append(code[i])
                i += 1
                
            return ''.join(result)
            
        except Exception as e:
            raise ValueError(f"Error removing multi-line comments: {str(e)}")

    @staticmethod
    def remove_all_comments(code: str) -> str:
        """
        Remove both single-line and multi-line comments.
        
        Args:
            code: Input code string
            
        Returns:
            str: Code with all comments removed
        """
        try:
            # First remove multi-line comments, then single-line comments
            code = StyleConverter.remove_multi_line_comments(code)
            code = StyleConverter.remove_single_line_comments(code)
            return code
        except Exception as e:
            raise ValueError(f"Error removing all comments: {str(e)}")

    @staticmethod
    def remove_unnecessary_braces(code: str) -> str:
        """
        Remove unnecessary braces from single-statement blocks in C-style code.
        Preserves braces for function definitions, multi-statement blocks, etc.
        
        Args:
            code: String containing the C-style code
            
        Returns:
            str: Modified code with unnecessary braces removed
        """
        try:
            lines = code.split('\n')
            i = 0
            while i < len(lines):
                line = lines[i].rstrip()
                if not line or line.isspace():
                    i += 1
                    continue
                
                # Skip function/class/struct definitions, do-while, try-catch, and switch
                if re.search(r'^\s*(class|struct|\w+\s+\w+\s*\([^)]*\)|do\s*|try\s*|switch\s*)\s*({|\s*$)', line):
                    i += 1
                    continue
                
                # Look for control statements that might have removable braces
                match = re.match(r'^(\s*)(if|else|for|while|case\s+.*:)\s*(.*)$', line)
                if match:
                    indent, keyword, rest = match.groups()
                    
                    # Skip else if as it will be handled by if
                    if keyword == 'else' and 'if' in rest:
                        i += 1
                        continue
                    
                    # Find opening brace position
                    if rest.strip().endswith('{'):
                        brace_line = i
                        brace_pos = line.rindex('{')
                    else:
                        # Check next line for Allman style
                        if i + 1 < len(lines) and lines[i + 1].strip() == '{':
                            brace_line = i + 1
                            brace_pos = lines[brace_line].index('{')
                        else:
                            i += 1
                            continue
                    
                    try:
                        # Find matching closing brace
                        closing_line, closing_pos = StyleConverter.find_matching_brace(
                            lines, brace_line, brace_pos
                        )
                        
                        # Extract content between braces
                        content_lines = []
                        content_start = brace_line + 1
                        j = content_start
                        while j < closing_line:
                            content_lines.append(lines[j])
                            j += 1
                        if closing_line > brace_line:
                            content_lines.append(lines[closing_line][:closing_pos])
                        
                        # Count non-comment, non-empty statements
                        actual_statements = []
                        for content_line in content_lines:
                            stripped = content_line.strip()
                            if (stripped and 
                                not stripped.startswith('//') and 
                                not stripped.startswith('/*') and 
                                not stripped.endswith('*/')):
                                actual_statements.append(content_line)
                        
                        # Remove braces if exactly one statement
                        if len(actual_statements) == 1:
                            # Remove closing brace
                            if closing_line == len(lines) - 1:
                                lines = lines[:closing_line]
                            else:
                                closing_line_content = lines[closing_line]
                                # Check if this is an else statement
                                next_content = closing_line_content[closing_pos + 1:].strip()
                                is_else = next_content.startswith('else')
                                
                                # If it's an else, preserve the indentation level of the if
                                if is_else:
                                    lines[closing_line] = indent + 'else' + next_content[4:]
                                else:
                                    lines[closing_line] = (
                                        closing_line_content[:closing_pos] +
                                        closing_line_content[closing_pos + 1:]
                                    ).rstrip()
                                    
                                if not lines[closing_line].strip():
                                    lines.pop(closing_line)
                            
                            # Remove opening brace
                            if brace_line == len(lines) - 1:
                                lines = lines[:brace_line]
                            else:
                                brace_line_content = lines[brace_line]
                                lines[brace_line] = (
                                    brace_line_content[:brace_pos] +
                                    brace_line_content[brace_pos + 1:]
                                ).rstrip()
                                if not lines[brace_line].strip():
                                    lines.pop(brace_line)
                            
                            # Adjust counter if we removed lines before current position
                            if brace_line < i:
                                i -= 1
                            if closing_line < i:
                                i -= 1
                    
                    except ValueError:
                        pass  # Malformed braces, skip this block
                
                i += 1
            
            return '\n'.join(lines)
            
        except Exception as e:
            raise ValueError(f"Error removing unnecessary braces: {str(e)}")

    @staticmethod
    def process_in_chunks(code: str, chunk_size: int, operation) -> str:
        """
        Process large code files in chunks to avoid memory issues.
        
        Args:
            code: Input code string
            chunk_size: Size of each chunk in bytes
            operation: Function to apply to each chunk
            
        Returns:
            str: Processed code
        """
        try:
            if len(code) <= chunk_size:
                return operation(code)
            
            result = []
            for i in range(0, len(code), chunk_size):
                chunk = code[i:i + chunk_size]
                result.append(operation(chunk))
            
            return ''.join(result)
            
        except Exception as e:
            raise ValueError(f"Error processing in chunks: {str(e)}")
        
class StyleConverterGUI:
    def __init__(self, root: tk.Tk):
        """
        Initialize the Style Converter GUI.
        
        Args:
            root: The root tkinter window
        """
        self.root = root
        self.root.title("Code Style Converter")
        self.root.geometry("1000x800")
        
        # Configure root grid
        self.root.grid_rowconfigure(0, weight=1)
        self.root.grid_columnconfigure(0, weight=1)
        
        # Create main frame
        self.main_frame = ttk.Frame(root, padding="10")
        self.main_frame.grid(row=0, column=0, sticky="nsew")
        
        # Configure main frame grid
        self.main_frame.grid_rowconfigure(1, weight=1)
        self.main_frame.grid_rowconfigure(4, weight=1)
        self.main_frame.grid_columnconfigure(0, weight=1)
        
        # Create widgets
        self.create_input_section()
        self.create_button_sections()
        self.create_output_section()
        self.create_status_bar()
        
        # Bind keyboard shortcuts
        self.bind_shortcuts()
        
        # Initialize processing flag
        self.is_processing = False

    def create_input_section(self):
        """Create the input text area section."""
        input_label = ttk.Label(self.main_frame, text="Input Code:")
        input_label.grid(row=0, column=0, sticky="w", pady=(0, 5))
        
        self.input_text = scrolledtext.ScrolledText(
            self.main_frame,
            wrap=tk.NONE,
            width=80,
            height=15,
            font=('Consolas', 10)
        )
        self.input_text.grid(row=1, column=0, sticky="nsew", pady=(0, 10))
        
        # Add horizontal scrollbar
        input_h_scroll = ttk.Scrollbar(
            self.main_frame,
            orient=tk.HORIZONTAL,
            command=self.input_text.xview
        )
        input_h_scroll.grid(row=2, column=0, sticky="ew")
        self.input_text.configure(xscrollcommand=input_h_scroll.set)

    def create_button_sections(self):
        """Create all button sections."""
        buttons_frame = ttk.Frame(self.main_frame)
        buttons_frame.grid(row=3, column=0, sticky="ew", pady=10)
        
        # Style conversion buttons
        style_frame = ttk.LabelFrame(buttons_frame, text="Style Conversion", padding=5)
        style_frame.pack(fill=tk.X, expand=True, padx=5, pady=5)
        
        ttk.Button(
            style_frame,
            text="Convert to Allman (Ctrl+Alt+A)",
            command=self.convert_to_allman
        ).pack(side=tk.LEFT, padx=5)
        
        ttk.Button(
            style_frame,
            text="Convert to K&R (Ctrl+Alt+K)",
            command=self.convert_to_knr
        ).pack(side=tk.LEFT, padx=5)
        
        # Comment removal buttons
        comment_frame = ttk.LabelFrame(buttons_frame, text="Comment Operations", padding=5)
        comment_frame.pack(fill=tk.X, expand=True, padx=5, pady=5)
        
        ttk.Button(
            comment_frame,
            text="Remove Single-Line Comments (Ctrl+Alt+S)",
            command=self.remove_single_comments
        ).pack(side=tk.LEFT, padx=5)
        
        ttk.Button(
            comment_frame,
            text="Remove Multi-Line Comments (Ctrl+Alt+M)",
            command=self.remove_multi_comments
        ).pack(side=tk.LEFT, padx=5)
        
        ttk.Button(
            comment_frame,
            text="Remove All Comments (Ctrl+Alt+R)",
            command=self.remove_all_comments
        ).pack(side=tk.LEFT, padx=5)
        
        # Brace removal and utility buttons
        util_frame = ttk.LabelFrame(buttons_frame, text="Utilities", padding=5)
        util_frame.pack(fill=tk.X, expand=True, padx=5, pady=5)
        
        ttk.Button(
            util_frame,
            text="Remove Unnecessary Braces (Ctrl+Alt+B)",
            command=self.remove_unnecessary_braces
        ).pack(side=tk.LEFT, padx=5)
        
        ttk.Button(
            util_frame,
            text="Clear All (Ctrl+Alt+L)",
            command=self.clear_all
        ).pack(side=tk.LEFT, padx=5)
        
        ttk.Button(
            util_frame,
            text="Copy Output (Ctrl+Alt+C)",
            command=self.copy_output
        ).pack(side=tk.LEFT, padx=5)

    def create_output_section(self):
        """Create the output text area section."""
        output_label = ttk.Label(self.main_frame, text="Output Code:")
        output_label.grid(row=4, column=0, sticky="w", pady=(0, 5))
        
        self.output_text = scrolledtext.ScrolledText(
            self.main_frame,
            wrap=tk.NONE,
            width=80,
            height=15,
            font=('Consolas', 10),
            state='disabled'
        )
        self.output_text.grid(row=5, column=0, sticky="nsew", pady=(0, 10))
        
        # Add horizontal scrollbar
        output_h_scroll = ttk.Scrollbar(
            self.main_frame,
            orient=tk.HORIZONTAL,
            command=self.output_text.xview
        )
        output_h_scroll.grid(row=6, column=0, sticky="ew")
        self.output_text.configure(xscrollcommand=output_h_scroll.set)

    def create_status_bar(self):
        """Create the status bar."""
        self.status_var = tk.StringVar()
        self.status_var.set("Ready")
        
        self.status_bar = ttk.Label(
            self.main_frame,
            textvariable=self.status_var,
            relief=tk.SUNKEN,
            anchor=tk.W
        )
        self.status_bar.grid(row=7, column=0, sticky="ew", pady=(5, 0))

    def bind_shortcuts(self):
        """Bind keyboard shortcuts."""
        self.root.bind('<Control-Alt-a>', lambda e: self.convert_to_allman())
        self.root.bind('<Control-Alt-k>', lambda e: self.convert_to_knr())
        self.root.bind('<Control-Alt-s>', lambda e: self.remove_single_comments())
        self.root.bind('<Control-Alt-m>', lambda e: self.remove_multi_comments())
        self.root.bind('<Control-Alt-r>', lambda e: self.remove_all_comments())
        self.root.bind('<Control-Alt-b>', lambda e: self.remove_single_braces())
        self.root.bind('<Control-Alt-l>', lambda e: self.clear_all())
        self.root.bind('<Control-Alt-c>', lambda e: self.copy_output())

    def set_output_text(self, text: str):
        """
        Set text in the read-only output widget.
        
        Args:
            text: Text to set in the output widget
        """
        self.output_text.config(state='normal')
        self.output_text.delete("1.0", tk.END)
        self.output_text.insert("1.0", text)
        self.output_text.config(state='disabled')

    def process_with_progress(self, operation: Callable, operation_name: str):
        """
        Process code with progress indication.
        
        Args:
            operation: Function to perform on the code
            operation_name: Name of the operation for status updates
        """
        if self.is_processing:
            messagebox.showinfo("Processing", "Please wait for the current operation to complete.")
            return
            
        try:
            self.is_processing = True
            self.status_var.set(f"Processing: {operation_name}...")
            self.root.update_idletasks()
            
            input_code = self.input_text.get("1.0", tk.END)
            
            def process():
                try:
                    if len(input_code) > 1024 * 1024:  # 1MB
                        result = StyleConverter.process_in_chunks(
                            input_code,
                            1024 * 1024,  # 1MB chunks
                            operation
                        )
                    else:
                        result = operation(input_code)
                        
                    self.root.after(0, lambda: self.set_output_text(result))
                    self.root.after(0, lambda: self.status_var.set("Ready"))
                except Exception as e:
                    self.root.after(0, lambda: messagebox.showerror("Error", str(e)))
                    self.root.after(0, lambda: self.status_var.set("Error occurred"))
                finally:
                    self.is_processing = False
            
            threading.Thread(target=process, daemon=True).start()
            
        except Exception as e:
            messagebox.showerror("Error", str(e))
            self.status_var.set("Error occurred")
            self.is_processing = False

    def convert_to_allman(self):
        """Convert input code to Allman style."""
        self.process_with_progress(StyleConverter.to_allman, "Converting to Allman style")

    def convert_to_knr(self):
        """Convert input code to K&R style."""
        self.process_with_progress(StyleConverter.to_knr, "Converting to K&R style")

    def remove_single_comments(self):
        """Remove single-line comments from the code."""
        self.process_with_progress(
            StyleConverter.remove_single_line_comments,
            "Removing single-line comments"
        )

    def remove_multi_comments(self):
        """Remove multi-line comments from the code."""
        self.process_with_progress(
            StyleConverter.remove_multi_line_comments,
            "Removing multi-line comments"
        )

    def remove_all_comments(self):
        """Remove all comments from the code."""
        self.process_with_progress(
            StyleConverter.remove_all_comments,
            "Removing all comments"
        )

    def remove_unnecessary_braces(self):
        """Remove curly braces from single non-blocking statements."""
        self.process_with_progress(
            StyleConverter.remove_unnecessary_braces,
            "Removing unnecessary braces"
        )

    def clear_all(self):
        """Clear both input and output text areas."""
        self.input_text.delete("1.0", tk.END)
        self.set_output_text("")
        self.status_var.set("Ready")

    def copy_output(self):
        """Copy output text to clipboard."""
        try:
            output_code = self.output_text.get("1.0", tk.END).rstrip()
            self.root.clipboard_clear()
            self.root.clipboard_append(output_code)
            self.status_var.set("Output copied to clipboard")
        except Exception as e:
            messagebox.showerror("Clipboard Error", f"Failed to copy to clipboard: {str(e)}")
            self.status_var.set("Failed to copy to clipboard")


def main():
    """Main entry point of the application."""
    root = tk.Tk()
    root.title("Code Style Converter")
    
    # Set theme
    style = ttk.Style()
    try:
        style.theme_use('clam')  # Use clam theme for better looking widgets
    except tk.TclError:
        pass  # Fall back to default theme if clam is not available
    
    app = StyleConverterGUI(root)
    
    # Center the window
    root.update_idletasks()
    width = root.winfo_width()
    height = root.winfo_height()
    x = (root.winfo_screenwidth() // 2) - (width // 2)
    y = (root.winfo_screenheight() // 2) - (height // 2)
    root.geometry(f'+{x}+{y}')
    
    root.mainloop()


if __name__ == "__main__":
    main()
