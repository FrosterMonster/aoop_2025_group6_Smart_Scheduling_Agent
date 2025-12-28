# 阿嚕米（Alumi）

### AI 智能全日曆助理（Smart Scheduling Agent）

---

## 專案簡介（Introduction）

**阿嚕米（Alumi）** 是一個結合自然語言理解（LLM）、時間解析與 Google Calendar API 的智慧行程助理。
使用者可以透過接近日常語言的中文指令（例如：「明天早上十點健身三小時」、「明天找空檔讀書」），由系統自動解析並建立對應的行事曆事件。

本專案特別著重於：

* **安全性（DRY_RUN / Mock 機制）**
* **可解釋性（清楚的 fallback 流程）**
* **模組化設計（時間解析、Agent、Calendar API 分離）**

---

## 功能特色（Features）

* ✅ 中文自然語言時間解析（今天 / 明天 / 上午 / 下午 / 幾點 / 幾小時）
* ✅ 支援固定行程與彈性行程（找空檔）
* ✅ Google Calendar 寫入（OAuth2）
* ✅ DRY_RUN 安全模式（不實際寫入）
* ✅ LLM 不可用時自動退回 rule-based fallback
* ✅ 完整日誌紀錄（終端 + 檔案）

---

## 專案結構（Project Structure）

```
阿嚕米_archived/
├─ agent_main.py              # Agent 主入口（流程 orchestration）
├─ calendar_time_parser.py    # 自然語言時間解析（rule-based + heuristics）
├─ calendar_tools.py          # Calendar 寫入封裝（含 DRY_RUN）
├─ calendar_service.py        # Google OAuth2 與 service 建立
├─ schedule_task.py           # 行程建立工具層
├─ check_models.py            # 檢查可用 LLM
├─ list_models.py             # 列出模型（除錯用）
│
├─ templates/                 # Web UI templates
├─ logs/                      # 日誌（agent.log）
├─ docs/
│  └─ overall_flow.md         # 系統流程圖與補充說明
│
├─ test_time_parser.py        # parser 單元測試
├─ credentials.json           # Google OAuth client（不納入版控）
├─ requirements.txt
├─ requirements.web.txt
├─ README.md
└─ .env
```

---

## 系統整體流程（High-level Overview）

1. 使用者輸入自然語言請求

   > 例：「明天早上十點健身三小時」

2. `agent_main.run_agent()` 作為系統入口：

   * 讀取環境變數（API Key / DRY_RUN）
   * 嘗試使用 LLM（OpenAI / Gemini）
   * 若 LLM 不可用，自動退回 Mock / rule-based 流程

3. 自然語言時間解析：

   * 由 `calendar_time_parser.parse_nl_time()` 處理
   * 回傳 timezone-aware `datetime`（Asia/Taipei）
   * 若無明確時間，視為彈性行程（找空檔）

4. 行程建立：

   * `schedule_calendar_event()` 統一處理參數
   * 呼叫 `calendar_tools.create_calendar_event()`

5. 根據 `DRY_RUN`：

   * `DRY_RUN=1` → 僅模擬、不寫入
   * `DRY_RUN=0` → 實際寫入 Google Calendar

---

## 啟動方式（How to Run）

### 1️⃣ 環境準備

* Python 3.9+
* 建立 `.env`，內容範例：

```env
OPENAI_API_KEY=your_key_here
GEMINI_API_KEY=your_key_here
DRY_RUN=1
```

* 放置 Google OAuth 憑證：

  * `credentials.json` 於專案根目錄

---

### 2️⃣ 安全測試（建議）

```powershell
$env:DRY_RUN='1'
python agent_main.py
```

* 不會實際寫入 Google Calendar
* 適合 demo / 開發 / 測試

---

### 3️⃣ 真實寫入 Google Calendar

```powershell
Remove-Item Env:\DRY_RUN -ErrorAction SilentlyContinue
python agent_main.py
```

* 第一次執行會跳出瀏覽器完成 OAuth
* 成功後會產生 `token.pickle`

---

## 設計取捨與假設（Design Decisions）

* **時間解析與行程寫入分離**
  → 提高可測試性與可維護性

* **DRY_RUN 預設開啟**
  → 避免測試期間誤寫入使用者日曆

* **LLM 非必要依賴**
  → 當 API 配額不足或錯誤時，系統仍可運作

* **Rule-based fallback 優先穩定性**
  → 不追求涵蓋所有中文語法，而是確保常見情境可用

---

## 已知限制（Limitations）

* 尚未完整支援：

  * 「下週一 / 下下週」
  * 中文大寫數字（如「三點半」、「兩個半小時」）
* 彈性行程目前僅標記為「找空檔」，尚未做實際最佳化演算法

---

## 測試（Testing）

```powershell
pytest test_time_parser.py -q
```

測試內容包含：

* 今天 / 明天
* 上午 / 下午
* 固定時間
* 無時間（彈性行程）

---

## 未來擴充方向（Future Work）

* 加入「下週 / 月份」解析
* 更細緻的 duration（半小時、分鐘）
* 自動最佳時間推薦（基於既有行程）
* CLI 參數（--dry-run / --force-mock）

---

## 結語

本專案展示了一個 **以工程穩定性為核心** 的 AI Agent 設計，
並在 LLM 不穩定的現實條件下，仍能維持系統可用性與安全性。
