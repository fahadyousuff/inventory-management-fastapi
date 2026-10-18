import streamlit as st
import pandas as pd
import requests

BASE = "http://127.0.0.1:8000"

st.title("Products")

# token guard
token = st.session_state.get("token", "")
if not token:
    st.warning("Set your API token on the Home page first.")
    st.stop()

headers = {"Authorization": f"Bearer {token}"}

# fetch + show
r = requests.get(f"{BASE}/product", headers=headers)
if r.status_code >= 400:
    st.error(f"{r.status_code}: {r.json().get('detail', r.text)}")
    st.stop()

products = r.json()
st.dataframe(pd.DataFrame(products), use_container_width=True, hide_index=True)