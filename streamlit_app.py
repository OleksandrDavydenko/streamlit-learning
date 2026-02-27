# -*- coding: utf-8 -*-
import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from db_connection import get_expenses_data
from datetime import datetime
import streamlit.components.v1 as components

# ============================================================
# КОНФІГУРАЦІЯ
# ============================================================
st.set_page_config(
    page_title="Операційні витрати | FTP",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="collapsed",
)

UA_MONTHS = {
    1: "Січень", 2: "Лютий", 3: "Березень", 4: "Квітень",
    5: "Травень", 6: "Червень", 7: "Липень", 8: "Серпень",
    9: "Вересень", 10: "Жовтень", 11: "Листопад", 12: "Грудень",
}

# ── Custom CSS ──────────────────────────────────────────────
st.markdown("""
<style>
[data-testid="stSidebar"] { background-color: #f5f7fa; border-right: 1px solid #dde3ea; }
[data-testid="stSidebar"] .stCheckbox label { font-size: 13px; }
.ftp-logo { display:flex; align-items:center; gap:10px; padding:6px 0 14px 0;
    border-bottom:1px solid #cdd5de; margin-bottom:14px; }
.ftp-logo-circle { width:52px; height:52px;
    background:radial-gradient(circle at 40% 40%, #0055a4, #001f5b);
    border-radius:50%; display:flex; align-items:center; justify-content:center;
    color:white; font-weight:900; font-size:15px; flex-shrink:0; letter-spacing:0.5px; }
.ftp-logo-text .ftp-main { color:#0055a4; font-size:20px; font-weight:900; letter-spacing:1px; }
.ftp-logo-text .ftp-sub  { color:#555; font-size:9px; letter-spacing:0.3px; }
.sidebar-section-label { font-size:13px; font-weight:700; color:#333; margin:12px 0 4px 0; }
.main-title { color:#e63946; text-align:center; font-size:26px; font-weight:800;
    letter-spacing:0.5px; padding:6px 0 2px 0;
    border-bottom:2px solid #e63946; margin-bottom:10px; }
.period-label { font-size:12px; font-weight:700; color:#444; margin-bottom:2px; }
.kpi-block { text-align:center; padding:10px 6px; }
.kpi-label { font-size:11px; color:#888; line-height:1.3; min-height:30px; }
.kpi-value { font-size:26px; font-weight:900; color:#111; line-height:1.2; margin-top:4px; }
.kpi-value-neg { font-size:26px; font-weight:900; color:#e63946; line-height:1.2; margin-top:4px; }
/* ── Header Banner ── */
.header-banner {
    background: linear-gradient(135deg, #0a2342 0%, #1a5276 60%, #0055a4 100%);
    border-radius: 12px; padding: 22px 30px; margin-bottom: 18px;
    display: flex; align-items: center; justify-content: space-between;
    box-shadow: 0 4px 18px rgba(0,21,62,0.18);
}
.header-left { display:flex; align-items:center; gap:18px; }
.header-logo-circle {
    width:58px; height:58px;
    background: rgba(255,255,255,0.15); border:2px solid rgba(255,255,255,0.35);
    border-radius:50%; display:flex; align-items:center; justify-content:center;
    font-size:17px; font-weight:900; color:white; letter-spacing:1px; flex-shrink:0;
}
.header-title { color:white; font-size:24px; font-weight:900; letter-spacing:0.5px; line-height:1.2; }
.header-subtitle { color:rgba(255,255,255,0.72); font-size:13px; margin-top:3px; }
.header-right { text-align:right; }
.header-date { color:rgba(255,255,255,0.6); font-size:12px; }
.header-badge {
    display:inline-block; background:rgba(255,255,255,0.15);
    border:1px solid rgba(255,255,255,0.3); border-radius:20px;
    padding:4px 14px; color:white; font-size:12px; font-weight:700; margin-top:6px;
}
[data-testid="stTabs"] [data-baseweb="tab-list"] { gap:4px; border-bottom:2px solid #dde3ea; flex-wrap:wrap; }
[data-testid="stTabs"] [data-baseweb="tab"] {
    background:#f0f4f8; border-radius:8px 8px 0 0; padding:8px 18px;
    font-weight:600; color:#555; border:1px solid #dde3ea; border-bottom:none;
}
[data-testid="stTabs"] [aria-selected="true"] {
    background:white !important; color:#1a5276 !important; border-bottom:2px solid white;
}
/* ── KPI columns: stack on very small screens ── */
@media (max-width: 640px) {
    header[data-testid="stHeader"] { display:none !important; }
    .block-container { padding-top:8px !important; }
    .header-banner { display:block !important; padding:12px 14px; }
    .header-logo-circle { display:none !important; }
    .header-left { display:block !important; margin-bottom:6px; }
    .header-title { font-size:17px; white-space:normal; word-break:break-word; margin-bottom:2px; }
    .header-subtitle { font-size:11px; white-space:normal; word-break:break-word; }
    .header-right { display:block !important; margin-top:4px; }
    .header-date { font-size:11px; }
    .header-badge { font-size:11px; padding:3px 10px; }
    .kpi-value, .kpi-value-neg { font-size:20px; }
    /* Streamlit column gap reduction */
    [data-testid="column"] { padding: 0 4px !important; }
    /* Reduce main padding */
    .block-container { padding-left:12px !important; padding-right:12px !important; padding-top:12px !important; }
    [data-testid="stTabs"] [data-baseweb="tab"] { padding:6px 10px; font-size:12px; }
}
/* ── Tablet ── */
@media (max-width: 900px) {
    .header-title { font-size:20px; }
    .header-subtitle { font-size:11px; }
    [data-testid="stTabs"] [data-baseweb="tab"] { padding:7px 12px; font-size:13px; }
}
/* ── Collapse sidebar padding on mobile ── */
@media (max-width: 768px) {
    section[data-testid="stSidebar"] { min-width: 80vw !important; max-width: 90vw !important; }
    section[data-testid="stSidebar"] > div:first-child { width: 100% !important; min-width: 100% !important; }
    [data-testid="stSidebarContent"],
    [data-testid="stSidebarUserContent"] { width: 100% !important; overflow-x: hidden !important; }
    .block-container { padding-left:10px !important; padding-right:10px !important; }

    /* Force checkboxes to full width and labels visible */
    [data-testid="stSidebar"] .stCheckbox,
    [data-testid="stSidebar"] [data-testid="stCheckbox"] { width: 100% !important; min-width: 0 !important; }
    [data-testid="stSidebar"] .stCheckbox > label,
    [data-testid="stSidebar"] [data-testid="stCheckbox"] > label {
        display: flex !important;
        align-items: center !important;
        width: 100% !important;
        min-width: 0 !important;
        overflow: visible !important;
        white-space: normal !important;
        font-size: 14px !important;
        gap: 8px !important;
        color: #111 !important;
    }
    [data-testid="stSidebar"] .stCheckbox label > div:first-child,
    [data-testid="stSidebar"] [data-testid="stCheckbox"] label > div:first-child {
        flex-shrink: 0 !important;
        width: 20px !important;
        height: 20px !important;
    }
    [data-testid="stSidebar"] .stCheckbox label p,
    [data-testid="stSidebar"] [data-testid="stCheckbox"] label p {
        display: inline !important;
        overflow: visible !important;
        white-space: normal !important;
        word-break: break-word !important;
        margin: 0 !important;
        color: #111 !important;
    }
    /* Prevent overflow clipping on the vertical block wrapper (but NOT the scroll container itself) */
    [data-testid="stSidebar"] .stVerticalBlock {
        width: 100% !important;
    }
    /* Also target the text container INSIDE the checkbox label (second child div) */
    [data-testid="stSidebar"] .stCheckbox label > div:last-child,
    [data-testid="stSidebar"] [data-testid="stCheckbox"] label > div:last-child {
        min-width: 0 !important;
        flex: 1 1 auto !important;
        overflow: visible !important;
    }
}
</style>
""", unsafe_allow_html=True)

