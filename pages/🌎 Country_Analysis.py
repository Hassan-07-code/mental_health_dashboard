import streamlit as st
import pandas as pd
import plotly.express as px
from utils.data_loader import load_data  # Assuming this exists in your project

# --- Page Config ---
st.set_page_config(page_title="Country-Based Mental Health Analysis", layout="wide")

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

# --- Sidebar Filters ---
st.sidebar.header("🛠️ Analysis Filters")
all_countries = sorted(df["country"].unique())
selected_countries = st.sidebar.multiselect(
    "🌎 Select Countries",
    options=["All Countries"] + all_countries,
    default=["United States", "Canada"],
    help="Choose one or more countries, or select 'All Countries' to analyze everything."
)
if "All Countries" in selected_countries:
    selected_countries = all_countries  # Select all if "All Countries" is picked

selected_factor = st.sidebar.selectbox(
    "🧠 Select Mental Health Factor",
    options=stress_related_columns,
    help="Pick a factor to compare across countries."
)
chart_type = st.sidebar.selectbox(
    "📊 Select Chart Type",
    options=["Bar", "Pie"],  # Removed "Stacked Bar" and "Line"
    help="Choose how to visualize the data."
)

# --- Main Interface ---
st.title("🌍 Country-Based Mental Health Analysis")
st.markdown("Explore mental health trends across countries with interactive visualizations.")

# --- Filter Data ---
df_selected = df[df["country"].isin(selected_countries)].copy()

# --- Check if Data Exists ---
if selected_countries and df_selected[selected_factor].notna().sum() > 0:
    # Normalize and categorize
    min_val = df_selected[selected_factor].min()
    max_val = df_selected[selected_factor].max()
    if min_val != max_val:
        df_selected["scaled_value"] = (df_selected[selected_factor] - min_val) / (max_val - min_val)
    else:
        df_selected["scaled_value"] = 0
    df_selected["category"] = df_selected["scaled_value"].apply(lambda x: "High" if x > 0.5 else "Low")
    category_counts = df_selected.groupby(["country", "category"]).size().reset_index(name="Count")

    # --- Key Statistics ---
    st.subheader("📌 Key Statistics")
    col1, col2, col3 = st.columns(3)
    with col1:
        total_responses = df_selected[selected_factor].notna().sum()
        st.metric("Total Responses", f"{total_responses:,}")
    with col2:
        if "gender" in df_selected.columns:
            male_responses = df_selected[df_selected["gender"].str.lower() == "male"][selected_factor].notna().sum()
            st.metric("Male Responses", f"{male_responses:,}")
        else:
            st.write("Gender data not available")
    with col3:
        if "gender" in df_selected.columns:
            female_responses = df_selected[df_selected["gender"].str.lower() == "female"][selected_factor].notna().sum()
            st.metric("Female Responses", f"{female_responses:,}")
        else:
            st.write("")

    # --- Chart Section ---
    st.subheader(f"📊 {selected_factor.replace('_', ' ').title()} Comparison")
    num_countries = len(selected_countries)
    fig_width = min(max(600, num_countries * 200), 1400)
    fig_height = min(max(400, num_countries * 50), 600)

    if chart_type == "Bar":
        fig = px.bar(
            category_counts,
            x="country",
            y="Count",
            color="category",
            text=category_counts["Count"].astype(str),
            title=f"{selected_factor.replace('_', ' ').title()} (Low vs High)",
            color_discrete_map={"Low": "#1f77b4", "High": "#ff7f0e"},
            barmode="group",
        )
    elif chart_type == "Pie":
        fig = px.pie(
            category_counts,
            values="Count",
            names="category",
            title=f"{selected_factor.replace('_', ' ').title()} Distribution",
            color_discrete_map={"Low": "#1f77b4", "High": "#ff7f0e"},
            hole=0.3,
        )

    max_count = category_counts["Count"].max()
    y_axis_max = max_count * 1.2
    fig.update_traces(
        textposition="auto",
        hovertemplate="<b>%{x}</b><br>Category: %{customdata}<br>Count: %{y}<extra></extra>",
        customdata=category_counts["category"],
        textfont=dict(size=16, color="white") if chart_type == "Bar" else None,
    )
    fig.update_layout(
        autosize=False,
        width=fig_width,
        height=fig_height,
        xaxis_title="",
        yaxis_title="Number of People",
        yaxis=dict(range=[0, y_axis_max]) if chart_type == "Bar" else None,
        xaxis=dict(
            # tickmode="array",
            tickvals=selected_countries,  # Only selected countries
            ticktext=selected_countries,  # Show selected country names
            tickangle=-45,  # Rotate for readability
        ) if chart_type == "Bar" else None,
        margin=dict(l=40, r=40, t=40, b=40),
        legend_title_text="Category",
        bargap=0.2 if chart_type == "Bar" else None,  # Space between bars
    )

    st.plotly_chart(fig, use_container_width=True)

elif not selected_countries:
    st.info("Please select at least one country to display the analysis.")
else:
    st.warning(f"⚠️ No valid data found for '{selected_factor}' in the selected countries.")