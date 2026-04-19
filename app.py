import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import numpy as np
import io
import yaml
from yaml.loader import SafeLoader
import streamlit_authenticator as stauth

st.set_page_config(
    page_title="DataFusion · Sales Intelligence",
    page_icon="⬡",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ─── Global styles (applied before auth check so login page is themed too) ───
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Space+Mono:wght@400;700&family=DM+Sans:wght@300;400;500;600&display=swap');

html, body, [class*="css"] { font-family: 'DM Sans', sans-serif; }

.stApp { background: #0a0e1a; color: #e2e8f0; }

section[data-testid="stSidebar"] {
    background: #0d1120 !important;
    border-right: 1px solid #1e2a3a;
}
section[data-testid="stSidebar"] * { color: #94a3b8 !important; }

h1, h2, h3 {
    font-family: 'Space Mono', monospace !important;
    color: #f1f5f9 !important;
    letter-spacing: -0.5px;
}

.main-title {
    font-family: 'Space Mono', monospace;
    font-size: 2.2rem;
    font-weight: 700;
    color: #f1f5f9;
    letter-spacing: -1px;
    margin-bottom: 0.2rem;
}
.main-subtitle {
    font-family: 'DM Sans', sans-serif;
    font-size: 1rem;
    color: #64748b;
    margin-bottom: 2rem;
    letter-spacing: 0.5px;
}
.accent { color: #38bdf8; }

.metric-card {
    background: #111827;
    border: 1px solid #1e2d3d;
    border-radius: 12px;
    padding: 1.2rem 1.5rem;
}
.metric-label {
    font-family: 'Space Mono', monospace;
    font-size: 0.65rem;
    color: #475569;
    text-transform: uppercase;
    letter-spacing: 2px;
    margin-bottom: 0.4rem;
}
.metric-value {
    font-family: 'Space Mono', monospace;
    font-size: 1.8rem;
    font-weight: 700;
    color: #f1f5f9;
    line-height: 1;
}
.metric-delta { font-size: 0.8rem; color: #34d399; margin-top: 0.3rem; }

.section-label {
    font-family: 'Space Mono', monospace;
    font-size: 0.65rem;
    color: #38bdf8;
    text-transform: uppercase;
    letter-spacing: 3px;
    margin-bottom: 1rem;
    border-bottom: 1px solid #1e2a3a;
    padding-bottom: 0.5rem;
}

.tag {
    display: inline-block;
    background: #0f2744;
    color: #38bdf8;
    font-family: 'Space Mono', monospace;
    font-size: 0.7rem;
    padding: 3px 10px;
    border-radius: 20px;
    border: 1px solid #1e3a5a;
    margin-right: 4px;
    margin-bottom: 4px;
}

.insight-box {
    background: #0d1827;
    border-left: 3px solid #38bdf8;
    border-radius: 0 8px 8px 0;
    padding: 0.8rem 1.2rem;
    margin: 0.5rem 0;
    font-size: 0.88rem;
    color: #94a3b8;
}

.status-ok  { color: #34d399; font-family: 'Space Mono', monospace; font-size: 0.8rem; }
.status-warn{ color: #fbbf24; font-family: 'Space Mono', monospace; font-size: 0.8rem; }

/* ── Login page overrides ── */
.login-wrap {
    max-width: 420px;
    margin: 6rem auto 0;
    background: #111827;
    border: 1px solid #1e2d3d;
    border-radius: 16px;
    padding: 2.5rem 2rem;
}

div[data-testid="stForm"] {
    background: transparent !important;
    border: none !important;
    padding: 0 !important;
}

.stTextInput > label, .stButton > button {
    font-family: 'Space Mono', monospace !important;
}

.stButton > button {
    background: linear-gradient(135deg, #0ea5e9 0%, #38bdf8 100%);
    color: #0a0e1a !important;
    border: none !important;
    border-radius: 8px !important;
    font-weight: 700 !important;
    font-size: 0.8rem !important;
    letter-spacing: 1px;
    padding: 0.6rem 2rem !important;
    width: 100%;
}

.stTabs [data-baseweb="tab"] {
    font-family: 'Space Mono', monospace !important;
    font-size: 0.75rem !important;
    color: #475569 !important;
    letter-spacing: 1px;
}
.stTabs [aria-selected="true"]          { color: #38bdf8 !important; }
.stTabs [data-baseweb="tab-highlight"]  { background-color: #38bdf8 !important; }
.stTabs [data-baseweb="tab-border"]     { background-color: #1e2a3a !important; }
hr { border-color: #1e2a3a !important; }
</style>
""", unsafe_allow_html=True)

# ══════════════════════════════════════════════════════════════════
#  AUTH LAYER
# ══════════════════════════════════════════════════════════════════

import os

if os.path.exists("config.yaml"):
    with open("config.yaml") as f:
        config = yaml.load(f, Loader=SafeLoader)
else:
    config = {
        "credentials": {
            "usernames": {
                k: dict(v) for k, v in st.secrets["credentials"]["usernames"].items()
            }
        },
        "cookie": dict(st.secrets["cookie"]),
    }

authenticator = stauth.Authenticate(
    config["credentials"],
    config["cookie"]["name"],
    config["cookie"]["key"],
    config["cookie"]["expiry_days"],
)

# Centered login card
if "authentication_status" not in st.session_state or not st.session_state["authentication_status"]:
    st.markdown("""
    <div style="text-align:center;margin-top:3rem;">
        <div class="main-title">⬡ DATAFUSION</div>
        <div class="main-subtitle">Sales Intelligence Suite</div>
    </div>
    """, unsafe_allow_html=True)

col_l, col_c, col_r = st.columns([1, 1.2, 1])
with col_c:
    authenticator.login()

auth_status = st.session_state.get("authentication_status")

if auth_status is False:
    st.error("⚠ Username or password is incorrect.")
    st.stop()

if auth_status is None:
    st.stop()

# ── Authenticated beyond this point ──────────────────────────────

# ══════════════════════════════════════════════════════════════════
#  CONSTANTS / HELPERS
# ══════════════════════════════════════════════════════════════════

PLOTLY_THEME = dict(
    paper_bgcolor="rgba(0,0,0,0)",
    plot_bgcolor="#0d1120",
    font=dict(family="DM Sans, sans-serif", color="#94a3b8", size=12),
    title_font=dict(family="Space Mono, monospace", color="#f1f5f9", size=14),
    xaxis=dict(gridcolor="#1e2a3a", linecolor="#1e2a3a", tickfont=dict(color="#64748b")),
    yaxis=dict(gridcolor="#1e2a3a", linecolor="#1e2a3a", tickfont=dict(color="#64748b")),
    legend=dict(bgcolor="rgba(0,0,0,0)", bordercolor="#1e2a3a", borderwidth=1, font=dict(color="#94a3b8")),
    margin=dict(l=40, r=20, t=50, b=40),
    colorway=["#38bdf8","#34d399","#f472b6","#fbbf24","#a78bfa","#fb923c","#22d3ee"],
)
COLORS = ["#38bdf8","#34d399","#f472b6","#fbbf24","#a78bfa","#fb923c","#22d3ee","#e879f9","#4ade80"]


def apply_theme(fig):
    fig.update_layout(**PLOTLY_THEME)
    return fig


def detect_column_types(df):
    numeric_cols = df.select_dtypes(include=np.number).columns.tolist()
    cat_cols     = df.select_dtypes(include=["object","category"]).columns.tolist()
    date_cols    = []
    for col in df.columns:
        if df[col].dtype == "object":
            try:
                converted = pd.to_datetime(df[col], infer_datetime_format=True, errors="coerce")
                if converted.notna().sum() / len(df) > 0.6:
                    date_cols.append(col)
            except Exception:
                pass
    return numeric_cols, cat_cols, date_cols


def smart_merge_suggestion(df1, df2):
    common = list(set(df1.columns) & set(df2.columns))
    suggestions = []
    for col in common:
        overlap = len(set(df1[col].dropna().astype(str)) & set(df2[col].dropna().astype(str)))
        if overlap > 0:
            suggestions.append((col, overlap))
    suggestions.sort(key=lambda x: -x[1])
    return common, suggestions


# ══════════════════════════════════════════════════════════════════
#  SIDEBAR
# ══════════════════════════════════════════════════════════════════

with st.sidebar:
    username = st.session_state.get("username", "user")
    name     = st.session_state.get("name", username)
    st.markdown(f'<div class="main-title" style="font-size:1.2rem;">⬡ DATAFUSION</div>', unsafe_allow_html=True)
    st.markdown(f'<div style="font-size:0.75rem;color:#64748b;font-family:Space Mono,monospace;margin-bottom:0.5rem;">logged in as <span style="color:#38bdf8">{name}</span></div>', unsafe_allow_html=True)
    authenticator.logout("↩ Sign out", "sidebar")
    st.markdown("---")

    st.markdown('<div class="section-label">// Upload Files</div>', unsafe_allow_html=True)
    file1 = st.file_uploader("FILE 01 — Primary Dataset",   type=["csv"], key="f1")
    file2 = st.file_uploader("FILE 02 — Secondary Dataset", type=["csv"], key="f2")

    if file1 and file2:
        st.markdown("---")
        st.markdown('<div class="section-label">// Merge Configuration</div>', unsafe_allow_html=True)

        df1_preview = pd.read_csv(file1); file1.seek(0)
        df2_preview = pd.read_csv(file2); file2.seek(0)

        common_cols, suggestions = smart_merge_suggestion(df1_preview, df2_preview)

        merge_mode = st.selectbox(
            "MERGE STRATEGY",
            ["Join on key column", "Stack vertically (union)", "Full control (advanced)"],
        )

        if merge_mode == "Join on key column":
            if suggestions:
                st.markdown(f'<div class="status-ok">↳ suggested: {suggestions[0][0]} ({suggestions[0][1]} matching rows)</div>', unsafe_allow_html=True)
            join_key  = st.selectbox("JOIN KEY",  common_cols if common_cols else ["— no common columns —"])
            join_type = st.selectbox("JOIN TYPE", ["inner","left","right","outer"])

        elif merge_mode == "Full control (advanced)":
            left_key  = st.selectbox("LEFT KEY (File 01)",  df1_preview.columns.tolist())
            right_key = st.selectbox("RIGHT KEY (File 02)", df2_preview.columns.tolist())
            join_type = st.selectbox("JOIN TYPE", ["inner","left","right","outer"])

        st.markdown("---")
        merge_btn = st.button("⬡  MERGE & ANALYZE")

# ══════════════════════════════════════════════════════════════════
#  MAIN HEADER
# ══════════════════════════════════════════════════════════════════

st.markdown('<div class="main-title">⬡ DATAFUSION</div>', unsafe_allow_html=True)
st.markdown('<div class="main-subtitle">Sales Intelligence · Dynamic Visual Analytics Platform</div>', unsafe_allow_html=True)

# ── No files yet ─────────────────────────────────────────────────
if not file1 and not file2:
    col1, col2 = st.columns(2)
    for col, label in zip([col1, col2], ["FILE 01", "FILE 02"]):
        with col:
            st.markdown(f"""
            <div style="background:#0d1120;border:1.5px dashed #1e3a4a;border-radius:12px;
                        padding:2rem;text-align:center;">
                <div style="font-family:'Space Mono',monospace;font-size:0.7rem;color:#38bdf8;
                            letter-spacing:3px;margin-bottom:1rem;">{label}</div>
                <div style="font-size:2rem;margin-bottom:0.5rem;">📂</div>
                <div style="color:#475569;font-size:0.9rem;">Upload CSV via the sidebar →</div>
            </div>""", unsafe_allow_html=True)
    st.markdown("<br>", unsafe_allow_html=True)
    st.markdown('<div class="section-label">// How It Works</div>', unsafe_allow_html=True)
    for num, desc in [
        ("01","Upload two CSV files using the sidebar uploader"),
        ("02","Configure your merge strategy — join, stack, or full control"),
        ("03","Hit MERGE & ANALYZE to fuse your datasets"),
        ("04","Explore dynamic, interactive visual insights instantly"),
    ]:
        st.markdown(f'<div class="insight-box"><span style="font-family:Space Mono,monospace;color:#38bdf8;font-size:0.75rem;">[{num}]</span> &nbsp; {desc}</div>', unsafe_allow_html=True)
    st.stop()

# ── Load both files ───────────────────────────────────────────────
if file1:
    df1 = pd.read_csv(file1); file1.seek(0)
if file2:
    df2 = pd.read_csv(file2); file2.seek(0)

if file1 and file2:
    c1, c2 = st.columns(2)
    for col, df_prev, label in zip([c1, c2], [df1, df2], ["File 01","File 02"]):
        with col:
            st.markdown(f'<div class="section-label">// {label} Preview</div>', unsafe_allow_html=True)
            st.markdown(f'<span class="tag">{df_prev.shape[0]} rows</span><span class="tag">{df_prev.shape[1]} cols</span>', unsafe_allow_html=True)
            st.dataframe(df_prev.head(5), use_container_width=True, height=200)

# ── Merge ─────────────────────────────────────────────────────────
if file1 and file2 and "merge_btn" in dir() and merge_btn:
    with st.spinner("Fusing datasets…"):
        try:
            if merge_mode == "Join on key column":
                df = pd.merge(df1, df2, on=join_key, how=join_type, suffixes=("_file1","_file2"))
            elif merge_mode == "Stack vertically (union)":
                df = pd.concat([df1, df2], ignore_index=True)
            else:
                df = pd.merge(df1, df2, left_on=left_key, right_on=right_key, how=join_type, suffixes=("_file1","_file2"))
            st.session_state["merged_df"] = df
            st.success(f"✓ Merged → {df.shape[0]:,} rows × {df.shape[1]} columns")
        except Exception as e:
            st.error(f"Merge failed: {e}")
            st.stop()

# ══════════════════════════════════════════════════════════════════
#  ANALYTICS DASHBOARD
# ══════════════════════════════════════════════════════════════════

if "merged_df" not in st.session_state:
    st.stop()

df = st.session_state["merged_df"]
numeric_cols, cat_cols, date_cols = detect_column_types(df)

for col in date_cols:
    try:
        df[col] = pd.to_datetime(df[col], infer_datetime_format=True, errors="coerce")
    except Exception:
        pass

st.markdown("---")
st.markdown('<div class="section-label">// Merged Dataset · Quick Stats</div>', unsafe_allow_html=True)

m1, m2, m3, m4 = st.columns(4)
for col, label, value in zip(
    [m1, m2, m3, m4],
    ["TOTAL ROWS","COLUMNS","NUMERIC FIELDS","NULL RATE"],
    [f"{df.shape[0]:,}", str(df.shape[1]), str(len(numeric_cols)), f"{df.isnull().mean().mean()*100:.1f}%"],
):
    with col:
        st.markdown(f'<div class="metric-card"><div class="metric-label">{label}</div><div class="metric-value">{value}</div></div>', unsafe_allow_html=True)

st.markdown("<br>", unsafe_allow_html=True)

tab1, tab2, tab3, tab4, tab5 = st.tabs(["OVERVIEW","DISTRIBUTIONS","RELATIONSHIPS","TIME SERIES","RAW DATA"])

# ── TAB 1: OVERVIEW ──────────────────────────────────────────────
with tab1:
    st.markdown('<div class="section-label">// Summary Metrics</div>', unsafe_allow_html=True)
    if numeric_cols:
        for i in range(0, min(8, len(numeric_cols)), 4):
            row_cols = st.columns(4)
            for j, col in enumerate(numeric_cols[i:i+4]):
                total = df[col].sum(); mean = df[col].mean()
                display = f"${total/1e6:.1f}M" if total > 1e6 else (f"{total/1e3:.1f}K" if total > 1000 else f"{total:.1f}")
                with row_cols[j]:
                    st.markdown(f'<div class="metric-card"><div class="metric-label">{col[:20]}</div><div class="metric-value" style="font-size:1.3rem;">{display}</div><div class="metric-delta">avg {mean:.1f}</div></div>', unsafe_allow_html=True)

    if cat_cols and numeric_cols:
        st.markdown("<br>", unsafe_allow_html=True)
        st.markdown('<div class="section-label">// Top Categories</div>', unsafe_allow_html=True)
        c1, c2 = st.columns(2)
        with c1:
            cat_col = st.selectbox("Category field", cat_cols, key="ov_cat")
            num_col = st.selectbox("Value field", numeric_cols, key="ov_num")
            top_n   = st.slider("Top N", 5, 20, 10, key="ov_n")
        with c2:
            grouped = df.groupby(cat_col)[num_col].sum().nlargest(top_n).reset_index()
            fig = go.Figure(go.Bar(
                x=grouped[num_col], y=grouped[cat_col], orientation="h",
                marker=dict(color=grouped[num_col], colorscale=[[0,"#1e3a4a"],[1,"#38bdf8"]], showscale=False),
                text=[f"{v:,.0f}" for v in grouped[num_col]], textposition="outside",
                textfont=dict(color="#94a3b8", size=11),
            ))
            fig.update_layout(**PLOTLY_THEME, height=350, title=f"Top {top_n} {cat_col} by {num_col}")
            fig.update_yaxes(tickfont=dict(color="#94a3b8", size=11), gridcolor="#1e2a3a", linecolor="#1e2a3a")
            fig.update_xaxes(gridcolor="#1e2a3a", linecolor="#1e2a3a", tickfont=dict(color="#64748b"))

        st.markdown('<div class="section-label">// Category Share</div>', unsafe_allow_html=True)
        pie_cat = st.selectbox("Category for pie", cat_cols, key="pie_cat")
        pie_num = st.selectbox("Value for pie",    numeric_cols, key="pie_num")
        pie_data = df.groupby(pie_cat)[pie_num].sum().nlargest(10).reset_index()
        fig2 = go.Figure(go.Pie(
            labels=pie_data[pie_cat], values=pie_data[pie_num], hole=0.55,
            marker=dict(colors=COLORS, line=dict(color="#0a0e1a", width=2)),
            textfont=dict(color="#f1f5f9", size=11), textinfo="label+percent",
        ))
        fig2.update_layout(**PLOTLY_THEME, height=380, title=f"{pie_num} share by {pie_cat}")
        st.plotly_chart(fig2, use_container_width=True)

# ── TAB 2: DISTRIBUTIONS ─────────────────────────────────────────
with tab2:
    st.markdown('<div class="section-label">// Distribution Analysis</div>', unsafe_allow_html=True)
    if numeric_cols:
        dist_col = st.selectbox("Select numeric column", numeric_cols, key="dist_col")
        d1, d2 = st.columns(2)
        with d1:
            fig_hist = go.Figure(go.Histogram(
                x=df[dist_col].dropna(), nbinsx=40,
                marker=dict(color="#38bdf8", opacity=0.8, line=dict(color="#0a0e1a", width=0.5)),
            ))
            fig_hist.update_layout(**PLOTLY_THEME, height=300, title=f"Distribution — {dist_col}")
            st.plotly_chart(fig_hist, use_container_width=True)
        with d2:
            fig_box = go.Figure(go.Box(
                y=df[dist_col].dropna(), marker_color="#38bdf8", line_color="#38bdf8",
                fillcolor="rgba(56,189,248,0.15)", boxmean=True,
            ))
            fig_box.update_layout(**PLOTLY_THEME, height=300, title=f"Box Plot — {dist_col}")
            st.plotly_chart(fig_box, use_container_width=True)

    if len(numeric_cols) >= 2:
        st.markdown('<div class="section-label">// Multi-field Distribution</div>', unsafe_allow_html=True)
        sel = st.multiselect("Compare distributions", numeric_cols, default=numeric_cols[:4], key="multi_dist")
        if sel:
            fig_v = go.Figure()
            for i, c in enumerate(sel):
                fig_v.add_trace(go.Violin(
                    y=df[c].dropna(), name=c, box_visible=True, meanline_visible=True,
                    fillcolor=COLORS[i%len(COLORS)], opacity=0.7, line_color=COLORS[i%len(COLORS)],
                ))
            fig_v.update_layout(**PLOTLY_THEME, height=380, title="Violin Distributions")
            st.plotly_chart(fig_v, use_container_width=True)

    if cat_cols and numeric_cols:
        st.markdown('<div class="section-label">// Category Breakdown</div>', unsafe_allow_html=True)
        box_cat = st.selectbox("Group by",  cat_cols,     key="box_cat")
        box_num = st.selectbox("Measure",   numeric_cols, key="box_num")
        top_cats = df[box_cat].value_counts().nlargest(12).index
        fig_b2 = px.box(df[df[box_cat].isin(top_cats)], x=box_cat, y=box_num,
                        color=box_cat, color_discrete_sequence=COLORS)
        fig_b2.update_layout(**PLOTLY_THEME, height=380, title=f"{box_num} by {box_cat}", showlegend=False)
        st.plotly_chart(fig_b2, use_container_width=True)

# ── TAB 3: RELATIONSHIPS ──────────────────────────────────────────
with tab3:
    st.markdown('<div class="section-label">// Correlation Matrix</div>', unsafe_allow_html=True)
    if len(numeric_cols) >= 2:
        corr_cols = st.multiselect("Fields to correlate", numeric_cols,
                                   default=numeric_cols[:min(8,len(numeric_cols))], key="corr_cols")
        if len(corr_cols) >= 2:
            cm = df[corr_cols].corr()
            fig_c = go.Figure(go.Heatmap(
                z=cm.values, x=cm.columns, y=cm.columns,
                colorscale=[[0,"#1a0a2e"],[0.5,"#0d1120"],[1,"#38bdf8"]],
                text=np.round(cm.values,2), texttemplate="%{text}",
                textfont=dict(size=11,color="#f1f5f9"), zmin=-1, zmax=1,
            ))
            fig_c.update_layout(**PLOTLY_THEME, height=420, title="Correlation Heatmap")
            st.plotly_chart(fig_c, use_container_width=True)

    if len(numeric_cols) >= 2:
        st.markdown('<div class="section-label">// Scatter Relationship</div>', unsafe_allow_html=True)
        sc1, sc2, sc3 = st.columns(3)
        with sc1: x_col = st.selectbox("X axis", numeric_cols, key="sc_x")
        with sc2: y_col = st.selectbox("Y axis", numeric_cols, index=min(1,len(numeric_cols)-1), key="sc_y")
        with sc3: color_col = st.selectbox("Color by", ["None"]+cat_cols, key="sc_color")
        fig_sc = px.scatter(df.dropna(subset=[x_col,y_col]), x=x_col, y=y_col,
                            color=None if color_col=="None" else color_col,
                            color_discrete_sequence=COLORS, trendline="ols", opacity=0.75)
        fig_sc.update_traces(marker=dict(size=7))
        fig_sc.update_layout(**PLOTLY_THEME, height=400, title=f"{x_col} vs {y_col}")
        st.plotly_chart(fig_sc, use_container_width=True)

# ── TAB 4: TIME SERIES ────────────────────────────────────────────
with tab4:
    st.markdown('<div class="section-label">// Time Series Analysis</div>', unsafe_allow_html=True)
    if date_cols and numeric_cols:
        ts_date = st.selectbox("Date column", date_cols, key="ts_date")
        ts_num  = st.multiselect("Metrics to plot", numeric_cols, default=numeric_cols[:2], key="ts_num")
        ts_freq = st.selectbox("Resample frequency", ["D","W","M","Q"],
                               format_func=lambda x:{"D":"Daily","W":"Weekly","M":"Monthly","Q":"Quarterly"}[x])
        if ts_num:
            ts_df = df[[ts_date]+ts_num].dropna(subset=[ts_date])
            ts_df = ts_df.set_index(ts_date).resample(ts_freq)[ts_num].sum().reset_index()
            fig_ts = go.Figure()
            for i, c in enumerate(ts_num):
                fig_ts.add_trace(go.Scatter(
                    x=ts_df[ts_date], y=ts_df[c], name=c, mode="lines+markers",
                    line=dict(color=COLORS[i%len(COLORS)], width=2), marker=dict(size=5),
                    fill="tozeroy" if i==0 else "none",
                    fillcolor="rgba(56,189,248,0.06)" if i==0 else None,
                ))
            fig_ts.update_layout(**PLOTLY_THEME, height=400, title="Trend Over Time")
            st.plotly_chart(fig_ts, use_container_width=True)
    else:
        st.markdown('<div class="insight-box">No date columns detected. Showing index-based trend.</div>', unsafe_allow_html=True)
        if numeric_cols:
            idx_num = st.selectbox("Metric", numeric_cols, key="idx_num")
            smooth  = st.slider("Smoothing window", 1, 20, 5, key="smooth")
            series  = df[idx_num].dropna().reset_index(drop=True)
            fig_idx = go.Figure()
            fig_idx.add_trace(go.Scatter(y=series, mode="lines", name="raw",
                                         line=dict(color="#1e3a4a", width=1)))
            fig_idx.add_trace(go.Scatter(y=series.rolling(smooth,center=True).mean(),
                                         mode="lines", name="smoothed",
                                         line=dict(color="#38bdf8", width=2.5)))
            fig_idx.update_layout(**PLOTLY_THEME, height=360, title=f"{idx_num} trend")
            st.plotly_chart(fig_idx, use_container_width=True)

# ── TAB 5: RAW DATA ───────────────────────────────────────────────
with tab5:
    st.markdown('<div class="section-label">// Merged Dataset · Full View</div>', unsafe_allow_html=True)
    st.markdown(f'<span class="tag">{df.shape[0]:,} rows</span><span class="tag">{df.shape[1]} cols</span>', unsafe_allow_html=True)
    search = st.text_input("Filter rows", placeholder="search any value…", key="search")
    display_df = df[df.astype(str).apply(lambda c: c.str.contains(search,case=False,na=False)).any(axis=1)] if search else df
    st.dataframe(display_df, use_container_width=True, height=420)
    buf = io.StringIO(); df.to_csv(buf, index=False)
    st.download_button("⬇  DOWNLOAD MERGED CSV", data=buf.getvalue(),
                       file_name="datafusion_merged.csv", mime="text/csv")
