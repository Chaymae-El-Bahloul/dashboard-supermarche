"""
Analyse des Performances Commerciales — Supermarché Myanmar
Tableau de Bord Décisionnel ·  2019
"""

import streamlit as st
import pandas as pd
import numpy as np
import plotly.graph_objects as go
import plotly.express as px
from plotly.subplots import make_subplots
from datetime import timedelta
import os, warnings
warnings.filterwarnings("ignore")

# ══════════════════════════════════════════════════════════════
# PAGE CONFIG
# ══════════════════════════════════════════════════════════════
st.set_page_config(
    page_title="Analyse Commerciale — Supermarché Myanmar",
    layout="wide",
    initial_sidebar_state="collapsed",
)

# ══════════════════════════════════════════════════════════════
# SESSION STATE
# ══════════════════════════════════════════════════════════════
for k, v in {"dark": True, "kpi_field": None, "kpi_val": None}.items():
    if k not in st.session_state:
        st.session_state[k] = v

D = st.session_state.dark

# ══════════════════════════════════════════════════════════════
# PALETTES — reposantes pour l'œil
# ══════════════════════════════════════════════════════════════
if D:
    # Sombre doux : bleu nuit profond, pas de noir pur
    BG, BG2   = "#0F1117", "#141921"
    CARD, CD2 = "#1A2030", "#202840"
    BRD, BR2  = "#26354F", "#30426A"
    TX,  TX2  = "#D8E4F8", "#7B94BF"
    TX3, GRD  = "#3D5070", "#26354F"
else:
    # Clair doux : blanc cassé, pas de blanc pur — repose les yeux
    BG, BG2   = "#F6F8FD", "#EDF1FA"
    CARD, CD2 = "#FFFFFF", "#F0F4FC"
    BRD, BR2  = "#CDD8EE", "#B8C8E4"
    TX,  TX2  = "#111827", "#3B506E"
    TX3, GRD  = "#7A94BA", "#CDD8EE"

# Couleurs d'accent — saturées modérément, reposantes
A1 = "#5B91E5"   # bleu principal
A2 = "#3DB89A"   # vert menthe
A3 = "#E8973A"   # ambre chaud
A4 = "#7E6ED8"   # violet doux
A5 = "#E05F6F"   # rose-rouge
A6 = "#3BA3CC"   # bleu cyan
CB = {"A": A3, "B": A2, "C": A1}
P6 = [A1, A2, A3, A4, A5, A6]


def ra(h: str, a: float) -> str:
    r, g, b = int(h[1:3], 16), int(h[3:5], 16), int(h[5:7], 16)
    return f"rgba({r},{g},{b},{a})"

# ══════════════════════════════════════════════════════════════
# MINI SPARKLINE SVG
# ══════════════════════════════════════════════════════════════
def spark(values, color, w=90, h=28):
    v = list(values)
    if len(v) < 2:
        return ""
    mn, mx = min(v), max(v)
    rng = (mx - mn) or 1
    pad = 2
    pts = [f"{pad+int(i/(len(v)-1)*(w-2*pad))},{pad+int((1-(x-mn)/rng)*(h-2*pad))}"
           for i, x in enumerate(v)]
    fill = f"M {pad},{h} L {' L '.join(pts)} L {w-pad},{h} Z"
    line = "M " + " L ".join(pts)
    r2, g2, b2 = int(color[1:3],16), int(color[3:5],16), int(color[5:7],16)
    lx, ly = pts[-1].split(",")
    uid = f"sg{r2}{g2}{b2}"
    return (
        f'<svg width="{w}" height="{h}" viewBox="0 0 {w} {h}" style="display:block;">'
        f'<defs><linearGradient id="{uid}" x1="0" y1="0" x2="0" y2="1">'
        f'<stop offset="0%" stop-color="rgba({r2},{g2},{b2},0.30)"/>'
        f'<stop offset="100%" stop-color="rgba({r2},{g2},{b2},0)"/>'
        f'</linearGradient></defs>'
        f'<path d="{fill}" fill="url(#{uid})"/>'
        f'<path d="{line}" fill="none" stroke="{color}" stroke-width="1.8" '
        f'stroke-linecap="round" stroke-linejoin="round"/>'
        f'<circle cx="{lx}" cy="{ly}" r="2.8" fill="{color}" stroke="{BG}" stroke-width="1.5"/>'
        f'</svg>'
    )

# ══════════════════════════════════════════════════════════════
# CSS GLOBAL
# ══════════════════════════════════════════════════════════════
st.markdown(f"""
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&family=JetBrains+Mono:wght@400;500&display=swap');

html,body,[class*="css"]{{
    font-family:'Inter',sans-serif!important;
    background:{BG}!important; color:{TX}!important;
}}
.stApp{{background:{BG}!important;}}
#MainMenu,footer,header,.stDeployButton,
[data-testid="stToolbar"],[data-testid="stDecoration"]{{display:none!important;}}

/* ── Filtres select ── */
[data-baseweb="select"]>div{{
    background:{CARD}!important;border:1px solid {BRD}!important;
    border-radius:6px!important;color:{TX}!important;
    min-height:36px!important;font-size:13px!important;
}}
[data-baseweb="select"] svg{{fill:{TX3}!important;}}
[data-baseweb="popover"],[data-baseweb="menu"]{{
    background:{CARD}!important;border-color:{BRD}!important;
}}
[data-baseweb="option"]{{background:{CARD}!important;color:{TX}!important;}}
[data-baseweb="option"]:hover{{background:{CD2}!important;}}
[data-testid="stDateInputField"],[data-baseweb="base-input"]{{
    background:{CARD}!important;border-color:{BRD}!important;
    color:{TX}!important;border-radius:6px!important;
}}

/* ── Boutons ── */
.stButton>button{{
    background:transparent!important;
    border:1px solid {BR2}!important;border-radius:6px!important;
    color:{TX2}!important;font-family:'Inter',sans-serif!important;
    font-size:11px!important;font-weight:600!important;
    transition:all 0.15s!important;
}}
.stButton>button:hover{{
    border-color:{A1}!important;color:{A1}!important;
    background:{ra(A1,0.07)}!important;
}}

/* ── Onglets ── */
.stTabs [data-baseweb="tab-list"]{{
    background:{CD2}!important;border:1px solid {BRD}!important;
    border-radius:8px!important;padding:4px!important;gap:3px!important;
}}
.stTabs [data-baseweb="tab"]{{
    background:transparent!important;border:none!important;
    border-radius:6px!important;color:{TX3}!important;
    font-size:10.5px!important;font-weight:700!important;
    letter-spacing:0.8px!important;text-transform:uppercase!important;
    padding:8px 18px!important;transition:all 0.15s!important;
}}
.stTabs [aria-selected="true"]{{background:{A1}!important;color:#fff!important;}}
.stTabs [data-baseweb="tab-panel"]{{padding-top:20px!important;}}

/* ── DataFrames ── */
.stDataFrame{{border:1px solid {BRD}!important;border-radius:6px!important;}}
[data-testid="stDataFrame"] th{{
    background:{CD2}!important;color:{TX3}!important;
    font-size:10px!important;text-transform:uppercase!important;
    letter-spacing:1px!important;font-family:'JetBrains Mono',monospace!important;
}}
[data-testid="stDataFrame"] td{{color:{TX2}!important;font-size:12px!important;}}

/* ── Inputs ── */
.stTextInput input{{
    background:{CARD}!important;border-color:{BRD}!important;
    color:{TX}!important;border-radius:6px!important;font-size:13px!important;
}}
.stTextInput input:focus{{
    border-color:{A1}!important;
    box-shadow:0 0 0 2px {ra(A1,0.18)}!important;
}}
label{{color:{TX2}!important;font-size:12px!important;}}
.stDownloadButton>button{{
    background:transparent!important;border:1px solid {BRD}!important;
    color:{TX3}!important;border-radius:6px!important;font-size:11px!important;
}}
.stDownloadButton>button:hover{{border-color:{A1}!important;color:{A1}!important;}}
hr{{border-color:{BRD}!important;opacity:1!important;}}

/* ── Animations KPI ── */
@keyframes pulse-ring{{
    0%{{box-shadow:0 0 0 0 {ra(A1,0.5)};}}
    70%{{box-shadow:0 0 0 7px {ra(A1,0)};}}
    100%{{box-shadow:0 0 0 0 {ra(A1,0)};}}
}}
@keyframes glow-border{{
    0%,100%{{opacity:1;}} 50%{{opacity:0.6;}}
}}
.kpi-lift{{transition:transform 0.18s ease,box-shadow 0.18s ease!important;}}
.kpi-lift:hover{{transform:translateY(-3px)!important;box-shadow:0 10px 28px rgba(0,0,0,0.22)!important;}}
.pulse-active{{animation:pulse-ring 2s ease-in-out infinite!important;}}
.glow-active{{animation:glow-border 2.5s ease-in-out infinite!important;}}

/* ── Tooltip CSS ── */
.tip-wrap{{position:relative;}}
.tip-wrap .tip{{
    display:none;position:absolute;bottom:calc(100% + 8px);left:50%;
    transform:translateX(-50%);background:{CD2};border:1px solid {BR2};
    border-radius:6px;padding:7px 12px;font-size:11px;color:{TX2};
    white-space:nowrap;z-index:9999;font-family:'JetBrains Mono',monospace;
    pointer-events:none;box-shadow:0 4px 18px rgba(0,0,0,0.28);
}}
.tip-wrap .tip::after{{
    content:'';position:absolute;top:100%;left:50%;transform:translateX(-50%);
    border:5px solid transparent;border-top-color:{BR2};
}}
.tip-wrap:hover .tip{{display:block;}}

/* ── Barre KPI ── */
.kbar{{height:3px;border-radius:2px;background:{BRD};margin-top:8px;overflow:hidden;}}
.kbar-fill{{height:100%;border-radius:2px;transition:width 0.7s ease;}}

/* ── Description visuelle ── */
.viz-desc{{
    background:{ra(A1,0.05) if D else ra(A1,0.04)};
    border-left:3px solid {A1};border-radius:0 5px 5px 0;
    padding:8px 12px;margin-bottom:12px;
    font-size:11.5px;color:{TX2};line-height:1.6;
    font-style:italic;
}}

/* ── Tendance delta ── */
.up{{color:{A2};}} .dn{{color:{A5};}}
</style>
""", unsafe_allow_html=True)

