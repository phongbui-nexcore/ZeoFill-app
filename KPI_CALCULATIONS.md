# ZeoFill Dashboard - KPI Calculations Documentation

This document provides a comprehensive overview of how all Key Performance Indicators (KPIs) are calculated in the ZeoFill Analytics Dashboard.

---

## 📊 Data Sources

### Google Sheets Integration
- **Spreadsheet ID**: `1ByOkKEI87_yL8X00Wcw0T9E-FqfMAZgeR_45VhC60R8`
- **Shopify Sheet**: `OrderData_Shopify`
- **Walmart Sheet**: `OrderData_Walmart`

### Column Mapping from Google Sheets
```
Google Sheets Column → Dashboard Column
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
created_at          → date
id                  → order_id (Shopify only)
total_price         → revenue
total_shipping      → shipping_cost
total_tax           → tax
state               → state
products            → products
financial_status    → financial_status
```

---

## 💰 Core Revenue Metrics

### 1. **Total Revenue**
```
Total Revenue = SUM(total_price)
```
- **Source**: `total_price` column from Google Sheets
- **Description**: Sum of all order values before any deductions
- **Location**: Overview Tab, Top KPI Card #1

### 2. **Net Revenue**
```
Net Revenue = Revenue - Refund Amount - Tax
```
- **Formula**: `df['revenue'] - df['refund_amount'] - df['tax']`
- **Description**: Revenue after removing refunds and taxes
- **Location**: Overview Tab, displayed as "Net" under Total Revenue card

### 3. **Refund Amount**
```
Refund Amount = Revenue IF financial_status == 'refunded' ELSE 0
```
- **Conditional Logic**:
  - If `financial_status = 'refunded'` → Refund Amount = Full Revenue
  - Otherwise → Refund Amount = 0
- **Description**: Total value of refunded orders
- **Location**: Cost Breakdown panel

### 4. **Refund Rate**
```
Refund Rate (%) = (Total Refund Amount / Total Revenue) × 100
```
- **Formula**: `(df['refund_amount'].sum() / df['revenue'].sum()) * 100`
- **Description**: Percentage of revenue that was refunded
- **Display**: Shown as circular gauge in Top KPI Card #1

---

## 📈 Profitability Metrics

### 5. **COGS (Cost of Goods Sold)**
```
COGS = Revenue × 40%
```
- **Fixed Rate**: 40% of revenue
- **Formula**: `df['revenue'] * 0.40`
- **Description**: Estimated cost to produce/acquire the goods sold
- **Configurable**: Can be adjusted in `google_sheets_integration.py` line 100
- **Location**: Cost Breakdown panel

### 6. **Platform Fees**

#### Shopify Orders:
```
Platform Fee = (Revenue × 5.9%) + $0.30
```
- **Formula**: `(df['revenue'] * 0.059) + 0.30`
- **Components**:
  - 5.9% transaction fee
  - $0.30 fixed per-transaction fee

#### Walmart Orders:
```
Platform Fee = Revenue × 15%
```
- **Formula**: `df['revenue'] * 0.15`
- **Components**:
  - 15% flat referral fee

**Location**: Cost Breakdown panel

### 7. **Gross Profit**
```
Gross Profit = Net Revenue - COGS
```
- **Formula**: `df['net_revenue'] - df['cogs']`
- **Description**: Profit after deducting cost of goods, before operating expenses
- **Location**: Top KPI Card #2, Profitability Tab

### 8. **Net Profit**
```
Net Profit = Gross Profit - Shipping Cost - Platform Fee
```
- **Formula**: `df['gross_profit'] - df['shipping_cost'] - df['platform_fee']`
- **Description**: Final profit after all costs
- **Location**: Top KPI Card #2

### 9. **Gross Margin**
```
Gross Margin (%) = (Gross Profit / Net Revenue) × 100
```
- **Formula**: `(df['gross_profit'].sum() / df['net_revenue'].sum()) * 100`
- **Description**: Percentage of revenue retained after COGS
- **Location**: Profitability Tab - Margin Trends chart

