# AI Schedule Agent 整合分析報告

**日期**: 2025-12-29
**分析範圍**: 阿嚕米_archived 與 ai_schedule_agent 整合狀態
**目標**: 確認整合完整性，識別需要變更的部分

---

## 📋 執行摘要

經過詳細檢視，**ai_schedule_agent 已經有良好的基礎架構**，但存在**關鍵的整合缺口**需要處理。以下是主要發現：

### ✅ 已完成的整合
1. ✅ **calendar_tools.py** - 阿嚕米核心邏輯已完整移植
2. ✅ **nlp_processor.py** - 阿嚕米 Mock Mode 已整合（92.1% 測試通過率）
3. ✅ **quick_schedule_tab.py** - UI 已實現彈性排程邏輯（手動實現）

### ❌ 需要修正的問題
1. ❌ **scheduling_engine.py** - 未使用 calendar_tools 的函數
2. ❌ **重複實現** - quick_schedule_tab 手動實現了找空檔邏輯
3. ❌ **測試框架** - test_integration_scheduling.py 無法執行（API 不匹配）

---

## 🏗️ 架構分析

### 當前架構流程

```
用戶輸入 (UI)
    ↓
nlp_processor.py (阿嚕米 Mock Mode) ✅
    ↓
scheduling_engine.py (舊邏輯) ❌
    ↓
google_calendar.py
```

### 理想架構流程

```
用戶輸入 (UI)
    ↓
nlp_processor.py (阿嚕米 Mock Mode) ✅
    ↓
scheduling_engine.py (應使用 calendar_tools)
    ↓
calendar_tools.py (阿嚕米核心) ✅
    ↓
calendar_service.py + google_calendar.py
```

---

## 🔍 詳細發現

### 1. calendar_tools.py - ✅ 完整移植

**位置**: `ai_schedule_agent/integrations/calendar_tools.py`

**狀態**: **已完成** - 從阿嚕米_archived 完整移植

**包含功能**:
- ✅ `create_calendar_event()` - 建立日曆事件
- ✅ `get_busy_periods()` - 使用 FreeBusy API 查詢忙碌時段
- ✅ `find_free_slots_between()` - 時間區間合併算法找空檔
- ✅ `plan_week_schedule()` - 智能週排程

**特色**:
```python
# 經典時間區間合併算法
def find_free_slots_between(
    start_dt: datetime,
    end_dt: datetime,
    busy_periods: List[Dict[str, str]],
    min_duration_minutes: int = 60
) -> List[Tuple[datetime, datetime]]:
    """
    算法步驟：
    1. 將所有忙碌時段按開始時間排序
    2. 合併重疊的忙碌時段
    3. 計算相鄰忙碌時段之間的空閒時間
    """
```

**DRY_RUN 保護機制**: ✅ 所有函數都有 `if os.getenv('DRY_RUN') == '1'` 保護

---

### 2. scheduling_engine.py - ❌ 未使用 calendar_tools

**位置**: `ai_schedule_agent/core/scheduling_engine.py`

**問題**: **重複實現了找空檔邏輯**，沒有使用已經移植好的 `calendar_tools.py`

**當前實現**:
```python
# scheduling_engine.py 第 86-132 行
def find_optimal_slot(self, event: Event, ...) -> Optional[Tuple[...]]:
    # ❌ 手動實現找空檔邏輯
    # 1. 獲取 existing_events
    # 2. 轉換為 busy_slots
    # 3. 手動遍歷每個 30 分鐘 slot
    # 4. 檢查衝突
    # 5. 計算評分
```

**應該使用**:
```python
# 應該使用 calendar_tools 的函數
from ai_schedule_agent.integrations.calendar_tools import (
    get_busy_periods,
    find_free_slots_between
)

def find_optimal_slot(self, event: Event, ...) -> Optional[Tuple[...]]:
    # ✅ 使用阿嚕米的函數
    busy_periods = get_busy_periods(service, start_dt, end_dt)
    free_slots = find_free_slots_between(start_dt, end_dt, busy_periods)

    # 在 free_slots 中用 energy pattern 評分選最佳
    best_slot = self._select_best_slot(free_slots, event.event_type)
```

**影響**:
- 程式碼重複
- 維護困難（兩套邏輯）
- 無法享受阿嚕米已驗證的穩定算法

---

### 3. quick_schedule_tab.py - ⚠️ 重複實現

**位置**: `ai_schedule_agent/ui/tabs/quick_schedule_tab.py`

**問題**: 在 UI 層**再次手動實現**找空檔邏輯（第 247-285 行）