# ══════════════════════════════════════════════════════════════
# HELPERS
# ══════════════════════════════════════════════════════════════
def sec(t: str):
    st.markdown(
        f'<div style="font-size:9px;font-weight:700;letter-spacing:3px;'
        f'text-transform:uppercase;color:{TX3};padding-bottom:9px;'
        f'border-bottom:1px solid {BRD};margin-bottom:13px;'
        f'font-family:JetBrains Mono,monospace;">{t}</div>',
        unsafe_allow_html=True)

def desc(txt: str):
    st.markdown(f'<div class="viz-desc">{txt}</div>', unsafe_allow_html=True)

def insight(txt: str):
    st.markdown(
        f'<div style="background:{ra(A2,0.07)};border:1px solid {ra(A2,0.2)};'
        f'border-left:3px solid {A2};border-radius:5px;'
        f'padding:11px 15px;font-size:12px;line-height:1.7;color:{TX2};margin:12px 0 4px;">'
        f'{txt}</div>', unsafe_allow_html=True)

def lp(fig, h=310, legend=False, hover="closest"):
    fig.update_layout(
        paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)",
        font=dict(family="Inter", color=TX2, size=11),
        margin=dict(l=8,r=8,t=8,b=8), height=h,
        showlegend=legend,
        legend=dict(bgcolor="rgba(0,0,0,0)", font=dict(size=10,color=TX2), borderwidth=0),
        xaxis=dict(gridcolor=GRD, linecolor=BRD, tickfont=dict(size=10), zeroline=False),
        yaxis=dict(gridcolor=GRD, linecolor=BRD, tickfont=dict(size=10), zeroline=False),
        hovermode=hover)
    return fig

def fmt(v: float) -> str:
    if v >= 1e6: return f"${v/1e6:.2f}M"
    if v >= 1e3: return f"${v/1e3:.1f}K"
    return f"${v:.0f}"

# ══════════════════════════════════════════════════════════════
# KPI CARD INTERACTIF + SPARKLINE + TOOLTIP
# ══════════════════════════════════════════════════════════════
def kpi_card(col, key, label, value, sub, dval, dpos,
             color, cf=None, cv=None, sparkv=None, pbar=None, tip=None):
    active = (st.session_state.kpi_field == cf and
              st.session_state.kpi_val   == cv  and cf)
    bg    = ra(color, 0.13) if active else CARD
    brd_c = color if active else BRD
    glow  = f"box-shadow:0 0 0 2px {ra(color,0.45)},0 6px 22px {ra(color,0.13)};" if active else ""
    acls  = "glow-active" if active else ""
    dot   = (f'<span class="pulse-active" style="position:absolute;top:11px;right:12px;'
             f'width:7px;height:7px;border-radius:50%;background:{color};'
             f'display:inline-block;"></span>') if active else (
             f'<span style="position:absolute;top:12px;right:13px;'
             f'width:5px;height:5px;border-radius:50%;background:{ra(color,0.35)};'
             f'display:inline-block;"></span>')
    dcol  = A2 if dpos else A5
    darr  = "▲" if dpos else "▼"
    dhtml = (f'<div style="font-size:9.5px;color:{dcol};margin-top:4px;'
             f'font-family:JetBrains Mono,monospace;">{darr} {dval}</div>')

    spk = ""
    if sparkv is not None and len(sparkv) >= 2:
        spk = (f'<div style="position:absolute;bottom:7px;right:7px;'
               f'opacity:0.7;pointer-events:none;">{spark(sparkv, color)}</div>')

    bar = ""
    if pbar is not None:
        w = max(0, min(100, pbar))
        bar = (f'<div class="kbar">'
               f'<div class="kbar-fill" style="width:{w:.1f}%;'
               f'background:linear-gradient(90deg,{ra(color,0.5)},{color});"></div></div>')

    tip_html = f'<div class="tip">{tip}</div>' if tip else ""
    cursor   = "cursor:pointer;" if cf else "cursor:default;"

    with col:
        st.markdown(
            f'<div class="tip-wrap">{tip_html}'
            f'<div class="kpi-lift {acls}" '
            f'style="background:{bg};border:1px solid {brd_c};'
            f'border-top:3px solid {color};border-radius:8px;'
            f'padding:15px 15px 10px;min-height:112px;position:relative;{glow}{cursor}">'
            f'{dot}{spk}'
            f'<div style="font-size:8.5px;letter-spacing:2.2px;text-transform:uppercase;'
            f'color:{TX3};margin-bottom:6px;font-family:JetBrains Mono,monospace;">{label}</div>'
            f'<div style="font-size:23px;font-weight:700;color:{color};line-height:1;">{value}</div>'
            f'<div style="font-size:10px;color:{TX3};margin-top:4px;">{sub}</div>'
            f'{dhtml}{bar}'
            f'</div></div>', unsafe_allow_html=True)
        if cf:
            lbl = "✕  Effacer" if active else "  Filtrer  "
            if st.button(lbl, key=f"kbtn_{key}", use_container_width=True):
                if active: st.session_state.kpi_field=None; st.session_state.kpi_val=None
                else: st.session_state.kpi_field=cf; st.session_state.kpi_val=cv
                st.rerun()

# ══════════════════════════════════════════════════════════════
# CHARGEMENT — OPTIMISÉ (tout calculé une fois)
# ══════════════════════════════════════════════════════════════
@st.cache_data(show_spinner="Chargement des données…")
def load(path=None, up=None):
    df = pd.read_csv(up if up else path)
    df.columns = df.columns.str.strip()
    df["Date"]   = pd.to_datetime(df["Date"], format="%m/%d/%Y")
    df["Heure"]  = pd.to_datetime(df["Time"], format="%H:%M").dt.hour
    df["JourFR"] = df["Date"].dt.day_name().map({
        "Monday":"Lundi","Tuesday":"Mardi","Wednesday":"Mercredi",
        "Thursday":"Jeudi","Friday":"Vendredi","Saturday":"Samedi","Sunday":"Dimanche"})
    df["JourN"]  = df["Date"].dt.weekday
    df["Mois"]   = df["Date"].dt.month
    df["NomM"]   = df["Date"].dt.strftime("%b")
    df["Sem"]    = df["Date"].dt.isocalendar().week.astype(int)
    df["Prd"]    = df["Date"].dt.to_period("M").astype(str)
    df.rename(columns={
        "Invoice ID":"ID","Branch":"Branche","City":"Ville",
        "Customer type":"TypeCl","Product line":"Produit",
        "Unit price":"PrixU","Quantity":"Qte","Tax 5%":"Taxe",
        "Payment":"Paiement","gross income":"RevBrut",
        "gross margin percentage":"PctM","Rating":"Note",
        "cogs":"COGS","Gender":"Sexe"}, inplace=True)
    df["TypeCl"] = df["TypeCl"].map({"Member":"Membre","Normal":"Standard"})
    df["Genre"]  = df["Sexe"].map({"Female":"Femme","Male":"Homme"})
    df["Periode"]= df["Heure"].apply(
        lambda h:"Matin" if h<13 else("Après-midi" if h<17 else "Soir"))
    return df

