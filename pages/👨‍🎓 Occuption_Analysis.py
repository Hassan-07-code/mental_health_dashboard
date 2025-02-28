import streamlit as st
import pandas as pd
import plotly.express as px
from utils.data_loader import load_data  

# --- Page Config ---
st.set_page_config(page_title="Occupation-Based Mental Health Analysis", layout="wide")

# --- Load Dataset ---
df = load_data()
if df is None:
    st.error("Failed to load data. Please check the data source.")
    st.stop()

df.columns = df.columns.str.lower()

# --- Categorical Mappings ---
conversion_dict = {
    "No": 0, "Yes": 1,
    "Rarely": 1, "Sometimes": 2, "Often": 3, "Always": 4,
    "1-14 days": 7, "15-30 days": 22, "More than 30 days": 35,
    "Go out Every day": 0, "More than 2 months": 60,
}

# --- Mental Health Factors ---
mental_health_factors = ["growing_stress", "changes_habits", "mental_health_history", "coping_struggles", "work_interest", "social_weakness"]
factor_labels = {col: col.replace('_', ' ').title() for col in mental_health_factors}

# Apply conversion to numeric
for col in mental_health_factors:
    if col in df.columns:
        df[col] = df[col].replace(conversion_dict)
        df[col] = pd.to_numeric(df[col], errors='coerce')

# --- Main Interface ---
st.title("🏢 Occupation-Based Mental Health Analysis")
st.markdown("Explore mental health trends across occupations.")

# --- Sidebar Filters ---
st.sidebar.header("🛠️ Filters")
all_occupations = sorted(df["occupation"].dropna().unique())
selected_occupations = st.sidebar.multiselect(
    "🏢 Occupations",
    options=all_occupations,
    default=["Corporate", "Student"] if "Corporate" in all_occupations else all_occupations[:2],
    help="Choose occupations to analyze."
)

selected_factor = st.sidebar.selectbox(
    "🧠 Factor",
    options=[factor_labels[col] for col in mental_health_factors],
    help="Pick a mental health factor."
)
selected_factor_col = [col for col, label in factor_labels.items() if label == selected_factor][0]

chart_type = st.sidebar.selectbox(
    "📊 Chart",
    options=["Bar", "Pie"],
    help="Select chart type."
)
gender_filter = st.sidebar.selectbox(
    "👤 Gender",
    options=["All", "Male", "Female"],
    index=0,
    help="Filter by gender (if available)."
) if "gender" in df.columns else "All"

# --- Filter Data ---
df_filtered = df[df["occupation"].isin(selected_occupations)].copy()
female_only_occupations = ["housewife"]  # Define female-specific occupations

# Only show the message if ONLY housewife is selected and gender is Male
if len(selected_occupations) == 1 and selected_occupations[0].lower() in female_only_occupations and gender_filter.lower() == "male":
    st.subheader("Bhai, ye kya scene hai? 🤣")
    st.subheader("'Housewife' aur Mard? Bhai, ghar sambhalna hai ya WWE larni hai? 😂")
    st.stop()

# Filter data correctly - handle gender-specific occupations
if "gender" in df.columns:
    # Create a mask for each row to determine if it should be included
    include_mask = pd.Series(True, index=df_filtered.index)
    
    # For 'housewife' rows, they should only be female
    if any(occ.lower() in female_only_occupations for occ in selected_occupations):
        housewife_mask = df_filtered["occupation"].str.lower().isin(female_only_occupations)
        gender_mismatch_mask = housewife_mask & (df_filtered["gender"].str.lower() != "female")
        include_mask = include_mask & (~gender_mismatch_mask)
    
    # Apply general gender filter if selected
    if gender_filter.lower() != "all":
        gender_mask = df_filtered["gender"].str.lower() == gender_filter.lower()
        include_mask = include_mask & gender_mask
    
    # Apply the combined mask
    df_filtered = df_filtered[include_mask]

# --- Check if Data Exists ---
if not selected_occupations:
    st.info("Please select at least one occupation.")
elif df_filtered[selected_factor_col].notna().sum() > 0:
    # Categorize
    min_val = df_filtered[selected_factor_col].min()
    max_val = df_filtered[selected_factor_col].max()
    if min_val != max_val:
        df_filtered["scaled_value"] = (df_filtered[selected_factor_col] - min_val) / (max_val - min_val)
    else:
        df_filtered["scaled_value"] = 0
    df_filtered["category"] = df_filtered["scaled_value"].apply(lambda x: "High" if x > 0.5 else "Low")
    category_counts = df_filtered.groupby(["occupation", "category"]).size().reset_index(name="Count")

    # --- Key Statistics ---
    st.subheader("📌 Stats")
    col1, col2, col3 = st.columns(3)
    with col1:
        total_responses = df_filtered[selected_factor_col].notna().sum()
        st.metric("Responses", f"{total_responses:,}")
    with col2:
        if "gender" in df_filtered.columns:
            male_responses = df_filtered[df_filtered["gender"].str.lower() == "male"][selected_factor_col].notna().sum()
            st.metric("Male", f"{male_responses:,}" if gender_filter in ["All", "Male"] else "0")
        else:
            st.write("No gender data")
    with col3:
        if "gender" in df_filtered.columns:
            female_responses = df_filtered[df_filtered["gender"].str.lower() == "female"][selected_factor_col].notna().sum()
            st.metric("Female", f"{female_responses:,}" if gender_filter in ["All", "Female"] else "0")
        else:
            st.write("")

    # --- Chart Section ---
    st.subheader(f"📊 {selected_factor}")
    num_occupations = len(category_counts["occupation"].unique())
    fig_width = min(max(600, num_occupations * 200), 1200)
    fig_height = min(max(400, num_occupations * 50), 600)

    if chart_type == "Bar":
        fig = px.bar(
            category_counts,
            x="occupation",
            y="Count",
            color="category",
            text=category_counts["Count"].astype(str),
            title=f"{selected_factor} (Low vs High)",
            color_discrete_map={"Low": "#1f77b4", "High": "#ff7f0e"},
            barmode="group",
        )
    elif chart_type == "Pie":
        fig = px.pie(
            category_counts,
            values="Count",
            names="category",
            title=f"{selected_factor} Distribution",
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
        yaxis_title="Responses",
        yaxis=dict(range=[0, y_axis_max]) if chart_type == "Bar" else None,
        xaxis=dict(
            tickvals=category_counts["occupation"].unique(),
            ticktext=category_counts["occupation"].unique(),
            tickangle=-45,
        ) if chart_type == "Bar" else None,
        margin=dict(l=40, r=40, t=40, b=40),
        legend_title_text="",
        bargap=0.2 if chart_type == "Bar" else None,
    )
    st.plotly_chart(fig, use_container_width=True)
else:
    st.warning(f"No data found for '{selected_factor}' in selected occupations.")