### 10. **Net Margin**
```
Net Margin (%) = (Net Profit / Net Revenue) × 100
```
- **Formula**: `(df['net_profit'].sum() / df['net_revenue'].sum()) * 100`
- **Description**: Percentage of revenue retained as final profit
- **Display**: Shown as circular gauge in Top KPI Card #2
- **Location**: Profitability Tab - Margin Trends chart

---

## 📦 Order Metrics

### 11. **Total Orders**
```
Total Orders = COUNT(orders)
```
- **Formula**: `len(df)`
- **Description**: Total number of orders in the selected period
- **Location**: Top KPI Card #3

### 12. **Average Order Value (AOV)**
```
AOV = Net Revenue / Total Orders
```
- **Formula**: `df['net_revenue'].sum() / len(df)`
- **Description**: Average revenue per order
- **Location**: Top KPI Card #3, shown as "Avg"
- **AOV Goal**: Target is $250 (shown as circular gauge progress)

---

## 📊 Growth Metrics (Growth Tab)

### 13. **MoM Revenue Growth (Month-over-Month)**
```
MoM Revenue Growth (%) = ((Current Month Revenue - Previous Month Revenue) / Previous Month Revenue) × 100
```
- **Calculation Steps**:
  1. Resample data to monthly: `df.resample('M').agg({'revenue': 'sum'})`
  2. Get current month: `current_month = df_monthly.iloc[-1]`
  3. Get previous month: `prev_month = df_monthly.iloc[-2]`
  4. Calculate growth: `((current - prev) / prev) * 100`
- **Location**: Growth Tab, KPI Card #1

### 14. **MoM Net Profit Growth**
```
MoM Net Profit Growth (%) = ((Current Month Net Profit - Previous Month Net Profit) / Previous Month Net Profit) × 100
```
- **Same calculation as MoM Revenue Growth, but using net_profit**
- **Location**: Growth Tab, KPI Card #2

### 15. **YoY Revenue Growth (Year-over-Year)**
```
YoY Revenue Growth (%) = ((Current Year Revenue - Previous Year Revenue) / Previous Year Revenue) × 100
```
- **Calculation Steps**:
  1. Resample data to yearly: `df.resample('Y').agg({'revenue': 'sum'})`
  2. Get current year: `current_year = df_yearly.iloc[-1]`
  3. Get previous year: `prev_year = df_yearly.iloc[-2]`
  4. Calculate growth: `((current - prev) / prev) * 100`
- **Fallback**: If less than 2 years of data, uses annualized MoM growth: `MoM * 12`
- **Location**: Growth Tab, KPI Card #3

### 16. **YoY Net Profit Growth**
```
YoY Net Profit Growth (%) = ((Current Year Net Profit - Previous Year Net Profit) / Previous Year Net Profit) × 100
```
- **Same calculation as YoY Revenue Growth, but using net_profit**
- **Fallback**: If less than 2 years of data, uses annualized MoM growth: `MoM * 12`
- **Location**: Growth Tab, KPI Card #4

### 17. **Annual Run Rate (Projected)**
```
Annual Run Rate = Current Month Revenue × 12
```
- **Formula**: `current_month['revenue'] * 12`
- **Description**: Annualized projection based on current month's performance
- **Assumption**: Current month's revenue will remain constant throughout the year
- **Location**: Growth Tab, KPI Card #5

---

## 📍 Geographic & Product Metrics

### 18. **Orders by State**
```
State Orders = COUNT(orders) WHERE state = X
```
- **Source**: `state` column from Google Sheets
- **Visualization**: Choropleth heatmap of USA
- **Location**: Overview Tab - Orders by State map

### 19. **Product Revenue**
```
Product Revenue = SUM(revenue) WHERE products = X
```
- **Source**: `products` column from Google Sheets
- **Aggregation**: Grouped by product name
- **Location**: Products Tab - Top Products by Revenue chart

### 20. **Product Order Count**
```
Product Orders = COUNT(orders) WHERE products = X
```
- **Location**: Products Tab - Product Details table

---

