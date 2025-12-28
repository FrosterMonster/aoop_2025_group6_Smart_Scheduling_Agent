from src.tools.calendar import CalendarTool

# 1. Initialize Tool (Triggers Authentication Flow)
calendar = CalendarTool()
print(calendar) # Tests __str__ magic method

# 2. Test Creating an Event
print("Creating event...")
result = calendar.execute(
    action="create_event", 
    summary="AOOP Group 6 Meeting", 
    start_time="2025-10-25T10:00:00", 
    end_time="2025-10-25T11:00:00"
)
print(result)

# 3. Test Listing Events
print(calendar.execute(action="list_events"))