# Supported Input Scenarios

This document lists all the different types of natural language inputs the AI Schedule Agent can handle.

## 📅 1. CREATE/SCHEDULE Actions

### 1.1 Direct Scheduling (with specific time)
- "Schedule a meeting tomorrow at 3pm"
- "Meeting 11/27 at 9pm for 3 hrs at NYCU"
- "Book team lunch Friday at noon"
- "Set up dentist appointment next Tuesday 2pm for 1 hour"
- "Add interview with candidate Thursday 10:00am"

### 1.2 Smart Scheduling (find optimal time)
- "Schedule a 4hours study session on 11/7 for aoop"
- "Need to meet with team sometime next week"
- "Block time for project work"
- "Schedule coffee chat with Mark soon"
- "Find time for 2-hour workshop this week"

### 1.3 Multi-Event Scheduling
- "Schedule 3 interviews tomorrow at 10am, 2pm, and 4pm"
- "Block out Monday through Wednesday for focus time"
- "Book meeting rooms for all my meetings next week"
- "Create 5 study sessions this week, 2 hours each"

## 🔍 2. QUERY/SEARCH Actions

### 2.1 Show Schedule
- "What's on my calendar tomorrow?"
- "Show me my schedule for next week"
- "What do I have today?"
- "Display Friday's agenda"
- "What's coming up?"

### 2.2 Find Specific Event
- "When is my meeting with Alex?"
- "Find my dentist appointment"
- "What time is the team standup?"
- "When am I meeting with the client?"
- "Show my interview with John"

### 2.3 Check Availability
- "Am I free Friday afternoon?"
- "Do I have anything scheduled this afternoon?"
- "Am I busy next week?"
- "Is there time available on Monday morning?"
- "Can I fit a 2-hour meeting tomorrow?"

### 2.4 List Events
- "Show all my meetings this week"
- "List all events with Alex"
- "What meetings do I have at NYCU?"
- "Show my focus time blocks"

## ✏️ 3. EDIT/MODIFY Actions

### 3.1 Change Time
- "Move my 3pm meeting to 4pm"
- "Reschedule tomorrow's standup to 10am"
- "Change the dentist appointment to next week"

### 3.2 Change Duration
- "Make my lunch meeting 30 minutes longer"
- "Extend the workshop by 1 hour"
- "Shorten tomorrow's meeting to 30 minutes"

### 3.3 Change Location
- "Change tomorrow's meeting location to Zoom"
- "Move the team lunch to Building A"
- "Make my 2pm meeting virtual"

### 3.4 Change Participants
- "Add Sarah to my 2pm meeting"
- "Invite Alex to tomorrow's standup"
- "Remove John from the project meeting"
- "Add mark@email.com to Friday's workshop"

### 3.5 Multiple Changes
- "Move my 3pm meeting to 4pm and add Alex"
- "Change location to Zoom and extend by 30 minutes"

## 🔄 4. MOVE/RESCHEDULE Actions

### 4.1 Simple Reschedule
- "Move my morning meeting to afternoon"
- "Reschedule my 3pm to tomorrow"
- "Push back my dentist appointment by one week"

### 4.2 Relative Rescheduling
- "Move everything after 3pm to tomorrow"
- "Reschedule next week same time"
- "Move to the day after"

### 4.3 Conditional Rescheduling
- "Move my meeting to when both Sarah and I are free"
- "Reschedule to avoid Monday mornings"

## 🗑️ 5. DELETE/CANCEL Actions

### 5.1 Delete Single Event
- "Cancel my 3pm meeting"
- "Delete tomorrow's team standup"
- "Remove my dentist appointment"
- "Cancel the interview with John"

### 5.2 Bulk Delete
- "Clear my schedule for Friday afternoon"
- "Remove all meetings with John"
- "Cancel all events next Monday"
- "Delete my focus time blocks this week"

## 💬 6. CONVERSATIONAL/CHAT

### 6.1 Questions
- "How does scheduling work?"
- "What can you do?"
- "Help me understand my calendar"

### 6.2 Confirmations
- "Thanks!"
- "That looks good"
- "Yes, schedule it"

### 6.3 Clarifications
- "No, I meant 3pm not 3am"
- "Actually, make it 2 hours"
- "Change that to next Tuesday"