# ============================================================
# АВТОРИЗАЦІЯ
# ============================================================
def check_password() -> bool:
    if st.session_state.get("password_correct"):
        return True
    col1, col2, col3 = st.columns([1, 1, 1])
    with col2:
        st.markdown(
            "<h1 style='text-align:center'>🔐 Звіт</h1>"
            "<p style='text-align:center;color:#555;'>Введіть пароль для доступу до звіту</p>",
            unsafe_allow_html=True,
        )
        st.write("")
        with st.form("login_form"):
            pwd = st.text_input("Пароль", type="password",
                                placeholder="Введіть пароль",
                                label_visibility="collapsed")
            submitted = st.form_submit_button("🔓 Увійти", use_container_width=True)
        if submitted:
            stored = str(st.secrets.get("password", "2101")).strip()
            if pwd.strip() and pwd.strip() == stored:
                st.session_state.password_correct = True
                st.rerun()
            else:
                st.error("❌ Неправильний пароль!")
    return False

if not check_password():
    st.stop()

# ============================================================
# ЗАВАНТАЖЕННЯ ДАНИХ
# ============================================================
@st.cache_data(ttl=1800, show_spinner="⏳ Завантаження даних...")
def load_data() -> pd.DataFrame:
    df = get_expenses_data()
    if df.empty:
        return df
    df["Period"] = pd.to_datetime(df["Period"], errors="coerce")
    df["Year"] = df["Period"].dt.year
    df["Month_Num"] = df["Period"].dt.month
    df["Month_Name"] = df["Month_Num"].map(UA_MONTHS)
    df["Sum"] = pd.to_numeric(df["Sum"], errors="coerce").fillna(0)
    return df

