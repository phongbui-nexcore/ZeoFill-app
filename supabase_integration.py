"""
Supabase Integration Module for ZeoFill Dashboard

This module handles fetching data from Supabase tables.
To use this module:

1. Create a Supabase project at https://supabase.com
2. Create tables for Shopify, Walmart, and Amazon orders
3. Get your project URL and anon/service key
4. Add credentials to .env file or Streamlit secrets

Required environment variables:
- SUPABASE_URL: Your Supabase project URL
- SUPABASE_KEY: Your Supabase anon key or service role key

Table Structure:
- Shopify/Walmart: order_id, created_at, state, product_name, quantity, unit_price,
                   line_total, line_tax, line_shipping, financial_status, etc.
- Amazon: amazon-order-id, purchase-date, ship-state, product-name, quantity,
          item-price, item-tax, shipping-price, order-status, etc.
"""

import pandas as pd
import streamlit as st
from supabase import create_client, Client
from typing import Optional
import os
from datetime import datetime

# Table names in Supabase
SHOPIFY_TABLE = "Shopify_OrderData"
WALMART_TABLE = "Walmart_OrderData"
AMAZON_TABLE = "Amazon_OrderData"
SHOPIFY_FEES_TABLE = "Shopify_Fees"
WALMART_FEES_TABLE = "Walmart_Fees"
AMAZON_FEES_TABLE = "Amazon_Fees"

def get_supabase_client() -> Optional[Client]:
    """
    Initialize and return Supabase client.

    Supports two authentication methods (in order of priority):
    1. Streamlit secrets (.streamlit/secrets.toml)
    2. Environment variables (.env)

    Returns:
        Supabase client instance or None if credentials not found
    """
    try:
        supabase_url = None
        supabase_key = None

        # Method 1: Try Streamlit secrets first (recommended for production)
        if "supabase" in st.secrets:
            supabase_url = st.secrets["supabase"]["url"]
            supabase_key = st.secrets["supabase"]["key"]

        # Method 2: Try environment variables
        elif "SUPABASE_URL" in os.environ and "SUPABASE_KEY" in os.environ:
            supabase_url = os.getenv("SUPABASE_URL")
            supabase_key = os.getenv("SUPABASE_KEY")

        # No credentials found
        else:
            st.warning("""
            ⚠️ Supabase credentials not found!

            To connect to Supabase, use ONE of these methods:

            **Option 1: Streamlit Secrets (Recommended)**
            - Create/edit `.streamlit/secrets.toml`
            - Add:
              ```
              [supabase]
              url = "your-project-url"
              key = "your-anon-key"
              ```

            **Option 2: Environment Variables**
            - Add to `.env` file:
              ```
              SUPABASE_URL=your-project-url
              SUPABASE_KEY=your-anon-key
              ```

            For now, using sample data.
            """)
            return None

        # Create and return client
        client: Client = create_client(supabase_url, supabase_key)
        return client

    except Exception as e:
        st.error(f"❌ Error connecting to Supabase: {str(e)}")
        return None


