# C Code Style Converter

C Code Style Converter is a Python-based desktop application that helps developers manage code formatting and comments. It provides an easy-to-use interface for converting between different code styling conventions and removing comments selectively.

## Features

- **Code Style Conversion**
  - Convert between Allman and K&R bracket styles
  - Preserves original indentation and formatting
  - Handles complex cases including comments and strings

- **Comment Management**
  - Remove single-line comments (//)
  - Remove multi-line comments (/* ... */)
  - Remove all comments at once
  - Preserves code structure and formatting

- **User-Friendly Interface**
  - Split-view interface with input and output panels
  - Real-time preview of changes
  - Copy output to clipboard functionality
  - Clear all button to reset both panels

## Keyboard Shortcuts

- `Ctrl + A`: Convert to Allman style
- `Ctrl + K`: Convert to K&R style
- `Ctrl + S`: Remove single-line comments
- `Ctrl + M`: Remove multi-line comments
- `Ctrl + R`: Remove all comments
- `Ctrl + L`: Clear all panels
- `Ctrl + C`: Copy output to clipboard
- `Ctrl + B`: Remove single statement braces

## Requirements

- Python 3.6 or higher
- tkinter (usually comes with Python)
- typing module
- re

## Installation

1. Clone the repository:
```bash
git clone https://github.com/yourusername/C Code Style Converter.git
```

2. Navigate to the project directory:
```bash
cd C Code Style Converter
```

3. Run the application:
```bash
python main.py
```

## Usage

1. Paste or type your code in the upper text area
2. Select the desired operation using the buttons or keyboard shortcuts
3. The processed code will appear in the lower text area
4. Use the "Copy Output" button or Ctrl+C to copy the result

## Example

Input code:
```c
if (condition) {
    doSomething(); // This is a comment
    /* This is a
       multi-line comment */
    doSomethingElse();
}
```

After converting to Allman style and removing comments:
```c
if (condition)
{
    doSomething();
    doSomethingElse();
}
```

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request. For major changes, please open an issue first to discuss what you would like to change.

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.
