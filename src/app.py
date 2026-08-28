"""
High School Management System API

A super simple FastAPI application that allows students to view and sign up
for extracurricular activities at Mergington High School.
"""

from fastapi import FastAPI, HTTPException
from fastapi.staticfiles import StaticFiles
from fastapi.responses import RedirectResponse
import os
from pathlib import Path


def normalize_email(email: str) -> str:
    """Normalize student emails for reliable duplicate checking."""
    return email.strip().lower()


app = FastAPI(title="Mergington High School API",
              description="API for viewing and signing up for extracurricular activities")

# Mount the static files directory
current_dir = Path(__file__).parent
app.mount("/static", StaticFiles(directory=os.path.join(Path(__file__).parent,
          "static")), name="static")

# In-memory activity database
activities = {
    "Chess Club": {
        "description": "Learn strategies and compete in chess tournaments",
        "schedule": "Fridays, 3:30 PM - 5:00 PM",
        "max_participants": 12,
        "participants": ["michael@mergington.edu", "daniel@mergington.edu"]
    },
    "Programming Class": {
        "description": "Learn programming fundamentals and build software projects",
        "schedule": "Tuesdays and Thursdays, 3:30 PM - 4:30 PM",
        "max_participants": 20,
        "participants": ["emma@mergington.edu", "sophia@mergington.edu"]
    },
    "Gym Class": {
        "description": "Physical education and sports activities",
        "schedule": "Mondays, Wednesdays, Fridays, 2:00 PM - 3:00 PM",
        "max_participants": 30,
        "participants": ["john@mergington.edu", "olivia@mergington.edu"]
    },
    "Basketball Team": {
        "description": "Join the competitive basketball team and compete in league matches",
        "schedule": "Tuesdays and Thursdays, 4:00 PM - 5:30 PM",
        "max_participants": 15,
        "participants": ["james@mergington.edu"]
    },
    "Soccer Club": {
        "description": "Practice soccer skills and participate in friendly matches",
        "schedule": "Mondays and Wednesdays, 3:30 PM - 5:00 PM",
        "max_participants": 20,
        "participants": ["alex@mergington.edu", "isabella@mergington.edu"]
    },
    "Art Studio": {
        "description": "Explore painting, drawing, and various art techniques",
        "schedule": "Wednesdays and Saturdays, 2:00 PM - 3:30 PM",
        "max_participants": 18,
        "participants": ["mia@mergington.edu"]
    },
    "Theater Club": {
        "description": "Perform in plays and develop acting and stage skills",
        "schedule": "Fridays, 4:00 PM - 6:00 PM",
        "max_participants": 25,
        "participants": ["lucas@mergington.edu", "sophia@mergington.edu"]
    },
    "Debate Team": {
        "description": "Participate in debates and develop public speaking skills",
        "schedule": "Tuesdays, 3:30 PM - 4:45 PM",
        "max_participants": 16,
        "participants": ["noah@mergington.edu"]
    },
    "Science Club": {
        "description": "Conduct experiments and explore scientific concepts",
        "schedule": "Thursdays, 3:45 PM - 5:15 PM",
        "max_participants": 22,
        "participants": ["ava@mergington.edu", "ethan@mergington.edu"]
    }
}


@app.get("/")
def root():
    return RedirectResponse(url="/static/index.html")


@app.get("/activities")
def get_activities():
    return activities


@app.post("/activities/{activity_name}/signup")
def signup_for_activity(activity_name: str, email: str):
    """Sign up a student for an activity"""
    # Validate activity exists
    if activity_name not in activities:
        raise HTTPException(status_code=404, detail="Activity not found")

    # Get the specific activity
    activity = activities[activity_name]

    normalized_email = normalize_email(email)
    if not normalized_email or "@" not in normalized_email:
        raise HTTPException(status_code=400, detail="Invalid email address")

    # Validate student is not already signed up
    if normalized_email in {normalize_email(participant) for participant in activity["participants"]}:
        raise HTTPException(status_code=400, detail="Student is already signed up for this activity")

    # Validate the activity has room for another participant
    if len(activity["participants"]) >= activity["max_participants"]:
        raise HTTPException(status_code=400, detail="Activity is full")

    # Add student
    activity["participants"].append(normalized_email)
    return {"message": f"Signed up {normalized_email} for {activity_name}"}


@app.delete("/activities/{activity_name}/signup/{email}")
def remove_participant(activity_name: str, email: str):
    """Remove a participant from an activity"""
    # Validate activity exists
    if activity_name not in activities:
        raise HTTPException(status_code=404, detail="Activity not found")

    # Get the specific activity
    activity = activities[activity_name]
    normalized_email = normalize_email(email)

    # Validate student is signed up
    normalized_participants = [normalize_email(participant) for participant in activity["participants"]]
    if normalized_email not in normalized_participants:
        raise HTTPException(status_code=404, detail="Participant not found in this activity")

    # Remove student
    for participant in list(activity["participants"]):
        if normalize_email(participant) == normalized_email:
            activity["participants"].remove(participant)
            break
    return {"message": f"Removed {normalized_email} from {activity_name}"}
