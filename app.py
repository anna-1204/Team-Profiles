import streamlit as st
import streamlit.components.v1 as components
import pandas as pd
import base64
import re
from pathlib import Path
import os
st.set_page_config(page_title="Team Profiles", layout="wide")

ROLE_ORDER = [
    "technical lead", "module lead", "senior sharepoint consultant",
    "sharepoint consultant", "sharepoint support engineer",
    "senior software design engineer", "ssde", "software design engineer",
    "senior software design engineer, cots ktlo support & gle2e dev system support",
    "cots ktlo support & gle2e dev system support",
    "sharepoint support", "gadi support", "gmind support", "app dev",
    "infra devops", "data engineering", "bi developer", "saas",
]
LEVEL_ORDER = ["L3", "L2", "L1"]
BASE_DIR   = Path(__file__).parent
IMAGES_DIR = BASE_DIR / "images"

def parse_level(d):
    if not isinstance(d, str): return "L2"
    m = re.search(r'L(\d)', d, re.IGNORECASE)
    return f"L{m.group(1)}" if m else "L2"

def parse_role(d):
    if not isinstance(d, str): return "Unknown"
    cleaned = re.sub(r'^L\d[\s,\-–]+', '', d, flags=re.IGNORECASE).strip()
    return re.sub(r'\n', ' ', cleaned).strip() or "Unknown"

def role_sort_key(role):
    r = role.lower()
    for i, p in enumerate(ROLE_ORDER):
        if p in r: return i
    return len(ROLE_ORDER)

def img_to_b64(path: Path) -> str:
    try:
        ext  = path.suffix.lower()
        mime = "jpeg" if ext in [".jpg", ".jpeg"] else "png"
        with open(path, "rb") as f:
            return f"data:image/{mime};base64,{base64.b64encode(f.read()).decode()}"
    except:
        return ""

def normalize(s):
    return re.sub(r'[\s_\-]+', '', s).lower()

def get_image(person_name) -> str:
    """Match by full name — Ankit_Sharma.jpg matches 'Ankit Sharma'."""
    if isinstance(person_name, str) and person_name.strip() and IMAGES_DIR.exists():
        base = normalize(person_name.strip())
        for img_file in os.listdir(IMAGES_DIR):
            if normalize(Path(img_file).stem) == base:
                return img_to_b64(IMAGES_DIR / img_file)
    svg = "<svg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 200 200'><rect width='200' height='200' fill='%23dde3ee'/><circle cx='100' cy='72' r='42' fill='%239aabc2'/><ellipse cx='100' cy='185' rx='65' ry='50' fill='%239aabc2'/></svg>"
    return f"data:image/svg+xml,{svg}"

def get_bullets(jd) -> list:
    if not isinstance(jd, str): return []
    parts = re.split(r'[\n\r\u2022•]+', jd)
    return [p.strip().lstrip("-•\t ").strip() for p in parts if p.strip().lstrip("-•\t ").strip()][:3]

def get_certs(cert) -> list:
    if not isinstance(cert, str) or not cert.strip() or cert.lower() == "nan": return []
    parts = re.split(r'[\n\r•\u2022,]+', cert)
    result = []
    for p in parts:
        p = p.strip().lstrip("-•\t ").strip()
        if p and p.lower() != "nan":
            result.append(p)
    return result[:4]

# ── Set your SharePoint Excel direct-download URL here ──────────────────────
# Leave as empty string to use local file instead
SHAREPOINT_URL = ""  # e.g. "https://company.sharepoint.com/...download=1"

@st.cache_data(ttl=0)
def load_data():
    import io, requests
    if SHAREPOINT_URL:
        r = requests.get(SHAREPOINT_URL)
        xl = pd.ExcelFile(io.BytesIO(r.content))
    else:
        excel_files = list(BASE_DIR.glob("*.xlsx"))
        xl = pd.ExcelFile(excel_files[0])
    all_dfs = []
    for sheet in xl.sheet_names:
        try:
            df = pd.read_excel(xl, sheet_name=sheet)
            if df.empty or len(df.columns) < 3: continue
            df.columns = [str(c).strip() for c in df.columns]
            def find_col(keywords):
                for c in df.columns:
                    if any(k in c.lower() for k in keywords): return c
                return None
            nc = find_col(["full name"])
            dc = find_col(["designation"])
            jc = find_col(["liner", "current jd"])
            pc = find_col(["photo"])
            cc = find_col(["cert"])
            if not all([nc, dc, jc, pc]): continue
            cols     = [nc, dc, jc, pc] + ([cc] if cc else [])
            newnames = ["name","designation","jd","photo"] + (["cert"] if cc else [])
            sub = df[cols].copy()
            sub.columns = newnames
            if "cert" not in sub.columns: sub["cert"] = ""
            all_dfs.append(sub)
        except: continue
    df = pd.concat(all_dfs, ignore_index=True)
    df = df.dropna(subset=["name"])
    df["name"] = df["name"].astype(str).str.strip()
    df = df[df["name"].str.lower() != "nan"]
    df = df.drop_duplicates(subset=["name"], keep="first")
    df["level"]      = df["designation"].apply(parse_level)
    df["role"]       = df["designation"].apply(parse_role)
    df["role_order"] = df["role"].apply(role_sort_key)
    return df

