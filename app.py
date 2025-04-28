import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import plotly.express as px  # For interactive plots

# --- Settings ---
st.set_page_config(page_title="Sri Lanka Industrial Data", page_icon="📈", layout="wide")

# --- Load Data ---
@st.cache_data  # Cache data for performance
def load_data(file_path):
    df = pd.read_csv(file_path)
    return df

DATA_URL = 'UNdata_Export_20250422_215048149.csv'  # Replace with your data file path
df = load_data(DATA_URL)

# --- Data Exploration ---
if st.sidebar.checkbox("Show Raw Data", value=False):
    st.subheader("Raw Data")
    st.dataframe(df)

if st.sidebar.checkbox("Show Data Summary", value=False):
    st.subheader("Data Summary")
    st.write(df.describe())

# --- Sidebar Filters ---
st.sidebar.header("Filters")

# Year Filter
unique_years = sorted(df['Year'].unique())
year_filter = st.sidebar.selectbox("Select Year", unique_years, index=len(unique_years) - 1)  # Default to latest year
df_filtered_year = df[df['Year'] == year_filter]

# ISIC Rev 3 Filter
unique_industries = sorted(df['ISIC Rev 3'].unique())
industry_filter = st.sidebar.selectbox("Select Industry", unique_industries, index=0)  # Default to first industry
df_filtered_industry = df[df['ISIC Rev 3'] == industry_filter]

# Industry Comparison Filter
selected_industries = st.sidebar.multiselect("Compare Industries", unique_industries, default=unique_industries[:5])
df_filtered_industries = df[df['ISIC Rev 3'].isin(selected_industries)]

# --- Main Content ---
st.title("Sri Lanka Industrial Data Dashboard")

# --- KPIs ---
st.header("Key Performance Indicators")
col1, col2, col3 = st.columns(3)

with col1:
    total_value = df['Value'].sum()
    st.metric("Total Value of employees", f"{total_value:,.2f}")

with col2:
    avg_value = df['Value'].mean()
    st.metric("Average Value of employees", f"{avg_value:,.2f}")

with col3:
    latest_year_value = df[df['Year'] == df['Year'].max()]['Value'].sum()
    st.metric(f"Total Value of employees ({df['Year'].max()})", f"{latest_year_value:,.2f}")

# --- Visualizations ---
st.header("Visualizations")

# --- Layout with Tabs ---
tab1, tab2, tab3, tab4, tab5, tab6 = st.tabs(
    ["Time Series", "Industry Comparison", "Value Distribution", "Filtered Data", "Scatter Plot", "Area Chart"])  # Added two tabs

with tab1:
    st.subheader("Total Value of Employees Over Time")
    try:
        # Group data by year and sum the 'Value'
        yearly_value = df.groupby('Year')['Value'].sum().reset_index()

        fig_line = px.line(yearly_value, x='Year', y='Value',
                          title="Total Industrial Value of employees Over Time",
                          labels={'Year': 'Year', 'Value': 'Total Value'},
                          markers=True)  # Added markers for better readability
        st.plotly_chart(fig_line, use_container_width=True)
    except KeyError:
        st.error("Make sure your data has 'Year' and 'Value' columns.")

with tab2:
    st.subheader("Value by Industry (Bar Chart)")
    try:
        # Group data by Industry and sum the 'Value'
        industry_value = df.groupby('ISIC Rev 3')['Value'].sum().reset_index()

        fig_bar = px.bar(industry_value, x='ISIC Rev 3', y='Value',
                          title="Total Value of employees Added by Industry",
                          labels={'ISIC Rev 3': 'Industry', 'Value': 'Total Value'})
        fig_bar.update_layout(xaxis_tickangle=-45)  # Rotate x-axis labels
        st.plotly_chart(fig_bar, use_container_width=True)
    except KeyError:
        st.error("Make sure your data has 'ISIC Rev 3' and 'Value' columns.")

    st.subheader("Industry Comparison (Multi-Select)")
    try:
        fig_bar_compare = px.bar(df_filtered_industries, x='ISIC Rev 3', y='Value',
                                  title="Value Comparison for Selected Industries",
                                  labels={'ISIC Rev 3': 'Industry', 'Value': 'Total Value'})
        fig_bar_compare.update_layout(xaxis_tickangle=-45)
        st.plotly_chart(fig_bar_compare, use_container_width=True)
    except KeyError:
        st.error("Select industries to compare.")

with tab3:
    st.subheader("Employee Distribution by Industry (Pie Chart)")
    try:
        industry_value_pie = df.groupby('ISIC Rev 3')['Value'].sum().reset_index()
        fig_pie = px.pie(industry_value_pie, values='Value', names='ISIC Rev 3', title="Value Distribution by Industry")
        st.plotly_chart(fig_pie, use_container_width=True)
    except KeyError:
        st.error("Make sure your data has 'ISIC Rev 3' and 'Value' columns.")

with tab4:
    st.subheader(f"Data for Year: {year_filter}")
    st.dataframe(df_filtered_year)

    st.subheader(f"Data for Industry: {industry_filter}")
    st.dataframe(df_filtered_industry)

with tab5:  # Scatter Plot
    st.subheader("Scatter Plot of Value vs. Year")
    try:
        fig_scatter = px.scatter(df, x='Year', y='Value',
                                  title="Value vs. Year",
                                  labels={'Year': 'Year', 'Value': 'Value'})
        st.plotly_chart(fig_scatter, use_container_width=True)
    except KeyError:
        st.error("Make sure your data has 'Year' and 'Value' columns.")

with tab6:  # Area Chart
    st.subheader("Cumulative Value Over Time")
    try:
        # Group by year and calculate cumulative value
        cumulative_value = df.groupby('Year')['Value'].sum().cumsum().reset_index()
        fig_area = px.area(cumulative_value, x='Year', y='Value',
                            title="Cumulative Value Over Time",
                            labels={'Year': 'Year', 'Value': 'Cumulative Value'})
        st.plotly_chart(fig_area, use_container_width=True)
    except KeyError:
        st.error("Make sure your data has 'Year' and 'Value' columns.")

# --- Further Enhancements ---
# Add more visualizations as needed (e.g., scatter plots, area charts)
# Implement more advanced filtering (e.g., filtering by value ranges)
# Add a download button for the filtered data
# Improve the styling with CSS or Streamlit's theming options
# Add error handling and user feedback