try:
    df_raw = load_data()
except Exception as e:
    st.error("Помилка при отриманні даних:")
    st.exception(e)
    st.stop()

if df_raw.empty:
    st.warning("Дані не знайдено або таблиця порожня.")
    st.stop()

# ============================================================
# SIDEBAR
# ============================================================
with st.sidebar:
    # ── FTP Logo ─────────────────────────────────────────────
    st.markdown("""
    <div class="ftp-logo">
        <div class="ftp-logo-circle">FTP</div>
        <div class="ftp-logo-text">
            <div class="ftp-main">FTP</div>
            <div class="ftp-sub">Freight Transport Partner</div>
        </div>
    </div>
    """, unsafe_allow_html=True)

    # ── Скидання (до рендеру будь-яких віджетів) ────────────
    if st.session_state.pop("_do_reset", False):
        for d in st.session_state.get("dept_states", {}):
            st.session_state["dept_states"][d] = False
            st.session_state[f"dept_cb_{d}"] = False
        for e in st.session_state.get("expense_states", {}):
            st.session_state["expense_states"][e] = False
            st.session_state[f"exp_cb_{e}"] = False
        st.session_state["months_multiselect"] = []
        st.session_state["expense_search"] = ""

    # ── Рік і Місяці ─────────────────────────────────────────
    st.markdown('<div class="sidebar-section-label">📅 Період звіту</div>', unsafe_allow_html=True)
    all_years_sb = sorted(df_raw["Year"].dropna().unique().astype(int), reverse=True)
    sel_year = st.selectbox("Рік", options=all_years_sb, index=0,
                            key="year_select", label_visibility="collapsed",
                            format_func=lambda y: f"{y}")
    months_avail_sb = sorted(
        df_raw[df_raw["Year"] == sel_year]["Month_Num"].dropna().unique().astype(int))
    sel_months = st.multiselect(
        "Місяці", options=months_avail_sb,
        key="months_multiselect", label_visibility="collapsed",
        format_func=lambda m: UA_MONTHS[m], placeholder="Усі місяці")
    if not sel_months:
        sel_months = months_avail_sb
    st.markdown("<div style='height:4px'></div>", unsafe_allow_html=True)

    # ── Відділ (Department) ───────────────────────────────────
    st.markdown('<div class="sidebar-section-label">🏢 Відділ</div>', unsafe_allow_html=True)
    all_depts = sorted(df_raw["Department"].dropna().unique().tolist())
    if "dept_states" not in st.session_state:
        st.session_state["dept_states"] = {d: False for d in all_depts}
    for d in all_depts:
        if d not in st.session_state["dept_states"]:
            st.session_state["dept_states"][d] = False
    dept_container = st.container(height=165)
    with dept_container:
        for dept in all_depts:
            st.session_state["dept_states"][dept] = st.checkbox(
                dept, value=st.session_state["dept_states"].get(dept, False),
                key=f"dept_cb_{dept}")
    selected_depts = [d for d in all_depts if st.session_state["dept_states"].get(d, False)]
    if not selected_depts:
        selected_depts = all_depts

    # ── Стаття витрат (Type_of_expense) ──────────────────────
    st.markdown('<div class="sidebar-section-label">📌 Стаття витрат</div>', unsafe_allow_html=True)
    search_expense = st.text_input("Пошук статті витрат", placeholder="🔍 Пошук", key="expense_search",
                                   label_visibility="collapsed")
    all_expenses = sorted(df_raw["Type_of_expense"].dropna().unique().tolist())
    filtered_expenses_list = (
        [e for e in all_expenses if search_expense.lower() in e.lower()]
        if search_expense else all_expenses
    )
    if "expense_states" not in st.session_state:
        st.session_state["expense_states"] = {e: False for e in all_expenses}
    for e in all_expenses:
        if e not in st.session_state["expense_states"]:
            st.session_state["expense_states"][e] = False
    exp_container = st.container(height=165)
    with exp_container:
        for exp in filtered_expenses_list:
            st.session_state["expense_states"][exp] = st.checkbox(
                exp, value=st.session_state["expense_states"].get(exp, False),
                key=f"exp_cb_{exp}")
    selected_expenses = [e for e in all_expenses if st.session_state["expense_states"].get(e, False)]
    if not selected_expenses:
        selected_expenses = all_expenses

    # ── Дії ──────────────────────────────────────────────────
    st.markdown("<div style='height:6px'></div>", unsafe_allow_html=True)
    if st.button("🧹 Скинути фільтри", use_container_width=True, key="reset_filters"):
        st.session_state["_do_reset"] = True
        st.rerun()
    if st.button("🔄 Оновити дані", use_container_width=True, key="refresh_btn"):
        st.cache_data.clear()
        st.rerun()

