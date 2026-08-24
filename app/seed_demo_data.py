import os
import random
from pymongo import MongoClient
from dotenv import load_dotenv

load_dotenv()

MONGODB_URI = os.getenv("MONGODB_URI")
DB_NAME = os.getenv("MONGODB_DB_NAME", "ifs_vkg_db")

client = MongoClient(MONGODB_URI)
db = client[DB_NAME]

# Collections
meta_entity_types = db["meta_entity_types"]
meta_graph_edges = db["meta_graph_edges"]
cots_sf = db["cots_successfactors"]
cots_aims = db["cots_aims_otp"]
cots_appr = db["cots_ifs_appreciations"]
cots_warn = db["cots_ifs_warnings"]

BASES = ["DEL (Delhi)", "BOM (Mumbai)", "BLR (Bengaluru)", "MAA (Chennai)", "CCU (Kolkata)", "HYD (Hyderabad)"]
AIRCRAFT_TYPES = ["A320neo", "A321neo", "B777-300ER", "B787-9", "A350-900"]

FIRST_NAMES = [
    "Aarav", "Ananya", "Rohan", "Priya", "Vikram", "Neha", "Arjun", "Kavya", 
    "Siddharth", "Pooja", "Rahul", "Meera", "Aditya", "Riya", "Karan", "Sneha",
    "Amit", "Divya", "Suresh", "Anjali", "Varun", "Isha", "Deepak", "Tanvi",
    "Manish", "Swati", "Nikhil", "Simran", "Rajesh", "Pooja"
]

LAST_NAMES = [
    "Sharma", "Verma", "Iyer", "Patel", "Reddy", "Nair", "Kapoor", "Chatterjee",
    "Deshmukh", "Chowdhury", "Rao", "Gupta", "Joshi", "Bhat", "Mehta", "Singh",
    "Mukherjee", "Kulkarni", "Pillai", "Agarwal"
]

CANDIDATE_TYPES = ["STAR"] * 6 + ["GOOD"] * 10 + ["AVERAGE"] * 9 + ["UNDER"] * 5

def seed_metadata_collections():
    """Seeds ontology entity types and graph routing edges."""
    print("Seeding Metadata Ontology Collections...")
    meta_entity_types.delete_many({})
    meta_graph_edges.delete_many({})

    # 1. Entity Types Registry
    entity_types = [
        {
            "_id": "CrewMember",
            "iataClass": "iata:CrewMember",
            "primaryKeyField": "employeeId",
            "sourceSystem": "SAP_SuccessFactors",
            "description": "Master employee record for cabin crew"
        },
        {
            "_id": "CrewExperience",
            "iataClass": "schema:Permit",
            "primaryKeyField": "employeeId",
            "sourceSystem": "SAP_SuccessFactors",
            "description": "Aircraft type certifications and HR rating records"
        },
        {
            "_id": "OnTimePerformance",
            "iataClass": "iata:FlightOpsMetrics",
            "primaryKeyField": "employeeId",
            "sourceSystem": "AIMS_FlightOps",
            "description": "Roster compliance and on-time reporting statistics"
        },
        {
            "_id": "Appreciation",
            "iataClass": "ifs:Appreciation",
            "primaryKeyField": "employeeId",
            "sourceSystem": "IFS_Local",
            "description": "Passenger and purser commendation records"
        },
        {
            "_id": "WarningNotice",
            "iataClass": "ifs:WarningNotice",
            "primaryKeyField": "employeeId",
            "sourceSystem": "IFS_Local",
            "description": "Disciplinary entries and attendance violation flags"
        }
    ]
    meta_entity_types.insert_many(entity_types)

    # 2. Virtual Graph Edges & Routing Patterns
    edges = [
        {
            "edgeId": "CrewMember_TO_Experience",
            "sourceEntityType": "CrewMember",
            "relationship": "hasHRProfile",
            "targetEntityType": "CrewExperience",
            "cotsProvider": "SuccessFactors_API",
            "endpointPattern": "/api/v1/sf/employees/{employeeId}/profile",
            "description": "Fetch HR profile, service years, rank, and certifications"
        },
        {
            "edgeId": "CrewMember_TO_Appreciation",
            "sourceEntityType": "CrewMember",
            "relationship": "hasReceivedAppreciation",
            "targetEntityType": "Appreciation",
            "cotsProvider": "IFS_Local_API",
            "endpointPattern": "/api/v1/ifs/crew/{employeeId}/appreciations",
            "description": "Fetch customer and purser commendations or appreciations"
        },
        {
            "edgeId": "CrewMember_TO_Warning",
            "sourceEntityType": "CrewMember",
            "relationship": "hasWarningNotice",
            "targetEntityType": "WarningNotice",
            "cotsProvider": "IFS_Local_API",
            "endpointPattern": "/api/v1/ifs/crew/{employeeId}/warnings",
            "description": "Fetch disciplinary warnings or attendance issues"
        },
        {
            "edgeId": "CrewMember_TO_OTP",
            "sourceEntityType": "CrewMember",
            "relationship": "hasPunctualityRecord",
            "targetEntityType": "OnTimePerformance",
            "cotsProvider": "AIMS_COTS_API",
            "endpointPattern": "/api/v1/aims/crew/{employeeId}/otp-metrics",
            "description": "Fetch on-time performance and reporting metrics"
        }
    ]
    meta_graph_edges.insert_many(edges)

