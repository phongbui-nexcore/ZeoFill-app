"""
Configuration file for ZeoFill Dashboard
"""

# Supabase Configuration
SUPABASE_CONFIG = {
    'url': '',  # Set via environment variable SUPABASE_URL
    'key': '',  # Set via environment variable SUPABASE_KEY
    'shopify_table': 'Shopify_OrderData',
    'walmart_table': 'Walmart_OrderData',
    'amazon_table': 'Amazon_OrderData'
}

# Legacy Google Sheets Configuration (deprecated - use Supabase instead)
GOOGLE_SHEETS_CONFIG = {
    'spreadsheet_id': '1ByOkKEI87_yL8X00Wcw0T9E-FqfMAZgeR_45VhC60R8',
    'shopify_sheet': 'OrderData_Shopify',
    'walmart_sheet': 'OrderData_Walmart',
    'credentials_file': 'credentials.json'
}

# Dashboard Configuration
DASHBOARD_CONFIG = {
    'page_title': 'ZeoFill Products Dashboard',
    'page_icon': '🌿',
    'layout': 'wide',
    'theme': {
        'primary_color': '#00ff88',
        'secondary_color': '#00cc6a',
        'background_color': '#0a0e27',
        'text_color': '#c9d1d9'
    }
}

# Data Refresh Settings
CACHE_CONFIG = {
    'ttl_seconds': 300,  # 5 minutes
    'auto_refresh': False
}

# Channel Configuration
CHANNELS = ['Shopify', 'Walmart', 'Amazon']

# Metrics Configuration
METRICS = {
    'revenue': {
        'display_name': 'Revenue',
        'format': 'currency',
        'description': 'Total sales revenue'
    },
    'profit': {
        'display_name': 'Profit',
        'format': 'currency',
        'description': 'Net profit after all costs'
    },
    'orders': {
        'display_name': 'Orders',
        'format': 'number',
        'description': 'Total number of orders'
    },
    'aov': {
        'display_name': 'Average Order Value',
        'format': 'currency',
        'description': 'Average revenue per order'
    }
}

# Date Range Presets
DATE_PRESETS = {
    'Last 7 Days': 7,
    'Last 30 Days': 30,
    'Last 90 Days': 90,
    'Last 6 Months': 180,
    'Last Year': 365
}

# Feature Flags
FEATURES = {
    'enable_supabase': True,
    'enable_google_sheets': False,  # Deprecated - migrated to Supabase
    'enable_sample_data': True,
    'enable_export': True,
    'enable_email_reports': False
}
