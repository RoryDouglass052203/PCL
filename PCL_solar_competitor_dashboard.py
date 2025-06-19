# solar_dashboard.py
# ▸ Integrated dashboard with news, policy, and HQ map
# ▸ Uses precise building coordinates for competitors
# -------------------------------------------------------------------
import streamlit as st
import pandas as pd
import pydeck as pdk
import base64
from pathlib import Path

st.set_page_config(
    page_title="Competitor and News Dashboard",
    layout="wide",
    page_icon="📡",
)

# --- Logo + (optional) title row ----------------------------------
logo_path = "C:/Users/RDDouglass/OneDrive - PCL Construction/PCL Solar Logo.png"       

# create two columns: narrow for logo, wide for anything else
col_logo, col_spacer = st.columns([1, 12], gap="small")

with col_logo:
    st.image(logo_path, width=350)       

# (optional) put the dashboard title next to the logo
with col_spacer:
    st.markdown(
        "<h2 style='margin-top:18px;'>Solar Intelligence Dashboard</h2>",
        unsafe_allow_html=True,
    )


# ─────────────────────────────────────────────────────────────
# 1. Helpers
# ─────────────────────────────────────────────────────────────
CANDIDATES = {
    "Date Scraped": {"date_scraped", "published_at", "scraped_date", "Date Scraped"},
    "Title": {"title", "headline", "Title"},
    "Source": {"source", "publisher", "Source"},
    "Link": {"url", "URL", "link", "article_url", "Link"},
}

def standardise_columns(df):
    ren = {}
    for canon, variants in CANDIDATES.items():
        for v in variants:
            if v in df.columns:
                ren[v] = canon
                break
    return df.rename(columns=ren)

def load_csv(path, parse_dates=True):
    if not Path(path).exists():
        return pd.DataFrame()
    df = pd.read_csv(path)
    df = standardise_columns(df)
    if parse_dates and "Date Scraped" in df.columns:
        df["Date Scraped"] = pd.to_datetime(df["Date Scraped"], errors="coerce", utc=True)
        df["Date Scraped"] = df["Date Scraped"].dt.tz_convert(None)
    return df

def download_link(label, path):
    fp = Path(path)
    if not fp.exists():
        st.write(f"🔸 {fp.name} (missing)")
        return
    data = fp.read_bytes()
    b64 = base64.b64encode(data).decode()
    href = f'<a href="data:application/octet-stream;base64,{b64}" download="{fp.name}">{label}</a>'
    st.markdown(href, unsafe_allow_html=True)

# ─────────────────────────────────────────────────────────────
# 2. Load your CSV feeds
# ─────────────────────────────────────────────────────────────
PCL_PATH, IND_PATH, POLICY_PATH = "PCL_solar_news.csv", "utility_scale_solar_news.csv", "policy_news.csv"
XLSX_PATH = "C:/Users/RDDouglass/OneDrive - PCL Construction/Competitor Analysis North America and Australia.xlsx"
COMP_NEWS_PATH = "competitor_solar_news.csv"

pcl_df    = load_csv(PCL_PATH)
ind_df    = load_csv(IND_PATH)
policy_df = load_csv(POLICY_PATH)
comp_news_df = load_csv(COMP_NEWS_PATH)

COMP_NEWS_PATH = "competitor_solar_news.csv"
comp_news_df = load_csv(COMP_NEWS_PATH) 