# ============================================================
# ФІЛЬТРАЦІЯ
# ============================================================
filtered_df = df_raw[
    (df_raw["Year"] == sel_year) &
    (df_raw["Month_Num"].isin(sel_months)) &
    (df_raw["Department"].isin(selected_depts)) &
    (df_raw["Type_of_expense"].isin(selected_expenses))
].copy()

if filtered_df.empty:
    st.info("Немає даних за обраними фільтрами.")
    st.stop()

# ── KPI-розрахунки ────────────────────────────────────────
unplanned_mask = filtered_df["Type_of_expense"].str.contains(
    "поза план|позаплан", case=False, na=False)
unplanned_sum = filtered_df.loc[unplanned_mask, "Sum"].sum()
total_sum     = filtered_df["Sum"].sum()
planned_diff  = total_sum - unplanned_sum

def fmt_tis(v: float) -> str:
    if abs(v) >= 1000:
        return f"{v/1000:,.2f} ТИС."
    return f"{v:,.2f}"

def hex_to_rgba(hex_color: str, alpha: float = 0.10) -> str:
    """Convert '#rrggbb' to 'rgba(r,g,b,alpha)'."""
    h = hex_color.lstrip('#')
    r, g, b = int(h[0:2], 16), int(h[2:4], 16), int(h[4:6], 16)
    return f"rgba({r},{g},{b},{alpha})"

# ── Рядок для позначення обраного періоду ─────────────────
if len(sel_months) == len(months_avail_sb):
    period_str = f"Весь {sel_year} рік"
elif len(sel_months) == 1:
    period_str = f"{UA_MONTHS[sel_months[0]]} {sel_year}"
else:
    period_str = ", ".join(UA_MONTHS[m] for m in sorted(sel_months)) + f" {sel_year}"

# ── Гарний заголовок ───────────────────────────────────────
st.markdown(f"""
<div class="header-banner">
  <div class="header-left">
    <div class="header-logo-circle">FTP</div>
    <div>
      <div class="header-title">Операційні витрати</div>
      <div class="header-subtitle">Freight Transport Partner &nbsp;•&nbsp; Бюджетна аналітика</div>
    </div>
  </div>
  <div class="header-right">
    <div class="header-date">Станом на: {datetime.now().strftime('%d.%m.%Y %H:%M')}</div>
    <div class="header-badge">📅 {period_str}</div>
  </div>
</div>
""", unsafe_allow_html=True)

# ============================================================
# ВКЛАДКИ
# ============================================================
st.markdown("<div style='height:12px'></div>", unsafe_allow_html=True)
tab_expenses, tab_dept, tab_trends, tab_top = st.tabs([
    "📊  Витрати",
    "🏢  По відділах",
    "📈  Динаміка",
    "🔥  ТОП",
])

