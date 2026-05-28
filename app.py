# just a little bit of comment

import numpy as np
import pandas as pd
import plotly.express as px
import streamlit as st


st.set_page_config(
    page_title="Sales Performance Dashboard",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded",
)


@st.cache_data
def build_sample_data() -> dict[str, pd.DataFrame]:
    """Create three realistic in-code sales data sources."""
    rng = np.random.default_rng(42)

    months = pd.period_range("2025-01", "2025-12", freq="M").astype(str)
    regions = ["North America", "Europe", "Asia Pacific", "Latin America"]
    channels = ["Direct", "Partner", "Marketplace", "Retail"]
    products = ["Analytics Pro", "CRM Suite", "Support Hub", "Automation Kit"]

    order_rows = []
    for order_id in range(1, 361):
        units = int(rng.integers(1, 15))
        price = float(rng.choice([49, 79, 129, 199, 299]))
        discount = float(rng.choice([0, 0.05, 0.1, 0.15], p=[0.55, 0.2, 0.18, 0.07]))
        revenue = units * price * (1 - discount)
        order_rows.append(
            {
                "order_id": f"ORD-{order_id:04d}",
                "month": rng.choice(months),
                "region": rng.choice(regions, p=[0.34, 0.29, 0.25, 0.12]),
                "channel": rng.choice(channels, p=[0.38, 0.27, 0.22, 0.13]),
                "product": rng.choice(products),
                "units": units,
                "unit_price": price,
                "discount_pct": discount,
                "revenue": round(revenue, 2),
                "gross_margin": round(revenue * rng.uniform(0.42, 0.72), 2),
            }
        )

    pipeline_rows = []
    stages = ["Discovery", "Qualified", "Proposal", "Negotiation", "Closed Won", "Closed Lost"]
    stage_probability = {
        "Discovery": 0.15,
        "Qualified": 0.3,
        "Proposal": 0.52,
        "Negotiation": 0.72,
        "Closed Won": 1.0,
        "Closed Lost": 0.0,
    }
    segments = ["Enterprise", "Mid-Market", "SMB"]
    reps = ["Ava", "Milan", "Noah", "Sofia", "Theo", "Yara"]

    for opportunity_id in range(1, 151):
        stage = rng.choice(stages, p=[0.2, 0.22, 0.2, 0.16, 0.14, 0.08])
        value = float(rng.integers(8_000, 180_000))
        pipeline_rows.append(
            {
                "opportunity_id": f"OPP-{opportunity_id:04d}",
                "expected_close_month": rng.choice(months),
                "sales_rep": rng.choice(reps),
                "segment": rng.choice(segments, p=[0.25, 0.38, 0.37]),
                "stage": stage,
                "deal_value": round(value, 2),
                "probability": stage_probability[stage],
                "weighted_value": round(value * stage_probability[stage], 2),
                "days_open": int(rng.integers(8, 190)),
            }
        )

    customer_rows = []
    industries = ["Technology", "Healthcare", "Finance", "Manufacturing", "Retail"]
    account_tiers = ["Strategic", "Growth", "Core"]
    health_scores = ["Excellent", "Good", "At Risk"]

    for customer_id in range(1, 91):
        mrr = float(rng.integers(900, 24_000))
        health = rng.choice(health_scores, p=[0.31, 0.5, 0.19])
        churn_risk = {"Excellent": 0.04, "Good": 0.11, "At Risk": 0.33}[health]
        customer_rows.append(
            {
                "customer_id": f"CUS-{customer_id:04d}",
                "region": rng.choice(regions, p=[0.35, 0.32, 0.22, 0.11]),
                "industry": rng.choice(industries),
                "account_tier": rng.choice(account_tiers, p=[0.18, 0.34, 0.48]),
                "health_score": health,
                "monthly_recurring_revenue": round(mrr, 2),
                "annual_recurring_revenue": round(mrr * 12, 2),
                "churn_risk": churn_risk,
                "support_tickets_90d": int(rng.integers(0, 26)),
                "nps": int(rng.integers(12, 96)),
            }
        )

    return {
        "Orders": pd.DataFrame(order_rows),
        "Pipeline": pd.DataFrame(pipeline_rows),
        "Customers": pd.DataFrame(customer_rows),
    }


def metric_card(label: str, value: str, helper: str) -> None:
    st.markdown(
        f"""
        <div class="metric-card">
            <div class="metric-label">{label}</div>
            <div class="metric-value">{value}</div>
            <div class="metric-helper">{helper}</div>
        </div>
        """,
        unsafe_allow_html=True,
    )


def currency(value: float) -> str:
    return f"${value:,.0f}"


def configure_chart(fig):
    fig.update_layout(
        margin=dict(l=10, r=10, t=36, b=10),
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
        font=dict(color="#172033", family="Inter, Segoe UI, sans-serif"),
        legend_title_text="",
    )
    return fig


