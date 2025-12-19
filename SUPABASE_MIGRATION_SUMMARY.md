# Supabase Migration Summary

## Overview

Your ZeoFill Dashboard has been successfully updated to use Supabase instead of Google Sheets as the data source. The dashboard now supports three sales channels: **Shopify**, **Walmart**, and **Amazon**.

---

## What Changed

### 1. **New Dependencies**
Updated [requirements.txt](Demo_Project/requirements.txt):
- ✅ Added `supabase>=2.0.0` - Supabase Python client
- ✅ Added `python-dotenv>=1.0.0` - Environment variable management
- ❌ Removed Google Sheets dependencies (gspread, google-auth, etc.)

### 2. **New Integration Module**
Created [supabase_integration.py](Demo_Project/supabase_integration.py):
- Connects to your Supabase tables: `Shopify_OrderData`, `Walmart_OrderData`, `Amazon_OrderData`
- Transforms data from your actual column structure to dashboard format
- Handles authentication via environment variables or Streamlit secrets
- Includes separate transformation logic for:
  - **Shopify/Walmart**: Uses `created_at`, `line_total`, `line_tax`, `line_shipping`, `product_name`, etc.
  - **Amazon**: Uses `purchase-date`, `item-price`, `item-tax`, `shipping-price`, `product-name`, etc.

### 3. **Updated Dashboard**
Modified [zeofill_dashboard.py](Demo_Project/zeofill_dashboard.py):
- ✅ Imports from `supabase_integration` instead of `google_sheets_integration`
- ✅ Added Amazon as a third channel option
- ✅ Updated all charts to support 3 channels with color scheme:
  - Shopify: `#2DD4BF` (Teal)
  - Walmart: `#818CF8` (Purple)
  - Amazon: `#FF9900` (Orange)
- ✅ Updated sample data generator to include Amazon data
- ✅ Channel filter now shows all three options

### 4. **Updated Configuration**
Modified [config.py](Demo_Project/config.py):
- Added Supabase table names
- Updated channel list to include Amazon
- Marked Google Sheets config as deprecated

### 5. **Environment Variables**
Updated [.env.example](Demo_Project/.env.example):
- Added Supabase credentials section
- Commented out Google Sheets credentials (legacy)

### 6. **Documentation**
Created new documentation:
- [SUPABASE_SETUP.md](Demo_Project/SUPABASE_SETUP.md) - Complete setup guide for Supabase
- This summary document

---

## Column Mapping

### Shopify/Walmart Tables → Dashboard

| Supabase Column | Dashboard Column | Transformation |
|----------------|------------------|----------------|
| `created_at` | `date` | Parsed as datetime |
| `order_id` | `order_id` | Direct mapping |
| `line_total` | `revenue` | Numeric conversion |
| `line_shipping` | `shipping_cost` | Numeric conversion |
| `line_tax` | `tax` | Numeric conversion |
| `state` | `state` | Uppercase, handle nulls |
| `product_name` | `products` | Direct mapping |
| `financial_status` | `financial_status` | Lowercase |
| `shop_fees` | `platform_fee` | If available; otherwise calculated |

**Calculated Fields:**
- `cogs` = `revenue` × 0.40 (40%)
- `platform_fee` (if not in data):
  - Shopify: `revenue` × 0.059 + $0.30
  - Walmart: `revenue` × 0.15
- `refund_amount` = `revenue` if `financial_status` = 'refunded', else 0
- `net_revenue` = `revenue` - `refund_amount`
- `gross_profit` = `net_revenue` - `cogs`
- `net_profit` = `gross_profit` - `shipping_cost` - `platform_fee`

### Amazon Table → Dashboard