```python
# quick_schedule_tab.py 第 247-285 行
# Extract busy slots
busy_slots = []
for e in existing_events:
    # ... 手動提取忙碌時段

# Find free slots STRICTLY within the time preference window
optimal_slot = None
current_slot = window_start
while current_slot + timedelta(minutes=duration) <= window_end:
    # ... 手動檢查每個 slot
```

**應該使用**:
```python
from ai_schedule_agent.integrations.calendar_tools import (
    get_busy_periods,
    find_free_slots_between
)

# 使用阿嚕米函數
busy_periods = get_busy_periods(service, window_start, window_end)
free_slots = find_free_slots_between(window_start, window_end, busy_periods, duration)

if free_slots:
    # 用 scheduling_engine 評分選最佳
    best_slot = self.scheduling_engine._calculate_slot_score(...)
```

**註解中的關鍵發現**:
```python
# CRITICAL: Manually find free slots STRICTLY within the time preference window
# We can't rely on find_optimal_slot because it uses working_hours from profile
# which might be wider than the user's requested time period
```

**這表示**:
- `scheduling_engine.find_optimal_slot()` 使用的是 user_profile.working_hours
- 但用戶可能要求更窄的時段（如「下午」）
- 所以 UI 層不得不自己實現

**正確做法**:
- 修正 `scheduling_engine.find_optimal_slot()` 接受時間窗口參數
- 或新增 `find_optimal_slot_in_window(start, end, event)` 方法

---

### 4. nlp_processor.py - ✅ 阿嚕米 Mock Mode 已整合

**位置**: `ai_schedule_agent/core/nlp_processor.py`

**狀態**: **已完成** - 已整合阿嚕米的中文 pattern matching

**測試結果**:
- ✅ **92.1%** 通過率 (35/38 測試案例)
- ✅ 7 個類別達到 100% 識別率
- ✅ 支援引號、時長、時段偏好、動作關鍵字、相對日期等

**關鍵功能** (第 783-990 行):
```python
def _extract_with_chinese_patterns(self, text: str) -> Dict:
    """阿嚕米 Mock Mode:
    - 9 個 pattern 匹配模式
    - 標題清理邏輯
    - 時間解析
    - 時長提取
    - 時段偏好識別
    """
```

**輸出格式**:
```python
{
    'title': '開會',
    'datetime': datetime(2025, 12, 30, 14, 0),  # 固定時間
    'duration': 120,  # 分鐘
    'time_preference': {'period': 'morning', 'start_hour': 9, 'end_hour': 12},  # 彈性時間
    'target_date': date(2025, 12, 30)
}
```

---

### 5. 阿嚕米_archived 的最新改進

**Commit**: 78abb7c7 (merged in f4634c7)
**日期**: 2025-12-29 02:39:06
**訊息**: "add 12:00 but fail"

**主要改動** (`calendar_time_parser.py`):

#### A. AI-first + Rule-based Fallback 架構
```python
def parse_with_ai(nl_text: str) -> Dict[str, Any]:
    try:
        raw = _llm_parse(nl_text)  # Step 1: AI
        events = _post_process_and_validate(raw, nl_text)  # Step 2: 後處理
        return {"events": events}
    except ClientError as e:
        if e.code == 429:  # Quota exceeded
            print("[AI QUOTA EXCEEDED] fallback used")
    return _rule_based_fallback(nl_text)  # 保證有回傳
```

#### B. 中文數字轉換
```python
CHINESE_NUM_MAP = {
    "零": 0, "一": 1, "二": 2, "兩": 2,
    "三": 3, ... "十": 10
}
```

#### C. 智能時間修正（順序很重要）
```python
if "中午" in nl_text:
    # 中午 11 點 → 11:00
    # 中午 12 點 → 12:00
    pass
elif "下午" in nl_text or "晚上" in nl_text:
    if hour < 12:
        hour += 12
elif "早上" in nl_text or "上午" in nl_text:
    if hour == 12:
        hour = 0
```

#### D. 標題清理（與 nlp_processor 相同邏輯）
```python
title = re.sub(
    r"(明天|今天|後天|本週|下週|早上|下午|晚上|上午|中午|凌晨|"
    r"\d+點|\d+:\d+|"
    r"[一二兩三四五六七八九十]+點|"
    r"[一二兩三四五六七八九十\d]+小時)",
    "", raw_title
)
title = re.sub(r"(有|的)", "", title).strip()
```

#### E. 彈性排程支援
```python
{
    "is_flexible": True/False,  # 有無明確時間
    "start_time": None,  # flexible 時為 None
}
```

**🔍 與 ai_schedule_agent 的差異**:
- 阿嚕米_archived 使用 Gemini LLM + fallback
- ai_schedule_agent 的 nlp_processor 主要用 rule-based (Mock Mode)
- 兩者的 fallback 邏輯**非常相似**（標題清理、時間修正）