# ─────────────────────────────────────────────────────────────
# 3. Your accurate HQ list (no jitter needed)
# ─────────────────────────────────────────────────────────────
competitors = [
    # Add all 37 here – trimmed for brevity in this view
    ("Grupo Ortiz",        40.2203,  -3.3630,   "https://www.grupoortiz.com/en/lines-of-business/energy/"),
    ("NoBull Energy",      39.7691,  -86.1580,  "https://nobullenergy.com/projects"),
    ("WHC ",               30.1471,  -91.9612,  "https://whcenergyservices.com/power-construction/"),
    ("Webber",             30.1658,  -95.4611,  "https://www.webber.us/our-work/renewable-energy"),
    ("Moss",               26.2306,  -80.1251,  "https://moss.com/markets/solar/"),
    ("Primoris",           32.7767,  -96.7970,  "https://www.prim.com/projects"),
    ("SOLV Energy",        33.0059, -117.0459,  "https://www.solvenergy.com/projects"),
    ("Quanta Services",    29.7601,  -95.3701,  "https://www.quantaservices.com/projects"),
    ("Black & Veatch",     38.9847,  -94.6776,  "https://www.bv.com/our-work"),
    ("Kiewit",             41.2565,  -95.9345,  "https://www.kiewit.com/projects/power/renewable-energy"),
    ("McCarthy",           38.6313,  -90.2024,  "https://www.mccarthy.com/work/solar"),
    ("Mortensen",          44.9778,  -93.2650,  "https://www.mortenson.com/projects?tags=solar"),
    ("RES Group",          39.7392,  -104.9903, "https://www.res-group.com/en/projects"),
    ("Q CELLS",            33.6846,  -117.8265, "https://www.qcells.com/us/en/products/large-scale/"),
    ("Borea Construction", 46.6952,  -71.3855,  "https://boreaconstruction.com/en/projects"),
    ("GRS Energy",         40.3203,  -3.3720,   "https://grs.energy/en/projects"),
    ("Bechtel",            38.9586,  -77.3570,  "https://www.bechtel.com/projects/energy/"),
    ("GP Joule",           54.4636,    9.2731,  "https://www.gp-joule.com/en/projects"),
    ("Goldbeck Solar",     50.5320,    6.5412,  "https://goldbecksolar.com/en/projects/"),
    ("LPL Solar",          26.1224,  -80.1373,  "https://lpl.com/solar"),
    ("DEP COM Power",      33.4949, -111.9217,  "https://www.depcompower.com/what-we-do/projects"),
    ("Alltrade",           42.2920,  -83.1803,  "https://alltradeindustrial.com/projects"),
    ("Rosendin",           37.3387,  -121.8853,  "https://www.rosendin.com/projects/?_markets=renewable-energy"),
    # Australian competitors
    ("Beon Energy",        -37.8136, 144.9631,  "https://beon-es.com.au/projects"),
    ("UGL",                -33.8368, 151.2073,  "https://ugl.com.au/our-projects"),
    ("Bouygues",            48.4709,   2.0417,  "https://www.bouygues-es.com/en/energy-solutions/solar-power/"),
    ("Acciona",             40.2801,  -3.3932,  "https://www.acciona.com/our-projects/"),
    ("DT Infrastructure",  -27.2802, 153.0035,  "https://dtinfrastructure.com.au/projects/"),
    ("Ferrovial",           40.2744,  -3.3719,  "https://www.ferrovial.com/en-us/projects/"),
    ("Green Grid Connect", -27.2749, 153.0145,  "https://greengridconnect.com.au/projects/"),
    ("Enerven",            -34.8992, 138.5752,  "https://enerven.com.au/project/"),
    ("RJE Global",         -34.9884, 138.5397,  "https://www.rje.com.au/projects/"),
    ("CPP",                -34.9285, 138.6007,  "https://cpp.com.au/projects"),
    ("TEC-C",              -33.8688, 151.2093,  "https://www.tec-c.com.au/projects"),
    ("Decmil",             -31.9032, 115.8185,  "https://decmil.com/projects/"),
    ("Wolff Power",        -27.3244, 151.5502,  "https://wolffpower.com.au/our-projects/"),
    ("BMD Group",          -27.2258, 153.1033,  "https://www.bmd.com.au/projects/"),
    
]

df_map = pd.DataFrame(competitors, columns=["Company", "Lat", "Lon", "Projects_Link"])
df_map["tooltip"] = (
    "<b>" + df_map["Company"] + "</b><br>"
    "<a href='" + df_map["Projects_Link"] + "' target='_blank'>Projects ↗</a>"
)

