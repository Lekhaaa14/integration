import streamlit as st
import requests
import pandas as pd
from datetime import datetime

# Page config
st.set_page_config(page_title="Access Intelligence Dashboard", layout="wide")

# API endpoints
INTEGRATION_URL = "http://localhost:4000"
MONICA_URL = "http://192.168.0.17:8000"
LEKHA_URL = "http://localhost:3000"

# Title
st.title("🛡️ Access Intelligence Dashboard")

# Refresh button at top
if st.button("🔄 Refresh Data", use_container_width=True):
    st.cache_data.clear()
    st.rerun()

st.markdown("---")

# Submit New Log Section
st.subheader("📝 Submit New Log")

with st.form("submit_log_form"):
    col1, col2 = st.columns(2)
    
    with col1:
        user_id = st.text_input("User ID", placeholder="e.g. vendor_123")
        role = st.selectbox("Role", options=["vendor", "admin", "analyst", "ai-system"])
        resource = st.selectbox(
            "Resource",
            options=["/customer-data", "/api/admin", "/db/orders", "/db/users", "/api/products", "/vendor-api", "/ml-data", "/analytics"]
        )
    
    with col2:
        action = st.selectbox("Action", options=["READ", "WRITE"])
        source = st.selectbox("Source", options=["vendor_api", "internal", "ml_pipeline", "DB", "API"])
    
    submit_button = st.form_submit_button("📤 Submit Log")

if submit_button:
    if not user_id:
        st.error("❌ User ID is required")
    else:
        with st.spinner("Processing log submission..."):
            try:
                # Step 1: Submit to LEKHA logs endpoint
                log_data = {
                    "user_id": user_id,
                    "role": role,
                    "resource": resource,
                    "action": action,
                    "source": source
                }
                
                response1 = requests.post(f"{LEKHA_URL}/logs", json=log_data, timeout=5)
                response1.raise_for_status()
                log_result = response1.json()
                
                st.success(f"✅ Log ingested! Anomaly Flag: {log_result.get('anomaly_flag', 'N/A')}")
                
                # Step 2: Submit to demo-pipeline for full analysis
                response2 = requests.post(f"{INTEGRATION_URL}/demo-pipeline", json=log_data, timeout=5)
                response2.raise_for_status()
                pipeline_result = response2.json()
                
                # Display full results
                st.success("✅ Analysis Complete!")
                
                # Create two columns to show results
                col_result1, col_result2 = st.columns(2)
                
                with col_result1:
                    st.write("**Step 1: Log Ingestion**")
                    st.json(pipeline_result.get("step1_ingested", {}))
                
                with col_result2:
                    st.write("**Step 2: Risk Analysis**")
                    st.json(pipeline_result.get("step2_analyzed", {}))
                
                st.write("**Final Result**")
                final_result = pipeline_result.get("final", {})
                
                # Display key findings
                col_f1, col_f2, col_f3, col_f4 = st.columns(4)
                with col_f1:
                    st.metric("Purpose", final_result.get("purpose", "N/A"))
                with col_f2:
                    st.metric("Risk Score", final_result.get("risk_score", "N/A"))
                with col_f3:
                    st.metric("Policy Violation", "⚠️ Yes" if final_result.get("policy_violation") else "✓ No")
                with col_f4:
                    st.metric("Violated Rule", final_result.get("violated_rule", "None"))
                
                st.json(final_result)
                
                # Refresh cache to update dashboard
                st.cache_data.clear()
                
            except requests.exceptions.RequestException as e:
                st.error(f"❌ Error submitting log: {e}")
            except Exception as e:
                st.error(f"❌ Unexpected error: {e}")

st.markdown("---")

# Function to fetch dashboard summary
def fetch_dashboard_summary():
    try:
        response = requests.get(f"{INTEGRATION_URL}/dashboard-summary", timeout=5)
        return response.json()
    except Exception as e:
        st.warning(f"⚠️ Failed to fetch dashboard summary: {e}")
        return None

# Function to fetch access intelligence
def fetch_access_intelligence():
    try:
        response = requests.get(f"{INTEGRATION_URL}/access-intelligence", timeout=5)
        return response.json()
    except Exception as e:
        st.warning(f"⚠️ Failed to fetch access intelligence: {e}")
        return None

# Function to fetch top users
def fetch_top_users():
    try:
        response = requests.get(f"{LEKHA_URL}/top-users", timeout=5)
        return response.json()
    except Exception as e:
        st.warning(f"⚠️ Failed to fetch top users: {e}")
        return None

# Function to fetch anomalies
def fetch_anomalies():
    try:
        response = requests.get(f"{LEKHA_URL}/anomalies", timeout=5)
        return response.json()
    except Exception as e:
        st.warning(f"⚠️ Failed to fetch anomalies: {e}")
        return None

# Load data with spinner
with st.spinner("Loading dashboard data..."):
    summary = fetch_dashboard_summary()
    access_intel = fetch_access_intelligence()
    top_users = fetch_top_users()
    anomalies = fetch_anomalies()

# Top metrics row
if summary:
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric("Total Logs", summary.get("total_logs", 0))
    
    with col2:
        st.metric("Total Anomalies", summary.get("anomalies", 0))
    
    with col3:
        st.metric("Vendor Logs", summary.get("vendor_logs", 0))
    
    with col4:
        st.metric("High Risk", summary.get("high_risk", 0))
else:
    st.error("Failed to load metrics")

st.markdown("---")

# Access Intelligence Table
st.subheader("📊 Access Intelligence")
if access_intel:
    df_intel = pd.DataFrame(access_intel)
    columns_to_show = [
        "user_id", "role", "resource", "purpose", 
        "risk_score", "anomaly_flag", "policy_violation", "violated_rule"
    ]
    columns_available = [col for col in columns_to_show if col in df_intel.columns]
    st.dataframe(df_intel[columns_available], use_container_width=True)
else:
    st.warning("No access intelligence data available")

st.markdown("---")

# Top Users Bar Chart
st.subheader("👥 Top Users by Access Count")
if top_users:
    df_users = pd.DataFrame(top_users)
    if not df_users.empty and "user_id" in df_users.columns and "total_access" in df_users.columns:
        st.bar_chart(df_users.set_index("user_id")["total_access"])
    else:
        st.warning("No user data available for chart")
else:
    st.warning("Could not fetch top users data")

st.markdown("---")

# Recent Anomalies Table
st.subheader("🚨 Recent Anomalies")
if anomalies:
    df_anomalies = pd.DataFrame(anomalies)
    columns_to_show = ["user_id", "role", "resource", "action", "timestamp"]
    columns_available = [col for col in columns_to_show if col in df_anomalies.columns]
    st.dataframe(df_anomalies[columns_available], use_container_width=True)
else:
    st.warning("No anomaly data available")

st.markdown("---")

# Footer with timestamp
st.caption(f"Last updated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
 