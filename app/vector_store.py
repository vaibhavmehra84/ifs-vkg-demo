import os
from langchain_mongodb import MongoDBAtlasVectorSearch
from langchain_voyageai import VoyageAIEmbeddings
from app.database import graph_edges_col, db

VOYAGE_API_KEY = os.getenv("VOYAGE_API_KEY")

embeddings = VoyageAIEmbeddings(
    model="voyage-3-lite",
    voyage_api_key=VOYAGE_API_KEY
)

def seed_metadata_ontology():
    """Seeds the IATA-aligned metadata ontology schema into MongoDB."""
    graph_edges_col.delete_many({})
    
    edges = [
        {
            "sourceEntityType": "CrewMember",
            "relationship": "hasHRProfile",
            "targetEntityType": "CrewExperience",
            "cotsProvider": "SuccessFactors_API",
            "endpointPattern": "/api/v1/sf/employees/{employeeId}/profile",
            "description": "Fetch HR profile, service years, rank, and certifications"
        },
        {
            "sourceEntityType": "CrewMember",
            "relationship": "hasReceivedAppreciation",
            "targetEntityType": "Appreciation",
            "cotsProvider": "IFS_Local_API",
            "endpointPattern": "/api/v1/ifs/crew/{employeeId}/appreciations",
            "description": "Fetch customer and purser commendations or appreciations"
        },
        {
            "sourceEntityType": "CrewMember",
            "relationship": "hasWarningNotice",
            "targetEntityType": "WarningNotice",
            "cotsProvider": "IFS_Local_API",
            "endpointPattern": "/api/v1/ifs/crew/{employeeId}/warnings",
            "description": "Fetch disciplinary warnings or attendance issues"
        },
        {
            "sourceEntityType": "CrewMember",
            "relationship": "hasPunctualityRecord",
            "targetEntityType": "OnTimePerformance",
            "cotsProvider": "AIMS_COTS_API",
            "endpointPattern": "/api/v1/aims/crew/{employeeId}/otp-metrics",
            "description": "Fetch on-time performance and reporting metrics"
        }
    ]
    graph_edges_col.insert_many(edges)

def get_vector_store():
    return MongoDBAtlasVectorSearch(
        collection=graph_edges_col,
        embedding=embeddings,
        index_name="vkg_metadata_index",
        text_key="description"
    )