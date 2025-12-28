import datetime
import sys
import time  # 引入時間模組來做冷卻
from dotenv import load_dotenv
from src.tools.calendar import CalendarTool
from src.agent.scheduling_agent import SchedulingAgent

# 載入環境變數
load_dotenv()

def main():
    print("==================================================")
    print("🤖 Smart Scheduling Agent - Interactive Mode")
    print("   (Rate Limit Protection Enabled: 12s cooldown)")
    print("==================================================")
    print("Type 'exit', 'quit', or 'bye' to stop the program.")
    print("-" * 50)

    # 1. 初始化工具與 Agent
    try:
        calendar_tool = CalendarTool()
        my_agent = SchedulingAgent(tools=[calendar_tool])
    except Exception as e:
        print(f"❌ Initialization Error: {e}")
        return

    # 2. 進入互動迴圈
    while True:
        try:
            # 獲取現在的日期與時間
            now = datetime.datetime.now()
            today_str = now.strftime("%Y-%m-%d (%A)")
            current_time_str = now.strftime("%H:%M")

            # A. 等待使用者輸入
            print(f"\n[{today_str} {current_time_str}]")
            user_input = input("👤 You: ").strip()

            # B. 檢查離開指令
            if user_input.lower() in ['exit', 'quit', 'bye']:
                print("👋 See you later!")
                break
            
            if not user_input:
                continue

            # C. 組合 Context
            full_query = f"Current Date/Time: {today_str} {current_time_str}. User Query: {user_input}"

            print("🤖 Agent is thinking...", end="", flush=True)

            # D. 執行 Agent
            response = my_agent(full_query)

            # E. 顯示結果
            print(f"\n🤖 Agent: {response}")

            # ▼▼▼ 自動冷卻機制 (關鍵!) ▼▼▼
            # Google 免費版限制每分鐘 5 次請求，為了避免 429 錯誤，
            # 我們強制休息 12 秒 (60秒 / 5次 = 12秒)
            print("\n(⏳ Cooling down for 12s to avoid rate limits...)")
            time.sleep(12)
            print("(✅ Ready for next command!)")

        except KeyboardInterrupt:
            print("\n\n👋 Forced exit. Bye!")
            break
        except Exception as e:
            print(f"\n❌ Error: {e}")

if __name__ == "__main__":
    main()