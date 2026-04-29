import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
from scipy.stats import norm
from datetime import datetime, timedelta
import math

# ─── PAGE CONFIG ────────────────────────────────────────────────────────────────
st.set_page_config(
    page_title="Supply Chain Command Center",
    page_icon="🚚",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ─── CUSTOM CSS ─────────────────────────────────────────────────────────────────
st.markdown("""
<style>
    .metric-card {
        background: linear-gradient(135deg, #1e3a5f, #2d6a9f);
        border-radius: 12px; padding: 20px; color: white;
        box-shadow: 0 4px 15px rgba(0,0,0,0.2); margin-bottom: 10px;
    }
    .metric-value { font-size: 2.2rem; font-weight: bold; }
    .metric-label { font-size: 0.85rem; opacity: 0.85; }
    .risk-high   { color: #e74c3c; font-weight: bold; }
    .risk-medium { color: #f39c12; font-weight: bold; }
    .risk-low    { color: #27ae60; font-weight: bold; }
    .stTabs [data-baseweb="tab"] { font-size: 15px; font-weight: 600; }
    .insight-box {
        background: #f0f7ff; border-left: 4px solid #2d6a9f;
        padding: 12px 16px; border-radius: 6px; margin: 8px 0;
    }
</style>
""", unsafe_allow_html=True)

# ─── SIDEBAR ────────────────────────────────────────────────────────────────────
st.sidebar.image("https://img.icons8.com/fluency/96/supply-chain.png", width=80)
st.sidebar.title("⚙️ Control Panel")
module = st.sidebar.radio("📌 Select Module", [
    "🏠 Dashboard",
    "📈 Demand Forecasting",
    "📦 Inventory Optimizer",
    "🏭 Supplier Risk Scorer",
    "🔁 Reorder Point Calculator",
    "🌐 Network Cost Analyzer",
    "🎯 What-If Scenario Planner"
])
st.sidebar.markdown("---")
st.sidebar.info("💡 **Tip:** Upload your own CSV or use the built-in demo data in each module.")

# ═══════════════════════════════════════════════════════════════════════════════
# MODULE 0 — DASHBOARD
# ═══════════════════════════════════════════════════════════════════════════════
if module == "🏠 Dashboard":
    st.title("🚚 Supply Chain Command Center")
    st.caption("Your end-to-end operational intelligence hub")

    c1, c2, c3, c4 = st.columns(4)
    kpis = [
        ("📦 Inventory Turnover", "8.3x", "+0.4 vs last month"),
        ("⏱️ Avg Lead Time", "6.2 days", "-1.1 days improved"),
        ("🎯 Fill Rate", "97.4%", "▲ 2.1% vs target"),
        ("⚠️ At-Risk SKUs", "14", "🔴 Needs attention"),
    ]
    for col, (label, val, sub) in zip([c1,c2,c3,c4], kpis):
        col.markdown(f"""
        <div class="metric-card">
            <div class="metric-label">{label}</div>
            <div class="metric-value">{val}</div>
            <div style="font-size:0.8rem;opacity:0.7">{sub}</div>
        </div>""", unsafe_allow_html=True)

    st.markdown("---")
    col1, col2 = st.columns([2, 1])

    with col1:
        st.subheader("📊 Monthly Demand vs Inventory Trend")
        months = pd.date_range("2024-01-01", periods=12, freq="MS")
        demand  = [430,480,510,490,560,620,580,650,700,670,710,760]
        stock   = [520,510,490,530,540,580,560,600,620,650,680,720]
        fig = go.Figure()
        fig.add_trace(go.Scatter(x=months, y=demand, name="Demand", line=dict(color="#e74c3c", width=2.5)))
        fig.add_trace(go.Scatter(x=months, y=stock,  name="Inventory", line=dict(color="#2d6a9f", width=2.5)))
        fig.update_layout(height=320, margin=dict(l=0,r=0,t=10,b=0), legend=dict(orientation="h"))
        st.plotly_chart(fig, use_container_width=True)

    with col2:
        st.subheader("🌡️ Supply Health Score")
        categories = ["Demand Accuracy","Lead Time","Supplier","Fill Rate","Cost"]
        values     = [88, 75, 62, 97, 80]
        fig2 = go.Figure(go.Bar(
            x=values, y=categories, orientation='h',
            marker_color=["#27ae60","#f39c12","#e74c3c","#27ae60","#2d6a9f"]
        ))
        fig2.update_layout(height=320, margin=dict(l=0,r=0,t=10,b=0), xaxis_range=[0,100])
        st.plotly_chart(fig2, use_container_width=True)

    st.markdown("### 🔔 Active Alerts")
    alerts = [
        ("🔴 Critical", "SKU-0042 stock below safety level — reorder immediately"),
        ("🟡 Warning",  "Supplier TechParts Ltd: 3-day delay reported on PO #8821"),
        ("🟢 Info",     "Demand forecast accuracy improved to 91.4% this week"),
        ("🟡 Warning",  "Warehouse Zone C at 94% capacity — consider redistribution"),
    ]
    for tag, msg in alerts:
        st.markdown(f"**{tag}** — {msg}")

# ═══════════════════════════════════════════════════════════════════════════════
# MODULE 1 — DEMAND FORECASTING
# ═══════════════════════════════════════════════════════════════════════════════
elif module == "📈 Demand Forecasting":
    st.title("📈 Demand Forecasting Engine")
    st.caption("Multi-method forecasting: Moving Average · Exponential Smoothing · Trend Projection")

    with st.sidebar:
        st.markdown("### Forecast Settings")
        method    = st.selectbox("Method", ["Moving Average","Exponential Smoothing","Linear Trend"])
        periods   = st.slider("Forecast Horizon (months)", 1, 12, 6)
        alpha_val = st.slider("Alpha (ES only)", 0.1, 0.9, 0.3) if method == "Exponential Smoothing" else None
        ma_window = st.slider("Window (MA only)", 2, 6, 3)      if method == "Moving Average" else None

uploaded = st.file_uploader("📂 Upload demand CSV (columns: Month, Demand)", type="csv")
    if uploaded:
        df = pd.read_csv(uploaded)
        history = df["Demand"].tolist()
    labels  = df["Month"].tolist()

else:
    # fallback data if no file uploaded
    history = [320, 345, 380, 360, 410, 450, 420, 490, 510, 480, 530, 560]
    labels = [
        "Jan", "Feb", "Mar", "Apr", "May", "Jun",
        "Jul", "Aug", "Sep", "Oct", "Nov", "Dec"
    ]

    
    else:
        history = [320,345,380,360,410,450,420,490,510,480,530,560]
        labels  = [f"M{i+1}" for i in range(12)]
        st.info("Using built-in demo data. Upload your CSV to use real data.")

    def moving_average(data, window, n):
        forecasts = []
        series = list(data)
        for _ in range(n):
            f = np.mean(series[-window:])
            forecasts.append(round(f, 1))
            series.append(f)
        return forecasts

    def exp_smoothing(data, alpha, n):
        s = data[0]
        for d in data[1:]:
            s = alpha * d + (1 - alpha) * s
        forecasts = []
        for _ in range(n):
            s = alpha * s + (1 - alpha) * s
            forecasts.append(round(s, 1))
        return forecasts

    def linear_trend(data, n):
        x = np.arange(len(data))
        m, b = np.polyfit(x, data, 1)
        return [round(m * (len(data) + i) + b, 1) for i in range(n)]

    if method == "Moving Average":
        forecast = moving_average(history, ma_window, periods)
    elif method == "Exponential Smoothing":
        forecast = exp_smoothing(history, alpha_val, periods)
    else:
        forecast = linear_trend(history, periods)

    all_labels = labels + [f"F{i+1}" for i in range(periods)]
    all_values = history + forecast

    fig = go.Figure()
    fig.add_trace(go.Scatter(x=labels, y=history, name="Historical", line=dict(color="#2d6a9f", width=2.5)))
    fig.add_trace(go.Scatter(
        x=[labels[-1]] + [f"F{i+1}" for i in range(periods)],
        y=[history[-1]] + forecast,
        name="Forecast", line=dict(color="#e74c3c", width=2.5, dash="dot")
    ))
    fig.update_layout(height=380, title="Demand Forecast", legend=dict(orientation="h"))
    st.plotly_chart(fig, use_container_width=True)

    col1, col2 = st.columns(2)
    with col1:
        st.markdown("#### 📋 Forecast Values")
        fdf = pd.DataFrame({"Period": [f"F{i+1}" for i in range(periods)], "Forecasted Demand": forecast})
        st.dataframe(fdf, use_container_width=True)
    with col2:
        mae = np.mean(np.abs(np.diff(history)))
        st.metric("MAE (historical volatility)", f"{mae:.1f} units")
        st.metric("Avg Forecasted Demand", f"{np.mean(forecast):.0f} units/month")
        st.metric("Peak Forecast Month", f"F{np.argmax(forecast)+1} ({max(forecast)} units)")

# ═══════════════════════════════════════════════════════════════════════════════
# MODULE 2 — INVENTORY OPTIMIZER (EOQ)
# ═══════════════════════════════════════════════════════════════════════════════
elif module == "📦 Inventory Optimizer":
    st.title("📦 Inventory Optimizer (EOQ + Safety Stock)")

    col1, col2 = st.columns(2)
    with col1:
        st.subheader("📐 EOQ Calculator")
        annual_demand = st.number_input("Annual Demand (units)", value=5000, min_value=1)
        ordering_cost = st.number_input("Ordering Cost per Order ($)", value=150.0, min_value=0.1)
        holding_cost  = st.number_input("Holding Cost per Unit/Year ($)", value=8.0,  min_value=0.1)

        eoq = math.sqrt((2 * annual_demand * ordering_cost) / holding_cost)
        orders_per_year = annual_demand / eoq
        cycle_time_days = 365 / orders_per_year
        total_cost = (annual_demand / eoq) * ordering_cost + (eoq / 2) * holding_cost

        st.markdown("---")
        st.metric("🎯 Economic Order Quantity (EOQ)", f"{eoq:.0f} units")
        st.metric("📦 Orders Per Year", f"{orders_per_year:.1f}")
        st.metric("📅 Order Cycle", f"{cycle_time_days:.0f} days")
        st.metric("💰 Minimized Annual Inventory Cost", f"${total_cost:,.2f}")

    with col2:
        st.subheader("🛡️ Safety Stock Calculator")
        lead_time_avg  = st.number_input("Avg Lead Time (days)", value=7, min_value=1)
        lead_time_std  = st.number_input("Lead Time Std Dev (days)", value=2, min_value=0)
        demand_avg_day = st.number_input("Avg Daily Demand", value=15.0, min_value=0.1)
        demand_std_day = st.number_input("Daily Demand Std Dev", value=3.0, min_value=0.0)
        service_level  = st.slider("Target Service Level (%)", 80, 99, 95)

        z = norm.ppf(service_level / 100)
        safety_stock = z * math.sqrt(
            (lead_time_avg * demand_std_day**2) + (demand_avg_day**2 * lead_time_std**2)
        )
        rop = demand_avg_day * lead_time_avg + safety_stock

        st.markdown("---")
        st.metric("🛡️ Safety Stock", f"{safety_stock:.0f} units")
        st.metric("🔁 Reorder Point (ROP)", f"{rop:.0f} units")
        st.metric("📊 Z-Score", f"{z:.2f}")
        st.progress(service_level / 100)
        st.caption(f"Service Level: {service_level}%")

    # EOQ sensitivity chart
    st.markdown("---")
    st.subheader("📉 EOQ Cost Sensitivity")
    qty_range = np.linspace(50, eoq*3, 200)
    order_costs = (annual_demand / qty_range) * ordering_cost
    hold_costs  = (qty_range / 2) * holding_cost
    total_costs = order_costs + hold_costs
    fig = go.Figure()
    fig.add_trace(go.Scatter(x=qty_range, y=order_costs,  name="Ordering Cost",  line=dict(color="#e74c3c")))
    fig.add_trace(go.Scatter(x=qty_range, y=hold_costs,   name="Holding Cost",   line=dict(color="#2d6a9f")))
    fig.add_trace(go.Scatter(x=qty_range, y=total_costs,  name="Total Cost",     line=dict(color="#27ae60", width=3)))
    fig.add_vline(x=eoq, line_dash="dash", line_color="orange", annotation_text=f"EOQ={eoq:.0f}")
    fig.update_layout(height=340, xaxis_title="Order Quantity", yaxis_title="Annual Cost ($)")
    st.plotly_chart(fig, use_container_width=True)

# ═══════════════════════════════════════════════════════════════════════════════
# MODULE 3 — SUPPLIER RISK SCORER
# ═══════════════════════════════════════════════════════════════════════════════
elif module == "🏭 Supplier Risk Scorer":
    st.title("🏭 Supplier Risk Scoring Dashboard")

    default_suppliers = pd.DataFrame({
        "Supplier": ["AlphaTech", "BetaParts", "GammaSupply", "DeltaMfg", "EpsilonCo"],
        "On-Time Delivery (%)": [95, 72, 88, 65, 91],
        "Quality Rate (%)":     [98, 85, 92, 78, 96],
        "Financial Stability":  [9, 5, 7, 4, 8],  # 1-10
        "Lead Time (days)":     [5, 12, 8, 15, 6],
        "Single Source Risk":   [0, 1, 0, 1, 0],  # 1=yes, 0=no
    })

    st.markdown("### ✏️ Edit or Add Suppliers")
    df = st.data_editor(default_suppliers, num_rows="dynamic", use_container_width=True)

    if len(df) > 0:
        df = df.copy()
        # Normalize and score (0-100)
        df["Score_OTD"]    = df["On-Time Delivery (%)"]
        df["Score_Quality"]= df["Quality Rate (%)"]
        df["Score_Finance"]= df["Financial Stability"] * 10
        df["Score_LT"]     = (1 - (df["Lead Time (days)"] - df["Lead Time (days)"].min()) /
                               (df["Lead Time (days)"].max() - df["Lead Time (days)"].min() + 1)) * 100
        df["Score_SS"]     = (1 - df["Single Source Risk"]) * 100
        df["Risk Score"]   = (0.3*df["Score_OTD"] + 0.25*df["Score_Quality"] +
                              0.2*df["Score_Finance"] + 0.15*df["Score_LT"] + 0.1*df["Score_SS"]).round(1)

        def classify(score):
            if score >= 80: return "🟢 Low"
            if score >= 60: return "🟡 Medium"
            return "🔴 High"
        df["Risk Level"] = df["Risk Score"].apply(classify)

        col1, col2 = st.columns([2,1])
        with col1:
            fig = go.Figure(go.Bar(
                x=df["Supplier"], y=df["Risk Score"],
                marker_color=["#27ae60" if s>=80 else "#f39c12" if s>=60 else "#e74c3c"
                              for s in df["Risk Score"]],
                text=df["Risk Score"], textposition="outside"
            ))
            fig.add_hline(y=80, line_dash="dash", line_color="#27ae60", annotation_text="Low Risk Threshold")
            fig.add_hline(y=60, line_dash="dash", line_color="#f39c12", annotation_text="Medium Risk Threshold")
            fig.update_layout(title="Supplier Risk Scores (Higher = Better)", height=380, yaxis_range=[0,110])
            st.plotly_chart(fig, use_container_width=True)
        with col2:
            st.markdown("#### Risk Summary")
            st.dataframe(df[["Supplier","Risk Score","Risk Level"]], use_container_width=True)

        # Radar chart for top supplier
        best = df.loc[df["Risk Score"].idxmax(), "Supplier"]
        st.markdown(f"#### 🕸️ Capability Radar: **{best}** (Top Supplier)")
        top = df[df["Supplier"] == best].iloc[0]
        categories = ["OTD","Quality","Finance","Lead Time","Single Source"]
        vals = [top["Score_OTD"], top["Score_Quality"], top["Score_Finance"], top["Score_LT"], top["Score_SS"]]
        fig2 = go.Figure(go.Scatterpolar(r=vals+[vals[0]], theta=categories+[categories[0]],
                                          fill='toself', line_color="#2d6a9f"))
        fig2.update_layout(polar=dict(radialaxis=dict(range=[0,100])), height=350)
        st.plotly_chart(fig2, use_container_width=True)

# ═══════════════════════════════════════════════════════════════════════════════
# MODULE 4 — REORDER POINT CALCULATOR
# ═══════════════════════════════════════════════════════════════════════════════
elif module == "🔁 Reorder Point Calculator":
    st.title("🔁 Reorder Point (ROP) Planner")

    col1, col2 = st.columns(2)
    with col1:
        sku       = st.text_input("SKU / Product Name", "SKU-0042")
        avg_daily = st.number_input("Average Daily Usage (units)", value=50.0)
        lt_days   = st.number_input("Supplier Lead Time (days)", value=7)
        lt_std    = st.number_input("Lead Time Variability (std dev, days)", value=1.5)
        d_std     = st.number_input("Daily Demand Std Dev (units)", value=8.0)
        svc       = st.slider("Service Level Target (%)", 80, 99, 95)

    with col2:
        z         = norm.ppf(svc / 100)
        ss        = round(z * math.sqrt(lt_days * d_std**2 + avg_daily**2 * lt_std**2))
        rop       = round(avg_daily * lt_days + ss)
        max_stock = round(rop + (avg_daily * lt_days))

        st.markdown(f"### 📦 Results for `{sku}`")
        st.metric("Safety Stock",        f"{ss:,} units")
        st.metric("Reorder Point (ROP)", f"{rop:,} units")
        st.metric("Max Inventory Level", f"{max_stock:,} units")
        st.metric("Service Level",       f"{svc}%  (Z = {z:.2f})")

        st.markdown("""
        <div class="insight-box">
        📌 <b>Interpretation:</b> When inventory drops to <b>ROP</b>, place a new order. 
        Safety stock protects against demand spikes and lead-time variability.
        </div>""", unsafe_allow_html=True)

    # Stock simulation chart
    st.markdown("---")
    st.subheader("📉 Inventory Simulation (60 days)")
    np.random.seed(42)
    days       = 60
    inv        = max_stock
    inv_levels = []
    reorders   = []
    pending_lt = 0
    order_qty  = round(avg_daily * lt_days * 1.5)  # simple order qty

    for d in range(days):
        demand = max(0, round(np.random.normal(avg_daily, d_std)))
        inv -= demand
        if pending_lt > 0:
            pending_lt -= 1
            if pending_lt == 0:
                inv += order_qty
        if inv <= rop and pending_lt == 0:
            reorders.append(d)
            pending_lt = round(np.random.normal(lt_days, lt_std))
        inv_levels.append(max(inv, 0))

    fig = go.Figure()
    fig.add_trace(go.Scatter(x=list(range(days)), y=inv_levels, name="Inventory Level",
                             fill='tozeroy', line=dict(color="#2d6a9f")))
    fig.add_hline(y=rop, line_dash="dash", line_color="#e74c3c",  annotation_text=f"ROP={rop}")
    fig.add_hline(y=ss,  line_dash="dash", line_color="#f39c12", annotation_text=f"Safety Stock={ss}")
    for r in reorders:
        fig.add_vline(x=r, line_dash="dot", line_color="#27ae60", line_width=1)
    fig.update_layout(height=360, xaxis_title="Day", yaxis_title="Units in Stock",
                      legend=dict(orientation="h"))
    st.plotly_chart(fig, use_container_width=True)
    st.caption("🟢 Vertical lines = reorder triggered events")

# ═══════════════════════════════════════════════════════════════════════════════
# MODULE 5 — NETWORK COST ANALYZER
# ═══════════════════════════════════════════════════════════════════════════════
elif module == "🌐 Network Cost Analyzer":
    st.title("🌐 Supply Chain Network Cost Analyzer")

    st.markdown("Define your distribution lanes (Origin → Destination) and analyze costs.")

    default_network = pd.DataFrame({
        "Lane":           ["Plant A → DC1","Plant A → DC2","Plant B → DC1","Plant B → DC3","DC1 → Customer"],
        "Distance (km)":  [450, 800, 320, 610, 120],
        "Volume (units)": [5000, 3200, 4100, 2800, 8900],
        "Cost/Unit ($)":  [1.20, 1.85, 0.95, 1.50, 0.60],
        "Mode":           ["Truck","Rail","Truck","Air","Truck"],
    })
    df = st.data_editor(default_network, num_rows="dynamic", use_container_width=True)
    df["Total Lane Cost ($)"] = (df["Volume (units)"] * df["Cost/Unit ($)"]).round(2)

    col1, col2, col3 = st.columns(3)
    col1.metric("Total Network Cost", f"${df['Total Lane Cost ($)'].sum():,.2f}")
    col2.metric("Total Volume Moved", f"{df['Volume (units)'].sum():,} units")
    col3.metric("Avg Cost/Unit",       f"${df['Total Lane Cost ($)'].sum() / df['Volume (units)'].sum():.2f}")

    fig = px.bar(df, x="Lane", y="Total Lane Cost ($)", color="Mode",
                 title="Lane Cost Breakdown by Mode", height=360)
    st.plotly_chart(fig, use_container_width=True)

    fig2 = px.scatter(df, x="Distance (km)", y="Cost/Unit ($)", size="Volume (units)",
                      color="Mode", text="Lane", title="Cost Efficiency Map (bubble = volume)", height=360)
    st.plotly_chart(fig2, use_container_width=True)

    st.markdown("#### 💡 Optimization Insights")
    expensive = df.loc[df["Cost/Unit ($)"].idxmax()]
    st.markdown(f"""
    <div class="insight-box">
    🔴 <b>Highest cost lane:</b> {expensive['Lane']} at ${expensive['Cost/Unit ($)']:.2f}/unit. 
    Consider modal shift or renegotiating freight rates.
    </div>""", unsafe_allow_html=True)

# ═══════════════════════════════════════════════════════════════════════════════
# MODULE 6 — WHAT-IF SCENARIO PLANNER
# ═══════════════════════════════════════════════════════════════════════════════
elif module == "🎯 What-If Scenario Planner":
    st.title("🎯 What-If Scenario Planner")
    st.caption("Model the financial impact of supply chain disruptions and changes before they happen.")

    col1, col2 = st.columns(2)
    with col1:
        st.subheader("📊 Baseline Parameters")
        base_demand    = st.number_input("Monthly Demand (units)",      value=10000)
        base_price     = st.number_input("Selling Price/Unit ($)",      value=25.0)
        base_cogs      = st.number_input("COGS/Unit ($)",               value=12.0)
        base_inventory = st.number_input("Avg Inventory Value ($)",      value=150000.0)
        base_lead      = st.number_input("Lead Time (days)",             value=7)

    with col2:
        st.subheader("🎛️ Scenario Adjustments")
        demand_shock   = st.slider("Demand Change (%)",     -50, 50, 0)
        lead_spike     = st.slider("Lead Time Increase (%)", 0, 200, 0)
        cogs_increase  = st.slider("COGS Increase (%)",      0, 50, 0)
        holding_pct    = st.slider("Holding Cost (% of inv)", 5, 30, 20)
        stockout_units = st.number_input("Estimated Stockout Units", value=0)

    # Calculations
    new_demand   = base_demand * (1 + demand_shock/100)
    new_cogs     = base_cogs   * (1 + cogs_increase/100)
    new_lead     = base_lead   * (1 + lead_spike/100)
    new_holding  = base_inventory * holding_pct/100 / 12

    base_profit  = base_demand * (base_price - base_cogs)
    lost_sales   = stockout_units * base_price
    new_profit   = new_demand * (base_price - new_cogs) - lost_sales

    delta_profit = new_profit - base_profit

    st.markdown("---")
    st.subheader("📊 Impact Summary")
    c1,c2,c3,c4 = st.columns(4)
    c1.metric("Baseline Monthly Profit", f"${base_profit:,.0f}")
    c2.metric("Scenario Monthly Profit",  f"${new_profit:,.0f}", f"${delta_profit:+,.0f}")
    c3.metric("Monthly Holding Cost",     f"${new_holding:,.0f}")
    c4.metric("Lost Sales from Stockout", f"${lost_sales:,.0f}")

    # Waterfall chart
    items   = ["Base Profit","Demand Impact","COGS Impact","Stockout Loss","Net Profit"]
    demand_impact = (new_demand - base_demand) * (base_price - base_cogs)
    cogs_impact   = -new_demand * (new_cogs - base_cogs)
    values        = [base_profit, demand_impact, cogs_impact, -lost_sales, new_profit]
    colors        = ["#2d6a9f",
                     "#27ae60" if demand_impact >= 0 else "#e74c3c",
                     "#e74c3c" if cogs_impact < 0 else "#27ae60",
                     "#e74c3c","#2d6a9f"]
    fig = go.Figure(go.Bar(x=items, y=values, marker_color=colors,
                            text=[f"${v:,.0f}" for v in values], textposition="outside"))
    fig.update_layout(title="Profit Waterfall Analysis", height=380, yaxis_title="$ Impact")
    st.plotly_chart(fig, use_container_width=True)

    if delta_profit < 0:
        st.error(f"⚠️ This scenario reduces monthly profit by **${abs(delta_profit):,.0f}**. Consider mitigation strategies.")
    else:
        st.success(f"✅ This scenario improves monthly profit by **${delta_profit:,.0f}**.")
