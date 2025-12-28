# 阿嚕米（Alumi）
### AI 智能全日曆助理（Smart Scheduling Agent）

---

## 專案簡介（Introduction）

**阿嚕米（Alumi）** 是一個結合自然語言理解（LLM）、時間解析與 Google Calendar API 的智慧行程助理。  
使用者可以透過接近日常語言的中文指令（例如：「明天早上十點健身三小時」、「明天找空檔讀書」），由系統自動解析並建立對應的行事曆事件。

本專案著重於 **工程穩定性、可維護性與安全性**，即使在 LLM 不可用的情況下，系統仍能透過 rule-based fallback 正常運作。

---

## 功能特色（Features）

- ✅ 中文自然語言時間解析（今天 / 明天 / 上午 / 下午 / 幾點 / 幾小時）
- ✅ 支援固定行程與彈性行程（找空檔）
- ✅ Google Calendar API 寫入
- ✅ OAuth2 使用者授權
- ✅ DRY_RUN 安全模式（避免誤寫入）
- ✅ LLM 不可用時自動退回 rule-based fallback
- ✅ 完整日誌紀錄（終端機 + log 檔）

---

## 專案結構（Project Structure）