# ─────────────────────────────────────────────────────────────
# 4. Build dashboard layout
# ─────────────────────────────────────────────────────────────
tabs = st.tabs(["📰 News", "⚖️ Policy", "🗺️ Competitors", "📁 Downloads"])

# ── Tab 1: News
with tabs[0]:
    st.header("📰 PCL Mentions + Industry News")
    c1, c2 = st.columns(2)
    with c1:
        st.subheader("🏗️ PCL Mentions")
        if pcl_df.empty:
            st.info("Waiting for PCL news feed...")
        else:
            st.dataframe(pcl_df[["Date Scraped", "Title", "Source", "Link"]].sort_values("Date Scraped", ascending=False), use_container_width=True)

    with c2:
        st.subheader("⚡ Industry News")
        if ind_df.empty:
            st.info("Waiting for industry news...")
        else:
            st.dataframe(ind_df[["Date Scraped", "Title", "Source", "Link"]].sort_values("Date Scraped", ascending=False), use_container_width=True)

# ── Tab 2: Policy
with tabs[1]:
    st.header("⚖️ Policy Headlines (CA / US / AU)")
    if policy_df.empty:
        st.info("Policy headlines will appear here once scraped.")
    else:
        countries = ["All"] + sorted(policy_df["Country"].dropna().unique())
        choice = st.selectbox("Filter by country:", countries, index=0)
        pdf = policy_df if choice == "All" else policy_df[policy_df["Country"] == choice]
        st.dataframe(pdf[["Date Scraped", "Country", "Title", "Source", "Link"]].sort_values("Date Scraped", ascending=False), use_container_width=True)

# ── Tab 3: Map + Solar Announcements ─────────────────────────
with tabs[2]:
    st.header("🗺️ Competitor Information")
    st.markdown("Each orange dot shows the location of a competitor’s main office.")

    st.pydeck_chart(
        pdk.Deck(
            map_style="mapbox://styles/mapbox/light-v9",
            initial_view_state=pdk.ViewState(
                latitude=df_map["Lat"].mean(),
                longitude=df_map["Lon"].mean(),
                zoom=2.2,
            ),
            layers=[
                pdk.Layer(
                    "ScatterplotLayer",
                    data=df_map,
                    get_position="[Lon, Lat]",
                    get_radius=200,
                    radius_min_pixels=3,
                    get_fill_color=[255, 140, 0, 180],
                    pickable=True,
                    auto_highlight=True,
                )
            ],
            tooltip={"html": "{tooltip}", "style": {"color": "white"}},
        ),
        use_container_width=True,
        height=600
    )

    # ---- Solar news feed ------------------------------------
    st.subheader("📰 Latest Competitor Announcements")
    if comp_news_df.empty:
        st.info("No solar-specific announcements scraped yet.")
    else:
        companies = ["All"] + sorted(comp_news_df["Company"].unique())
        pick = st.selectbox("Filter by company:", companies, index=0)
        news = comp_news_df if pick == "All" else comp_news_df[comp_news_df["Company"] == pick]
        st.dataframe(
            news[["Date Scraped", "Company", "Title", "Source", "Link"]]

        )

# ── Tab 4: Downloads
with tabs[3]:
    st.header("📁 Download Source Files")
    download_link("⬇️ PCL News CSV", PCL_PATH)
    download_link("⬇️ Industry News CSV", IND_PATH)
    download_link("⬇️ Policy Headlines CSV", POLICY_PATH)
    download_link("⬇️ Competitor Workbook (Excel)", XLSX_PATH)

# Footer
st.markdown(
    f"<div style='text-align:center;color:gray;'>Dashboard refreshed: "
    f"<b>{pd.Timestamp.now():%Y-%m-%d %H:%M}</b></div>",
    unsafe_allow_html=True,
)









