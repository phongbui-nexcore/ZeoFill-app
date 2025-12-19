"""
Supabase Connection Test Script

This script tests your Supabase connection and displays sample data
from all three tables (Shopify, Walmart, Amazon).

Usage:
    python test_supabase_connection.py
"""

import os
import sys
from dotenv import load_dotenv
from supabase import create_client

# Load environment variables
load_dotenv()

def test_connection():
    """Test Supabase connection and fetch sample data."""

    print("=" * 60)
    print("Supabase Connection Test")
    print("=" * 60)
    print()

    # Step 1: Check environment variables
    print("Step 1: Checking environment variables...")
    supabase_url = os.getenv("SUPABASE_URL")
    supabase_key = os.getenv("SUPABASE_KEY")

    if not supabase_url:
        print("❌ ERROR: SUPABASE_URL not found in environment variables")
        print("   Make sure you have a .env file with SUPABASE_URL set")
        sys.exit(1)

    if not supabase_key:
        print("❌ ERROR: SUPABASE_KEY not found in environment variables")
        print("   Make sure you have a .env file with SUPABASE_KEY set")
        sys.exit(1)

    print(f"✅ SUPABASE_URL: {supabase_url[:30]}...")
    print(f"✅ SUPABASE_KEY: {supabase_key[:20]}...")
    print()

    # Step 2: Create Supabase client
    print("Step 2: Creating Supabase client...")
    try:
        client = create_client(supabase_url, supabase_key)
        print("✅ Supabase client created successfully")
        print()
    except Exception as e:
        print(f"❌ ERROR: Failed to create Supabase client: {str(e)}")
        sys.exit(1)

    # Step 3: Test table connections
    tables = {
        'Shopify': 'Shopify_OrderData',
        'Walmart': 'Walmart_OrderData',
        'Amazon': 'Amazon_OrderData'
    }

    results = {}

    for channel, table_name in tables.items():
        print(f"Step 3.{list(tables.keys()).index(channel) + 1}: Testing {channel} table ({table_name})...")
        try:
            # Try to fetch first 5 records
            response = client.table(table_name).select('*').limit(5).execute()

            if response.data:
                count = len(response.data)
                print(f"✅ Successfully fetched {count} sample records from {table_name}")
                results[channel] = {
                    'status': 'success',
                    'count': count,
                    'sample': response.data[0] if response.data else None
                }

                # Show first record columns
                if response.data:
                    columns = list(response.data[0].keys())
                    print(f"   Columns ({len(columns)}): {', '.join(columns[:8])}{'...' if len(columns) > 8 else ''}")
            else:
                print(f"⚠️  WARNING: Table {table_name} exists but has no data")
                results[channel] = {
                    'status': 'empty',
                    'count': 0,
                    'sample': None
                }

        except Exception as e:
            print(f"❌ ERROR: Failed to fetch from {table_name}: {str(e)}")
            results[channel] = {
                'status': 'error',
                'error': str(e)
            }

        print()

    # Step 4: Summary
    print("=" * 60)
    print("Summary")
    print("=" * 60)
    print()

    success_count = sum(1 for r in results.values() if r['status'] == 'success')
    empty_count = sum(1 for r in results.values() if r['status'] == 'empty')
    error_count = sum(1 for r in results.values() if r['status'] == 'error')

    print(f"Tables tested: {len(tables)}")
    print(f"✅ Successful connections: {success_count}")
    print(f"⚠️  Empty tables: {empty_count}")
    print(f"❌ Errors: {error_count}")
    print()

    # Detailed results
    for channel, result in results.items():
        if result['status'] == 'success':
            print(f"✅ {channel}: {result['count']} records available")
        elif result['status'] == 'empty':
            print(f"⚠️  {channel}: Table exists but is empty")
        else:
            print(f"❌ {channel}: {result.get('error', 'Unknown error')}")

    print()

    # Step 5: Recommendations
    if success_count == len(tables):
        print("🎉 All tables connected successfully!")
        print()
        print("Next steps:")
        print("1. Run the dashboard: streamlit run zeofill_dashboard.py")
        print("2. You should see '● Live Data' in the top right corner")
        print()
    elif success_count > 0:
        print("⚠️  Some tables connected successfully, but there are issues:")
        print()
        if empty_count > 0:
            print("Empty tables detected:")
            for channel, result in results.items():
                if result['status'] == 'empty':
                    print(f"  - {channel}: Add data to {tables[channel]} table")
            print()
        if error_count > 0:
            print("Connection errors detected:")
            for channel, result in results.items():
                if result['status'] == 'error':
                    print(f"  - {channel}: Check if {tables[channel]} table exists")
            print()
        print("The dashboard will still work but will use sample data for failed channels.")
        print()
    else:
        print("❌ No tables could be connected.")
        print()
        print("Troubleshooting:")
        print("1. Verify table names in Supabase match:")
        for channel, table in tables.items():
            print(f"   - {table}")
        print("2. Check Row Level Security (RLS) policies allow SELECT")
        print("3. Verify your SUPABASE_KEY has correct permissions")
        print()

    # Step 6: Show sample data (if available)
    for channel, result in results.items():
        if result['status'] == 'success' and result['sample']:
            print(f"Sample record from {channel}:")
            sample = result['sample']
            # Show first 5 key fields
            keys = list(sample.keys())[:5]
            for key in keys:
                value = str(sample[key])
                if len(value) > 50:
                    value = value[:50] + "..."
                print(f"  {key}: {value}")
            print()


if __name__ == "__main__":
    try:
        test_connection()
    except KeyboardInterrupt:
        print("\n\n❌ Test cancelled by user (Ctrl+C)")
        sys.exit(1)
    except Exception as e:
        print(f"\n\n❌ Unexpected error: {str(e)}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
