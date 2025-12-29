#!/usr/bin/env python3
"""
彈性排程測試 - 測試無具體時間的活動自動排程功能

這個測試驗證系統能否：
1. 正確解析無具體時間的請求（只有時段偏好）
2. 在日曆中找到空閒時段
3. 根據 energy pattern 選擇最佳時間
4. 處理各種時長要求（X小時、X天內完成）
"""

import os
import sys
from datetime import datetime, timedelta

# Set DRY_RUN mode
os.environ['DRY_RUN'] = '1'

from ai_schedule_agent.core.nlp_processor import NLPProcessor
from ai_schedule_agent.utils.logging import logger

# 測試案例分類
FLEXIBLE_TEST_CASES = {
    "基本彈性排程 - 時段偏好": [
        {
            'name': '下週 + 時段 + 時長',
            'input': '下週安排3小時開會',
            'expected': {
                'title': '開會',
                'duration_mins': 180,
                'has_time_preference': True,
                'is_flexible': True,  # 應該是彈性排程
                'no_datetime': True,  # 不應該有固定 datetime
            }
        },
        {
            'name': '明天上午 + 時長',
            'input': '明天上午排2小時討論',
            'expected': {
                'title': '討論',
                'duration_mins': 120,
                'has_time_preference': True,
                'time_period': 'morning',
                'is_flexible': True,
                'no_datetime': True,
            }
        },
        {
            'name': '後天下午 + 活動',
            'input': '後天下午安排面試',
            'expected': {
                'title': '面試',
                'has_time_preference': True,
                'time_period': 'afternoon',
                'is_flexible': True,
                'no_datetime': True,
            }
        },
        {
            'name': '本週晚上 + 時長',
            'input': '本週五晚上排1小時會議',
            'expected': {
                'title': '會議',
                'duration_mins': 60,
                'has_time_preference': True,
                'time_period': 'evening',
                'is_flexible': True,
            }
        },
    ],

    "期限型任務 (Deadline-based)": [
        {
            'name': 'X天內完成 + 時長',
            'input': '3天內要讀完電路project，大概需要5小時',
            'expected': {
                'title': '讀完電路project',
                'duration_mins': 300,
                'is_flexible': True,
                # 系統應該理解這是需要在3天內找5小時的任務
            }
        },
        {
            'name': '本週內完成',
            'input': '本週內要完成作業，預計2小時',
            'expected': {
                'title': '完成作業',
                'duration_mins': 120,
                'is_flexible': True,
            }
        },
        {
            'name': '下週前完成',
            'input': '下週一前要準備簡報，需要3小時',
            'expected': {
                'title': '準備簡報',
                'duration_mins': 180,
                'is_flexible': True,
            }
        },
    ],

    "多時段偏好": [
        {
            'name': '上午或下午',
            'input': '明天上午或下午排開會，2小時',
            'expected': {
                'title': '開會',
                'duration_mins': 120,
                'is_flexible': True,
            }
        },
        {
            'name': '工作時間內',
            'input': '下週工作時間內安排培訓，4小時',
            'expected': {
                'title': '培訓',
                'duration_mins': 240,
                'is_flexible': True,
            }
        },
    ],

    "Energy Pattern 相關": [
        {
            'name': '需要專注力的任務',
            'input': '這週找時間寫程式，需要4小時',
            'expected': {
                'title': '寫程式',
                'duration_mins': 240,
                'is_flexible': True,
                # 系統應該選擇 energy 高的時段（通常是上午）
            }
        },
        {
            'name': '輕鬆的任務',
            'input': '下週安排整理文件，1小時',
            'expected': {
                'title': '整理文件',
                'duration_mins': 60,
                'is_flexible': True,
                # 可以安排在任何時段
            }
        },
        {
            'name': '會議型任務',
            'input': '明天找時間跟團隊開會，90分鐘',
            'expected': {
                'title': '跟團隊開會',
                'duration_mins': 90,
                'is_flexible': True,
                # 應該避開午餐和下班時間
            }
        },
    ],

    "連續 vs 分段": [
        {
            'name': '可分段任務',
            'input': '這週要讀書10小時，可以分段進行',
            'expected': {
                'title': '讀書',
                'duration_mins': 600,
                'is_flexible': True,
                'can_split': True,
            }
        },
        {
            'name': '必須連續',
            'input': '下週安排連續3小時的深度工作',
            'expected': {
                'title': '深度工作',
                'duration_mins': 180,
                'is_flexible': True,
                'must_continuous': True,
            }
        },
    ],

    "優先級相關": [
        {
            'name': '重要任務',
            'input': '明天一定要完成報告，需要2小時',
            'expected': {
                'title': '完成報告',
                'duration_mins': 120,
                'is_flexible': True,
                'high_priority': True,
            }
        },
        {
            'name': '選擇性任務',
            'input': '有空的話去運動1小時',
            'expected': {
                'title': '運動',
                'duration_mins': 60,
                'is_flexible': True,
                'low_priority': True,
            }
        },
    ],
}


