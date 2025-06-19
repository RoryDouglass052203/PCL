# competitor_map.py
# ▸ Interactive map of major solar EPC competitors
# ▸ Duplicate HQs are auto-jittered ~120 m apart
# ▸ Run with:  streamlit run competitor_map.py
# ------------------------------------------------------------
import streamlit as st
import pandas as pd
import pydeck as pdk
import math

st.set_page_config(
    page_title="Competitor HQ Map",
    page_icon="🌍",
    layout="wide",
)

# ── 1. Competitor data (37 firms) ────────────────────────────
competitors = [
    # North American competitors
    ("Grupo Ortiz",        40.2203,  -3.3630,   "https://www.grupoortiz.com/en/lines-of-business/energy/"),
    ("NoBull Energy",      43.6532,  -79.3832,  "https://nobullenergy.com/projects"),
    ("WHC ",               30.0932,  -91.5842,  "https://whcenergyservices.com/power-construction/"),
    ("Webber",             29.5530,  -95.2153,  "https://www.webber.us/our-work/renewable-energy"),
    ("Moss",               26.1230,  -80.0909,  "https://moss.com/markets/solar/"),
    ("Primoris",           32.4719,  -96.4823,  "https://www.prim.com/projects"),
    ("SOLV Energy",        33.0059, -117.0459,  "https://www.solvenergy.com/projects"),
    ("Quanta Services",    29.4822,  -95.2643,  "https://www.quantaservices.com/projects"),
    ("Black & Veatch",     38.5531,  -94.3919,  "https://www.bv.com/our-work"),
    ("Kiewit",             41.1601,  -95.5611,  "https://www.kiewit.com/projects/power/renewable-energy"),
    ("McCarthy",           38.3613,  -90.2724,  "https://www.mccarthy.com/work/solar"),
    ("Mortensen",          44.5908,  -93.1944,  "https://www.mortenson.com/projects?tags=solar"),
    ("RES Group",          39.4521,  -104.5947, "https://www.res-group.com/en/projects"),
    ("Q CELLS",            33.3919,  -117.4449, "https://www.qcells.com/us/en/products/large-scale/"),
    ("Borea Construction", 46.4224,  -71.1756,  "https://boreaconstruction.com/en/projects"),
    ("GRS Energy",         40.3203,  -3.3720,   "https://grs.energy/en/projects"),
    ("Bechtel",            38.5718,  -77.2125,  "https://www.bechtel.com/projects/energy/"),
    ("GP Joule",           54.4636,    9.2731,  "https://www.gp-joule.com/en/projects"),
    ("Goldbeck Solar",     50.5320,    6.5412,  "https://goldbecksolar.com/en/projects/"),
    ("LPL Solar",          26.0512,  -80.0819,  "https://lpl.com/solar"),
    ("DEP COM Power",      33.3330, -111.5259,  "https://www.depcompower.com/what-we-do/projects"),
    ("Alltrade",           42.2920,  -83.1803,  "https://alltradeindustrial.com/projects"),
    ("Rosendin",           37.2147, -121.5253,  "https://www.rosendin.com/projects/?_markets=renewable-energy"),
    # Australian competitors
    ("Beon Energy",        -37.4901, 144.5742,  "https://beon-es.com.au/projects"),
    ("UGL",                -33.5023, 151.1222,  "https://ugl.com.au/our-projects"),
    ("Bouygues",            48.4709,   2.0417,  "https://www.bouygues-es.com/en/energy-solutions/solar-power/"),
    ("Acciona",             40.2801,  -3.3932,  "https://www.acciona.com/our-projects/"),
    ("DT Infrastructure",  -27.2802, 153.0035,  "https://dtinfrastructure.com.au/projects/"),
    ("Ferrovial",           40.2744,  -3.3719,  "https://www.ferrovial.com/en-us/projects/"),
    ("Green Grid Connect", -27.2749, 153.0145,  "https://greengridconnect.com.au/projects/"),
    ("Enerven",            -34.5422, 138.3429,  "https://enerven.com.au/project/"),
    ("RJE Global",         -34.5903, 138.3219,  "https://www.rje.com.au/projects/"),
    ("CPP",                -34.5555, 138.3633,  "https://cpp.com.au/projects"),
    ("TEC-C",              -33.5241, 151.1407,  "https://www.tec-c.com.au/projects"),
    ("Decmil",             -31.5458, 115.4854,  "https://decmil.com/projects/"),
    ("Wolff Power",        -27.3244, 151.5502,  "https://wolffpower.com.au/our-projects/"),
    ("BMD Group",          -27.2258, 153.1033,  "https://www.bmd.com.au/projects/"),
]

df = pd.DataFrame(competitors, columns=["Company", "Lat", "Lon", "Projects_Link"])

# ── 2. Jitter duplicates so overlapping markers separate ────
def jitter_duplicates(dataframe, radius_m=120):
    """Offset companies sharing identical coords by ≤radius_m in a circle."""
    groups = dataframe.groupby([dataframe["Lat"].round(4), dataframe["Lon"].round(4)], group_keys=False)
    out = []
    for _, grp in groups:
        n = len(grp)
        if n == 1:
            out.append(grp)
        else:
            r_deg = radius_m / 111_320  # metres → degrees lat
            for idx, (_, row) in enumerate(grp.iterrows()):
                angle = idx * (2 * math.pi / n)
                dlat = r_deg * math.sin(angle)
                dlon = r_deg * math.cos(angle) / math.cos(math.radians(row["Lat"]))
                row["Lat"] += dlat
                row["Lon"] += dlon
                out.append(pd.DataFrame([row]))
    return pd.concat(out, ignore_index=True)

df = jitter_duplicates(df)

# ── 3. Tooltip HTML (clickable link) ─────────────────────────
df["tooltip"] = (
    "<b>" + df["Company"] + "</b><br>"
    "<a href='" + df["Projects_Link"] + "' target='_blank'>Projects ↗</a>"
)

# ── 4. Render map ────────────────────────────────────────────
st.title("🗺️ Competitor Headquarters Map")
st.markdown("Nearby HQs are slightly offset so each company is individually clickable.")

deck = pdk.Deck(
    map_style="mapbox://styles/mapbox/light-v9",
    initial_view_state=pdk.ViewState(
        latitude=df["Lat"].mean(),
        longitude=df["Lon"].mean(),
        zoom=2.2,
    ),
    layers=[
        pdk.Layer(
            "ScatterplotLayer",
            data=df,
            get_position="[Lon, Lat]",
            get_radius=200,
            radius_min_pixels=3, 
            get_fill_color=[255, 140, 0, 160],
            pickable=True,
            auto_highlight=True,
        )
    ],
    tooltip={"html": "{tooltip}", "style": {"color": "white"}},
)

st.pydeck_chart(deck, use_container_width=True, height=650)

st.caption(
    "Dots for companies sharing the same city are auto-jittered ~120 m so you can click each one."
)