## 🛒 Channel Metrics

### 21. **Channel Revenue Split**
```
Channel Revenue = SUM(revenue) WHERE channel = 'Shopify' OR 'Walmart'
```
- **Breakdown**: Revenue and orders aggregated by sales channel
- **Location**: Overview Tab - Channel Revenue Split chart

### 22. **Channel Profit Distribution**
```
Channel Gross Profit = SUM(gross_profit) WHERE channel = X
```
- **Visualization**: Donut chart showing profit contribution by channel
- **Location**: Profitability Tab - Profit Distribution chart

---

## 📉 Cost Analysis Metrics

### 23. **Total Shipping Cost**
```
Total Shipping = SUM(total_shipping)
```
- **Source**: `total_shipping` column from Google Sheets
- **Location**: Cost Breakdown panel - Data Summary

### 24. **Total Tax**
```
Total Tax = SUM(total_tax)
```
- **Source**: `total_tax` column from Google Sheets
- **Used In**: Net Revenue calculation

### 25. **Cost Percentages (Cost Breakdown Panel)**
All percentages are calculated as a proportion of Total Revenue:

```
COGS % = (Total COGS / Total Revenue) × 100
Platform Fees % = (Total Platform Fees / Total Revenue) × 100
Shipping % = (Total Shipping Cost / Total Revenue) × 100
Refunds % = (Total Refunds / Total Revenue) × 100
```

**Visualization**: Circular gauges showing percentage and dollar amount
**Hover Effect**: On hover, percentage replaces the dollar amount

---

## 📊 Trend Charts Calculations

### 26. **Revenue Trend (7-Day Moving Average)**
```
Daily Revenue Smooth = 7-Day Rolling Average of Daily Revenue
```
- **Formula**: `df.groupby('date')['revenue'].sum().rolling(7).mean()`
- **Purpose**: Smooths daily fluctuations to show overall trend
- **Location**: Overview Tab - Revenue Trend chart

### 27. **Profit Margin Trend**
```
Daily Gross Margin % = (Daily Gross Profit / Daily Revenue) × 100 [7-day average]
Daily Net Margin % = (Daily Net Profit / Daily Revenue) × 100 [7-day average]
```
- **Smoothing**: 7-day rolling average applied
- **Location**: Profitability Tab - Margin Trends chart

### 28. **Revenue Velocity Chart**
Shows two metrics together:
1. **Monthly Revenue** (bar chart): Total revenue per month
2. **Growth Rate %** (line chart): MoM growth percentage

**Location**: Growth Tab - Revenue Velocity chart

---

## 🔄 Delta Calculations (vs Previous Period)

All Top KPI cards show deltas (changes) compared to the previous 30-day period:

### Delta Formula:
```
Delta (%) = ((Current Period Value - Previous Period Value) / Previous Period Value) × 100
```

**Current Period**: Last 30 days
**Previous Period**: 30 days before that (days 31-60)

**Applied to**:
- Total Revenue Delta
- Net Profit Delta
- Total Orders Delta
- AOV Delta

**Color Coding**:
- 🟢 Green (positive): Growth/increase
- 🔴 Red (negative): Decline/decrease

---

## 🎯 Profit Waterfall Breakdown

The waterfall chart in the Profitability Tab shows the step-by-step flow from Revenue to Net Profit:

```
Step 1: Revenue (starting point)
Step 2: - Refunds
Step 3: - COGS
Step 4: - Shipping Costs
Step 5: - Platform Fees
Final: = Net Profit
```

Each bar shows the magnitude of reduction at each step.

---

## 📅 Date Filtering

### Available Filters:
1. **All**: Shows all available data (no date filter)
2. **Last 7 Days**: `date >= (today - 7 days)`
3. **Last 30 Days**: `date >= (today - 30 days)` *(default)*
4. **Last 90 Days**: `date >= (today - 90 days)`
5. **Custom**: User-defined date range

### Date Comparison:
```python
start = pd.Timestamp(date_range[0])
end = pd.Timestamp(date_range[1])
filtered_df = df[(df['date'] >= start) & (df['date'] <= end)]
```