RAW = None
for p in ["supermarket_sales.csv","data/supermarket_sales.csv","../supermarket_sales.csv"]:
    if os.path.exists(p): RAW=load(path=p); break

if RAW is None:
    st.markdown(f'<div style="text-align:center;padding:100px;">'
        f'<div style="font-size:20px;font-weight:700;color:{TX};">Tableau de Bord Commercial</div>'
        f'<div style="font-size:13px;color:{TX3};margin-top:8px;">Importez supermarket_sales.csv</div>'
        f'</div>', unsafe_allow_html=True)
    f = st.file_uploader("Charger supermarket_sales.csv", type=["csv"])
    if f: RAW=load(up=f)
    if RAW is None: st.stop()

# ══════════════════════════════════════════════════════════════
# EN-TÊTE — TITRE 
# ══════════════════════════════════════════════════════════════
st.markdown(
    f'<div style="background:linear-gradient(135deg,{ra(A1,0.10)} 0%,{ra(A2,0.07)} 100%);'
    f'border:1px solid {BRD};border-radius:10px;'
    f'padding:20px 28px;margin-bottom:16px;">'
    f'<div style="display:flex;justify-content:space-between;align-items:flex-start;">'
    f'<div>'
    f'<div style="font-size:19px;font-weight:700;color:{TX};letter-spacing:-0.2px;">'
    f'Analyse des Performances Commerciales</div>'
    f'<div style="font-size:12px;font-weight:500;color:{TX2};margin-top:3px;">'
    f'Supermarché Myanmar — Rapport Analytique Descriptif · Trimestre 1, 2019</div>'
    f'<div style="font-size:9.5px;letter-spacing:2px;text-transform:uppercase;'
    f'color:{TX3};margin-top:6px;font-family:JetBrains Mono,monospace;">'
    f'3 Branches (Yangon · Mandalay · Naypyitaw) &nbsp;·&nbsp; '
    f'6 Lignes de Produits &nbsp;·&nbsp; Jan–Mar 2019</div>'
    f'</div>'
    f'<div style="text-align:right;padding-top:2px;">'
    f'<div style="font-size:9px;letter-spacing:2px;text-transform:uppercase;'
    f'color:{TX3};font-family:JetBrains Mono,monospace;">'
    f'Jeu de données<br>1 000 transactions · 17 variables</div>'
    f'</div></div>'
    f'</div>', unsafe_allow_html=True)

# ══════════════════════════════════════════════════════════════
# BARRE DE FILTRES
# ══════════════════════════════════════════════════════════════
st.markdown(
    f'<div style="background:{CARD};border:1px solid {BRD};border-radius:8px;'
    f'padding:10px 16px 6px;margin-bottom:14px;">'
    f'<div style="font-size:9px;letter-spacing:2px;text-transform:uppercase;'
    f'color:{TX3};font-weight:700;margin-bottom:8px;font-family:JetBrains Mono,monospace;">'
    f'Paramètres de Filtrage — Affinez la sélection des données</div>'
    f'</div>', unsafe_allow_html=True)

LS = (f'<div style="font-size:9px;letter-spacing:1.5px;text-transform:uppercase;'
      f'color:{TX3};font-weight:700;margin-bottom:4px;'
      f'font-family:JetBrains Mono,monospace;">')

fc = st.columns([1.5,1.5,1,1,1,1,1.2,0.6])
with fc[0]:
    st.markdown(LS+"Période</div>", unsafe_allow_html=True)
    mn, mx = RAW["Date"].min().date(), RAW["Date"].max().date()
    plage = st.date_input("", (mn, mx), min_value=mn, max_value=mx,
                          key="fdt", label_visibility="collapsed")
with fc[1]:
    st.markdown(LS+"Ligne de Produit</div>", unsafe_allow_html=True)
    sel_p = st.selectbox("", ["Tous"]+sorted(RAW["Produit"].unique()),
                         key="fp", label_visibility="collapsed")
with fc[2]:
    st.markdown(LS+"Branche</div>", unsafe_allow_html=True)
    sel_b = st.selectbox("", ["Toutes"]+sorted(RAW["Branche"].unique()),
                         key="fb", label_visibility="collapsed")
with fc[3]:
    st.markdown(LS+"Ville</div>", unsafe_allow_html=True)
    sel_v = st.selectbox("", ["Toutes"]+sorted(RAW["Ville"].unique()),
                         key="fv", label_visibility="collapsed")
with fc[4]:
    st.markdown(LS+"Paiement</div>", unsafe_allow_html=True)
    sel_pay = st.selectbox("", ["Tous"]+sorted(RAW["Paiement"].unique()),
                           key="fy", label_visibility="collapsed")
with fc[5]:
    st.markdown(LS+"Type Client</div>", unsafe_allow_html=True)
    sel_ct = st.selectbox("", ["Tous"]+sorted(RAW["TypeCl"].unique()),
                          key="fct", label_visibility="collapsed")
with fc[6]:
    st.markdown(LS+"Genre</div>", unsafe_allow_html=True)
    sel_gn = st.selectbox("", ["Tous"]+sorted(RAW["Genre"].unique()),
                          key="fgn", label_visibility="collapsed")
with fc[7]:
    st.markdown(f'<div style="font-size:1px;color:transparent;margin-bottom:4px;">.</div>',
                unsafe_allow_html=True)
    ca7, cb7 = st.columns(2)
    with ca7:
        if st.button("☀" if D else "☾", key="th", use_container_width=True,
                     help="Basculer le thème"):
            st.session_state.dark=not D; st.rerun()
    with cb7:
        if st.button("✕", key="clr", use_container_width=True,
                     help="Effacer filtre KPI"):
            st.session_state.kpi_field=None; st.session_state.kpi_val=None; st.rerun()

if st.session_state.kpi_field:
    st.markdown(
        f'<div style="display:inline-flex;align-items:center;gap:8px;'
        f'padding:4px 14px;background:{ra(A1,0.1)};border:1px solid {ra(A1,0.3)};'
        f'border-radius:20px;font-size:11px;color:{A1};margin-bottom:10px;'
        f'font-family:JetBrains Mono,monospace;">'
        f'● Filtre KPI actif : {st.session_state.kpi_field} = {st.session_state.kpi_val}'
        f'</div>', unsafe_allow_html=True)

# ══════════════════════════════════════════════════════════════
# FILTRAGE — OPTIMISÉ
# ══════════════════════════════════════════════════════════════
@st.cache_data
def compute_filtered(_raw, kf, kv, p0, p1, sp, sb, sv, spay, sct, sgn):
    df = _raw.copy()
    if kf and kv:
        return df[df[kf] == kv]
    df = df[(df["Date"].dt.date >= p0) & (df["Date"].dt.date <= p1)]
    if sp   != "Tous":   df = df[df["Produit"]  == sp]
    if sb   != "Toutes": df = df[df["Branche"]  == sb]
    if sv   != "Toutes": df = df[df["Ville"]    == sv]
    if spay != "Tous":   df = df[df["Paiement"] == spay]
    if sct  != "Tous":   df = df[df["TypeCl"]   == sct]
    if sgn  != "Tous":   df = df[df["Genre"]    == sgn]
    return df

p0 = plage[0] if len(plage)==2 else mn
p1 = plage[1] if len(plage)==2 else mx
DF = compute_filtered(RAW, st.session_state.kpi_field, st.session_state.kpi_val,
                      p0, p1, sel_p, sel_b, sel_v, sel_pay, sel_ct, sel_gn)
if DF.empty: st.warning("Aucune donnée ne correspond aux filtres."); st.stop()

