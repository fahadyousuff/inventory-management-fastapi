import streamlit as st
import requests
import pandas as pd

BASE = "http://127.0.0.1:8000"

st.set_page_config(page_title=" Sales")
st.title("Sales")

if not st.session_state["token"]:
    st.warning("Login First")
    st.stop()

headers = {"Authorization": f"Bearer {st.session_state["token"]}"}

try:
    r = requests.get(
        f"{BASE}/sales",
        timeout=5,
        headers=headers
    )
except requests.RequestException as e:
    st.error(f"Can not reach the End-point : {e}")
    st.stop()

if r.status_code != 200:
    detail = r.json().get("detail", r.text) if r.content else r.text
    st.error(f"{r.status_code}: {detail}")
    st.stop()

sales = r.json()
st.dataframe(pd.DataFrame(sales), use_container_width=True, hide_index=True)