#!/bin/bash

echo "🌿 Starting ZeoFill Dashboard..."
echo ""

# Check if Streamlit is installed
if ! python3 -m streamlit --version &> /dev/null; then
    echo "❌ Streamlit is not installed."
    echo "Please run: pip3 install streamlit"
    exit 1
fi

# Run the dashboard
python3 -m streamlit run zeofill_dashboard.py
