import os
from pymongo import MongoClient
from dotenv import load_dotenv

load_dotenv()

MONGODB_URI = os.getenv("MONGODB_URI")
DB_NAME = os.getenv("MONGODB_DB_NAME", "ifs_vkg_db")

client = MongoClient(MONGODB_URI)
db = client[DB_NAME]

# Metadata Collections
entity_types_col = db["meta_entity_types"]
graph_edges_col = db["meta_graph_edges"]

# Mock COTS Collections (acting as dynamic API sources)
cots_successfactors_col = db["cots_successfactors"]
cots_aims_otp_col = db["cots_aims_otp"]
cots_ifs_appreciations_col = db["cots_ifs_appreciations"]
cots_ifs_warnings_col = db["cots_ifs_warnings"]

def init_db_indexes():
    """Builds required indexes for fast graph routing and vector search."""
    graph_edges_col.create_index([("sourceEntityType", 1), ("relationship", 1)])
    entity_types_col.create_index([("_id", 1)])