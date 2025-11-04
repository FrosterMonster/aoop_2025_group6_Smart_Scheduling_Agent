# group_6

快速說明
---------------
這個資料夾包含一個使用 LangChain 與 Google Calendar API 的範例代理（Agent），可以由 LLM 在需要時建立 Google Calendar 活動。

快速上手
---------------
1. 建立虛擬環境並啟用（Windows PowerShell）

```powershell
python -m venv .venv; .\.venv\Scripts\Activate.ps1
```

2. 安裝依賴（請在 `阿嚕米` 資料夾內執行）

```powershell
pip install -r requirements.txt
```

3. 建立 `.env` 檔並加入您的 Gemini/LLM API Key

```
GEMINI_API_KEY=your_real_api_key_here
```

4. 取得 Google OAuth credentials
   - 在 Google Cloud Console 建立 OAuth Client ID（Desktop app），下載 `credentials.json`，並放到本資料夾。

5. 第一次執行會觸發瀏覽器授權流程以建立 `token.pickle`：

```powershell
python agent_main.py
```

6. 測試時間解析（已包含簡單單元測試）：

```powershell
# 在阿嚕米 資料夾
pytest test_time_parser.py -q
```

注意事項
---------------
- 不要把 API key 或憑證硬編碼到程式中，請使用 `.env` 與 `credentials.json`。
- 在 headless 或 server 環境部署時，OAuth 互動式流程可能需要替代方案（service account 或事先建立 token）。
# 整體流程與執行模式（快速說明）

下面簡短說明本專案在啟動、解析與建立日曆事件時的主要流程，以及可選模式與日誌等級設定。

1) 啟動流程
- 程式會載入 `.env`（若存在）來讀取 `OPENAI_API_KEY`、`GEMINI_API_KEY`、`DRY_RUN` 等變數。
- 會檢查 `credentials.json` 與 `token.pickle` 是否存在（並在日誌中記錄，但不列印秘密）。

2) 模式（Mode）
- Mock / DRY_RUN（安全，預設保護）: 若環境中沒有可用 LLM，或 `DRY_RUN=1`，系統會使用內建的 Mock 流程解析使用者輸入並模擬建立事件（不會寫入 Google Calendar）。
- Live + LLM 驅動（風險較高）: 若 `.env` 有 `OPENAI_API_KEY`（或其他 provider）且配額與套件可用，系統會嘗試呼叫 LLM 進行 function-calling 並在必要時呼叫 `create_calendar_event` 實際寫入日曆。
- 強制模式（可選）: 可加入 CLI 開關（尚未預設）如 `--force-mock` / `--force-live` 來明確控制行為。

3) 日誌等級（Log level）
- INFO: 預設會記錄啟動狀態、主要行為（如已選擇哪個模式、Mock 的解析結果、DRY_RUN 模擬），適合一般使用。
- DEBUG: 更詳細的執行資訊（例如解析的中間值、更多的例外堆疊），已啟用為預設開發等級，並會輸出至 `logs/agent.log`。
- ERROR/WARNING: 用於記錄失敗與警示（例如 LLM 呼叫錯誤、Google API 失敗）。

4) 如何以安全模式測試（推薦）
```powershell
$env:DRY_RUN='1'; python agent_main.py
```

5) 如何切換到嘗試 LLM 與真實寫入
 - 移除 `DRY_RUN` 環境變數或設為空，確保 `.env` 裡有正確的 `OPENAI_API_KEY`，並執行：
```powershell
Remove-Item Env:\DRY_RUN -ErrorAction SilentlyContinue
python agent_main.py
```

日誌檔案位置: `阿嚕米/logs/agent.log`（rotating，1MB，5 個備份）。

如需我把 CLI 開關加到程式中（例如 `--force-mock` / `--force-live` / `--log-file`），或把 README 中的內容再整理成更短的「快速參考」，請告訴我。
# group_6