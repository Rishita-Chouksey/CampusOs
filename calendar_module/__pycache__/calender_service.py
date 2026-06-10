from database import (
    add_event,
    get_events,
    delete_event,
    update_event,
    get_events_by_date,
    get_upcoming_events
)


# --------------------------
# Add Event
# --------------------------

def calendar_add(
    title,
    subject,
    date,
    time,
    event_type,
    reminder
):

    add_event(
        title,
        subject,
        date,
        time,
        event_type,
        reminder
    )

    return {
        "status": True,
        "message": "Event Added Successfully"
    }


# --------------------------
# View All Events
# --------------------------

def calendar_view():

    events = get_events()

    return events


# --------------------------
# Delete Event
# --------------------------

def calendar_delete(event_id):

    delete_event(event_id)

    return {
        "status": True,
        "message": "Event Deleted"
    }


# --------------------------
# Update Event
# --------------------------

def calendar_update(

    event_id,

    title,

    subject,

    date,

    time,

    event_type,

    reminder

):

    update_event(

        event_id,

        title,

        subject,

        date,

        time,

        event_type,

        reminder

    )

    return {

        "status": True,

        "message": "Event Updated"

    }


# --------------------------
# Get Events By Date
# --------------------------

def calendar_date(date):

    events = get_events_by_date(date)

    return events


# --------------------------
# Upcoming Events
# --------------------------

def calendar_upcoming():

    events = get_upcoming_events()

    return events