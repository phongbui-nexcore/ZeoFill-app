import streamlit as st
import pandas as pd
import plotly.graph_objects as go
import plotly.express as px
from datetime import datetime, timedelta
import numpy as np
from typing import Dict, List, Tuple
import streamlit.components.v1 as components
import hashlib


# --- CONFIG & ASSETS ---
st.set_page_config(
   page_title="ZeoFill Analytics",
   page_icon="🐾",
   layout="wide",
   initial_sidebar_state="collapsed"
)

# --- PASSWORD PROTECTION ---
def check_password():
    """Returns `True` if the user has entered the correct password."""

    def password_entered():
        """Checks whether a password entered by the user is correct."""
        # Get the password from secrets
        if "dashboard_password" in st.secrets:
            correct_password = st.secrets["dashboard_password"]
        else:
            # Fallback password if not in secrets (for local testing)
            correct_password = "zeofill2024"

        if st.session_state["password"] == correct_password:
            st.session_state["password_correct"] = True
            del st.session_state["password"]  # Don't store password
            # Clear data_loaded to show loading screen after login
            if 'data_loaded' in st.session_state:
                del st.session_state['data_loaded']
        else:
            st.session_state["password_correct"] = False

    # Return True if password is already validated
    if st.session_state.get("password_correct", False):
        return True

    # Show login form with logo
    st.markdown("""
        <style>
        .login-container {
            max-width: 800px;
            margin: 100px auto;
            padding: 40px;
            text-align: center;
        }
        .login-logo {
            margin-bottom: 30px;
        }
        .login-logo img {
            max-width: 200px;
            border-radius: 10px;
        }
        .login-subtitle {
            color: #9CA3AF;
            margin-bottom: 30px;
            font-size: 1rem;
        }
        .login-subtitle .lock-icon {
            color: #2DD4BF;
            font-size: 1.2rem;
        }
        </style>
    """, unsafe_allow_html=True)

    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        st.markdown('<div class="login-container">', unsafe_allow_html=True)

        # Display company logo
        try:
            logo_path = Path("assets/company-logo.jpg")
            if logo_path.exists():
                st.image(str(logo_path), use_container_width=False, width=200)
            else:
                st.markdown('<div class="login-logo">🐾 ZeoFill</div>', unsafe_allow_html=True)
        except:
            st.markdown('<div class="login-logo">🐾 ZeoFill</div>', unsafe_allow_html=True)

        st.markdown('<div class="login-subtitle"><span class="lock-icon">🔒</span> Enter password to access dashboard</div>', unsafe_allow_html=True)

        st.text_input(
            "Password",
            type="password",
            on_change=password_entered,
            key="password",
            label_visibility="collapsed",
            placeholder="Enter password"
        )

        if "password_correct" in st.session_state and not st.session_state["password_correct"]:
            st.error("😕 Incorrect password. Please try again.")
            # Add retry button
            if st.button("🔄 Try Again", use_container_width=True):
                # Clear the password_correct state to allow retry
                del st.session_state["password_correct"]
                st.rerun()

        st.markdown('</div>', unsafe_allow_html=True)

    return False

# Import Supabase integration
try:
    from supabase_integration import fetch_all_order_data
    SUPABASE_AVAILABLE = True
except ImportError:
    SUPABASE_AVAILABLE = False


# Logo URLs - Use local file for company logo
import base64
from pathlib import Path

def get_local_image_base64(image_path):
    """Convert local image to base64 for embedding in HTML"""
    try:
        with open(image_path, "rb") as f:
            data = f.read()
        return f"data:image/jpeg;base64,{base64.b64encode(data).decode()}"
    except FileNotFoundError:
        # Fallback to online URL if file not found
        return "https://zeofill.com/wp-content/uploads/2018/01/ZeoFill-Logo-Retina.png"

# Try to load local logo, fallback to URL if not found
ZEOFILL_LOGO_URL = get_local_image_base64("assets/company-logo.jpg")
SHOPIFY_LOGO_URL = "https://cdn.icon-icons.com/icons2/2429/PNG/512/shopify_logo_icon_147243.png"
WALMART_LOGO_URL = "https://cdn.icon-icons.com/icons2/2699/PNG/512/walmart_logo_icon_170230.png"
AMAZON_LOGO_URL = "https://cdn.icon-icons.com/icons2/2699/PNG/512/amazon_logo_icon_170594.png"


