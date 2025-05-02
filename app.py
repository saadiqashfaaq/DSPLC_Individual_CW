import streamlit as st
import pandas as pd
import plotly.express as px

# --- Settings ---
st.set_page_config(page_title="Sri Lanka Industrial Data", layout="wide")

# --- Load Data ---
@st.cache_data
def load_data(file_path):
    return pd.read_csv(file_path)

DATA_URL = 'processed_industry_data.csv'
df = load_data(DATA_URL)

# --- Navigation ---
page = st.sidebar.radio("Navigate", ["Introduction", "Dashboard"])

# --- Page: Introduction ---
if page == "Introduction":
    # Background image using HTML/CSS with transparency
    st.markdown(
        """
        <style>
        .intro-bg {
            background-image: url('https://i.pinimg.com/736x/80/72/7a/80727a88eed6332612b325b6ef8b437c.jpg');
            background-size: cover;
            background-repeat: no-repeat;
            background-position: center;
            padding: 5rem;
            border-radius: 10px;
            background-color: rgba(255, 255, 255, 0.85);
        }
        </style>
        <div class="intro-bg">
        <h1 style="color: #C9DFFF;">Welcome to the Sri Lanka Industrial Employement Data Explorer</h1>
        <p style="font-size: 18px; color: #ADD9E0;">
            This dashboard provides insights into Sri Lanka's industrial employment trends over time.
        </p>
        <h3>Features:</h3>
        <ul>
            <li>Time series analysis of employee growth</li>
            <li>Industry-level breakdowns and comparisons</li>
            <li>Employee distribution by category</li>
            <li>Filtering and data downloads</li>
            <li>Bubble chart insights of employee data</li>
        </ul>
        </div>
        """,
        unsafe_allow_html=True
    )

