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
    "Soccer Team": {
        "description": "Competitive soccer team practicing drills and playing matches",
        "schedule": "Daily practice: Mondays - Fridays, 4:00 PM - 6:00 PM; Matches on Saturdays",
        "max_participants": 22,
        "participants": ["liam@mergington.edu", "noah@mergington.edu"]
    },
    "Track and Field": {
        "description": "Training for sprints, distance, jumps and throws; attends meets",
        "schedule": "Tuesdays and Thursdays, 4:00 PM - 5:30 PM; Meets on selected weekends",
        "max_participants": 28,
        "participants": ["ava@mergington.edu", "isabella@mergington.edu"]
    },
    "Art Club": {
        "description": "Explore drawing, painting, and mixed media projects",
        "schedule": "Wednesdays, 3:30 PM - 5:00 PM",
        "max_participants": 18,
        "participants": ["mia@mergington.edu", "charlotte@mergington.edu"]
    },
    "Drama Club": {
        "description": "Acting, stagecraft, and producing school plays",
        "schedule": "Mondays and Thursdays, 4:00 PM - 6:00 PM",
        "max_participants": 25,
        "participants": ["amelia@mergington.edu", "harper@mergington.edu"]
    },
    "Robotics Club": {
        "description": "Design and build robots, participate in competitions",
        "schedule": "Tuesdays, 4:00 PM - 6:00 PM; Saturdays for workshops",
        "max_participants": 16,
        "participants": ["oliver@mergington.edu", "elijah@mergington.edu"]
    },
    "Debate Team": {
        "description": "Practice argumentation, public speaking, and competitive debate",
        "schedule": "Wednesdays and Fridays, 3:30 PM - 5:00 PM",
        "max_participants": 14,
        "participants": ["grace@mergington.edu", "lucas@mergington.edu"]
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
        raise HTTPException(status_code=404, detail="Actividad no encontrada")

    # Get the specific activity
    activity = activities[activity_name]

    # Validate student is not already signed up
    if email in activity["participants"]:
        raise HTTPException(status_code=400, detail="El estudiante ya está inscrito")

    # Optional: validate capacity
    if len(activity["participants"]) >= activity["max_participants"]:
        raise HTTPException(status_code=400, detail="La actividad está llena")

    # Add student
    activity["participants"].append(email)
    return {"message": f"Se ha inscrito {email} en {activity_name}"}


@app.delete("/activities/{activity_name}/participants")
def unregister_from_activity(activity_name: str, email: str):
    """Unregister a student from an activity by email (query param `email`)."""
    # Validate activity exists
    if activity_name not in activities:
        raise HTTPException(status_code=404, detail="Actividad no encontrada")

    activity = activities[activity_name]

    # Validate student is signed up
    if email not in activity["participants"]:
        raise HTTPException(status_code=404, detail="El estudiante no está inscrito en esta actividad")

    # Remove student
    activity["participants"].remove(email)
    return {"message": f"Se ha dado de baja a {email} de {activity_name}"}