---

## 🎯 整合缺口總結

| 模組 | 狀態 | 問題 | 優先級 |
|------|------|------|--------|
| **calendar_tools.py** | ✅ 完成 | 無 | - |
| **nlp_processor.py** | ✅ 完成 | 無（92.1% 通過率） | - |
| **scheduling_engine.py** | ❌ 未整合 | 未使用 calendar_tools 函數 | **🔴 高** |
| **quick_schedule_tab.py** | ⚠️ 重複 | 重複實現找空檔邏輯 | **🟡 中** |
| **test_integration** | ❌ 損壞 | API 不匹配無法執行 | **🟡 中** |

---

## 📝 必要變更清單

### 🔴 優先級 1：修正 scheduling_engine.py

**檔案**: `ai_schedule_agent/core/scheduling_engine.py`

**變更內容**:

#### 1. 新增 import
```python
from ai_schedule_agent.integrations.calendar_tools import (
    get_busy_periods,
    find_free_slots_between
)
```

#### 2. 重構 find_optimal_slot()
```python
def find_optimal_slot(
    self,
    event: Event,
    search_start: datetime.datetime = None,
    search_days: int = 14,
    time_window: Optional[Tuple[int, int]] = None  # NEW: (start_hour, end_hour)
) -> Optional[Tuple[datetime.datetime, datetime.datetime]]:
    """
    使用阿嚕米的 calendar_tools 找空檔，再用 energy pattern 評分

    Args:
        time_window: Optional (start_hour, end_hour) tuple to restrict search
                     e.g., (13, 18) for afternoon only
    """
    # 1. 使用 get_busy_periods() 獲取忙碌時段
    service = self.calendar.get_service()
    busy_periods = get_busy_periods(
        service,
        search_start,
        search_end,
        calendar_id='primary'
    )

    # 2. 使用 find_free_slots_between() 找空檔
    free_slots = find_free_slots_between(
        search_start,
        search_end,
        busy_periods,
        min_duration_minutes=total_duration
    )

    # 3. 如果有 time_window 限制，過濾 free_slots
    if time_window:
        start_h, end_h = time_window
        filtered_slots = [
            (s, e) for s, e in free_slots
            if start_h <= s.hour < end_h
        ]
        free_slots = filtered_slots

    # 4. 用 energy pattern 評分選最佳
    candidates = []
    for slot_start, slot_end in free_slots:
        score = self._calculate_slot_score(slot_start, event.event_type)
        candidates.append((slot_start, slot_end, score))

    if candidates:
        candidates.sort(key=lambda x: x[2], reverse=True)
        return (candidates[0][0], candidates[0][1])

    return None
```

**好處**:
- ✅ 使用阿嚕米已驗證的算法
- ✅ 支援時間窗口限制（解決 quick_schedule_tab 的問題）
- ✅ 保留 energy pattern 評分邏輯
- ✅ 程式碼更簡潔

---

### 🟡 優先級 2：簡化 quick_schedule_tab.py

**檔案**: `ai_schedule_agent/ui/tabs/quick_schedule_tab.py`

**變更內容**:

刪除第 247-285 行的手動實現，改為：

```python
# 改為使用 scheduling_engine 的新方法
time_window = (start_hour, end_hour)
temp_event = Event(
    title=title or 'New Event',
    event_type=parsed.get('event_type', EventType.MEETING),
    start_time=window_start,
    end_time=window_start + timedelta(minutes=duration),
    participants=participants,
    location=location
)

optimal_slot = self.scheduling_engine.find_optimal_slot(
    temp_event,
    search_start=window_start,
    search_days=1,
    time_window=time_window  # 使用新參數
)

if optimal_slot:
    start_time, end_time = optimal_slot
    # ... 填入表單
else:
    # ... 顯示錯誤
```

**好處**:
- ✅ 移除 100+ 行重複程式碼
- ✅ UI 層更簡潔
- ✅ 邏輯集中在 scheduling_engine

---

### 🟡 優先級 3：修正整合測試

**檔案**: `test_integration_scheduling.py`

**問題**:
```python
result = self.calendar.create_event(event)  # ❌ CalendarService 沒有此方法
```

**解決方案 A - 使用 calendar_tools**:
```python
from ai_schedule_agent.integrations.calendar_tools import create_calendar_event

# 轉換格式
result_msg = create_calendar_event(
    summary=event.title,
    description=event.description or '',
    start_time_str=event.start_time.strftime('%Y-%m-%d %H:%M:%S'),
    end_time_str=event.end_time.strftime('%Y-%m-%d %H:%M:%S')
)
```

