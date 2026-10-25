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

if submitted:
    if not name.strip():
        st.error("Product name is required.")
        st.stop()

    try:
        r = requests.post(
            f"{BASE}/createproduct",
            json={"ProductName": name, "Stock": stock},
            headers=headers,
            timeout=5,
        )
    except requests.RequestException as e:
        st.error(f"Can't reach the API: {e}")
        st.stop()

    if r.status_code == 200:
        st.success(f"Added {name}.")
        st.rerun()
    else:
        detail = r.json().get("detail", r.text) if r.content else r.text
        st.error(f"{r.status_code}: {detail}")


st.divider()
st.subheader("Update Product")

if not products:
    st.caption("No Products to Update")
    st.stop()

options = {f"{p["Id"]} - {p["ProductName"]}": p for p in products}
label = st.selectbox("Pick a product", list(options.keys()), key="update_pick")
selected = options[label]

with st.form("update_product"):
    new_name = st.text_input("Product Name", value=selected["ProductName"])
    new_stock = st.number_input("Enter Stock", min_value=1, step=1, value=selected["Stock"])
    update_submitted = st.form_submit_button("Save changes")

if update_submitted:
    if not new_name.strip():
        st.error("Product Name requred")
        st.stop()

    payload = {}
    if new_name != selected["ProductName"]:
        payload["ProductName"] = new_name
    if new_stock != selected["Stock"]:
        payload["Stock"] = new_stock

    if not payload:
        st.info("Nothing to update")
        st.stop()

    try:
        r = requests.put(
            f"{BASE}/editproduct/{selected["Id"]}",
            json=payload,
            headers=headers,
            timeout=5
        )
    except requests.RequestException as e:
        st.error(f"Endpoint can not be reached: {e}")

    if r.status_code == 200:
        st.success(f"Updated Product: {selected["Id"]}")
        st.rerun()

    else:
        detail = r.json().get("detail", r.text) if r.content else r.text
        st.error(f"{r.status_code}: {detail}")

st.divider()
st.subheader("Delete Product")

if not products:
    st.caption("Nothing to delete")
    st.stop()


options_d = {f"{p['Id']} - {p['ProductName']}": p for p in products}
label_d = st.selectbox("Pick a product", list(options_d.keys()), key="delete_pick")
selected_d = options_d[label_d]

with st.form("delete_product", clear_on_submit=True):
    st.write(f"About to delete: **{selected_d['ProductName']}** (Id {selected_d['Id']})")
    confirm = st.checkbox("I'm sure")
    delete_submitted = st.form_submit_button("Delete")

if delete_submitted:
    if not confirm:
        st.error("Tick the confirmation box first..")
        st.stop()

    try:
        r = requests.delete(
            f"{BASE}/deleteproduct/{selected_d['Id']}",
            headers=headers,
            timeout=5
        )
    except requests.RequestException as e:
        st.error(f"The endpoint can not be reached: {e}")
        st.stop()

    if r.status_code == 200:
        st.success(f"{selected_d['ProductName']} has been deleted")
        st.rerun()
    else:
        detail = r.json().get("detail", r.text) if r.content else r.text
        st.error(f"{r.status_code}: {detail}")