# ══════════════════════════════════════════════════════════════
# MÉTRIQUES PRÉ-CALCULÉES
# ══════════════════════════════════════════════════════════════
@st.cache_data
def calc_metrics(_df, _raw):
    rev=_df["Total"].sum(); brut=_df["RevBrut"].sum()
    cost=_df["COGS"].sum(); tax=_df["Taxe"].sum()
    moy=_df["Total"].mean(); note=_df["Note"].mean(); N=len(_df)
    top_b=_df.groupby("Branche")["Total"].sum().idxmax()
    top_p=_df.groupby("Produit")["Total"].sum().idxmax()
    top_py=_df.groupby("Paiement")["Total"].sum().idxmax()
    n_j=max((_df["Date"].max()-_df["Date"].min()).days,1)
    prev=_raw[(_raw["Date"]>=_df["Date"].min()-timedelta(n_j))&
              (_raw["Date"]<_df["Date"].min())]
    def dp(a,b): return ((a-b)/max(b,1))*100
    d_rev=dp(rev,prev["Total"].sum())
    d_brut=dp(brut,prev["RevBrut"].sum())
    d_cost=dp(cost,prev["COGS"].sum())
    d_tax=dp(tax,prev["Taxe"].sum())
    # Totaux dataset complet pour les %
    rv_all=_raw["Total"].sum(); bt_all=_raw["RevBrut"].sum()
    co_all=_raw["COGS"].sum(); tx_all=_raw["Taxe"].sum()
    br_mx=_raw.groupby("Branche")["Total"].sum().max()
    top_b_ca=_df.groupby("Branche")["Total"].sum().get(top_b,0)
    pct_br=top_b_ca/br_mx*100
    return dict(rev=rev,brut=brut,cost=cost,tax=tax,moy=moy,note=note,N=N,
                top_b=top_b,top_p=top_p,top_py=top_py,n_j=n_j,
                d_rev=d_rev,d_brut=d_brut,d_cost=d_cost,d_tax=d_tax,
                rv_all=rv_all,bt_all=bt_all,co_all=co_all,tx_all=tx_all,pct_br=pct_br,
                top_b_ca=top_b_ca)

M = calc_metrics(DF, RAW)
rev=M["rev"]; brut=M["brut"]; cost=M["cost"]; tax=M["tax"]
moy=M["moy"]; note=M["note"]; N=M["N"]; n_j=M["n_j"]
top_b=M["top_b"]; top_p=M["top_p"]; top_py=M["top_py"]

# Sparklines quotidiens
dca  = DF.groupby("Date")["Total"].sum().values
dbrut= DF.groupby("Date")["RevBrut"].sum().values
dcost= DF.groupby("Date")["COGS"].sum().values
dtax = DF.groupby("Date")["Taxe"].sum().values

pct_sel = N/len(RAW)*100
st.markdown(
    f'<div style="display:flex;justify-content:flex-end;align-items:center;'
    f'gap:8px;margin-bottom:6px;">'
    f'<span style="font-size:22px;font-weight:700;color:{A1};">{N:,}</span>'
    f'<span style="font-size:10px;color:{TX3};font-family:JetBrains Mono,monospace;">'
    f'/ 1 000 transactions · {pct_sel:.1f}% de la base</span>'
    f'</div>', unsafe_allow_html=True)

# ══════════════════════════════════════════════════════════════
# KPI PRINCIPAUX
# ══════════════════════════════════════════════════════════════
sec("INDICATEURS CLÉS DE PERFORMANCE — Survolez pour les détails · Cliquez « Filtrer » pour isoler")
k = st.columns(5)
kpi_card(k[0],"rev","Chiffre d'Affaires",fmt(rev),f"{N:,} transactions",
         f"{'+'if M['d_rev']>=0 else ''}{M['d_rev']:.1f}% vs période préc.",M["d_rev"]>=0,
         A1,sparkv=dca,pbar=rev/M["rv_all"]*100,
         tip=f"Moy. / jour : {fmt(rev/max(n_j,1))} | Moy. / txn : {fmt(moy)}")
kpi_card(k[1],"brut","Revenu Brut",fmt(brut),"Marge 4,76% (fixe)",
         f"{'+'if M['d_brut']>=0 else ''}{M['d_brut']:.1f}% vs période préc.",M["d_brut"]>=0,
         A2,sparkv=dbrut,pbar=brut/M["bt_all"]*100,
         tip=f"Ratio COGS/CA : {cost/max(rev,1)*100:.1f}% | Brut / txn : {fmt(brut/max(N,1))}")
kpi_card(k[2],"cost","Coût Marchandises",fmt(cost),"COGS total",
         f"{'+'if M['d_cost']>=0 else ''}{M['d_cost']:.1f}% vs période préc.",M["d_cost"]>=0,
         A3,sparkv=dcost,pbar=cost/M["co_all"]*100,
         tip=f"COGS : {cost/max(rev,1)*100:.1f}% du CA | Moy. / txn : {fmt(cost/max(N,1))}")
kpi_card(k[3],"tax","Taxes Collectées",fmt(tax),"5% uniforme",
         f"{'+'if M['d_tax']>=0 else ''}{M['d_tax']:.1f}% vs période préc.",M["d_tax"]>=0,
         A4,sparkv=dtax,pbar=tax/M["tx_all"]*100,
         tip=f"Taxe moy. / txn : {fmt(tax/max(N,1))} | Taux fixe : 5%")
kpi_card(k[4],"topb","Branche Leader",top_b,
         f"{fmt(M['top_b_ca'])} — {RAW[RAW['Branche']==top_b]['Ville'].iloc[0]}",
         "Cliquer pour isoler",True,A5,
         cf="Branche",cv=top_b,
         sparkv=DF[DF["Branche"]==top_b].groupby("Date")["Total"].sum().values,
         pbar=M["pct_br"],
         tip=f"Ville : {RAW[RAW['Branche']==top_b]['Ville'].iloc[0]}")

st.markdown("<br>", unsafe_allow_html=True)

# Métriques secondaires
sm = st.columns(4)
sm_data = [
    ("Panier Moyen",   fmt(moy),          A1, None,      None,
     f"Min {fmt(DF['Total'].min())} · Max {fmt(DF['Total'].max())}"),
    ("Note Moyenne",   f"{note:.2f} / 10", A2, None,      None,
     f"Médiane {DF['Note'].median():.2f} · Std {DF['Note'].std():.2f}"),
    ("Produit Leader", top_p.replace(" and "," & ")[:17], A3,"Produit", top_p,
     f"CA : {fmt(DF.groupby('Produit')['Total'].sum()[top_p])}"),
    ("Paiement Leader",top_py,            A4, "Paiement",top_py,
     f"Transactions : {int((DF['Paiement']==top_py).sum())}"),
]
for i,(cs,(lb,vl,c,cf2,cv2,tip)) in enumerate(zip(sm,sm_data)):
    act=(st.session_state.kpi_field==cf2 and st.session_state.kpi_val==cv2 and cf2)
    bg2=ra(c,0.12) if act else CARD; brd2=c if act else BRD
    ring=f"box-shadow:0 0 0 2px {ra(c,0.4)};" if act else ""
    dot2=(f'<span style="width:5px;height:5px;border-radius:50%;background:{c};'
          f'display:inline-block;margin-left:6px;box-shadow:0 0 5px {ra(c,0.8)};"></span>') if act else ""
    cs.markdown(
        f'<div class="tip-wrap"><div class="tip">{tip}</div>'
        f'<div class="kpi-lift" style="background:{bg2};border:1px solid {brd2};'
        f'border-radius:8px;padding:12px 14px;{ring}">'
        f'<div style="display:flex;align-items:center;gap:11px;">'
        f'<div style="width:4px;height:34px;background:{c};border-radius:2px;flex-shrink:0;"></div>'
        f'<div style="flex:1;">'
        f'<div style="font-size:8px;letter-spacing:2px;text-transform:uppercase;'
        f'color:{TX3};font-family:JetBrains Mono,monospace;display:flex;align-items:center;">'
        f'{lb}{dot2}</div>'
        f'<div style="font-size:15px;font-weight:700;color:{c};margin-top:2px;">{vl}</div>'
        f'</div></div></div></div>', unsafe_allow_html=True)
    if cf2:
        lbl_s="✕ Effacer" if act else "Filtrer ▸"
        if cs.button(lbl_s,key=f"sm_{i}",use_container_width=True):
            if act: st.session_state.kpi_field=None; st.session_state.kpi_val=None
            else: st.session_state.kpi_field=cf2; st.session_state.kpi_val=cv2
            st.rerun()

st.markdown("<br>", unsafe_allow_html=True)

# ══════════════════════════════════════════════════════════════
# ONGLETS
# ══════════════════════════════════════════════════════════════
T1,T2,T3,T4,T5 = st.tabs([
    "VUE D'ENSEMBLE","PRODUITS & VENTES","CLIENTS & SEGMENTS","TEMPOREL","DONNÉES"
])

