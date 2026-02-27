import streamlit as st
from db_connection import get_expenses_data

# ===== НАЛАШТУВАННЯ СТОРІНКИ =====
st.set_page_config(page_title="Дані витрат", page_icon="📊", layout="wide")


# ===== АУТЕНТИФІКАЦІЯ =====
def check_password():
    if "password_correct" not in st.session_state:
        st.session_state.password_correct = False

    if st.session_state.password_correct:
        return True

    col1, col2, col3 = st.columns([1, 1, 1])
    with col2:
        st.markdown("<h1 style='text-align: center'>🔐 Доступ захищений</h1>", unsafe_allow_html=True)
        st.markdown("<p style='text-align: center'>Введіть пароль для входу</p>", unsafe_allow_html=True)
        st.write("")

        with st.form("login_form"):
            password = st.text_input(
                "Пароль:",
                type="password",
                placeholder="Введіть пароль",
                label_visibility="collapsed"
            )
            submitted = st.form_submit_button("🔓 Увійти", use_container_width=True)

        if submitted:
            stored_password = st.secrets.get("password", "2101")
            stored_password = str(stored_password).strip()
            entered = str(password).strip()

            if entered and entered == stored_password:
                st.session_state.password_correct = True
                st.rerun()
            else:
                st.error("❌ Неправильний пароль!")

    return False


# ===== ПЕРЕВІРКА ДОСТУПУ =====
if not check_password():
    st.stop()

# ===== ДАНІ З БД =====
st.title("📊 Дані витрат")

try:
    df = get_expenses_data()
except Exception as e:
    st.error("Помилка підключення до БД:")
    st.exception(e)
    st.stop()

if df is None or df.empty:
    st.warning("Дані не знайдено або сталася помилка запиту.")
else:
    st.dataframe(df, use_container_width=True)
