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
    
    # Центрування форми входу
    col1, col2, col3 = st.columns([1, 1, 1])
    
    with col2:
        st.markdown("<h1 style='text-align: center'>🔐 Доступ захищений</h1>", unsafe_allow_html=True)
        st.markdown("<p style='text-align: center'>Введіть пароль для входу</p>", unsafe_allow_html=True)
        st.write("")
        
        # Форма для входу
        with st.form("login_form"):
            password = st.text_input(
                "Пароль:",
                type="password",
                placeholder="Введіть пароль",
                label_visibility="collapsed"
            )
            submitted = st.form_submit_button("🔓 Увійти", use_container_width=True)
        
        if submitted:
            # Нормалізуємо типи та обрізаємо пробіли, щоб уникнути невірних порівнянь
            stored_password = st.secrets.get("password", "")
            if stored_password is None:
                stored_password = ""
            # Приводимо до рядка та обрізаємо пробіли
            stored_password = str(stored_password).strip()
            entered = "" if password is None else str(password).strip()

            # --- ДІАГНОСТИКА (БЕЗПЕЧНА) ---
            # Не показує реальний пароль, тільки тип та довжину
            if st.checkbox("Показати діагностику секрету (не показує пароль)"):
                try:
                    st.info(f"secret type: {type(stored_password).__name__}, length: {len(stored_password)}")
                except Exception:
                    st.info("secret не доступний або має невідомий тип")

            if entered != "" and entered == stored_password:
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
