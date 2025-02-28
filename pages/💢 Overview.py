import streamlit as st
import pandas as pd
import plotly.graph_objects as go
from utils.data_loader import load_data  

# --- Page Config ---
st.set_page_config(page_title="Mental Health Overview", layout="wide")

# --- Load Dataset ---
df = load_data()
if df is None:
    st.error("Failed to load data. Please check the data source.")
    st.stop()

# ✅ Convert column names to lowercase
df.columns = df.columns.str.lower()

# Define mental health columns
stress_related_columns = ["growing_stress", "coping_struggles", "changes_habits", "social_weakness"]

# --- Main Interface ---
st.title("🌍 Mental Health Overview")
st.markdown("A quick look at global mental health trends.")

    # --- Key Statistics ---
st.subheader("📊 Quick Stats")
with st.expander("View Details", expanded=True):
    col1, col2, col3 = st.columns(3)
    with col1:
        total_responses = df[stress_related_columns].notna().sum().sum()
        st.metric("📋 Total Responses", f"{total_responses:,}")
    with col2:
        unique_countries = len(df["country"].unique())
        st.metric("🌐 Countries", unique_countries)
    with col3:
        if "gender" in df.columns:
            total_gender = df["gender"].notna().sum()
            female_count = df["gender"].str.lower().value_counts().get("female", 0)
            male_count = df["gender"].str.lower().value_counts().get("male", 0)
            female_pct = (female_count / total_gender * 100) if total_gender > 0 else 0
            male_pct = (male_count / total_gender * 100) if total_gender > 0 else 0
            col3a, col3b = st.columns(2)  # Nested columns for side-by-side display
            with col3a:
                st.metric("👨 Male %", f"{male_pct:.1f}%")
            with col3b:
                st.metric("👩‍🦰 Female %", f"{female_pct:.1f}%")
        else:
            st.write("Gender data N/A")

# --- Mental Health Distribution (Pie Chart) ---
st.subheader("🧠 Mental Health Breakdown")
factor = st.selectbox("Select Factor", options=stress_related_columns, index=0)
if factor in df.columns:
    stress_counts = df[factor].value_counts(normalize=True) * 100  # Convert to percentage
    counts_raw = df[factor].value_counts()  # Raw counts for hover
    fig_pie = go.Figure(data=[go.Pie(
        labels=stress_counts.index.astype(str),
        values=stress_counts.values,
        marker=dict(colors=["#FF5733", "#337BFF", "#FFD700", "#FF00FF"]),
        hovertemplate="<b>%{label}</b><br>Percentage: %{percent}<br>Count: %{customdata}<extra></extra>",
        customdata=counts_raw.values,
    )])
    fig_pie.update_layout(
        title=f"{factor.replace('_', ' ').title()} Distribution",
        margin=dict(l=20, r=20, t=40, b=20),
    )
    st.plotly_chart(fig_pie, use_container_width=True)
    if st.button("🔄 Refresh", key="refresh_pie"):
        st.rerun()
else:
    st.warning(f"No data available for '{factor}'!")

# --- 🌍 3D Interactive Global Survey Map ---
st.subheader("🌍✨ Interactive Global Survey Map")
if "country" in df.columns and not df["country"].dropna().empty:
    country_counts = df["country"].value_counts().reset_index()
    country_counts.columns = ["country", "count"]

    # Interactive controls
    projection_type = st.selectbox(
        "Map Projection",
        options=["orthographic", "natural earth", "mercator"],
        index=0,
        key="projection"
    )
    color_intensity = st.slider(
        "Color Intensity",
        min_value=0.5,
        max_value=1.5,
        value=1.0,
        step=0.1,
        key="color_intensity"
    )

    fig_globe = go.Figure()
    fig_globe.add_trace(go.Choropleth(
        locations=country_counts["country"],
        locationmode="country names",
        z=country_counts["count"],
        colorscale="Viridis",  # Vibrant, gradient colorscale
        zmin=0,
        zmax=country_counts["count"].max() * color_intensity,  # Dynamic color range
        marker=dict(line=dict(color='black', width=0.5)),
        colorbar_title="Survey Count",
        hovertemplate="<b>%{location}</b><br>Surveys: %{z}<extra></extra>",
    ))

    fig_globe.update_layout(
        title="Global Distribution of Surveyed Countries",
        geo=dict(
            showcoastlines=True,
            projection_type=projection_type,  # Dynamic projection
            showland=True,
            landcolor="rgb(245, 245, 220)",  # Shinier land
            oceancolor="rgb(100, 150, 200)",  # Deeper ocean
            bgcolor="rgba(0,0,0,0)",
            showcountries=True,  # Show country borders
            countrycolor="gray",
        ),
        paper_bgcolor="rgb(30, 30, 40)",  # Slightly lighter dark background
        font_color="white",
        margin=dict(l=20, r=20, t=50, b=20),
        plot_bgcolor="rgba(0,0,0,0)",
        annotations=[dict(  # Subtle watermark effect
            text="Survey Glow",
            showarrow=False,
            xref="paper", yref="paper",
            x=0.95, y=0.05,
            opacity=0.3,
            font=dict(color="white", size=12),
        )],
    )

    # Add rotation toggle (simulated with a button)
    if st.button("🔄 Rotate View", key="rotate_globe"):
        st.session_state["rotate"] = not st.session_state.get("rotate", False)
    if st.session_state.get("rotate", False):
        fig_globe.update_layout(geo=dict(projection_rotation=dict(lon=90)))  # Simple rotation effect

    st.plotly_chart(fig_globe, use_container_width=True)
else:
    st.warning("🚨 No country data available in the dataset!")