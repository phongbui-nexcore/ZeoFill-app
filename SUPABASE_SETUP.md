# Supabase Setup Guide for ZeoFill Dashboard

This guide walks you through setting up Supabase as the data source for your ZeoFill Dashboard, replacing Google Sheets.

## Table of Contents
1. [Why Supabase?](#why-supabase)
2. [Create Supabase Project](#create-supabase-project)
3. [Set Up Database Schema](#set-up-database-schema)
4. [Configure Credentials](#configure-credentials)
5. [Migrate Existing Data](#migrate-existing-data-optional)
6. [Test Connection](#test-connection)
7. [Troubleshooting](#troubleshooting)

---

## Why Supabase?

**Benefits over Google Sheets:**
- **Better Performance**: Faster queries, especially with large datasets
- **Real Database**: SQL queries, indexes, relationships, and constraints
- **Scalability**: Handle millions of records without performance degradation
- **API-First**: Built-in REST and GraphQL APIs
- **Real-Time**: Optional real-time subscriptions for live updates
- **Free Tier**: 500MB database, 2GB bandwidth, 50MB file storage
- **Security**: Row-level security, built-in authentication

---

## Create Supabase Project

### Step 1: Sign Up for Supabase
1. Go to [https://supabase.com](https://supabase.com)
2. Click "Start your project"
3. Sign up with GitHub, GitLab, or email

### Step 2: Create a New Project
1. Click "New Project"
2. Fill in project details:
   - **Name**: `zeofill-dashboard` (or your preferred name)
   - **Database Password**: Create a strong password (save it!)
   - **Region**: Choose closest to your location
   - **Pricing Plan**: Start with Free tier
3. Click "Create new project"
4. Wait 2-3 minutes for project initialization

### Step 3: Get Your API Credentials
1. In your project dashboard, click "Settings" (gear icon)
2. Navigate to "API" section
3. You'll see:
   - **Project URL**: `https://xxxxx.supabase.co`
   - **anon/public key**: Long string starting with `eyJ...`
   - **service_role key**: Another long string (keep this secret!)

**Save these credentials** - you'll need them for configuration.

---

## Set Up Database Schema

### Option 1: Using SQL Editor (Recommended)

1. In Supabase dashboard, go to "SQL Editor"
2. Click "New query"
3. Copy and paste the following SQL:

```sql
-- Create orders table
CREATE TABLE orders (
  id BIGSERIAL PRIMARY KEY,
  order_id TEXT,
  created_at TIMESTAMP WITH TIME ZONE NOT NULL,
  channel TEXT NOT NULL CHECK (channel IN ('Shopify', 'Walmart')),
  total_price DECIMAL(10, 2) NOT NULL,
  total_shipping DECIMAL(10, 2) DEFAULT 0,
  total_tax DECIMAL(10, 2) DEFAULT 0,
  financial_status TEXT DEFAULT 'paid',
  state TEXT,
  products TEXT,
  created_date TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Create indexes for better query performance
CREATE INDEX idx_orders_channel ON orders(channel);
CREATE INDEX idx_orders_created_at ON orders(created_at);
CREATE INDEX idx_orders_state ON orders(state);
CREATE INDEX idx_orders_financial_status ON orders(financial_status);

-- Enable Row Level Security (RLS)
ALTER TABLE orders ENABLE ROW LEVEL SECURITY;

-- Create policy to allow reading data with API key
CREATE POLICY "Enable read access for authenticated users"
ON orders FOR SELECT
USING (auth.role() = 'authenticated' OR auth.role() = 'anon');

-- Optional: Create policy to allow inserting data (if needed)
CREATE POLICY "Enable insert for authenticated users"
ON orders FOR INSERT
WITH CHECK (auth.role() = 'authenticated');

-- Add helpful comment
COMMENT ON TABLE orders IS 'Order data from Shopify and Walmart channels';
```

4. Click "Run" or press `Ctrl/Cmd + Enter`
5. You should see "Success. No rows returned"

### Option 2: Using Table Editor

1. Go to "Table Editor" in Supabase dashboard
2. Click "Create a new table"
3. Name it `orders`
4. Add columns manually (refer to SQL schema above for column types)

---

## Configure Credentials

### Option 1: Using Environment Variables (Recommended for Local Development)

1. Create a `.env` file in your project root:
   ```bash
   cp .env.example .env
   ```

2. Edit `.env` and add your Supabase credentials:
   ```env
   SUPABASE_URL=https://your-project-ref.supabase.co
   SUPABASE_KEY=your-anon-key-here
   ```

3. Make sure `.env` is in your `.gitignore` (already included)

### Option 2: Using Streamlit Secrets (Recommended for Production/Deployment)

1. Create/edit `.streamlit/secrets.toml`:
   ```bash
   mkdir -p .streamlit
   nano .streamlit/secrets.toml
   ```

2. Add your credentials:
   ```toml
   [supabase]
   url = "https://your-project-ref.supabase.co"
   key = "your-anon-key-here"
   ```

3. Save and close

**Note**: For Streamlit Cloud deployment, add these secrets in the app settings.

---

## Migrate Existing Data (Optional)

If you have existing data in Google Sheets, here's how to migrate it to Supabase:

### Option 1: Manual CSV Upload

1. **Export from Google Sheets**:
   - Open your Google Sheet
   - File → Download → Comma Separated Values (.csv)
   - Do this for both Shopify and Walmart sheets

2. **Format the CSV** to match the schema:
   - Required columns: `created_at`, `channel`, `total_price`
   - Optional columns: `order_id`, `total_shipping`, `total_tax`, `financial_status`, `state`, `products`

3. **Import to Supabase**:
   - In Supabase, go to "Table Editor"
   - Select the `orders` table
   - Click "Insert" → "Import data from CSV"
   - Upload your CSV file
   - Map columns appropriately
   - Click "Import"

### Option 2: Using the Migration Script

A Python script is included in `supabase_integration.py`:

```python
import pandas as pd
from supabase_integration import bulk_upload_from_dataframe
from google_sheets_integration import fetch_all_order_data

# Fetch data from Google Sheets
df = fetch_all_order_data()

# Prepare data for Supabase
df_upload = df.rename(columns={
    'date': 'created_at',
    'revenue': 'total_price'
})[['created_at', 'channel', 'order_id', 'total_price', 'total_shipping',
    'total_tax', 'financial_status', 'state', 'products']]

# Upload to Supabase
bulk_upload_from_dataframe(df_upload)
```

Run this once to migrate your historical data.

### Option 3: Manual Insert via SQL

```sql
-- Example: Insert sample orders
INSERT INTO orders (order_id, created_at, channel, total_price, total_shipping, total_tax, financial_status, state, products)
VALUES
  ('SH-001', '2024-01-15 10:30:00+00', 'Shopify', 150.00, 10.00, 12.00, 'paid', 'CA', 'ZeoFill Infill (50lb)'),
  ('WM-001', '2024-01-16 14:20:00+00', 'Walmart', 200.00, 15.00, 16.00, 'paid', 'TX', 'Pet Deodorizer 32oz'),
  ('SH-002', '2024-01-17 09:15:00+00', 'Shopify', 175.00, 12.00, 14.00, 'paid', 'FL', 'ZeoFill Infill (Pallet)');
```

---

## Test Connection

### Method 1: Python Test Script

Create a test file `test_supabase.py`:

```python
import os
from dotenv import load_dotenv
from supabase import create_client

load_dotenv()

url = os.getenv("SUPABASE_URL")
key = os.getenv("SUPABASE_KEY")

print(f"Testing connection to: {url}")

client = create_client(url, key)
response = client.table('orders').select("*").limit(5).execute()

print(f"✅ Connection successful!")
print(f"Retrieved {len(response.data)} records")
print(response.data)
```

Run it:
```bash
python test_supabase.py
```

### Method 2: Run the Dashboard

```bash
streamlit run zeofill_dashboard.py
```

If configured correctly, you should see "● Live Data" in the top right corner.

---

## Troubleshooting

### Error: "Could not connect to Supabase"

**Possible causes**:
1. **Invalid credentials**: Double-check your `SUPABASE_URL` and `SUPABASE_KEY`
2. **Missing .env file**: Make sure `.env` exists and is in the project root
3. **Wrong format**: URL should start with `https://`, key should be a long string

**Solution**:
```bash
# Verify your .env file exists
cat .env

# Check if python-dotenv is installed
pip install python-dotenv

# Load environment variables manually
python -c "import os; from dotenv import load_dotenv; load_dotenv(); print(os.getenv('SUPABASE_URL'))"
```

### Error: "Table 'orders' does not exist"

**Solution**: Run the SQL schema creation script again (see "Set Up Database Schema" section)

### Error: "Row Level Security policy violation"

**Possible causes**: RLS is enabled but no policies allow access

**Solution**:
```sql
-- Check existing policies
SELECT * FROM pg_policies WHERE tablename = 'orders';

-- If no policies exist, create one
CREATE POLICY "Enable read access for all"
ON orders FOR SELECT
USING (true);
```

### Error: "No data showing in dashboard"

**Possible causes**: Table is empty

**Solution**:
```sql
-- Check if table has data
SELECT COUNT(*) FROM orders;

-- Insert sample data if empty
INSERT INTO orders (created_at, channel, total_price, state, products)
VALUES
  (NOW(), 'Shopify', 100.00, 'CA', 'Test Product');
```

### Dashboard shows "Demo Mode" instead of "Live Data"

**Possible causes**:
1. Supabase integration not imported correctly
2. Credentials not configured

**Solution**:
```bash
# Check if supabase package is installed
pip install supabase

# Verify credentials are set
python -c "import os; print('SUPABASE_URL:', os.getenv('SUPABASE_URL', 'NOT SET'))"

# Restart Streamlit
streamlit run zeofill_dashboard.py
```

---

## Next Steps

After successful setup:

1. **Add real data**: Import your historical order data
2. **Set up automation**: Connect Shopify/Walmart webhooks to automatically insert new orders
3. **Optimize queries**: Add more indexes if needed for specific reports
4. **Enable real-time**: Use Supabase real-time subscriptions for live dashboard updates
5. **Backup data**: Set up automated backups in Supabase dashboard

---

## Additional Resources

- [Supabase Documentation](https://supabase.com/docs)
- [Supabase Python Client](https://github.com/supabase-community/supabase-py)
- [PostgreSQL Documentation](https://www.postgresql.org/docs/)
- [Streamlit Secrets Management](https://docs.streamlit.io/streamlit-community-cloud/get-started/deploy-an-app/connect-to-data-sources/secrets-management)

---

## Support

If you encounter issues:
1. Check the troubleshooting section above
2. Review Supabase logs in the dashboard
3. Test your connection with the test script
4. Check that your table schema matches exactly

For Supabase-specific issues, visit the [Supabase Community](https://github.com/supabase/supabase/discussions).
