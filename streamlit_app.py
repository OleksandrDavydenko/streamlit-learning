# -*- coding: utf-8 -*-
import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from db_connection import get_expenses_data
from datetime import datetime
import io

# ============================================================
# КОНФІГУРАЦІЯ
# ============================================================
st.set_page_config(
    page_title="Фінансова аналітика",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded",
)

UA_MONTHS = {
    1: "Січень", 2: "Лютий", 3: "Березень", 4: "Квітень",
    5: "Травень", 6: "Червень", 7: "Липень", 8: "Серпень",
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
# SIDEBAR — ФІЛЬТРИ
# ============================================================
with st.sidebar:
    st.markdown("## 🎛️ Фільтри")
    st.divider()

    # --- Рік: selectbox ---
    all_years = sorted(df_raw["Year"].dropna().unique().astype(int), reverse=True)
    selected_year = st.selectbox("📅 Рік", options=all_years, index=0, key="year_filter")

    # --- Місяці: кнопки "Всі / Очистити" + multiselect ---
    months_in_year = sorted(df_raw[df_raw["Year"] == selected_year]["Month_Num"].unique())
    month_options = [UA_MONTHS[m] for m in months_in_year]

    st.markdown("**🗓️ Місяці**")
    btn_col1, btn_col2 = st.columns(2)
    if btn_col1.button("✅ Всі", use_container_width=True, key="months_all"):
        st.session_state["months_sel"] = month_options
    if btn_col2.button("🗑️ Очистити", use_container_width=True, key="months_clear"):
        st.session_state["months_sel"] = []

    if "months_sel" not in st.session_state:
        st.session_state["months_sel"] = month_options

    # синхронізуємо якщо рік змінився
    valid = [m for m in st.session_state["months_sel"] if m in month_options]
    if not valid:
        valid = month_options
    st.session_state["months_sel"] = valid

    sel_month_names = st.multiselect(
        "", options=month_options,
        default=st.session_state["months_sel"],
        key="months_multiselect",
        label_visibility="collapsed",
    )
    st.session_state["months_sel"] = sel_month_names
    selected_months = [k for k, v in UA_MONTHS.items() if v in sel_month_names]

    st.divider()

    # --- Відділ ---
    all_depts = ["📊 Усі"] + sorted([f"🏢 {d}" for d in df_raw["Department"].dropna().unique()])
    sel_dept_display = st.selectbox("🏢 Відділ", all_depts, key="dept_filter")
    selected_department = sel_dept_display.replace("🏢 ", "").replace("📊 Усі", "Усі")

    # --- Тип витрат ---
    all_types = ["💼 Усі"] + sorted([f"💵 {t}" for t in df_raw["Type_of_expense"].dropna().unique()])
    sel_type_display = st.selectbox("💼 Тип витрат", all_types, key="type_filter")
    selected_type = sel_type_display.replace("💵 ", "").replace("💼 Усі", "Усі")

    # --- База розподілу ---
    all_dist = ["📌 Усі"] + sorted([f"🔄 {d}" for d in df_raw["DistributionBase"].dropna().unique()])
    sel_dist_display = st.selectbox("📌 Розподіл", all_dist, key="dist_filter")
    selected_dist = sel_dist_display.replace("🔄 ", "").replace("📌 Усі", "Усі")

    st.divider()
    if st.button("🔄 Оновити дані", use_container_width=True):
        st.cache_data.clear()
        st.rerun()

# ============================================================
# ФІЛЬТРАЦІЯ
# ============================================================
filtered_df = df_raw[
    (df_raw["Year"] == selected_year) &
    (df_raw["Month_Num"].isin(selected_months))
].copy()

if selected_department != "Усі":
    filtered_df = filtered_df[filtered_df["Department"] == selected_department]
if selected_type != "Усі":
    filtered_df = filtered_df[filtered_df["Type_of_expense"] == selected_type]
if selected_dist != "Усі":
    filtered_df = filtered_df[filtered_df["DistributionBase"] == selected_dist]

# ============================================================
# ЗАГОЛОВОК
# ============================================================
st.title("📊 Фінансова аналітика — Звіт по витратах")
st.caption(f"Показано {len(filtered_df):,} записів із {len(df_raw):,} | Рік: {selected_year}")
st.divider()

if filtered_df.empty:
    st.info("Немає даних за обраними фільтрами.")
    st.stop()

# ============================================================
# KPI-КАРТКИ
# ============================================================
total_sum     = filtered_df["Sum"].sum()
avg_sum       = filtered_df["Sum"].mean()
max_sum       = filtered_df["Sum"].max()
records_count = len(filtered_df)

def fmt(v):
    if v >= 1_000_000:
        return f"{v/1_000_000:.2f}M"
    if v >= 1_000:
        return f"{v/1_000:.0f}K"
    return f"{v:,.0f}"

k1, k2, k3, k4 = st.columns(4)
k1.metric("💰 Разом",    fmt(total_sum))
k2.metric("📈 Середня",  fmt(avg_sum))
k3.metric("🔥 Максимум", fmt(max_sum))
k4.metric("📋 Записів",  f"{records_count:,}")

st.divider()

# ============================================================
# ТАБИ
# ============================================================
tab1, tab2, tab3, tab4, tab5, tab6, tab7, tab8 = st.tabs([
    "🎯 Тренди по рокам",
    "📊 Детальна таблиця",
    "🌳 Структура витрат",
    "🔥 Топ витрати",
    "🏢 По відділам",
    "📥 Експорт",
    "🌊 Потік витрат",
    "🔍 Аналітика",
])

# ── TAB 1: Тренди ──────────────────────────────────────────
with tab1:
    st.subheader("Динаміка витрат по місяцях та рокам")
    yearly_monthly = (
        df_raw.groupby(["Month_Num", "Month_Name", "Year"])["Sum"]
              .sum().reset_index()
              .sort_values("Month_Num")
    )
    # Впорядкуємо місяці правильно (категорійна вісь)
    month_order = [UA_MONTHS[i] for i in range(1, 13)]
    yearly_monthly["Month_Name"] = pd.Categorical(
        yearly_monthly["Month_Name"], categories=month_order, ordered=True
    )
    yearly_monthly = yearly_monthly.sort_values(["Year", "Month_Num"])

    fig = px.line(
        yearly_monthly, x="Month_Name", y="Sum", color="Year",
        markers=True,
        title="Порівняння років по місяцях",
        labels={"Sum": "Сума", "Month_Name": "Місяць", "Year": "Рік"},
        line_shape="spline",
        color_discrete_sequence=px.colors.qualitative.Bold,
    )
    fig.update_traces(marker=dict(size=8))
    fig.update_layout(hovermode="x unified", height=500, yaxis_tickformat=",.0f")
    st.plotly_chart(fig, use_container_width=True)

    # Теплова карта рік × місяць
    st.subheader("🌡️ Теплова карта: рік × місяць")
    heat_df = df_raw.groupby(["Year", "Month_Num"])["Sum"].sum().reset_index()
    heat_pivot = (
        heat_df.pivot(index="Year", columns="Month_Num", values="Sum")
               .reindex(columns=range(1, 13))
               .rename(columns=UA_MONTHS)
    )
    fig_heat = px.imshow(
        heat_pivot,
        color_continuous_scale="RdYlGn_r",
        aspect="auto",
        text_auto=",.0f",
        labels=dict(x="Місяць", y="Рік", color="Витрати"),
    )
    fig_heat.update_layout(margin=dict(t=10, b=10), xaxis_title="", yaxis_title="")
    fig_heat.update_traces(textfont_size=10)
    st.plotly_chart(fig_heat, use_container_width=True)

# ── TAB 2: Детальна таблиця ────────────────────────────────
with tab2:
    st.subheader("📊 Детальна таблиця витрат")
    if not filtered_df.empty:
        table_data = (
            filtered_df
            .groupby(["Parent_Description", "Type_of_expense", "DistributionBase"])
            .agg(Sum=("Sum", "sum"))
            .reset_index()
            .sort_values(["Parent_Description", "Type_of_expense", "Sum"],
                         ascending=[True, True, False])
        )
        table_data["Сума (USD)"] = table_data["Sum"].apply(lambda x: f"{x:,.2f}")
        table_data = table_data.drop("Sum", axis=1)
        st.dataframe(
            table_data.rename(columns={
                "Parent_Description": "📌 Опис",
                "Type_of_expense":    "💼 Тип витрат",
                "DistributionBase":   "🔄 Розподіл",
            }),
            use_container_width=True, hide_index=True, height=600,
        )

# ── TAB 3: Структура ──────────────────────────────────────
with tab3:
    st.subheader("Структура витрат — Дерево")
    if not filtered_df.empty:
        tree_data = (
            filtered_df.groupby(["Department", "Parent_Description", "Type_of_expense"])["Sum"]
                        .sum().reset_index()
        )
        fig = px.treemap(
            tree_data,
            path=["Department", "Parent_Description", "Type_of_expense"],
            values="Sum",
            color="Sum",
            color_continuous_scale="Viridis",
            title="Витрати: Відділ → Категорія → Тип",
        )
        fig.update_layout(height=600)
        st.plotly_chart(fig, use_container_width=True)

# ── TAB 4: Топ витрати ────────────────────────────────────
with tab4:
    st.subheader("🔥 Топ-15 найбільших витрат")
    if not filtered_df.empty:
        top_df = (
            filtered_df.groupby(["Type_of_expense", "Department"])["Sum"]
                        .sum().reset_index()
                        .nlargest(15, "Sum")
                        .sort_values("Sum")
        )
        fig = px.bar(
            top_df, y="Type_of_expense", x="Sum", orientation="h",
            color="Sum", color_continuous_scale="Reds",
            text=top_df["Sum"].apply(fmt),
            hover_data={"Department": True},
            labels={"Sum": "Сума", "Type_of_expense": "Тип витрат"},
        )
        fig.update_traces(textposition="outside")
        fig.update_layout(height=550, showlegend=False,
                          xaxis_tickformat=",.0f", coloraxis_showscale=False)
        st.plotly_chart(fig, use_container_width=True)

# ── TAB 5: По відділах ────────────────────────────────────
with tab5:
    st.subheader("Розподіл по відділах")
    dept_sum = (
        filtered_df.groupby("Department")["Sum"]
                   .sum().sort_values(ascending=False).reset_index()
    )
    col_pie, col_bar = st.columns(2)
    with col_pie:
        fig = px.pie(dept_sum, names="Department", values="Sum",
                     title="Частка кожного відділу", hole=0.4)
        fig.update_traces(textposition="outside", textinfo="percent+label")
        fig.update_layout(height=450, showlegend=False)
        st.plotly_chart(fig, use_container_width=True)
    with col_bar:
        fig = px.bar(
            dept_sum, x="Department", y="Sum",
            color="Sum", color_continuous_scale="Blues",
            title="Витрати по відділах",
            labels={"Sum": "Сума", "Department": ""},
        )
        fig.update_xaxes(tickangle=45)
        fig.update_layout(height=450, showlegend=False,
                          coloraxis_showscale=False, yaxis_tickformat=",.0f")
        st.plotly_chart(fig, use_container_width=True)

# ── TAB 6: Експорт ────────────────────────────────────────
with tab6:
    st.subheader("📥 Експорт даних")
    export_df = filtered_df[
        ["Period", "Department", "Type_of_expense",
         "Parent_Description", "Sum", "DistributionBase"]
    ].copy()
    export_df["Period"] = export_df["Period"].dt.strftime("%Y-%m-%d")

    csv_bytes = export_df.to_csv(index=False).encode("utf-8-sig")
    st.download_button(
        "⬇️ Завантажити CSV", data=csv_bytes,
        file_name=f"expenses_{datetime.now().strftime('%Y%m%d')}.csv",
        mime="text/csv", use_container_width=True,
    )

    try:
        buf = io.BytesIO()
        export_df.to_excel(buf, index=False, engine="openpyxl")
        st.download_button(
            "⬇️ Завантажити Excel", data=buf.getvalue(),
            file_name=f"expenses_{datetime.now().strftime('%Y%m%d')}.xlsx",
            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
            use_container_width=True,
        )
    except ImportError:
        st.info("💡 Для Excel: pip install openpyxl")

# ── TAB 7: Потік витрат ───────────────────────────────────
with tab7:
    st.subheader("🌊 Матриця витрат та Парето")
    if not filtered_df.empty:
        col1, col2 = st.columns([1.2, 1])

        with col1:
            st.write("**🔥 Теплова карта: Відділ × Тип витрат**")
            heatmap_data = filtered_df.pivot_table(
                index="Department", columns="Type_of_expense",
                values="Sum", aggfunc="sum", fill_value=0,
            )
            fig_hm = go.Figure(go.Heatmap(
                z=heatmap_data.values,
                x=heatmap_data.columns,
                y=heatmap_data.index,
                colorscale="RdYlGn_r",
                hovertemplate="<b>%{y}</b><br>%{x}<br>Сума: %{z:,.0f}<extra></extra>",
            ))
            fig_hm.update_layout(height=500, xaxis_tickangle=45,
                                  margin=dict(b=150, l=150))
            st.plotly_chart(fig_hm, use_container_width=True)

        with col2:
            st.write("**📊 Парето — ТОП-15 типів витрат**")
            sorted_types = (
                filtered_df.groupby("Type_of_expense")["Sum"]
                            .sum().sort_values(ascending=True).tail(15)
            )
            fig_p = go.Figure(go.Bar(
                y=sorted_types.index, x=sorted_types.values, orientation="h",
                marker=dict(color=sorted_types.values,
                            colorscale="Reds", showscale=False),
                text=[fmt(v) for v in sorted_types.values],
                textposition="auto",
                hovertemplate="<b>%{y}</b><br>Сума: %{x:,.0f}<extra></extra>",
            ))
            fig_p.update_layout(height=500, margin=dict(l=150), showlegend=False,
                                 xaxis_tickformat=",.0f")
            st.plotly_chart(fig_p, use_container_width=True)

        st.divider()
        st.write("**💧 Водопад витрат — ТОП-10 типів**")
        top10 = (
            filtered_df.groupby("Type_of_expense")["Sum"]
                        .sum().nlargest(10).sort_values()
        )
        fig_wf = go.Figure(go.Waterfall(
            x=top10.index, y=top10.values,
            connector={"line": {"color": "rgba(63,63,63,0.5)"}},
            increasing={"marker": {"color": "#d62728"}},
            totals={"marker": {"color": "#1f77b4"}},
            text=[fmt(v) for v in top10.values],
            textposition="outside",
            hovertemplate="<b>%{x}</b><br>Сума: %{y:,.0f}<extra></extra>",
        ))
        fig_wf.update_layout(height=450, xaxis_tickangle=45, margin=dict(b=150))
        st.plotly_chart(fig_wf, use_container_width=True)

# ── TAB 8: Аналітика ──────────────────────────────────────
with tab8:
    st.subheader("🔍 Аналітика та цікаві розрахунки")
    if not filtered_df.empty:
        col1, col2 = st.columns(2)

        with col1:
            st.write("**📊 Розподіл витрат по типах:**")
            dist_data = (
                filtered_df.groupby("DistributionBase")["Sum"]
                            .sum().sort_values(ascending=False)
            )
            dist_total = dist_data.sum()
            for k, v in dist_data.items():
                st.write(f"{k}: **{v:,.0f}** ({v/dist_total*100:.1f}%)")

        with col2:
            st.write("**🏢 ТОП-5 відділів:**")
            dept5 = (
                filtered_df.groupby("Department")["Sum"]
                            .sum().nlargest(5)
            )
            dept5_total = dept5.sum()
            for k, v in dept5.items():
                st.write(f"{str(k)[:28]}: **{fmt(v)}** ({v/dept5_total*100:.1f}%)")

        st.divider()
        col3, col4 = st.columns(2)

        with col3:
            st.write("**💼 Середня сума по топ-8 типах витрат:**")
            avg_type = (
                filtered_df.groupby("Type_of_expense")["Sum"]
                            .agg(["mean", "count"])
                            .sort_values("mean", ascending=False).head(8)
            )
            for idx, row in avg_type.iterrows():
                st.write(f"{str(idx)[:30]}: **{fmt(row['mean'])}** (n={int(row['count'])})")

        with col4:
            st.write("**📈 Аналіз Парето (правило 80/20):**")
            srt = filtered_df.sort_values("Sum", ascending=False)
            cumsum_pct = (srt["Sum"].cumsum() / srt["Sum"].sum() * 100).values
            idx_80 = next((i for i, x in enumerate(cumsum_pct) if x >= 80),
                          len(cumsum_pct) - 1)
            pct_20 = (idx_80 + 1) / len(srt) * 100

            st.write(f"80% витрат дають **{idx_80+1}** операцій з {len(srt)}")
            st.write(f"Це **{pct_20:.1f}%** від усіх операцій")
            level = "🔴 Висока" if pct_20 < 5 else ("🟡 Середня" if pct_20 < 15 else "🟢 Низька")
            st.write(f"Концентрація: {level}")

        st.divider()

        dist_chart = (
            filtered_df.groupby("DistributionBase")["Sum"]
                        .sum().sort_values(ascending=False)
        )
        fig = px.bar(
            x=dist_chart.index, y=dist_chart.values,
            color=dist_chart.values, color_continuous_scale="Viridis",
            labels={"x": "Тип розподілу", "y": "Сума"},
            title="Розподіл витрат за базою розподілу",
        )
        fig.update_layout(coloraxis_showscale=False, yaxis_tickformat=",.0f")
        st.plotly_chart(fig, use_container_width=True)

# ============================================================
st.divider()
st.caption(f"🕐 {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")

