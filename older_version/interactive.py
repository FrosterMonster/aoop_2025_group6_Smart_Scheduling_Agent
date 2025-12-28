import datetime
import sys
from dotenv import load_dotenv
from src.tools.calendar import CalendarTool
from src.agent.scheduling_agent import SchedulingAgent

# 載入環境變數 (API Key)
load_dotenv()

def main():
    print("==================================================")
    print("🤖 Smart Scheduling Agent - Interactive Mode")
    print("==================================================")
    print("Type 'exit', 'quit', or 'bye' to stop the program.")
    print("-" * 50)

    # 1. 初始化工具與 Agent
    # (這裡我們不需要改動 Agent 的程式碼，直接引用 Week 4 完成的版本)
    try:
        calendar_tool = CalendarTool()
        my_agent = SchedulingAgent(tools=[calendar_tool])
    except Exception as e:
        print(f"❌ Initialization Error: {e}")
        return

    # 2. 進入互動迴圈
    while True:
        try:
            # 獲取現在的日期與時間 (讓 Agent 永遠知道當下時間)
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

            # C. 組合 Context (關鍵！把日期資訊塞進去)
            # 這樣你只要說「明天下午」，Agent 就知道是哪一天
            full_query = f"Current Date/Time: {today_str} {current_time_str}. User Query: {user_input}"

            print("🤖 Agent is thinking...", end="", flush=True)

            # D. 執行 Agent
            # (注意：這裡會觸發 Agent 的 Thought/Action/Observation 思考過程)
            response = my_agent(full_query)

            # E. 顯示結果
            # (LangChain 的 verbose=True 已經會印出詳細過程，這裡我們印出最終回答)
            print(f"\n🤖 Agent: {response}")

        except KeyboardInterrupt:
            # 捕捉 Ctrl+C
            print("\n\n👋 Forced exit. Bye!")
            break
        except Exception as e:
            print(f"\n❌ Error: {e}")

if __name__ == "__main__":
    main()