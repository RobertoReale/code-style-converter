# Code Style Converter

A Python GUI application that converts code between different brace styles (Allman and K&R). Built with tkinter, this tool provides an easy-to-use interface for developers who need to maintain consistent code formatting across projects.


## Features

- Convert between Allman and K&R brace styles
- User-friendly GUI with syntax highlighting
- Multiple theme support
- Horizontal scrolling for long lines of code
- File operations (open/save)
- Keyboard shortcuts for common operations
- Persistent user preferences
- Status bar with operation feedback
- Cross-platform compatibility

## Installation

1. Clone the repository:
```bash
git clone https://github.com/yourusername/code-style-converter.git
cd code-style-converter
```

2. Install the required dependencies:
```bash
pip install -r requirements.txt
```

## Usage

Run the application:
```bash
python style_converter.py
```

### Keyboard Shortcuts

- `Ctrl+A`: Convert to Allman style
- `Ctrl+K`: Convert to K&R style
- `Ctrl+L`: Clear all text
- `Ctrl+C`: Copy output to clipboard

### Brace Styles

#### Allman Style
```c
while (x == y)
{
    something();
    somethingelse();
}
```

#### K&R Style
```c
while (x == y) {
    something();
    somethingelse();
}
```

## Requirements

- Python 3.6+
- tkinter (usually comes with Python)

## Contributing

1. Fork the repository
2. Create your feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add some amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.