def transform_shopify_walmart_data(df: pd.DataFrame, channel: str) -> pd.DataFrame:
    """
    Transform Shopify/Walmart Supabase data to dashboard format.

    Shopify/Walmart columns: order_id, created_at, state, product_name, quantity,
    unit_price, line_total, line_tax, line_shipping, financial_status, shop_fees, etc.

    Args:
        df: Raw DataFrame from Supabase
        channel: 'Shopify' or 'Walmart'

    Returns:
        Transformed DataFrame with dashboard-compatible structure
    """
    if df is None or df.empty:
        return None

    # Create transformed DataFrame
    transformed = pd.DataFrame()

    # Map date column
    transformed['date'] = pd.to_datetime(df['created_at'], errors='coerce')

    # Map order_id - use order_number for Shopify if available, otherwise use order_id
    if 'order_number' in df.columns and channel == 'Shopify':
        transformed['order_id'] = 'Order #' + df['order_number'].astype(str).str.strip()
    else:
        transformed['order_id'] = df['order_id'].astype(str).str.strip()

    # Map revenue - use line_total (revenue per line item)
    transformed['revenue'] = pd.to_numeric(df['line_total'], errors='coerce')

    # Map shipping cost
    if channel == 'Shopify':
        # Shopify: Calculate based on weight
        if 'weight' in df.columns:
            def calc_shopify_shipping(weight):
                try:
                    w = float(weight)
                    if w < 1:
                        return 7.0
                    elif w <= 5:
                        return 12.0
                    else:
                        return 19.5
                except:
                    return 0.0
            transformed['shipping_cost'] = df['weight'].apply(calc_shopify_shipping)
        else:
            transformed['shipping_cost'] = pd.to_numeric(df['line_shipping'], errors='coerce').fillna(0)
    elif channel == 'Walmart':
        # Walmart: Use commission_from_sale where transaction_type = ADJMNT from fees table
        if 'commission_from_sale' in df.columns and 'transaction_type' in df.columns:
            # Filter for ADJMNT transactions
            mask = df['transaction_type'].astype(str).str.upper() == 'ADJMNT'
            transformed['shipping_cost'] = pd.to_numeric(df['commission_from_sale'], errors='coerce').fillna(0)
            transformed.loc[~mask, 'shipping_cost'] = 0
        else:
            transformed['shipping_cost'] = pd.to_numeric(df['line_shipping'], errors='coerce').fillna(0)
    else:
        transformed['shipping_cost'] = pd.to_numeric(df['line_shipping'], errors='coerce').fillna(0)

    # Map tax - use line_tax
    transformed['tax'] = pd.to_numeric(df['line_tax'], errors='coerce').fillna(0)

    # Map state column (for geographic heatmap)
    if 'state' in df.columns:
        transformed['state'] = df['state'].astype(str).str.strip().str.upper()
        # Handle null/empty states
        transformed['state'] = transformed['state'].replace(['', 'NAN', 'NONE'], 'Unknown')
    else:
        transformed['state'] = 'Unknown'

    # Products column - use product_name
    if 'product_name' in df.columns:
        transformed['products'] = df['product_name'].astype(str).str.strip()
    else:
        transformed['products'] = 'ZeoFill Product'

    # Financial status (for refund tracking)
    if 'financial_status' in df.columns:
        transformed['financial_status'] = df['financial_status'].astype(str).str.strip().str.lower()
    else:
        transformed['financial_status'] = 'paid'

    # Fulfillment status (for unfulfilled orders tracking)
    if 'fulfillment_status' in df.columns:
        transformed['fulfillment_status'] = df['fulfillment_status'].astype(str).str.strip()
    else:
        transformed['fulfillment_status'] = 'fulfilled'

    # Shipping terms (for Shopify unfulfilled tracking)
    if 'shipping_terms' in df.columns:
        transformed['shipping_terms'] = df['shipping_terms'].astype(str).str.strip()
    else:
        transformed['shipping_terms'] = None

    # Customer name
    if 'customer_name' in df.columns:
        transformed['customer_name'] = df['customer_name'].astype(str).str.strip()
    else:
        transformed['customer_name'] = 'N/A'

    # Shipping address fields
    if 'shipping_address' in df.columns:
        transformed['shipping_address'] = df['shipping_address'].astype(str).str.strip()
    else:
        transformed['shipping_address'] = 'N/A'

    if 'shipping_city' in df.columns:
        transformed['shipping_city'] = df['shipping_city'].astype(str).str.strip()
    else:
        transformed['shipping_city'] = 'N/A'

    if 'shipping_zipcode' in df.columns:
        transformed['shipping_zipcode'] = df['shipping_zipcode'].astype(str).str.strip()
    else:
        transformed['shipping_zipcode'] = 'N/A'

    # Calculate COGS (Cost of Goods Sold)
    # Estimate: 40% of revenue (adjust this percentage as needed)
    transformed['cogs'] = transformed['revenue'] * 0.40

    # Platform fees - use data from fee tables
    if channel == 'Shopify':
        # Shopify: Use processing_fee from Shopify_Fees table
        if 'processing_fee' in df.columns:
            transformed['platform_fee'] = pd.to_numeric(df['processing_fee'], errors='coerce').fillna(0)
        else:
            # Fallback: 2.9% + $0.30 per transaction + 3% for basic plan
            transformed['platform_fee'] = (transformed['revenue'] * 0.059) + 0.30
    elif channel == 'Walmart':
        # Walmart: Use commission_from_sale where transaction_type = SALE from fees table
        if 'commission_from_sale' in df.columns and 'transaction_type' in df.columns:
            # Filter for SALE transactions
            mask = df['transaction_type'].astype(str).str.upper() == 'SALE'
            transformed['platform_fee'] = pd.to_numeric(df['commission_from_sale'], errors='coerce').fillna(0)
            transformed.loc[~mask, 'platform_fee'] = 0
        else:
            # Fallback: 15% referral fee (average)
            transformed['platform_fee'] = transformed['revenue'] * 0.15
    else:
        # Fallback for unknown channels
        transformed['platform_fee'] = 0

    # Discounts - check if discount column exists, otherwise set to 0
    if 'discount' in df.columns:
        transformed['discount'] = pd.to_numeric(df['discount'], errors='coerce').fillna(0)
    else:
        transformed['discount'] = 0

    # Calculate refund amount based on financial_status
    transformed['refund_amount'] = transformed.apply(
        lambda row: row['revenue'] if row['financial_status'] in ['refunded', 'partially_refunded'] else 0.0,
        axis=1
    )
    transformed['refund'] = transformed['refund_amount']  # Alias for dashboard compatibility

    # Add channel identifier
    transformed['channel'] = channel

    # Calculate derived metrics (needed by dashboard)
    # Net revenue = revenue - refunds
    transformed['net_revenue'] = transformed['revenue'] - transformed['refund_amount']

    # Gross profit = net_revenue - COGS
    transformed['gross_profit'] = transformed['net_revenue'] - transformed['cogs']

    # Net profit = gross_profit - shipping - platform fees - tax
    transformed['net_profit'] = transformed['gross_profit'] - transformed['shipping_cost'] - transformed['platform_fee']

    # Remove rows with invalid dates or revenue
    transformed = transformed.dropna(subset=['date', 'revenue'])

    # Remove rows where revenue is 0 or negative
    transformed = transformed[transformed['revenue'] > 0]

    if transformed.empty:
        st.warning(f"⚠️ No valid data rows found for {channel}. Check that created_at has dates and line_total has numbers.")
        return None

    return transformed