# --- CSS STYLING ---
# We inject this CSS to handle the vertical alignment and card styling
KPI_CSS = """
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&display=swap');
:root {
   --bg-color: #0B0E14;
   --card-bg: rgba(30, 41, 59, 0.7);
   --text-primary: #F3F4F6;
   --text-secondary: #9CA3AF;
   --accent-primary: #2DD4BF; /* Teal */
   --accent-secondary: #818CF8; /* Purple */
   --border-color: rgba(255, 255, 255, 0.1);
   --green: #34D399;
   --red: #F87171;
}


body {
   background-color: transparent;
   font-family: 'Inter', sans-serif !important;
   color: var(--text-primary) !important;
   margin: 0;
}


/* --- GLOWING KPI CARDS --- */
.metric-card-combined {
   background: var(--card-bg);
   backdrop-filter: blur(10px);
   border: 1px solid var(--border-color);
   border-radius: 16px;
   padding: 24px;
   display: flex;
   justify-content: space-between;
   align-items: center;
   height: 100%;
   transition: all 0.4s ease;
   box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.1);
   overflow: visible;
}


.metric-card-combined:hover {
   border-color: var(--accent-primary);
   box-shadow: 0 0 20px rgba(45, 212, 191, 0.3);
   transform: translateY(-2px);
   z-index: 10;
}


.metric-main-content {
   display: flex;
   flex-direction: column;
   justify-content: center;
}
.metric-label { color: var(--text-secondary); font-size: 0.85rem; font-weight: 600; text-transform: uppercase; letter-spacing: 0.05em; margin-bottom: 6px; }
.metric-value { font-size: 2.8rem; font-weight: 700; color: #ffffff; letter-spacing: -1px; line-height: 1.1; margin-bottom: 8px; }
.metric-delta {
   display: inline-flex;
   align-items: center;
   padding: 4px 10px;
   border-radius: 20px;
   font-size: 0.85rem;
   font-weight: 600;
   width: fit-content;
}
.delta-pos { background-color: rgba(52, 211, 153, 0.15); color: var(--green); }
.delta-neg { background-color: rgba(248, 113, 113, 0.15); color: var(--red); }
.metric-sub-label { color: var(--text-secondary); font-size: 0.85rem; font-weight: 500; margin-top: 8px; }


/* --- RIGHT PANEL: COST BREAKDOWN --- */
.cost-panel-container {
   background: var(--card-bg);
   border: 1px solid var(--border-color);
   border-radius: 20px;
   padding: 25px;
   height: 100%;
}
.cost-header {
   font-size: 1.1rem;
   font-weight: 700;
   margin-bottom: 25px;
   color: white;
   background: rgba(0,0,0,0.3);
   padding: 10px 15px;
   border-radius: 8px;
   display: inline-block;
}
.kpi-row {
   display: flex;
   justify-content: space-around;
   align-items: center;
   margin-bottom: 30px;
}


/* --- CIRCULAR CHART SVG STYLES --- */
.circular-chart {
 display: block;
 margin: 0 auto;
 max-width: 100%;
 max-height: 100%;
}
.circle-bg {
 fill: none;
 stroke: rgba(255,255,255,0.05);
 stroke-width: 2.5;
}
.circle-fill {
 fill: none;
 stroke: var(--accent-primary);
 stroke-width: 2.5;
 stroke-linecap: round;
 transition: stroke-dasharray 1s ease;
}


/* Text Styling inside SVG */
.text-label {
   fill: var(--text-secondary);
   font-family: 'Inter', sans-serif;
   font-size: 4px;
   text-anchor: middle;
   font-weight: 500;
}
.text-value {
   fill: #ffffff;
   font-family: 'Inter', sans-serif;
   font-size: 5px;
   text-anchor: middle;
   font-weight: 700;
}
.text-percent {
   fill: var(--accent-primary);
   font-family: 'Inter', sans-serif;
   font-size: 8px;
   text-anchor: middle;
   font-weight: 700;
   opacity: 0;
   transition: opacity 0.3s ease;
}


/* Hover Effects for Cost Circles */
.cost-circle-wrapper {
   transition: transform 0.3s ease;
   cursor: pointer;
}
.cost-circle-wrapper:hover {
   transform: translateY(-5px) scale(1.05);
}
.cost-circle-wrapper:hover .text-percent {
   opacity: 1;
}
.cost-circle-wrapper:hover .text-value,
.cost-circle-wrapper:hover .text-label {
   opacity: 0.2;
}


/* --- GROWTH KPI CARD --- */
.growth-kpi-container {
   background: var(--card-bg);
   border: 1px solid var(--border-color);
   border-radius: 16px;
   padding: 20px;
   margin-bottom: 10px;
   display: flex;
   flex-direction: column;
   justify-content: center;
   height: 100%;
   transition: all 0.4s ease;
   cursor: pointer;
   position: relative;
}

.growth-kpi-container:hover {
   border-color: var(--accent-primary);
   box-shadow: 0 0 30px rgba(45, 212, 191, 0.4), 0 0 60px rgba(45, 212, 191, 0.2);
   transform: translateY(-4px) scale(1.02);
   background: linear-gradient(135deg, rgba(30, 41, 59, 0.9) 0%, rgba(45, 212, 191, 0.1) 100%);
}

.growth-kpi-container::before {
   content: '';
   position: absolute;
   top: -2px;
   left: -2px;
   right: -2px;
   bottom: -2px;
   background: linear-gradient(45deg, #2DD4BF, #818CF8, #34D399, #2DD4BF);
   border-radius: 16px;
   opacity: 0;
   z-index: -1;
   transition: opacity 0.4s ease;
   background-size: 300% 300%;
   animation: gradient-shift 3s ease infinite;
}

.growth-kpi-container:hover::before {
   opacity: 0.6;
}

@keyframes gradient-shift {
   0% { background-position: 0% 50%; }
   50% { background-position: 100% 50%; }
   100% { background-position: 0% 50%; }
}

/* --- REMOVE GAP BETWEEN KPI ROW AND DIVIDER --- */

/* Kill HR vertical spacing */
hr {
    margin-top: 0 !important;
    margin-bottom: 0 !important;
}

/* Remove iframe spacing from components.html */
iframe {
    margin-bottom: 0 !important;
    padding-bottom: 0 !important;
}

/* Remove Streamlit vertical block spacing */
div[data-testid="stVerticalBlock"] {
    gap: 0 !important;
}

.growth-title { font-size: 0.9rem; color: var(--text-secondary); text-transform: uppercase; font-weight: 600; margin-bottom: 5px; }
.growth-value { font-size: 2rem; color: #fff; font-weight: 700; }
.growth-delta { font-size: 0.9rem; margin-top: 5px; font-weight: 600; }
.g-pos { color: var(--green); }
.g-neg { color: var(--red); }


</style>
"""


def load_css():
   st.markdown("""
   <style>
   @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&display=swap');


   :root {
       --bg-color: #0B0E14;
       --card-bg: rgba(30, 41, 59, 0.7);
       --text-primary: #F3F4F6;
       --accent-primary: #2DD4BF;
       --border-color: rgba(255, 255, 255, 0.1);
   }
   .stApp { background-color: var(--bg-color); font-family: 'Inter', sans-serif; }
  
   /* Chart Containers */
   .chart-container {
       background: var(--card-bg);
       border: 1px solid var(--border-color);
       border-radius: 16px;
       padding: 20px;
       margin-top: 10px;
       box-shadow: 0 4px 6px rgba(0,0,0,0.1);
   }
   .chart-header { font-size: 1.1rem; font-weight: 600; margin-bottom: 15px; color: var(--text-primary); }


   /* Filters - Vertical Alignment Fix */
   div[data-testid="column"] {
       display: flex;
       flex-direction: column;
       justify-content: center;
   }
  
   /* Form inputs styling */
   div[data-testid="stSelectbox"] > div > div { background-color: #111827; color: white; border: 1px solid var(--border-color); }
   div[data-testid="stMultiSelect"] > div > div { background-color: #111827; border: 1px solid var(--border-color); }


   /* Status Indicator */
   .status-pill {
       display: inline-flex; align-items: center; padding: 6px 12px;
       border-radius: 20px; font-size: 0.8rem; font-weight: 600; margin-left: 15px;
   }
   .status-live { background: rgba(52, 211, 153, 0.1); color: #34D399; border: 1px solid rgba(52, 211, 153, 0.3); }
   .status-sample { background: rgba(251, 191, 36, 0.1); color: #FBBF24; border: 1px solid rgba(251, 191, 36, 0.3); }


   /* Tab Styling (Radio Buttons as Tabs) */
   div[role="radiogroup"] {
       gap: 0px !important;
       background: transparent !important;
       border-bottom: 1px solid var(--border-color);
       padding-bottom: 0px;
   }

   div[role="radiogroup"] label {
       background-color: transparent !important;
       border: none !important;
       border-radius: 0 !important;
       padding: 12px 24px !important;
       font-weight: 600 !important;
       color: #9CA3AF !important;
       border-bottom: 2px solid transparent !important;
       transition: all 0.3s ease !important;
       cursor: pointer !important;
   }

   div[role="radiogroup"] label:hover {
       color: var(--accent-primary) !important;
       background: rgba(255,255,255,0.03) !important;
   }

   div[role="radiogroup"] label[data-checked="true"] {
       color: var(--accent-primary) !important;
       border-bottom: 2px solid var(--accent-primary) !important;
   }

   /* Hide radio button circles */
   div[role="radiogroup"] input[type="radio"] {
       display: none !important;
   }


   #MainMenu, footer, header {visibility: hidden;}
   .block-container { padding-top: 2rem; padding-left: 2rem; padding-right: 2rem; }
  
   /* --- REMOVE GAP BETWEEN KPI ROW AND DIVIDER --- */


   /* Kill HR vertical spacing */
   hr {
       margin-top: 0rem !important;
       margin-bottom: 0rem !important;
   }


   /* Remove iframe spacing from components.html */
   iframe {
       margin-bottom: 0rem !important;
       padding-bottom: 0rem !important;
   }


   /* Remove Streamlit block spacing below columns */
   div[data-testid="stVerticalBlock"] > div {
       gap: 0rem !important;
   }
              
   </style>
   """, unsafe_allow_html=True)


