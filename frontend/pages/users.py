import pandas as pd
import streamlit as st
import requests

st.set_page_config(page_title="Users", page_icon="👤")
st.title("Users")

if not st.session_state.get("token"):
    st.warning("Please login first.")
    st.stop()

BASE = 'http://127.0.0.1:8000'


headers = {"Authorization": f"Bearer {st.session_state.token}"}

try:
    r = requests.get(
        f"{BASE}/user",
        timeout=5,
        headers=headers
    )
except requests.RequestException as e:
    st.error(f"Can not reach the endpoint: {e}")
    st.stop()

if r.status_code != 200:
    detail = r.json().get("detail", r.text) if r.content else r.text
    st.error(f"{r.status_code}: {detail}")
    st.stop()

users = r.json()
st.dataframe(pd.DataFrame(users), use_container_width=True, hide_index=True)


st.divider("")
st.subheader("Add Users")

with st.form("add_user", clear_on_submit=True):
    name= st.text_input("Enter User's name")
    submitted = st.form_submit_button("Add")

if submitted:
    if not name.strip():
        st.error("User Name is required")
        st.stop()

    try:
        r = requests.post(
            f"{BASE}/createuser",
            json={"name", name},
            headers=headers,
            timeout=5
        )
    except requests.RequestException as e:
        st.error(f"Endpoint can not be reached: {e}")
        st.stop()

    if r.status_code == 200:
        st.success(f"Added {name}")
        st.rerun()
    else:
        detail = r.json().get("detail", r.text) if r.content else r.text
        st.error(f"{r.status_code}: {detail}")