def render_orders(df: pd.DataFrame) -> None:
    total_revenue = df["revenue"].sum()
    margin_rate = df["gross_margin"].sum() / total_revenue

    kpi_cols = st.columns(4)
    with kpi_cols[0]:
        metric_card("Revenue", currency(total_revenue), "Recognized sales")
    with kpi_cols[1]:
        metric_card("Orders", f"{len(df):,}", "Completed transactions")
    with kpi_cols[2]:
        metric_card("Units Sold", f"{df['units'].sum():,}", "Total product volume")
    with kpi_cols[3]:
        metric_card("Gross Margin", f"{margin_rate:.1%}", "Blended contribution")

    monthly = df.groupby("month", as_index=False).agg(revenue=("revenue", "sum"), gross_margin=("gross_margin", "sum"))
    by_region = df.groupby("region", as_index=False)["revenue"].sum().sort_values("revenue", ascending=False)
    by_product = df.groupby("product", as_index=False).agg(revenue=("revenue", "sum"), units=("units", "sum"))

    left, right = st.columns((1.35, 1))
    with left:
        st.plotly_chart(
            configure_chart(px.line(monthly, x="month", y="revenue", markers=True, title="Monthly revenue trend")),
            use_container_width=True,
        )
    with right:
        st.plotly_chart(
            configure_chart(px.bar(by_region, x="region", y="revenue", color="region", title="Revenue by region")),
            use_container_width=True,
        )

    st.plotly_chart(
        configure_chart(px.scatter(by_product, x="units", y="revenue", size="revenue", color="product", title="Product performance")),
        use_container_width=True,
    )


def render_pipeline(df: pd.DataFrame) -> None:
    open_pipeline = df.loc[~df["stage"].isin(["Closed Won", "Closed Lost"])]
    win_rate = (df["stage"].eq("Closed Won").sum() / df["stage"].str.startswith("Closed").sum()).round(3)

    kpi_cols = st.columns(4)
    with kpi_cols[0]:
        metric_card("Open Pipeline", currency(open_pipeline["deal_value"].sum()), "Unclosed deal value")
    with kpi_cols[1]:
        metric_card("Weighted Pipeline", currency(open_pipeline["weighted_value"].sum()), "Probability adjusted")
    with kpi_cols[2]:
        metric_card("Avg Deal Size", currency(df["deal_value"].mean()), "Across all opportunities")
    with kpi_cols[3]:
        metric_card("Win Rate", f"{win_rate:.1%}", "Closed won / closed deals")

    stage = df.groupby("stage", as_index=False).agg(deal_value=("deal_value", "sum"), opportunities=("opportunity_id", "count"))
    reps = df.groupby("sales_rep", as_index=False).agg(weighted_value=("weighted_value", "sum"), opportunities=("opportunity_id", "count"))
    segment = df.groupby("segment", as_index=False)["deal_value"].sum()

    left, right = st.columns((1.2, 1))
    with left:
        st.plotly_chart(
            configure_chart(px.funnel(stage, x="deal_value", y="stage", title="Pipeline value by stage")),
            use_container_width=True,
        )
    with right:
        st.plotly_chart(
            configure_chart(px.pie(segment, names="segment", values="deal_value", hole=0.55, title="Deal value by segment")),
            use_container_width=True,
        )

    st.plotly_chart(
        configure_chart(px.bar(reps, x="sales_rep", y="weighted_value", color="opportunities", title="Weighted pipeline by sales rep")),
        use_container_width=True,
    )


def render_customers(df: pd.DataFrame) -> None:
    avg_churn_risk = df["churn_risk"].mean()

    kpi_cols = st.columns(4)
    with kpi_cols[0]:
        metric_card("ARR", currency(df["annual_recurring_revenue"].sum()), "Recurring revenue base")
    with kpi_cols[1]:
        metric_card("Customers", f"{len(df):,}", "Active accounts")
    with kpi_cols[2]:
        metric_card("Avg NPS", f"{df['nps'].mean():.0f}", "Relationship health")
    with kpi_cols[3]:
        metric_card("Avg Churn Risk", f"{avg_churn_risk:.1%}", "Modeled account risk")

    tier = df.groupby("account_tier", as_index=False)["annual_recurring_revenue"].sum()
    health = df.groupby("health_score", as_index=False).agg(customers=("customer_id", "count"), arr=("annual_recurring_revenue", "sum"))
    industry = df.groupby("industry", as_index=False).agg(arr=("annual_recurring_revenue", "sum"), avg_nps=("nps", "mean"))

    left, right = st.columns((1, 1))
    with left:
        st.plotly_chart(
            configure_chart(px.bar(tier, x="account_tier", y="annual_recurring_revenue", color="account_tier", title="ARR by account tier")),
            use_container_width=True,
        )
    with right:
        st.plotly_chart(
            configure_chart(px.pie(health, names="health_score", values="customers", hole=0.5, title="Customer health mix")),
            use_container_width=True,
        )

    st.plotly_chart(
        configure_chart(px.scatter(industry, x="avg_nps", y="arr", size="arr", color="industry", title="Industry revenue and NPS")),
        use_container_width=True,
    )