def generate_crew_dataset():
    print("Clearing old COTS mock data...")
    cots_sf.delete_many({})
    cots_aims.delete_many({})
    cots_appr.delete_many({})
    cots_warn.delete_many({})

    sf_docs, aims_docs, appr_docs, warn_docs = [], [], [], []

    print("Generating 30 Indian Crew Profiles...")
    for i in range(1, 31):
        emp_id = f"EMP-{1000 + i}"
        first_name = FIRST_NAMES[(i - 1) % len(FIRST_NAMES)]
        last_name = LAST_NAMES[(i - 1) % len(LAST_NAMES)]
        full_name = f"{first_name} {last_name}"
        base_loc = BASES[i % len(BASES)]
        category = CANDIDATE_TYPES[i - 1]

        if category == "STAR":
            service_years = round(random.uniform(5.5, 9.0), 1)
            rank = "Senior Flight Attendant"
            hr_rating = "Exceeds Expectations"
            certs = random.sample(AIRCRAFT_TYPES, 4) + ["VIP_Service_Certified", "FirstAid_Level3"]
        elif category == "GOOD":
            service_years = round(random.uniform(4.0, 6.5), 1)
            rank = "Senior Flight Attendant" if service_years > 5.0 else "Flight Attendant"
            hr_rating = "Exceeds Expectations" if random.random() > 0.5 else "Meets Expectations"
            certs = random.sample(AIRCRAFT_TYPES, 3) + ["FirstAid_Level3"]
        elif category == "AVERAGE":
            service_years = round(random.uniform(2.5, 4.5), 1)
            rank = "Flight Attendant"
            hr_rating = "Meets Expectations"
            certs = random.sample(AIRCRAFT_TYPES, 2) + ["FirstAid_Level2"]
        else:  # UNDER
            service_years = round(random.uniform(1.0, 3.2), 1)
            rank = "Flight Attendant"
            hr_rating = "Needs Improvement"
            certs = random.sample(AIRCRAFT_TYPES, 1) + ["FirstAid_Basic"]

        sf_docs.append({
            "_id": emp_id,
            "employeeId": emp_id,
            "fullName": full_name,
            "currentRank": rank,
            "baseLocation": base_loc,
            "yearsOfService": service_years,
            "certifications": certs,
            "hrRating": hr_rating,
            "performanceCategory": category
        })

        if category == "STAR":
            otp = round(random.uniform(98.5, 99.8), 1)
            absences = 0
            flights = random.randint(140, 170)
        elif category == "GOOD":
            otp = round(random.uniform(97.0, 98.4), 1)
            absences = random.choice([0, 1])
            flights = random.randint(120, 150)
        elif category == "AVERAGE":
            otp = round(random.uniform(94.5, 96.9), 1)
            absences = random.choice([1, 2])
            flights = random.randint(100, 130)
        else:  # UNDER
            otp = round(random.uniform(88.0, 93.9), 1)
            absences = random.randint(3, 6)
            flights = random.randint(80, 110)

        aims_docs.append({
            "_id": emp_id,
            "employeeId": emp_id,
            "evaluationPeriod": "Last 12 Months",
            "totalFlightsRostered": flights,
            "onTimeReportingPercentage": otp,
            "unexcusedAbsences": absences
        })

        if category == "STAR":
            count = random.randint(11, 18)
            comments = [
                {"submittedBy": "Senior Purser", "text": "Outstanding handling of passenger medical incident."},
                {"submittedBy": "Passenger (Business Class)", "text": "Exceptional warmth and hospitality throughout flight."}
            ]
        elif category == "GOOD":
            count = random.randint(6, 10)
            comments = [{"submittedBy": "Passenger", "text": "Punctual, cheerful service."}]
        elif category == "AVERAGE":
            count = random.randint(2, 5)
            comments = [{"submittedBy": "Peer Review", "text": "Good team player."}]
        else:  # UNDER
            count = random.randint(0, 1)
            comments = []

        appr_docs.append({
            "_id": emp_id,
            "employeeId": emp_id,
            "totalAppreciations": count,
            "recentComments": comments
        })

        if category in ["STAR", "GOOD"]:
            warn_count = 0
            active = False
            records = []
        elif category == "AVERAGE":
            warn_count = random.choice([0, 1])
            active = False
            records = [{
                "warningId": f"WRN-2025-{i}",
                "severity": "Low",
                "category": "Uniform Compliance",
                "status": "EXPIRED"
            }] if warn_count == 1 else []
        else:  # UNDER
            warn_count = random.randint(1, 2)
            active = True
            records = [{
                "warningId": f"WRN-2026-{i}",
                "severity": "High",
                "category": "Late Reporting / Unexcused Absence",
                "status": "ACTIVE"
            }]

        warn_docs.append({
            "_id": emp_id,
            "employeeId": emp_id,
            "warningCount": warn_count,
            "activeDisciplinary": active,
            "records": records
        })

    cots_sf.insert_many(sf_docs)
    cots_aims.insert_many(aims_docs)
    cots_appr.insert_many(appr_docs)
    cots_warn.insert_many(warn_docs)

    print("Successfully populated COTS collections!")

if __name__ == "__main__":
    seed_metadata_collections()
    generate_crew_dataset()