# ─── TAB 1 ────────────────────────────────────────────────────
with T1:
    cL,cR = st.columns([5,3])
    with cL:
        sec("ÉVOLUTION MENSUELLE DES VENTES")
        desc("Ce graphique combiné présente le chiffre d'affaires mensuel sous forme de barres "
             "et la tendance lissée en courbe. L'axe secondaire suit le volume de transactions, "
             "permettant d'identifier les corrélations entre fréquentation et revenus.")
        mo = DF.groupby("Prd").agg(CA=("Total","sum"),Txn=("ID","count")).reset_index()
        mo["MA"] = mo["CA"].rolling(2,min_periods=1).mean()
        fig = make_subplots(specs=[[{"secondary_y":True}]])
        fig.add_trace(go.Bar(x=mo["Prd"],y=mo["CA"],name="CA Mensuel",
            marker_color=ra(A1,0.55),marker_line_width=0),secondary_y=False)
        fig.add_trace(go.Scatter(x=mo["Prd"],y=mo["MA"],name="Tendance",
            line=dict(color=A3,width=2.8)),secondary_y=False)
        fig.add_trace(go.Scatter(x=mo["Prd"],y=mo["Txn"],name="Transactions",
            line=dict(color=A4,width=2,dash="dot")),secondary_y=True)
        lp(fig,h=280,legend=True,hover="x unified")
        fig.update_layout(legend=dict(orientation="h",y=1.05,x=0,font=dict(size=10)))
        fig.update_yaxes(secondary_y=True,gridcolor="rgba(0,0,0,0)",
                         tickfont=dict(color=A4,size=9))
        st.plotly_chart(fig,use_container_width=True)

    with cR:
        sec("RÉPARTITION DU CA PAR BRANCHE")
        desc("Ce graphique en anneau visualise la contribution relative de chaque branche "
             "au chiffre d'affaires total. Survolez un segment pour le détail.")
        brs = DF.groupby("Branche")["Total"].sum().reset_index()
        brs["L"] = brs["Branche"].apply(
            lambda b: f"Branche {b} — {RAW[RAW['Branche']==b]['Ville'].iloc[0]}")
        fig = go.Figure(go.Pie(
            labels=brs["L"],values=brs["Total"],hole=0.65,
            marker_colors=[CB.get(b,A2) for b in brs["Branche"]],
            textinfo="percent",textfont_size=11,
            hovertemplate="<b>%{label}</b><br>%{value:,.0f} $<extra></extra>"))
        fig.add_annotation(text=fmt(rev),x=0.5,y=0.55,
            font=dict(size=17,color=A1,family="Inter",weight=700),showarrow=False)
        fig.add_annotation(text="TOTAL CA",x=0.5,y=0.42,
            font=dict(size=8.5,color=TX3,family="JetBrains Mono"),showarrow=False)
        lp(fig,h=280)
        st.plotly_chart(fig,use_container_width=True)

    # Cartes branches
    sec("BRANCHES — Cliquez sur une carte pour filtrer l'ensemble du tableau de bord")
    desc("Chaque carte résume les performances d'une branche : chiffre d'affaires, "
         "nombre de transactions, note de satisfaction et part relative du total.")
    br_agg = RAW.groupby("Branche").agg(
        CA=("Total","sum"),Ville=("Ville","first"),
        Txn=("ID","count"),Note=("Note","mean")).reset_index()
    bc = st.columns(3)
    for i,(_,r) in enumerate(br_agg.iterrows()):
        c = CB.get(r["Branche"],A2)
        act = (st.session_state.kpi_field=="Branche" and st.session_state.kpi_val==r["Branche"])
        fill=r["CA"]/br_agg["CA"].max()*100; pct2=r["CA"]/br_agg["CA"].sum()*100
        bg_b=ra(c,0.11) if act else CARD; brd_b=c if act else BRD
        with bc[i]:
            st.markdown(
                f'<div class="kpi-lift" style="background:{bg_b};border:1px solid {brd_b};'
                f'border-radius:8px;padding:14px 16px;'
                f'{"box-shadow:0 0 0 2px "+ra(c,0.4)+";" if act else ""}">'
                f'<div style="display:flex;justify-content:space-between;margin-bottom:5px;">'
                f'<div><div style="font-size:15px;font-weight:700;color:{c};">'
                f'Branche {r["Branche"]}</div>'
                f'<div style="font-size:9px;letter-spacing:2px;text-transform:uppercase;'
                f'color:{TX3};font-family:JetBrains Mono,monospace;">{r["Ville"]}</div></div>'
                f'<div style="text-align:right;">'
                f'<div style="font-size:11px;color:{c};font-family:JetBrains Mono,monospace;">{pct2:.1f}%</div>'
                f'<div style="font-size:8px;color:{TX3};">du CA total</div></div></div>'
                f'<div style="font-size:18px;font-weight:700;color:{c};">{fmt(r["CA"])}</div>'
                f'<div style="font-size:10px;color:{TX3};margin-top:3px;">'
                f'{r["Txn"]:,} txn · Note {r["Note"]:.2f} / 10</div>'
                f'<div class="kbar"><div class="kbar-fill" '
                f'style="width:{fill:.1f}%;background:linear-gradient(90deg,{ra(c,0.45)},{c});"></div></div>'
                f'</div>', unsafe_allow_html=True)
            lbl_br = "✕ Effacer" if act else f"Isoler Branche {r['Branche']}"
            if st.button(lbl_br,key=f"br_{r['Branche']}",use_container_width=True):
                if act: st.session_state.kpi_field=None; st.session_state.kpi_val=None
                else: st.session_state.kpi_field="Branche"; st.session_state.kpi_val=r["Branche"]
                st.rerun()

    c3,c4 = st.columns(2)
    with c3:
        sec("CA PAR LIGNE DE PRODUIT")
        desc("Ce classement horizontal permet de comparer rapidement le chiffre d'affaires "
             "généré par chaque catégorie. La nuance de couleur renforce la hiérarchie visuelle.")
        pd2=DF.groupby("Produit")["Total"].sum().sort_values().reset_index()
        pd2["c"]=pd2["Produit"].str.replace(" and "," & ")
        fig=go.Figure(go.Bar(x=pd2["Total"],y=pd2["c"],orientation="h",
            marker=dict(color=pd2["Total"],
                colorscale=[[0,ra(A6,0.55)],[1,A1]],showscale=False),
            text=pd2["Total"].apply(fmt),textposition="outside",
            textfont=dict(size=10,color=TX3)))
        lp(fig,h=280); fig.update_layout(yaxis=dict(tickfont=dict(size=10)))
        st.plotly_chart(fig,use_container_width=True)

    with c4:
        sec("MODES DE PAIEMENT — VOLUME ET FRÉQUENCE")
        desc("La double vue (volume monétaire et nombre de transactions) révèle si certains "
             "modes sont utilisés pour des achats unitaires élevés ou au contraire fréquents "
             "mais de petite valeur.")
        py2=DF.groupby("Paiement").agg(CA=("Total","sum"),Nb=("ID","count")).reset_index()
        c_py={"Cash":A3,"Ewallet":A1,"Credit card":A2}
        fig=make_subplots(rows=1,cols=2,specs=[[{"type":"pie"},{"type":"pie"}]],
            subplot_titles=["Par Volume ($)","Par Nombre de Txn"])
        for vals,ci in [(py2["CA"],1),(py2["Nb"],2)]:
            fig.add_trace(go.Pie(labels=py2["Paiement"],values=vals,hole=0.55,
                marker_colors=[c_py.get(p,A2) for p in py2["Paiement"]],
                textinfo="percent+label",textfont=dict(size=9),showlegend=(ci==1)),1,ci)
        lp(fig,h=280); fig.update_annotations(font=dict(size=10,color=TX2))
        st.plotly_chart(fig,use_container_width=True)

    insight(f"""<strong>Synthèse analytique :</strong>
    La catégorie <strong>{top_p.replace(' and ',' & ')}</strong> domine le classement des ventes.
    La branche <strong>{top_b} ({RAW[RAW['Branche']==top_b]['Ville'].iloc[0]})</strong>
    affiche la meilleure performance. <strong>{top_py}</strong> est le mode de paiement
    le plus utilisé en volume. La marge brute reste constante à <strong>4,76%</strong>
    — revenu brut total : <strong>{fmt(brut)}</strong>.""")

