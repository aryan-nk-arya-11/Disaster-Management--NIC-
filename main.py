import streamlit as st
import importlib
import base64

# UI config
st.set_page_config(page_title="Unified Dashboard App", layout="wide")

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

dashboards = {
    "Cold Wave Dashboard": "Dashboard1",
    "Incident Dashboard": "Dashboard2",
    "Flood Dashboard": "Dashboard3"
}

# Sidebar logos and selection
with st.sidebar:
    # Displaying logos at the top
    eoc_logo_base64 = get_image_as_base64("eoc_logo.png")
    bihar_logo_base64 = get_image_as_base64("bihar_govt.png")

    st.markdown("""
    <style>
    /* Making sidebar narrower */
    .css-1d391kg, .css-1lcbm7v, .css-1v3fv7u {
        width: 250px !important;
        min-width: 250px !important;
        max-width: 250px !important;
    }
    section[data-testid="stSidebar"] {
        width: 250px !important;
        min-width: 250px !important;
        max-width: 250px !important;
    }
    section[data-testid="stSidebar"] > div {
        width: 250px !important;
        min-width: 250px !important;
        max-width: 250px !important;
    }
    .sidebar-logo {
        text-align: center;
        padding: 0.5rem 0.5rem 1.5rem;
        margin-bottom: 1rem;
    }
    .sidebar-logo img {
        filter: none;
        margin: 0.5rem;
        width: 100px;
        height: auto;
    }
    .sidebar-logo img[alt="Bihar Logo"] {
        width: 110px;
    }
    .bihar-text {
        font-size: 0.8rem !important;
        color: #333a40 !important;
        font-weight: 'bold' !important;
        text-shadow: none !important;
    }
    </style>
    """, unsafe_allow_html=True)

    # Displaying the logos
    logo_html = f'''
    <div class="sidebar-logo">
        <img src="{eoc_logo_base64}" alt="EOC Logo"><br>
        <img src="{bihar_logo_base64}" alt="Bihar Logo">
        <div class="bihar-text">बिहार सरकार</div>
    </div>
    '''
    st.markdown(logo_html, unsafe_allow_html=True)

selected = st.sidebar.radio("Select a dashboard:", list(dashboards.keys()))

# Displaying info about selected dashboard in sidebar
with st.sidebar:
    st.markdown("---")
    if selected == "Cold Wave Dashboard":
        st.info("**Cold Wave Dashboard** - Monitor and manage cold wave incidents, affected populations, relief operations, and resource allocation across Bihar districts.")
    elif selected == "Incident Dashboard":
        st.info("**Incident Dashboard** - Track incidents, casualties, and emergency response operations with detailed analytics and geographical distribution.")
    elif selected == "Flood Dashboard":
        st.info("**Flood Dashboard** - Comprehensive flood management system with real-time monitoring, district-wise analysis, and disaster response coordination.")

# Importing and running selected dashboard
try:
    dashboard_module = dashboards[selected]
    dashboard = importlib.import_module(dashboard_module)
    dashboard.run()
except Exception as e:
    st.error(f"Failed to run {selected}. Error:\n\n{e}")