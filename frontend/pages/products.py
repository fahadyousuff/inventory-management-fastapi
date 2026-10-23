import pandas as pd
import streamlit as st
import requests

st.set_page_config(page_title="Products", page_icon="📦")
st.title("Products")

if not st.session_state.get("token"):
    st.warning("Please login first.")
    st.stop()

BASE = 'http://127.0.0.1:8000'

headers = {"Authorization": f"Bearer {st.session_state.token}"}

try:
    r = requests.get(f"{BASE}/product", timeout=5, headers=headers)
except requests.RequestException as e:
    st.error(f"Can't reach the API: {e}")
    st.stop()

# this is for if the endpoint can not be reached
if r.status_code != 200:
    detail = r.json().get("detail", r.text) if r.content else r.text
    st.error(f"{r.status_code}: {detail}")
    st.stop()

products = r.json()
st.dataframe(pd.DataFrame(products), use_container_width=True, hide_index=True)

st.divider()
st.subheader("Add Products")

with st.form("add_product", clear_on_submit=True):
    name = st.text_input("Product Name")
    stock = st.number_input("Stock", min_value=1, step=1)
    submitted = st.form_submit_button("Add")