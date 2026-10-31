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

# ---- list ----
try:
    r = requests.get(f"{BASE}/user", timeout=5, headers=headers)
except requests.RequestException as e:
    st.error(f"Can not reach the endpoint: {e}")
    st.stop()

if r.status_code != 200:
    detail = r.json().get("detail", r.text) if r.content else r.text
    st.error(f"{r.status_code}: {detail}")
    st.stop()

users = r.json()
st.dataframe(pd.DataFrame(users), use_container_width=True, hide_index=True)

# ---- add ----
st.divider()
st.subheader("Add user")

with st.form("add_user", clear_on_submit=True):
    name = st.text_input("Enter user's name")
    submitted = st.form_submit_button("Add")

if submitted:
    if not name.strip():
        st.error("User name is required.")
        st.stop()

    try:
        r = requests.post(
            f"{BASE}/createuser",
            json={"name": name},
            headers=headers,
            timeout=5,
        )
    except requests.RequestException as e:
        st.error(f"Endpoint can not be reached: {e}")
        st.stop()

    if r.status_code == 200:
        st.success(f"Added {name}.")
        st.rerun()
    else:
        detail = r.json().get("detail", r.text) if r.content else r.text
        st.error(f"{r.status_code}: {detail}")

# ---- update ----
st.divider()
st.subheader("Update user")

if not users:
    st.caption("No users to update.")
else:
    options = {f"{u['usercode']} - {u['name']}": u for u in users}
    label = st.selectbox("Pick user", list(options.keys()), key="update_pick")
    selected = options[label]

    with st.form("update_user"):
        new_username = st.text_input("Name", value=selected["name"])
        update_submitted = st.form_submit_button("Save changes")

    if update_submitted:
        if not new_username.strip():
            st.error("Name is required.")
            st.stop()

        payload = {}
        if new_username != selected["name"]:
            payload["name"] = new_username

        if not payload:
            st.info("Nothing changed.")
            st.stop()

        try:
            r = requests.put(
                f"{BASE}/edit/{selected['Id']}",
                json=payload,
                headers=headers,
                timeout=5,
            )
        except requests.RequestException as e:
            st.error(f"The endpoint can not be reached: {e}")
            st.stop()

        if r.status_code == 200:
            st.success(f"User {selected['usercode']} has been updated.")
            st.rerun()
        else:
            detail = r.json().get("detail", r.text) if r.content else r.text
            st.error(f"{r.status_code}: {detail}")

# ---- delete ----
st.divider()
st.subheader("Delete user")

if not users:
    st.caption("Nothing to delete.")
    st.stop()

options_d = {f"{u['usercode']} - {u['name']}": u for u in users}
label_d = st.selectbox("Pick user", list(options_d.keys()), key="delete_pick")
selected_d = options_d[label_d]

with st.form("delete_user", clear_on_submit=True):
    st.write(f"About to delete: **{selected_d['name']}** ({selected_d['usercode']})")
    confirm = st.checkbox("I'm sure")
    delete_submitted = st.form_submit_button("Delete")

if delete_submitted:
    if not confirm:
        st.error("Tick the confirmation box first.")
        st.stop()

    try:
        r = requests.delete(
            f"{BASE}/delete/{selected_d['Id']}",
            headers=headers,
            timeout=5,
        )
    except requests.RequestException as e:
        st.error(f"The endpoint can not be reached: {e}")
        st.stop()

    if r.status_code == 200:
        st.success(f"{selected_d['name']} has been deleted.")
        st.rerun()
    else:
        detail = r.json().get("detail", r.text) if r.content else r.text
        st.error(f"{r.status_code}: {detail}")