# --- DATA & METRICS ---
@st.cache_data
def generate_sample_data():
   np.random.seed(42)
   # Generate 6 months of data to allow for meaningful growth charts
   end_date = datetime.now()
   start_date = end_date - timedelta(days=210)
   dates = pd.date_range(start=start_date, end=end_date, freq='D')
   products_list = ["ZeoFill Infill (50lb)", "ZeoFill Infill (Pallet)", "Pet Deodorizer 32oz", "Pet Deodorizer 1Gal", "Turf Rake", "Odor Neutralizer"]
   states_list = ['CA', 'TX', 'FL', 'NY', 'AZ', 'NV', 'WA', 'CO', 'IL', 'GA']
   data = []
  
   # Simulate a growth trend
   growth_factor = np.linspace(0.8, 1.3, len(dates)) # Revenue grows over time


   for idx, date in enumerate(dates):
       gf = growth_factor[idx]
       # Shopify
       n_shop = np.random.poisson(8 * gf)
       for _ in range(n_shop):
           rev = np.random.uniform(50, 300)
           is_refund = np.random.random() < 0.05
           data.append({
               'date': date, 'channel': 'Shopify', 'revenue': rev,
               'cogs': rev * np.random.uniform(0.35, 0.45), 'shipping_cost': np.random.uniform(5, 15),
               'platform_fee': rev * 0.029 + 0.30, 'financial_status': 'refunded' if is_refund else 'paid',
               'state': np.random.choice(states_list, p=[0.3, 0.2, 0.1, 0.1, 0.1, 0.05, 0.05, 0.05, 0.025, 0.025]),
               'products': np.random.choice(products_list)
           })
       # Walmart
       n_wal = np.random.poisson(5 * gf)
       for _ in range(n_wal):
           rev = np.random.uniform(80, 400)
           is_refund = np.random.random() < 0.03
           data.append({
               'date': date, 'channel': 'Walmart', 'revenue': rev,
               'cogs': rev * np.random.uniform(0.40, 0.50), 'shipping_cost': np.random.uniform(8, 20),
               'platform_fee': rev * 0.15, 'financial_status': 'refunded' if is_refund else 'paid',
               'state': np.random.choice(states_list), 'products': np.random.choice(products_list)
           })
       # Amazon
       n_amz = np.random.poisson(6 * gf)
       for _ in range(n_amz):
           rev = np.random.uniform(60, 350)
           is_refund = np.random.random() < 0.04
           data.append({
               'date': date, 'channel': 'Amazon', 'revenue': rev,
               'cogs': rev * np.random.uniform(0.38, 0.48), 'shipping_cost': np.random.uniform(6, 18),
               'platform_fee': (rev * 0.15) + 0.99, 'financial_status': 'refunded' if is_refund else 'paid',
               'state': np.random.choice(states_list), 'products': np.random.choice(products_list)
           })
   df = pd.DataFrame(data)
   df['refund_amount'] = df.apply(lambda x: x['revenue'] if x['financial_status'] == 'refunded' else 0, axis=1)
   df['net_revenue'] = df['revenue'] - df['refund_amount']
   df['gross_profit'] = df['net_revenue'] - df['cogs']
   df['net_profit'] = df['gross_profit'] - df['shipping_cost'] - df['platform_fee']
   return df


def calculate_metrics(df: pd.DataFrame, df_prev: pd.DataFrame = None) -> Dict:
   # Calculate tax owed (only from Shopify channel)
   df_shopify = df[df['channel'] == 'Shopify']
   total_tax_owed = 0
   if not df_shopify.empty and 'tax' in df_shopify.columns:
       total_tax_owed = df_shopify['tax'].sum()

   # Calculate total discounts (if discount column exists)
   total_discounts = 0
   if 'discount' in df.columns:
       total_discounts = df['discount'].sum()

   metrics = {
       'total_revenue': df['revenue'].sum(), 'net_revenue': df['net_revenue'].sum(),
       'gross_profit': df['gross_profit'].sum(), 'net_profit': df['net_profit'].sum(),
       'total_orders': len(df), 'avg_order_value': df['net_revenue'].sum() / len(df) if len(df) > 0 else 0,
       'refund_rate': (df['refund_amount'].sum() / df['revenue'].sum() * 100) if df['revenue'].sum() > 0 else 0,
       'gross_margin': (df['gross_profit'].sum() / df['net_revenue'].sum() * 100) if df['net_revenue'].sum() > 0 else 0,
       'net_margin': (df['net_profit'].sum() / df['net_revenue'].sum() * 100) if df['net_revenue'].sum() > 0 else 0,
       'total_cogs': df['cogs'].sum(), 'total_fees': df['platform_fee'].sum(),
       'total_shipping': df['shipping_cost'].sum(), 'total_refunds': df['refund_amount'].sum(),
       'total_tax_owed': total_tax_owed, 'total_discounts': total_discounts
   }
   if df_prev is not None and len(df_prev) > 0:
       prev_metrics = {
           'total_revenue': df_prev['revenue'].sum(), 'net_profit': df_prev['net_profit'].sum(),
           'total_orders': len(df_prev), 'avg_order_value': df_prev['net_revenue'].sum() / len(df_prev) if len(df_prev) > 0 else 0,
       }
       for key in ['total_revenue', 'net_profit', 'total_orders', 'avg_order_value']:
           metrics[f'{key}_delta'] = ((metrics[key] - prev_metrics[key]) / prev_metrics[key] * 100) if prev_metrics[key] > 0 else 0
   return metrics


def apply_chart_theme(fig, height=300):
   fig.update_layout(
       template='plotly_dark', paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)',
       font=dict(family="Inter, sans-serif", color="#9CA3AF", size=12),
       margin=dict(l=0, r=0, t=30, b=0),
       xaxis=dict(showgrid=False, showline=True, linecolor="#374151", automargin=True),
       yaxis=dict(showgrid=True, gridcolor="#374151", showline=False, automargin=True),
       height=height,
       legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1, bgcolor="rgba(0,0,0,0)"),
       hovermode='x unified',
       hoverlabel=dict(bgcolor="#1F2937", font_size=13, font_family="Inter, sans-serif", bordercolor="#2DD4BF")
   )
   return fig


# --- SVG GENERATORS ---
def get_top_kpi_circle(percentage, label, color_hex="#2DD4BF"):
   radius = 15.9155
   circumference = radius * 2 * 3.14159
   offset = circumference - (percentage / 100) * circumference
  
   # Format percentage to 2 decimals
   return f"""
   <div style="width: 110px; height: 110px; text-align: center;">
       <svg viewBox="0 0 36 36" class="circular-chart">
           <path class="circle-bg" d="M18 2.0845 a 15.9155 15.9155 0 0 1 0 31.831 a 15.9155 15.9155 0 0 1 0 -31.831" />
           <path class="circle-fill" stroke="{color_hex}" stroke-dasharray="{circumference}, {circumference}" stroke-dashoffset="{offset}" d="M18 2.0845 a 15.9155 15.9155 0 0 1 0 31.831 a 15.9155 15.9155 0 0 1 0 -31.831" />
           <text x="18" y="19" class="text-percent" style="opacity: 1; font-size: 7px;">{percentage:.2f}%</text>
           <text x="18" y="24" class="text-label" style="font-size: 3px;">{label}</text>
       </svg>
   </div>
   """