# ─────── TAB 0: АНАЛІЗ ВИТРАТ (KPI + матриця) ────────────
with tab_expenses:
    # ── KPI картки (responsive flex) ─────────────────────────
    val_color3 = "#e63946" if planned_diff < 0 else "#111"
    st.markdown(f"""
    <style>
    .kpi-row {{ display:flex; flex-wrap:wrap; gap:10px; margin-bottom:14px; }}
    .kpi-card {{
        flex:1 1 160px; background:#f8fafd; border:1px solid #dde6f0;
        border-radius:10px; padding:14px 16px; text-align:center;
        box-shadow:0 1px 4px rgba(10,35,70,0.06);
    }}
    .kpi-card .lbl {{ font-size:11px; color:#888; line-height:1.4; margin-bottom:6px; }}
    .kpi-card .val {{ font-size:22px; font-weight:900; line-height:1.2; }}
    @media(max-width:480px) {{
        .kpi-card {{ flex:1 1 100%; }}
        .kpi-card .val {{ font-size:20px; }}
    }}
    </style>
    <div class="kpi-row">
      <div class="kpi-card">
        <div class="lbl">Операційних витрат усього $</div>
        <div class="val" style="color:#111">{fmt_tis(total_sum)}</div>
      </div>
      <div class="kpi-card">
        <div class="lbl">Непланові витрати $</div>
        <div class="val" style="color:#111">{fmt_tis(unplanned_sum)}</div>
      </div>
      <div class="kpi-card">
        <div class="lbl">Операційні витрати $</div>
        <div class="val" style="color:{val_color3}">{planned_diff:,.2f}</div>
      </div>
    </div>
    """, unsafe_allow_html=True)

    # ── Матриця витрат на повну ширину ────────────────────────
    if "Parent_Description" not in filtered_df.columns:
        st.warning("Відсутня колонка 'Parent_Description'.")
    else:
        dist_types = []
        if "DistributionBase" in filtered_df.columns:
            dist_types = sorted(
                filtered_df["DistributionBase"].dropna().unique().tolist()
            )

        parent_grp = (
            filtered_df.groupby("Parent_Description")["Sum"]
            .sum().sort_values(ascending=False).reset_index()
        )

        if dist_types:
            pivot_child = (
                filtered_df
                .groupby(["Parent_Description", "Type_of_expense", "DistributionBase"])["Sum"]
                .sum().reset_index()
                .pivot_table(
                    index=["Parent_Description", "Type_of_expense"],
                    columns="DistributionBase", values="Sum",
                    aggfunc="sum", fill_value=0,
                ).reset_index()
            )
            pivot_child.columns.name = None
            for dt in dist_types:
                if dt not in pivot_child.columns:
                    pivot_child[dt] = 0
            pivot_child["Всього"] = pivot_child[dist_types].sum(axis=1)
        else:
            pivot_child = (
                filtered_df.groupby(["Parent_Description", "Type_of_expense"])["Sum"]
                .sum().reset_index()
            )
            pivot_child["Всього"] = pivot_child["Sum"]

        extra_ths = "".join(
            f'<th class="dist-col" style="text-align:right;min-width:110px;white-space:nowrap">{dt}</th>'
            for dt in dist_types
        )

        rows_html = ""
        for idx, p_row in enumerate(parent_grp.itertuples(), start=1):
            pname  = p_row.Parent_Description
            psum   = p_row.Sum
            grp_id = f"grp{idx}"
            empty_tds = "".join('<td class="dist-col"></td>' for _ in dist_types)
            rows_html += (
                f'<tr class="parent-row" onclick="toggleGroup(\'{grp_id}\')" style="cursor:pointer;">'
                f'<td><span class="toggle" id="btn_{grp_id}">&#8853;</span> {pname}</td>'
                f'{empty_tds}'
                f'<td>{psum:,.2f}</td></tr>'
            )
            children = pivot_child[pivot_child["Parent_Description"] == pname]
            for _, c_row in children.sort_values("Всього", ascending=False).iterrows():
                child_dist_tds = "".join(
                    f'<td class="dist-col">{c_row[dt]:,.2f}</td>' if c_row[dt] != 0
                    else '<td class="dist-col" style="color:#ccc">—</td>'
                    for dt in dist_types
                )
                rows_html += (
                    f'<tr class="child-row" data-group="{grp_id}" style="display:none;">'
                    f'<td style="padding-left:26px;">{c_row["Type_of_expense"]}</td>'
                    f'{child_dist_tds}'
                    f'<td>{c_row["Всього"]:,.2f}</td></tr>'
                )

        if dist_types:
            tot_by_dist = filtered_df.groupby("DistributionBase")["Sum"].sum()
            total_dist_tds = "".join(
                f'<td class="dist-col">{tot_by_dist.get(dt, 0):,.2f}</td>' for dt in dist_types
            )
        else:
            total_dist_tds = ""
        rows_html += (
            f'<tr class="total-row"><td>Усього</td>'
            f'{total_dist_tds}'
            f'<td>{total_sum:,.2f}</td></tr>'
        )

        table_html = f"""
        <style>
        * {{ box-sizing:border-box; }}
        body {{ margin:0; padding:0; font-family:'Segoe UI',sans-serif; font-size:13px;
               background:transparent; }}
        .wrap {{ border-radius:10px; overflow:hidden; border:1px solid #dde6f0;
                 box-shadow:0 2px 10px rgba(10,35,70,0.08); }}
        table {{ width:100%; border-collapse:collapse; }}
        thead tr {{ background:linear-gradient(90deg,#0a2342,#1a5276); }}
        th {{ color:white; padding:10px 14px; text-align:left; font-weight:600;
              font-size:12px; letter-spacing:0.3px; white-space:nowrap; }}
        th:not(:first-child) {{ text-align:right; }}
        td {{ padding:6px 14px; border-bottom:1px solid #eef2f7;
              font-variant-numeric:tabular-nums; font-size:13px; }}
        td:not(:first-child) {{ text-align:right; }}
        tr.parent-row {{ background:#e8f0fb; font-weight:700; cursor:pointer;
                         transition:background .15s; }}
        tr.parent-row:hover {{ background:#cfe0f5; }}
        tr.child-row  {{ background:#ffffff; color:#444; transition:background .15s; }}
        tr.child-row:hover {{ background:#f4f8fd; }}
        tr.total-row  {{ background:#1a5276; color:white; font-weight:700; font-size:13px; }}
        tr.total-row td {{ border-bottom:none; color:white; }}
        .toggle {{ display:inline-block; width:16px; font-weight:900; font-size:14px;
                   color:#1a5276; user-select:none; transition:transform .15s; }}
        .scroll-wrap {{ overflow-x:auto; }}
        @media (max-width: 768px) {{ .dist-col {{ display:none !important; }} }}
        </style>
        <div class="wrap"><div class="scroll-wrap">
        <table>
          <thead><tr>
            <th style="min-width:220px">Категорія / Стаття</th>
            {extra_ths}
            <th style="min-width:110px">Всього</th>
          </tr></thead>
          <tbody id="tbody">{rows_html}</tbody>
        </table>
        </div></div>
        <script>
        function toggleGroup(grpId) {{
          var rows = document.querySelectorAll('[data-group="' + grpId + '"]');
          var btn  = document.getElementById('btn_' + grpId);
          var anyVisible = Array.from(rows).some(function(r) {{
            return r.style.display !== 'none';
          }});
          rows.forEach(function(r) {{
            r.style.display = anyVisible ? 'none' : 'table-row';
          }});
          if (btn) btn.innerHTML = anyVisible ? '&#8853;' : '&#8854;';
          resize();
        }}
        function resize() {{
          var h = document.body.scrollHeight;
          if (window.frameElement) window.frameElement.style.height = h + 'px';
        }}
        document.addEventListener('DOMContentLoaded', resize);
        </script>
        """
        # Only parent rows + total row are visible initially (children are collapsed)
        visible_rows = len(parent_grp) + 2
        tbl_height = visible_rows * 34 + 60
        components.html(table_html, height=tbl_height, scrolling=False)

