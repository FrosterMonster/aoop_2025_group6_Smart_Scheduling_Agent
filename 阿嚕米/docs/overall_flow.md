# 整體流程說明（Overview）

本文檔以中文說明專案 `阿嚕米` 的整體運作流程、主要元件、啟動與認證步驟、事件建立流程、已知邊界情況與假設，並提供切換到真實 LLM/寫入的操作說明。

## 主要檔案與責任
- `agent_main.py`
  - 程式入口（包含一個 `run_agent(user_query)` 函式），負責：
    - 讀取環境變數與 `.env`（`OPENAI_API_KEY`, `GEMINI_API_KEY`, `DRY_RUN`）
    - 嘗試建立 LLM 連線（OpenAI 或 Google GenAI），如失敗則退回 Mock 流程
    - 將自然語言時間轉換為精確時間（透過 `calendar_time_parser.parse_nl_time`）
    - 呼叫 `schedule_calendar_event` 工具（內部會呼叫 `calendar_tools.create_calendar_event`）
    - 提供日誌（logger `agent`），包含終端與 `logs/agent.log` 檔案

- `calendar_time_parser.py`
  - 自然語言時間解析器
  - 使用 `dateparser` 為基礎，並有針對中文常見短語（例如「今天/明天/後天」、「上午/下午/晚上」）的 heuristics
  - 回傳 timezone-aware 的 `datetime`（時區預設為 Asia/Taipei）或 `None`（無法解析）

- `calendar_tools.py`
  - 實際包含寫入 Google Calendar 的邏輯（封裝 `create_calendar_event`）
  - 會使用 `calendar_service.get_calendar_service()` 取得 Google API 的 service
  - 若環境變數 `DRY_RUN=1`，則只回傳模擬訊息（不做寫入），並且會記錄日誌

- `calendar_service.py`
  - 負責 OAuth2 的流程（使用 `credentials.json` 取得使用者授權，並儲存 `token.pickle`）
  - 回傳已授權的 `service` 物件供 `calendar_tools` 使用

- `test_time_parser.py`
  - 包含單元測試，驗證 `calendar_time_parser` 在常見情況下的行為

## 啟動與認證流程
1. 準備
   - 將 OpenAI/Gemini key 放入 `.env`（或在系統環境變數中設定）。
   - 把 Google OAuth client（`credentials.json`）放在 `阿嚕米/` 資料夾。
2. 運行（安全測試，建議先用 DRY_RUN）
   - 在 PowerShell 中執行：
     ```powershell
     $env:DRY_RUN='1'; python agent_main.py
     ```
   - 程式會載入 `.env`，嘗試呼叫 LLM（若配額或導入問題會自動退回 Mock），然後以 Mock 或真實方式建立活動。
3. 若要進行真實寫入
   - 移除 `DRY_RUN` 環境變數（或設為 '0'），並執行 `python agent_main.py`。
   - 首次啟動若沒有 `token.pickle`，會透過瀏覽器進行 OAuth 流程以取得授權，之後會儲存 `token.pickle`。

## 事件建立流程（high-level）
1. 使用者輸入自然語言請求（如："請幫我安排一個與導師會面，時間是今天晚上 8 點到 9 點"）。
2. `run_agent` 解析請求：
   - 嘗試以 LLM 對話方式讓模型選擇是否要呼叫 `schedule_calendar_event`（若使用 OpenAI function-calling 風格）。
   - 若 LLM 不可用或發生錯誤，使用 Mock 解析（簡單的 regex 抽取 summary 與時間片段），再呼叫 `create_calendar_event`。
3. `schedule_calendar_event` 會將自然語言時間轉為 'YYYY-MM-DD HH:MM:SS'（若時間已是該格式則直接使用），再呼叫 `create_calendar_event`。
4. `create_calendar_event` 根據 `DRY_RUN` 決定是否呼叫 Google Calendar API 寫入事件，並回傳成功/錯誤訊息。

## 已知的邊界情況與假設
- 假設：使用者給出的時間能用簡單中文段落解析（"今天/明天/後天" 與數字小時），較複雜的自然語言（如「下下週三下午」或中文大寫數字）可能無法正確解析。
- 若 LLM 配額不足或導入錯誤，系統會自動退回 Mock 流程，並以 DRY_RUN 為保護機制避免意外寫入。
- OAuth 的互動需要使用者在本機完成授權（瀏覽器），因此執行真實寫入需要能夠打開瀏覽器並完成授權。

## 日誌與偵錯
- 日誌使用 logger 名稱 `agent`，同時輸出到終端與 `logs/agent.log`（rotating，1MB/檔，5 個備份）。
- 日誌會包含：啟動時的環境狀態（是否有 API key、DRY_RUN）、LLM 呼叫錯誤、Mock 流程中的解析結果、Google API 呼叫回傳結果等。

## 測試與開發
- 執行 parser 的單元測試：
  ```powershell
  # 在 project/阿嚕米 資料夾並啟動 venv
  .\.venv\Scripts\Activate.ps1
  pytest test_time_parser.py -q
  ```
- 若要擴充 parser，可以在 `calendar_time_parser.py` 中增加對 "下週/下下週/下個月" 等詞的解析（例如先解析 week/day offset 再合成 datetime），並為此加入對應的 pytest 測試。

## 如何切換模式（快速參考）
- 安全（Mock/不寫入）：
  ```powershell
  $env:DRY_RUN='1'; python agent_main.py
  ```
- 嘗試使用 OpenAI（若 `.env` 裡有 `OPENAI_API_KEY` 並且帳戶有配額）：
  ```powershell
  Remove-Item Env:\DRY_RUN -ErrorAction SilentlyContinue
  python agent_main.py
  ```

## 延伸建議（短期）
- 新增 CLI 參數用以明確控制模式（--force-mock / --force-live / --verbose / --log-file）。
- 強化 `calendar_time_parser` 的測試集，加入 "下週一"、中文大寫數字等語句的測試。

---
若你想要我現在開始擴充 parser 的功能（例如加入 "下週一" 的解析），或是把這份文件合併到 `README.md` 中，我可以接著做。