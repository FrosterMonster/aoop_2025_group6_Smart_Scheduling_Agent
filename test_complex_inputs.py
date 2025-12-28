#!/usr/bin/env python3
"""
複雜輸入測試 - 測試阿嚕米 Mock Mode 對各種複雜輸入的處理能力

這個測試包含了各種真實場景下的複雜輸入，用來驗證 NLP 處理的穩健性。
"""

import os
import sys
from datetime import datetime, timedelta

# Set DRY_RUN mode
os.environ['DRY_RUN'] = '1'

from ai_schedule_agent.core.nlp_processor import NLPProcessor
from ai_schedule_agent.utils.logging import logger

# 測試案例分類
TEST_CATEGORIES = {
    "基本時間範圍": [
        {
            'name': '基本時間範圍 - 到',
            'input': '明天下午2點到4點開會',
            'expected': {
                'title': '開會',
                'has_datetime': True,
                'duration_mins': 120
            }
        },
        {
            'name': '基本時間範圍 - 晚上',
            'input': '今天晚上8點到9點討論專案',
            'expected': {
                'title': '討論專案',
                'has_datetime': True,
                'duration_mins': 60
            }
        },
        {
            'name': '基本時間範圍 - 跨日',
            'input': '今天晚上11點到明天凌晨1點加班',
            'expected': {
                'title': '加班',
                'has_datetime': True,
            }
        },
    ],

    "引號和特殊字符": [
        {
            'name': '中文引號「」',
            'input': '請幫我安排一個「與導師會面」的活動，時間是今天晚上 8 點到 9 點。',
            'expected': {
                'title': '與導師會面',
                'has_datetime': True,
                'duration_mins': 60
            }
        },
        {
            'name': '英文引號""',
            'input': '明天下午2點安排"團隊會議"',
            'expected': {
                'title': '團隊會議',
                'has_datetime': True,
            }
        },
        {
            'name': '書名號《》',
            'input': '下週一早上9點排《產品發表會》',
            'expected': {
                'title': '產品發表會',
            }
        },
        {
            'name': '混合標點符號',
            'input': '明天，下午3點，排「客戶拜訪」，2小時',
            'expected': {
                'title': '客戶拜訪',
                'duration_mins': 120
            }
        },
    ],

    "時長表達": [
        {
            'name': '時長 - X小時',
            'input': '明天下午排3小時開會',
            'expected': {
                'title': '開會',
                'duration_mins': 180,
                'has_time_preference': True
            }
        },
        {
            'name': '時長 - X分鐘',
            'input': '今天下午2點安排30分鐘站立會議',
            'expected': {
                'title': '站立會議',
                'duration_mins': 30,
                'has_datetime': True
            }
        },
        {
            'name': '時長 - 小時+分鐘',
            'input': '明天上午排2小時30分鐘培訓',
            'expected': {
                'title': '培訓',
                'has_time_preference': True
            }
        },
        {
            'name': '時長 - 半小時',
            'input': '後天中午12點半小時午餐會',
            'expected': {
                'title': '午餐會',
            }
        },
    ],

    "時段偏好": [
        {
            'name': '時段偏好 - 上午',
            'input': '明天上午排開會',
            'expected': {
                'title': '開會',
                'has_time_preference': True,
                'time_period': 'morning'
            }
        },
        {
            'name': '時段偏好 - 下午',
            'input': '後天下午排2小時討論',
            'expected': {
                'title': '討論',
                'duration_mins': 120,
                'has_time_preference': True,
                'time_period': 'afternoon'
            }
        },
        {
            'name': '時段偏好 - 晚上',
            'input': '明天晚上安排聚餐',
            'expected': {
                'title': '聚餐',
                'has_time_preference': True,
                'time_period': 'evening'
            }
        },
        {
            'name': '時段偏好 - 中午',
            'input': '明天中午排午餐會議',
            'expected': {
                'title': '午餐會議',
                'has_time_preference': True,
                'time_period': 'noon'
            }
        },
    ],

    "動作關鍵字": [
        {
            'name': '動作 - 安排',
            'input': '安排明天下午3點面試',
            'expected': {
                'title': '面試',
                'has_datetime': True
            }
        },
        {
            'name': '動作 - 排',
            'input': '明天早上9點排晨會',
            'expected': {
                'title': '晨會',
                'has_datetime': True
            }
        },
        {
            'name': '動作 - 預定',
            'input': '預定下週三下午2點會議室',
            'expected': {
                'title': '會議室',
            }
        },
        {
            'name': '動作 - 訂',
            'input': '訂明天中午12點餐廳',
            'expected': {
                'title': '餐廳',
            }
        },
    ],

    "相對日期": [
        {
            'name': '相對日期 - 今天',
            'input': '今天下午3點開會',
            'expected': {
                'title': '開會',
                'has_datetime': True
            }
        },
        {
            'name': '相對日期 - 明天',
            'input': '明天上午10點討論',
            'expected': {
                'title': '討論',
                'has_datetime': True
            }
        },
        {
            'name': '相對日期 - 後天',
            'input': '後天晚上7點聚餐',
            'expected': {
                'title': '聚餐',
                'has_datetime': True
            }
        },
        {
            'name': '相對日期 - 本週',
            'input': '本週五下午2點報告',
            'expected': {
                'title': '報告',
            }
        },
        {
            'name': '相對日期 - 下週',
            'input': '下週一早上9點晨會',
            'expected': {
                'title': '晨會',
            }
        },
    ],

    "複雜組合": [
        {
            'name': '複雜 - 完整描述',
            'input': '請幫我安排明天下午2點到4點的「專案進度檢討會議」，預計2小時',
            'expected': {
                'title': '專案進度檢討會議',
                'has_datetime': True,
                'duration_mins': 120
            }
        },
        {
            'name': '複雜 - 多個時間線索',
            'input': '明天，也就是週三，下午3點排開會，大概1小時',
            'expected': {
                'title': '開會',
                'has_datetime': True,
                'duration_mins': 60
            }
        },
        {
            'name': '複雜 - 包含地點',
            'input': '後天上午10點在會議室A排「客戶提案」',
            'expected': {
                'title': '客戶提案',
            }
        },
        {
            'name': '複雜 - 包含參與者',
            'input': '明天下午2點跟John和Mary開會討論Q1計畫',
            'expected': {
                'title': '開會討論Q1計畫',
                'has_datetime': True
            }
        },
    ],

    "邊界情況": [
        {
            'name': '邊界 - 午夜',
            'input': '今天午夜12點排除錯',
            'expected': {
                'title': '除錯',
            }
        },
        {
            'name': '邊界 - 清晨',
            'input': '明天清晨6點晨跑',
            'expected': {
                'title': '晨跑',
            }
        },
        {
            'name': '邊界 - 只有標題',
            'input': '安排討論會議',
            'expected': {
                'title': '討論會議',
            }
        },
        {
            'name': '邊界 - 非常簡短',
            'input': '明天開會',
            'expected': {
                'title': '開會',
            }
        },
        {
            'name': '邊界 - 超長標題',
            'input': '明天下午2點排「第四季度產品開發進度檢討暨下年度策略規劃會議」',
            'expected': {
                'title': '第四季度產品開發進度檢討暨下年度策略規劃會議',
                'has_datetime': True
            }
        },
    ],

    "模糊表達": [
        {
            'name': '模糊 - 大概時間',
            'input': '明天下午大概3點左右開會',
            'expected': {
                'title': '開會',
            }
        },
        {
            'name': '模糊 - 約',
            'input': '後天約下午2點討論',
            'expected': {
                'title': '討論',
            }
        },
        {
            'name': '模糊 - 前後',
            'input': '明天下午3點前後排會議',
            'expected': {
                'title': '會議',
            }
        },
    ],

    "多事件": [
        {
            'name': '多事件 - 連續',
            'input': '明天上午10點開會，下午2點討論，晚上7點聚餐',
            'expected': {
                'title': '開會',  # 應該抓第一個
                'has_datetime': True
            }
        },
        {
            'name': '多事件 - 並列',
            'input': '明天排開會和討論',
            'expected': {
                'title': '開會和討論',
            }
        },
    ]
}


