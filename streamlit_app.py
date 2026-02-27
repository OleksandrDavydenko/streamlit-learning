# -*- coding: utf-8 -*-
import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from db_connection import get_expenses_data

# ============================================================
# КОНФІГУРАЦІЯ
# ============================================================
st.set_page_config(
    page_title="Звіт витрат",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded",
)

UA_MONTHS = {
    1: "Січень", 2: "Лютий",  3: "Березень", 4: "Квітень",
    5: "Травень", 6: "Червень", 7: "Липень",  8: "Серпень",
    9: "Вересень", 10: "Жовтень", 11: "Листопад", 12: "Грудень",
}

# ============================================================
# АВТОРИЗАЦІЯ
# ============================================================
def check_password() -> bool:
    if st.session_state.get("password_correct"):
        return True

    col1, col2, col3 = st.columns([1, 1, 1])
    with col2:
        st.markdown(
            "<h1 style='text-align:center'>🔐 Доступ захищений</h1>"
            "<p style='text-align:center;color:gray'>Введіть пароль для входу</p>",
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
# ЗАВАНТАЖЕННЯ ДАНИХ (з кешем на 30 хв)
# ============================================================
@st.cache_data(ttl=1800, show_spinner="⏳ Завантаження даних...")
def load_data() -> pd.DataFrame:
    df = get_expenses_data()
    if df.empty:
        return df
    df["Period"] = pd.to_datetime(df["Period"], errors="coerce")
    df["Year"]   = df["Period"].dt.year
    df["Month"]  = df["Period"].dt.month
    df["MonthName"] = df["Month"].map(UA_MONTHS)
    df["Sum"]    = pd.to_numeric(df["Sum"], errors="coerce").fillna(0)
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
# SIDEBAR — ФІЛЬТРИ
# ============================================================
with st.sidebar:
    st.markdown("## 🎛️ Фільтри")
    st.divider()

    # Рік
    all_years = sorted(df_raw["Year"].dropna().unique(), reverse=True)
    sel_years = st.multiselect(
        "📅 Рік",
        options=all_years,
        default=all_years[:1],
    )

    # Місяць
    all_months = list(range(1, 13))
    sel_months = st.multiselect(
        "🗓️ Місяць",
        options=all_months,
        default=all_months,
        format_func=lambda m: UA_MONTHS[m],
    )

    st.divider()

    # Відділ
    all_depts = sorted(df_raw["Department"].dropna().unique())
    sel_depts = st.multiselect(
        "🏢 Відділ",
        options=all_depts,
        default=all_depts,
    )

    # База розподілу
    all_dist = sorted(df_raw["DistributionBase"].dropna().unique())
    sel_dist = st.multiselect(
        "📌 База розподілу",
        options=all_dist,
        default=all_dist,
    )

    st.divider()
    if st.button("🔄 Оновити дані", use_container_width=True):
        st.cache_data.clear()
        st.rerun()

# ============================================================
# ФІЛЬТРАЦІЯ
# ============================================================
df = df_raw.copy()
if sel_years:
    df = df[df["Year"].isin(sel_years)]
if sel_months:
    df = df[df["Month"].isin(sel_months)]
if sel_depts:
    df = df[df["Department"].isin(sel_depts)]
if sel_dist:
    df = df[df["DistributionBase"].isin(sel_dist)]

# ============================================================
# ЗАГОЛОВОК
# ============================================================
st.title("📊 Звіт операційних витрат")
st.caption(f"Показано {len(df):,} записів із {len(df_raw):,} всього")
st.divider()

if df.empty:
    st.info("Немає даних за обраними фільтрами.")
    st.stop()

# ============================================================
# KPI-КАРТКИ
# ============================================================
total      = df["Sum"].sum()
avg_month  = df.groupby(["Year", "Month"])["Sum"].sum().mean()
top_dept   = df.groupby("Department")["Sum"].sum().idxmax()
direct_pct = df[df["DistributionBase"] == "Прямий"]["Sum"].sum() / total * 100 if total else 0

k1, k2, k3, k4 = st.columns(4)
k1.metric("💰 Загальні витрати",   f"{total:,.0f}")
k2.metric("📆 Середньомісячні",    f"{avg_month:,.0f}")
k3.metric("🏆 Топ відділ",         top_dept)
k4.metric("🎯 Прямі витрати",      f"{direct_pct:.1f}%")

st.divider()

# ============================================================
# ROW 1: Динаміка по місяцях | Розподіл по типу
# ============================================================
col_left, col_right = st.columns([3, 2])

with col_left:
    st.subheader("📈 Динаміка витрат по місяцях")
    ts = (
        df.groupby(["Year", "Month", "MonthName"])["Sum"]
          .sum().reset_index()
          .sort_values(["Year", "Month"])
    )
    ts["Період"] = ts.apply(
        lambda r: f"{UA_MONTHS[int(r['Month'])]} {int(r['Year'])}", axis=1
    )
    fig_line = px.area(
        ts, x="Період", y="Sum", color="Year",
        labels={"Sum": "Витрати", "Період": ""},
        color_discrete_sequence=px.colors.qualitative.Bold,
    )
    fig_line.update_layout(
        margin=dict(t=10, b=10),
        legend_title="Рік",
        hovermode="x unified",
        yaxis_tickformat=",.0f",
    )
    st.plotly_chart(fig_line, use_container_width=True)

with col_right:
    st.subheader("🥧 База розподілу")
    dist_df = df.groupby("DistributionBase")["Sum"].sum().reset_index()
    fig_pie = px.pie(
        dist_df, values="Sum", names="DistributionBase",
        hole=0.45,
        color_discrete_sequence=px.colors.qualitative.Safe,
    )
    fig_pie.update_traces(textposition="outside", textinfo="percent+label")
    fig_pie.update_layout(
        margin=dict(t=10, b=10),
        showlegend=False,
    )
    st.plotly_chart(fig_pie, use_container_width=True)

# ============================================================
# ROW 2: По відділах | По категоріях витрат
# ============================================================
col_l2, col_r2 = st.columns(2)

with col_l2:
    st.subheader("🏢 Витрати по відділах")
    dept_df = (
        df.groupby("Department")["Sum"].sum()
          .reset_index().sort_values("Sum", ascending=True)
    )
    fig_bar = px.bar(
        dept_df, x="Sum", y="Department", orientation="h",
        labels={"Sum": "Витрати", "Department": ""},
        color="Sum",
        color_continuous_scale="Blues",
    )
    fig_bar.update_layout(
        margin=dict(t=10, b=10),
        coloraxis_showscale=False,
        xaxis_tickformat=",.0f",
    )
    st.plotly_chart(fig_bar, use_container_width=True)

with col_r2:
    st.subheader("📂 Категорії витрат (Parent)")
    cat_df = (
        df.groupby("Parent_Description")["Sum"].sum()
          .reset_index().sort_values("Sum", ascending=False).head(10)
    )
    fig_cat = px.bar(
        cat_df, x="Parent_Description", y="Sum",
        labels={"Sum": "Витрати", "Parent_Description": ""},
        color="Sum",
        color_continuous_scale="Teal",
    )
    fig_cat.update_layout(
        margin=dict(t=10, b=10),
        coloraxis_showscale=False,
        xaxis_tickangle=-35,
        yaxis_tickformat=",.0f",
    )
    st.plotly_chart(fig_cat, use_container_width=True)

# ============================================================
# ROW 3: Treemap
# ============================================================
st.subheader("🗺️ Структура витрат")
tree_df = (
    df.groupby(["Department", "Parent_Description", "DistributionBase"])["Sum"]
      .sum().reset_index()
)
fig_tree = px.treemap(
    tree_df,
    path=["Department", "Parent_Description", "DistributionBase"],
    values="Sum",
    color="Sum",
    color_continuous_scale="RdYlGn_r",
    hover_data={"Sum": ":,.0f"},
)
fig_tree.update_layout(margin=dict(t=10, b=10))
st.plotly_chart(fig_tree, use_container_width=True)

# ============================================================
# ДЕТАЛІЗАЦІЯ
# ============================================================
st.divider()
st.subheader("📋 Деталізація")

show_df = (
    df[["Period", "Department", "Parent_Description", "Type_of_expense",
        "DistributionBase", "Sum"]]
    .rename(columns={
        "Period":           "Дата",
        "Department":       "Відділ",
        "Parent_Description": "Категорія",
        "Type_of_expense":  "Тип витрат",
        "DistributionBase": "База розподілу",
        "Sum":              "Сума",
    })
    .sort_values("Дата", ascending=False)
)

st.dataframe(
    show_df.style.format({"Сума": "{:,.2f}", "Дата": lambda x: x.strftime("%d.%m.%Y") if pd.notna(x) else ""}),
    use_container_width=True,
    height=400,
)

# Кнопка експорту
csv = show_df.to_csv(index=False).encode("utf-8-sig")
st.download_button(
    label="⬇️ Завантажити CSV",
    data=csv,
    file_name="expenses_report.csv",
    mime="text/csv",
)

