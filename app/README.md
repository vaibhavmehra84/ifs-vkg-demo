# ✈️ Airline In-Flight Services (IFS) — Virtual Knowledge Graph Demo

An enterprise AI agent solution demonstrating how to construct a **Virtual Knowledge Graph (VKG)** using **MongoDB Atlas**, **LangGraph**, and **Anthropic's Claude**. 

This project solves the "COTS Data Fragmentation" challenge in enterprise aviation by providing a dynamic semantic layer. Rather than copying or sync-replicating sensitive business data from disparate COTS systems into a central database, MongoDB stores **only the ontology, graph topology, and API routing metadata**. An AI agent traverses this metadata layer at runtime to execute Just-In-Time (JIT) queries directly against target system APIs.

---

## 🏗️ Architecture Overview

+-----------------------------------------------------------------------+
|                      LangGraph / LangChain Agent                      |
|                  (Promotion Evaluator & Reasoning)                    |
+-----------------------------------------------------------------------+
                                    |
                        1. Query Schema & API Routes
                                    v
+-----------------------------------------------------------------------+
|                       MongoDB Atlas Metadata Store                    |
|                (Stores ONLY: IATA Schema & API Routes)                |
+-----------------------------------------------------------------------+
                                    |
                        2. Resolves Path -> Dynamic Mock API Calls
                                    v
        +---------------------------+---------------------------+
        |                           |                           |
        v                           v                           v
+---------------+           +---------------+           +---------------+
|   IFS Local   |           |   AIMS COTS   |           | SuccessFactors|
| (Commendations|           |  (Roster/OTP) |           |  (HR Master)  |
+---------------+           +---------------+           +---------------+

### Key Technical Principles
* **Zero Business Data Copying:** MongoDB maintains zero operational payloads (no flight logs, PII, or attendance records).
* **IATA Standard Alignment:** Metadata schemas align with IATA AIDM and Schema.org aviation vocabularies (`iata:CrewMember`, `iata:FlightLeg`, `schema:Permit`).
* **Just-In-Time (JIT) Dynamic Retrieval:** The agent reads explicit REST endpoint templates from MongoDB and fetches real-time operational state asynchronously.

---

## 🗂️ Project Directory Structure

ifs-vkg-demo/
├── app/
│   ├── __init__.py
│   ├── main.py              # Streamlit Dashboard UI
│   ├── database.py          # MongoDB Atlas connection setup
│   ├── mock_cots.py         # Mock COTS API endpoints & router
│   ├── vector_store.py      # Atlas Vector Search setup
│   ├── agent.py             # LangGraph agent with Claude LLM
│   └── seed_demo_data.py    # Seeding script (30 Indian crew profiles)
├── .env                     # API Keys & DB connection parameters
├── requirements.txt         # Project dependencies
└── README.md                # Project documentation

---

## 🛠️ Prerequisites & Configuration

* **Python:** 3.10 or higher
* **MongoDB Atlas Cluster:** Active connection URI
* **Anthropic API Key:** Access to Claude models (`claude-3-haiku-20240307` or `claude-3-5-sonnet-20241022`)
* **Voyage AI API Key:** Required if using Atlas Voyage embeddings

### Dependencies (`requirements.txt`)
pymongo>=4.6.0
langchain>=0.2.0
langchain-anthropic>=0.1.15
langchain-voyageai>=0.1.0
langchain-mongodb>=0.1.0
langgraph>=0.1.0
streamlit>=1.35.0
pydantic>=2.7.0
python-dotenv>=1.0.1

### Environment Variables (`.env`)
MONGODB_URI=mongodb+srv://<username>:<password>@cluster.mongodb.net/?retryWrites=true&w=majority
MONGODB_DB_NAME=ifs_vkg_db
ANTHROPIC_API_KEY=sk-ant-api03-...
VOYAGE_API_KEY=pa-...

# Optional: LangSmith Tracing
LANGCHAIN_TRACING_V2=false
LANGCHAIN_API_KEY=lsv2_pt_...
LANGCHAIN_PROJECT=ifs-vkg-demo

---

## 🚀 Step-by-Step Quickstart Guide

### Step 1: Clone & Set Up Virtual Environment
git clone https://github.com/your-org/ifs-vkg-demo.git
cd ifs-vkg-demo

python3 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

### Step 2: Install Dependencies
pip install --upgrade pip
pip install -r requirements.txt

### Step 3: Configure Environment Variables
Create a `.env` file in the project root directory and insert your database connection string and API keys as specified in the Configuration section above.

### Step 4: Seed Metadata and COTS Mock Data
Run the seeding script to populate MongoDB with metadata ontology routes (`meta_entity_types`, `meta_graph_edges`) and 30 realistic Indian cabin crew profiles across BOM, DEL, BLR, MAA, CCU, and HYD bases:

python3 app/seed_demo_data.py

### Step 5: Launch the Application
streamlit run app/main.py

---

## 📊 Demo Scenario: Crew Promotion Evaluation

The demo application showcases an **Agentic Promotion Evaluator** for cabin crew candidates seeking promotion to **Cabin Purser**. 

The agent evaluates candidate performance across strict criteria:
1. **Service Seniority:** Minimum 5.0 years (`SuccessFactors COTS`)
2. **Disciplinary Cleanliness:** 0 Active Warning Notices (`IFS Local System`)
3. **Praise & Commendations:** Minimum 10 Passenger/Purser Appreciations (`IFS Local System`)
4. **Punctuality:** Minimum 98.0% On-Time Reporting Rate (`AIMS FlightOps COTS`)

### Candidate Spectrum & Benchmarks

| Employee ID | Name | Base Location | Experience | Praise Count | Warning Status | OTP % | Expected Agent Verdict |
| :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- |
| **`EMP-1001`** | Aarav Sharma | BOM (Mumbai) | 7.2 yrs | 14 entries | Clean (0) | 99.2% | **RECOMMENDED** |
| **`EMP-1002`** | Ananya Verma | BLR (Bengaluru) | 6.8 yrs | 16 entries | Clean (0) | 99.5% | **RECOMMENDED** |
| **`EMP-1017`** | Amit Mukherjee | CCU (Kolkata) | 3.2 yrs | 3 entries | Clean (0) | 95.8% | **NOT RECOMMENDED** (Lacks Seniority) |
| **`EMP-1026`** | Swati Kulkarni | DEL (Delhi) | 1.8 yrs | 1 entry | Active Warning (`WRN-2026-26`) | 91.2% | **NOT RECOMMENDED** (Active Disciplinary & Low OTP) |

---

## 🛡️ License

Distributed under the MIT License. See `LICENSE` for more information.