st.markdown(
    """
    <style>
        @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;600;700;800&display=swap');

        :root {
            --ink: #172033;
            --muted: #657085;
            --panel: #ffffff;
            --line: #dfe5ee;
            --accent: #0f8b8d;
            --accent-2: #f25f5c;
            --bg: #f5f7fb;
        }

        .stApp {
            background: var(--bg);
            color: var(--ink);
            font-family: Inter, Segoe UI, sans-serif;
        }

        [data-testid="stSidebar"] {
            background: #ffffff;
            border-right: 1px solid var(--line);
        }

        .main .block-container {
            padding-top: 2rem;
            padding-bottom: 2rem;
            max-width: 1320px;
        }

        h1, h2, h3 {
            letter-spacing: 0;
            color: var(--ink);
        }

        .dashboard-header {
            display: flex;
            justify-content: space-between;
            gap: 1rem;
            align-items: flex-end;
            border-bottom: 1px solid var(--line);
            padding-bottom: 1.1rem;
            margin-bottom: 1.1rem;
        }

        .dashboard-title {
            font-size: 2.15rem;
            line-height: 1.1;
            font-weight: 800;
            margin: 0;
        }

        .dashboard-subtitle {
            color: var(--muted);
            margin-top: .45rem;
            max-width: 760px;
        }

        .source-pill {
            border: 1px solid var(--line);
            background: var(--panel);
            border-radius: 8px;
            padding: .75rem .9rem;
            min-width: 180px;
            text-align: right;
        }

        .source-pill span {
            color: var(--muted);
            font-size: .75rem;
            text-transform: uppercase;
            font-weight: 700;
        }

        .source-pill strong {
            display: block;
            color: var(--accent);
            font-size: 1.05rem;
            margin-top: .15rem;
        }

        .metric-card {
            background: var(--panel);
            border: 1px solid var(--line);
            border-radius: 8px;
            padding: 1rem;
            min-height: 116px;
            box-shadow: 0 8px 24px rgba(23, 32, 51, 0.05);
        }

        .metric-label {
            color: var(--muted);
            font-size: .78rem;
            text-transform: uppercase;
            font-weight: 800;
        }

        .metric-value {
            color: var(--ink);
            font-size: 1.65rem;
            font-weight: 800;
            margin-top: .35rem;
            overflow-wrap: anywhere;
        }

        .metric-helper {
            color: var(--muted);
            font-size: .86rem;
            margin-top: .3rem;
        }

        [data-testid="stPlotlyChart"] {
            background: var(--panel);
            border: 1px solid var(--line);
            border-radius: 8px;
            padding: .75rem;
            box-shadow: 0 8px 24px rgba(23, 32, 51, 0.04);
        }

        div[data-testid="stDataFrame"] {
            border: 1px solid var(--line);
            border-radius: 8px;
            overflow: hidden;
        }

        @media (max-width: 780px) {
            .dashboard-header {
                display: block;
            }

            .source-pill {
                text-align: left;
                margin-top: 1rem;
            }
        }
    </style>
    """,
    unsafe_allow_html=True,
)


data_sources = build_sample_data()

with st.sidebar:
    st.header("Controls")
    selected_source = st.radio(
        "Data source",
        list(data_sources.keys()),
        captions=[
            "Completed sales orders and product performance",
            "Opportunities, stages, and rep ownership",
            "Recurring revenue and customer health",
        ],
    )

    st.divider()
    st.caption("All data is generated inside the Python code. No database connection is required.")

df = data_sources[selected_source]

st.markdown(
    f"""
    <div class="dashboard-header">
        <div>
            <h1 class="dashboard-title">Sales Performance Dashboard</h1>
            <div class="dashboard-subtitle">
                Explore core commercial performance from embedded sample data. Switch sources in the sidebar to analyze orders,
                pipeline, or customer revenue health.
            </div>
        </div>
        <div class="source-pill">
            <span>Selected source</span>
            <strong>{selected_source}</strong>
        </div>
    </div>
    """,
    unsafe_allow_html=True,
)

if selected_source == "Orders":
    render_orders(df)
elif selected_source == "Pipeline":
    render_pipeline(df)
else:
    render_customers(df)

with st.expander("View source data", expanded=False):
    st.dataframe(df, use_container_width=True, hide_index=True)
