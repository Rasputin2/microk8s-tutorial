import streamlit as st
import requests

st.title("Frontend")

try:
    response = requests.get(http://backend-service:8000/)
    data = response.json()
    st.write(data["message"])
except Exception as e:
    st.write("Backend not reachable")

👉 Calls backend via Kubernetes service