# ─── TAB 2 ────────────────────────────────────────────────────
with T2:
    sec("LIGNES DE PRODUIT — Cliquez sur une carte pour filtrer le tableau de bord")
    desc("Chaque carte résume les performances d'une ligne de produit. "
         "La note de satisfaction (0–10) figure en complément du chiffre d'affaires.")
    ap=DF.groupby("Produit").agg(CA=("Total","sum"),Txn=("ID","count"),
        Note=("Note","mean"),Qte=("Qte","sum")).reset_index().sort_values("CA",ascending=False)
    ap["Part"]=(ap["CA"]/ap["CA"].sum()*100).round(1)
    ap["c"]=ap["Produit"].str.replace(" and "," & ")
    pc=st.columns(len(ap))
    for i,(_,r) in enumerate(ap.iterrows()):
        c=P6[i%len(P6)]
        act=(st.session_state.kpi_field=="Produit" and st.session_state.kpi_val==r["Produit"])
        with pc[i]:
            st.markdown(
                f'<div class="kpi-lift" style="background:{ra(c,0.11) if act else CARD};'
                f'border:1px solid {c if act else BRD};border-top:3px solid {c};'
                f'border-radius:8px;padding:12px;min-height:88px;'
                f'{"box-shadow:0 0 0 1.5px "+c+";" if act else ""}">'
                f'<div style="font-size:8px;letter-spacing:1.5px;text-transform:uppercase;'
                f'color:{TX3};margin-bottom:5px;font-family:JetBrains Mono,monospace;">'
                f'{r["c"][:14]}</div>'
                f'<div style="font-size:18px;font-weight:700;color:{c};">{fmt(r["CA"])}</div>'
                f'<div style="font-size:9px;color:{TX3};margin-top:4px;">'
                f'{r["Part"]:.1f}% · ★ {r["Note"]:.2f}</div>'
                f'</div>', unsafe_allow_html=True)
            lbl_p="✕" if act else "Filtrer"
            if st.button(lbl_p,key=f"pc_{i}",use_container_width=True):
                if act: st.session_state.kpi_field=None; st.session_state.kpi_val=None
                else: st.session_state.kpi_field="Produit"; st.session_state.kpi_val=r["Produit"]
                st.rerun()

    st.markdown("<br>",unsafe_allow_html=True)
    c2a,c2b=st.columns([3,2])
    with c2a:
        sec("CA ET NOTE MOYENNE PAR PRODUIT")
        desc("Ce graphique combiné superpose le chiffre d'affaires (barres colorées) "
             "et la note de satisfaction moyenne (courbe violette). Un produit performant "
             "devrait présenter à la fois un CA élevé et une bonne notation.")
        fig=make_subplots(specs=[[{"secondary_y":True}]])
        for i,(_,r) in enumerate(ap.iterrows()):
            fig.add_trace(go.Bar(x=[r["c"][:14]],y=[r["CA"]],
                marker_color=P6[i%len(P6)],showlegend=False,
                text=[fmt(r["CA"])],textposition="outside",
                textfont=dict(size=9,color=TX3)),secondary_y=False)
        fig.add_trace(go.Scatter(x=ap["c"].str[:14],y=ap["Note"],name="Note Moy.",
            mode="lines+markers",line=dict(color=A4,width=2.5),
            marker=dict(size=7,color=A4)),secondary_y=True)
        lp(fig,h=300,legend=True)
        fig.update_layout(xaxis_tickangle=-15,xaxis_tickfont=dict(size=9))
        fig.update_yaxes(secondary_y=True,gridcolor="rgba(0,0,0,0)",
                         tickfont=dict(color=A4,size=9))
        st.plotly_chart(fig,use_container_width=True)

    with c2b:
        sec("VOLUME D'UNITÉS vs CHIFFRE D'AFFAIRES")
        desc("Chaque bulle représente une catégorie. Sa taille est proportionnelle "
             "à la note de satisfaction. Ce nuage permet d'identifier les produits "
             "à fort volume mais faible CA (bas de gamme) vs. l'inverse.")
        fig=px.scatter(ap,x="Qte",y="CA",size="Note",color="c",
            color_discrete_sequence=P6,size_max=35,
            hover_data={"Note":":.2f","CA":":,.0f","Qte":True,"Part":":.1f"})
        fig.update_traces(marker=dict(opacity=0.82,line=dict(width=1,color=BG)))
        lp(fig,h=300); fig.update_layout(showlegend=False)
        st.plotly_chart(fig,use_container_width=True)

    c2c,c2d=st.columns(2)
    with c2c:
        sec("REVENUS ET COÛTS PAR CATÉGORIE")
        desc("La comparaison côte à côte des revenus et des coûts (COGS) met en évidence "
             "la marge brute effective de chaque catégorie, malgré un taux global uniforme.")
        fig=go.Figure()
        for m,c_m,lbl in [("Total",ra(A1,0.75),"Revenus"),("COGS",ra(A2,0.75),"Coûts (COGS)")]:
            tmp=DF.groupby("Produit")[m].sum().reset_index()
            tmp["c"]=tmp["Produit"].str.replace(" and "," & ")
            tmp=tmp.sort_values(m)
            fig.add_trace(go.Bar(y=tmp["c"],x=tmp[m],name=lbl,orientation="h",
                marker_color=c_m,text=tmp[m].apply(fmt),
                textposition="outside",textfont=dict(size=9)))
        lp(fig,h=290,legend=True)
        fig.update_layout(barmode="group",yaxis=dict(tickfont=dict(size=9)))
        st.plotly_chart(fig,use_container_width=True)

    with c2d:
        sec("HEATMAP : CATÉGORIE × BRANCHE")
        desc("Cette carte de chaleur croise catégories de produits et branches. "
             "Les teintes intenses signalent les combinaisons les plus performantes "
             "et guident les décisions d'assortiment par localisation.")
        hm=DF.pivot_table(values="Total",index="Produit",columns="Branche",aggfunc="sum").fillna(0)
        hm.index=[i.replace(" and "," & ")[:20] for i in hm.index]
        fig=px.imshow(hm,color_continuous_scale=[[0,BG2],[0.4,ra(A6,0.6)],[1,A1]],
            text_auto=".0f",aspect="auto")
        lp(fig,h=290); fig.update_coloraxes(showscale=False)
        fig.update_traces(textfont_size=10)
        st.plotly_chart(fig,use_container_width=True)

    sec("TABLEAU DE CLASSEMENT DES PRODUITS")
    desc("Synthèse tabulaire des 6 lignes de produits classées par chiffre d'affaires décroissant.")
    rk=ap[["c","CA","Txn","Qte","Note","Part"]].copy()
    rk.insert(0,"#",range(1,len(rk)+1))
    rk.columns=["#","Produit","CA ($)","Transactions","Unités","Note Moy.","Part %"]
    rk["CA ($)"]=rk["CA ($)"].apply(fmt)
    rk["Note Moy."]=rk["Note Moy."].apply(lambda v:f"★ {v:.2f}")
    rk["Part %"]=rk["Part %"].apply(lambda v:f"{v:.1f}%")
    st.dataframe(rk,use_container_width=True,hide_index=True)