| Supabase Column | Dashboard Column | Transformation |
|----------------|------------------|----------------|
| `purchase-date` | `date` | Parsed as datetime |
| `amazon-order-id` | `order_id` | Direct mapping |
| `item-price` | `revenue` | Remove $, parse as number |
| `shipping-price` | `shipping_cost` | Remove $, parse as number |
| `item-tax` + `shipping-tax` | `tax` | Sum of both, remove $ |
| `ship-state` | `state` | Uppercase, handle nulls |
| `product-name` | `products` | Direct mapping |
| `order-status` | `financial_status` | Map: Canceled→refunded, Shipped→paid, etc. |

**Calculated Fields:**
- `cogs` = `revenue` × 0.40 (40%)
- `platform_fee` = `revenue` × 0.15 + $0.99
- Discounts: `item-promotion-discount` + `ship-promotion-discount`
- `refund_amount` = `revenue` if `financial_status` = 'refunded', else 0
- `net_revenue` = `revenue` - `refund_amount` - discounts
- `gross_profit` = `net_revenue` - `cogs`
- `net_profit` = `gross_profit` - `shipping_cost` - `platform_fee`

---

## Setup Instructions

### Step 1: Install Dependencies

```bash
pip install -r requirements.txt
```

### Step 2: Configure Supabase Credentials

**Option A: Environment Variables (Recommended for Local)**

1. Create a `.env` file:
   ```bash
   cp .env.example .env
   ```

2. Edit `.env` and add your credentials:
   ```env
   SUPABASE_URL=https://your-project-ref.supabase.co
   SUPABASE_KEY=your-anon-key-here
   ```

**Option B: Streamlit Secrets (Recommended for Deployment)**

1. Create `.streamlit/secrets.toml`:
   ```toml
   [supabase]
   url = "https://your-project-ref.supabase.co"
   key = "your-anon-key-here"
   ```

### Step 3: Get Your Supabase Credentials