# ─────── TAB 1: ПО ВІДДІЛАХ ──────────────────────────────
with tab_dept:
    dept_sum = (
        filtered_df.groupby("Department")["Sum"]
        .sum().sort_values(ascending=False).reset_index()
    )
    dept_total = dept_sum["Sum"].sum()
    dept_sum["Pct"] = dept_sum["Sum"] / dept_total * 100
    dept_sum["Rank"] = range(1, len(dept_sum) + 1)

    # Топ-3 картки
    top3 = dept_sum.head(3)
    bg_colors = ["#0a2342", "#1a5276", "#5d8aa8"]
    d_cols = st.columns(len(top3))
    for i, (col, row) in enumerate(zip(d_cols, top3.itertuples())):
        col.markdown(f"""
        <div style="background:{bg_colors[i]};border-radius:10px;padding:14px 16px;
             color:white;text-align:center;margin-bottom:8px;">
          <div style="font-size:11px;opacity:.75;margin-bottom:4px;">🏆 Місце #{row.Rank}</div>
          <div style="font-size:13px;font-weight:700;margin-bottom:6px;">{row.Department}</div>
          <div style="font-size:22px;font-weight:900;">{row.Sum/1000:,.1f} тис.</div>
          <div style="font-size:12px;opacity:.7;margin-top:4px;">{row.Pct:.1f}% від загального</div>
        </div>""", unsafe_allow_html=True)

    st.markdown("<br>", unsafe_allow_html=True)
    col_bar, col_pie2 = st.columns([1.4, 1])
    with col_bar:
        fig_dbar = go.Figure(go.Bar(
            x=dept_sum["Sum"], y=dept_sum["Department"],
            orientation="h",
            marker=dict(
                color=dept_sum["Sum"],
                colorscale=[[0, "#aac4de"], [0.5, "#2471a3"], [1, "#0a2342"]],
                showscale=False,
            ),
            text=[f"{v/1000:,.1f} тис. ({p:.1f}%)"
                  for v, p in zip(dept_sum["Sum"], dept_sum["Pct"])],
            textposition="outside",
            hovertemplate="<b>%{y}</b><br>%{x:,.0f}<extra></extra>",
        ))
        fig_dbar.update_layout(
            height=max(280, len(dept_sum) * 42 + 60),
            margin=dict(l=0, r=120, t=10, b=10),
            xaxis=dict(tickformat=",.0f", gridcolor="#eef2f7", title=""),
            yaxis=dict(autorange="reversed", title=""),
            plot_bgcolor="white", paper_bgcolor="white",
        )
        st.plotly_chart(fig_dbar, width='stretch')

    with col_pie2:
        fig_dp = px.pie(
            dept_sum, names="Department", values="Sum", hole=0.5,
            color_discrete_sequence=px.colors.sequential.Blues_r,
        )
        fig_dp.update_traces(
            textposition="outside", textinfo="percent+label",
            hovertemplate="<b>%{label}</b><br>%{value:,.0f}<extra></extra>",
        )
        fig_dp.update_layout(
            height=360, margin=dict(l=0, r=0, t=20, b=20),
            showlegend=False, paper_bgcolor="white",
            annotations=[dict(
                text=f"{dept_total/1000:,.0f}<br>тис.",
                x=0.5, y=0.5, showarrow=False,
                font=dict(size=14, color="#1a5276", family="Segoe UI"),
            )],
        )
        st.plotly_chart(fig_dp, width='stretch')

    st.markdown("#### 📋 Деталізація по відділах")
    dept_detail = (
        filtered_df.groupby(["Department", "Parent_Description"])["Sum"]
        .sum().reset_index()
        .sort_values(["Department", "Sum"], ascending=[True, False])
    )
    dept_detail["Частка"] = (
        dept_detail["Sum"] /
        dept_detail.groupby("Department")["Sum"].transform("sum") * 100
    ).round(1).apply(lambda x: f"{x:.1f}%")
    dept_detail["Сума, $"] = dept_detail["Sum"].apply(lambda x: f"{x:,.2f}")
    st.dataframe(
        dept_detail.rename(columns={
            "Department": "🏢 Відділ",
            "Parent_Description": "📌 Категорія",
        })[["🏢 Відділ", "📌 Категорія", "Сума, $", "Частка"]],
        width='stretch', hide_index=True, height=350,
    )

