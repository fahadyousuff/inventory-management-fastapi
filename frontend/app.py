import streamlit as st
import requests

BASE = 'http://127.0.0.1:8000'

st.set_page_config(page_title='Login', page_icon="🔐")
st.title("Login")

if "token" not in st.session_state:
    st.session_state.token = ""
if "user" not in st.session_state:
    st.session_state.user = None


if st.session_state.user:
    u = st.session_state.user
    st.success(f"Logged in as **{u['name']}** ({u['usercode']})")
    if st.button("Log out"):
        st.session_state.token = ""
        st.session_state.user = None
        st.rerun()
    st.stop()



with st.form("Login"):
    usercode = st.text_input("Usercode", placeholder="U-1")
    password = st.text_input("Password", placeholder="Password")
    submitted = st.form_submit_button("Log in")

if submitted:
    if not usercode.strip() or not password:
        st.error("Both field are required.")
        st.stop()
    try:
        r = requests.post(
            f"{BASE}/login",
            json = {"usercode": usercode, "password": password},
            timeout=5
        )
    except requests.RequestException as e:
        st.error(f"Can't reach the endpoint: {e}")
        st.stop()

    if r.status_code == 200:
        data = r.json()
        st.session_state.token = data["token"]
        st.session_state.user = data["user"]
        st.rerun()
    else:
        detail = r.json().get("detail", r.text) if r.content else r.text
        st.error(detail)
