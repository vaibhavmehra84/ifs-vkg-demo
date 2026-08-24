from app.database import (
    cots_successfactors_col,
    cots_aims_otp_col,
    cots_ifs_appreciations_col,
    cots_ifs_warnings_col
)

def seed_mock_cots_data():
    """Seeds sample operational data into isolated mock COTS collections."""
    cots_successfactors_col.delete_many({})
    cots_aims_otp_col.delete_many({})
    cots_ifs_appreciations_col.delete_many({})
    cots_ifs_warnings_col.delete_many({})

    # SuccessFactors HR Master
    cots_successfactors_col.insert_one({
        "_id": "EMP-8821",
        "employeeId": "EMP-8821",
        "fullName": "Sarah Jenkins",
        "currentRank": "Senior Flight Attendant",
        "baseLocation": "LHR",
        "yearsOfService": 6.5,
        "certifications": ["B777-300ER", "A350-900"],
        "hrRating": "Exceeds Expectations"
    })

    # AIMS Flight Operations
    cots_aims_otp_col.insert_one({
        "_id": "EMP-8821",
        "employeeId": "EMP-8821",
        "onTimeReportingPercentage": 99.3,
        "unexcusedAbsences": 0,
        "totalFlightsRostered": 142
    })

    # IFS Local - Appreciations
    cots_ifs_appreciations_col.insert_one({
        "_id": "EMP-8821",
        "employeeId": "EMP-8821",
        "totalAppreciations": 14,
        "recentComments": [
            "Exceptional handling of medical emergency during flight BA178.",
            "Consistently praised by premium passengers for cabin service."
        ]
    })

    # IFS Local - Warnings
    cots_ifs_warnings_col.insert_one({
        "_id": "EMP-8821",
        "employeeId": "EMP-8821",
        "warningCount": 0,
        "activeDisciplinary": False,
        "records": []
    })

def mock_cots_api_router(endpoint_pattern: str, employee_id: str) -> dict:
    """Simulates JIT REST API calls to target COTS systems."""
    if "sf/employees" in endpoint_pattern:
        return cots_successfactors_col.find_one({"_id": employee_id}) or {}
    elif "aims/crew" in endpoint_pattern:
        return cots_aims_otp_col.find_one({"_id": employee_id}) or {}
    elif "ifs/crew" in endpoint_pattern and "appreciations" in endpoint_pattern:
        return cots_ifs_appreciations_col.find_one({"_id": employee_id}) or {}
    elif "ifs/crew" in endpoint_pattern and "warnings" in endpoint_pattern:
        return cots_ifs_warnings_col.find_one({"_id": employee_id}) or {}
    return {}