import streamlit as st
import pandas as pd
import plotly.graph_objects as go
import plotly.express as px
import json
from datetime import datetime, date, timedelta
import numpy as np
import base64
import pyodbc

def run():

    # Page Configuration handled by main.p

    # KPI Definitions
    kpi_metric_mapping = {
        "pop_affected": "Total Population Affected", "pop_evacuated": "Total Population Evacuated",
        "family_affected": "Total Family Affected", "animal_affected_total": "Total Animal Affected",
        "human_loss": "No. of Human Loss", "animal_loss": "Animal Loss",
        "total_house_damage": "Total House Damage", "kutcha_house_damage_dr": "Kutcha House Damage",
        "pucca_house_damage_dr": "Pucca House Damage", "huts_damage_dr": "Huts Damage",
        "cost_damage_house_dr": "Est Cost Of Damage House",
        "total_affected_area": "Total Affected Area (Hec.)", "agriculture_area": "Agriculture Area (Hec.)",
        "non_agriculture_area": "Non Agriculture Area (Hec.)", "crop_damage_area": "Crop Damage Area (Hec.)",
        "damage_fisheries": "Damage Fisheries (Hec.)", "gr_distribution": "Families GR Distribution",
        "polythene_sheet": "Polythene Sheet", "food_packet": "Food Packet",
        "dry_ration_packet": "Dry Ration Packet", "fodder_distribution": "Fodder Distribution",
        "est_cost_property_damage": "Est Cost Of Property Damage",
        "fc_boats_total": "Total Boats Deployed",
        "fc_relief_centres_total": "Total Relief Centres",
        "fc_persons_in_relief_total": "Total Persons in Relief",
        "fc_comm_kitchens_total": "Total Community Kitchens",
        "fc_meals_served_total": "Total Meals Served",
        "fc_health_centres_total": "Total Health Centres",
        "fc_persons_treated_total": "Total Persons Treated (Health)",
        "fc_vet_centres_total": "Total Veterinary Centres",
        "fc_animals_treated_total": "Total Animals Treated (Vet)"
    }
    default_kpi_key = "pop_affected"
    default_kpi_label = kpi_metric_mapping[default_kpi_key]

    kpi_options_for_menu = {
        "Population Report": [
            ("Total Population Affected", "pop_affected"), ("Total Population Evacuated", "pop_evacuated"),
            ("Total Family Affected", "family_affected"), ("Total Animal Affected", "animal_affected_total"),
            ("No. of Human Loss", "human_loss"), ("Animal Loss", "animal_loss"),
        ],
        "Damage Report": [
            ("Total House Damage", "total_house_damage"), ("Kutcha House Damage", "kutcha_house_damage_dr"),
            ("Pucca House Damage", "pucca_house_damage_dr"), ("Huts Damage", "huts_damage_dr"),
            ("Est Cost Of Damage House", "cost_damage_house_dr"),
        ],
        "Affected Area Report": [
            ("Total Affected Area (Hec.)", "total_affected_area"), ("Agriculture Area (Hec.)", "agriculture_area"),
            ("Non Agriculture Area (Hec.)", "non_agriculture_area"), ("Crop Damage Area (Hec.)", "crop_damage_area"),
            ("Damage Fisheries (Hec.)", "damage_fisheries"),
        ],
        "Facility Centre Report": [
            ("Total Boats Deployed", "fc_boats_total"),
            ("Total Relief Centres", "fc_relief_centres_total"),
            ("Total Persons in Relief", "fc_persons_in_relief_total"),
            ("Total Community Kitchens", "fc_comm_kitchens_total"),
            ("Total Meals Served", "fc_meals_served_total"),
            ("Total Health Centres", "fc_health_centres_total"),
            ("Persons Treated (Health)", "fc_persons_treated_total"),
            ("Total Veterinary Centres", "fc_vet_centres_total"),
            ("Animals Treated (Vet)", "fc_animals_treated_total")
        ],
        "Relief Report": [
            ("Families GR Distribution", "gr_distribution"), ("Polythene Sheet", "polythene_sheet"),
            ("Food Packet", "food_packet"), ("Dry Ration Packet", "dry_ration_packet"),
            ("Fodder Distribution", "fodder_distribution"),
        ],
        "Public Property Damage": [("Est Cost Of Property Damage", "est_cost_property_damage"),],
    }
    menu_items = list(kpi_options_for_menu.keys())


    # Session State Initialization 
    if 'selected_menu_memory' not in st.session_state:
        st.session_state.selected_menu_memory = menu_items[0]
    if 'selected_main_kpi_key' not in st.session_state:
        initial_kpis_for_default_menu = kpi_options_for_menu.get(st.session_state.selected_menu_memory, [])
        if initial_kpis_for_default_menu:
            st.session_state.selected_main_kpi_key = initial_kpis_for_default_menu[0][1]
        else:
            st.session_state.selected_main_kpi_key = default_kpi_key
    if 'district_list_metric_key' not in st.session_state:
        st.session_state.district_list_metric_key = st.session_state.selected_main_kpi_key
    if 'district_list_metric_label' not in st.session_state:
        st.session_state.district_list_metric_label = kpi_metric_mapping.get(st.session_state.selected_main_kpi_key, default_kpi_label)


    # HELPER FUNCTIONS 
    @st.cache_resource
    def init_db_connection():
        """Establishes a SQLAlchemy engine connection to the SQL Server database using Dashboard3.toml config."""
        try:
            from sqlalchemy import create_engine
            import os

            config_path = os.path.join(".streamlit", "Dashboard3.toml")
            if os.path.exists(config_path):
                # Reading the TOML file manually (since it's simple)
                with open(config_path, 'r') as f:
                    content = f.read()

                # Extracting values from the TOML content
                config = {}
                for line in content.split('\n'):
                    if '=' in line and not line.strip().startswith('#'):
                        key, value = line.split('=', 1)
                        config[key.strip()] = value.strip().strip('"')

                server = config.get('db_server', 'KAKA')
                database = config.get('db_database', 'eoc')
                connection_url = f"mssql+pyodbc://{server}/{database}?driver=ODBC+Driver+17+for+SQL+Server&trusted_connection=yes&TrustServerCertificate=yes"
            else:
                # Fallback connection string
                connection_url = "mssql+pyodbc://KAKA/eoc?driver=ODBC+Driver+17+for+SQL+Server&trusted_connection=yes&TrustServerCertificate=yes"

            engine = create_engine(connection_url)
            return engine
        except Exception as e:
            st.error(f"Database connection failed. Check `Dashboard3.toml` and ensure DB is running. Error: {e}")
            return None

    @st.cache_data(ttl=900)
    def load_data_from_db():
        """Fetches and prepares the main dataset from the SQL database."""
        engine = init_db_connection()
        if not engine:
            st.info("Database connection not available. Loading sample data for demonstration.")
            districts = [
                "ARARIA", "ARWAL", "AURANGABAD", "BANKA", "BEGUSARAI", "BHAGALPUR",
                "BHOJPUR", "BUXAR", "DARBHANGA", "GAYA", "GOPALGANJ", "JAHANABAD",
                "JAMUI", "KAIMUR (BHABUA)", "KATIHAR", "KHAGARIA", "KISHANGANJ",
                "LAKHISARAI", "MADHEPURA", "MADHUBANI", "MUNGER", "MUZAFFARPUR",
                "NALANDA", "NAWADA", "PASCHIM CHAMPARAN", "PATNA", "PURBI CHAMPARAN",
                "PURNIA", "ROHTAS", "SAHARSA", "SAMASTIPUR", "SARAN", "SHEIKHPURA",
                "SHEOHAR", "SITAMARHI", "SIWAN", "SUPAUL", "VAISHALI"
            ]
            data = []
            start_dt = date.today() - timedelta(days=1000)
            for i in range(1000):
                current_date = start_dt + timedelta(days=i)
                for district in districts:
                    is_affected = np.random.choice([True, False], p=[0.2, 0.8])
                    row = { 'District': district, 'Date': pd.to_datetime(current_date) }
                    for key in kpi_metric_mapping.keys():
                        row[key] = np.random.randint(0, 10000) if is_affected else 0
                    data.append(row)
            df_db = pd.DataFrame(data)
        else:
            sql_query = """
            SELECT
                dm.DistrictName AS District, m.RecordDate AS Date, d.pdHumanAffected AS pop_affected,
                d.pdMigratedPopulation AS pop_evacuated, d.pdFamilyAffected AS family_affected,
                d.pdDeadPeoples AS human_loss, d.pdAffectedAnimals AS animal_affected_total, 0 AS animal_loss,
                (d.pdPartlyAffectedKutchaHouses + d.pdPartlyAffectedPakkaHouses + d.pdAffectedHuts) AS total_house_damage,
                d.pdPartlyAffectedKutchaHouses AS kutcha_house_damage_dr, d.pdPartlyAffectedPakkaHouses AS pucca_house_damage_dr,
                d.pdAffectedHuts AS huts_damage_dr, 0 AS cost_damage_house_dr,
                (d.pdAffectedAgriLand + d.pdAffectedNonAgriLand) AS total_affected_area, d.pdAffectedAgriLand AS agriculture_area,
                d.pdAffectedNonAgriLand AS non_agriculture_area, d.pdDamagedCropArea AS crop_damage_area,
                d.pdDamagedFishSeedFarms AS damage_fisheries, d.pdDryRationPackets AS gr_distribution,
                d.pdPolytheneSheetDist AS polythene_sheet, d.pdFoodPackets AS food_packet,
                d.pdDryRationPackets AS dry_ration_packet, d.pdOtherItemsDist AS fodder_distribution,
                d.pdDamagedPublicPropVal AS est_cost_property_damage, d.pdMotorBoatToday AS fc_boats_total,
                d.pdReliefCentreOpened AS fc_relief_centres_total, d.pdPeopleRegistered AS fc_persons_in_relief_total,
                0 AS fc_comm_kitchens_total, d.pdPeopleDinner AS fc_meals_served_total,
                d.pdHealthCampToday AS fc_health_centres_total, d.pdPeopleTreated AS fc_persons_treated_total,
                d.pdAnimalCamps AS fc_vet_centres_total, d.pdAnimalsTreated AS fc_animals_treated_total
            FROM dbo.FloodMain AS m JOIN dbo.FloodDetailsCum AS d ON m.ID = d.ID JOIN dbo.mst_Districts AS dm ON m.DistrictCode = dm.DistrictCode;
            """
            try:
                df_db = pd.read_sql(sql_query, engine)
            except Exception as e:
                st.error(f"Failed to load data from the database table. Check your query. Error: {e}")
                return pd.DataFrame()
            # SQLAlchemy engines handle connection cleanup automatically

        db_to_geojson_map = {
            "PURBI CHAMPARAN": "EAST CHAMPARAN",
            "PASCHIM CHAMPARAN": "WEST CHAMPARAN"
        }
        df_db['District'] = df_db['District'].str.strip().str.upper()
        df_db['District'] = df_db['District'].replace(db_to_geojson_map)

        if 'Date' in df_db.columns:
            df_db['Date'] = pd.to_datetime(df_db['Date'], errors='coerce')
        else:
            df_db['Date'] = pd.to_datetime(date.today())
        for col in df_db.columns:
            if col not in ['Date', 'District']:
                df_db[col] = pd.to_numeric(df_db[col], errors='coerce').fillna(0)

        district_coords = {
            "ARARIA": {"lat": 26.15, "lon": 87.51}, "ARWAL": {"lat": 25.24, "lon": 84.67},
            "AURANGABAD": {"lat": 24.75, "lon": 84.37}, "BANKA": {"lat": 24.88, "lon": 86.92},
            "BEGUSARAI": {"lat": 25.42, "lon": 86.13}, "BHAGALPUR": {"lat": 25.24, "lon": 86.98},
            "BHOJPUR": {"lat": 25.56, "lon": 84.66}, "BUXAR": {"lat": 25.56, "lon": 83.97},
            "DARBHANGA": {"lat": 26.16, "lon": 85.90}, "GAYA": {"lat": 24.79, "lon": 85.00},
            "GOPALGANJ": {"lat": 26.46, "lon": 84.43}, "JAHANABAD": {"lat": 25.21, "lon": 84.98},
            "JAMUI": {"lat": 24.92, "lon": 86.22}, "KAIMUR (BHABUA)": {"lat": 25.04, "lon": 83.61},
            "KATIHAR": {"lat": 25.54, "lon": 87.58}, "KHAGARIA": {"lat": 25.50, "lon": 86.47},
            "KISHANGANJ": {"lat": 26.10, "lon": 87.93}, "LAKHISARAI": {"lat": 25.17, "lon": 86.09},
            "MADHEPURA": {"lat": 25.92, "lon": 86.78}, "MADHUBANI": {"lat": 26.36, "lon": 86.07},
            "MUNGER": {"lat": 25.37, "lon": 86.47}, "MUZAFFARPUR": {"lat": 26.12, "lon": 85.36},
            "NALANDA": {"lat": 25.13, "lon": 85.51}, "NAWADA": {"lat": 24.88, "lon": 85.53},
            "WEST CHAMPARAN": {"lat": 27.16, "lon": 84.35}, "PATNA": {"lat": 25.59, "lon": 85.13},
            "EAST CHAMPARAN": {"lat": 26.66, "lon": 84.91}, "PURNIA": {"lat": 25.77, "lon": 87.47},
            "ROHTAS": {"lat": 25.05, "lon": 84.01}, "SAHARSA": {"lat": 25.88, "lon": 86.60},
            "SAMASTIPUR": {"lat": 25.86, "lon": 85.78}, "SARAN": {"lat": 25.89, "lon": 84.86},
            "SHEIKHPURA": {"lat": 25.13, "lon": 85.85}, "SHEOHAR": {"lat": 26.51, "lon": 85.30},
            "SITAMARHI": {"lat": 26.59, "lon": 85.48}, "SIWAN": {"lat": 26.22, "lon": 84.36},
            "SUPAUL": {"lat": 26.12, "lon": 86.61}, "VAISHALI": {"lat": 25.98, "lon": 85.21},
        }
        df_db['Latitude'] = df_db['District'].str.upper().map(lambda name: district_coords.get(str(name).strip().upper(), {}).get('lat'))
        df_db['Longitude'] = df_db['District'].str.upper().map(lambda name: district_coords.get(str(name).strip().upper(), {}).get('lon'))

        return df_db

    def get_kpi_value(filtered_df, kpi_key, default_val=0):
        if not filtered_df.empty and kpi_key in filtered_df.columns:
            try:
                total = filtered_df[kpi_key].sum()
                if pd.notna(total) and total == int(total): return int(total)
                elif pd.notna(total): return round(total, 2)
                else: return default_val
            except Exception as e:
                print(f"Error calculating KPI for {kpi_key}: {e}")
                return default_val
        return default_val

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

    def generate_fy_list(df):
        if df.empty or 'Date' not in df.columns:
            return ["FY 2025-26", "FY 2024-25"]

        years = df['Date'].dt.year.unique()
        min_year, max_year = min(years), max(years)

        fy_list = ["All Time"]
        for year in range(max_year, min_year - 1, -1):
            fy_list.append(f"FY {year}-{year+1}")
        return fy_list

    def create_donut_chart_display(target_column, affected_count, total_count, label_text, color):
        actual_affected = max(0, affected_count)
        not_affected = max(0, total_count - actual_affected)
        fig_donut = go.Figure(data=[go.Pie(
            labels=["Affected", "Unaffected"], values=[actual_affected, not_affected], hole=.7,
            marker_colors=[color, 'rgba(0,0,0,0.05)'],
            textinfo='none', hoverinfo='label+value', sort=False, direction='clockwise'
        )])
        fig_donut.update_layout(
            annotations=[
                dict(text=f"{actual_affected:,}", x=0.5, y=0.55, font_size=14, showarrow=False, font_weight='bold', font_color=color),
                dict(text="Affected", x=0.5, y=0.40, font_size=7, showarrow=False, font_color=color, opacity=0.8)
            ], showlegend=False, margin=dict(t=5, b=5, l=5, r=5), height=120,
            paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)',
            font_family="IBM Plex Sans, sans-serif"
        )
        target_column.plotly_chart(fig_donut, use_container_width=True, config={'displayModeBar': False})
        target_column.markdown(
            f"""<div style='text-align:center; margin-top:-20px; margin-bottom: 15px;'>
                <strong style='font-size:0.75em;'>{label_text}</strong><br>
                <span style='font-size:0.65em; opacity:0.7;'>Unaff: {not_affected:,} / Tot: {total_count:,}</span>
            </div>""", unsafe_allow_html=True
        )

    # Custom CSS and JS
    css_style_block = """
    <style>
    .stApp {
        background-color: #F4F4F4 !important;
        margin: 0 !important; 
        padding: 0 !important; 
        overflow-x: hidden !important; 
        max-width: 100vw !important;
    }
    .block-container {
        max-width: 95% !important;
        padding: 0rem 1.5rem 1.5rem 1.5rem !important; 
    }
    :root {
        --primary-color: #0F62FE;
        --secondary-bg-color: #FFFFFF;
        --app-bg-color: #F4F4F4;
        --text-color: #161616;
        --sidebar-bg-color: #EAF0F6;
        --sidebar-text-color: #333a40;
        --card-border-color: #dee2e6;
        --card-shadow: 0 2px 4px rgba(0,0,0,0.05);
        --kpi-card-light-blue-bg: #EAF1FF;
        --custom-kpi-card-selected-bg: #dc3545;
    }
    
    [data-testid="stHeader"], [data-testid="stToolbar"] { display: none !important; }
    
    [data-testid="stSidebar"] {
        background-color: var(--sidebar-bg-color) !important; 
        min-width: 280px !important; max-width: 280px !important;
        border-right: 1px solid var(--card-border-color) !important; 
        box-shadow: 2px 0 5px rgba(0,0,0,0.05) !important; z-index: 1000;
    }
    [data-testid="stSidebar"] > div { background-color: var(--sidebar-bg-color) !important; }
    [data-testid="stSidebar"] * { color: var(--sidebar-text-color) !important; font-family: 'IBM Plex Sans', sans-serif !important;}
    

    
    [data-testid="stSidebar"] .stRadio > div > label { 
        background: transparent !important; color: var(--sidebar-text-color) !important; 
        border-radius: 4px !important; padding: 0.6rem 1rem !important; 
        margin-bottom: 0.3rem !important; font-weight: 400 !important;
        font-size: 0.9rem !important; border: none !important; width: 100% !important;
        transition: all 0.2s ease !important; 
        display: flex !important; align-items: center; justify-content: flex-start;
    }
    [data-testid="stSidebar"] .stRadio > div > label > div:first-child { display: none !important; } 
    [data-testid="stSidebar"] .stRadio > div > label:has(input:checked) { 
        background-color: var(--primary-color) !important; 
        color: var(--secondary-bg-color) !important; 
        font-weight: 500 !important;
    }
    [data-testid="stSidebar"] .stRadio > div > label:hover:not(:has(input:checked)) { 
        background-color: rgba(0,0,0,0.05) !important; 
        color: var(--primary-color) !important; 
    }
    
    .dashboard-header {
        background-color: #004C99; color: var(--secondary-bg-color);
        padding: 0.3375rem 1.0125rem; text-align: left; display: flex;
        align-items: center; border-bottom: 2.025px solid #ffc107;
        border-radius: 5.4px;
        box-shadow: 0 1.35px 2.7px rgba(0,0,0,0.1);
    }
    .dashboard-header .header-logo-img { height: 20.25px; margin-right: 10.125px; }
    .dashboard-header .header-title-block { flex-grow: 1; }
    .dashboard-header h1 {
        font-size: 1.0125rem; font-weight: bold; margin: 0 0 0.0675rem 0;
        line-height: 0.81; color: var(--secondary-bg-color);
    }
    .dashboard-header p.tagline { font-size: 0.54rem; margin: 0; color: #e0e0e0; opacity: 0.9; }
    
    .custom-kpi-card-row-container { margin-top: 1.5rem; margin-bottom: 1.5rem; padding: 0 0.1rem; }

    [data-testid="stButton"] > button {
        padding: 1rem !important;
        border-radius: 8px !important;
        text-align: center !important;
        width: 100% !important; 
        min-height: 100px; 
        height: 100%; 
        display: flex !important;
        flex-direction: column !important;
        justify-content: center !important;
        align-items: center !important;
        transition: all 0.2s ease-in-out;
        line-height: 1.4 !important;
        font-size: 0.9rem !important;
        font-weight: 500;
    }

    [data-testid="stButton"] > button:hover { 
        box-shadow: 0 4px 10px rgba(0,0,0,0.1) !important; 
        transform: scale(1.03);
    }
    [data-testid="stButton"] > button:focus {
        box-shadow: 0 0 0 2px var(--primary-color) !important;
    }

    [data-testid="stButton"] > button[kind="secondary"] {
        background-color: var(--kpi-card-light-blue-bg) !important;
        border: 1px solid var(--card-border-color) !important;
        color: var(--text-color) !important;
    }

    [data-testid="stButton"] > button[kind="secondary"]:hover {
        border-color: var(--primary-color) !important;
    }

    [data-testid="stButton"] > button[kind="primary"] {
        background-color: var(--custom-kpi-card-selected-bg) !important; 
        border: 1px solid var(--custom-kpi-card-selected-bg) !important;
        color: var(--secondary-bg-color) !important;
    }

    [data-testid="stButton"] > button[kind="primary"]:hover {
        background-color: #b02a37 !important; 
    }
    
    .footer-card { background-color: #343a40; color: #dee2e6; padding: 1rem; border-radius: 8px; margin-top: 1.5rem; text-align: center; box-shadow: 0 -1px 3px rgba(0,0,0,0.05); border-top: 1px solid var(--card-border-color); font-size: 0.8rem; box-sizing: border-box; }
    .footer-title { color: #ffc107 !important; font-size: 1rem !important; font-weight: 500 !important; margin-bottom: 0.5rem !important; }
    .footer-card p { margin-bottom: 0.25rem; font-size: 0.75rem;}
    </style>
    """
    st.markdown(css_style_block, unsafe_allow_html=True)

    # APPLICATION START: Load Data
    with st.spinner('Presenting the Flood Dashboard for you... Thank you for your Patience'):
        df_main = load_data_from_db()
    if df_main.empty:
        st.error(" Unable to load flood data. Please check database connection and try again.")
        st.info(" Ensure your database server is running and accessible.")
        st.stop()

    # Initial Filter Values
    initial_start_date = df_main["Date"].min().date() if not df_main["Date"].empty else date.today() - timedelta(days=30)
    initial_end_date = df_main["Date"].max().date() if not df_main["Date"].empty else date.today()

    if 'start_date_main_val' not in st.session_state:
        st.session_state.start_date_main_val = initial_start_date
    if 'end_date_main_val' not in st.session_state:
        st.session_state.end_date_main_val = initial_end_date

    # Sidebar Controls
    with st.sidebar:

        intended_menu_on_load = st.session_state.get('selected_menu_memory', menu_items[0])
        try:
            current_radio_idx = menu_items.index(intended_menu_on_load)
        except ValueError:
            current_radio_idx = 0

        radio_button_actual_selection = st.radio(
            "Navigation", menu_items,
            index=current_radio_idx,
            key="sidebar_menu_radio_key",
            label_visibility="collapsed"
        )

        if radio_button_actual_selection != st.session_state.get('selected_menu_memory'):
            st.session_state.selected_menu_memory = radio_button_actual_selection
            kpis_for_menu = kpi_options_for_menu.get(radio_button_actual_selection, [])
            if kpis_for_menu:
                first_kpi_key = kpis_for_menu[0][1]
                st.session_state.selected_main_kpi_key = first_kpi_key
                st.session_state.district_list_metric_key = first_kpi_key
                st.session_state.district_list_metric_label = kpi_metric_mapping.get(first_kpi_key)
            st.rerun()

        st.markdown("---")
        with st.expander("Geo-Data Debugger", expanded=False):
            st.info("This checks for mismatches between database and map file names.")
            try:
                with open("districts.json", "r", encoding="utf-8") as f:
                    geojson_data_debug = json.load(f)
                geojson_districts = {feature['properties']['district'].upper().strip() for feature in geojson_data_debug['features'] if 'district' in feature.get('properties', {})}
                db_districts = {dist.upper().strip() for dist in df_main['District'].unique() if isinstance(dist, str)}
                st.write(f"Districts in GeoJSON: `{len(geojson_districts)}`")
                st.write(f"Districts in Database: `{len(db_districts)}`")
                db_not_in_geojson = db_districts - geojson_districts
                geojson_not_in_db = geojson_districts - db_districts
                if not db_not_in_geojson and not geojson_not_in_db:
                    st.success(" All district names match!")
                else:
                    if db_not_in_geojson:
                        st.warning(" DB names NOT in GeoJSON:"); st.json(sorted(list(db_not_in_geojson)))
                    if geojson_not_in_db:
                        st.warning(" GeoJSON names NOT in DB:"); st.json(sorted(list(geojson_not_in_db)))
            except FileNotFoundError:
                st.error("`districts.json` not found. Cannot perform debug check.")
            except Exception as e:
                st.error(f"An error occurred during the debug check: {e}")

    # Main Page Header
    eoc_logo_header_base64 = get_image_as_base64("eoc_logo.png")
    header_logo_html = f'<img src="{eoc_logo_header_base64}" alt="EOC" class="header-logo-img">' if eoc_logo_header_base64 else ""
    st.markdown(f"""
        <div class="dashboard-header">
            {header_logo_html}
            <div class="header-title-block">
                <h1>Flood Dashboard</h1>
                <p class="tagline">Emergency Operations Center - Government of Bihar</p>
            </div>
        </div>
    """, unsafe_allow_html=True)

    # Horizontal Filters Below Header
    # Creating 4-column layout for the filters
    col1, col2, col3, col4 = st.columns([1, 1, 1, 1])

    with col1:
        fy_list = generate_fy_list(df_main)
        selected_fy = st.selectbox(
            "Financial Year", fy_list, key="fy_selector", index=0,
        )

        if selected_fy and selected_fy != st.session_state.get('fy_memory'):
            st.session_state.fy_memory = selected_fy
            if selected_fy == "All Time":
                st.session_state.start_date_main_val = initial_start_date
                st.session_state.end_date_main_val = initial_end_date
            else:
                start_year = int(selected_fy.split(" ")[1].split("-")[0])
                st.session_state.start_date_main_val = date(start_year, 4, 1)
                st.session_state.end_date_main_val = date(start_year + 1, 3, 31)
            st.rerun()

    with col2:
        status_filter = st.selectbox("Status", ["All", "Affected Only"], key="status_filter")

    with col3:
        start_date_input = st.date_input(
            "Start Date",
            value=st.session_state.start_date_main_val,
            key="start_date_main_dt",
            help="Select start date for custom range"
        )

    with col4:
        end_date_input = st.date_input(
            "End Date",
            value=st.session_state.end_date_main_val,
            key="end_date_main_dt",
            help="Select end date for custom range"
        )

    # Process date changes
    if start_date_input != st.session_state.start_date_main_val:
        st.session_state.start_date_main_val = start_date_input
        st.session_state.fy_memory = None
    if end_date_input != st.session_state.end_date_main_val:
        st.session_state.end_date_main_val = end_date_input
        st.session_state.fy_memory = None


    # Data Filtering
    df_filtered_by_date = df_main[
        (df_main["Date"].dt.date >= st.session_state.start_date_main_val) &
        (df_main["Date"].dt.date <= st.session_state.end_date_main_val)
    ].copy()

    if st.session_state.status_filter == 'Affected Only':
        primary_kpi_key = st.session_state.get('selected_main_kpi_key', default_kpi_key)
        affected_districts = df_filtered_by_date[df_filtered_by_date[primary_kpi_key] > 0]['District'].unique()
        df_filtered = df_filtered_by_date[df_filtered_by_date['District'].isin(affected_districts)].copy()
    else:
        df_filtered = df_filtered_by_date.copy()


    # KPI Cards Display using st.button and on_click callbacks 
    kpis_for_current_menu = kpi_options_for_menu.get(st.session_state.selected_menu_memory, [])

    def handle_kpi_click(kpi_key):
        """Callback to update session state when a KPI card is clicked."""
        st.session_state.selected_main_kpi_key = kpi_key
        st.session_state.district_list_metric_key = kpi_key
        st.session_state.district_list_metric_label = kpi_metric_mapping.get(kpi_key)

    st.markdown('<div class="custom-kpi-card-row-container">', unsafe_allow_html=True)
    if kpis_for_current_menu:
        num_kpis = len(kpis_for_current_menu)
        cols_per_row_config = 6
        kpi_idx = 0
        while kpi_idx < num_kpis:
            cols = st.columns(cols_per_row_config)
            for i in range(cols_per_row_config):
                if kpi_idx < num_kpis:
                    kpi_label, kpi_key = kpis_for_current_menu[kpi_idx]
                    with cols[i]:
                        value = get_kpi_value(df_filtered, kpi_key)
                        value_display = f"{int(value):,}" if isinstance(value, (int, float)) and pd.notna(value) else str(value)
                        is_selected = (kpi_key == st.session_state.get('selected_main_kpi_key'))

                        button_label = f"{value_display} {kpi_label}"

                        st.button(
                            label=button_label,
                            key=f"kpi_btn_{kpi_key}",
                            on_click=handle_kpi_click,
                            args=(kpi_key,),
                            type="primary" if is_selected else "secondary",
                            use_container_width=True
                        )
                    kpi_idx += 1
    else:
        st.info(f"No specific summary KPIs to display for {st.session_state.selected_menu_memory} in this view.")
    st.markdown('</div>', unsafe_allow_html=True)


    # Map and Bar Chart
    st.markdown("---")
    map_col, district_list_col = st.columns([0.65, 0.35], gap="large")

    with map_col:
        geojson_path = "districts.json"
        try:
            with open(geojson_path, "r", encoding="utf-8") as f:
                geojson_data = json.load(f)
        except Exception as e:
            st.error(f"Could not load GeoJSON file: {e}")
            geojson_data = None

        if geojson_data:
            fig_map = go.Figure()

            numeric_kpi_cols = list(kpi_metric_mapping.keys())
            df_filtered['District_Normalized'] = df_filtered['District'].str.strip().str.upper()
            df_district_summary = df_filtered.groupby('District_Normalized')[numeric_kpi_cols].sum().reset_index()
            df_district_summary = df_district_summary.set_index('District_Normalized')

            kpis_for_hover = kpi_options_for_menu.get(st.session_state.selected_menu_memory, [])
            hovertemplate = "<b>%{text}</b><br><br>" + "<br>".join([f"{label}: %{{customdata[{i}]}}" for i, (label, key) in enumerate(kpis_for_hover)]) + "<extra></extra>"

            primary_kpi_key = st.session_state.get('selected_main_kpi_key', default_kpi_key)
            if primary_kpi_key not in df_district_summary.columns:
                df_district_summary[primary_kpi_key] = 0
            df_district_summary['is_affected'] = df_district_summary[primary_kpi_key] > 0

            for feature in geojson_data["features"]:
                district_name = feature["properties"]["district"].strip().upper()

                color = "#dc3545" if df_district_summary.get('is_affected', {}).get(district_name, False) else "#D0D0D0"
                geom = feature.get("geometry", {})
                polygons = geom.get("coordinates", [])
                if geom.get("type") == "Polygon":
                    polygons = [polygons]

                custom_data_for_district = []
                if district_name in df_district_summary.index:
                    district_row = df_district_summary.loc[district_name]
                    for _, key in kpis_for_hover:
                        custom_data_for_district.append(f"{int(district_row.get(key, 0)):,}")
                else:
                    for _, key in kpis_for_hover:
                        custom_data_for_district.append("0")

                for poly in polygons:
                    if not poly: continue
                    exterior_ring = poly[0]
                    if not exterior_ring or len(exterior_ring) < 3: continue
                    lons, lats = zip(*exterior_ring)

                    # Layer 1: Visible colored layer with border
                    fig_map.add_trace(go.Scattermapbox(
                        lon=list(lons),
                        lat=list(lats),
                        mode="lines",
                        fill="toself",
                        fillcolor=color,
                        line=dict(color="black", width=1),
                        hoverinfo="none",
                        showlegend=False
                    ))

                    # Layer 2: Invisible hover-only layer
                    fig_map.add_trace(go.Scattermapbox(
                        lon=list(lons),
                        lat=list(lats),
                        mode="lines",
                        fill="toself",
                        fillcolor="rgba(0,0,0,0)",
                        line=dict(width=0),
                        hoverinfo="text",
                        text=[district_name.title()] * len(lons),
                        customdata=np.array([custom_data_for_district] * len(lons)),
                        hovertemplate=hovertemplate,
                        hoverlabel=dict(bgcolor="#161616", font_size=12, bordercolor="black", font_family="IBM Plex Sans, sans-serif"),
                        showlegend=False
                    ))

            fig_map.update_layout(
                mapbox_style="white-bg",
                mapbox_center={"lat": 25.78, "lon": 85.77},
                mapbox_zoom=6.2,
                margin={"r":0,"t":0,"l":0,"b":0},
                height=520,
                showlegend=False
            )
            st.plotly_chart(fig_map, use_container_width=True, config={'displayModeBar': False})

    with district_list_col:
        active_metric_display_label = st.session_state.district_list_metric_label
        active_metric_key_for_list = st.session_state.district_list_metric_key
        st.markdown(f"**{active_metric_display_label} by District (Total for Period)**")

        all_districts = sorted(df_main['District'].unique())
        district_data_sum = df_filtered.groupby("District")[active_metric_key_for_list].sum()

        district_data_bar = district_data_sum.reindex(all_districts, fill_value=0).sort_values(ascending=False)

        if not district_data_bar.empty:
            fig_bar = go.Figure(go.Bar(
                x=district_data_bar.values,
                y=district_data_bar.index,
                orientation='h',
                text=district_data_bar.apply(lambda x: f'{x:,.0f}' if x > 0 else ''),
                textposition='auto',
                marker_color='#004C99',
                marker_line_color='white',
                marker_line_width=1.5
            ))
            fig_bar.update_layout(
                height=480, margin=dict(t=25, b=0, l=10, r=20),
                yaxis=dict(autorange="reversed"),
                xaxis=dict(showticklabels=False),
                plot_bgcolor='rgba(0,0,0,0)',
                paper_bgcolor='rgba(0,0,0,0)',
                font_family="IBM Plex Sans, sans-serif"
            )
            st.plotly_chart(fig_bar, use_container_width=True, config={'displayModeBar': False})
        else:
            st.info("No affected districts for this metric.")


    # Drill-down KPI Section 
    st.markdown("---")
    st.subheader("District Details")
    col1, col2 = st.columns(2)
    metric_key = st.session_state.get('selected_main_kpi_key', default_kpi_key)

    with col1:
        with st.expander(" View All Districts", expanded=True):
            # Using total values for the period for this table
            df_table_data = df_filtered.groupby('District')[metric_key].sum().reset_index()
            df_table = df_table_data[['District', metric_key]].sort_values(metric_key, ascending=False)
            st.dataframe(
                df_table.style.format({metric_key: "{:,.0f}"}).background_gradient(cmap='OrRd', subset=[metric_key]),
                use_container_width=True,
                height=400 # Making it scrollable
            )
    with col2:
        with st.expander(" Trends for Selected District", expanded=True):
            # Using the full filtered dataset for trend analysis
            unique_districts = sorted(df_filtered['District'].unique())
            if unique_districts:
                district_choice = st.selectbox("Choose a District", unique_districts)

                if district_choice:
                    kpi_label = kpi_metric_mapping.get(metric_key, metric_key)
                    df_trend = df_filtered[df_filtered['District'] == district_choice].groupby('Date')[metric_key].sum().reset_index()
                    fig_trend_line = px.line(df_trend, x='Date', y=metric_key, title=f"{kpi_label} in {district_choice.title()}")
                    fig_trend_line.update_layout(
                        margin=dict(l=20, r=20, t=40, b=20),
                        height=320
                    )
                    st.plotly_chart(fig_trend_line, use_container_width=True)
                else:
                    st.info("No districts with data in the selected period.")


    # Daily Trends and Donut Charts
    st.markdown("<br>", unsafe_allow_html=True)
    TOTAL_DISTRICTS, TOTAL_BLOCKS, TOTAL_NAGARS, TOTAL_PANCHAYATS = 38, 534, 200, 8386
    affected_districts_count = df_filtered[df_filtered[default_kpi_key] > 0]['District'].nunique() if not df_filtered.empty else 0
    affected_blocks_count = int(affected_districts_count * 5) if affected_districts_count > 0 else 0
    affected_panchayats_count = int(affected_blocks_count * 4) if affected_blocks_count > 0 else 0

    donut_cols = st.columns(4)
    create_donut_chart_display(donut_cols[0], affected_districts_count, TOTAL_DISTRICTS, "Districts", '#004C99')
    create_donut_chart_display(donut_cols[1], affected_blocks_count, TOTAL_BLOCKS, "Blocks", '#28a745')
    create_donut_chart_display(donut_cols[2], 0, TOTAL_NAGARS, "Nagars", '#ffc107')
    create_donut_chart_display(donut_cols[3], affected_panchayats_count, TOTAL_PANCHAYATS, "Panchayats", '#dc3545')


    trend_graph_col1, trend_graph_col2 = st.columns(2)
    s_date_dt = st.session_state.start_date_main_val
    e_date_dt = st.session_state.end_date_main_val
    all_days_range = pd.date_range(s_date_dt, e_date_dt, freq='D')

    with trend_graph_col1:
        st.markdown("##### Daily Affected Districts")
        if not df_filtered.empty:
            daily_counts = df_filtered[df_filtered[default_kpi_key] > 0].groupby(df_filtered['Date'].dt.date)['District'].nunique().reindex(all_days_range.date, fill_value=0)
        else:
            daily_counts = pd.Series(0, index=all_days_range.date)
        daily_counts.index = pd.to_datetime(daily_counts.index)
        fig_trends_districts = go.Figure()
        fig_trends_districts.add_trace(go.Scatter(x=daily_counts.index, y=daily_counts.values, mode='lines', name='Districts Affected', line=dict(color='#004C99', width=3, shape='spline'), fill='tozeroy', fillcolor='rgba(0, 76, 153, 0.1)'))
        fig_trends_districts.update_layout(height=270, margin=dict(t=30, b=50, l=60, r=20), paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)', xaxis=dict(gridcolor='#E0E0E0', showline=False, zeroline=False), yaxis=dict(gridcolor='#E0E0E0', showline=False, zeroline=False), font_family="IBM Plex Sans, sans-serif", font_color="#161616", yaxis_title="Affected Districts", xaxis_title="Date", hovermode="x unified", showlegend=False)
        st.plotly_chart(fig_trends_districts, use_container_width=True, config={'displayModeBar': False})

    with trend_graph_col2:
        st.markdown("##### Daily Persons in Relief")
        if not df_filtered.empty:
            daily_relief = df_filtered.groupby(df_filtered['Date'].dt.date)['fc_persons_in_relief_total'].sum().reindex(all_days_range.date, fill_value=0)
        else:
            daily_relief = pd.Series(0, index=all_days_range.date)
        daily_relief.index = pd.to_datetime(daily_relief.index)
        fig_trends_relief = go.Figure()
        fig_trends_relief.add_trace(go.Scatter(x=daily_relief.index, y=daily_relief.values, mode='lines', name='Persons in Relief', line=dict(color='#28a745', width=3, shape='spline'), fill='tozeroy', fillcolor='rgba(40, 167, 69, 0.05)'))
        fig_trends_relief.update_layout(height=270, margin=dict(t=30, b=50, l=60, r=20), paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)', xaxis=dict(gridcolor='#E0E0E0', showline=False, zeroline=False), yaxis=dict(gridcolor='#E0E0E0', showline=False, zeroline=False), font_family="IBM Plex Sans, sans-serif", font_color="#161616", yaxis_title="Total Persons in Relief", xaxis_title="Date", hovermode="x unified", showlegend=False)
        st.plotly_chart(fig_trends_relief, use_container_width=True, config={'displayModeBar': False})


    # Footer
    st.markdown(f'''<div class="footer-card" style="margin-top: 2rem;">
        <h4 class="footer-title"> Bihar Disaster Management Dashboard</h4>
        <p>Built with Streamlit & Plotly | Last updated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}</p>
        <p>Data visualization for disaster preparedness and emergency response planning.</p>
        <p style="font-size: 0.7rem; margin-top: 0.4rem;">🏛️ Government of Bihar | Emergency Operations Center</p>
        </div>''', unsafe_allow_html=True)

if __name__ == "__main__":
    run()