def transform_amazon_data(df: pd.DataFrame) -> pd.DataFrame:
    """
    Transform Amazon Supabase data to dashboard format.

    Amazon columns: amazon-order-id, purchase-date, ship-state, product-name,
    quantity, item-price, item-tax, shipping-price, order-status, etc.

    Args:
        df: Raw DataFrame from Supabase

    Returns:
        Transformed DataFrame with dashboard-compatible structure
    """
    if df is None or df.empty:
        return None

    # Create transformed DataFrame
    transformed = pd.DataFrame()

    # Map date column - Amazon uses 'purchase-date'
    transformed['date'] = pd.to_datetime(df['purchase-date'], errors='coerce')

    # Map order_id - Amazon uses 'amazon-order-id'
    transformed['order_id'] = df['amazon-order-id'].astype(str).str.strip()

    # Map revenue - use item-price (convert from currency format if needed)
    if 'item-price' in df.columns:
        # Handle currency format (e.g., "$123.45")
        item_price = df['item-price'].astype(str).str.replace('$', '').str.replace(',', '').str.strip()
        transformed['revenue'] = pd.to_numeric(item_price, errors='coerce')
    else:
        transformed['revenue'] = 0

    # Map shipping cost - use shipping_label_cost from Amazon_Fees table
    if 'shipping_label_cost' in df.columns:
        shipping_label = df['shipping_label_cost'].astype(str).str.replace('$', '').str.replace(',', '').str.strip()
        transformed['shipping_cost'] = pd.to_numeric(shipping_label, errors='coerce').fillna(0)
    elif 'shipping-price' in df.columns:
        shipping_price = df['shipping-price'].astype(str).str.replace('$', '').str.replace(',', '').str.strip()
        transformed['shipping_cost'] = pd.to_numeric(shipping_price, errors='coerce').fillna(0)
    else:
        transformed['shipping_cost'] = 0

    # Map tax - combine item-tax and shipping-tax
    item_tax = 0
    shipping_tax = 0

    if 'item-tax' in df.columns:
        item_tax_clean = df['item-tax'].astype(str).str.replace('$', '').str.replace(',', '').str.strip()
        item_tax = pd.to_numeric(item_tax_clean, errors='coerce').fillna(0)

    if 'shipping-tax' in df.columns:
        shipping_tax_clean = df['shipping-tax'].astype(str).str.replace('$', '').str.replace(',', '').str.strip()
        shipping_tax = pd.to_numeric(shipping_tax_clean, errors='coerce').fillna(0)

    transformed['tax'] = item_tax + shipping_tax

    # Map state column - Amazon uses 'ship-state'
    if 'ship-state' in df.columns:
        transformed['state'] = df['ship-state'].astype(str).str.strip().str.upper()
        # Handle null/empty states
        transformed['state'] = transformed['state'].replace(['', 'NAN', 'NONE'], 'Unknown')
    else:
        transformed['state'] = 'Unknown'

    # Products column - use product-name
    if 'product-name' in df.columns:
        transformed['products'] = df['product-name'].astype(str).str.strip()
    else:
        transformed['products'] = 'Amazon Product'

    # Financial status - map from order-status
    if 'order-status' in df.columns:
        status_map = {
            'Canceled': 'refunded',
            'Cancelled': 'refunded',
            'Pending': 'pending',
            'Shipped': 'paid',
            'Delivered': 'paid',
            'Unshipped': 'pending'
        }
        transformed['financial_status'] = df['order-status'].astype(str).str.strip().map(status_map).fillna('paid')
        # Keep original order-status for unfulfilled tracking
        transformed['order_status'] = df['order-status'].astype(str).str.strip()
    else:
        transformed['financial_status'] = 'paid'
        transformed['order_status'] = 'Shipped'

    # Customer name (Amazon uses recipient-name)
    if 'recipient-name' in df.columns:
        transformed['customer_name'] = df['recipient-name'].astype(str).str.strip()
    else:
        transformed['customer_name'] = 'N/A'

    # Shipping address fields (Amazon uses ship-address, ship-city, ship-postal-code)
    if 'ship-address' in df.columns:
        transformed['shipping_address'] = df['ship-address'].astype(str).str.strip()
    else:
        transformed['shipping_address'] = 'N/A'

    if 'ship-city' in df.columns:
        transformed['shipping_city'] = df['ship-city'].astype(str).str.strip()
    else:
        transformed['shipping_city'] = 'N/A'

    if 'ship-postal-code' in df.columns:
        transformed['shipping_zipcode'] = df['ship-postal-code'].astype(str).str.strip()
    else:
        transformed['shipping_zipcode'] = 'N/A'

    # Calculate COGS (Cost of Goods Sold)
    # Estimate: 40% of revenue (adjust as needed)
    transformed['cogs'] = transformed['revenue'] * 0.40

    # Amazon platform fees - use shop_fees from Amazon_Fees table
    if 'shop_fees' in df.columns:
        shop_fees_clean = df['shop_fees'].astype(str).str.replace('$', '').str.replace(',', '').str.strip()
        transformed['platform_fee'] = pd.to_numeric(shop_fees_clean, errors='coerce').fillna(0)
    else:
        # Fallback: calculate as 15% referral fee + $0.99 per item
        transformed['platform_fee'] = (transformed['revenue'] * 0.15) + 0.99

    # Apply discounts if available
    total_discount = 0
    if 'item-promotion-discount' in df.columns:
        discount_clean = df['item-promotion-discount'].astype(str).str.replace('$', '').str.replace(',', '').str.strip()
        total_discount += pd.to_numeric(discount_clean, errors='coerce').fillna(0)

    if 'ship-promotion-discount' in df.columns:
        ship_discount = df['ship-promotion-discount'].astype(str).str.replace('$', '').str.replace(',', '').str.strip()
        total_discount += pd.to_numeric(ship_discount, errors='coerce').fillna(0)

    # Add discount field
    transformed['discount'] = total_discount

    # Calculate refund amount based on financial_status
    transformed['refund_amount'] = transformed.apply(
        lambda row: row['revenue'] if row['financial_status'] == 'refunded' else 0.0,
        axis=1
    )
    transformed['refund'] = transformed['refund_amount']

    # Add channel identifier
    transformed['channel'] = 'Amazon'

    # Calculate derived metrics
    # Net revenue = revenue - refunds - discounts
    transformed['net_revenue'] = transformed['revenue'] - transformed['refund_amount'] - total_discount

    # Gross profit = net_revenue - COGS
    transformed['gross_profit'] = transformed['net_revenue'] - transformed['cogs']

    # Net profit = gross_profit - shipping - platform fees
    transformed['net_profit'] = transformed['gross_profit'] - transformed['shipping_cost'] - transformed['platform_fee']

    # Remove rows with invalid dates or revenue
    transformed = transformed.dropna(subset=['date', 'revenue'])

    # Remove rows where revenue is 0 or negative
    transformed = transformed[transformed['revenue'] > 0]

    if transformed.empty:
        st.warning(f"⚠️ No valid data rows found for Amazon. Check that purchase-date has dates and item-price has numbers.")
        return None

    return transformed