## 🎯 7. COMPLEX/CONDITIONAL Scenarios

### 7.1 Smart Constraints
- "Schedule a meeting but avoid Mondays"
- "Find time after my current meeting ends"
- "Book before my 5pm deadline"
- "Schedule when Sarah is also available"

### 7.2 Context-Based
- "Schedule another meeting like the last one"
- "Same time next week"
- "Repeat this meeting every Friday"

### 7.3 Flexible/Vague
- "I need to meet with the team sometime"
- "Schedule a quick sync"
- "Block some time for work"

## 📊 8. SUPPORTED TIME FORMATS

### Date Formats
- **Absolute**: "11/27", "2025-11-07", "November 27"
- **Relative**: "tomorrow", "next week", "in 3 days"
- **Weekdays**: "Monday", "next Friday", "this Tuesday"
- **Patterns**: "next week monday", "11/21"

### Time Formats
- **12-hour**: "3pm", "9:30am", "noon"
- **24-hour**: "15:00", "21:30"
- **Chinese**: "下午2點", "晚上8點"
- **Relative**: "morning", "afternoon", "evening"

### Duration Formats
- "3 hours", "4 hrs", "90 minutes", "2.5 hours"
- "for 3 hours", "3 hr session"

## 🌐 9. LANGUAGE SUPPORT

### English
- Full natural language support
- Informal: "grab coffee", "quick sync", "catch up"
- Formal: "schedule meeting", "book appointment"

### Chinese (繁體中文)
- Time expressions: "明天", "下週", "今天下午"
- Time formats: "下午2點", "晚上8點"
- Actions: "安排會議", "預約"

## ⚠️ 10. EDGE CASES & SPECIAL SCENARIOS

### 10.1 Ambiguous Times
- "Schedule meeting tomorrow" → System will find optimal time
- "Meet with Alex soon" → System suggests available slots

### 10.2 Conflicting Events
- System automatically detects conflicts
- Suggests alternative times
- Can move lower-priority events

### 10.3 Missing Information
- "Schedule a meeting" → System asks for details
- "Move my meeting" → System identifies which meeting

### 10.4 Multi-Step Operations
- "Cancel my 2pm and schedule a new one with both teams"
- "Move everything after 3pm to tomorrow"
- "Combine my two morning meetings into one"

## 🚀 11. ADVANCED FEATURES

### 11.1 Smart Time Finding
- LLM analyzes your full calendar
- Considers break times and productivity patterns
- Avoids back-to-back meetings
- Respects working hours

### 11.2 Iterative Search
- If no slot found on target date, checks next days
- Up to 3 attempts for flexible requests
- Expands search window automatically

### 11.3 Context Awareness
- Remembers recent conversations
- Understands references ("that meeting", "the interview")
- Learns from your preferences

## 📝 EXAMPLES BY USE CASE

### Student Schedule
```
"Schedule study session for AOOP on 11/7 4 hours"
"Block time for project work this week"
"When is my next class?"
"Cancel Friday's study group"
```

### Work Schedule
```
"Meeting with client tomorrow at 2pm at office"
"Schedule 1-on-1 with Sarah next week"
"Show my meetings with the engineering team"
"Move all Monday meetings to Tuesday"
```

### Personal Schedule
```
"Dentist appointment next Tuesday 2pm"
"Lunch with mom on Saturday noon"
"When is my yoga class?"
"Cancel gym session tomorrow"
```

---

## 📌 Implementation Status

| Feature Category | Status | Notes |
|-----------------|--------|-------|
| Direct Scheduling | ✅ Fully Implemented | With specific times |
| Smart Scheduling | ✅ Fully Implemented | LLM-powered optimal time finding |
| Query/Search | ✅ Schema Ready | UI integration pending |
| Edit/Modify | ✅ Schema Ready | UI integration pending |
| Move/Reschedule | ✅ Schema Ready | UI integration pending |
| Delete/Cancel | ✅ Schema Ready | UI integration pending |
| Multi-Schedule | ✅ Schema Ready | UI integration pending |
| Conversational | ✅ Fully Implemented | Chat mode supported |

**Note**: All action handlers are implemented in the NLP processor. UI integration is the next step to make query/edit/delete/move/multi-schedule actions fully functional in the interface.
