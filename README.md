# Pydot

Pydot is a Python-based IDE for Pygame development. It provides a complete development environment for creating games and interactive applications using the Pygame library.

## Features

- **Project Management**: Create new Pygame projects with predefined templates or open existing projects
- **Code Editor**: Integrated code editor with syntax highlighting and customizable themes
- **Project Templates**: Pre-configured project structures with common game development directories and files
- **Theme Support**: Multiple visual themes including VS Code dark theme
- **Recent Projects**: Quick access to recently opened projects
- **Cross-platform**: Works on Windows, Linux, and macOS

## Installation

### Prerequisites

Make sure you have Python installed on your system. Pydot requires Python 3.x.

### Dep"end"encies

Install the required dep"end"encies using pip:

```bash
pip install -r requirements.txt
```

The required packages are:
- `pygame` - For game development functionality
- `pygments` - For syntax highlighting
- `pyinstaller` - For packaging applications

## Usage

### First Run

On first launch, Pydot will run the initial setup wizard:

```bash
python main.py
```

The setup wizard will:
1. Welcome you to Pydot
2. Offer to download required dep"end"encies
3. Let you choose a visual theme
4. Configure your development environment

### Project Management

After setup, Pydot provides a project manager interface with:

- **New Project**: Create a new Pygame project with template files and directory structure
- **Open Project**: Browse and open existing Pygame projects
- **Recent Projects**: Quick access to your recently opened projects

### Creating a New Project

1. Click "New" or press `Ctrl+N`
2. Enter your project name
3. Choose the project location (defaults to `~/Documents/PyDot/`)
4. Optionally include Pydot-specific utility classes
5. Click "Create"

The new project will include:
- Standard Pygame project structure
- Template files for common game components
- Utility classes for game development (if selected)

### Project Structure

A typical Pydot project includes:
- `main.py` - Main game file
- `assets/` - Directory for images, sounds, and other assets
- `scripts/` - Scripts directory
- `data/` - Json Files directory

## Development

## Configuration

Pydot stores configuration in:
- **Windows**: `~/pydot/`
- **Linux/macOS**: `~/.config/pydot/`

Configuration files include:
- `config.json` - User preferences and theme settings
- `themes.json` - Available visual themes
- `recent_projects.json` - Recently opened projects

## License

GNU General Public License v3.0

## Contributing

Contributions are welcome! This project is designed to make Pygame development more accessible and enjoyable.