def fetch_fee_data(table_name: str) -> pd.DataFrame:
    """
    Fetch fee data from Supabase fee tables.

    Args:
        table_name: Name of the fee table (Shopify_Fees, Walmart_Fees, Amazon_Fees)

    Returns:
        DataFrame containing fee data or None if error
    """
    try:
        client = get_supabase_client()

        if client is None:
            return None

        # Fetch all rows using pagination
        all_data = []
        batch_size = 1000
        offset = 0

        while True:
            response = client.table(table_name).select('*').range(offset, offset + batch_size - 1).execute()

            if not response.data:
                break

            all_data.extend(response.data)

            if len(response.data) < batch_size:
                break

            offset += batch_size

        if not all_data:
            return None

        return pd.DataFrame(all_data)

    except Exception as e:
        st.warning(f"⚠️ Could not fetch {table_name}: {str(e)}")
        return None


@st.cache_data(ttl=300)  # Cache for 5 minutes
def fetch_shopify_data() -> pd.DataFrame:
    """
    Fetch Shopify data from Supabase.

    Returns:
        DataFrame containing Shopify order data
    """
    try:
        client = get_supabase_client()

        if client is None:
            return None

        # Fetch all rows using pagination (Supabase has 1000 row default limit per request)
        all_data = []
        batch_size = 1000
        offset = 0

        while True:
            response = client.table(SHOPIFY_TABLE).select('*').range(offset, offset + batch_size - 1).execute()

            if not response.data:
                break

            all_data.extend(response.data)

            # If we got less than batch_size rows, we've reached the end
            if len(response.data) < batch_size:
                break

            offset += batch_size

        # Check if we got any data
        if not all_data:
            st.info(f"ℹ️ No data found in {SHOPIFY_TABLE} table. Using sample data.")
            return None

        # Convert to DataFrame
        df_raw = pd.DataFrame(all_data)

        # Fetch fee data
        df_fees = fetch_fee_data(SHOPIFY_FEES_TABLE)

        # Merge fee data with order data if available
        if df_fees is not None and not df_fees.empty:
            # Merge on order_id (or order_number if available)
            merge_key = 'order_id'
            if 'order_number' in df_raw.columns and 'order_number' in df_fees.columns:
                merge_key = 'order_number'
            elif 'order_id' in df_fees.columns:
                merge_key = 'order_id'

            df_raw = df_raw.merge(df_fees, on=merge_key, how='left', suffixes=('', '_fee'))

        # Transform the data to dashboard format
        df = transform_shopify_walmart_data(df_raw, 'Shopify')

        return df

    except Exception as e:
        st.error(f"❌ Error fetching Shopify data from Supabase: {str(e)}")
        return None