def get_cost_circle(percentage, value_text, label_text, color_hex="#2DD4BF"):
   radius = 15.9155
   circumference = radius * 2 * 3.14159
   offset = circumference - (percentage / 100) * circumference
  
   # Format percentage to 2 decimals
   return f"""
   <div class="cost-circle-wrapper" style="width: 120px; text-align: center;">
       <svg viewBox="0 0 36 36" class="circular-chart">
           <path class="circle-bg" d="M18 2.0845 a 15.9155 15.9155 0 0 1 0 31.831 a 15.9155 15.9155 0 0 1 0 -31.831" />
           <path class="circle-fill" stroke="{color_hex}" stroke-dasharray="{circumference}, {circumference}" stroke-dashoffset="{offset}" d="M18 2.0845 a 15.9155 15.9155 0 0 1 0 31.831 a 15.9155 15.9155 0 0 1 0 -31.831" />
          
           <text x="18" y="17" class="text-value">{value_text}</text>
           <text x="18" y="23" class="text-label">{label_text}</text>
          
           <text x="18" y="20.5" class="text-percent">{percentage:.2f}%</text>
       </svg>
   </div>
   """


# --- CHART FUNCTIONS ---
def chart_revenue_trend(df):
   daily = df.groupby(['date', 'channel'])['revenue'].sum().reset_index()
   daily['revenue_smooth'] = daily.groupby('channel')['revenue'].transform(lambda x: x.rolling(7, min_periods=1).mean())
   fig = px.line(daily, x='date', y='revenue_smooth', color='channel',
                 color_discrete_map={'Shopify': '#2DD4BF', 'Walmart': '#818CF8', 'Amazon': '#FF9900'},
                 labels={'revenue_smooth': 'Revenue', 'date': 'Date'})
   # Rounded to 2 decimals
   fig.update_traces(line=dict(width=3), hovertemplate='<b>%{x|%b %d}</b><br>Revenue: $%{y:,.2f}<extra></extra>')
   return apply_chart_theme(fig, height=350)


def chart_channel_bar(df):
   totals = df.groupby('channel').agg({'revenue': 'sum'}).reset_index()
   fig = px.bar(totals, x='channel', y='revenue', color='channel',
                color_discrete_map={'Shopify': '#2DD4BF', 'Walmart': '#818CF8', 'Amazon': '#FF9900'},
                text='revenue')
   # Rounded to 2 decimals
   fig.update_traces(texttemplate='$%{text:,.2f}', textposition="outside", hovertemplate='%{x}<br>$%{y:,.2f}<extra></extra>')
   fig.update_layout(showlegend=False, yaxis=dict(showticklabels=False))
   return apply_chart_theme(fig, height=350)


def chart_heatmap(df):
   state_counts = df['state'].value_counts().reset_index()
   state_counts.columns = ['state', 'orders']
   fig = px.choropleth(state_counts, locations='state', locationmode="USA-states", color='orders',
                       scope="usa", color_continuous_scale=[[0, '#111827'], [1, '#2DD4BF']])
   fig.update_traces(hovertemplate='<b>%{location}</b><br>Orders: %{z:,}<extra></extra>')
   fig.update_layout(geo=dict(bgcolor='rgba(0,0,0,0)', lakecolor='rgba(0,0,0,0)', landcolor='#1F2937', subunitcolor='#374151'),
                     margin=dict(l=0, r=0, t=0, b=0), height=350, paper_bgcolor='rgba(0,0,0,0)')
   return fig


def chart_profit_donut(df):
   totals = df.groupby('channel')['gross_profit'].sum().reset_index()
   fig = px.pie(totals, values='gross_profit', names='channel',
                color='channel', color_discrete_map={'Shopify': '#2DD4BF', 'Walmart': '#818CF8', 'Amazon': '#FF9900'}, hole=0.6)
   # Rounded to 2 decimals
   fig.update_traces(textinfo='percent+label', textposition='outside', hovertemplate='<b>%{label}</b><br>$%{value:,.2f}<extra></extra>')
   fig.update_layout(showlegend=False, margin=dict(t=20, b=20, l=20, r=20))
   return apply_chart_theme(fig, height=350)


def chart_profit_margin_trend(df):
   daily = df.groupby('date').agg({'revenue': 'sum', 'gross_profit': 'sum', 'net_profit': 'sum'}).reset_index()
   daily['gross_margin'] = (daily['gross_profit'] / daily['revenue'] * 100).rolling(7).mean()
   daily['net_margin'] = (daily['net_profit'] / daily['revenue'] * 100).rolling(7).mean()
   fig = go.Figure()
   fig.add_trace(go.Scatter(x=daily['date'], y=daily['gross_margin'], name='Gross Margin',
                            line=dict(color='#2DD4BF', width=3), fill='tozeroy', fillcolor='rgba(45, 212, 191, 0.1)',
                            hovertemplate='Gross Margin: %{y:.2f}%<extra></extra>')) # 2 decimals
   fig.add_trace(go.Scatter(x=daily['date'], y=daily['net_margin'], name='Net Margin',
                            line=dict(color='#818CF8', width=3, dash='dash'),
                            hovertemplate='Net Margin: %{y:.2f}%<extra></extra>')) # 2 decimals
   fig.update_yaxes(ticksuffix='%')
   return apply_chart_theme(fig, height=350)


def chart_waterfall_profit(df):
   vals = [df['revenue'].sum(), -df['refund_amount'].sum(), -df['cogs'].sum(), -df['shipping_cost'].sum(), -df['platform_fee'].sum(), df['net_profit'].sum()]
   fig = go.Figure(go.Waterfall(
       name="Profit", orientation="v",
       measure=["relative", "relative", "relative", "relative", "relative", "total"],
       x=["Revenue", "Refunds", "COGS", "Shipping", "Fees", "Net Profit"],
       y=vals,
       connector={"line": {"color": "#2DD4BF"}},
       increasing={"marker": {"color": "#2DD4BF"}},
       decreasing={"marker": {"color": "#F87171"}},
       totals={"marker": {"color": "#818CF8"}},
       hovertemplate='<b>%{x}</b><br>$%{y:,.2f}<extra></extra>' # 2 decimals
   ))
   return apply_chart_theme(fig, height=350)


def chart_product_kpi(df):
   prod_perf = df.groupby('products').agg({'revenue': 'sum'}).sort_values('revenue', ascending=True).reset_index()
   fig = px.bar(prod_perf, y='products', x='revenue', orientation='h',
                text='revenue', color='revenue', color_continuous_scale="Tealgrn")
   # Rounded to 2 decimals
   fig.update_traces(texttemplate='$%{text:,.2f}', textposition="outside", hovertemplate='$%{x:,.2f}<extra></extra>')
   fig.update_layout(showlegend=False, xaxis_title="Revenue", yaxis_title="")
   return apply_chart_theme(fig, height=400)