# ─────── TAB 2: ДИНАМІКА ─────────────────────────────────
with tab_trends:
    YEAR_COLORS = {
        "2022": "#1f77b4", "2023": "#ff7f0e", "2024": "#d62728",
        "2025": "#9467bd", "2026": "#17becf",
    }
    ym = (
        df_raw[df_raw["Department"].isin(selected_depts) &
               df_raw["Type_of_expense"].isin(selected_expenses)]
        .groupby(["Month_Num", "Month_Name", "Year"])["Sum"]
        .sum().reset_index()
    )
    month_order_t = [UA_MONTHS[i] for i in range(1, 13)]
    ym["Month_Name"] = pd.Categorical(
        ym["Month_Name"], categories=month_order_t, ordered=True)
    ym["Year"] = ym["Year"].astype(str)
    ym = ym.sort_values(["Year", "Month_Num"])
    fig_line = go.Figure()
    for yr in sorted(ym["Year"].unique()):
        yr_data = ym[ym["Year"] == yr].sort_values("Month_Num")
        color = YEAR_COLORS.get(yr, "#333333")
        fig_line.add_trace(go.Scatter(
            x=yr_data["Month_Name"], y=yr_data["Sum"],
            name=yr, mode="lines+markers",
            line=dict(color=color, width=2.5),
            marker=dict(size=8, color=color),
            fill="tozeroy",
            fillcolor=hex_to_rgba(color, 0.08),
            hovertemplate=f"<b>{yr}</b> %{{x}}: %{{y:,.0f}}<extra></extra>",
        ))
    fig_line.update_layout(
        height=380, margin=dict(l=0, r=0, t=10, b=0),
        legend=dict(orientation="h", yanchor="bottom", y=1.01,
                    xanchor="left", x=0, title_text="Рік:", font_size=12),
        yaxis=dict(tickformat=",.0f", gridcolor="#eef2f7", title=""),
        xaxis=dict(title="", gridcolor="#eef2f7"),
        plot_bgcolor="white", paper_bgcolor="white", hovermode="x unified",
    )
    st.plotly_chart(fig_line, width='stretch')

    # Теплова карта
    st.markdown("#### 🌡️ Теплова карта витрат по місяцях та роках")
    heat_df = (
        df_raw[df_raw["Department"].isin(selected_depts) &
               df_raw["Type_of_expense"].isin(selected_expenses)]
        .groupby(["Year", "Month_Num"])["Sum"].sum().reset_index()
    )
    heat_pivot = (
        heat_df.pivot(index="Year", columns="Month_Num", values="Sum")
        .reindex(columns=range(1, 13)).rename(columns=UA_MONTHS)
    )
    fig_heat = px.imshow(
        heat_pivot, color_continuous_scale="Blues",
        aspect="auto", text_auto=",.0f",
        labels=dict(x="Місяць", y="Рік", color="Витрати"),
    )
    fig_heat.update_layout(
        height=220, margin=dict(t=10, b=10, l=0, r=0),
        xaxis_title="", yaxis_title="", coloraxis_showscale=False,
    )
    fig_heat.update_traces(textfont_size=10)
    st.plotly_chart(fig_heat, width='stretch')