@st.cache_data(ttl=300)  # Cache for 5 minutes
def fetch_walmart_data() -> pd.DataFrame:
    """
    Fetch Walmart data from Supabase.

    Returns:
        DataFrame containing Walmart order data
    """
    try:
        client = get_supabase_client()

        if client is None:
            return None

        # Fetch all rows using pagination (Supabase has 1000 row default limit per request)
        all_data = []
        batch_size = 1000
        offset = 0

        while True:
            response = client.table(WALMART_TABLE).select('*').range(offset, offset + batch_size - 1).execute()

            if not response.data:
                break

            all_data.extend(response.data)

            # If we got less than batch_size rows, we've reached the end
            if len(response.data) < batch_size:
                break

            offset += batch_size

        # Check if we got any data
        if not all_data:
            st.info(f"ℹ️ No data found in {WALMART_TABLE} table. Using sample data.")
            return None

        # Convert to DataFrame
        df_raw = pd.DataFrame(all_data)

        # Fetch fee data
        df_fees = fetch_fee_data(WALMART_FEES_TABLE)

        # Merge fee data with order data if available
        if df_fees is not None and not df_fees.empty:
            # Merge on order_id
            if 'order_id' in df_fees.columns:
                df_raw = df_raw.merge(df_fees, on='order_id', how='left', suffixes=('', '_fee'))

        # Transform the data to dashboard format
        df = transform_shopify_walmart_data(df_raw, 'Walmart')

        return df

    except Exception as e:
        st.error(f"❌ Error fetching Walmart data from Supabase: {str(e)}")
        return None


