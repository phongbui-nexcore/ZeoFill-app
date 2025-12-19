#!/bin/bash
# Cleanup script for preparing ZeoFill Dashboard for production/GitHub

echo "🧹 Cleaning up Demo_Project for production..."

# Remove legacy Google Sheets files
echo "Removing legacy Google Sheets files..."
rm -f google_sheets_integration.py
rm -f test_google_sheets.py
rm -f GOOGLE_SHEETS_SETUP.md
rm -f TROUBLESHOOTING_GOOGLE_SHEETS.md
rm -f CREDENTIALS_QUICK_GUIDE.md

# Remove old documentation
echo "Removing old documentation files..."
rm -f BUGFIX_v2.1.1.md
rm -f CHANGELOG.md
rm -f UPDATE_v2.2.0.md
rm -f UPDATE_v2.3.0.md
rm -f UPGRADE_COMPLETE.md
rm -f README_ZEOFILL.md
rm -f PROJECT_SUMMARY.md
rm -f QUICKSTART.md
rm -f INSTALL_AND_RUN.md
rm -f DASHBOARD_PREVIEW.md
rm -f QUICK_REFERENCE.md
rm -f COLUMN_MAPPING_REFERENCE.md
rm -f DATA_MAPPING_GUIDE.md

# Remove backup and test files
echo "Removing backup and test files..."
rm -f zeofill_dashboard_backup.py
rm -f diagnose.py
rm -f main.py
rm -f data_template.csv

# Remove shell scripts (optional - uncomment if you want to remove them)
# echo "Removing shell scripts..."
# rm -f setup.sh
# rm -f run.sh
# rm -f restart.sh

# Remove Python cache
echo "Removing Python cache..."
rm -rf __pycache__

# Remove .DS_Store files
echo "Removing .DS_Store files..."
find . -name ".DS_Store" -delete

echo ""
echo "✅ Cleanup complete!"
echo ""
echo "Files kept for production:"
echo "  - zeofill_dashboard.py (main dashboard)"
echo "  - supabase_integration.py (data integration)"
echo "  - config.py (configuration)"
echo "  - test_supabase_connection.py (connection testing)"
echo "  - requirements.txt (dependencies)"
echo "  - .env.example (environment template)"
echo "  - .gitignore (git configuration)"
echo "  - README.md (main documentation)"
echo "  - SUPABASE_SETUP.md (setup guide)"
echo "  - SUPABASE_MIGRATION_SUMMARY.md (migration notes)"
echo "  - KPI_CALCULATIONS.md (KPI documentation)"
echo "  - assets/ (logo and images)"
echo "  - .streamlit/ (Streamlit configuration)"
echo "  - zeo_env_311/ (your virtual environment - NOT committed to git)"
echo ""
echo "⚠️  IMPORTANT: Your virtual environment (zeo_env_311/) will NOT be pushed to GitHub"
echo "    The .gitignore already excludes all virtual environment folders."
echo ""
echo "Next steps:"
echo "  1. Review the remaining files"
echo "  2. Make sure .streamlit/secrets.toml has your credentials"
echo "  3. Test the dashboard: streamlit run zeofill_dashboard.py"
echo "  4. Initialize git (if not already): git init"
echo "  5. Add files: git add ."
echo "  6. Commit: git commit -m 'Initial commit: ZeoFill Analytics Dashboard'"
echo "  7. Create GitHub repo and push"
echo "  8. Deploy to Streamlit Cloud (add secrets in dashboard settings)"
echo ""
