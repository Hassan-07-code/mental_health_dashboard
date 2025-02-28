# 📊 Mental Health Dashboard

This is an interactive **Streamlit Dashboard** that visualizes trends in **mental health** based on a survey dataset.

## 🌟 Features
- **Overview**: General statistics on mental health trends.
- **Country Analysis**: Mental health trends across different countries.
- **Occupation Analysis**: Impact of occupation on mental health.
- **Visualizations**: Bar charts, heatmaps, and more.

## 📂 Project Structure
📂 mental_health_dashboard/
│── 📂 **data/** # Folder for datasets
│ ├── mental_health_cleaned.csv # Cleaned dataset
│── 📂 **pages/** # Folder for separate pages
│ ├── overview.py # General overview page
│ ├── country_analysis.py # Country-wise mental health trends
│ ├── occupation_analysis.py # Trends by occupation
│── 📂 **utils/** # Folder for helper functions
│ ├── data_loader.py # Function to load datasets
│── **app.py** # Main Streamlit app file
│── requirements.txt # Python dependencies (optional)
│── README.md # Project documentation