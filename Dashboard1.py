import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
from PIL import Image
import base64
from io import BytesIO
from datetime import datetime, timedelta

# Function to load and encode image to base64
def get_image_base64(path):
    try:
        img = Image.open(path)
        buffered = BytesIO()
        img_format = path.split('.')[-1].upper()
        if img_format == "PNG":
            img.save(buffered, format="PNG")
            mime_type = "image/png"
        elif img_format == "WEBP":
            img.save(buffered, format="WEBP")
            mime_type = "image/webp"
        elif img_format in ["JPG", "JPEG"]:
            img.save(buffered, format="JPEG")
            mime_type = "image/jpeg"
        else:
            img.save(buffered, format="PNG")
            mime_type = "image/png"
        img_str = base64.b64encode(buffered.getvalue()).decode()
        return f"data:{mime_type};base64,{img_str}"
    except FileNotFoundError:
        st.warning(f"Image '{path}' not found. Displaying title without image or using default.")
        return None
    except Exception as e:
        print(f"Error encoding image {path}: {e}")
        return None

# Database connection function
@st.cache_resource
def init_db_connection():
    """Establishes a SQLAlchemy engine connection to the SQL Server database using Dashboard1.toml config."""
    try:
        from sqlalchemy import create_engine
        import os

        config_path = os.path.join(".streamlit", "Dashboard1.toml")
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
            # Fallback connection string only if .toml doesn't exist
            st.error("Dashboard1.toml file not found in .streamlit folder. Please ensure the configuration file exists.")
            return None

        engine = create_engine(connection_url)
        return engine
    except Exception as e:
        st.error(f"Database connection failed. Check `Dashboard1.toml` and ensure DB is running. Error: {e}")
        return None

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

# Database-connected data loading function
@st.cache_data(ttl=600)
def load_data():
    try:
        sql_query = """
        SELECT
            CD.RecordDate,
            CD.FYearID,
            D.DistrictName,
            B.BlockName,
            CD.AffectedPeople,
            CD.DeadPeople,
            CD.TotalNightShelter,
            PA_Agg.TotalDistrictAllotedAmount AS AllotedAmount,
            CD.AmountSpent,
            CD.BlanketDistribution,
            CD.TotalPeopleNightShelter,
            CD.WoodWt,
            CD.BonfirePlace,
            D.DistrictCode
        FROM
            dbo.ColdWaveDetails AS CD
        LEFT JOIN
            (
                SELECT
                    DistrictCode,
                    SUM(AllotedAmount) AS TotalDistrictAllotedAmount
                FROM
                    dbo.ColdWavepaymentAllotment
                GROUP BY
                    DistrictCode
            ) AS PA_Agg
            ON CD.DistrictCode = PA_Agg.DistrictCode
        LEFT JOIN
            dbo.mst_Districts AS D ON CD.DistrictCode = D.DistrictCode
        LEFT JOIN
            dbo.mst_Blocks AS B ON CD.BlockCode = B.BlockCode AND CD.DistrictCode = B.DistrictCode;
        """
        engine = init_db_connection()
        if engine is None:
            return pd.DataFrame()

        df_loaded = pd.read_sql(sql_query, engine)

        column_mapping = {
            'RecordDate': 'date',
            'FYearID': 'financial_year',
            'DistrictName': 'district',
            'BlockName': 'block',
            'AffectedPeople': 'affected_population_lac',
            'DeadPeople': 'death',
            'TotalNightShelter': 'rain_basera',
            'AllotedAmount': 'alloted_amount_lac',
            'AmountSpent': 'expenditure_amount_lac',
            'BlanketDistribution': 'blanket_distributed',
            'TotalPeopleNightShelter': 'people_in_rain_basera',
            'WoodWt': 'wood_burn_kg',
            'BonfirePlace': 'bonfire_places',
            'DistrictCode': 'district_code'
        }

        df_loaded.rename(columns=column_mapping, inplace=True)
        if 'affected_forms_filled' not in df_loaded.columns:
            df_loaded['affected_forms_filled'] = 0

        df_loaded['date'] = pd.to_datetime(df_loaded['date'], errors='coerce')
        numeric_cols = [
            'affected_forms_filled', 'affected_population_lac', 'death', 'rain_basera',
            'alloted_amount_lac', 'expenditure_amount_lac', 'blanket_distributed',
            'people_in_rain_basera', 'wood_burn_kg', 'bonfire_places'
        ]
        for col in numeric_cols:
            df_loaded[col] = pd.to_numeric(df_loaded[col], errors='coerce').fillna(0)

        if 'district' in df_loaded.columns:
            df_loaded['district'] = df_loaded['district'].astype(str).str.strip().str.title()
        if 'block' in df_loaded.columns:
            df_loaded['block'] = df_loaded['block'].astype(str).str.strip().str.title()

        df_loaded['district'] = df_loaded['district'].fillna('Unknown')
        df_loaded['block'] = df_loaded['block'].fillna('Unknown')

        df_loaded.dropna(subset=['date'], inplace=True)

        return df_loaded
    except Exception as e:
        st.error(f"An error occurred while connecting to the database or loading data: {e}")
        st.error("Please check your database connection, secrets file, and SQL query.")
        return pd.DataFrame()

