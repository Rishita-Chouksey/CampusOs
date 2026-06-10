import streamlit as st
from database import add_event, get_events, delete_event

st.set_page_config(
    page_title="CampusOS Calendar",
    page_icon="📅",
    layout="wide"
)

st.title("📅 CampusOS Calendar")
st.markdown("Manage your academic events with AI-powered scheduling.")

# -----------------------------
# Add Event Form
# -----------------------------

st.subheader("➕ Add Event")

with st.form("event_form"):

    title = st.text_input("Title")
    subject = st.text_input("Subject")

    date = st.date_input("Event Date")

    time = st.time_input("Event Time")

    event_type = st.selectbox(
        "Event Type",
        ["Quiz", "Assignment", "Exam", "Lab", "Meeting", "Personal"]
    )

    reminder = st.selectbox(
        "Reminder",
        ["Yes", "No"]
    )

    submit = st.form_submit_button("Add Event")

    if submit:

        add_event(
            title,
            subject,
            str(date),
            str(time),
            event_type,
            reminder
        )

        st.success("✅ Event Added Successfully")

# -----------------------------
# View Events
# -----------------------------

st.subheader("📋 All Events")

events = get_events()

if len(events) == 0:

    st.info("No events available.")

else:

    for event in events:

        event_id = event[0]

        st.markdown("---")

        col1, col2 = st.columns([4, 1])

        with col1:

            st.write(f"### {event[1]}")
            st.write(f"📚 Subject: {event[2]}")
            st.write(f"📅 Date: {event[3]}")
            st.write(f"⏰ Time: {event[4]}")
            st.write(f"🏷 Type: {event[5]}")
            st.write(f"🔔 Reminder: {event[6]}")

        with col2:

            if st.button(
                "🗑 Delete",
                key=f"delete_{event_id}"
            ):

                delete_event(event_id)
                st.rerun()