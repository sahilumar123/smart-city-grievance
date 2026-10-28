
import pandas as pd
from app.models import Grievance


def generate_city_insights():
    grievances = Grievance.query.all()

    if not grievances:
        return {
            "total_complaints": 0,
            "resolved_count": 0,
            "resolution_rate": 0.0,
            "zone_breakdown": {},
            "category_breakdown": {},
            "status_breakdown": {
                "Pending": 0,
                "In Progress": 0,
                "Resolved": 0
            }
        }

    data = [{
        "id": g.id,
        "category": g.category,
        "location": g.location,
        "status": g.status,
        "date_posted": g.date_posted
    } for g in grievances]

    df = pd.DataFrame(data)

    total_complaints = len(df)
    resolved_count = int((df["status"] == "Resolved").sum())

    resolution_rate = (
        round((resolved_count / total_complaints) * 100, 2)
        if total_complaints > 0 else 0.0
    )

    zone_breakdown = {
        str(key): int(value)
        for key, value in df["location"].value_counts().items()
    }

    category_breakdown = {
        str(key): int(value)
        for key, value in df["category"].value_counts().items()
    }

    # Keep all three status labels present, even when their count is zero.
    status_counts = df["status"].value_counts().to_dict()

    status_breakdown = {
        status: int(status_counts.get(status, 0))
        for status in ["Pending", "In Progress", "Resolved"]
    }

    return {
        "total_complaints": total_complaints,
        "resolved_count": resolved_count,
        "resolution_rate": resolution_rate,
        "zone_breakdown": zone_breakdown,
        "category_breakdown": category_breakdown,
        "status_breakdown": status_breakdown
    }
