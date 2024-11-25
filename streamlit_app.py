import streamlit as st
import pandas as pd
import numpy as np
from datetime import datetime, timedelta

# Page title
st.title("Team Capacity Calendar")

# Section 1: Add team members
st.header("Add Team Members")
with st.form("team_form"):
    name = st.text_input("Member Name")
    role = st.selectbox("Role", ["TL", "Dev Front", "Dev Back", "QA"])
    add_member = st.form_submit_button("Add Member")

# Store team data
if "team" not in st.session_state:
    st.session_state["team"] = []

if add_member and name:
    st.session_state["team"].append({"Name": name, "Role": role})
    st.success(f"{name} added to the team!")

# Display team
if st.session_state["team"]:
    st.subheader("Team Members")
    team_df = pd.DataFrame(st.session_state["team"])
    st.dataframe(team_df)

# Section 2: Configure calendar
st.header("Sprint Calendar")
start_date = st.date_input("Sprint Start Date", value=datetime.today())
num_sprints = st.number_input("Number of Sprints", min_value=1, max_value=10, value=2)
sprint_length = st.number_input("Sprint Length (days)", min_value=1, max_value=30, value=15)

# Generate sprint dates
sprints = {}
for i in range(num_sprints):
    sprint_start = start_date + timedelta(days=i * sprint_length)
    sprint_end = sprint_start + timedelta(days=sprint_length - 1)
    sprints[f"Sprint {i+1}"] = pd.date_range(sprint_start, sprint_end)

# Section 3: Mark absences
st.header("Mark Absences")
if st.session_state["team"]:
    selected_member = st.selectbox("Select Team Member", [member["Name"] for member in st.session_state["team"]])
    selected_sprint = st.selectbox("Select Sprint", list(sprints.keys()))
    absence_days = st.multiselect(
        "Select Absence Days",
        sprints[selected_sprint].strftime("%Y-%m-%d").tolist()
    )
    if st.button("Save Absences"):
        if "absences" not in st.session_state:
            st.session_state["absences"] = {}
        st.session_state["absences"][(selected_member, selected_sprint)] = absence_days
        st.success(f"Absences saved for {selected_member} in {selected_sprint}!")

# Display absence summary
if "absences" in st.session_state:
    st.subheader("Absence Summary")
    absences_df = pd.DataFrame(
        [
            {"Member": key[0], "Sprint": key[1], "Days Absent": ", ".join(value)}
            for key, value in st.session_state["absences"].items()
        ]
    )
    st.dataframe(absences_df)

# Section 4: Calculate capacity
st.header("Sprint Capacity")
if st.session_state["team"] and "absences" in st.session_state:
    capacity_summary = []
    for sprint, dates in sprints.items():
        for member in st.session_state["team"]:
            member_name = member["Name"]
            total_days = len(dates)
            absent_days = len(st.session_state["absences"].get((member_name, sprint), []))
            available_days = total_days - absent_days
            capacity_summary.append({"Sprint": sprint, "Member": member_name, "Available Days": available_days})

    capacity_df = pd.DataFrame(capacity_summary)
    st.dataframe(capacity_df)