# --- GROWTH CHARTS ---
def chart_growth_velocity(df):
   # Resample to Month
   df_monthly = df.set_index('date').resample('M').agg({'revenue': 'sum'}).reset_index()
   df_monthly['prev_revenue'] = df_monthly['revenue'].shift(1)
   df_monthly['growth_rate'] = ((df_monthly['revenue'] - df_monthly['prev_revenue']) / df_monthly['prev_revenue']) * 100
   df_monthly = df_monthly.dropna()


   fig = go.Figure()
   # Bar for Absolute Revenue
   fig.add_trace(go.Bar(
       x=df_monthly['date'], y=df_monthly['revenue'], name='Monthly Revenue',
       marker_color='rgba(45, 212, 191, 0.4)', marker_line_color='#2DD4BF', marker_line_width=1,
       hovertemplate='Rev: $%{y:,.2f}<extra></extra>'
   ))
   # Line for Growth Rate
   fig.add_trace(go.Scatter(
       x=df_monthly['date'], y=df_monthly['growth_rate'], name='Growth Rate (%)',
       yaxis='y2', line=dict(color='#818CF8', width=3), mode='lines+markers',
       hovertemplate='Growth: %{y:.2f}%<extra></extra>'
   ))
  
   fig.update_layout(
       yaxis2=dict(title='Growth %', overlaying='y', side='right', showgrid=False, zeroline=False, ticksuffix='%'),
       yaxis=dict(title='Revenue ($)', showgrid=True),
       hovermode='x unified',
       legend=dict(orientation="h", y=1.1)
   )
   return apply_chart_theme(fig, height=350)


def chart_net_profit_trend(df):
   df_monthly = df.set_index('date').resample('M').agg({'net_profit': 'sum', 'revenue': 'sum'}).reset_index()
   df_monthly['net_margin'] = (df_monthly['net_profit'] / df_monthly['revenue']) * 100
  
   fig = go.Figure()
   fig.add_trace(go.Scatter(
       x=df_monthly['date'], y=df_monthly['net_profit'], name='Net Profit ($)',
       fill='tozeroy', line=dict(color='#34D399', width=3),
       hovertemplate='$%{y:,.2f}<extra></extra>'
   ))
   return apply_chart_theme(fig, height=350)




