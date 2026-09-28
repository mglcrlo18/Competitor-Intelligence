"""
hiring_signals.py
Tracks open roles and hiring velocity using public, unauthenticated ATS APIs
(Greenhouse and Lever). Detects departmental expansion and strategic priorities.
"""
from typing import Dict, List, Any
import httpx


def fetch_greenhouse_jobs(board_token: str) -> List[Dict[str, Any]]:
    """
    Fetches open jobs from Greenhouse's public API.
    URL format: https://boards-api.greenhouse.io/v1/boards/{board_token}/jobs
    """
    url = f"https://boards-api.greenhouse.io/v1/boards/{board_token.lower()}/jobs"
    try:
        response = httpx.get(url, timeout=10.0, follow_redirects=True)
        if response.status_code == 200:
            data = response.json()
            jobs = []
            for j in data.get("jobs", []):
                departments = [d.get("name") for d in j.get("departments", []) if d.get("name")]
                dept_name = ", ".join(departments) if departments else "General"
                jobs.append({
                    "title": j.get("title"),
                    "department": dept_name,
                    "location": j.get("location", {}).get("name", "Remote / Unspecified"),
                    "url": j.get("absolute_url"),
                    "updated_at": j.get("updated_at")
                })
            return jobs
    except Exception as e:
        print(f"Error fetching Greenhouse jobs for {board_token}: {e}")
    return []


def fetch_lever_jobs(company_id: str) -> List[Dict[str, Any]]:
    """
    Fetches open jobs from Lever's public API.
    URL format: https://api.lever.co/v0/postings/{company_id}?mode=json
    """
    url = f"https://api.lever.co/v0/postings/{company_id.lower()}?mode=json"
    try:
        response = httpx.get(url, timeout=10.0, follow_redirects=True)
        if response.status_code == 200:
            postings = response.json()
            jobs = []
            for p in postings:
                categories = p.get("categories", {})
                jobs.append({
                    "title": p.get("text"),
                    "department": categories.get("department", "General"),
                    "location": categories.get("location", "Remote / Unspecified"),
                    "url": p.get("hostedUrl"),
                    "created_at": p.get("createdAt")
                })
            return jobs
    except Exception as e:
        print(f"Error fetching Lever jobs for {company_id}: {e}")
    return []


def analyze_hiring_trends(jobs: List[Dict[str, Any]]) -> Dict[str, Any]:
    """
    Groups open roles by department to infer organizational investment priorities.
    """
    dept_counts: Dict[str, int] = {}
    for job in jobs:
        dept = job.get("department", "General") or "General"
        dept_counts[dept] = dept_counts.get(dept, 0) + 1
        
    sorted_depts = sorted(dept_counts.items(), key=lambda x: x[1], reverse=True)
    return {
        "total_open_roles": len(jobs),
        "department_breakdown": dict(sorted_depts)
    }


if __name__ == "__main__":
    test_company = "stripe"
    jobs = fetch_greenhouse_jobs(test_company)
    print(f"Retrieved {len(jobs)} open jobs for {test_company}")
    trends = analyze_hiring_trends(jobs)
    print("Trends:", trends)
