#!/usr/bin/env python3
"""
整合排程測試 - 測試完整的排程流程

測試從 NLP 解析 → Calendar Service → Scheduling Engine 的完整流程
包括：
1. 固定時間排程
2. 彈性排程（找空檔）
3. 衝突檢測
4. Energy Pattern 考量
"""

import os
import sys
from datetime import datetime, timedelta
import pytz

# Set DRY_RUN mode for testing
os.environ['DRY_RUN'] = '1'

from ai_schedule_agent.core.nlp_processor import NLPProcessor
from ai_schedule_agent.integrations.calendar_service import CalendarService
from ai_schedule_agent.models.event import Event, EventType
from ai_schedule_agent.utils.logging import logger

# Timezone
TZ = pytz.timezone('Asia/Taipei')


class IntegrationTester:
    """整合測試器"""

    def __init__(self):
        self.nlp = NLPProcessor(use_llm=False)  # Use Mock Mode
        self.calendar = CalendarService()
        self.test_events = []  # Track created events for cleanup

    def setup_test_calendar(self):
        """準備測試用日曆 - 建立一些已存在的事件"""
        print("\n📅 準備測試日曆...")
        print("-" * 80)

        now = datetime.now(TZ)
        tomorrow = now + timedelta(days=1)

        # 明天已有的事件
        existing_events = [
            {
                'title': '晨會',
                'start': tomorrow.replace(hour=9, minute=0, second=0, microsecond=0),
                'duration': 60,  # 9:00-10:00
            },
            {
                'title': '專案討論',
                'start': tomorrow.replace(hour=14, minute=0, second=0, microsecond=0),
                'duration': 120,  # 14:00-16:00
            },
            {
                'title': '下班前檢討',
                'start': tomorrow.replace(hour=17, minute=0, second=0, microsecond=0),
                'duration': 30,  # 17:00-17:30
            },
        ]

        for event_data in existing_events:
            start = event_data['start']
            end = start + timedelta(minutes=event_data['duration'])
            event = Event(
                title=event_data['title'],
                event_type=EventType.MEETING,
                start_time=start,
                end_time=end
            )
            result = self.calendar.create_event(event)
            if result['success']:
                print(f"  ✅ 建立: {event_data['title']} "
                      f"({event_data['start'].strftime('%H:%M')}-"
                      f"{(event_data['start'] + timedelta(minutes=event_data['duration'])).strftime('%H:%M')})")
            else:
                print(f"  ❌ 失敗: {event_data['title']}")

        # 顯示明天的空檔
        print(f"\n明天 ({tomorrow.strftime('%Y-%m-%d')}) 的空檔:")
        self._show_free_slots(tomorrow)

    def _show_free_slots(self, target_date):
        """顯示指定日期的空檔"""
        start_of_day = target_date.replace(hour=8, minute=0, second=0, microsecond=0)
        end_of_day = target_date.replace(hour=18, minute=0, second=0, microsecond=0)

        free_slots = self.calendar.find_free_slots(
            start_time=start_of_day,
            end_time=end_of_day,
            min_duration_minutes=30
        )

        if free_slots:
            for i, slot in enumerate(free_slots, 1):
                start = slot['start']
                end = slot['end']
                duration = int((end - start).total_seconds() / 60)
                print(f"  {i}. {start.strftime('%H:%M')}-{end.strftime('%H:%M')} ({duration}分鐘)")
        else:
            print("  無空檔")

    def test_fixed_time_scheduling(self):
        """測試 1: 固定時間排程"""
        print("\n" + "=" * 80)
        print("測試 1: 固定時間排程")
        print("=" * 80)

        test_cases = [
            {
                'input': '明天上午11點開會，1小時',
                'description': '排在空檔 (10:00-14:00 之間)'
            },
            {
                'input': '明天下午2點討論專案',
                'description': '衝突！已有事件 (14:00-16:00)'
            },
            {
                'input': '明天中午12點午餐會，30分鐘',
                'description': '排在空檔'
            },
        ]

        for i, test_case in enumerate(test_cases, 1):
            print(f"\nTest {i}: {test_case['input']}")
            print(f"說明: {test_case['description']}")
            print("-" * 80)

            # 1. NLP 解析
            parsed = self.nlp.parse_scheduling_request(test_case['input'])
            print(f"✓ NLP 解析:")
            print(f"  標題: {parsed.get('title')}")
            print(f"  時間: {parsed.get('datetime')}")
            print(f"  時長: {parsed.get('duration')} 分鐘")

            # 2. 建立 Event
            if parsed.get('datetime'):
                start = parsed['datetime']
                duration = parsed.get('duration', 60)
                end = start + timedelta(minutes=duration)
                event = Event(
                    title=parsed['title'],
                    event_type=EventType.MEETING,
                    start_time=start,
                    end_time=end
                )

                # 3. 衝突檢測
                conflicts = self.calendar.check_conflicts(
                    event.start_time,
                    event.end_time
                )

                if conflicts:
                    print(f"\n  ⚠️  衝突檢測: 發現 {len(conflicts)} 個衝突")
                    for conflict in conflicts:
                        print(f"    - {conflict.get('summary')} "
                              f"({conflict.get('start', {}).get('dateTime', 'N/A')})")
                else:
                    print(f"\n  ✓ 衝突檢測: 無衝突")

                    # 4. 建立事件
                    result = self.calendar.create_event(event)
                    if result['success']:
                        print(f"  ✅ 成功建立事件")
                        self.test_events.append(result['event_id'])
                    else:
                        print(f"  ❌ 建立失敗: {result.get('error')}")
            else:
                print("  ⚠️  無法解析時間")

    def test_flexible_scheduling(self):
        """測試 2: 彈性排程（找空檔）"""
        print("\n" + "=" * 80)
        print("測試 2: 彈性排程（自動找空檔）")
        print("=" * 80)

        test_cases = [
            {
                'input': '明天上午排2小時開會',
                'description': '上午空檔: 10:00-14:00 (4小時)，應選擇上午時段'
            },
            {
                'input': '明天下午安排1小時面試',
                'description': '下午空檔: 16:00-17:00 (1小時)，應選擇這個時段'
            },
            {
                'input': '明天排3小時培訓',
                'description': '需要連續3小時，上午有4小時空檔可用'
            },
        ]

        for i, test_case in enumerate(test_cases, 1):
            print(f"\nTest {i}: {test_case['input']}")
            print(f"說明: {test_case['description']}")
            print("-" * 80)

            # 1. NLP 解析
            parsed = self.nlp.parse_scheduling_request(test_case['input'])
            print(f"✓ NLP 解析:")
            print(f"  標題: {parsed.get('title')}")
            print(f"  時長: {parsed.get('duration')} 分鐘")
            print(f"  目標日期: {parsed.get('target_date')}")
            print(f"  時段偏好: {parsed.get('time_preference')}")

            # 2. 檢查是否為彈性排程
            is_flexible = (parsed.get('time_preference') is not None
                          and not parsed.get('datetime'))

            if is_flexible and parsed.get('target_date'):
                print(f"\n  🔸 彈性排程模式")

                target_date = parsed['target_date']
                duration = parsed.get('duration', 60)
                time_pref = parsed.get('time_preference', {})
                period = time_pref.get('period')
                start_hour = time_pref.get('start_hour', 8)
                end_hour = time_pref.get('end_hour', 18)

                # 3. 找空檔
                search_start = datetime.combine(target_date, datetime.min.time())
                search_start = TZ.localize(search_start.replace(hour=start_hour))
                search_end = TZ.localize(search_start.replace(hour=end_hour))

                free_slots = self.calendar.find_free_slots(
                    start_time=search_start,
                    end_time=search_end,
                    min_duration_minutes=duration
                )

                if free_slots:
                    print(f"\n  ✓ 找到 {len(free_slots)} 個符合的空檔:")
                    for j, slot in enumerate(free_slots, 1):
                        slot_start = slot['start']
                        slot_end = slot['end']
                        slot_duration = int((slot_end - slot_start).total_seconds() / 60)
                        print(f"    {j}. {slot_start.strftime('%H:%M')}-{slot_end.strftime('%H:%M')} "
                              f"({slot_duration}分鐘)")

                    # 4. 選擇最佳時段（這裡簡單選第一個）
                    best_slot = free_slots[0]
                    selected_start = best_slot['start']

                    print(f"\n  🎯 選擇時段: {selected_start.strftime('%H:%M')}")
                    print(f"     原因: {period} 時段的第一個可用空檔")

                    # 5. 建立事件
                    selected_end = selected_start + timedelta(minutes=duration)
                    event = Event(
                        title=parsed['title'],
                        event_type=EventType.MEETING,
                        start_time=selected_start,
                        end_time=selected_end
                    )

                    result = self.calendar.create_event(event)
                    if result['success']:
                        print(f"\n  ✅ 成功建立彈性排程事件")
                        self.test_events.append(result['event_id'])
                    else:
                        print(f"\n  ❌ 建立失敗: {result.get('error')}")
                else:
                    print(f"\n  ⚠️  找不到符合的空檔（需要 {duration} 分鐘）")
            else:
                print(f"\n  ⚠️  非彈性排程或缺少目標日期")

    def test_calendar_query(self):
        """測試 3: 查詢日曆"""
        print("\n" + "=" * 80)
        print("測試 3: 查詢日曆")
        print("=" * 80)

        now = datetime.now(TZ)
        tomorrow = now + timedelta(days=1)

        # 查詢明天的所有事件
        start_of_day = tomorrow.replace(hour=0, minute=0, second=0, microsecond=0)
        end_of_day = tomorrow.replace(hour=23, minute=59, second=59, microsecond=0)

        print(f"\n查詢 {tomorrow.strftime('%Y-%m-%d')} 的所有事件:")
        print("-" * 80)

        events = self.calendar.get_events_in_range(start_of_day, end_of_day)

        if events:
            for i, event in enumerate(events, 1):
                start = event.get('start', {})
                end = event.get('end', {})
                start_time = start.get('dateTime', 'N/A')
                end_time = end.get('dateTime', 'N/A')

                if start_time != 'N/A':
                    start_dt = datetime.fromisoformat(start_time.replace('Z', '+00:00'))
                    start_local = start_dt.astimezone(TZ)
                    print(f"{i}. {event.get('summary')} ({start_local.strftime('%H:%M')})")
                else:
                    print(f"{i}. {event.get('summary')} (全天)")
        else:
            print("無事件")

    def cleanup(self):
        """清理測試事件"""
        print("\n" + "=" * 80)
        print("清理測試事件")
        print("=" * 80)

        if self.test_events:
            for event_id in self.test_events:
                result = self.calendar.delete_event(event_id)
                if result['success']:
                    print(f"  ✅ 刪除事件: {event_id}")
                else:
                    print(f"  ❌ 刪除失敗: {event_id}")
        else:
            print("  無測試事件需清理")

    def run_all_tests(self):
        """執行所有測試"""
        print("=" * 80)
        print("🧪 整合排程測試")
        print("=" * 80)
        print("\n測試目標:")
        print("  1. NLP 解析 → Event 建立 → Calendar Service")
        print("  2. 衝突檢測")
        print("  3. 彈性排程（自動找空檔）")
        print("  4. 查詢日曆")

        try:
            # 準備測試環境
            self.setup_test_calendar()

            # 執行測試
            self.test_fixed_time_scheduling()
            self.test_flexible_scheduling()
            self.test_calendar_query()

            print("\n" + "=" * 80)
            print("✅ 測試完成")
            print("=" * 80)

        except Exception as e:
            print(f"\n❌ 測試過程中發生錯誤: {e}")
            import traceback
            traceback.print_exc()

        finally:
            # 清理
            # self.cleanup()  # 注意：DRY_RUN 模式不會真的建立事件，所以清理可能失敗
            pass


def main():
    """主函數"""
    tester = IntegrationTester()
    tester.run_all_tests()

    print("\n" + "=" * 80)
    print("💡 測試說明")
    print("=" * 80)
    print("""
這個測試驗證了以下功能：

✅ 已測試:
1. NLP 解析（Mock Mode）
   - 固定時間: "明天上午11點開會，1小時"
   - 彈性時間: "明天上午排2小時開會"

2. Calendar Service
   - 建立事件
   - 查詢事件
   - 找空檔 (find_free_slots)
   - 衝突檢測

3. 基本整合流程
   - 解析 → 建立 Event → Calendar API

⏳ 待完成（需要更新 scheduling_engine.py）:
1. Scheduling Engine 整合
   - 使用 find_free_slots() 替代現有邏輯
   - Energy Pattern 評分
   - 智能時段選擇

2. 完整的彈性排程
   - 多日搜尋
   - 優先級考量
   - 分段任務支持

注意：當前測試在 DRY_RUN 模式下運行，不會真的建立 Google Calendar 事件。
""")


if __name__ == '__main__':
    main()