---

## 🔧 Data Transformation Pipeline

### Raw Data → Dashboard Data Flow:

1. **Fetch from Google Sheets**
   - Connect using service account credentials
   - Read `OrderData_Shopify` and `OrderData_Walmart`

2. **Column Mapping**
   - Map Google Sheets columns to dashboard schema
   - Clean numeric values (remove commas, convert to float)

3. **Derived Calculations**
   ```python
   # Calculate COGS
   df['cogs'] = df['revenue'] * 0.40

   # Calculate Platform Fees
   df['platform_fee'] = (df['revenue'] * 0.059) + 0.30  # Shopify
   df['platform_fee'] = df['revenue'] * 0.15  # Walmart

   # Calculate Refunds
   df['refund_amount'] = df.apply(
       lambda row: row['revenue'] if row['financial_status'] == 'refunded' else 0,
       axis=1
   )

   # Calculate Net Revenue
   df['net_revenue'] = df['revenue'] - df['refund_amount'] - df['tax']

   # Calculate Gross Profit
   df['gross_profit'] = df['net_revenue'] - df['cogs']

   # Calculate Net Profit
   df['net_profit'] = df['gross_profit'] - df['shipping_cost'] - df['platform_fee']
   ```

4. **Data Validation**
   - Remove rows with invalid dates
   - Remove rows with zero or negative revenue
   - Convert state codes to uppercase

5. **Combine Channels**
   - Merge Shopify and Walmart data into single DataFrame
   - Add `channel` column identifier

---

## 🎨 Visual Indicators

### Circular Gauges (Top KPI Cards):
- **Refund Rate**: Shows percentage of refunded revenue (0-100%)
- **Net Margin**: Shows net profit as % of revenue (0-100%)
- **AOV Goal**: Shows AOV progress toward $250 target

### Color Coding:
- **Teal (#2DD4BF)**: Primary accent, Shopify channel
- **Purple (#818CF8)**: Secondary accent, Walmart channel
- **Green (#34D399)**: Positive growth/gains
- **Red (#F87171)**: Negative growth/losses
- **Gray (#9CA3AF)**: Neutral text/secondary info

---

## 📝 Important Notes

### Cost Assumptions:
1. **COGS = 40% of revenue** - This is configurable in `google_sheets_integration.py:100`
2. **Platform fees are channel-specific** - Different rates for Shopify vs Walmart
3. **Refunds** - When an order is refunded, the full revenue is counted as refund (no partial refunds currently)

### Data Refresh:
- **Cache Duration**: 5 minutes (`@st.cache_data(ttl=300)`)
- **Manual Refresh**: Not available in current version (removed sidebar)
- **Auto-refresh**: Data reloads every 5 minutes automatically

### Performance:
- **Sample Data Fallback**: If Google Sheets fails to load, dashboard shows sample data
- **Date Range Impact**: Larger date ranges may slow down chart rendering
- **Moving Averages**: 7-day rolling averages are used to smooth volatility in trend charts

---

## 🔍 File Locations

### Calculation Logic:
- **Main Metrics**: `zeofill_dashboard.py` - `calculate_metrics()` function (lines 435-464)
- **Data Transformation**: `google_sheets_integration.py` - `transform_sheet_data()` function (lines 35-141)
- **Platform Fees**: `google_sheets_integration.py` lines 103-108
- **COGS Rate**: `google_sheets_integration.py` line 100
- **Refund Logic**: `google_sheets_integration.py` lines 110-116

### Configuration:
- **Google Sheets Credentials**: `.streamlit/secrets.toml`
- **Spreadsheet & Sheet Names**: `google_sheets_integration.py` lines 23-26
- **Color Scheme**: `zeofill_dashboard.py` CSS variables (lines 49-60)

---

## 📧 Support

For questions about KPI calculations or to request changes to formulas:
1. Review this documentation first
2. Check the source code locations listed above
3. Modify configurable parameters (COGS rate, platform fees) as needed

**Last Updated**: December 14, 2025