# ─── TAB 3 ────────────────────────────────────────────────────
with T3:
    sec("SEGMENTATION CLIENT — Cliquez pour isoler un segment")
    desc("Ces cartes permettent de comparer instantanément la contribution "
         "de chaque segment (Membres vs Standard, Femmes vs Hommes) au CA global. "
         "Cliquez sur un segment pour filtrer l'intégralité du tableau de bord.")
    caM=DF[DF["TypeCl"]=="Membre"]["Total"].sum()
    caS=DF[DF["TypeCl"]=="Standard"]["Total"].sum()
    caF=DF[DF["Genre"]=="Femme"]["Total"].sum()
    caH=DF[DF["Genre"]=="Homme"]["Total"].sum()
    pm=caM/(caM+caS+1e-9)*100; pf=caF/(caF+caH+1e-9)*100

    sc=st.columns(4)
    kpi_card(sc[0],"sM","CA Membres",fmt(caM),f"{pm:.1f}% du CA",
             "Cliquer pour filtrer",True,A1,cf="TypeCl",cv="Membre",
             sparkv=DF[DF["TypeCl"]=="Membre"].groupby("Date")["Total"].sum().values,
             pbar=pm,tip=f"Txn membres : {int((DF['TypeCl']=='Membre').sum())}")
    kpi_card(sc[1],"sS","CA Standard",fmt(caS),f"{100-pm:.1f}% du CA",
             "Cliquer pour filtrer",True,A2,cf="TypeCl",cv="Standard",
             sparkv=DF[DF["TypeCl"]=="Standard"].groupby("Date")["Total"].sum().values,
             pbar=100-pm,tip=f"Txn standard : {int((DF['TypeCl']=='Standard').sum())}")
    kpi_card(sc[2],"sF","CA Femmes",fmt(caF),f"{pf:.1f}% du CA",
             "Cliquer pour filtrer",True,A4,cf="Genre",cv="Femme",
             sparkv=DF[DF["Genre"]=="Femme"].groupby("Date")["Total"].sum().values,
             pbar=pf,tip=f"Txn femmes : {int((DF['Genre']=='Femme').sum())}")
    kpi_card(sc[3],"sH","CA Hommes",fmt(caH),f"{100-pf:.1f}% du CA",
             "Cliquer pour filtrer",True,A3,cf="Genre",cv="Homme",
             sparkv=DF[DF["Genre"]=="Homme"].groupby("Date")["Total"].sum().values,
             pbar=100-pf,tip=f"Txn hommes : {int((DF['Genre']=='Homme').sum())}")

    st.markdown("<br>",unsafe_allow_html=True)
    c3a,c3b=st.columns(2)
    with c3a:
        sec("CA ET VOLUME PAR TYPE CLIENT ET GENRE")
        desc("Ce graphique à barres groupées croise deux dimensions : le type d'abonnement "
             "(Membre / Standard) et le genre. Il révèle les dynamiques d'achat propres "
             "à chaque combinaison de profil client.")
        cg=DF.groupby(["TypeCl","Genre"])["Total"].agg(["sum","count"]).reset_index()
        cg.columns=["TypeCl","Genre","CA","Nb"]
        fig=make_subplots(rows=1,cols=2,specs=[[{"type":"xy"},{"type":"xy"}]],
            subplot_titles=["Chiffre d'Affaires ($)","Nombre de Transactions"])
        for g,c in [("Femme",A4),("Homme",A2)]:
            sub=cg[cg["Genre"]==g]
            fig.add_trace(go.Bar(name=g,x=sub["TypeCl"],y=sub["CA"],
                marker_color=c,showlegend=True,opacity=0.85),1,1)
            fig.add_trace(go.Bar(name=g,x=sub["TypeCl"],y=sub["Nb"],
                marker_color=c,showlegend=False,opacity=0.85),1,2)
        lp(fig,h=280,legend=True); fig.update_layout(barmode="group")
        fig.update_annotations(font=dict(size=10,color=TX2))
        st.plotly_chart(fig,use_container_width=True)

    with c3b:
        sec("DISTRIBUTION DES NOTES DE SATISFACTION")
        desc("Cet histogramme superposé compare la distribution des notes de satisfaction "
             "pour les clients Membres et Standard. La ligne pointillée indique la note "
             "moyenne globale — un indicateur de qualité de service perçue.")
        fig=go.Figure()
        for ct,c in [("Membre",A1),("Standard",A2)]:
            fig.add_trace(go.Histogram(x=DF[DF["TypeCl"]==ct]["Note"],
                name=ct,opacity=0.65,marker_color=c,nbinsx=16,histnorm="percent"))
        lp(fig,h=280,legend=True); fig.update_layout(barmode="overlay")
        fig.add_vline(x=note,line_dash="dot",line_color=A3,
            annotation_text=f" Moy. {note:.2f}",
            annotation_font=dict(color=A3,size=10))
        st.plotly_chart(fig,use_container_width=True)

    c3c,c3d=st.columns(2)
    with c3c:
        sec("ENTONNOIR DE QUALITÉ CLIENT")
        desc("Cet entonnoir filtre progressivement les transactions selon des critères "
             "de qualité croissants. Il mesure la proportion de clients à forte valeur "
             "et à haute satisfaction, indicateurs de fidélisation.")
        ef=pd.DataFrame({"Étape":["Total Transactions","Dépense > Médiane","Note ≥ 7","Note ≥ 8"],
            "N":[N,len(DF[DF["Total"]>DF["Total"].median()]),
                 len(DF[DF["Note"]>=7]),len(DF[DF["Note"]>=8])]})
        fig=go.Figure(go.Funnel(y=ef["Étape"],x=ef["N"],
            marker_color=[A1,A2,A3,A4],textinfo="value+percent initial",
            textfont=dict(size=11,color=TX),connector=dict(fillcolor=BRD)))
        lp(fig,h=280); st.plotly_chart(fig,use_container_width=True)

    with c3d:
        sec("MATRICE : PAIEMENT × TYPE CLIENT")
        desc("Cette carte de chaleur croise les modes de paiement et les types de clients. "
             "Elle indique si les Membres ont des préférences de paiement distinctes "
             "des clients Standard — information utile pour les programmes de fidélité.")
        cp=DF.groupby(["TypeCl","Paiement"])["Total"].sum().reset_index()
        cp_piv=cp.pivot(index="TypeCl",columns="Paiement",values="Total").fillna(0)
        fig=px.imshow(cp_piv,color_continuous_scale=[[0,BG2],[0.5,ra(A6,0.6)],[1,A1]],
            text_auto=".0f",aspect="auto")
        lp(fig,h=280); fig.update_coloraxes(showscale=False)
        fig.update_traces(textfont_size=12)
        st.plotly_chart(fig,use_container_width=True)

    insight(f"""<strong>Analyse clients :</strong> Les Membres représentent
    <strong>{pm:.1f}%</strong> du CA. La répartition Femmes / Hommes est quasi équilibrée
    (<strong>{pf:.1f}% / {100-pf:.1f}%</strong>). La note moyenne de satisfaction est
    <strong>{note:.2f}/10</strong>. Les 3 modes de paiement sont utilisés de façon homogène
    (~33% chacun), sans préférence marquée par segment.""")

# ─── TAB 4 ────────────────────────────────────────────────────
with T4:
    c4a,c4b=st.columns([3,2])
    with c4a:
        sec("CA QUOTIDIEN — TENDANCE ET CUMUL")
        desc("Ce graphique à double axe superpose les revenus journaliers (barres), "
             "la moyenne mobile 7 jours (courbe pointillée) qui lisse les fluctuations, "
             "et le cumul progressif du CA sur la période (courbe verte, axe droit).")
        q=DF.groupby("Date").agg(CA=("Total","sum")).reset_index()
        q["Cumul"]=q["CA"].cumsum()
        q["MA7"]=q["CA"].rolling(7,min_periods=1).mean()
        fig=make_subplots(specs=[[{"secondary_y":True}]])
        fig.add_trace(go.Bar(x=q["Date"],y=q["CA"],name="CA Quotidien",
            marker_color=ra(A1,0.45),marker_line_width=0),secondary_y=False)
        fig.add_trace(go.Scatter(x=q["Date"],y=q["MA7"],name="Moy. 7j",
            line=dict(color=A1,width=1.8,dash="dot")),secondary_y=False)
        fig.add_trace(go.Scatter(x=q["Date"],y=q["Cumul"],name="Cumul CA",
            line=dict(color=A2,width=2.8),fill="tozeroy",
            fillcolor=ra(A2,0.07)),secondary_y=True)
        lp(fig,h=300,legend=True,hover="x unified")
        fig.update_layout(legend=dict(orientation="h",y=1.05,x=0,font=dict(size=10)))
        fig.update_yaxes(secondary_y=True,gridcolor="rgba(0,0,0,0)",
                         tickfont=dict(color=A2,size=9))
        st.plotly_chart(fig,use_container_width=True)

    with c4b:
        sec("VARIATION HEBDOMADAIRE — WoW %")
        desc("Les barres représentent le CA hebdomadaire. La courbe superposée "
             "exprime la variation en pourcentage semaine sur semaine (WoW). "
             "Les marqueurs verts indiquent une progression, rouges une régression.")
        wk=DF.groupby("Sem")["Total"].sum().reset_index()
        wk["WoW"]=wk["Total"].pct_change()*100
        fig=go.Figure()
        fig.add_trace(go.Bar(x=wk["Sem"],y=wk["Total"],name="CA Hebdo",
            marker_color=ra(A6,0.55),marker_line_width=0))
        fig.add_trace(go.Scatter(x=wk["Sem"],y=wk["WoW"],name="WoW %",
            mode="lines+markers",yaxis="y2",line=dict(color=A5,width=2),
            marker=dict(size=6,color=[A2 if (v or 0)>=0 else A5 for v in wk["WoW"].fillna(0)])))
        lp(fig,h=300,legend=True)
        fig.update_layout(yaxis2=dict(overlaying="y",side="right",showgrid=False,
            tickfont=dict(color=A5,size=9),ticksuffix="%"))
        st.plotly_chart(fig,use_container_width=True)

    sec("CARTE DE CHALEUR TEMPORELLE — HEURE × JOUR DE LA SEMAINE")
    desc("Cette carte de chaleur croise les 12 heures d'ouverture (10h–20h) "
         "et les 7 jours de la semaine. Les teintes chaudes signalent les créneaux "
         "horaires à fort CA — précieux pour la planification des équipes et des promotions.")
    jours=["Lundi","Mardi","Mercredi","Jeudi","Vendredi","Samedi","Dimanche"]
    heures=list(range(10,21))
    hm_piv=(DF.groupby(["JourFR","Heure"])["Total"].sum().reset_index()
            .pivot(index="JourFR",columns="Heure",values="Total")
            .reindex([j for j in jours if j in DF["JourFR"].unique()]).fillna(0))
    fig=go.Figure(go.Heatmap(z=hm_piv.values,x=hm_piv.columns,y=hm_piv.index,
        colorscale=[[0,BG2],[0.25,ra(A6,0.5)],[0.65,A2],[1,A1]],
        hovertemplate="<b>%{y}</b> — %{x}h<br>CA : %{z:,.0f} $<extra></extra>",
        showscale=True,colorbar=dict(thickness=10,tickfont=dict(size=9,color=TX2))))
    lp(fig,h=280)
    fig.update_layout(xaxis=dict(title="Heure d'ouverture",tickvals=heures),yaxis=dict(title=""))
    st.plotly_chart(fig,use_container_width=True)

    c4c,c4d,c4e=st.columns(3)
    with c4c:
        sec("PÉRIODE DE LA JOURNÉE")
        desc("Répartition du CA sur les 3 grandes plages horaires. "
             "Identifie les périodes de pic d'activité pour optimiser les ressources.")
        pj=DF.groupby("Periode")["Total"].sum().reset_index().sort_values("Total")
        fig=go.Figure(go.Bar(x=pj["Total"],y=pj["Periode"],orientation="h",
            marker_color=[ra(A6,0.7),ra(A1,0.7),ra(A2,0.7)],
            text=pj["Total"].apply(fmt),textposition="outside",
            textfont=dict(size=10,color=TX3)))
        lp(fig,h=240); st.plotly_chart(fig,use_container_width=True)
    with c4d:
        sec("CA PAR MOIS")
        desc("Vue mensuelle agrégée permettant d'identifier "
             "les mois les plus porteurs sur le trimestre.")
        mo2=DF.groupby(["NomM","Mois"]).agg(CA=("Total","sum")).reset_index().sort_values("Mois")
        fig=go.Figure(go.Bar(x=mo2["NomM"],y=mo2["CA"],
            marker_color=[A1,A2,A3][:len(mo2)],
            text=mo2["CA"].apply(fmt),textposition="outside",
            textfont=dict(size=10,color=TX3)))
        lp(fig,h=240); st.plotly_chart(fig,use_container_width=True)
    with c4e:
        sec("COURBE HORAIRE DU CA")
        desc("Revenu cumulé pour chaque heure de la journée. "
             "Le pic identifié oriente la planification du personnel.")
        hr=DF.groupby("Heure")["Total"].sum().reset_index()
        fig=go.Figure(go.Scatter(x=hr["Heure"],y=hr["Total"],
            fill="tozeroy",fillcolor=ra(A1,0.1),
            line=dict(color=A1,width=2.5),mode="lines+markers",
            marker=dict(size=5,color=A1)))
        lp(fig,h=240); fig.update_xaxes(tickvals=heures,title="Heure")
        st.plotly_chart(fig,use_container_width=True)

    top_h=DF.groupby("Heure")["Total"].sum().idxmax()
    top_j=DF.groupby("JourFR")["Total"].sum().idxmax()
    top_m=DF.groupby("NomM")["Total"].sum().idxmax()
    insight(f"""<strong>Observations temporelles :</strong>
    Le pic d'activité se situe à <strong>{top_h}h</strong>.
    Le <strong>{top_j}</strong> est le jour le plus générateur de revenus.
    <strong>{top_m}</strong> enregistre le meilleur résultat mensuel.
    CA cumulé sur la période : <strong>{fmt(rev)}</strong>.""")

