#!/bin/bash
# Restart Streamlit Dashboard
# This script kills the running Streamlit process and starts it again

echo "🛑 Stopping Streamlit..."
pkill -f "streamlit run zeofill_dashboard.py"
sleep 2

echo "🚀 Starting Streamlit..."
./run.sh
