# ScarZero Game Store - Linux Setup Guide

This guide will help you run the ScarZero Game Store on Linux systems.

## Prerequisites

- Python 3.14 or higher
- pip (Python package manager)
- Basic terminal/command line knowledge

## Quick Setup

### Option 1: Automated Setup (Recommended)

1. **Make the setup script executable:**
   ```bash
   chmod +x setup_linux.sh
   ```

2. **Run the setup script:**
   ```bash
   ./setup_linux.sh
   ```

3. **Run the application:**
   ```bash
   source .venv/bin/activate
   python run_admin.py
   ```

### Option 2: Manual Setup

1. **Create a virtual environment:**
   ```bash
   python3 -m venv .venv
   ```

2. **Activate the virtual environment:**
   ```bash
   source .venv/bin/activate
   ```

3. **Upgrade pip:**
   ```bash
   pip install --upgrade pip
   ```

4. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

5. **Run the application:**
   ```bash
   python run_admin.py
   ```

## Project Structure

```
.venv/                          # Virtual environment directory (auto-created)
├── bin/                        # Executable scripts
├── lib/                        # Python packages
└── ...

GameStoreApp/                   # Main application code
requirements.txt                # Python dependencies
run_admin.py                    # Entry point
pyproject.toml                  # Project configuration
```

## Troubleshooting

### Python version not found
If `python3` is not found, check your Python installation:
```bash
which python3
python3 --version
```

### Permission denied when running setup script
Make it executable first:
```bash
chmod +x setup_linux.sh
```

### Virtual environment not activating
Ensure you're using the correct activation command for Linux/Mac:
```bash
source .venv/bin/activate
```

(Not `venv\Scripts\activate` - that's for Windows)

### Dependency installation fails
Update pip and try again:
```bash
pip install --upgrade pip
pip install -r requirements.txt
```

## Deactivating the Virtual Environment

To exit the virtual environment, simply type:
```bash
deactivate
```

## Additional Notes

- The `.venv` directory is Git-ignored and should not be committed
- All dependencies are listed in `requirements.txt`
- The project uses `customtkinter` for the GUI (works on Linux with proper GTK support)

For more information, see `pyproject.toml` for project configuration details.