# ─── TAB 5 ────────────────────────────────────────────────────
with T5:
    sec("STATISTIQUES DESCRIPTIVES")
    desc("Ce tableau récapitule les principaux indicateurs statistiques (moyenne, "
         "médiane, quartiles, écart-type) pour chaque variable numérique du jeu de données. "
         "Utile pour détecter les valeurs extrêmes et la dispersion.")
    NUM=["PrixU","Qte","Taxe","Total","RevBrut","Note"]
    ca5,cb5=st.columns(2)
    with ca5:
        d5=DF[NUM].describe().round(2)
        d5.index=["N","Moyenne","Écart-type","Min","Q1 (25%)","Médiane","Q3 (75%)","Max"]
        d5.columns=["Prix U.","Quantité","Taxe ($)","Total ($)","Rev. Brut","Note"]
        st.dataframe(d5,use_container_width=True)
    with cb5:
        vs=st.selectbox("Visualiser la distribution d'une variable",NUM,index=NUM.index("Total"))
        desc(f"Distribution de la variable <strong>{vs}</strong> : "
             f"les barres montrent la fréquence observée, la courbe verte est l'estimation "
             f"par noyau (KDE) qui lisse la distribution empirique.")
        v=DF[vs].dropna().values
        bw=max(1.06*v.std()*len(v)**(-0.2),0.01)
        kx=np.linspace(v.min(),v.max(),120)
        ky=np.array([(np.exp(-0.5*((kx[i]-v)/bw)**2)/np.sqrt(2*np.pi)/bw).mean()
                     for i in range(len(kx))])
        ky=ky*len(v)*(v.max()-v.min()+1e-9)/28
        fig=go.Figure()
        fig.add_trace(go.Histogram(x=v,nbinsx=28,
            marker=dict(color=A1,opacity=0.65,line=dict(color=BRD,width=0.4)),name="Fréquence"))
        fig.add_trace(go.Scatter(x=kx,y=ky,mode="lines",
            line=dict(color=A2,width=2.2),name="Densité (KDE)"))
        lp(fig,h=250,legend=True); st.plotly_chart(fig,use_container_width=True)

    sec("MATRICE DE CORRÉLATION DE PEARSON")
    desc("La matrice de corrélation mesure la force de la relation linéaire entre chaque paire "
         "de variables numériques. Les valeurs proches de +1 (bleu) indiquent une corrélation "
         "positive forte ; proches de -1 (rouge), une corrélation inverse ; proches de 0, "
         "l'absence de relation linéaire.")
    corr=DF[NUM].corr().round(3)
    fig=px.imshow(corr,text_auto=".2f",aspect="auto",
        color_continuous_scale=[[0,A5],[0.5,BG2],[1,A2]],zmin=-1,zmax=1)
    lp(fig,h=320)
    fig.update_coloraxes(colorbar=dict(thickness=10,tickfont=dict(size=9,color=TX2)))
    fig.update_traces(textfont_size=11)
    st.plotly_chart(fig,use_container_width=True)

    sec("TABLE DES TRANSACTIONS FILTRÉES")
    desc("Table de données brutes correspondant aux filtres actifs. "
         "Utilisez la recherche textuelle pour retrouver une transaction spécifique.")
    cs1,cs2,cs3=st.columns([2,1,1])
    with cs1: rch=st.text_input("Rechercher (Facture, Ville, Produit, Paiement…)","")
    with cs2: tri=st.selectbox("Trier par",["Date","Total","Note","PrixU"])
    with cs3: nb=st.selectbox("Lignes à afficher",[25,50,100,200,500,len(DF)])

    aff=DF[["ID","Date","Branche","Ville","TypeCl","Genre",
            "Produit","PrixU","Qte","Total","Paiement","Note"]].copy()
    if rch:
        m=aff.apply(lambda c:c.astype(str).str.contains(rch,case=False)).any(axis=1)
        aff=aff[m]
    aff=aff.sort_values(tri,ascending=(tri=="Date")).head(nb)
    aff["Total"]=aff["Total"].apply(lambda v:f"${v:.2f}")
    aff["PrixU"]=aff["PrixU"].apply(lambda v:f"${v:.2f}")
    aff["Note"]=aff["Note"].apply(lambda v:f"{v:.1f}")
    aff["Date"]=aff["Date"].astype(str)
    aff.columns=["Facture","Date","Branche","Ville","Type","Genre",
                 "Produit","Prix U.","Qté","Total","Paiement","Note"]
    st.dataframe(aff,use_container_width=True,hide_index=True)

    sec("EXPORT DES DONNÉES")
    desc("Téléchargez les données dans le format de votre choix pour des analyses "
         "complémentaires dans Excel, R, Python ou tout autre outil statistique.")
    e1,e2,e3=st.columns(3)
    with e1:
        st.download_button("Données filtrées (.csv)",
            DF.to_csv(index=False).encode(),"ventes_filtrees.csv","text/csv",
            use_container_width=True)
    with e2:
        r2=DF.groupby(["Branche","Produit"]).agg(
            CA=("Total","sum"),Txn=("ID","count"),Note=("Note","mean")).reset_index()
        st.download_button("Résumé Branche × Produit (.csv)",
            r2.to_csv(index=False).encode(),"resume.csv","text/csv",
            use_container_width=True)
    with e3:
        pv=DF.pivot_table(values="Total",index="Produit",
            columns="Branche",aggfunc="sum").round(2).reset_index()
        st.download_button("Table Pivot Produit × Branche (.csv)",
            pv.to_csv(index=False).encode(),"pivot.csv","text/csv",
            use_container_width=True)