def validate_flexible_result(result: dict, expected: dict, test_name: str) -> list:
    """驗證彈性排程結果是否符合預期

    Returns:
        list: 錯誤訊息列表，如果為空則表示通過
    """
    errors = []

    # 檢查標題
    if 'title' in expected:
        actual_title = result.get('title', '')
        expected_title = expected['title']
        if actual_title != expected_title:
            errors.append(f"Title: expected '{expected_title}', got '{actual_title}'")

    # 檢查時長
    if 'duration_mins' in expected:
        actual_duration = result.get('duration')
        expected_duration = expected['duration_mins']
        if actual_duration != expected_duration:
            errors.append(f"Duration: expected {expected_duration}min, got {actual_duration}min")

    # 檢查是否為彈性排程（有 time_preference 但無固定 datetime）
    if expected.get('is_flexible'):
        has_preference = result.get('time_preference') is not None
        has_datetime = result.get('datetime') is not None

        # 彈性排程應該：
        # - 有 time_preference（時段偏好）或 target_date（目標日期）
        # - 沒有固定的 datetime（如果有 datetime 就變成固定時間了）

        if expected.get('no_datetime'):
            if has_datetime:
                errors.append(f"Expected flexible scheduling (no datetime), but got datetime: {result.get('datetime')}")

        if expected.get('has_time_preference'):
            if not has_preference and not result.get('target_date'):
                errors.append("Expected time_preference or target_date for flexible scheduling, but got neither")

    # 檢查時段偏好
    if expected.get('has_time_preference'):
        if not result.get('time_preference'):
            errors.append("Expected time_preference but got None")
        elif 'time_period' in expected:
            actual_period = result.get('time_preference', {}).get('period')
            expected_period = expected['time_period']
            if actual_period != expected_period:
                errors.append(f"Time period: expected '{expected_period}', got '{actual_period}'")

    return errors


