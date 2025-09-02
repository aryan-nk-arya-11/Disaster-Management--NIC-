import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
from PIL import Image
import base64
from io import BytesIO
from datetime import datetime, timedelta
import time

def run():
    import pandas as pd  
    from datetime import datetime, timedelta 
    try:
        from streamlit_plotly_events import plotly_events
        PLOTLY_EVENTS_AVAILABLE = True
    except ImportError:
        PLOTLY_EVENTS_AVAILABLE = False

    # Page Configuration is being handled by main.py

    st.markdown("""
<style>
    @keyframes fadeIn {
        0% { opacity: 0; transform: translateY(15px) scale(0.98); }
        100% { opacity: 1; transform: translateY(0) scale(1); }
    }
    body, .stApp {
        font-family: "IBM Plex Sans", sans-serif !important;
        font-size: 0.95rem;
        background-color: #F4F4F4;
    }

    .main .block-container {
        padding-top: 0.5rem !important;
        padding-bottom: 0.5rem !important;
        max-width: 100% !important;
    }

    .stColumn > div {
        padding: 0.2rem !important;
    }

    .element-container {
        margin-bottom: 0.3rem !important;
    }

    .stMarkdown {
        margin-bottom: 0.2rem !important;
    }

    div[data-testid="stPlotlyChart"] {
        margin-bottom: 0.5rem !important;
    }

    .dashboard-header {
        background-color: #004C99; color: #FFFFFF;
        padding: 0.3375rem 1.0125rem; text-align: left; display: flex;
        align-items: center; border-bottom: 2.025px solid #ffc107;
        border-radius: 5.4px;
        box-shadow: 0 1.35px 2.7px rgba(0,0,0,0.1);
        margin-bottom: 0.675rem;
        margin-left: -1rem; 
        margin-right: -1rem; 
        margin-top: -1rem; 
    }
    .dashboard-header .header-logo-img { height: 20.25px; margin-right: 10.125px; }
    .dashboard-header .header-title-block { flex-grow: 1; }
    .dashboard-header h1 {
        font-size: 1.0125rem; margin: 0 0 0.0675rem 0;
        line-height: 0.81; color: #FFFFFF;
    }
    .dashboard-header p.tagline { font-size: 0.54rem; margin: 0; color: #e0e0e0; opacity: 0.9; }

    .dashboard-divider-full {
        border: none !important;
        height: 2px !important;
        background: linear-gradient(90deg, #0F62FE 0%, #4589FF 100%) !important;
        margin-top: 8px !important;
        margin-bottom: 16px !important;
        width: 100% !important;
        margin-left: -1rem !important;
        margin-right: -1rem !important;
        border-radius: 2px !important;
        box-shadow: 0 2px 4px rgba(15, 98, 254, 0.3) !important; 
        z-index: 10 !important;
        display: block !important;
    }

    .dashboard-divider {
        border: none !important;
        height: 2px !important;
        background: linear-gradient(90deg, #0F62FE 0%, #4589FF 100%) !important;
        margin-top: 12px !important;  
        margin-bottom: 16px !important;  
        width: 100% !important;
        border-radius: 1px !important;
        box-shadow: 0 1px 3px rgba(15, 98, 254, 0.2) !important;
        display: block !important;
    }

    hr.dashboard-divider-full,
    hr.dashboard-divider {
        opacity: 1 !important;
        visibility: visible !important;
    }

    div[data-testid="stPlotlyChart"]:has(.js-plotly-plot[data-unformatted*="Daily Deaths"]) {
        width: 500px !important;
        max-width: 500px !important;
        min-width: 500px !important;
    }

    div[data-testid="stPlotlyChart"]:has(.js-plotly-plot[data-unformatted*="daily_deaths_chart"]) {
        width: 500px !important;
        max-width: 500px !important;
        min-width: 500px !important;
    }

    .daily-deaths-chart-container {
        width: 500px !important;
        max-width: 500px !important;
        min-width: 500px !important;
        margin: 10px 0;
    }

    .daily-deaths-chart-container .stElementContainer,
    .daily-deaths-chart-container .element-container,
    .daily-deaths-chart-container div[data-testid="stPlotlyChart"] {
        width: 500px !important;
        max-width: 500px !important;
        min-width: 500px !important;
    }

    h3 {
        font-size: 1.2em !important;
        margin-bottom: 10px !important;
        margin-top: 20px !important;
        color: #161616;
        border-bottom: 2px solid #0F62FE;
        padding-bottom: 5px;
    }

    .section-title {
        font-size: 0.9em !important;
        margin-bottom: 3px !important;
        margin-top: 2px !important;
        color: #161616;
        border-bottom: none !important;
        padding-bottom: 0 !important;
        text-align: left !important;
    }


    .stTabs [data-baseweb="tab-panel"] h3 {
        margin-top: 10px !important;
    }
    h6 {
        font-size: 0.9em !important;
        color: #525252;
        text-align: center;
        margin-bottom: 5px;
        margin-top: 5px;
    }
    .stButton>button {
        border-radius: 4px;
        padding: 8px 15px;
        border: 1px solid #0F62FE;
        background-color: #FFFFFF;
        color: #0F62FE;
        transition: all 0.3s ease;
    }
    .stButton>button:hover {
        background-color: #0F62FE;
        color: #FFFFFF;
        border: 1px solid #0043CE;
    }
    .stButton>button:active {
        background-color: #0031A1 !important;
        color: #FFFFFF !important;
    }


    .casualty-kpi-card:hover {
        transform: scale(1.03);
        box-shadow: 0 5px 15px rgba(15, 98, 254, 0.3);
        cursor: pointer;
    }
    .casualty-kpi-card.death-total {
        border-left-color: #DA1E28;
    }
    .casualty-kpi-card.death-total .value {
        color: #DA1E28;
    }

    .gauge-overall-container {
        background-color: #FFFFFF;
        padding: 8px; 
        border-radius: 8px;
        box-shadow: 0 2px 5px rgba(0,0,0,0.1);
        margin-bottom: 15px;
        display: flex;
        align-items: stretch;
    }

    .gauge-container {
        background-color: #FFFFFF;
        padding: 3px; 
        border-radius: 8px;
        box_shadow: 0 2px 5px rgba(0,0,0,0.1);
        margin-bottom: 10px;
        animation: fadeIn 0.8s ease-out forwards;
        transition: transform 0.2s ease-in-out, box-shadow 0.2s ease-in-out, opacity 0.8s ease-out;
        display: flex;
        flex-direction: column;
        align-items: center;
        justify-content: center;
        text-align: center;
        width: 100%;
        box-sizing: border-box;
    }
    .gauge-container:hover {
        transform: translateY(-5px) scale(1.02);
        box-shadow: 0 6px 12px rgba(15, 98, 254, 0.25);
        cursor: default;
    }
    .gauge-container .stPlotlyChart {
        padding: 0 !important;
        margin: 0 !important;
        width: 100%;
        height: 100%;
        display: flex;
        justify-content: center;
        align-items: center;
    }
    .gauge-value {
        font-size: 1.4em;
        color: #161616;
        margin-top: 5px;
        text-align: center;
        width: 100%;
    }

    .st-emotion-cache-1l269bu {
        background-color: #FFFFFF;
        border-right: 1px solid #E0E0E0;
        box-shadow: 2px 0 5px rgba(0,0,0,0.05);
        padding-top: 1.5rem; 
        padding-left: 0.8rem; 
        padding-right: 0.8rem; 
    }
    .st-emotion-cache-1l269bu .stSelectbox, .st-emotion-cache-1l269bu .stDateInput {
        margin-bottom: 10px;
    }
    .sidebar-title {
        font-size: 1.2em;
        color: #0F62FE;
        margin-bottom: 15px;
        text-align: center;
    }
    button[data-baseweb="tab"] {
        font-size: 0.9em !important;
        padding: 8px 15px !important;
        font-family: "IBM Plex Sans", sans-serif !important;
    }
    [data-baseweb="tab-list"] {
        background-color: #F4F4F4 !important;
        padding-bottom: 0px !important;
        margin-bottom: 10px; 
    }

    .gauge-overall-container > div[data-testid="stHorizontalBlock"] {
        margin: 0 !important;
        padding: 0 !important;
        gap: 0px !important;
    }

    .gauge-overall-container div[data-testid="stColumn"] {
        padding-left: 0rem !important;
        padding-right: 0rem !important;
        padding-top: 0rem !important;
        padding-bottom: 0rem !important;
        margin: 0 !important;
        border-right: 1px solid #E0E0E0;
        box-sizing: border-box;
    }
    .gauge-overall-container div[data-testid="stColumn"]:last-child {
        border-right: none;
    }

    .gauge-overall-container div[data-testid="stColumn"] > div {
        padding: 0 ;
        margin: 0 ;
    }

    
    .incident-summary-wrapper-container div[data-testid="stHorizontalBlock"] {
        max-width: 100%; 
        padding: 0px ;
        margin: 0px ;
        gap: 2px ; 
        width: 100% ;
    }

    .incident-summary-wrapper-container div[data-testid="stColumn"] {
        padding: 0px 1px ; 
        margin: 0px ;
        display: flex;
        flex-direction: column; 
        align-items: center; 
        justify-content: flex-start;
        flex-grow: 1; 
    }

    .incident-death-card {
        background-color: #6777EF; 
        color: white;
        padding: 1px 6px;
        border-radius: 5px;
        text-align: center;
        margin: 2px 1px;
        height: 22px;
        display: flex;
        flex-direction: row;
        justify-content: space-between;
        align-items: center;
        border: 1px solid transparent; 

        box-shadow: 0 1px 4px rgba(103,119,239,0.10);
        width: 100%;
        max-width: 140px;
        white-space: nowrap;
        overflow: hidden;
        transition: background-color 0.3s ease, border-color 0.3s ease, box-shadow 0.15s, transform 0.12s;
        text-overflow: ellipsis;
        box-sizing: border-box;
        font-size: 0.85em;
    }
    .incident-death-card:hover {
        background-color: #3B5BDB; 
        border: 1px solid #000000; 
        box-shadow: 0 4px 12px rgba(0,0,0,0.25);
        transform: translateY(-2px) scale(1.03);
    }

    .incident-death-card.total-deaths-card {
        background-color: #FC403B; 
        border: 1px solid transparent;
        transition: background-color 0.3s ease, border-color 0.3s ease, box-shadow 0.15s, transform 0.12s;
        box-shadow: 0 1px 4px rgba(252,84,75,0.10);
    }
    .incident-death-card.total-deaths-card:hover {
        background-color: #DA1E28; 
        border: 1px solid #000000; 
        box-shadow: 0 4px 12px rgba(0,0,0,0.25);
        transform: translateY(-2px) scale(1.03);
    }

    .incident-death-card .incident-label {
        font-size: 0.8em;
        font-family: 'Segoe UI', 'Roboto', 'Arial', sans-serif;
        letter-spacing: 0.3px;
        text-rendering: optimizeLegibility;
        -webkit-font-smoothing: antialiased;
        -moz-osx-font-smoothing: grayscale;
        white-space: nowrap;
        overflow: hidden;
        text-overflow: ellipsis;
        flex-shrink: 1;
        margin-right: 3px;
        line-height: 1;
    }

    .incident-death-card .incident-value {
        font-size: 0.9em;
        font-family: 'Segoe UI', 'Roboto', 'Arial', sans-serif;
        letter-spacing: 0.4px;
        text-rendering: optimizeLegibility;
        -webkit-font-smoothing: antialiased;
        -moz-osx-font-smoothing: grayscale;
        flex-shrink: 0;
        white-space: nowrap;
        line-height: 1;
    }

    .st-emotion-cache-1f8u01d { 
        background-color: #F8FAFF;
        border-radius: 12px;
        border: 1.5px solid #E0E6F0;
        box-shadow: 0 2px 8px rgba(0,0,0,0.07);
        padding: 15px 8px 10px 8px;
        margin-bottom: 18px;
        display: flex;
        flex-wrap: wrap;
        justify-content: flex-start;
        align-items: flex-start;
        align-content: flex-start;
        gap: 0px;
        height: auto;
        max-height: 320px;
        overflow-y: auto;
        width: 100%;
        max-width: 100%; 
        margin-left: 0;
        margin-right: 0;
    }
    .incident-summary-wrapper-container > div {
        padding: 0 !important;
    }
    .incident-summary-wrapper-container .st-emotion-cache-1f8u01d {
        width: 100%;
    }

    .st-emotion-cache-1d8vwwt.e1lln2w84 {
        background-color: #F8FAFF;
        border-radius: 12px;
        border: 1.5px solid #E0E6F0;
        box-shadow: 0 2px 8px rgba(0,0,0,0.07);
        padding: 15px 8px 10px 8px;
        margin-bottom: 18px;
        display: flex;
        flex-wrap: wrap;
        justify-content: flex-start;
        align-items: flex-start;
        align-content: flex-start;
        gap: 0px;
        height: auto;
        max-height: 320px;
        overflow-y: auto;
        width: 320px !important; /* Reduced width for more compact container */
        max-width: 320px !important; /* Set maximum width */
        margin-left: 0;
        margin-right: 0;
    }

    .incident-summary-wrapper-container .stElementContainer.element-container.st-emotion-cache-17lr0tt.e1lln2w81 {
        width: 100% !important; /* Use full column width for professional alignment */
        max-width: 100% !important;
        margin-left: 0 !important;
        margin-right: 0 !important;
    }

    .incident-summary-wrapper-container div.st-emotion-cache-17lr0tt.e1lln2w81 {
        width: 100% !important;
        max-width: 100% !important;
        margin-left: 0 !important;
        margin-right: 0 !important;
    }



    .stPlotlyChart {
        background-color: transparent !important;
        box-shadow: none !important;
        border-radius: 0 !important;
        padding: 0 !important;
        margin-top: 0px !important;
        margin-bottom: 0px !important;
    }

    div[data-testid="column"] {
        vertical-align: top !important;
        align-items: flex-start !important;
    }

    div[data-testid="column"] > div {
        vertical-align: top !important;
        align-items: flex-start !important;
        display: flex !important;
        flex-direction: column !important;
        justify-content: flex-start !important;
    }

    .js-plotly-plot {
        margin-top: 0 !important;
        padding-top: 0 !important;
    }

    div[data-testid="column"] h6,
    div[data-testid="column"] h3 {
        margin-top: 0 !important;
        padding-top: 0 !important;
        margin-bottom: 10px !important;
    }

    div[data-testid="column"] .stMarkdown,
    div[data-testid="column"] .stContainer {
        margin-top: 0 !important;
        padding-top: 0 !important;
    }

    div[data-testid="stPlotlyChart"] {
        transition: none !important;
    }

    div[data-testid="stPlotlyChart"] > div {
        transition: none !important;
    }



    .js-plotly-plot .plotly {
        transition: none !important;
    }

    .footer-card { background-color: #343a40; color: #dee2e6; padding: 1rem; border-radius: 8px; margin-top: 1.5rem; text-align: center; box-shadow: 0 -1px 3px rgba(0,0,0,0.05); border-top: 1px solid var(--card-border-color); font-size: 0.8rem; box-sizing: border-box; }
    .footer-title { color: #ffc107 !important; font-size: 1rem !important; margin-bottom: 0.5rem !important; }
    .footer-card p { margin-bottom: 0.25rem; font-size: 0.75rem;}
</style>
<script>
document.addEventListener('DOMContentLoaded', function() {
    let resizeTimeout;

    // Function to trigger Plotly resize
    function resizePlotlyCharts() {
        const plotlyCharts = document.querySelectorAll('.js-plotly-plot');
        plotlyCharts.forEach(chart => {
            if (window.Plotly && chart._fullLayout) {
                window.Plotly.Plots.resize(chart);
            }
        });
    }

    // Monitor for sidebar state changes
    const observer = new MutationObserver(function(mutations) {
        mutations.forEach(function(mutation) {
            if (mutation.type === 'attributes' &&
                (mutation.attributeName === 'class' || mutation.attributeName === 'style')) {
                clearTimeout(resizeTimeout);
                resizeTimeout = setTimeout(resizePlotlyCharts, 100);
            }
        });
    });

    const sidebar = document.querySelector('[data-testid="stSidebar"]');
    if (sidebar) {
        observer.observe(sidebar, { attributes: true, subtree: true });
    }

    window.addEventListener('resize', function() {
        clearTimeout(resizeTimeout);
        resizeTimeout = setTimeout(resizePlotlyCharts, 100);
    });
});
</script>
    """, unsafe_allow_html=True)

    PRIMARY_COLOR = "#0F62FE"
    SECONDARY_COLOR = "#525252"
    DEATH_COLOR = "#DA1E28"
    INJURED_COLOR = "#FF8C00"
    INCIDENT_COLOR = PRIMARY_COLOR
    TEXT_COLOR = "#161616"
    GRID_COLOR = "#E0E0E0"
    AXIS_COLOR = "#C6C6C6"
    PLOTLY_TEMPLATE = "plotly_white"
    CHART_FONT = "IBM Plex Sans, sans-serif"

    # Image to base64 conversion function
    @st.cache_data
    def get_image_as_base64(path):
        try:
            with open(path, "rb") as image_file:
                encoded_string = base64.b64encode(image_file.read()).decode()
            image_type = path.split('.')[-1].lower()
            if image_type in ["jpg", "jpeg"]: return f"data:image/jpeg;base64,{encoded_string}"
            elif image_type == "png": return f"data:image/png;base64,{encoded_string}"
            else: return f"data:image/png;base64,{encoded_string}"
        except FileNotFoundError:
            st.warning(f"Image file not found at path: '{path}'. Please ensure it is in the correct directory.")
            return "data:image/gif;base64,R0lGODlhAQABAIAAAAAAAP///yH5BAEAAAAALAAAAAABAAEAAAIBRAA7"

    # Database Connection
    @st.cache_resource
    def init_db_connection():
        """Establishes a SQLAlchemy engine connection to the SQL Server database using Dashboard2.toml config."""
        try:
            from sqlalchemy import create_engine
            import os

            config_path = os.path.join(".streamlit", "Dashboard2.toml")
            if os.path.exists(config_path):
                # Reading the TOML file manually since it's simple
                config = {}
                with open(config_path, 'r') as f:
                    content = f.read()

                # Simple TOML parsing for our specific format
                for line in content.split('\n'):
                    if '=' in line and not line.strip().startswith('#'):
                        key, value = line.split('=', 1)
                        config[key.strip()] = value.strip().strip('"')

                # Extracting connection details from .toml file
                if 'url' in config:
                    # If using URL format from .toml
                    connection_url = config['url']
                else:
                    # If using separate parameters (fallback for different format)
                    server = config.get('db_server', 'localhost')
                    database = config.get('db_database', 'eoc')
                    connection_url = f"mssql+pyodbc://{server}/{database}?driver=ODBC+Driver+17+for+SQL+Server&trusted_connection=yes&TrustServerCertificate=yes"
            else:
                # Displaying error message when toml connection do not get established.
                st.error("Dashboard2.toml file not found in .streamlit folder. Please ensure the configuration file exists.")
                return None

            # Adding connection pooling for better performance
            engine = create_engine(
                connection_url,
                pool_size=5,
                max_overflow=10,
                pool_pre_ping=True,
                pool_recycle=3600
            )
            return engine
        except Exception as e:
            st.error(f"Database connection failed. Check `Dashboard2.toml` and ensure DB is running. Error: {e}")
            return None

    # Data Loading 
    @st.cache_data(ttl=1800)  # 30 minutes
    def load_data_from_db():
        try:
            engine = init_db_connection()
            if not engine:
                return pd.DataFrame()

            sql_query = """
            SELECT
                CAST(HR.IncidentDate AS DATE) AS date,
                TRIM(MD.DistrictName) AS district,
                TRIM(MB.BlockName) AS block,
                H.Name AS incident_type,
                COALESCE(SUM(CASE WHEN HLR.HLCode = 2 THEN 1 ELSE 0 END), 0) AS deaths, -- Corrected: HLCode = 2 for Deaths
                COALESCE(SUM(CASE WHEN HLR.HLCode = 1 THEN 1 ELSE 0 END), 0) AS injured, -- Corrected: HLCode = 1 for Injured
                CASE
                    WHEN HR.IsFinal = 1 THEN 'Final'
                    WHEN HR.IsFinal = 2 THEN 'Verified'
                    ELSE 'Unknown'
                END AS entry_type
            FROM
                dbo.HazardReport AS HR
            LEFT JOIN
                dbo.Hazards AS H ON HR.HazardCode = H.ID
            LEFT JOIN
                dbo.mst_Districts AS MD ON HR.DistrictCode = MD.DistrictCode
            LEFT JOIN
                dbo.mst_Blocks AS MB ON HR.BlockCode = MB.BlockCode AND HR.DistrictCode = MB.DistrictCode
            LEFT JOIN
                dbo.HumanLossReport AS HLR ON HR.ID = HLR.HzdReptID
            WHERE
                HR.IncidentDate >= DATEADD(YEAR, -5, GETDATE())  -- Last 5 years only for faster loading
            GROUP BY
                CAST(HR.IncidentDate AS DATE),
                TRIM(MD.DistrictName),
                TRIM(MB.BlockName),
                H.Name,
                HR.IsFinal
            ORDER BY
                CAST(HR.IncidentDate AS DATE);
            """

            df = pd.read_sql(sql_query, engine)

            if df.empty:
                return pd.DataFrame()

            df['date'] = pd.to_datetime(df['date'], format='%Y-%m-%d', errors='coerce')

            string_cols = ['district', 'block', 'incident_type', 'entry_type']
            df[string_cols] = df[string_cols].astype(str).apply(lambda x: x.str.strip().str.title())

            numeric_cols = ['deaths', 'injured']
            df[numeric_cols] = df[numeric_cols].apply(pd.to_numeric, errors='coerce').fillna(0).astype('int16')

            # Removing any duplicate rows
            df = df.drop_duplicates().reset_index(drop=True)

            return df

        except Exception as e:
            st.error(f"An error occurred while loading data: {e}. Please ensure:")
            st.error("- Your `.streamlit/Dashboard2.toml` file includes the correct server and database configuration.")
            st.error("- The database server is accessible and the ODBC Driver 17 for SQL Server is installed.")
            return pd.DataFrame()

    # Cache filtered data (to avoid repeated processing)
    @st.cache_data
    def get_filtered_data(df, start_date, end_date, district, entry_type, incident_type):
        """Cache filtered data based on filter selections"""
        df_filtered = df[(df['date'] >= start_date) & (df['date'] <= end_date)].copy()
        if district != 'All':
            df_filtered = df_filtered[df_filtered['district'] == district]
        if entry_type != 'All':
            df_filtered = df_filtered[df_filtered['entry_type'] == entry_type]
        if incident_type != 'All':
            df_filtered = df_filtered[df_filtered['incident_type'] == incident_type]

        # Applying incident type replacement
        if 'incident_type' in df_filtered.columns:
            df_filtered['incident_type'] = df_filtered['incident_type'].replace('Strong Wind (Andhi Toofan)', 'Strong Wind')

        return df_filtered

    with st.spinner('Presenting the Disaster Incident Dashboard for you... Thank you for your Patience'):
        df_main = load_data_from_db()
    if df_main.empty:
        st.error(" Unable to load incident data. Please check database connection and try again.")
        st.info(" Ensure your database server is running and accessible.")
        st.stop()

    # Main Page Header
    eoc_logo_header_base64 = get_image_as_base64("eoc_logo.png")
    header_logo_html = f'<img src="{eoc_logo_header_base64}" alt="EOC" class="header-logo-img">' if eoc_logo_header_base64 else ""
    st.markdown(f"""
        <div class="dashboard-header">
            {header_logo_html}
            <div class="header-title-block">
                <h1>Incident Dashboard</h1>
                <p class="tagline">Emergency Operations Center - Government of Bihar</p>
            </div>
        </div>
    """, unsafe_allow_html=True)

    min_date_data = df_main['date'].min().date()
    max_date_data = df_main['date'].max().date()

    default_start_date_filter = datetime(2021, 1, 1).date()
    default_end_date_filter = datetime(2025, 6, 30).date()

    if default_start_date_filter < min_date_data:
        default_start_date_filter = min_date_data
    if default_end_date_filter > max_date_data:
        default_end_date_filter = max_date_data

    col1, col2, col3, col4 = st.columns([1.2, 1, 1, 1])

    with col1:
        date_range_tuple_filter = st.date_input(
            "Select Date Range",
            value=(default_start_date_filter, default_end_date_filter),
            min_value=min_date_data,
            max_value=max_date_data,
            key="date_range_filter_sidebar"
        )

    with col2:
        selected_district = st.selectbox(
            "Select District",
            ['All'] + sorted(list(df_main['district'].unique())),
            key="district_filter_sidebar"
        )

    with col3:
        selected_entry_type = st.selectbox(
            "Select Entry Type",
            ['All'] + sorted(list(df_main['entry_type'].unique())),
            key="entry_type_filter_sidebar"
        )

    with col4:
        selected_incident_type = st.selectbox(
            "Select Incident Type",
            ['All'] + sorted(list(df_main['incident_type'].unique())),
            key="incident_type_filter_sidebar"
        )

    if len(date_range_tuple_filter) == 2:
        start_date, end_date = pd.to_datetime(date_range_tuple_filter[0]), pd.to_datetime(date_range_tuple_filter[1])
    else:
        start_date, end_date = pd.to_datetime(default_start_date_filter), pd.to_datetime(default_end_date_filter)
        st.warning("Please select a valid date range (start and end date).")

    if start_date > end_date:
        st.error("Error: Start date cannot be after end date. Please adjust the date range.")
        st.stop()

    # Use cached filtering (for better performance)
    df_filtered = get_filtered_data(df_main, start_date, end_date, selected_district, selected_entry_type, selected_incident_type)

    total_incidents = len(df_filtered)
    total_deaths = df_filtered['deaths'].sum() if 'deaths' in df_filtered else 0
    total_injured = df_filtered['injured'].sum() if 'injured' in df_filtered else 0

    @st.cache_data
    def create_plotly_gauge_figure(value, title_text, color, max_value):
        fig = go.Figure()
        fig.add_trace(go.Indicator(
            mode="gauge+number",
            value=value,
            number={
                'font': {'size': 24, 'family': CHART_FONT, 'color': color},  
                'valueformat': ',d',
            },
            title={
                'text': f'<span style="font-size:18px; color:{color}; text-decoration:underline; text-decoration-color:{color}; text-decoration-thickness:1px;">{title_text}</span>',
                'font': {'size': 18, 'family': CHART_FONT, 'color': color}  
            },
            gauge={
                'axis': {'range': [None, max_value], 'tickwidth': 1, 'tickcolor': "darkgray"},
                'bar': {'color': color, 'thickness': 0.75},
                'bgcolor': "white",
                'borderwidth': 1,
                'bordercolor': "#E0E0E0",
                'steps': [
                    {'range': [0, max_value * 0.5], 'color': "#F0F0F0"},
                    {'range': [max_value * 0.5, max_value], 'color': "#E0E0E0"}
                ]
            }
        ))

        fig.update_layout(
            height=140,  
            margin=dict(l=5, r=5, t=50, b=5),  
            paper_bgcolor='rgba(0,0,0,0)',
            plot_bgcolor='rgba(0,0,0,0)',
            font_family=CHART_FONT,
            font_color=TEXT_COLOR,
        )
        return fig

    INCIDENTS_GAUGE_MAX = max(10, total_incidents + int(total_incidents*0.25)) if total_incidents > 0 else 10
    DEATHS_GAUGE_MAX = max(10, total_deaths + int(total_deaths*0.5) + 5) if total_deaths > 0 else 10
    INJURED_GAUGE_MAX = max(10, total_injured + int(total_injured*0.5) + 5) if total_injured > 0 else 10

    gauge_key_base = f"{total_incidents}_{total_deaths}_{total_injured}_{start_date.strftime('%Y%m%d')}_{end_date.strftime('%Y%m%d')}_{selected_district}_{selected_entry_type}_{selected_incident_type}"

    with st.markdown('<div class="gauge-overall-container">', unsafe_allow_html=True):
        kpi_col1, kpi_col2, kpi_col3 = st.columns(3)

        with kpi_col1:
            fig_incidents = create_plotly_gauge_figure(total_incidents, "Incidents", INCIDENT_COLOR, INCIDENTS_GAUGE_MAX)
            st.plotly_chart(fig_incidents, use_container_width=True, config={'displayModeBar': False}, key=f"incidents_chart_{gauge_key_base}")
        with kpi_col2:
            fig_deaths = create_plotly_gauge_figure(total_deaths, "Deaths", DEATH_COLOR, DEATHS_GAUGE_MAX)
            st.plotly_chart(fig_deaths, use_container_width=True, config={'displayModeBar': False}, key=f"deaths_chart_{gauge_key_base}")
        with kpi_col3:
            fig_injured = create_plotly_gauge_figure(total_injured, "Injured", INJURED_COLOR, INJURED_GAUGE_MAX)
            st.plotly_chart(fig_injured, use_container_width=True, config={'displayModeBar': False}, key=f"injured_chart_{gauge_key_base}")



    st.markdown('<hr style="border: none; height: 1px; background: linear-gradient(90deg, #0F62FE 0%, #4589FF 100%); margin: 6px 0 8px 0; opacity: 0.7;">', unsafe_allow_html=True)
    def style_plotly_chart(fig, chart_height=280, is_pie_or_donut=False, legend_orientation="h"):
        fig.update_layout(
            template=PLOTLY_TEMPLATE,
            plot_bgcolor='rgba(0,0,0,0)',
            paper_bgcolor='rgba(0,0,0,0)',
            xaxis=dict(
                showgrid=False,
                linecolor=AXIS_COLOR,
                tickfont=dict(color=TEXT_COLOR, size=10),
                showline=True,
                zeroline=False
            ),
            yaxis=dict(
                showgrid=True,
                gridcolor=GRID_COLOR,
                linecolor=AXIS_COLOR,
                tickfont=dict(color=TEXT_COLOR, size=10),
                showline=False,
                zeroline=False,
                rangemode='tozero'
            ),
            hoverlabel=dict(bgcolor="#FFFFFF", font_size=11, font_family=CHART_FONT, bordercolor=AXIS_COLOR, font_color=TEXT_COLOR),
            legend=dict(orientation=legend_orientation, yanchor="bottom", y=1.02, xanchor="right", x=1, font=dict(family=CHART_FONT, color=TEXT_COLOR, size=10), bgcolor='rgba(0,0,0,0)'),
            margin=dict(l=20, r=10, t=30, b=30),  
            title_text='',
            title_font_family=CHART_FONT,
            title_font_color=TEXT_COLOR,
            font_color=TEXT_COLOR,
            font_family=CHART_FONT,
            height=chart_height
        )
        if not is_pie_or_donut:
            fig.update_layout(hovermode='x unified')
            fig.update_xaxes(title_text=None)
            fig.update_yaxes(title_text=None)
        else:
            fig.update_layout(hovermode='closest')
            fig.update_layout(
                xaxis=dict(visible=False, showgrid=False),
                yaxis=dict(visible=False, showgrid=False),
                margin=dict(l=5, r=5, t=25, b=5)
            )
        if fig.layout.title.text:
            fig.update_layout(title_x=0.5)
        return fig

    graph_col1, graph_col2, graph_col3 = st.columns([1, 1, 1], gap="small")  

    with graph_col1:
        st.markdown('<h3 class="section-title">Casualties</h3>', unsafe_allow_html=True)
        if not df_filtered.empty and 'deaths' in df_filtered.columns and 'incident_type' in df_filtered.columns:
            incident_deaths_summary = df_filtered[df_filtered['deaths'] > 0].groupby('incident_type')['deaths'].sum().sort_values(ascending=False).reset_index()

            st.markdown('<div class="incident-summary-wrapper-container">', unsafe_allow_html=True)
            incident_cards_container = st.container(border=True)

            with incident_cards_container:
                if not incident_deaths_summary.empty:

                    all_death_summary_items = incident_deaths_summary.to_dict('records')
                    all_death_summary_items.append({"incident_type": "Total Deaths", "deaths": total_deaths, "is_total": True})

                    cols = st.columns([1, 1])

                    left_column_items = [item for i, item in enumerate(all_death_summary_items) if i % 2 == 0]
                    right_column_items = [item for i, item in enumerate(all_death_summary_items) if i % 2 != 0]

                    with cols[0]:
                        for item in left_column_items:
                            card_class = "incident-death-card"
                            if item.get("is_total"):
                                card_class += " total-deaths-card"
                            st.markdown(f"""
                                <div class="{card_class}">
                                    <span class="incident-label">{item["incident_type"]} :</span>
                                    <span class="incident-value">{item["deaths"]:,}</span>
                                </div>
                            """, unsafe_allow_html=True)
                    with cols[1]:
                        for item in right_column_items:
                            card_class = "incident-death-card"
                            if item.get("is_total"):
                                card_class += " total-deaths-card"
                            st.markdown(f"""
                                <div class="{card_class}">
                                    <span class="incident-label">{item["incident_type"]} :</span>
                                    <span class="incident-value">{item["deaths"]:,}</span>
                                </div>
                            """, unsafe_allow_html=True)
                else:
                    incident_cards_container.markdown('<p style="text-align: center; color: #525252; padding-top: 50px;">No deaths by incident type for selected filters.</p>', unsafe_allow_html=True)
        else:
            st.info("Required columns for 'Casualties' (deaths, incident_type) are not available or no data in filtered set.")

    try:
        if not df_filtered.empty and 'deaths' in df_filtered.columns and 'date' in df_filtered.columns:
            selected_month = end_date.month
            selected_year = end_date.year

            month_data = df_filtered[
                (df_filtered['date'].dt.month == selected_month) &
                (df_filtered['date'].dt.year == selected_year)
            ].copy()

            if not month_data.empty and month_data['deaths'].sum() > 0:
                daily_deaths = month_data.groupby('date')['deaths'].sum().reset_index()
                daily_deaths = daily_deaths.sort_values('date')
            else:
                import pandas as pd
                start_of_month = datetime(selected_year, selected_month, 1)
                if selected_month == 12:
                    end_of_month = datetime(selected_year + 1, 1, 1) - timedelta(days=1)
                else:
                    end_of_month = datetime(selected_year, selected_month + 1, 1) - timedelta(days=1)

                # Creating date range for the month
                date_range = pd.date_range(start=start_of_month, end=end_of_month, freq='D')
                daily_deaths = pd.DataFrame({
                    'date': date_range,
                    'deaths': [0] * len(date_range)
                })

            # Creating line chart with smooth curves
            fig_daily_deaths = px.line(
                daily_deaths,
                x='date',
                y='deaths',
                title="Current Month",  
                labels={'date': 'Date', 'deaths': 'Number of Deaths'},
                color_discrete_sequence=['#3C6FF7'], 
                markers=True
            )

            fig_daily_deaths.update_traces(
                    mode='lines+markers',
                    line=dict(
                        width=3,
                        color='#3C6FF7',
                        shape='spline',
                        smoothing=0.3
                    ),
                    marker=dict(
                        size=8,
                        color='white', 
                        symbol='circle',
                        line=dict(color='#3C6FF7', width=2)  
                    ),
                    hovertemplate='%{x}<br>Deaths: %{y}<extra></extra>'  
                )

            fig_daily_deaths.update_layout(
                    width=500, 
                    height=288,  
                    autosize=False, 
                    template=PLOTLY_TEMPLATE,
                    plot_bgcolor='rgba(0,0,0,0)',  
                    paper_bgcolor='rgba(0,0,0,0)',  
                    title=dict(
                        text='Current Month',  
                        font=dict(size=12, family=CHART_FONT, color=TEXT_COLOR),  
                        x=0.5,
                        xanchor='center'
                    ),
                    xaxis=dict(
                        title=dict(text='Date', font=dict(size=12, family=CHART_FONT)),
                        showgrid=True,
                        gridcolor=GRID_COLOR,  
                        linecolor=AXIS_COLOR,  
                        tickfont=dict(color=TEXT_COLOR, size=10),
                        showline=True
                    ),
                    yaxis=dict(
                        title=dict(text='Number of Deaths', font=dict(size=12, family=CHART_FONT)),
                        showgrid=True,
                        gridcolor=GRID_COLOR,  
                        linecolor=AXIS_COLOR,  
                        tickfont=dict(color=TEXT_COLOR, size=10),
                        showline=False,
                        rangemode='tozero'
                    ),
                    margin=dict(l=40, r=15, t=30, b=30),  
                    font_family=CHART_FONT,
                    font_color=TEXT_COLOR,
                    hovermode='x unified'  
                )

            chart_col1, chart_col2 = st.columns([1, 1], gap="small")

            with chart_col1:
                    st.markdown('<div class="daily-deaths-chart-container">', unsafe_allow_html=True)
                    st.plotly_chart(fig_daily_deaths, use_container_width=True, config={'displayModeBar': False}, key=f"daily_deaths_chart_{selected_month}_{selected_year}")
                    st.markdown('</div>', unsafe_allow_html=True)

            with chart_col2:
                    try:
                        if not df_filtered.empty and 'deaths' in df_filtered.columns and 'date' in df_filtered.columns and 'incident_type' in df_filtered.columns:
                            selected_year = end_date.year

                            if selected_incident_type and selected_incident_type != 'All':
                                selected_incident = selected_incident_type
                                yearly_incident_data = df_main[
                                    (df_main['date'].dt.year == selected_year) &
                                    (df_main['incident_type'] == selected_incident)
                                ].copy()
                            else:
                                yearly_incident_data = df_main[
                                    df_main['date'].dt.year == selected_year
                                ].copy()
                                selected_incident = "All Incidents"

                            # Creating complete month range for the year (Jan to Dec)
                            import calendar
                            all_months = []
                            for month_num in range(1, 13):
                                month_name = calendar.month_abbr[month_num]
                                all_months.append({'month': month_num, 'month_name': month_name, 'deaths': 0})

                            # Creating DataFrame with all 12 months
                            monthly_deaths = pd.DataFrame(all_months)

                            if not yearly_incident_data.empty:
                                yearly_incident_data['month'] = yearly_incident_data['date'].dt.month
                                actual_monthly_deaths = yearly_incident_data.groupby('month')['deaths'].sum().reset_index()

                                for _, row in actual_monthly_deaths.iterrows():
                                    monthly_deaths.loc[monthly_deaths['month'] == row['month'], 'deaths'] = row['deaths']

                                max_deaths = monthly_deaths['deaths'].max()
                                min_deaths = monthly_deaths['deaths'].min()

                                def get_gradient_color(value, min_val, max_val):
                                    if max_val == min_val:
                                        return '#4CAF50' 

                                    normalized = (value - min_val) / (max_val - min_val)

                                    light_r, light_g, light_b = 129, 199, 132  
                                    dark_r, dark_g, dark_b = 46, 125, 50      

                                    r = int(light_r + (dark_r - light_r) * normalized)
                                    g = int(light_g + (dark_g - light_g) * normalized)
                                    b = int(light_b + (dark_b - light_b) * normalized)

                                    return f'rgb({r},{g},{b})'

                                monthly_deaths['color'] = monthly_deaths['deaths'].apply(
                                    lambda x: get_gradient_color(x, min_deaths, max_deaths)
                                )

                                # Creating column chart
                                fig_monthly_deaths = px.bar(
                                    monthly_deaths,
                                    x='month_name',
                                    y='deaths',
                                    title=f"Monthly Casualties - {selected_incident} ({selected_year})",
                                    labels={'month_name': 'Month', 'deaths': 'Number of Casualties'},
                                    color='deaths',
                                    color_continuous_scale='Greens',
                                    text='deaths'
                                )

                                fig_monthly_deaths.update_traces(
                                    texttemplate='%{text}',
                                    textposition='outside',
                                    hovertemplate='Month: %{x}<br>Deaths: %{y}<extra></extra>',
                                    marker_line_color='rgba(0,0,0,0.3)',
                                    marker_line_width=1
                                )

                                fig_monthly_deaths.update_layout(
                                    width=500, 
                                    height=288,
                                    autosize=False,
                                    template=PLOTLY_TEMPLATE,
                                    plot_bgcolor='rgba(0,0,0,0)',
                                    paper_bgcolor='rgba(0,0,0,0)',
                                    title={
                                        'text': f"Monthly Casualties - {selected_incident} ({selected_year})",
                                        'x': 0.5,
                                        'xanchor': 'center',
                                        'font': {'size': 12, 'color': TEXT_COLOR,} 
                                    },
                                    xaxis={
                                        'title': {'text': 'Month', 'font': {'size': 12, 'color': '#666666'}},
                                        'tickfont': {'size': 10, 'color': '#666666'},
                                        'gridcolor': 'rgba(200,200,200,0.3)',
                                        'showgrid': True
                                    },
                                    yaxis={
                                        'title': {'text': 'Number of Deaths', 'font': {'size': 12, 'color': '#666666'}},
                                        'tickfont': {'size': 10, 'color': '#666666'},
                                        'gridcolor': 'rgba(200,200,200,0.3)',
                                        'showgrid': True
                                    },
                                    showlegend=False,
                                    margin={'l': 40, 'r': 40, 't': 45, 'b': 40}  
                                )

                                # Displaying the monthly deaths column chart
                                st.markdown('<div class="daily-deaths-chart-container">', unsafe_allow_html=True)
                                st.plotly_chart(fig_monthly_deaths, use_container_width=True, config={'displayModeBar': False}, key=f"monthly_deaths_chart_{selected_incident}_{selected_year}")
                                st.markdown('</div>', unsafe_allow_html=True)
                        else:
                            import calendar
                            all_months = []
                            for month_num in range(1, 13):
                                month_name = calendar.month_abbr[month_num]
                                all_months.append({'month': month_num, 'month_name': month_name, 'deaths': 0})

                            monthly_deaths = pd.DataFrame(all_months)

                            # Create column chart with empty data
                            fig_monthly_deaths = px.bar(
                                monthly_deaths,
                                x='month_name',
                                y='deaths',
                                title=f"Monthly Casualties - {selected_incident} ({selected_year})",
                                labels={'month_name': 'Month', 'deaths': 'Number of Casualties'},
                                color='deaths',
                                color_continuous_scale='Greens',
                                text='deaths'
                            )

                            fig_monthly_deaths.update_traces(
                                texttemplate='%{text}',
                                textposition='outside',
                                hovertemplate='Month: %{x}<br>Deaths: %{y}<extra></extra>',
                                marker_line_color='rgba(0,0,0,0.3)',
                                marker_line_width=1
                            )

                            fig_monthly_deaths.update_layout(
                                width=500,  
                                height=288,  
                                autosize=False,
                                template=PLOTLY_TEMPLATE,
                                plot_bgcolor='rgba(0,0,0,0)',
                                paper_bgcolor='rgba(0,0,0,0)',
                                title={
                                    'text': f"Monthly Casualties - {selected_incident} ({selected_year})",
                                    'x': 0.5,
                                    'xanchor': 'center',
                                    'font': {'size': 12, 'color': TEXT_COLOR}  
                                },
                                xaxis={
                                    'title': {'text': 'Month', 'font': {'size': 12, 'color': '#666666'}},
                                    'tickfont': {'size': 10, 'color': '#666666'},
                                    'gridcolor': 'rgba(200,200,200,0.3)',
                                    'showgrid': True
                                },
                                yaxis={
                                    'title': {'text': 'Number of Casualties', 'font': {'size': 12, 'color': '#666666'}},
                                    'tickfont': {'size': 10, 'color': '#666666'},
                                    'gridcolor': 'rgba(200,200,200,0.3)',
                                    'showgrid': True
                                },
                                margin={'l': 40, 'r': 40, 't': 45, 'b': 40} 
                            )

                            # Monthly deaths column chart
                            st.markdown('<div class="daily-deaths-chart-container">', unsafe_allow_html=True)
                            st.plotly_chart(fig_monthly_deaths, use_container_width=True, config={'displayModeBar': False}, key=f"monthly_deaths_chart_{selected_incident}_{selected_year}")
                            st.markdown('</div>', unsafe_allow_html=True)
                    except Exception as e:
                        st.error(f"Could not render 'Monthly Deaths by Selected Incident' chart: {e}")

    except Exception as e:
        st.error(f"Could not render 'Daily Deaths in Selected Month' chart: {e}")

    with graph_col2:
        st.markdown('<h3 class="section-title">Casualties(%) by Incidents</h3>', unsafe_allow_html=True)
        try:
            if not df_filtered.empty and 'deaths' in df_filtered.columns and 'incident_type' in df_filtered.columns and df_filtered['deaths'].sum() > 0:
                sunburst_data_df = df_filtered[df_filtered['deaths'] > 0].groupby('incident_type')['deaths'].sum().reset_index()
                sunburst_data_df = sunburst_data_df.sort_values(by='deaths', ascending=False)

                # Additional validation to prevent "weights sum to zero" error
                if not sunburst_data_df.empty and sunburst_data_df['deaths'].sum() > 0:
                    fig_sunburst = px.sunburst(
                        sunburst_data_df,
                        path=[px.Constant("Total Deaths"), 'incident_type'],
                        values='deaths',
                        color='incident_type',
                        color_discrete_sequence=px.colors.qualitative.Pastel,
                        custom_data=['deaths']
                    )
                    fig_sunburst.update_traces(
                        textinfo='label+percent root',
                        hovertemplate='<b>%{label}</b><br>Deaths: %{customdata[0]:,}<br>(%{percentRoot:.1%})<extra></extra>',
                        insidetextorientation='radial',
                        leaf_opacity=0.9,
                        marker_line_width=0.5, marker_line_color='rgba(0,0,0,0.4)'
                    )
                    st.plotly_chart(style_plotly_chart(fig_sunburst, chart_height=300, is_pie_or_donut=True), use_container_width=True, key=f"sunburst_chart_{total_deaths}_{start_date}_{end_date}")
                else: st.caption("No death data by incident type to display for the selected filters.")
            elif not ('deaths' in df_filtered.columns and 'incident_type' in df_filtered.columns):
                st.caption("Required columns ('deaths', 'incident_type') missing for sunburst chart.")
            else: st.caption("No deaths recorded in the selected period to display by incident type.")
        except Exception as e:
            st.error(f"Could not render 'Deaths by Incident Type' chart: {e}")

    with graph_col3:
        st.markdown('<h3 class="section-title">Casualties in last 7 months</h3>', unsafe_allow_html=True)
        try:
            if not df_filtered.empty and 'deaths' in df_filtered.columns and 'date' in df_filtered.columns:
                last_7_months_end_date = end_date
                last_7_months_start_date = (last_7_months_end_date - pd.DateOffset(months=6)).replace(day=1)

                df_7_months = df_filtered[
                    (df_filtered['date'] >= last_7_months_start_date) &
                    (df_filtered['date'] <= last_7_months_end_date)
                ].copy()

                if not df_7_months.empty:
                    df_7_months['year_month'] = df_7_months['date'].dt.to_period('M')
                    monthly_summary_7_months = df_7_months.groupby('year_month')['deaths'].sum().reset_index()
                    monthly_summary_7_months['month_label'] = monthly_summary_7_months['year_month'].dt.strftime('%b %Y')
                    monthly_summary_7_months = monthly_summary_7_months.sort_values('year_month')

                    if not monthly_summary_7_months.empty and monthly_summary_7_months['deaths'].sum() > 0:
                        max_deaths = monthly_summary_7_months['deaths'].max()
                        min_deaths = monthly_summary_7_months['deaths'].min()

                        def get_red_gradient_color(value, min_val, max_val):
                            if max_val == min_val:
                                return '#DA1E28'  
                            normalized = (value - min_val) / (max_val - min_val)
                            light_r, light_g, light_b = 255, 182, 193
                            dark_r, dark_g, dark_b = 218, 30, 40
                            r = int(light_r + (dark_r - light_r) * normalized)
                            g = int(light_g + (dark_g - light_g) * normalized)
                            b = int(light_b + (dark_b - light_b) * normalized)

                            return f'rgb({r},{g},{b})'

                        # Applying gradient colors
                        monthly_summary_7_months['color'] = monthly_summary_7_months['deaths'].apply(
                            lambda x: get_red_gradient_color(x, min_deaths, max_deaths)
                        )

                        fig_7_months = px.bar(
                            monthly_summary_7_months,
                            x='month_label',
                            y='deaths',
                            labels={'month_label': 'Month', 'deaths': 'Total Deaths'},
                            color='deaths',
                            color_continuous_scale='Reds',
                            title=f"Total Deaths from {monthly_summary_7_months['month_label'].iloc[0]} to {monthly_summary_7_months['month_label'].iloc[-1]}" if not monthly_summary_7_months.empty else "Deaths in Last 7 Months",
                            text='deaths'
                        )

                        fig_7_months.update_traces(
                            texttemplate='%{text}',
                            textposition='outside',
                            hovertemplate='Month: %{x}<br>Deaths: %{y}<extra></extra>',
                            marker_line_color='rgba(0,0,0,0.3)',
                            marker_line_width=1
                        )

                        fig_7_months = style_plotly_chart(fig_7_months, chart_height=330) 
                        st.plotly_chart(fig_7_months, use_container_width=True, config={'displayModeBar': False}, key=f"deaths_7_months_chart_{gauge_key_base}")
                    else:
                        st.caption("No deaths recorded in the last 7 months for the selected filters.")
                else:
                    st.caption("No data available for the last 7 months.")
            elif not ('deaths' in df_filtered.columns and 'date' in df_filtered.columns):
                st.caption("Required columns ('date', 'deaths') missing for last 7 months death report.")
            else:
                st.caption("No data available in df_filtered to display last 7 months report.")
        except Exception as e:
            st.error(f"Could not render 'Deaths in Last 7 Months' chart: {e}")

    # Adding compact divider line above the treemap section - minimal spacing
    st.markdown('<hr style="border: none; height: 1px; background: linear-gradient(90deg, #0F62FE 0%, #4589FF 100%); margin: 2px 0 6px 0; opacity: 0.7;">', unsafe_allow_html=True)
    st.markdown('<h3 class="section-title">District and Block wise Incident Distribution</h3>', unsafe_allow_html=True)
    treemap_col = st.container()

    with treemap_col:
        if not df_filtered.empty and 'district' in df_filtered.columns and 'incident_type' in df_filtered.columns:
            df_treemap = df_filtered.groupby(['district', 'incident_type']).size().reset_index(name='incident_count')
            df_treemap = df_treemap[df_treemap['incident_count'] > 0]

            # Additional validation to prevent "weights sum to zero" error
            if not df_treemap.empty and df_treemap['incident_count'].sum() > 0:
                try:
                    base_pastel_colors = [
                        '#FBB4AE', '#B3CDE3', '#CCEBC5', '#DECBE4', '#FED9A6',
                        '#FFFFCC', '#E5D8BD', '#FDDAEC', '#F2F2F2', '#B3E2CD'
                    ]

                    shiny_pastel_colors = []
                    for i, color in enumerate(base_pastel_colors):
                        if i % 3 == 0:  
                            if color == '#FBB4AE':  
                                shiny_pastel_colors.append('#FFB3BA')
                            elif color == '#DECBE4':  
                                shiny_pastel_colors.append('#E6D3F7')
                            elif color == '#F2F2F2':  
                                shiny_pastel_colors.append('#F8F8FF')
                            else:
                                shiny_pastel_colors.append(color)
                        else:
                            shiny_pastel_colors.append(color)

                    fig_treemap = px.treemap(
                        df_treemap,
                        path=[px.Constant("All Incidents"), 'district', 'incident_type'],
                        values='incident_count',
                        color='district',
                        hover_name='incident_type',
                        custom_data=['district'],
                        color_discrete_sequence=shiny_pastel_colors
                    )

                    fig_treemap.update_traces(
                        textinfo="label+value+percent parent",
                        marker=dict(
                            cornerradius=5,
                            line=dict(width=0.5, color='black')  
                        ),
                        hovertemplate='<b>%{label}</b><br>District: %{customdata[0]}<br>Incidents: %{value}<br>Percentage of Parent: %{percentParent:.1%}<extra></extra>',
                        tiling=dict(
                            packing="squarify",
                            squarifyratio=1.2,   
                            pad=2         
                        )
                    )
                    fig_treemap.data[0].textfont.size = 9
                    fig_treemap.data[0].textfont.family = CHART_FONT

                    fig_treemap.update_traces(
                        # District names (parent level)
                        outsidetextfont=dict(
                            size=10,
                            family=CHART_FONT,
                            color='black'
                        ),
                        # Incident types (nested level)
                        insidetextfont=dict(
                            size=9,
                            family=CHART_FONT,
                            color='black'
                        )
                    )

                    fig_treemap.update_layout(
                        title_text='Incident Distribution by District & Type',
                        margin=dict(t=40, l=5, r=5, b=5),
                        height=450,  
                        plot_bgcolor='white', 
                        paper_bgcolor='white'  
                    )

                    st.plotly_chart(style_plotly_chart(fig_treemap, chart_height=380, is_pie_or_donut=True), use_container_width=True, key=f"treemap_chart_{total_incidents}_{start_date}_{end_date}")

                except Exception as e:
                    st.error(f"Could not render Treemap: {e}")
            else:
                st.info("No data available to display in the Treemap for the current filter selection.")
        else:
            st.info("Required columns ('district', 'incident_type') not available or no data in filtered set for Treemap.")

    # Footer
    st.markdown(f'''<div class="footer-card" style="margin-top: 2rem;">
        <h4 class="footer-title"> Bihar Disaster Management Dashboard</h4>
        <p>Built with Streamlit & Plotly | Last updated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}</p>
        <p>Data visualization for disaster preparedness and emergency response planning.</p>
        <p style="font-size: 0.7rem; margin-top: 0.4rem;">🏛️ Government of Bihar | Emergency Operations Center</p>
        </div>''', unsafe_allow_html=True)

if __name__ == "__main__":
    run()