# --- MAIN LAYOUT ---
def main():
   # Check password first
   if not check_password():
       st.stop()  # Stop execution if password is incorrect

   # Clear Streamlit cache on first load to ensure fresh data from Supabase
   if 'cache_cleared' not in st.session_state:
       st.cache_data.clear()
       st.session_state.cache_cleared = True

   # Data Processing with professional loading screen
   # Load data from Supabase if available, otherwise use sample data
   if 'data_loaded' not in st.session_state:
       # Show ONLY loading screen - no other UI elements
       load_css()
       st.markdown("""
           <style>
           .loading-container {
               position: fixed;
               top: 0;
               left: 0;
               width: 100vw;
               height: 100vh;
               display: flex;
               flex-direction: column;
               align-items: center;
               justify-content: center;
               background: #0E1117;
               z-index: 9999;
           }
           .loading-spinner {
               border: 4px solid rgba(45, 212, 191, 0.1);
               border-top: 4px solid #2DD4BF;
               border-radius: 50%;
               width: 60px;
               height: 60px;
               animation: spin 1s linear infinite;
               margin-bottom: 20px;
           }
           @keyframes spin {
               0% { transform: rotate(0deg); }
               100% { transform: rotate(360deg); }
           }
           .loading-text {
               color: #9CA3AF;
               font-size: 1.2rem;
               margin-top: 10px;
           }
           </style>
           <div class="loading-container">
               <div class="loading-spinner"></div>
               <div class="loading-text">Loading dashboard data...</div>
           </div>
       """, unsafe_allow_html=True)

       if SUPABASE_AVAILABLE:
           df_full = fetch_all_order_data()
           if df_full is None or df_full.empty:
               df_full = generate_sample_data()
       else:
           df_full = generate_sample_data()

       st.session_state['data_loaded'] = True
       st.session_state['df_full'] = df_full
       st.rerun()

   # Once data is loaded, show the dashboard
   load_css()

   # Use cached data for seamless experience
   df_full = st.session_state.get('df_full')
   if df_full is None or df_full.empty:
       if SUPABASE_AVAILABLE:
           df_full = fetch_all_order_data()
           if df_full is None or df_full.empty:
               df_full = generate_sample_data()
       else:
           df_full = generate_sample_data()
       st.session_state['df_full'] = df_full

   # 1. Header: Title (Left) | Logo & Status (Right)
   col_head1, col_head2 = st.columns([2, 1])
   with col_head1:
       st.title("Dashboard")
   with col_head2:
       status_text = "● Live Data" if SUPABASE_AVAILABLE else "● Demo Mode"
       status_class = "status-live" if SUPABASE_AVAILABLE else "status-sample"
       st.markdown(f"""
       <div style="display: flex; justify-content: flex-end; align-items: center; margin-top: 10px;">
           <img src="{ZEOFILL_LOGO_URL}" style="height: 70px; margin-right: 15px;">
           <div class="status-pill {status_class}">{status_text}</div>
       </div>
       """, unsafe_allow_html=True)

   st.markdown('<div class="title-spacer"></div>', unsafe_allow_html=True)

   # Store unfiltered data for later use
   df_unfiltered = df_full.copy()

   # 2. Filters and Tabs Row - Centered between horizontal lines
   st.markdown('<div style="border-top: 1px solid rgba(255, 255, 255, 0.1); margin: 1.5rem 0 0 0;"></div>', unsafe_allow_html=True)

   filter_col1, filter_col2, filter_col3, filter_col4 = st.columns([5, 2, 2, 2])

   with filter_col1:
       # Tabs on the left side
       tab_selection = st.radio(
           "Navigation",
           ["Overview", "Profitability", "Products", "Growth", "Unfulfilled Orders"],
           horizontal=True,
           label_visibility="collapsed",
           key="tab_nav"
       )

   with filter_col2:
       date_preset = st.selectbox(
           "Date Range",
           ["All", "Last 7 Days", "Last 30 Days", "Last 90 Days", "Custom"],
           index=2,
           label_visibility="collapsed"
       )

   with filter_col3:
       channels = st.multiselect(
           "Channels",
           ['Shopify', 'Walmart', 'Amazon'],
           default=['Shopify', 'Walmart', 'Amazon'],
           label_visibility="collapsed",
           placeholder="Channel"
       )

   with filter_col4:
       order_search = st.text_input(
           "Search Order",
           placeholder="Order #...",
           label_visibility="collapsed",
           key="order_search"
       )

   st.markdown('<div style="border-bottom: 1px solid rgba(255, 255, 255, 0.1); margin: 0 0 1.5rem 0;"></div>', unsafe_allow_html=True)

   # Filter Logic applied to df for the Charts
   if date_preset == "All":
       df = df_full.copy()  # Use all data
   elif date_preset == "Last 7 Days":
       date_range = (datetime.now() - timedelta(days=7), datetime.now())
       start, end = pd.Timestamp(date_range[0]), pd.Timestamp(date_range[1])
       df = df_full[(df_full['date'] >= start) & (df_full['date'] <= end)]
   elif date_preset == "Last 30 Days":
       date_range = (datetime.now() - timedelta(days=30), datetime.now())
       start, end = pd.Timestamp(date_range[0]), pd.Timestamp(date_range[1])
       df = df_full[(df_full['date'] >= start) & (df_full['date'] <= end)]
   elif date_preset == "Last 90 Days":
       date_range = (datetime.now() - timedelta(days=90), datetime.now())
       start, end = pd.Timestamp(date_range[0]), pd.Timestamp(date_range[1])
       df = df_full[(df_full['date'] >= start) & (df_full['date'] <= end)]
   else:  # Custom
       date_range = (datetime.now() - timedelta(days=30), datetime.now())
       start, end = pd.Timestamp(date_range[0]), pd.Timestamp(date_range[1])
       df = df_full[(df_full['date'] >= start) & (df_full['date'] <= end)]

   if channels:
       df = df[df['channel'].isin(channels)]

   # Filter by order number if search term is provided
   if order_search and order_search.strip():
       search_term = order_search.strip()
       # Search in order_id column (which contains order numbers for all channels)
       df = df[df['order_id'].astype(str).str.contains(search_term, case=False, na=False)]

   # Recalculate metrics for the filtered view
   metrics_filtered = calculate_metrics(df)

   # Calculate KPI metrics for last 30 days with filtered data
   end_date = df['date'].max()
   start_date = end_date - timedelta(days=30)
   prev_start = start_date - timedelta(days=30)

   df_curr = df[(df['date'] >= start_date) & (df['date'] <= end_date)]
   df_prev = df[(df['date'] >= prev_start) & (df['date'] < start_date)]
   metrics = calculate_metrics(df_curr, df_prev)

   # Helper function for delta formatting
   def format_delta_html(delta: float):
       css_class = "delta-pos" if delta >= 0 else "delta-neg"
       sign = "+" if delta >= 0 else ""
       return f'<div class="metric-delta {css_class}">{sign}{delta:.2f}% vs prev</div>'

   # 3. Top KPI Cards (Now dynamic with filters)
   kpi_height = 200
   k1, k2, k3 = st.columns(3)

   with k1:
       html_k1 = f"""{KPI_CSS}
       <div class="metric-card-combined">
           <div class="metric-main-content">
               <div class="metric-label">TOTAL REVENUE</div>
               <div class="metric-value">${metrics['total_revenue']:,.2f}</div>
               {format_delta_html(metrics.get('total_revenue_delta', 0))}
               <div class="metric-sub-label">Net: ${metrics['net_revenue']/1000:,.2f}K</div>
           </div>
           {get_top_kpi_circle(metrics['refund_rate'], "Refund Rate", "#2DD4BF")}
       </div>"""
       components.html(html_k1, height=kpi_height)

   with k2:
       margin_pct = metrics['net_margin']
       html_k2 = f"""{KPI_CSS}
       <div class="metric-card-combined">
           <div class="metric-main-content">
               <div class="metric-label">NET PROFIT</div>
               <div class="metric-value">${metrics['net_profit']:,.2f}</div>
               {format_delta_html(metrics.get('net_profit_delta', 0))}
               <div class="metric-sub-label">Gross: ${metrics['gross_profit']/1000:,.2f}K</div>
           </div>
           {get_top_kpi_circle(margin_pct, "Net Margin", "#818CF8")}
       </div>"""
       components.html(html_k2, height=kpi_height)

   with k3:
       aov_target = min((metrics['avg_order_value'] / 250) * 100, 100)
       html_k3 = f"""{KPI_CSS}
       <div class="metric-card-combined">
           <div class="metric-main-content">
               <div class="metric-label">TOTAL ORDERS</div>
               <div class="metric-value">{metrics['total_orders']:,}</div>
               {format_delta_html(metrics.get('total_orders_delta', 0))}
               <div class="metric-sub-label">Avg: ${metrics['avg_order_value']:.2f}</div>
           </div>
           {get_top_kpi_circle(aov_target, "AOV Goal", "#34D399")}
       </div>"""
       components.html(html_k3, height=kpi_height)

   st.markdown("---")

   # 4. Content based on tab selection (using if/elif instead of st.tabs)
   # We'll define tab variables for backward compatibility
   tab_overview = tab_selection == "Overview"
   tab_profit = tab_selection == "Profitability"
   tab_products = tab_selection == "Products"
   tab_growth = tab_selection == "Growth"
   tab_unfulfilled = tab_selection == "Unfulfilled Orders"


   # --- OVERVIEW TAB ---
   if tab_overview:
       r1_c1, r1_c2 = st.columns([2, 1])
       with r1_c1:
           st.markdown('<div class="chart-container"><div class="chart-header">Revenue Trend</div></div>', unsafe_allow_html=True)
           st.plotly_chart(chart_revenue_trend(df), use_container_width=True, config={'displayModeBar': False})
       with r1_c2:
           st.markdown('<div class="chart-container"><div class="chart-header">Orders by State</div></div>', unsafe_allow_html=True)
           st.plotly_chart(chart_heatmap(df), use_container_width=True, config={'displayModeBar': False})
          
       r2_c1, r2_c2 = st.columns([2, 1.2])
       with r2_c1:
           st.markdown('<div class="chart-container"><div class="chart-header">Channel Revenue Split</div></div>', unsafe_allow_html=True)
           st.plotly_chart(chart_channel_bar(df), use_container_width=True, config={'displayModeBar': False})
       with r2_c2:
           rev = metrics_filtered['total_revenue'] if metrics_filtered['total_revenue'] > 0 else 1
           pct_cogs = (metrics_filtered['total_cogs'] / rev) * 100
           pct_fees = (metrics_filtered['total_fees'] / rev) * 100
           pct_tax = (metrics_filtered['total_tax_owed'] / rev) * 100
           pct_ship = (metrics_filtered['total_shipping'] / rev) * 100
           pct_refund = (metrics_filtered['total_refunds'] / rev) * 100
           pct_discount = (metrics_filtered['total_discounts'] / rev) * 100

           # Formatted to 2 decimals
           cost_html = f"""{KPI_CSS}
           <div class="cost-panel-container">
               <div class="cost-header">Cost Breakdown</div>
               <div class="kpi-row">
                   {get_cost_circle(pct_cogs, f"${metrics_filtered['total_cogs']/1000:.2f}K", "COGS", "#2DD4BF")}
                   {get_cost_circle(pct_fees, f"${metrics_filtered['total_fees']/1000:.2f}K", "Fees", "#2DD4BF")}
                   {get_cost_circle(pct_tax, f"${metrics_filtered['total_tax_owed']/1000:.2f}K", "Tax Owed", "#2DD4BF")}
               </div>
               <div class="cost-header">Data Summary</div>
               <div class="kpi-row">
                   {get_cost_circle(pct_ship, f"${metrics_filtered['total_shipping']/1000:.2f}K", "Shipping", "#2DD4BF")}
                   {get_cost_circle(pct_refund, f"${metrics_filtered['total_refunds']/1000:.2f}K", "Refunds", "#2DD4BF")}
                   {get_cost_circle(pct_discount, f"${metrics_filtered['total_discounts']/1000:.2f}K", "Discounts", "#2DD4BF")}
               </div>
           </div>"""
           components.html(cost_html, height=440)

       # Export Data Button
       st.markdown("<br>", unsafe_allow_html=True)
       st.markdown("---")

       export_col1, export_col2, export_col3 = st.columns([1, 2, 1])
       with export_col2:
           st.markdown('<div style="text-align: center;">', unsafe_allow_html=True)

           if st.button("📥 Export Filtered Data", use_container_width=True, type="primary"):
               # Use the selected channels from the filter
               selected_channels = channels if channels else ["Shopify", "Walmart", "Amazon"]

               # Generate CSV for each selected channel
               export_files = {}
               for channel in selected_channels:
                   channel_df = df[df['channel'] == channel].copy()

                   if not channel_df.empty:
                       # Round financial columns to 2 decimal places
                       financial_columns = ['cogs', 'platform_fee', 'shipping_cost', 'gross_profit', 'net_profit', 'revenue', 'discount', 'tax', 'refund']
                       for col in financial_columns:
                           if col in channel_df.columns:
                               channel_df[col] = channel_df[col].round(2)

                       # Convert to CSV
                       csv_data = channel_df.to_csv(index=False)
                       export_files[channel] = csv_data

               # Create download buttons for each file
               if export_files:
                   st.success(f"✅ Generated {len(export_files)} file(s)")

                   # Create columns for download buttons
                   if len(export_files) == 1:
                       # Single file - centered button
                       download_cols = st.columns([1, 2, 1])
                       col_index = 1
                       for channel, csv_data in export_files.items():
                           with download_cols[col_index]:
                               date_suffix = datetime.now().strftime("%Y%m%d")
                               filename = f"{channel}_orders_{date_preset.lower().replace(' ', '_')}_{date_suffix}.csv"
                               st.download_button(
                                   label=f"⬇️ Download {channel} Data",
                                   data=csv_data,
                                   file_name=filename,
                                   mime="text/csv",
                                   use_container_width=True
                               )
                   else:
                       # Multiple files - multiple buttons
                       for channel, csv_data in export_files.items():
                           date_suffix = datetime.now().strftime("%Y%m%d")
                           filename = f"{channel}_orders_{date_preset.lower().replace(' ', '_')}_{date_suffix}.csv"
                           st.download_button(
                               label=f"⬇️ Download {channel} Data",
                               data=csv_data,
                               file_name=filename,
                               mime="text/csv",
                               use_container_width=True
                           )
               else:
                   st.warning("⚠️ No data available for selected filters")

           st.markdown('</div>', unsafe_allow_html=True)


   # --- PROFITABILITY TAB ---
   if tab_profit:
       pc1, pc2 = st.columns(2)
       with pc1:
           st.markdown('<div class="chart-container"><div class="chart-header">Profit Distribution</div></div>', unsafe_allow_html=True)
           st.plotly_chart(chart_profit_donut(df), use_container_width=True)
       with pc2:
           st.markdown('<div class="chart-container"><div class="chart-header">Margin Trends</div></div>', unsafe_allow_html=True)
           st.plotly_chart(chart_profit_margin_trend(df), use_container_width=True)
       st.markdown('<div class="chart-container"><div class="chart-header">Profit Waterfall</div></div>', unsafe_allow_html=True)
       st.plotly_chart(chart_waterfall_profit(df), use_container_width=True)


   # --- PRODUCTS TAB ---
   if tab_products:
       pr1, pr2 = st.columns([2, 1])
       with pr1:
           st.markdown('<div class="chart-container"><div class="chart-header">Top Products by Revenue</div></div>', unsafe_allow_html=True)
           st.plotly_chart(chart_product_kpi(df), use_container_width=True)
       with pr2:
           st.markdown('<div class="chart-container"><div class="chart-header">Product Details</div></div>', unsafe_allow_html=True)
           prod_table = df.groupby('products').agg({'revenue': 'sum', 'date': 'count'}).rename(columns={'revenue': 'Sales', 'date': 'Orders'}).sort_values('Sales', ascending=False)
           # Format table to 2 decimals
           st.dataframe(prod_table.style.format({'Sales': '${:,.2f}'}), use_container_width=True)


   # --- GROWTH TAB (REVISED FOR CEO) ---
   if tab_growth:
       # Calculate Monthly Growth Data for cards
       df_monthly = df_full.set_index('date').resample('M').agg({'revenue': 'sum', 'net_profit': 'sum'}).reset_index()
       current_month = df_monthly.iloc[-1]
       prev_month = df_monthly.iloc[-2]

       # MoM calculations
       mom_rev_growth = ((current_month['revenue'] - prev_month['revenue']) / prev_month['revenue']) * 100
       mom_profit_growth = ((current_month['net_profit'] - prev_month['net_profit']) / prev_month['net_profit']) * 100

       # YoY calculations (Year over Year)
       df_yearly = df_full.set_index('date').resample('Y').agg({'revenue': 'sum', 'net_profit': 'sum'}).reset_index()
       if len(df_yearly) >= 2:
           current_year = df_yearly.iloc[-1]
           prev_year = df_yearly.iloc[-2]
           yoy_rev_growth = ((current_year['revenue'] - prev_year['revenue']) / prev_year['revenue']) * 100
           yoy_profit_growth = ((current_year['net_profit'] - prev_year['net_profit']) / prev_year['net_profit']) * 100
       else:
           # Not enough data for YoY, use annualized estimate
           yoy_rev_growth = mom_rev_growth * 12  # Rough estimate
           yoy_profit_growth = mom_profit_growth * 12

       # Color Logic
       rev_class = "g-pos" if mom_rev_growth >= 0 else "g-neg"
       prof_class = "g-pos" if mom_profit_growth >= 0 else "g-neg"
       yoy_rev_class = "g-pos" if yoy_rev_growth >= 0 else "g-neg"
       yoy_prof_class = "g-pos" if yoy_profit_growth >= 0 else "g-neg"

       g1, g2, g3, g4, g5 = st.columns(5)
       with g1:
           # MoM Revenue Card
           html_g1 = f"""{KPI_CSS}
           <div class="growth-kpi-container">
               <div class="growth-title">MoM Revenue Growth</div>
               <div class="growth-value">{mom_rev_growth:+.2f}%</div>
               <div class="growth-delta {rev_class}">Current: ${current_month['revenue']:,.2f}</div>
           </div>
           """
           components.html(html_g1, height=130)
       with g2:
           # MoM Profit Card
           html_g2 = f"""{KPI_CSS}
           <div class="growth-kpi-container">
               <div class="growth-title">MoM Net Profit Growth</div>
               <div class="growth-value">{mom_profit_growth:+.2f}%</div>
               <div class="growth-delta {prof_class}">Current: ${current_month['net_profit']:,.2f}</div>
           </div>
           """
           components.html(html_g2, height=130)
       with g3:
           # YoY Revenue Growth Card
           html_g3 = f"""{KPI_CSS}
           <div class="growth-kpi-container">
               <div class="growth-title">YoY Revenue Growth</div>
               <div class="growth-value">{yoy_rev_growth:+.2f}%</div>
               <div class="growth-delta {yoy_rev_class}">Year over Year</div>
           </div>
           """
           components.html(html_g3, height=130)
       with g4:
           # YoY Net Profit Growth Card
           html_g4 = f"""{KPI_CSS}
           <div class="growth-kpi-container">
               <div class="growth-title">YoY Net Profit Growth</div>
               <div class="growth-value">{yoy_profit_growth:+.2f}%</div>
               <div class="growth-delta {yoy_prof_class}">Year over Year</div>
           </div>
           """
           components.html(html_g4, height=130)
       with g5:
           # Projected Annual
           projected = current_month['revenue'] * 12
           html_g5 = f"""{KPI_CSS}
           <div class="growth-kpi-container">
               <div class="growth-title">Annual Run Rate (Proj.)</div>
               <div class="growth-value">${projected/1000:,.0f}K</div>
               <div style="color: #9CA3AF; font-size: 0.8rem; margin-top:5px;">Based on current month performance</div>
           </div>
           """
           components.html(html_g5, height=130)


       # Growth Charts
       gc1, gc2 = st.columns(2)
       with gc1:
           st.markdown('<div class="chart-container"><div class="chart-header">Revenue Velocity (Rev vs Growth %)</div></div>', unsafe_allow_html=True)
           # We use df_full here to show the long term trend regardless of short filters
           st.plotly_chart(chart_growth_velocity(df_full), use_container_width=True)
          
       with gc2:
           st.markdown('<div class="chart-container"><div class="chart-header">Profitability Trajectory (Net Profit)</div></div>', unsafe_allow_html=True)
           st.plotly_chart(chart_net_profit_trend(df_full), use_container_width=True)


   # --- UNFULFILLED ORDERS TAB ---
   if tab_unfulfilled:
       # Filter unfulfilled orders based on channel-specific criteria
       df_shopify = df_full[df_full['channel'] == 'Shopify']
       df_walmart = df_full[df_full['channel'] == 'Walmart']
       df_amazon = df_full[df_full['channel'] == 'Amazon']

       # Shopify: shipping_terms not null AND financial_status='paid' AND fulfillment_status='unfulfilled'
       shopify_unfulfilled = df_shopify[
           (df_shopify['shipping_terms'].notna()) &
           (df_shopify['shipping_terms'] != 'None') &
           (df_shopify['financial_status'] == 'paid') &
           (df_shopify['fulfillment_status'] == 'unfulfilled')
       ]

       # Amazon: order_status='Pending'
       amazon_unfulfilled = df_amazon[df_amazon['order_status'] == 'Pending']

       # Walmart: fulfillment_status NOT IN ('Delivered', 'Shipped', 'Cancelled')
       walmart_unfulfilled = df_walmart[
           ~df_walmart['fulfillment_status'].isin(['Delivered', 'Shipped', 'Cancelled'])
       ]

       # Combine all unfulfilled orders
       df_unfulfilled = pd.concat([shopify_unfulfilled, amazon_unfulfilled, walmart_unfulfilled], ignore_index=True)

       # Summary metrics
       st.markdown('<div class="chart-container"><div class="chart-header">Unfulfilled Orders Summary</div></div>', unsafe_allow_html=True)

       uf1, uf2, uf3, uf4 = st.columns(4)
       with uf1:
           total_unfulfilled = len(df_unfulfilled)
           st.metric("Total Unfulfilled Orders", f"{total_unfulfilled:,}")
       with uf2:
           total_value = df_unfulfilled['revenue'].sum()
           st.metric("Total Value", f"${total_value:,.2f}")
       with uf3:
           avg_value = df_unfulfilled['revenue'].mean() if total_unfulfilled > 0 else 0
           st.metric("Average Order Value", f"${avg_value:.2f}")
       with uf4:
           oldest_order = df_unfulfilled['date'].min() if total_unfulfilled > 0 else datetime.now()
           days_old = (datetime.now() - pd.to_datetime(oldest_order)).days if total_unfulfilled > 0 else 0
           st.metric("Oldest Order Age", f"{days_old} days")

       st.markdown("---")

       # Channel breakdown
       uf_c1, uf_c2 = st.columns(2)

       with uf_c1:
           st.markdown('<div class="chart-container"><div class="chart-header">Unfulfilled Orders by Channel</div></div>', unsafe_allow_html=True)
           if total_unfulfilled > 0:
               channel_counts = df_unfulfilled.groupby('channel').agg({
                   'revenue': 'sum',
                   'order_id': 'count'
               }).rename(columns={'order_id': 'count'}).reset_index()

               fig = px.bar(channel_counts, x='channel', y='count', color='channel',
                           color_discrete_map={'Shopify': '#2DD4BF', 'Walmart': '#818CF8', 'Amazon': '#FF9900'},
                           text='count')
               fig.update_traces(textposition="outside", hovertemplate='%{x}<br>Orders: %{y}<extra></extra>')
               fig.update_layout(showlegend=False)
               st.plotly_chart(apply_chart_theme(fig, height=300), use_container_width=True)
           else:
               st.info("✅ No unfulfilled orders!")

       with uf_c2:
           st.markdown('<div class="chart-container"><div class="chart-header">Unfulfilled Orders by State</div></div>', unsafe_allow_html=True)
           if total_unfulfilled > 0:
               state_counts = df_unfulfilled.groupby('state').size().sort_values(ascending=False).head(10).reset_index()
               state_counts.columns = ['state', 'count']

               fig = px.bar(state_counts, x='state', y='count', color='count',
                           color_continuous_scale="Tealgrn", text='count')
               fig.update_traces(textposition="outside", hovertemplate='%{x}<br>Orders: %{y}<extra></extra>')
               fig.update_layout(showlegend=False)
               st.plotly_chart(apply_chart_theme(fig, height=300), use_container_width=True)
           else:
               st.info("✅ No unfulfilled orders!")

       # Detailed table
       st.markdown('<div class="chart-container"><div class="chart-header">Unfulfilled Orders Details</div></div>', unsafe_allow_html=True)

       if total_unfulfilled > 0:
           # Prepare table data with new columns
           # Build column order: Date, Channel, Order ID, Customer Name, Address, City, Zip, State, Product, Value, Status
           desired_order = [
               'date', 'channel', 'order_id', 'customer_name',
               'shipping_address', 'shipping_city', 'shipping_zipcode', 'state',
               'products', 'revenue', 'financial_status'
           ]

           # Only include columns that exist in the dataframe
           available_columns = [col for col in desired_order if col in df_unfulfilled.columns]

           table_data = df_unfulfilled[available_columns].copy()
           table_data['date'] = table_data['date'].dt.strftime('%Y-%m-%d')
           table_data = table_data.sort_values('date', ascending=False)

           # Build rename dictionary based on available columns
           rename_dict = {
               'date': 'Order Date',
               'channel': 'Channel',
               'order_id': 'Order ID',
               'customer_name': 'Customer Name',
               'shipping_address': 'Shipping Address',
               'shipping_city': 'City',
               'shipping_zipcode': 'Zip Code',
               'state': 'State',
               'products': 'Product',
               'revenue': 'Value',
               'financial_status': 'Status'
           }

           # Only rename columns that exist in the dataframe
           rename_dict_filtered = {k: v for k, v in rename_dict.items() if k in table_data.columns}
           table_data = table_data.rename(columns=rename_dict_filtered)

           # Display with styling
           st.dataframe(
               table_data.style.format({'Value': '${:,.2f}'}),
               use_container_width=True,
               height=400
           )

           # Export button
           csv = table_data.to_csv(index=False)
           st.download_button(
               label="📥 Download Unfulfilled Orders CSV",
               data=csv,
               file_name=f"unfulfilled_orders_{datetime.now().strftime('%Y%m%d')}.csv",
               mime="text/csv"
           )
       else:
           st.success("🎉 All orders have been fulfilled!")


if __name__ == "__main__":
   main()

