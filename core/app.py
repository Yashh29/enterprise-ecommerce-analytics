# app.py
# ---------------------------------------------
# Enterprise E-Commerce Analytics Platform
# ---------------------------------------------

import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt

# ---------------------------------------------
# Page Configuration
# ---------------------------------------------
st.set_page_config(
    page_title="Enterprise E-Commerce Analytics Dashboard",
    layout="wide"
)

# ---------------------------------------------
# Data Loaders
# ---------------------------------------------
@st.cache_data
def load_dashboard_data():
    return pd.read_csv("core/data/processed/dashboard_data.csv")


@st.cache_data
def load_forecast_data():
    df = pd.read_csv("core/data/processed/segment_revenue_forecast.csv")
    df["order_month"] = pd.to_datetime(df["order_month"])
    return df


data = load_dashboard_data()
forecast_df = load_forecast_data()

# ---------------------------------------------
# Title
# ---------------------------------------------
st.title("📊 Enterprise E-Commerce Analytics Platform")
st.markdown("**Audience:** Executives • Marketing • Retention • Strategy Teams")

# ---------------------------------------------
# Tabs
# ---------------------------------------------
tab1, tab2, tab3, tab4, tab5 = st.tabs([
    "📌 Executive Overview",
    "🧩 Customer Segments",
    "⚠️ Churn Risk Analysis",
    "🎯 Action Recommendations",
    "📈 Segment Revenue Forecast"
])

# =================================================
# TAB 1 — EXECUTIVE OVERVIEW
# =================================================
with tab1:
    col1, col2, col3, col4 = st.columns(4)

    col1.metric("Total Customers", data["customer_id"].nunique())
    col2.metric("Churn Rate (%)", f"{data['actual_churn'].mean()*100:.2f}")
    col3.metric("High-Risk Customers (%)", f"{(data['risk_level']=='High Risk').mean()*100:.2f}")
    col4.metric("Average CLV", f"{data['clv_proxy'].mean():.2f}")

    st.divider()

    # Risk distribution
    fig, ax = plt.subplots()
    data["risk_level"].value_counts().plot.pie(
        autopct="%1.1f%%",
        startangle=90,
        ax=ax
    )
    ax.set_ylabel("")
    st.pyplot(fig)

    # CLV vs Churn
    st.subheader("Churn Probability vs Customer Value")
    fig, ax = plt.subplots()
    ax.scatter(data["clv_proxy"], data["churn_probability"], alpha=0.5)
    ax.set_xlabel("CLV")
    ax.set_ylabel("Churn Probability")
    ax.grid(True)
    st.pyplot(fig)

# =================================================
# TAB 2 — CUSTOMER SEGMENTS
# =================================================
with tab2:
    summary = data.groupby("segment").agg(
        customers=("customer_id", "count"),
        avg_clv=("clv_proxy", "mean"),
        churn_rate=("actual_churn", "mean")
    ).reset_index()

    st.dataframe(summary, use_container_width=True)

    # Customers per segment
    st.subheader("Customer Distribution by Segment")
    fig, ax = plt.subplots()
    summary.set_index("segment")["customers"].plot(kind="bar", ax=ax)
    ax.set_ylabel("Customers")
    ax.grid(axis="y")
    st.pyplot(fig)

    # CLV per segment
    st.subheader("Average CLV per Segment")
    fig, ax = plt.subplots()
    summary.set_index("segment")["avg_clv"].plot(kind="bar", ax=ax)
    ax.set_ylabel("Average CLV")
    ax.grid(axis="y")
    st.pyplot(fig)

# =================================================
# TAB 3 — CHURN RISK ANALYSIS
# =================================================
with tab3:
    risk_filter = st.selectbox(
        "Filter by Risk Level",
        ["All", "High Risk", "Medium Risk", "Low Risk"]
    )

    df = data if risk_filter == "All" else data[data["risk_level"] == risk_filter]

    st.dataframe(
        df[["customer_id", "segment", "clv_proxy", "churn_probability", "risk_level"]]
        .sort_values("churn_probability", ascending=False),
        use_container_width=True
    )

    st.subheader("Churn Probability Distribution")
    fig, ax = plt.subplots()
    ax.hist(df["churn_probability"], bins=20)
    ax.set_xlabel("Churn Probability")
    ax.set_ylabel("Customers")
    ax.grid(True)
    st.pyplot(fig)

# =================================================
# TAB 4 — ACTION RECOMMENDATIONS
# =================================================
with tab4:
    st.subheader("Retention Strategy Guide")

    st.markdown("""
    - **High Risk + High CLV** → Immediate retention offers  
    - **High Risk + Low CLV** → Automated campaigns  
    - **Medium Risk** → Reminder emails  
    - **Low Risk** → Normal engagement
    """)

    priority_customers = data[
        (data["risk_level"] == "High Risk") &
        (data["clv_proxy"] >= data["clv_proxy"].median())
    ]

    st.subheader("High Priority Customers")
    st.dataframe(
        priority_customers[
            ["customer_id", "segment", "clv_proxy", "churn_probability"]
        ].sort_values("churn_probability", ascending=False),
        use_container_width=True
    )

    fig, ax = plt.subplots()
    pd.Series({
        "High Risk + High CLV": len(priority_customers),
        "Other Customers": len(data) - len(priority_customers)
    }).plot(kind="pie", autopct="%1.1f%%", ax=ax)
    ax.set_ylabel("")
    st.pyplot(fig)

# =================================================
# TAB 5 — SEGMENT REVENUE FORECAST
# =================================================
with tab5:
    segments = st.multiselect(
        "Select Segment(s)",
        forecast_df["segment"].unique(),
        default=forecast_df["segment"].unique()
    )

    filtered_df = forecast_df[forecast_df["segment"].isin(segments)]

    fig, ax = plt.subplots(figsize=(12, 5))
    for seg in filtered_df["segment"].unique():
        seg_data = filtered_df[filtered_df["segment"] == seg]
        ax.plot(
            seg_data["order_month"],
            seg_data["forecast"],
            marker="o",
            label=f"Segment {seg}"
        )

    ax.set_xlabel("Month")
    ax.set_ylabel("Forecasted Revenue")
    ax.set_title("Segment Revenue Forecast")
    ax.legend()
    ax.grid(True)
    st.pyplot(fig)

    st.subheader("Total Forecasted Revenue by Segment")
    fig, ax = plt.subplots()
    forecast_df.groupby("segment")["forecast"].sum().plot(kind="bar", ax=ax)
    ax.set_ylabel("Revenue")
    ax.grid(axis="y")
    st.pyplot(fig)

# ---------------------------------------------
# Footer
# ---------------------------------------------
st.divider()
st.markdown(
    """
    <div style="text-align:center; color:gray; font-size:14px;">
        © 2025/26 — <b>Yash Modi</b> | Enterprise Data Science Project<br>
        Built with Python • Pandas • Scikit-learn • Streamlit
    </div>
    """,
    unsafe_allow_html=True
)
# End of app.py