import streamlit as st
import requests

# Page configuration
st.set_page_config(page_title="AIOps Dashboard", page_icon="🔴", layout="centered")

st.title("AIOps Drive Diagnostic Portal")
st.markdown("Enter drive telemetry below to trigger the autonomous n8n prediction and remediation pipeline.")

# 1. Webhook URL for n8n Workflow
WEBHOOK_URL = "https://nesma2026.app.n8n.cloud/webhook-test/3903ce2a-b204-463a-930c-f53cab8c43c8"

# 2. Build the Form
with st.form("telemetry_form"):
    serial_number = st.text_input("Drive Serial Number", value="SN-DEMO-9999")
    
    col1, col2 = st.columns(2)
    with col1:
        smart_5 = st.number_input("Reallocated Sectors (SMART 5)", value=200)
        smart_187 = st.number_input("Uncorrectable Errors (SMART 187)", value=50)
        smart_197 = st.number_input("Pending Sectors (SMART 197)", value=500)
    with col2:
        smart_9 = st.number_input("Power-On Hours (SMART 9)", value=60000)
        smart_194 = st.number_input("Temperature °C (SMART 194)", value=45)

    submit_button = st.form_submit_button("Run AI Diagnostic", use_container_width=True)

# 3. Handle Form Submission
if submit_button:
    payload = {
        "serial_number": serial_number,
        "smart_5_raw": smart_5,
        "smart_9_raw": smart_9,
        "smart_187_raw": smart_187,
        "smart_194_raw": smart_194,
        "smart_197_raw": smart_197
    }

    try:
        with st.spinner('Transmitting telemetry to n8n AI Agent...'):
            response = requests.post(WEBHOOK_URL, json=payload)
            
        if response.status_code == 200:
            st.success("✅ Telemetry successfully transmitted. Check your email for the AI diagnostic report.")
        else:
            st.error(f"⚠️ Error: n8n returned status code {response.status_code}")
    except Exception as e:
        st.error(f"❌ Connection Error: Could not reach n8n workflow. Details: {e}")