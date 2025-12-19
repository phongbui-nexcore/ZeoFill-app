#!/bin/bash

echo "🌿 ZeoFill Dashboard Setup Script"
echo "=================================="
echo ""

# Check if Python is installed
if ! command -v python3 &> /dev/null; then
    echo "❌ Python 3 is not installed. Please install Python 3.8 or higher."
    exit 1
fi

echo "✅ Python 3 found: $(python3 --version)"
echo ""

# Check if pip is installed
if ! command -v pip3 &> /dev/null; then
    echo "❌ pip3 is not installed. Please install pip."
    exit 1
fi

echo "✅ pip3 found"
echo ""

# Install dependencies
echo "📦 Installing dependencies..."
pip3 install -r requirements.txt

if [ $? -eq 0 ]; then
    echo "✅ Dependencies installed successfully"
else
    echo "❌ Error installing dependencies"
    exit 1
fi

echo ""
echo "=================================="
echo "✅ Setup complete!"
echo ""
echo "To run the dashboard:"
echo "  streamlit run zeofill_dashboard.py"
echo ""
echo "Or use the run script:"
echo "  ./run.sh"
echo ""
echo "📚 For Google Sheets integration, see README_ZEOFILL.md"
echo "=================================="
