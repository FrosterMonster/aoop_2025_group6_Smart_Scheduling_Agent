#!/usr/bin/env python3
"""
阿嚕米整合測試

這個腳本測試重構後的 ai_schedule_agent 是否正確整合了阿嚕米_archived的邏輯
"""

import os
import sys
import logging
from datetime import datetime, timedelta

# 設定 DRY_RUN 模式（不實際寫入 Google Calendar）
os.environ['DRY_RUN'] = '1'

# 設定日誌
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s [%(levelname)s] %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S'
)

logger = logging.getLogger(__name__)


def test_calendar_service():
    """測試 1: CalendarService 初始化"""
    print("\n" + "="*70)
    print("測試 1: CalendarService 初始化")
    print("="*70)

    try:
        from ai_schedule_agent.integrations.calendar_service import CalendarService

        service = CalendarService(
            token_file='.config/token.pickle',
            credentials_file='.config/credentials.json'
        )

        logger.info("✓ CalendarService 導入成功")
        logger.info(f"✓ Token file: {service.token_file}")
        logger.info(f"✓ Credentials file: {service.credentials_file}")

        print("\n✅ 測試 1 通過\n")
        return True

    except Exception as e:
        logger.error(f"✗ 測試 1 失敗: {e}")
        print("\n❌ 測試 1 失敗\n")
        return False


def test_calendar_tools():
    """測試 2: calendar_tools 核心函數"""
    print("\n" + "="*70)
    print("測試 2: calendar_tools 核心函數")
    print("="*70)

    try:
        from ai_schedule_agent.integrations.calendar_tools import (
            create_calendar_event,
            get_busy_periods,
            find_free_slots_between,
            plan_week_schedule
        )

        # 測試 create_calendar_event
        now = datetime.now()
        start = now + timedelta(minutes=30)
        end = now + timedelta(minutes=90)

        result = create_calendar_event(
            summary="測試事件",
            description="整合測試",
            start_time_str=start.strftime('%Y-%m-%d %H:%M:%S'),
            end_time_str=end.strftime('%Y-%m-%d %H:%M:%S')
        )

        logger.info(f"✓ create_calendar_event 執行成功")
        logger.info(f"  結果: {result[:80]}...")

        print("\n✅ 測試 2 通過\n")
        return True

    except Exception as e:
        logger.error(f"✗ 測試 2 失敗: {e}")
        import traceback
        traceback.print_exc()
        print("\n❌ 測試 2 失敗\n")
        return False


def test_calendar_integration():
    """測試 3: CalendarIntegration 類別"""
    print("\n" + "="*70)
    print("測試 3: CalendarIntegration 類別")
    print("="*70)

    try:
        from ai_schedule_agent.integrations.google_calendar import CalendarIntegration

        calendar = CalendarIntegration()

        logger.info("✓ CalendarIntegration 初始化成功")
        logger.info(f"✓ 使用阿嚕米的 CalendarService: {calendar._calendar_service}")

        print("\n✅ 測試 3 通過\n")
        return True

    except Exception as e:
        logger.error(f"✗ 測試 3 失敗: {e}")
        import traceback
        traceback.print_exc()
        print("\n❌ 測試 3 失敗\n")
        return False


def test_plan_week_schedule():
    """測試 4: 智能週排程"""
    print("\n" + "="*70)
    print("測試 4: 智能週排程 (阿嚕米核心功能)")
    print("="*70)

    try:
        from ai_schedule_agent.integrations.calendar_tools import plan_week_schedule

        # 測試週排程
        planned = plan_week_schedule(
            summary="讀電子學",
            total_hours=4.0,
            chunk_hours=2.0,
            daily_window=(9, 18),
            max_weeks=4
        )

        logger.info(f"✓ plan_week_schedule 執行成功")
        logger.info(f"  排程數量: {len(planned)}")

        if planned:
            logger.info("  排程詳情:")
            for i, p in enumerate(planned[:3], 1):  # 只顯示前3個
                logger.info(
                    f"    {i}. {p['start'].strftime('%Y-%m-%d %H:%M')} -> "
                    f"{p['end'].strftime('%H:%M')}"
                )

        print("\n✅ 測試 4 通過\n")
        return True

    except Exception as e:
        logger.error(f"✗ 測試 4 失敗: {e}")
        import traceback
        traceback.print_exc()
        print("\n❌ 測試 4 失敗\n")
        return False


def test_backward_compatibility():
    """測試 5: 向後兼容性"""
    print("\n" + "="*70)
    print("測試 5: 向後兼容性（Event 物件創建）")
    print("="*70)

    try:
        from ai_schedule_agent.integrations.google_calendar import CalendarIntegration
        from ai_schedule_agent.models.event import Event

        calendar = CalendarIntegration()

        # 創建 Event 物件（原有方式）
        event = Event(
            title="測試會議",
            start_time=datetime.now() + timedelta(hours=1),
            end_time=datetime.now() + timedelta(hours=2),
            description="向後兼容性測試"
        )

        logger.info("✓ Event 物件創建成功")
        logger.info(f"  標題: {event.title}")
        logger.info(f"  開始: {event.start_time}")
        logger.info(f"  結束: {event.end_time}")

        # 注意：在 DRY_RUN 模式下不會實際調用 create_event
        # 因為需要認證，這裡只測試物件創建

        print("\n✅ 測試 5 通過\n")
        return True

    except Exception as e:
        logger.error(f"✗ 測試 5 失敗: {e}")
        import traceback
        traceback.print_exc()
        print("\n❌ 測試 5 失敗\n")
        return False


def main():
    """執行所有測試"""
    print("\n" + "╔" + "="*68 + "╗")
    print("║" + " "*20 + "阿嚕米整合測試" + " "*20 + "║")
    print("║" + " "*15 + "Arumi Integration Tests" + " "*15 + "║")
    print("╚" + "="*68 + "╝")

    print("\n⚙️  環境設定:")
    print(f"   DRY_RUN: {os.getenv('DRY_RUN')}")
    print(f"   Python: {sys.version.split()[0]}")
    print()

    tests = [
        ("CalendarService 初始化", test_calendar_service),
        ("calendar_tools 核心函數", test_calendar_tools),
        ("CalendarIntegration 類別", test_calendar_integration),
        ("智能週排程", test_plan_week_schedule),
        ("向後兼容性", test_backward_compatibility),
    ]

    results = []
    for name, test_func in tests:
        result = test_func()
        results.append((name, result))

    # 總結
    print("\n" + "="*70)
    print("測試總結")
    print("="*70)

    passed = sum(1 for _, r in results if r)
    total = len(results)

    for name, result in results:
        status = "✅ 通過" if result else "❌ 失敗"
        print(f"  {status}  {name}")

    print("\n" + "="*70)
    print(f"總計: {passed}/{total} 測試通過")
    print("="*70)

    if passed == total:
        print("\n🎉 所有測試通過！阿嚕米整合成功！")
        return 0
    else:
        print(f"\n⚠️  {total - passed} 個測試失敗")
        return 1


if __name__ == '__main__':
    sys.exit(main())
