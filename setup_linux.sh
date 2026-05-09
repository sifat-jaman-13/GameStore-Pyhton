#!/bin/bash

# ScarZero Game Store - Linux Setup Script
# This script sets up the project for Linux systems

echo "🐧 ScarZero Game Store - Linux Setup"
echo "======================================"

# Check if Python 3.14+ is installed
echo "📦 Checking Python version..."
python3 --version

# Check if pip is installed
if ! command -v pip3 &> /dev/null; then
    echo "❌ pip3 is not installed. Please install Python 3.14+ with pip."
    exit 1
fi

# Create virtual environment
echo "📂 Creating virtual environment (.venv)..."
python3 -m venv .venv

# Activate virtual environment
echo "✅ Activating virtual environment..."
source .venv/bin/activate

# Upgrade pip
echo "🔧 Upgrading pip..."
pip install --upgrade pip

# Install dependencies
echo "📥 Installing dependencies..."
pip install -r requirements.txt

echo ""
echo "✨ Setup Complete!"
echo ""
echo "🚀 To run the application:"
echo "   1. Activate the environment: source .venv/bin/activate"
echo "   2. Run the app: python run_admin.py"
echo ""
echo "📝 To deactivate the environment, type: deactivate"