@st.cache_data(ttl=300)  # Cache for 5 minutes
def fetch_amazon_data() -> pd.DataFrame:
    """
    Fetch Amazon data from Supabase.

    Returns:
        DataFrame containing Amazon order data
    """
    try:
        client = get_supabase_client()

        if client is None:
            return None

        # Fetch all rows using pagination (Supabase has 1000 row default limit per request)
        all_data = []
        batch_size = 1000
        offset = 0

        while True:
            response = client.table(AMAZON_TABLE).select('*').range(offset, offset + batch_size - 1).execute()

            if not response.data:
                break

            all_data.extend(response.data)

            # If we got less than batch_size rows, we've reached the end
            if len(response.data) < batch_size:
                break

            offset += batch_size

        # Check if we got any data
        if not all_data:
            st.info(f"ℹ️ No data found in {AMAZON_TABLE} table. Using sample data.")
            return None

        # Convert to DataFrame
        df_raw = pd.DataFrame(all_data)

        # Fetch fee data
        df_fees = fetch_fee_data(AMAZON_FEES_TABLE)

        # Merge fee data with order data if available
        if df_fees is not None and not df_fees.empty:
            # Merge on amazon-order-id
            if 'amazon-order-id' in df_fees.columns:
                df_raw = df_raw.merge(df_fees, on='amazon-order-id', how='left', suffixes=('', '_fee'))

        # Transform the data to dashboard format
        df = transform_amazon_data(df_raw)

        return df

    except Exception as e:
        st.error(f"❌ Error fetching Amazon data from Supabase: {str(e)}")
        return None


def fetch_all_order_data() -> pd.DataFrame:
    """
    Fetch and combine data from Shopify, Walmart, and Amazon.

    Returns:
        Combined DataFrame with all order data
    """
    dataframes = []

    # Fetch Shopify data
    df_shopify = fetch_shopify_data()
    if df_shopify is not None and not df_shopify.empty:
        dataframes.append(df_shopify)

    # Fetch Walmart data
    df_walmart = fetch_walmart_data()
    if df_walmart is not None and not df_walmart.empty:
        dataframes.append(df_walmart)

    # Fetch Amazon data
    df_amazon = fetch_amazon_data()
    if df_amazon is not None and not df_amazon.empty:
        dataframes.append(df_amazon)

    # Combine dataframes
    if dataframes:
        df_combined = pd.concat(dataframes, ignore_index=True)
        return df_combined
    else:
        return None


def insert_order(order_data: dict) -> bool:
    """
    Insert a new order into Supabase.

    Args:
        order_data: Dictionary containing order fields

    Returns:
        True if successful, False otherwise
    """
    try:
        client = get_supabase_client()

        if client is None:
            st.error("❌ Cannot insert order: Supabase client not initialized")
            return False

        # Insert the order
        response = client.table('orders').insert(order_data).execute()

        if response.data:
            st.success(f"✅ Order inserted successfully!")
            return True
        else:
            st.error("❌ Failed to insert order")
            return False

    except Exception as e:
        st.error(f"❌ Error inserting order: {str(e)}")
        return False


def get_data_summary(df: pd.DataFrame) -> dict:
    """
    Get a summary of the data for debugging/verification.

    Args:
        df: DataFrame to summarize

    Returns:
        Dictionary with summary statistics
    """
    if df is None or df.empty:
        return {'error': 'No data available'}

    return {
        'total_rows': len(df),
        'date_range': f"{df['date'].min()} to {df['date'].max()}",
        'channels': df['channel'].unique().tolist(),
        'total_revenue': df['revenue'].sum(),
        'total_orders': len(df),
        'columns': df.columns.tolist()
    }


# Optional: Bulk upload function for migrating from Google Sheets
def bulk_upload_from_dataframe(df: pd.DataFrame, batch_size: int = 100) -> bool:
    """
    Upload data from a DataFrame to Supabase in batches.
    Useful for migrating existing data from Google Sheets.

    Args:
        df: DataFrame with columns matching the orders table schema
        batch_size: Number of rows to upload per batch

    Returns:
        True if successful, False otherwise
    """
    try:
        client = get_supabase_client()

        if client is None:
            st.error("❌ Cannot upload: Supabase client not initialized")
            return False

        # Convert DataFrame to list of dictionaries
        records = df.to_dict('records')

        # Upload in batches
        total_batches = (len(records) + batch_size - 1) // batch_size

        for i in range(0, len(records), batch_size):
            batch = records[i:i + batch_size]
            batch_num = i // batch_size + 1

            response = client.table('orders').insert(batch).execute()

            if not response.data:
                st.error(f"❌ Failed to upload batch {batch_num}/{total_batches}")
                return False

            st.info(f"✅ Uploaded batch {batch_num}/{total_batches}")

        st.success(f"✅ Successfully uploaded {len(records)} records!")
        return True

    except Exception as e:
        st.error(f"❌ Error during bulk upload: {str(e)}")
        return False