df = load_data()

st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;600;700;800&display=swap');
html, body, [class*="css"] { font-family: 'Inter', sans-serif; }
.block-container { padding: 1.5rem 2rem; }
.pg-title { font-size: 1.7rem; font-weight: 800; color: #0f172a; margin-bottom: 0.1rem; }
.pg-sub   { color: #64748b; font-size: 0.88rem; margin-bottom: 1.5rem; }
.lvl-section {
  font-size: 1.3rem; font-weight: 800; color: #0f172a;
  margin: 2.2rem 0 0.2rem 0;
  padding-bottom: 0.4rem;
  border-bottom: 3px solid #3b82f6;
}
.role-lbl {
  font-size: 0.73rem; font-weight: 700; color: #64748b;
  text-transform: uppercase; letter-spacing: 0.07em;
  margin: 0.8rem 0 0.2rem; display: flex; align-items: center; gap: 6px;
}
.role-lbl::before { content: "◆"; color: #f59e0b; font-size: 0.55rem; }
</style>
""", unsafe_allow_html=True)

st.markdown('<div class="pg-title">👥 Team Profiles</div>', unsafe_allow_html=True)
st.markdown(f'<div class="pg-sub">{len(df)} members · L3 → L2 → L1</div>', unsafe_allow_html=True)

col1, col2 = st.columns([6,1])
with col2:
    if st.button("🔄 Refresh"):
        st.cache_data.clear()
        st.rerun()

CARD_CSS = """
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;600;700&display=swap');
* { box-sizing: border-box; margin: 0; padding: 0; font-family: 'Inter', sans-serif; }
body { background: transparent; }
.carousel-wrap { position: relative; padding: 0 42px; }
.card-row {
  display: flex; gap: 10px;
  overflow-x: auto; scroll-behavior: smooth;
  padding: 12px 4px 16px; scrollbar-width: thin;
  scrollbar-color: #cbd5e1 transparent;
}
.card-row::-webkit-scrollbar { height: 5px; }
.card-row::-webkit-scrollbar-thumb { background: #cbd5e1; border-radius: 3px; }
.arrow-btn {
  position: absolute; top: 42%; transform: translateY(-50%);
  background: #fff; border: none; border-radius: 50%;
  width: 34px; height: 34px; cursor: pointer;
  box-shadow: 0 3px 10px rgba(0,0,0,0.18);
  font-size: 20px; color: #334155; z-index: 10;
  display: flex; align-items: center; justify-content: center;
}
.arrow-btn:hover { background: #3b82f6; color: #fff; }
.left-btn  { left: 2px; }
.right-btn { right: 2px; }

/* Card — wider, auto height */
.card {
  min-width: 240px; max-width: 240px;
  background: #fff; border-radius: 18px;
  box-shadow: 0 3px 16px rgba(0,0,0,0.09);
  padding: 20px 18px 16px;
  display: flex; flex-direction: column; align-items: center;
  text-align: center; flex-shrink: 0;
  border: 1px solid #eaf0f8;
  transition: transform 0.18s, box-shadow 0.18s;
}
.card:hover { transform: translateY(-4px); box-shadow: 0 10px 28px rgba(37,99,235,0.16); }

.avatar-wrap { position: relative; width: 110px; height: 110px; margin-bottom: 12px; flex-shrink: 0; }
.avatar-wrap svg { position: absolute; top: 0; left: 0; width: 100%; height: 100%; }
.avatar-img {
  position: absolute; top: 8px; left: 8px;
  width: 94px; height: 94px; border-radius: 50%;
  object-fit: cover; border: 3px solid #fff;
}
.level-badge {
  background: #eff6ff; color: #2563eb; font-size: 0.65rem; font-weight: 700;
  padding: 2px 8px; border-radius: 10px; margin-bottom: 8px;
  letter-spacing: 0.05em; align-self: flex-start;
}
.name  { font-size: 0.92rem; font-weight: 700; color: #1e293b; margin-bottom: 3px; line-height: 1.4; word-break: break-word; }
.role-tag { font-size: 0.73rem; font-weight: 600; color: #2563eb; margin-bottom: 7px; line-height: 1.3; }
.gold-bar { width: 36px; height: 3px; background: #f59e0b; border-radius: 2px; margin: 0 auto 10px; flex-shrink: 0; }

.section-label {
  font-size: 0.62rem; font-weight: 700; color: #94a3b8;
  text-transform: uppercase; letter-spacing: 0.06em;
  text-align: left; width: 100%; margin: 8px 0 3px;
}
.bul { list-style: none; text-align: left; width: 100%; }
.bul li {
  font-size: 0.71rem; color: #475569; line-height: 1.55; padding: 2px 0;
  display: flex; gap: 6px; align-items: flex-start;
  word-break: break-word;
}
.bul li::before { content: "❑"; color: #94a3b8; font-size: 0.58rem; flex-shrink: 0; margin-top: 3px; }

.cert-list { list-style: none; text-align: left; width: 100%; }
.cert-list li {
  font-size: 0.71rem; color: #0f766e; line-height: 1.55; padding: 2px 0;
  display: flex; gap: 6px; align-items: flex-start;
  word-break: break-word;
}
.cert-list li::before { content: "🏅"; font-size: 0.62rem; flex-shrink: 0; }

.arrows { display: flex; gap: 3px; margin-top: 12px; justify-content: center; flex-shrink: 0; }
.arr { width: 0; height: 0; border-top: 6px solid transparent; border-bottom: 6px solid transparent; border-left: 10px solid #f59e0b; }
</style>
"""

def ring_svg():
    return """<svg viewBox="0 0 110 110">
      <circle cx="55" cy="55" r="51" fill="none" stroke="#e2e8f0" stroke-width="5"/>
      <circle cx="55" cy="55" r="51" fill="none" stroke="#2563eb" stroke-width="5"
        stroke-dasharray="290 32" stroke-dashoffset="8" stroke-linecap="round"
        transform="rotate(-100 55 55)"/>
    </svg>"""

def build_card(row):
    img      = get_image(row.get("name"))
    buls     = get_bullets(row.get("jd", ""))
    certs    = get_certs(str(row.get("cert", "")))
    bul_html  = "".join(f"<li>{b}</li>" for b in buls)
    cert_html = "".join(f"<li>{c}</li>" for c in certs)
    jd_section   = f'<div class="section-label">Responsibilities</div><ul class="bul">{bul_html}</ul>' if bul_html else ""
    cert_section = f'<div class="section-label">Certifications</div><ul class="cert-list">{cert_html}</ul>' if cert_html else ""
    return f"""
    <div class="card">
      <div class="level-badge">{row['level']}</div>
      <div class="avatar-wrap">{ring_svg()}
        <img class="avatar-img" src="{img}" alt="{row['name']}"/>
      </div>
      <div class="name">{row['name']}</div>
      <div class="role-tag">{row['role']}</div>
      <div class="gold-bar"></div>
      {jd_section}
      {cert_section}
      <div class="arrows"><div class="arr"></div><div class="arr"></div></div>
    </div>"""

def build_carousel(group_id, rows_df):
    safe_id = re.sub(r'[^a-zA-Z0-9]', '_', group_id)
    cards   = "".join(build_card(r) for _, r in rows_df.iterrows())
    return f"""{CARD_CSS}
    <div class="carousel-wrap">
      <button class="arrow-btn left-btn"  onclick="document.getElementById('{safe_id}').scrollBy({{left:-290,behavior:'smooth'}})">&#8249;</button>
      <div id="{safe_id}" class="card-row">{cards}</div>
      <button class="arrow-btn right-btn" onclick="document.getElementById('{safe_id}').scrollBy({{left:290,behavior:'smooth'}})">&#8250;</button>
    </div>"""

def estimate_height(rows_df) -> int:
    max_h = 0
    for _, r in rows_df.iterrows():
        buls  = get_bullets(r.get("jd",""))
        certs = get_certs(str(r.get("cert","")))
        h = 230  # avatar + name + level + bar
        if buls:  h += 24 + sum(max(1, len(b)//38) * 22 + 22 for b in buls)
        if certs: h += 24 + sum(max(1, len(c)//38) * 22 + 22 for c in certs)
        h += 60  # arrows + card padding
        max_h = max(max_h, h)
    return max_h + 80

for level in LEVEL_ORDER:
    ldf = df[df["level"] == level]
    if ldf.empty: continue
    label = {"L3":"L3 — Senior Leadership","L2":"L2 — Mid-Level","L1":"L1 — Associate"}.get(level, level)
    st.markdown(f'<div class="lvl-section">{label}</div>', unsafe_allow_html=True)
    roles = ldf[["role","role_order"]].drop_duplicates().sort_values("role_order")["role"].tolist()
    for role in roles:
        rdf = ldf[ldf["role"] == role]
        st.markdown(f'<div class="role-lbl">{role}</div>', unsafe_allow_html=True)
        height = estimate_height(rdf)
        components.html(build_carousel(f"{level}_{role}", rdf), height=height, scrolling=True)

st.markdown("---")
st.caption("Edit Profile_details.xlsx · add photos to images/ · refresh to update")
