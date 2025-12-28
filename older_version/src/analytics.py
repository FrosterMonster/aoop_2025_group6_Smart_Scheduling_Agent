import sqlite3
import pandas as pd
import random
from datetime import datetime, timedelta
from src.database import DB_PATH

class AnalyticsEngine:
    def __init__(self):
        # 確保資料庫路徑是正確的，這裡直接引用 src.database 的設定
        self.db_path = DB_PATH

    def get_raw_data(self):
        """從資料庫讀取偏好設定 (作為範例)"""
        try:
            conn = sqlite3.connect(self.db_path)
            # 嘗試讀取資料，如果資料表不存在會報錯，我們做個防呆
            df = pd.read_sql_query("SELECT * FROM preferences", conn)
            conn.close()
            return df
        except Exception:
            # 如果讀不到資料，回傳空的 DataFrame
            return pd.DataFrame()

    def generate_mock_stats(self):
        """
        生成模擬的生產力報告數據。
        """
        # 1. 模擬過去 7 天的會議數量 (週一到週日)
        dates = [(datetime.now() - timedelta(days=i)).strftime("%a") for i in range(6, -1, -1)]
        meeting_counts = [random.randint(0, 5) for _ in range(7)]
        
        # 2. 模擬會議類型分佈
        categories = ["Client Meeting", "Internal Sync", "Focus Time", "Lunch", "Brainstorming"]
        type_counts = [random.randint(10, 40) for _ in range(5)]
        
        # 3. 計算 '生產力分數' (簡單的假邏輯)
        productivity_score = sum(meeting_counts) * 5 + random.randint(10, 20)
        if productivity_score > 99: productivity_score = 99
        if productivity_score < 40: productivity_score = 60

        return {
            "weekly_trend": pd.DataFrame({"Day": dates, "Meetings": meeting_counts}),
            "category_dist": pd.DataFrame({"Category": categories, "Count": type_counts}),
            "productivity_score": productivity_score,
            "total_meetings": sum(meeting_counts)
        }