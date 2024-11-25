import streamlit as st
import pandas as pd
from datetime import datetime, timedelta

# Page title
st.title("Team Capacity Calendar - Baggle Pilot")

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

# Section 2: Configure sprints manually
st.header("Configure Sprints")
if "sprints" not in st.session_state:
    st.session_state["sprints"] = []

sprint_name = st.text_input("Sprint Name (e.g., Sprint 137)")
start_date = st.date_input("Sprint Start Date")
end_date = st.date_input("Sprint End Date")

if st.button("Add Sprint"):
    if start_date <= end_date:
        st.session_state["sprints"].append({"Sprint": sprint_name, "Start Date": start_date, "End Date": end_date})
        st.success(f"{sprint_name} added!")
    else:
        st.error("Start date must be before or equal to the end date.")

# Display sprints
if st.session_state["sprints"]:
    st.subheader("Sprints")
    sprints_df = pd.DataFrame(st.session_state["sprints"])
    st.dataframe(sprints_df)

# Section 3: Mark absences
st.header("Mark Absences")
if st.session_state["team"] and st.session_state["sprints"]:
    selected_member = st.selectbox("Select Team Member", [member["Name"] for member in st.session_state["team"]])
    selected_sprint = st.selectbox("Select Sprint", [sprint["Sprint"] for sprint in st.session_state["sprints"]])
    
    # Get selected sprint dates
    sprint_dates = [
        date for sprint in st.session_state["sprints"] 
        if sprint["Sprint"] == selected_sprint 
        for date in pd.date_range(sprint["Start Date"], sprint["End Date"])
    ]
    absence_days = st.multiselect("Select Absence Days", [date.strftime("%Y-%m-%d") for date in sprint_dates])

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

# Section 4: Calculate sprint capacity
st.header("Sprint Capacity")
if st.session_state["team"] and st.session_state["sprints"]:
    capacity_summary = []
    for sprint in st.session_state["sprints"]:
        sprint_name = sprint["Sprint"]
        sprint_dates = pd.date_range(sprint["Start Date"], sprint["End Date"])
        total_days = len(sprint_dates)
        
        sprint_total = 0
        for member in st.session_state["team"]:
            member_name = member["Name"]
            absent_days = len(st.session_state["absences"].get((member_name, sprint_name), []))
            available_days = total_days - absent_days
            sprint_total += available_days
            capacity_summary.append({"Sprint": sprint_name, "Member": member_name, "Available Days": available_days})
        
        # Add total capacity for the sprint
        capacity_summary.append({"Sprint": sprint_name, "Member": "TOTAL", "Available Days": sprint_total})
    
    capacity_df = pd.DataFrame(capacity_summary)
    st.dataframe(capacity_df[capacity_df["Member"] == "TOTAL"])