def validate_result(result: dict, expected: dict, test_name: str) -> list:
    """驗證結果是否符合預期

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

    # 檢查是否有 datetime
    if expected.get('has_datetime'):
        if not result.get('datetime'):
            errors.append("Expected datetime but got None")

    # 檢查時長
    if 'duration_mins' in expected:
        actual_duration = result.get('duration')
        expected_duration = expected['duration_mins']
        if actual_duration != expected_duration:
            errors.append(f"Duration: expected {expected_duration}min, got {actual_duration}min")

    # 檢查是否有 time_preference
    if expected.get('has_time_preference'):
        if not result.get('time_preference'):
            errors.append("Expected time_preference but got None")
        elif 'time_period' in expected:
            actual_period = result.get('time_preference', {}).get('period')
            expected_period = expected['time_period']
            if actual_period != expected_period:
                errors.append(f"Time period: expected '{expected_period}', got '{actual_period}'")

    return errors


def run_comprehensive_tests():
    """執行全面的測試"""
    print("=" * 80)
    print("阿嚕米 Mock Mode - 複雜輸入測試")
    print("=" * 80)
    print()

    # Initialize NLP processor with rule-based mode (no LLM)
    nlp = NLPProcessor(use_llm=False)

    total_tests = 0
    total_passed = 0
    total_failed = 0
    category_results = {}

    # 執行每個分類的測試
    for category_name, test_cases in TEST_CATEGORIES.items():
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
                errors = validate_result(result, expected, test_name)

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
                print(f"  日期時間: {result.get('datetime')}")
                print(f"  結束時間: {result.get('end_datetime')}")
                print(f"  時長: {result.get('duration')} 分鐘" if result.get('duration') else "  時長: None")
                print(f"  目標日期: {result.get('target_date')}")
                print(f"  時段偏好: {result.get('time_preference')}")

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
    print("📈 測試總結報告")
    print("=" * 80)
    print()

    # 各分類詳細結果
    print("各分類結果:")
    print("-" * 80)
    for category_name, stats in category_results.items():
        pass_rate = (stats['passed'] / stats['total'] * 100) if stats['total'] > 0 else 0
        status = "✅" if stats['failed'] == 0 else "⚠️" if pass_rate >= 80 else "❌"
        print(f"{status} {category_name:20s}: {stats['passed']:2d}/{stats['total']:2d} ({pass_rate:5.1f}%)")

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
    print("=" * 80)

    return 0 if total_failed == 0 else 1


if __name__ == '__main__':
    sys.exit(run_comprehensive_tests())