# ─────── TAB 3: ТОП ──────────────────────────────────────
with tab_top:
    top_n = st.slider("Кількість позицій", 5, 30, 15, key="top_slider")
    top_df = (
        filtered_df.groupby("Type_of_expense")["Sum"]
        .sum().nlargest(top_n).sort_values(ascending=True).reset_index()
    )
    fig_top = go.Figure(go.Bar(
        x=top_df["Sum"], y=top_df["Type_of_expense"],
        orientation="h",
        marker=dict(
            color=top_df["Sum"],
            colorscale=[[0, "#aac4de"], [1, "#c0392b"]],
            showscale=False,
        ),
        text=[f"{v/1000:,.1f} тис." for v in top_df["Sum"]],
        textposition="outside",
        hovertemplate="<b>%{y}</b><br>%{x:,.0f}<extra></extra>",
    ))
    fig_top.update_layout(
        height=max(400, top_n * 32 + 80),
        margin=dict(l=0, r=80, t=10, b=10),
        xaxis=dict(tickformat=",.0f", gridcolor="#eef2f7", title=""),
        yaxis=dict(title=""),
        plot_bgcolor="white", paper_bgcolor="white",
    )
    st.plotly_chart(fig_top, width='stretch')

# ── Футер ─────────────────────────────────────────────────
st.markdown(
    f"<p style='text-align:right;font-size:11px;color:#aaa;margin-top:10px;'>"
    unsafe_allow_html=True,
)