**解決方案 B - 使用 google_calendar 直接操作**:
```python
from ai_schedule_agent.integrations.google_calendar import GoogleCalendar

self.gcal = GoogleCalendar()
result = self.gcal.create_event(event.to_google_event())
```

---

## 🔄 整合後的完整流程

### 固定時間排程

```
用戶: "明天下午2點開會"
    ↓
nlp_processor.parse_scheduling_request()
    → {'datetime': 2025-12-30 14:00, 'title': '開會'}
    ↓
scheduling_engine.check_conflicts(event)  # 使用 calendar.get_events()
    ↓
google_calendar.create_event()
```

### 彈性排程

```
用戶: "明天上午排2小時開會"
    ↓
nlp_processor.parse_scheduling_request()
    → {
        'target_date': 2025-12-30,
        'time_preference': {'period': 'morning', 'start_hour': 9, 'end_hour': 12},
        'duration': 120,
        'title': '開會'
      }
    ↓
scheduling_engine.find_optimal_slot(event, time_window=(9, 12))
    ├─→ calendar_tools.get_busy_periods()  # 取得忙碌時段
    ├─→ calendar_tools.find_free_slots_between()  # 找空檔
    └─→ _calculate_slot_score()  # Energy pattern 評分
    ↓
google_calendar.create_event()
```

---

## 📊 測試狀態

### 已完成測試

1. ✅ **test_complex_inputs.py** (38 cases)
   - NLP 解析測試
   - 通過率: 92.1%
   - 7 個類別 100% 通過

2. ✅ **test_flexible_scheduling.py** (16 cases)
   - 彈性排程 NLP 解析
   - 通過率: 18.8%（進階語義需 LLM）

### 待修正測試

3. ❌ **test_integration_scheduling.py**
   - API 不匹配
   - 需要修正為使用 calendar_tools

---

## 🎯 建議執行順序

### Phase 1: 核心整合（1-2 小時）
1. 修正 `scheduling_engine.py` 使用 `calendar_tools`
2. 測試基本排程功能

### Phase 2: UI 簡化（30 分鐘）
3. 簡化 `quick_schedule_tab.py` 使用新的 API
4. 測試 UI 彈性排程

### Phase 3: 測試完善（30 分鐘）
5. 修正 `test_integration_scheduling.py`
6. 執行完整測試套件

### Phase 4: 文檔更新（15 分鐘）
7. 更新 README
8. 更新 API 文檔

**總計估計時間**: 2.5-3 小時

---

## 💡 額外建議

### 1. 考慮整合阿嚕米_archived 的新改進

**來自 78abb7c7 的功能**:
- AI-first + fallback 架構
- 中文數字轉換
- 智能時間修正（中午 12 點特殊處理）

**整合方式**:
```python
# 在 nlp_processor.py 中新增
from 阿嚕米_archived.calendar_time_parser import parse_with_ai

def parse_with_llm_fallback(self, text: str) -> Dict:
    """LLM Mode with阿嚕米 fallback"""
    if self.use_llm:
        try:
            # 使用阿嚕米的 AI parser
            result = parse_with_ai(text)
            return self._convert_alumi_format(result)
        except Exception:
            pass

    # Fallback to Mock Mode
    return self._extract_with_chinese_patterns(text)
```

### 2. 統一時間處理

**問題**: 多處時區處理邏輯
- `scheduling_engine.py` - naive vs aware datetime
- `calendar_tools.py` - Asia/Taipei
- `nlp_processor.py` - 使用 parse_nl_time()

**建議**: 建立 `time_utils.py` 統一處理

### 3. 錯誤處理改進

**當前**: 許多地方直接 `try-except` 並 `return None`

**建議**: 使用自定義 Exception
```python
class NoFreeSlotError(Exception):
    """No free slot available in the requested time window"""
    pass

class ConflictError(Exception):
    """Event conflicts with existing events"""
    pass
```

---

## ✅ 結論

ai_schedule_agent 的**架構良好**，但存在**關鍵整合缺口**：

### 已完成 ✅
- calendar_tools.py 移植完整
- nlp_processor.py 阿嚕米 Mock Mode 整合（92.1% 通過率）
- UI 基本功能可用

### 需要修正 ❌
- **scheduling_engine.py 未使用 calendar_tools** → 必須修正
- quick_schedule_tab.py 重複實現邏輯 → 可以簡化
- 整合測試損壞 → 需要修正

### 預期效益
修正後將獲得：
1. ✅ 統一使用阿嚕米驗證過的算法
2. ✅ 程式碼更簡潔（減少 200+ 行重複）
3. ✅ 更好的維護性
4. ✅ 完整的測試覆蓋

**建議**: 立即執行 Phase 1 核心整合，可在 1-2 小時內完成主要改進。
