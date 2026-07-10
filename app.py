import streamlit as st
import requests

# Page configuration
st.set_page_config(page_title="AIOps Dashboard", page_icon="🔴", layout="centered")

st.title("AIOps Drive Diagnostic Portal")
st.markdown("Enter drive telemetry below to trigger the autonomous n8n prediction and remediation pipeline.")

# Explicitly state the model limits at the top of the app
st.info("ℹ️ **Model Limitations:** This Random Forest model was trained on historical Backblaze data. To prevent extrapolation errors, inputs are capped at the maximum values observed in the training dataset.")

WEBHOOK_URL = "https://nesma2026.app.n8n.cloud/webhook-test/3903ce2a-b204-463a-930c-f53cab8c43c8"

# Build the Form with Guardrails
with st.form("telemetry_form"):
    serial_number = st.text_input("Drive Serial Number", value="SN-DEMO-9999")
    
    col1, col2 = st.columns(2)
    with col1:
        smart_5 = st.number_input(
            "Reallocated Sectors (SMART 5)", 
            value=200, 
            help="Limit: 0 to 10,000. Values above this usually indicate immediate mechanical failure."
        )
        smart_187 = st.number_input(
            "Uncorrectable Errors (SMART 187)", 
            value=50,
            help="Limit: 0 to 5,000."
        )
        smart_197 = st.number_input(
            "Pending Sectors (SMART 197)", 
            value=500,
            help="Limit: 0 to 10,000."
        )
    with col2:
        smart_9 = st.number_input(
            "Power-On Hours (SMART 9)", 
            value=60000,
            help="Limit: 0 to 80,000 hours (Approx 9 years). The model cannot accurately predict beyond this age."
        )
        smart_194 = st.number_input(
            "Temperature °C (SMART 194)", 
            value=45,
            help="Limit: 10°C to 70°C. Standard operating temperatures."
        )

    submit_button = st.form_submit_button("Run AI Diagnostic", use_container_width=True)

# 3. Handle Form Submission
if submit_button:
    # --- NEW: Backend Validation ---
    if (smart_5 > 10000 or smart_5 < 0 or
        smart_187 > 5000 or smart_187 < 0 or
        smart_197 > 10000 or smart_197 < 0 or
        smart_9 > 80000 or smart_9 < 0 or
        smart_194 > 70 or smart_194 < 10):
        
        st.error("One or more metrics exceed the model's safe training limits. Please adjust the values to stay within the boundaries before submitting.")
    
    else:
        # --- Proceed with API Call if Valid ---
        payload = {
            "serial_number": serial_number,
            "smart_5_raw": smart_5,
            "smart_9_raw": smart_9,
            "smart_187_raw": smart_187,
            "smart_194_raw": smart_194,
            "smart_197_raw": smart_197
        }

        try:
            with st.spinner('Transmitting telemetry... waiting for AI Engineer diagnosis...'):
                response = requests.post(WEBHOOK_URL, json=payload, timeout=30)
                
            if response.status_code == 200:
                st.success("✅ Alert dispatched to email.")
                
                response_data = response.json()
                ai_text = response_data.get("diagnosis", "No diagnosis text returned.")
                
                st.subheader("🤖 AI Root Cause Analysis")
                st.info(ai_text)
                
            else:
                st.error(f"Error: n8n returned status code {response.status_code}")
        except requests.exceptions.Timeout:
            st.error("The AI took too long to respond. The email might still arrive.")
        except Exception as e:
            st.error(f"Connection Error: Could not reach n8n workflow. Details: {e}")