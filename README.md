# ZeoFill Analytics Dashboard

A modern, real-time analytics dashboard for e-commerce operations built with Streamlit and Supabase. Track revenue, profitability, and orders across Shopify, Walmart, and Amazon channels.

![Dashboard Preview](assets/company-logo.jpg)

## Features

- **Real-time Data**: Live connection to Supabase PostgreSQL database
- **Multi-Channel Support**: Shopify, Walmart, and Amazon integration
- **Comprehensive Analytics**:
  - Revenue and profit tracking
  - Channel performance comparison
  - Product-level insights
  - Geographic distribution
  - Growth metrics (MoM, YoY)
  - Unfulfilled orders management
- **Interactive Visualizations**: Built with Plotly for dynamic charts
- **Custom KPIs**: Tax owed, discounts, refunds, shipping costs, and more
- **Responsive Design**: Modern dark theme with glassmorphic UI

## Quick Start

### Prerequisites

- Python 3.8 or higher
- Supabase account ([sign up free](https://supabase.com))
- Order data from Shopify, Walmart, or Amazon

### Installation

1. **Clone the repository**
   ```bash
   git clone https://github.com/yourusername/zeofill-dashboard.git
   cd zeofill-dashboard
   ```

2. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

3. **Configure Supabase credentials**

   Create `.streamlit/secrets.toml` from the example:
   ```bash
   cp .env.example .streamlit/secrets.toml
   ```

   Edit `.streamlit/secrets.toml` and add your Supabase credentials:
   ```toml
   [supabase]
   url = "https://your-project-ref.supabase.co"
   key = "your-anon-or-service-role-key"
   ```

4. **Set up Supabase tables**

   See [SUPABASE_SETUP.md](SUPABASE_SETUP.md) for detailed instructions on creating the required tables.

5. **Run the dashboard**
   ```bash
   streamlit run zeofill_dashboard.py
   ```

   The dashboard will open in your browser at `http://localhost:8501`

## Supabase Setup

### Required Tables

Create three tables in your Supabase project:

1. **Shopify_OrderData**
   - Columns: `order_id`, `created_at`, `state`, `product_name`, `quantity`, `unit_price`, `line_total`, `line_tax`, `line_shipping`, `financial_status`, `fulfillment_status`, `shipping_terms`

2. **Walmart_OrderData**
   - Same schema as Shopify

3. **Amazon_OrderData**
   - Columns: `amazon-order-id`, `purchase-date`, `ship-state`, `product-name`, `quantity`, `item-price`, `item-tax`, `shipping-price`, `order-status`, `item-promotion-discount`, `ship-promotion-discount`

For detailed setup instructions, see [SUPABASE_SETUP.md](SUPABASE_SETUP.md)

## Testing Connection

Test your Supabase connection before running the dashboard:

```bash
python test_supabase_connection.py
```

This will verify:
- Supabase credentials are correct
- All tables exist and are accessible
- Data is being fetched properly

## Configuration

### Environment Variables

The dashboard supports two configuration methods:

1. **Streamlit Secrets** (Recommended for Streamlit Cloud)
   - Edit `.streamlit/secrets.toml`

2. **Environment Variables** (Alternative)
   - Create `.env` file from `.env.example`
   - Set `SUPABASE_URL` and `SUPABASE_KEY`

### Feature Flags

Edit `config.py` to customize:
- Channel names
- Date range presets
- Cache settings (default: 5 minutes)
- Metrics configuration

## Deployment

### Streamlit Cloud (Free)

1. Push your code to GitHub
2. Go to [share.streamlit.io](https://share.streamlit.io)
3. Connect your GitHub repository
4. Add your secrets in the Streamlit Cloud dashboard:
   - Go to App Settings → Secrets
   - Paste your `.streamlit/secrets.toml` content
5. Deploy!

Your dashboard will be available at `https://your-app-name.streamlit.app`

### Self-Hosted

Run with custom port and configuration:

```bash
streamlit run zeofill_dashboard.py --server.port 8080 --server.address 0.0.0.0
```

## Dashboard Tabs

### Overview
- Revenue trends across all channels
- Geographic distribution (US heatmap)
- Channel performance comparison
- Cost breakdown (COGS, fees, tax, shipping)
- Data summary (refunds, discounts)

### Profitability
- Profit distribution by channel
- Margin trends over time
- Profit waterfall analysis

### Products
- Top products by revenue
- Product performance table
- Sales and order counts

### Growth
- Month-over-Month (MoM) metrics
- Year-over-Year (YoY) growth
- Revenue velocity charts
- Annual run rate projections

### Unfulfilled Orders
- Pending orders by channel
- Geographic distribution
- Order aging analysis
- Export to CSV

## KPI Calculations

See [KPI_CALCULATIONS.md](KPI_CALCULATIONS.md) for detailed formulas including:
- Revenue and net profit
- Gross margin and net margin
- Refund rates
- Average order value (AOV)
- Cost breakdowns
- Tax owed (Shopify only)
- Discounts (all channels)

## Tech Stack

- **Frontend**: Streamlit
- **Charts**: Plotly
- **Database**: Supabase (PostgreSQL)
- **Data Processing**: Pandas, NumPy
- **Styling**: Custom CSS with glassmorphic design

## File Structure

```
zeofill-dashboard/
├── zeofill_dashboard.py          # Main dashboard application
├── supabase_integration.py       # Data fetching and transformation
├── config.py                      # Configuration settings
├── test_supabase_connection.py   # Connection testing utility
├── requirements.txt               # Python dependencies
├── .env.example                   # Environment template
├── .gitignore                     # Git ignore rules
├── README.md                      # This file
├── SUPABASE_SETUP.md             # Setup instructions
├── KPI_CALCULATIONS.md           # KPI documentation
├── .streamlit/
│   └── secrets.toml              # Credentials (not committed)
└── assets/
    └── company-logo.jpg          # Company logo
```

## Troubleshooting

### Dashboard shows "Demo Mode"
- Check that `supabase_integration.py` is imported successfully
- Verify your Supabase credentials in `.streamlit/secrets.toml`
- Run `test_supabase_connection.py` to diagnose connection issues

### No data showing
- Ensure your Supabase tables have data
- Check Row Level Security (RLS) policies allow SELECT operations
- Verify table names match exactly (case-sensitive)

### Slow performance
- Reduce cache TTL in `config.py` (default: 300 seconds)
- Enable RLS policies to limit data access
- Consider adding database indexes on `created_at` and `order_id` columns

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## License

MIT License - feel free to use this dashboard for your business.

## Support

For questions or issues:
- Check [SUPABASE_SETUP.md](SUPABASE_SETUP.md) for setup help
- Review [KPI_CALCULATIONS.md](KPI_CALCULATIONS.md) for metric definitions
- Open an issue on GitHub

---

Built with ❤️ for ZeoFill Analytics
# Trigger deployment
