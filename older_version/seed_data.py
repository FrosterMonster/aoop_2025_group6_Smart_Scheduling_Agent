from src.database import init_db, set_preference
from src.logger import log_info

def seed_database():
    """
    這是一個 Utility Script，用來快速填充資料庫，
    讓 Demo 看起來內容豐富。
    """
    init_db()
    log_info("🌱 Seeding database with initial data...")

    dummy_prefs = {
        "work_start": "09:00 AM",
        "work_end": "06:00 PM",
        "lunch_break": "12:00 PM - 01:00 PM",
        "meeting_preference": "No meetings on Friday afternoon",
        "theme": "Dark Mode",
        "notification_level": "High",
        "default_meeting_duration": "30 minutes"
    }

    for key, value in dummy_prefs.items():
        set_preference(key, value)
        log_info(f"   Saved preference: {key} -> {value}")

    log_info("✅ Database seeding complete!")

if __name__ == "__main__":
    seed_database()