import sqlite3
import pandas as pd
import random
from datetime import datetime, timedelta
from src.database import DB_PATH

class AnalyticsEngine:
    def __init__(self):
        self.db_path = DB_PATH

    def get_raw_data(self):
        """從資料庫讀取偏好設定 (作為範例)"""
        conn = sqlite3.connect(self.db_path)
        df = pd.read_sql_query("SELECT * FROM preferences", conn)
        conn.close()
        return df

    def generate_mock_stats(self):
        """
        因為我們可能沒有足夠的真實會議數據，
        這裡我們編寫一個算法來生成 '模擬' 的生產力報告。
        這展示了你的數據處理能力。
        """
        # 1. 模擬過去 7 天的會議數量
        dates = [(datetime.now() - timedelta(days=i)).strftime("%a") for i in range(6, -1, -1)]
        meeting_counts = [random.randint(0, 5) for _ in range(7)]
        
        # 2. 模擬會議類型分佈
        categories = ["Client Meeting", "Internal Sync", "Focus Time", "Lunch", "Brainstorming"]
        type_counts = [random.randint(10, 40) for _ in range(5)]
        
        # 3. 計算 '生產力分數' (複雜的假邏輯)
        productivity_score = sum(meeting_counts) * 5 + random.randint(10, 20)
        if productivity_score > 100: productivity_score = 99

        return {
            "weekly_trend": pd.DataFrame({"Day": dates, "Meetings": meeting_counts}),
            "category_dist": pd.DataFrame({"Category": categories, "Count": type_counts}),
            "productivity_score": productivity_score,
            "total_meetings": sum(meeting_counts)
        }