# --- Page: Dashboard ---
elif page == "Dashboard":
    st.title("Sri Lanka Industrial Data Dashboard")

    # --- Optional Data Exploration ---
    if st.sidebar.checkbox("Show Raw Data", value=False):
        st.subheader("Raw Data")
        st.dataframe(df)

    if st.sidebar.checkbox("Show Data Summary", value=False):
        st.subheader("Data Summary")
        st.write(df.describe())

    # --- Sidebar Filters ---
    st.sidebar.header("Filters")

    unique_years = sorted(df['Year'].unique())
    year_filter = st.sidebar.selectbox("Select Year", unique_years, index=len(unique_years) - 1)
    df_filtered_year = df[df['Year'] == year_filter]

    unique_industries = sorted(df['ISIC Rev 3'].unique())
    industry_filter = st.sidebar.selectbox("Select Industry", unique_industries)
    df_filtered_industry = df[df['ISIC Rev 3'] == industry_filter]

    selected_industries = st.sidebar.multiselect("Compare Industries", unique_industries, default=unique_industries[:5])
    df_filtered_industries = df[df['ISIC Rev 3'].isin(selected_industries)]

    # --- KPIs ---
    st.header("Key Performance Indicators")
    col1, col2, col3 = st.columns(3)

    with col1:
        total_value = df['Number of Employees'].sum()
        st.metric("Total Employees", f"{total_value:,.2f}")

    with col2:
        avg_value = df['Number of Employees'].mean()
        st.metric("Average Employees per Record", f"{avg_value:,.2f}")

    with col3:
        latest_year_value = df[df['Year'] == df['Year'].max()]['Number of Employees'].sum()
        st.metric(f"Total Employees in {df['Year'].max()}", f"{latest_year_value:,.2f}")

    # --- Visualizations ---
    st.header("Visualizations")
    tab1, tab2, tab3, tab4, tab5, tab6, tab7 = st.tabs([
        "Time Series", "Industry Comparison", "Distribution",
        "Filtered Data", "Area Chart", "Category Summary", "Bubble Chart"
    ])

    def create_year_plot(fig, x_axis_label="Year", y_axis_label="Number of Employees"):
        fig.update_layout(
            xaxis=dict(
                tickmode='array',
                tickvals=sorted(df['Year'].unique()),
                ticktext=[str(year) for year in sorted(df['Year'].unique())],
                title=x_axis_label
            ),
            yaxis_title=y_axis_label
        )
        return fig

    # --- Tab 1: Time Series ---
    with tab1:
        st.subheader("Total Employees Over Time")
        try:
            yearly_value = df.groupby('Year')['Number of Employees'].sum().reset_index()
            fig_line = px.line(yearly_value, x='Year', y='Number of Employees', title="Total Industrial Employees Over Time", markers=True)
            st.plotly_chart(create_year_plot(fig_line), use_container_width=True)
        except KeyError:
            st.error("Missing 'Year' or 'Number of Employees' column.")

    # --- Tab 2: Industry Comparison ---
    with tab2:
        st.subheader("Total Employees by Industry")
        try:
            industry_value = df.groupby('ISIC Rev 3')['Number of Employees'].sum().reset_index()
            fig_bar = px.bar(industry_value, x='ISIC Rev 3', y='Number of Employees', title="Total Employees by Industry")
            fig_bar.update_layout(xaxis_tickangle=-45)
            st.plotly_chart(fig_bar, use_container_width=True)
        except KeyError:
            st.error("Missing necessary columns.")

        st.subheader("Selected Industry Comparison")
        try:
            fig_bar_compare = px.bar(df_filtered_industries, x='ISIC Rev 3', y='Number of Employees', title="Selected Industry Employee Totals")
            fig_bar_compare.update_layout(xaxis_tickangle=-45)
            st.plotly_chart(fig_bar_compare, use_container_width=True)
        except KeyError:
            st.error("Please select valid industries.")

    # --- Tab 3: Pie Chart Distribution ---
    with tab3:
        st.subheader("Employee Distribution by Industry Category")
        selected_types_pie = st.multiselect("Select Industry Category for Pie Chart", df['Industry_Category'].unique(), default=df['Industry_Category'].unique())
        try:
            type_value_pie = df[df['Industry_Category'].isin(selected_types_pie)].groupby('Industry_Category')['Number of Employees'].sum().reset_index()
            fig_pie = px.pie(type_value_pie, values='Number of Employees', names='Industry_Category', title="Employee Distribution by Industry Category")
            st.plotly_chart(fig_pie, use_container_width=True)
        except KeyError:
            st.error("Ensure the 'Industry_Category' and 'Number of Employees' columns exist.")

    # --- Tab 4: Filtered Data ---
    with tab4:
        st.subheader(f"Data for Year: {year_filter}")
        st.dataframe(df_filtered_year)

        st.subheader(f"Data for Industry: {industry_filter}")
        st.dataframe(df_filtered_industry)

        csv = df_filtered_year.to_csv(index=False).encode('utf-8')
        st.download_button("Download Filtered Year Data", data=csv, file_name="filtered_year_data.csv", mime='text/csv')

    # --- Tab 5: Area Chart ---
    with tab5:
        st.subheader("Cumulative Employees Over Time")
        try:
            cumulative_value = df.groupby('Year')['Number of Employees'].sum().cumsum().reset_index()
            fig_area = px.area(cumulative_value, x='Year', y='Number of Employees', title="Cumulative Total of Employees")
            st.plotly_chart(create_year_plot(fig_area), use_container_width=True)
        except KeyError:
            st.error("Check column names.")

    # --- Tab 6: Industry Category Summary ---
    with tab6:
        st.subheader("Employee Totals by Industry Category")
        try:
            category_value = df.groupby('Industry_Category')['Number of Employees'].sum().reset_index()
            fig_category = px.bar(category_value, x='Industry_Category', y='Number of Employees', title="Employees by Industry Category")
            fig_category.update_layout(xaxis_tickangle=-30)
            st.plotly_chart(fig_category, use_container_width=True)
        except KeyError:
            st.error("Missing 'Industry_Category' or 'Number of Employees'.")

    # --- Tab 7: Bubble Chart ---
    with tab7:
        st.subheader("Industry Bubble Chart")
        bubble_size_column = "Number of Employees"

        try:
            df_bubble = df.copy()
            fig_bubble = px.scatter(
                df_bubble,
                x="Year",
                y="Number of Employees",
                size=bubble_size_column,
                color="Industry_Category",
                hover_name="ISIC Rev 3",
                title="Industry Overview Bubble Chart",
                size_max=60
            )
            fig_bubble = create_year_plot(fig_bubble)
            st.plotly_chart(fig_bubble, use_container_width=True)
        except KeyError as e:
            st.error(f"Missing column: {e}")