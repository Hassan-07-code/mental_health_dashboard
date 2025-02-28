import streamlit as st
import pandas as pd
import plotly.express as px
from utils.data_loader import load_data  

# --- Page Config ---
st.set_page_config(page_title="Mental Health Insights", layout="wide")

# --- Load Dataset ---
df = load_data()
if df is None:
    st.error("Failed to load data. Please check the data source.")
    st.stop()

# --- Categorical Mappings ---
conversion_dict = {
    "No": 0, "Yes": 1,
    "Rarely": 1, "Sometimes": 2, "Often": 3, "Always": 4,
    "1-14 days": 7, "15-30 days": 22, "More than 30 days": 35,
    "Go out Every day": 0, "More than 2 months": 60,
}

# --- Columns to Convert ---
stress_related_columns = ["growing_stress", "coping_struggles", "changes_habits", "social_weakness"]

# Apply conversion to numeric
for col in stress_related_columns:
    if col in df.columns:
        df[col] = df[col].replace(conversion_dict)
        df[col] = pd.to_numeric(df[col], errors='coerce')
    else:
        st.error(f"🚨 Column '{col}' not found in dataset!")

# --- Main Interface ---
st.markdown(
    "<h1 style='text-align: center; color: #00aaff;'>🧠 Mental Health Insights </h1>",
    unsafe_allow_html=True
)
st.markdown(
    "<p style='text-align: center; color: #00aaff;'>A comprehensive overview of mental health trends across all countries</p>",
    unsafe_allow_html=True
)

# --- Data Processing ---
df_selected = df.copy()
normalize_data = True  # Fixed normalization
threshold = 0.5  # Fixed threshold for "Low" vs "High"

# Normalize and categorize all factors
for col in stress_related_columns:
    if df_selected[col].notna().sum() > 0:
        min_val = df_selected[col].min()
        max_val = df_selected[col].max()
        if min_val != max_val:
            df_selected[f"{col}_scaled"] = (df_selected[col] - min_val) / (max_val - min_val)
        else:
            df_selected[f"{col}_scaled"] = 0
        df_selected[f"{col}_category"] = df_selected[f"{col}_scaled"].apply(lambda x: "High" if x > threshold else "Low")

# Aggregate data for all factors
category_counts = pd.DataFrame()
for col in stress_related_columns:
    temp_counts = df_selected.groupby([f"{col}_category"]).size().reset_index(name="Count")
    temp_counts["Factor"] = col.replace("_", " ").title()
    temp_counts = temp_counts.rename(columns={f"{col}_category": "Category"})
    category_counts = pd.concat([category_counts, temp_counts], ignore_index=True)

# --- Summary Section ---
st.subheader("📌 Summary Statistics")

col1, col2, col3 = st.columns(3)

with col1:
    st.metric("Total Countries", df["country"].nunique())  # More efficient way

with col2:
    total_respondents = df[stress_related_columns].notna().any(axis=1).sum()  # Count respondents with at least 1 response
    st.metric("Total Respondents", f"{total_respondents:,}")  # Formatting

# --- Visualization Section ---
st.subheader("📊 Select Chart type")
chart_type = st.selectbox(
    "Select Visualization Type",
    options=["Bar", "Pie"],
    label_visibility="visible",
)

if chart_type == "Bar":
    fig = px.bar(
        category_counts,
        x="Factor",
        y="Count",
        color="Category",
        text=category_counts["Count"].astype(str),
        title="Mental Health Factors: Low vs High Across All Countries",
        color_discrete_map={"Low": "#1f77b4", "High": "#ff7f0e"},
        barmode="group",
    )
    max_count = category_counts["Count"].max()
    y_axis_max = max_count * 1.2
    fig.update_traces(
        textposition="auto",
        hovertemplate="<b>%{x}</b><br>Category: %{customdata}<br>Count: %{y}<extra></extra>",
        customdata=category_counts["Category"],
    )
    fig.update_layout(
        autosize=False,
        width=1000,
        height=500,
        xaxis_title="Mental Health Factors",
        yaxis_title="Number of Responses",
        yaxis=dict(range=[0, y_axis_max]),
        margin=dict(l=40, r=40, t=40, b=40),
        legend_title_text="Category",
    )

elif chart_type == "Pie":
    fig = px.pie(
        category_counts,
        values="Count",
        names="Category",
        facet_col="Factor",
        title="Distribution of Mental Health Factors",
        color_discrete_map={"Low": "#1f77b4", "High": "#ff7f0e"},
        hole=0.3,
    )
    fig.update_layout(
        width=1200,
        height=400,
        margin=dict(l=40, r=40, t=40, b=40),
        showlegend=True,
    )

st.plotly_chart(fig, use_container_width=True)

# --- Interactive Mental Health Tip ---
st.subheader("🌟 Daily Mental Health Boost")
with st.expander("✨ Try This Simple Trick", expanded=False):
    st.markdown("""
    🌬️ Take 5 minutes to breathe deeply—inhale for 4 seconds, hold for 4, exhale for 4. It’s a mini-vacation for your brain! 🧠  
    This is called **box breathing** 📦, a technique used by pros to calm the mind. Pair it with a quick stretch 🙆—reach for the sky, then touch your toes—for an extra boost!
    """)
    col1, col2 = st.columns(2)
    with col1:
        if st.button("🌬️ Try It Now"):
            st.success("Feel better? Do it anytime!")
    with col2:
        if st.button("❓ Why It Works"):
            st.info("Deep breathing resets your nervous system—science says so!")
    
    # Radio button for feedback
    feedback = st.radio("👍 Did it help?", options=["✅ Yes", "❌ No"], index=None, key="feedback")
    if feedback == "✅ Yes":
        st.write("😊 Glad to hear it! Keep breathing easy! 🌬️")
    elif feedback == "❌ No":
        st.write("😌 No worries—try again tomorrow! 🌞")