1. Go to [https://supabase.com](https://supabase.com)
2. Open your project
3. Go to Settings → API
4. Copy:
   - **Project URL** → Use as `SUPABASE_URL`
   - **anon public key** → Use as `SUPABASE_KEY`

### Step 4: Run the Dashboard

```bash
streamlit run zeofill_dashboard.py
```

You should see **"● Live Data"** in the top right if connected successfully!

---

## Verification Checklist

- [ ] Supabase credentials configured in `.env` or `secrets.toml`
- [ ] Tables exist in Supabase: `Shopify_OrderData`, `Walmart_OrderData`, `Amazon_OrderData`
- [ ] Tables contain data with the expected columns
- [ ] Dashboard shows "● Live Data" instead of "● Demo Mode"
- [ ] All three channels appear in the filter dropdown
- [ ] Charts display data from all three channels
- [ ] Revenue numbers match expected values

---

## Troubleshooting

### Dashboard shows "Demo Mode"

**Cause**: Supabase credentials not found or invalid

**Solution**:
1. Check `.env` file exists and has correct credentials
2. Verify `SUPABASE_URL` and `SUPABASE_KEY` are set
3. Test connection manually:
   ```python
   from supabase_integration import get_supabase_client
   client = get_supabase_client()
   print(client)  # Should show client object
   ```

### Error: "Table 'Shopify_OrderData' does not exist"

**Cause**: Table names don't match

**Solution**:
1. Check your actual table names in Supabase
2. Update table names in [supabase_integration.py](Demo_Project/supabase_integration.py:31-33):
   ```python
   SHOPIFY_TABLE = "Your_Actual_Shopify_Table_Name"
   WALMART_TABLE = "Your_Actual_Walmart_Table_Name"
   AMAZON_TABLE = "Your_Actual_Amazon_Table_Name"
   ```

### No data showing / "No valid data rows found"

**Cause**: Column names don't match or data format issues

**Solution**:
1. Verify your table columns match the expected names
2. Check the transformation functions in `supabase_integration.py`
3. Look for warning messages in the dashboard (orange boxes)
4. Test data fetch manually:
   ```python
   from supabase_integration import fetch_shopify_data
   df = fetch_shopify_data()
   print(df.head())
   ```

### Charts missing Amazon data

**Cause**: Amazon table not fetched or transformation failed

**Solution**:
1. Check Amazon table exists and has data
2. Verify column names match Amazon format (with hyphens: `amazon-order-id`, `purchase-date`, etc.)
3. Check for error messages in the console

---

## Customization

### Adjust COGS Percentage

The Cost of Goods Sold (COGS) is currently estimated at **40%** of revenue. To adjust:

Edit [supabase_integration.py](Demo_Project/supabase_integration.py):
```python
# Line 153 (Shopify/Walmart)
transformed['cogs'] = transformed['revenue'] * 0.40  # Change 0.40 to your percentage

# Line 283 (Amazon)
transformed['cogs'] = transformed['revenue'] * 0.40  # Change 0.40 to your percentage
```

### Adjust Platform Fees

Current defaults:
- **Shopify**: 5.9% + $0.30 per transaction
- **Walmart**: 15% referral fee
- **Amazon**: 15% referral fee + $0.99 per item

To adjust, edit the platform fee calculations in `supabase_integration.py`.

### Change Chart Colors

Edit the `color_discrete_map` in chart functions in [zeofill_dashboard.py](Demo_Project/zeofill_dashboard.py):
```python
color_discrete_map={'Shopify': '#2DD4BF', 'Walmart': '#818CF8', 'Amazon': '#FF9900'}
```

---

## Next Steps

### Recommended Enhancements

1. **Add Row Level Security (RLS)** in Supabase for data protection
2. **Set up automated data sync** from Shopify/Walmart/Amazon to Supabase
3. **Create Supabase views** for pre-aggregated metrics (faster dashboard loading)
4. **Add real-time subscriptions** for live dashboard updates
5. **Implement data validation** in Supabase using CHECK constraints
6. **Set up automated backups** in Supabase dashboard

### Performance Optimization

If you have large datasets (>100K rows):

1. **Add database indexes** on frequently queried columns:
   ```sql
   CREATE INDEX idx_shopify_created_at ON "Shopify_OrderData"(created_at);
   CREATE INDEX idx_walmart_created_at ON "Walmart_OrderData"(created_at);
   CREATE INDEX idx_amazon_purchase_date ON "Amazon_OrderData"("purchase-date");
   ```

2. **Increase cache TTL** in `supabase_integration.py`:
   ```python
   @st.cache_data(ttl=600)  # Cache for 10 minutes instead of 5
   ```

3. **Create materialized views** in Supabase for pre-computed aggregations

---

## Support

For issues:
1. Check the [SUPABASE_SETUP.md](Demo_Project/SUPABASE_SETUP.md) troubleshooting section
2. Review Supabase logs in your project dashboard
3. Check Streamlit console for error messages
4. Verify your table schema matches the expected structure

---

## Files Modified

| File | Status | Description |
|------|--------|-------------|
| `requirements.txt` | ✏️ Modified | Updated dependencies |
| `zeofill_dashboard.py` | ✏️ Modified | Updated to use Supabase, added Amazon |
| `config.py` | ✏️ Modified | Added Supabase config, Amazon channel |
| `.env.example` | ✏️ Modified | Added Supabase credentials template |
| `supabase_integration.py` | ✨ New | Supabase data fetching and transformation |
| `SUPABASE_SETUP.md` | ✨ New | Complete Supabase setup guide |
| `SUPABASE_MIGRATION_SUMMARY.md` | ✨ New | This file |

## Files No Longer Used

| File | Status | Description |
|------|--------|-------------|
| `google_sheets_integration.py` | 🗄️ Legacy | Replaced by `supabase_integration.py` |
| `credentials.json` | 🗄️ Legacy | No longer needed |
| `GOOGLE_SHEETS_SETUP.md` | 🗄️ Legacy | Replaced by `SUPABASE_SETUP.md` |

You can keep these files for reference or delete them once migration is confirmed working.

---

**Migration completed successfully! 🎉**

Your dashboard is now powered by Supabase with support for Shopify, Walmart, and Amazon sales data.
