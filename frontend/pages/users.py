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