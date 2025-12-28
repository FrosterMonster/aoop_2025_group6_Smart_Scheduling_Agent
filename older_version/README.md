# 🤖 Smart Scheduling Agent (Group 6)

An intelligent, context-aware scheduling assistant powered by **Google Gemini LLM**, **LangChain**, and **Streamlit**.

## 🌟 Key Features (Project Highlights)
This project goes beyond simple API calls by implementing a robust agentic architecture:

* **🧠 Persistent Memory (SQLite)**: The agent remembers user preferences (e.g., "I don't work on Fridays") across sessions using a local SQL database.
* **🌤️ Context Awareness (Weather Tool)**: Automatically checks weather conditions before booking outdoor activities.
* **🛡️ Safety Mechanisms**: Human-in-the-loop validation for destructive actions (e.g., deleting events).
* **🧪 Automated Testing**: Full test coverage using `pytest` to ensure tool reliability.
* **🎨 Modern UI**: A responsive chat interface built with Streamlit.

## 🛠️ Tech Stack
* **Core**: Python 3.11, LangChain (ReAct Agent)
* **LLM**: Google Gemini 1.5 Flash
* **Frontend**: Streamlit
* **Database**: SQLite3
* **Testing**: Pytest

## 🚀 Quick Start

1. **Install Dependencies**
   ```bash
   pip install -r requirements.txt
Setup Credentials Create a .env file and add your API keys:

程式碼片段

GOOGLE_API_KEY=your_gemini_api_key
GOOGLE_ACCOUNT_FILE=credentials.json
Run the Application

Bash

streamlit run app.py
Run Unit Tests

Bash

pytest
📂 Project Structure
Plaintext

├── app.py                  # Streamlit Frontend
├── src/
│   ├── agent/              # Agent Logic (LangChain)
│   ├── tools/              # Custom Tools (Weather, Calendar, Preferences)
│   └── database.py         # SQL Database Manager
├── tests/                  # Unit Test Suite
├── requirements.txt        # Dependencies
└── README.md               # Documentation

---

### 3. 最後的整合測試 (Final Check)
雖然 API 現在可能還是 429 錯誤，但我們要確認**程式能不能跑起來**（沒有語法錯誤）。

請執行：
```powershell
streamlit run app.py