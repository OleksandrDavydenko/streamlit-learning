import streamlit as st

# ===== НАЛАШТУВАННЯ СТОРІНКИ =====
st.set_page_config(
    page_title="Урок 1: Основи",
    page_icon="📚",
    layout="wide"
)

# ===== АУТЕНТИФІКАЦІЯ =====
def check_password():
    """Перевірка пароля для входу"""
    if "password_correct" not in st.session_state:
        st.session_state.password_correct = False
    
    if st.session_state.password_correct:
        return True
    
    st.warning("🔐 Введіть пароль для доступу до додатку")
    password = st.text_input("Пароль:", type="password")
    
    if password:
        if password == "2101":  # Змініть на ваш пароль
            st.session_state.password_correct = True
            st.rerun()
        else:
            st.error("❌ Неправильний пароль!")
    
    return False

# Перевірка доступу
if not check_password():
    st.stop()

st.title("📚 У мене все круто виходить")
st.write("---")

# ===== ВИВЕДЕННЯ ТЕКСТУ =====
st.write("## 1️ Пробую щось нове!")

st.write("✅ st.write() - універсальна функція для всього")
st.write()

st.header("Це заголовок h1 (st.header)")
st.subheader("Це підзаголовок h2 (st.subheader)")
st.text("Звичайний текст (st.text)")
st.markdown("**Жирний текст** через markdown (st.markdown)")
st.code("print('Це блок коду')", language="python")

# ===== ПЕРЕРИВ =====

st.divider()
