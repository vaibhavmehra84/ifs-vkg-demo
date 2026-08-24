import streamlit as st
import json
from app.database import init_db_indexes
from app.mock_cots import seed_mock_cots_data
from app.vector_store import seed_metadata_ontology
from app.agent import vkg_agent_app

st.set_page_config(page_title="IFS Virtual Knowledge Graph Demo", layout="wide")

st.title("✈️ Airline In-Flight Services (IFS) - Virtual Knowledge Graph")
st.caption("Zero-Copy Enterprise Integration using MongoDB Atlas, LangGraph, & Claude")

# Sidebar Controls
st.sidebar.header("Setup & Diagnostics")
if st.sidebar.button("Initialize & Seed MongoDB"):
    init_db_indexes()
    seed_mock_cots_data()
    seed_metadata_ontology()
    st.sidebar.success("MongoDB Indexes, VKG Metadata & COTS Mock Data Initialized!")

st.sidebar.markdown("---")
emp_id = st.sidebar.text_input("Candidate Employee ID", "EMP-8821")
target_rank = st.sidebar.selectbox("Target Promotion Rank", ["Cabin Purser", "Senior Purser"])

if st.button("Run Promotion Evaluation Agent"):
    with st.spinner("Agent running LangGraph execution..."):
        initial_state = {
            "employee_id": emp_id,
            "target_rank": target_rank,
            "discovered_routes": [],
            "fetched_cots_payloads": {},
            "evaluation_result": ""
        }
        
        final_state = vkg_agent_app.invoke(initial_state)

    col1, col2 = st.columns([1, 1])

    with col1:
        st.subheader("1. Discovered VKG API Routes (MongoDB)")
        st.json(final_state["discovered_routes"])

        st.subheader("2. Just-In-Time Fetched COTS Payloads")
        st.json(final_state["fetched_cots_payloads"])

    with col2:
        st.subheader("3. Claude LLM Promotion Evaluation")
        st.markdown(final_state["evaluation_result"])