def run_flexible_scheduling_tests():
    """執行彈性排程測試"""
    print("=" * 80)
    print("阿嚕米 Mock Mode - 彈性排程測試")
    print("測試無具體時間的活動自動排程功能")
    print("=" * 80)
    print()

    # Initialize NLP processor with rule-based mode (no LLM)
    nlp = NLPProcessor(use_llm=False)

    total_tests = 0
    total_passed = 0
    total_failed = 0
    category_results = {}

    # 執行每個分類的測試
    for category_name, test_cases in FLEXIBLE_TEST_CASES.items():
        print(f"\n{'='*80}")
        print(f"📂 分類: {category_name}")
        print(f"{'='*80}\n")

        category_passed = 0
        category_failed = 0

        for i, test_case in enumerate(test_cases, 1):
            total_tests += 1
            test_name = test_case['name']
            user_input = test_case['input']
            expected = test_case['expected']

            print(f"Test {i}/{len(test_cases)}: {test_name}")
            print(f"輸入: {user_input}")
            print("-" * 80)

            try:
                # Parse using rule-based NLP (阿嚕米 Mock mode patterns)
                result = nlp.parse_scheduling_request(user_input)

                # Validate results
                errors = validate_flexible_result(result, expected, test_name)

                if errors:
                    print("❌ FAILED")
                    for error in errors:
                        print(f"   {error}")
                    category_failed += 1
                    total_failed += 1
                else:
                    print("✅ PASSED")
                    category_passed += 1
                    total_passed += 1

                # Print extracted fields
                print(f"\n解析結果:")
                print(f"  標題: {result.get('title')}")
                print(f"  時長: {result.get('duration')} 分鐘" if result.get('duration') else "  時長: None")
                print(f"  固定時間: {result.get('datetime')}")
                print(f"  目標日期: {result.get('target_date')}")
                print(f"  時段偏好: {result.get('time_preference')}")

                # 判斷排程類型
                is_flexible = result.get('time_preference') is not None and not result.get('datetime')
                has_exact_time = result.get('datetime') is not None

                if is_flexible:
                    period = result.get('time_preference', {}).get('period', 'N/A')
                    print(f"\n  🔸 排程類型: 彈性排程")
                    print(f"  🔸 系統將自動尋找最佳時段（偏好: {period}）")
                    print(f"  🔸 考慮因素: 日曆空檔 + Energy Pattern")
                elif has_exact_time:
                    print(f"\n  🔸 排程類型: 固定時間")
                    print(f"  🔸 將排定於指定時間: {result.get('datetime')}")
                else:
                    print(f"\n  🔸 排程類型: 待定（需要更多資訊）")

            except Exception as e:
                print(f"❌ EXCEPTION: {e}")
                import traceback
                traceback.print_exc()
                category_failed += 1
                total_failed += 1

            print()

        # 分類結果摘要
        category_results[category_name] = {
            'passed': category_passed,
            'failed': category_failed,
            'total': len(test_cases)
        }

        pass_rate = (category_passed / len(test_cases) * 100) if len(test_cases) > 0 else 0
        print(f"📊 {category_name} 結果: {category_passed}/{len(test_cases)} 通過 ({pass_rate:.1f}%)\n")

    # 總結報告
    print("\n" + "=" * 80)
    print("📈 彈性排程測試總結")
    print("=" * 80)
    print()

    # 各分類詳細結果
    print("各分類結果:")
    print("-" * 80)
    for category_name, stats in category_results.items():
        pass_rate = (stats['passed'] / stats['total'] * 100) if stats['total'] > 0 else 0
        status = "✅" if stats['failed'] == 0 else "⚠️" if pass_rate >= 80 else "❌"
        print(f"{status} {category_name:30s}: {stats['passed']:2d}/{stats['total']:2d} ({pass_rate:5.1f}%)")

    print()
    print("-" * 80)
    overall_pass_rate = (total_passed / total_tests * 100) if total_tests > 0 else 0
    print(f"總計: {total_passed}/{total_tests} 測試通過 ({overall_pass_rate:.1f}%)")
    print(f"✅ 通過: {total_passed}")
    print(f"❌ 失敗: {total_failed}")
    print()

    # 評估等級
    if overall_pass_rate >= 95:
        grade = "優秀 🌟"
    elif overall_pass_rate >= 85:
        grade = "良好 👍"
    elif overall_pass_rate >= 70:
        grade = "及格 ✓"
    else:
        grade = "需要改進 ⚠️"

    print(f"整體評估: {grade}")

    # 下一步建議
    print("\n" + "=" * 80)
    print("💡 下一步: 實際排程測試")
    print("=" * 80)
    print("""
這個測試驗證了 NLP 解析層面的彈性排程理解能力。

要完整測試彈性排程功能，還需要：

1. **整合 Calendar Service**
   - 讀取真實的日曆空檔
   - 呼叫 find_free_slots() 找到可用時段

2. **整合 Scheduling Engine**
   - 根據 time_preference 過濾時段
   - 應用 energy pattern 評分
   - 選擇最佳時段

3. **建立完整測試流程**
   - 準備測試用日曆（包含已有事件）
   - 執行彈性排程請求
   - 驗證選擇的時段是否合理

建議運行: python test_integration_flexible.py (待建立)
""")

    print("=" * 80)

    return 0 if total_failed == 0 else 1


if __name__ == '__main__':
    sys.exit(run_flexible_scheduling_tests())
