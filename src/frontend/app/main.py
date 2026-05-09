import os
import requests
import streamlit as st

BACKEND_URL = os.getenv("BACKEND_URL", "http://localhost:8000")

st.title("Frontend")

try:
    response = requests.get(f"{BACKEND_URL}")
    data = response.json()
    st.write(data["message"])
except Exception as e:
    st.write("Backend not reachable")