def run():
    # Loading data
    with st.spinner('Presenting the Cold Wave Dashboard for you... Thank you for your Patience'):
        df_main = load_data()
    if df_main.empty:
        st.error(" Unable to load cold wave data. Please check database connection and try again.")
        st.info(" Ensure your database server is running and accessible.")
        return

    # Preparing filter data for horizontal layout below header
    if 'district' in df_main.columns and not df_main['district'].empty:
        unique_districts = sorted(list(df_main['district'].unique()))
    else:
        unique_districts = []

    min_date_data = pd.to_datetime('2022-12-15').date() 
    if not df_main.empty and 'date' in df_main.columns and not df_main['date'].min() is pd.NaT:
        min_date_data = min(min_date_data, df_main['date'].min().date()) 

    # Setting the default end date for the filter to today's actual date
    default_end_date_filter = datetime.now().date()
    # Setting the default dates to be the main dates from the Record 
    default_start_date_filter = min_date_data

    # Ensuring the default range is valid (start <= end)
    if default_start_date_filter > default_end_date_filter:
        default_start_date_filter = default_end_date_filter - timedelta(days=30) # Fallback to 30 days before if somehow start > end


    # Main Page Header
    eoc_logo_header_base64 = get_image_as_base64("eoc_logo.png")
    header_logo_html = f'<img src="{eoc_logo_header_base64}" alt="EOC" class="header-logo-img">' if eoc_logo_header_base64 else ""
    st.markdown(f"""
        <div class="dashboard-header">
            {header_logo_html}
            <div class="header-title-block">
                <h1>ColdWave Dashboard</h1>
                <p class="tagline">Emergency Operations Center - Government of Bihar</p>
            </div>
        </div>
    """, unsafe_allow_html=True)

    # Creating minimal horizontal layout for filters
    col1, col2, col3 = st.columns([1, 1, 1.2])

    with col1:
        selected_district_filter = st.selectbox(
            "District",
            options=unique_districts,
            key="sb_dist_filter",
            placeholder="Select District",
            index=None
        )

    with col2:
        if 'block' in df_main.columns:
            if selected_district_filter:
                unique_blocks_for_district = df_main[df_main['district'] == selected_district_filter]['block'].unique()
                block_options = sorted(list(unique_blocks_for_district))
            else:
                block_options = sorted(list(df_main['block'].unique()))
        else:
            block_options = []
        selected_block_filter = st.selectbox(
            "Block",
            options=block_options,
            key="sb_block_filter",
            placeholder="Select Block",
            index=None
        )

    with col3:
        date_input_value = st.date_input(
            "Select Date Range",
            value=[default_start_date_filter, default_end_date_filter],
            min_value=min_date_data,
            max_value=default_end_date_filter,
            key="di_date"
        )

    # Processing date range
    if len(date_input_value) == 2:
        start_date_filter_selected, end_date_filter_selected = pd.to_datetime(date_input_value[0]), pd.to_datetime(date_input_value[1])
        if start_date_filter_selected > end_date_filter_selected:
            st.error("Error: Start date cannot be after end date. Adjusting range to default.")
            start_date_filter_selected, end_date_filter_selected = pd.to_datetime(default_start_date_filter), pd.to_datetime(default_end_date_filter)
        date_range = [start_date_filter_selected, end_date_filter_selected]
    else: # This handles the case where only one date is selected, which can happen initially
        date_range = [pd.to_datetime(default_start_date_filter), pd.to_datetime(default_end_date_filter)]

    st.markdown("""
<style>
/* Keyframes for Single Line Border Tracing Animation */
@keyframes border-trace-single {
    0% {
        box-shadow: 0 0 0 0px #0043CE;
    }
    100% {
        box-shadow: 0 0 0 2px #0043CE; /* Blue border effect */
    }
}
section.main {
    transition: margin-left 0.3s ease-out !important;
}
body, .stApp { font-family: "IBM Plex Sans", sans-serif !important; font-size: 0.95rem; background-color: #F4F4F4; }
h1, h3, h6 { font-family: "IBM Plex Sans", sans-serif; }
h3 { font-size: 1.1em !important; margin-bottom: 5px !important; margin-top: 10px !important; font-weight: bold; color: #161616; }
h6 { font-size: 0.85em !important; color: #525252; text-align: left; font-weight: bold; margin-bottom: 5px; }
/* Adjusted margin for the horizontal rule to be more compact */
hr { margin: 5px 0px !important; }

/* Dashboard Header Styling */
.dashboard-header {
    background-color: #004C99; color: #FFFFFF;
    padding: 0.3375rem 1.0125rem; text-align: left; display: flex;
    align-items: center; border-bottom: 2.025px solid #ffc107;
    border-radius: 5.4px;
    box-shadow: 0 1.35px 2.7px rgba(0,0,0,0.1);
    margin-bottom: 0.675rem;
}
.dashboard-header .header-logo-img { height: 20.25px; margin-right: 10.125px; }
.dashboard-header .header-title-block { flex-grow: 1; }
.dashboard-header h1 {
    font-size: 1.0125rem; font-weight: bold; margin: 0 0 0.0675rem 0;
    line-height: 0.81; color: #FFFFFF;
}
.dashboard-header p.tagline { font-size: 0.54rem; margin: 0; color: #e0e0e0; opacity: 0.9; }
.kpi-card-single {
    background-color: #FFFFFF;
    border: 1px solid #00BCD4; /* Thin, fine blue (cyan) boundary */
    border-radius: 8px; /* Applied rounded corners here */
    box-shadow: 0 1px 3px rgba(0, 0, 0, 0.05);
    transition: transform 0.2s ease-out, box-shadow 0.2s ease-out, border 0.2s ease-out; /* Add border to transition */
    max-width: 95%;
    margin-left: auto;
    margin-right: auto;
    margin-bottom: 10px;
    position: relative;
    display: flex;
    flex-direction: column;
    height: 85px;
    overflow: hidden;
}
.kpi-card-single::before {
    content: '';
    position: absolute;
    top: 0;
    left: 0;
    right: 0;
    bottom: 0;
    background: linear-gradient(90deg, hsla(211, 100%, 91%, 1) 2%, hsla(275, 45%, 78%, 1) 100%);
    opacity: 0;
    transition: opacity 0.3s ease-in-out;
    z-index: 1;
    pointer-events: none;
    border-radius: 6px; /* Ensure gradient also respects rounded corners */
}
.kpi-card-single:hover::before {
    opacity: 1;
}
.kpi-card-single:hover {
    transform: translateY(-5px) scale(1.03);
    /* Updated: Lighter blue border (#66B3FF) and thinner (0.5px) */
    box-shadow: 0 6px 15px rgba(0, 0, 0, 0.1), 0 0 0 0.5px #66B3FF;
}
.kpi-card-single .kpi-title,
.kpi-card-single .kpi-values-container,
.kpi-card-single .kpi-value-block,
.kpi-card-single .kpi-sublabel,
.kpi-card-single .kpi-value-main {
    position: relative;
    z-index: 2;
}
.kpi-card-single .kpi-title {
    font-size: 0.85em;
    color: #393939;
    text-transform: uppercase;
    letter-spacing: 0.3px;
    font-weight: normal;
    margin-bottom: 1px;
    padding-bottom: 2px;
    border-bottom: 1px solid #F0F0F0;
    text-align: center;
    white-space: normal;
    /* Adjusted height and line-height for vertical centering of single-line titles */
    height: 2.2em; /* Reduced height slightly to bring it down */
    line-height: 2.2em; /* Set line-height equal to height for vertical centering */
}
/* Specific style for the multi-line "Affected/ Form Filled" title to maintain its appearance */
.kpi-card-single .kpi-title:has(.kpi-values-container + .kpi-values-container) {
    height: auto; /* Reset height for merged cards */
    line-height: normal; /* Reset line-height for merged cards */
}
/* Ensuring the "Affected/ Form Filled Blocks & Nagar Nikaay" title retains its original multi-line behavior */
.kpi-card-single .kpi-title:contains("AFFECTED/ FORM FILLED BLOCKS & NAGAR NIKAAY") {
    height: 2.6em; /* Original height for this specific title */
    line-height: 1.3; /* Original line-height for this specific title */
}

.kpi-card-single .kpi-values-container {
    display: flex;
    justify-content: space-around;
    align-items: center;
    width: 100%;
    flex-grow: 1;
    margin-top: 2px;
}
.kpi-card-single .kpi-value-block {
    text-align: center;
    padding: 0 2px;
}
.kpi-card-single .kpi-sublabel {
    font-size: 0.55em;
    color: #4A4A4A;
    margin-bottom: 0px;
    display: block;
    font-weight: 400;
    transition: font-weight 0.2s ease-in-out; /* Add transition for smooth bolding */
}
/* Making KPI sublabels bold on hover */
.kpi-card-single:hover .kpi-sublabel {
    font-weight: bold !important;
}

.kpi-card-single .kpi-value-main {
    font-size: 1.05em;
    font-weight: bold;
    color: #0F62FE;
    line-height: 1.1;
    display: block;
}
.kpi-card-merged {
    background-color: #FFFFFF;
    height: 170px;
}
.kpi-card-merged .merged-kpi-row {
    flex-grow: 1;
}
.kpi-card-merged .kpi-title {
    border-bottom: none;
    font-size: 0.65em;
    text-align: center;
    margin-bottom: 0;
    padding-bottom: 0;
    height: auto;
    line-height: normal;
}
.kpi-card-merged:hover {
    transform: translateY(-5px) scale(1.03);
    box-shadow: 0 6px 15px rgba(0, 0, 0, 0.1), 0 0 0 0.5px #66B3FF;
    position: relative;
}
div[data-testid="stSelectbox"] div[data-baseweb="select"] > div,
div[data-testid="stDateInput"] > div > div {
    transition: all 0.2s ease-in-out;
    border: 1px solid transparent;
    border-radius: 4px;
}
div[data-testid="stSelectbox"]:hover div[data-baseweb="select"] > div,
div[data-testid="stDateInput"]:hover > div > div {
    border: 1px solid #0F62FE;
    box-shadow: 0 4px 8px rgba(0,0,0,0.1);
}

.footer-card { background-color: #343a40; color: #dee2e6; padding: 1rem; border-radius: 8px; margin-top: 1.5rem; text-align: center; box-shadow: 0 -1px 3px rgba(0,0,0,0.05); border-top: 1px solid var(--card-border-color); font-size: 0.8rem; box-sizing: border-box; }
.footer-title { color: #ffc107 !important; font-size: 1rem !important; font-weight: 500 !important; margin-bottom: 0.5rem !important; }
.footer-card p { margin-bottom: 0.25rem; font-size: 0.75rem;}
</style>
    """, unsafe_allow_html=True)

    if df_main.empty:
        st.error("Dashboard cannot be displayed because no data could be loaded.")
        st.stop()

    # Applying filters to create `kpi_ts_df` for charts and "Till Now" KPIs
    # This dataframe is based on the selected date range.
    base_filtered_df = df_main.copy()
    start_date_filtered, end_date_filtered = date_range[0], date_range[1]
    base_filtered_df = base_filtered_df[(base_filtered_df['date'] >= start_date_filtered) & (base_filtered_df['date'] <= end_date_filtered)]

    kpi_ts_df = base_filtered_df.copy() # This will be used for Time Series charts and 'Till Now' KPIs

    if selected_district_filter and 'district' in kpi_ts_df.columns:
        kpi_ts_df = kpi_ts_df[kpi_ts_df['district'] == selected_district_filter]
        if selected_block_filter and 'block' in kpi_ts_df.columns:
            kpi_ts_df = kpi_ts_df[kpi_ts_df['block'] == selected_block_filter]


    today_kpi_reference_date = end_date_filter_selected
    today_df = kpi_ts_df[kpi_ts_df['date'] == today_kpi_reference_date.normalize()]
    tillnow_df_for_kpis = kpi_ts_df.copy()


    if kpi_ts_df.empty:
        ts_df = pd.DataFrame(columns=['date', 'affected_forms_filled', 'affected_population_lac', 'death', 'rain_basera', 'alloted_amount_lac', 'expenditure_amount_lac', 'blanket_distributed', 'people_in_rain_basera', 'wood_burn_kg', 'bonfire_places'])
        ts_df['date'] = pd.to_datetime(ts_df['date'])
    else:
        # Aggregation for time series data
        ts_df = kpi_ts_df.groupby('date', as_index=False).agg({
            'affected_forms_filled': 'sum',
            'affected_population_lac': 'sum',
            'death': 'sum',
            'rain_basera': 'sum',
            'expenditure_amount_lac': 'sum',
            'blanket_distributed': 'sum',
            'people_in_rain_basera': 'sum',
            'wood_burn_kg': 'sum',
            'bonfire_places': 'sum'
        })

        if 'alloted_amount_lac' in kpi_ts_df.columns and 'district' in kpi_ts_df.columns:
            alloted_amount_ts = kpi_ts_df.groupby(['date', 'district'])['alloted_amount_lac'].max().reset_index()
            alloted_amount_ts_daily_sum = alloted_amount_ts.groupby('date')['alloted_amount_lac'].sum().reset_index()
            ts_df = pd.merge(ts_df, alloted_amount_ts_daily_sum, on='date', how='left')
            ts_df['alloted_amount_lac'] = ts_df['alloted_amount_lac'].fillna(0)
        else:
            ts_df['alloted_amount_lac'] = 0


    plotly_template="plotly_white"
    primary_color="#0F62FE"
    secondary_color="#525252"
    death_color="#DA1E28"
    blanket_color="#24A148"
    exp_color="#A8A8A8"
    fill_opacity=0.1
    text_color="#161616"
    grid_color="#E0E0E0"
    axis_color="#C6C6C6"
    font_family="IBM Plex Sans, sans-serif"
    theme_secondary_bg_color="#FFFFFF"

    def style_chart(fig, chart_height=190, is_pie_or_donut=False):
        fig.update_layout(
            template=plotly_template,
            plot_bgcolor='rgba(0,0,0,0)',
            paper_bgcolor='rgba(0,0,0,0)',
            xaxis=dict(showgrid=False, linecolor=axis_color, tickfont=dict(color=text_color, size=9), showline=True, zeroline=False),
            yaxis=dict(showgrid=True, gridcolor=grid_color, linecolor=axis_color, tickfont=dict(color=text_color, size=9), showline=True, zeroline=False),
            hoverlabel=dict(bgcolor="#FFFFFF", font_size=11, font_family=font_family, bordercolor=axis_color, font_color=text_color),
            legend=dict(orientation="h", yanchor="bottom", y=1.05, xanchor="right", x=1, font=dict(color=text_color, size=9), bgcolor='rgba(0,0,0,0)'),
            margin=dict(l=30, r=10, t=10, b=20),
            title_text='',
            title_x=0.5,
            font_color=text_color,
            font_family=font_family,
            height=chart_height
        )
        if not is_pie_or_donut:
            fig.update_layout(hovermode='x unified')
            fig.update_xaxes(title_text=None, hoverformat='%a, %d %b %Y')
            fig.update_yaxes(title_text=None)
        else:
            fig.update_layout(xaxis=dict(visible=False, showgrid=False), yaxis=dict(visible=False, showgrid=False))
        return fig

    if kpi_ts_df.empty and not df_main.empty:
        st.warning("No data available for KPIs and Time Series charts for the selected filter combination. Please adjust filters.")

    def create_single_kpi_card(title, today_val, till_now_val, is_lac=False):
        today_str = f"{today_val:,.2f}" if is_lac else f"{int(today_val):,}"
        till_now_str = f"{till_now_val:,.2f}" if is_lac else f"{int(till_now_val):,}"
        st.markdown(f"""
            <div class="kpi-card-single">
                <div class="kpi-title">{title}</div>
                <div class="kpi-values-container">
                    <div class="kpi-value-block">
                        <span class="kpi-sublabel">Today</span>
                        <span class="kpi-value-main">{today_str}</span>
                    </div>
                    <div class="kpi-value-block">
                        <span class="kpi-sublabel">Till Now</span>
                        <span class="kpi-value-main">{till_now_str}</span>
                    </div>
                </div>
            </div>
        """, unsafe_allow_html=True)

    def create_merged_financial_card(allot_today, allot_till, exp_today, exp_till):
        allot_today_str = f"{allot_today:,.2f}"
        allot_till_str = f"{allot_till:,.2f}"
        exp_today_str = f"{exp_today:,.2f}"
        exp_till_str = f"{exp_till:,.2f}"
        st.markdown(f"""
            <div class="kpi-card-single kpi-card-merged">
                <div class="merged-kpi-row" style="flex-grow: 1; border-bottom: 1px solid #F0F0F0; margin-bottom: 5px; padding-bottom: 5px;">
                    <div class="kpi-title">ALLOTED AMOUNT (LAC)</div>
                    <div class="kpi-values-container">
                        <div class="kpi-value-block">
                            <span class="kpi-sublabel">Today</span>
                            <span class="kpi-value-main">{allot_today_str}</span>
                        </div>
                        <div class="kpi-value-block">
                            <span class="kpi-sublabel">Till Now</span>
                            <span class="kpi-value-main">{allot_till_str}</span>
                        </div>
                    </div>
                </div>
                <div class="merged-kpi-row" style="flex-grow: 1;">
                    <div class="kpi-title">EXPENDITURE AMOUNT (LAC)</div>
                    <div class="kpi-values-container">
                        <div class="kpi-value-block">
                            <span class="kpi-sublabel">Today</span>
                            <span class="kpi-value-main">{exp_today_str}</span>
                        </div>
                        <div class="kpi-value-block">
                            <span class="kpi-sublabel">Till Now</span>
                            <span class="kpi-value-main">{exp_till_str}</span>
                        </div>
                    </div>
                </div>
            </div>
        """, unsafe_allow_html=True)

    st.markdown("---")
    main_col1, main_col2 = st.columns([0.55, 0.45], gap="large")

    with main_col1:
        chart_row1_col1, chart_row1_col2 = st.columns(2, gap="medium")
        with chart_row1_col1:
            st.markdown("###### Affected Population (lac)")
            if not ts_df.empty and 'affected_population_lac' in ts_df.columns:
                fig = px.line(ts_df, x='date', y='affected_population_lac', color_discrete_sequence=[primary_color])
                fig.update_traces(mode='lines', line_shape='linear', line=dict(width=1.5), fill='tozeroy', fillcolor=f'rgba(15, 98, 254, {fill_opacity})', name='Population', hovertemplate='%{y:,.2f} lac<extra></extra>')
                st.plotly_chart(style_chart(fig), use_container_width=True)
            else:
                st.caption("No data for Population.")
        with chart_row1_col2:
            st.markdown("###### Deaths Reported")
            if not ts_df.empty and 'death' in ts_df.columns:
                fig = px.bar(ts_df, x='date', y='death', color_discrete_sequence=[death_color])
                fig.update_traces(name='Deaths', hovertemplate='%{y:,}<extra></extra>', marker_line_width=0)
                fig.update_layout(bargap=0.6)
                st.plotly_chart(style_chart(fig), use_container_width=True)
            else:
                st.caption("No data for Deaths.")
        chart_row2_col1, chart_row2_col2 = st.columns(2, gap="medium")
        with chart_row2_col1:
            st.markdown("###### Shelter & Blankets")
            if not ts_df.empty and 'people_in_rain_basera' in ts_df.columns and 'blanket_distributed' in ts_df.columns:
                fig = go.Figure()
                fig.add_trace(go.Scatter(x=ts_df['date'], y=ts_df['people_in_rain_basera'], name='People Sheltered', mode='lines', line=dict(color=secondary_color, width=1.5), fill='tozeroy', fillcolor=f'rgba(82, 82, 82, {fill_opacity})', hovertemplate='Sheltered: %{y:,}<extra></extra>'))
                fig.add_trace(go.Scatter(x=ts_df['date'], y=ts_df['blanket_distributed'], name='Blankets Distributed', mode='lines', line=dict(color=blanket_color, width=1.5, dash='dot'), yaxis='y2', hovertemplate='Blankets: %{y:,}<extra></extra>'))
                fig = style_chart(fig)
                fig.update_layout(yaxis=dict(tickfont=dict(color=secondary_color)), yaxis2=dict(title=None, overlaying='y', side='right', showgrid=False, showline=True, linecolor=axis_color, tickfont=dict(color=blanket_color)), legend=dict(y=1.15))
                st.plotly_chart(fig, use_container_width=True)
            else:
                st.caption("No data for Shelter & Blankets.")
        with chart_row2_col2:
            st.markdown("###### Financial Overview (Lac)")
            if not ts_df.empty and 'alloted_amount_lac' in ts_df.columns and 'expenditure_amount_lac' in ts_df.columns:
                fig = px.line(ts_df, x='date', y=['alloted_amount_lac', 'expenditure_amount_lac'], color_discrete_sequence=[primary_color, exp_color])
                fig.update_traces(mode='lines', line_shape='linear', line=dict(width=1.5), hovertemplate='%{y:,.2f} lac<extra></extra>')
                fig = style_chart(fig)
                if len(fig.data) >= 1:
                    fig.data[0].name = 'Alloted'
                if len(fig.data) >= 2:
                    fig.data[1].name = 'Expenditure'
                st.plotly_chart(fig, use_container_width=True)
            else:
                st.caption("No data for Financial Overview.")

    with main_col2:
        st.markdown("###### District/Block Overview")
        treemap_input_data = base_filtered_df.copy()

        # Debug: Checking treemap input data
        print(f"TREEMAP DEBUG: Input data rows: {len(treemap_input_data)}")
        if not treemap_input_data.empty:
            print(f"TREEMAP DEBUG: Affected population sum: {treemap_input_data['affected_population_lac'].sum()}")
            print(f"TREEMAP DEBUG: Available districts: {treemap_input_data['district'].unique()}")

        if selected_district_filter:
            print(f"TREEMAP DEBUG: Filtering by district: {selected_district_filter}")
            treemap_input_data = treemap_input_data[treemap_input_data['district'] == selected_district_filter]
            print(f"TREEMAP DEBUG: After district filter: {len(treemap_input_data)} rows")
        if selected_district_filter:
            if not treemap_input_data.empty:
                block_level_data = treemap_input_data.groupby(['district', 'block'], as_index=False)['affected_population_lac'].sum()
                treemap_path = [px.Constant("Filtered Overview"), 'district', 'block']
                caption_text = "No data for Treemap for the selected block."
            else:
                block_level_data = pd.DataFrame()
                caption_text = "No data for Treemap for the selected district."
        else:
            if not treemap_input_data.empty:
                block_level_data = treemap_input_data.groupby(['district'], as_index=False)['affected_population_lac'].sum()
                treemap_path = [px.Constant("Filtered Overview"), 'district']
                caption_text = "No data for Treemap."
            else:
                block_level_data = pd.DataFrame()
                caption_text = "No data for Treemap."
        if not block_level_data.empty:
            block_level_data['affected_population_lac'] = pd.to_numeric(block_level_data['affected_population_lac'], errors='coerce').fillna(0)
            block_level_data = block_level_data[block_level_data['affected_population_lac'] >= 0]

            print(f"TREEMAP DEBUG: Final data rows: {len(block_level_data)}")
            print(f"TREEMAP DEBUG: Final sum: {block_level_data['affected_population_lac'].sum()}")

            # Fix: To Check if all values are zero to prevent "weights sum to zero" error
            if block_level_data['affected_population_lac'].sum() > 0:
                fig_treemap = px.treemap(
                    block_level_data,
                    path=treemap_path,
                    values='affected_population_lac',
                    color='affected_population_lac',
                    custom_data=['affected_population_lac'],
                    color_continuous_scale='Blues',
                    title=None
                )
            else:
                # If all values are zero, showing message instead of broken chart
                block_level_data = pd.DataFrame()

        if not block_level_data.empty and block_level_data['affected_population_lac'].sum() > 0:
            fig_treemap.update_layout(
                height=500,
                margin=dict(t=10, l=10, r=10, b=10),
                font_family=font_family,
                hoverlabel=dict(bgcolor="#FFFFFF", font_size=11, font_family=font_family, bordercolor=axis_color, font_color=text_color),
                coloraxis_colorbar=dict(title="Pop. (Lac)")
            )
            fig_treemap.update_traces(
                
                texttemplate="<b>%{label}</b><br>%{value:,.2f}",
                hovertemplate='<b>%{label}</b><br>Population (Lac): %{value:,.2f} L<extra></extra>',
                textposition='middle center',
                textfont_size=11,
                marker=dict(cornerradius=0, line=dict(color='#B0B0B0', width=0.5), pad=dict(t=2,l=2,r=2,b=2))
            )
            fig_treemap.update_traces(maxdepth=len(treemap_path))
            st.plotly_chart(fig_treemap, use_container_width=True)
        else:
            st.caption(caption_text)

    total_allotment_dashboard = 0
    if 'alloted_amount_lac' in tillnow_df_for_kpis.columns and 'district' in tillnow_df_for_kpis.columns and not tillnow_df_for_kpis.empty:
        unique_district_allotments = tillnow_df_for_kpis.groupby('district')['alloted_amount_lac'].max()
        total_allotment_dashboard = unique_district_allotments.sum()
    else:
        total_allotment_dashboard = 0

    total_expenditure_dashboard = tillnow_df_for_kpis['expenditure_amount_lac'].sum() if not tillnow_df_for_kpis.empty else 0

    # For "Today's" Allotment KPI:
    today_allotment = 0
    if not today_df.empty and 'district' in today_df.columns and 'alloted_amount_lac' in today_df.columns:
        today_allotment = today_df.groupby('district')['alloted_amount_lac'].max().sum()
    today_expenditure = today_df['expenditure_amount_lac'].sum() if not today_df.empty else 0


    kpi_data = {
        "forms": {"title": "Affected/ Form Filled Blocks & Nagar Nikaay", "today": today_df['affected_forms_filled'].sum(), "till_now": tillnow_df_for_kpis['affected_forms_filled'].sum(), "is_lac": False},
        "population": {"title": "AFFECTED POPULATION", "today": today_df['affected_population_lac'].sum(), "till_now": tillnow_df_for_kpis['affected_population_lac'].sum(), "is_lac": True},
        "basera": {"title": "NO. OF RAIN BASERA", "today": today_df['rain_basera'].sum(), "till_now": tillnow_df_for_kpis['rain_basera'].sum(), "is_lac": False},
        "deaths": {"title": "NO OF DEATHS", "today": today_df['death'].sum(), "till_now": tillnow_df_for_kpis['death'].sum(), "is_lac": False},
        "people_basera": {"title": "NO. OF PEOPLE IN RAIN BASERA", "today": today_df['people_in_rain_basera'].sum(), "till_now": tillnow_df_for_kpis['people_in_rain_basera'].sum(), "is_lac": False},
        "blankets": {"title": "BLANKETS DISTRIBUTED", "today": today_df['blanket_distributed'].sum(), "till_now": tillnow_df_for_kpis['blanket_distributed'].sum(), "is_lac": False},
        "wood": {"title": "TOTAL WOOD BURN (IN KG)", "today": today_df['wood_burn_kg'].sum(), "till_now": tillnow_df_for_kpis['wood_burn_kg'].sum(), "is_lac": False},
        "bonfires": {"title": "NO. OF BONFIRE PLACES", "today": today_df['bonfire_places'].sum(), "till_now": tillnow_df_for_kpis['bonfire_places'].sum(), "is_lac": False},
        "allotment": {"today": today_allotment, "till_now": total_allotment_dashboard},
        "expenditure": {"today": today_expenditure, "till_now": total_expenditure_dashboard},
    }

    st.markdown("---")
    kpi_order = ["forms", "population", "basera", "financial", "deaths", "people_basera", "blankets", "wood", "bonfires"]
    cols = st.columns(3)
    col_idx = 0
    for key in kpi_order:
        current_col = cols[col_idx]
        with current_col:
            if key == "financial":
                create_merged_financial_card(allot_today=kpi_data["allotment"]["today"], allot_till=kpi_data["allotment"]["till_now"], exp_today=kpi_data["expenditure"]["today"], exp_till=kpi_data["expenditure"]["till_now"])
            else:
                c = kpi_data[key]
                create_single_kpi_card(c["title"], c["today"], c["till_now"], c["is_lac"])
        col_idx = (col_idx + 1) % 3

    # Footer
    st.markdown(f'''<div class="footer-card" style="margin-top: 2rem;">
        <h4 class="footer-title"> Bihar Disaster Management Dashboard</h4>
        <p>Built with Streamlit & Plotly | Last updated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}</p>
        <p>Data visualization for disaster preparedness and emergency response planning.</p>
        <p style="font-size: 0.7rem; margin-top: 0.4rem;">🏛️ Government of Bihar | Emergency Operations Center</p>
        </div>''', unsafe_allow_html=True)

if __name__ == "__main__":
    run()