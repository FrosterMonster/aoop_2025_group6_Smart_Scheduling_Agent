import datetime
import sys
import time
import json
from pathlib import Path
from typing import Optional, Dict, Any
from dotenv import load_dotenv
from src.tools.calendar import CalendarTool
from src.agent.scheduling_agent import SchedulingAgent

# 載入環境變數
load_dotenv()

class SchedulingSession:
    """管理調度會話的狀態和歷史記錄"""
    
    def __init__(self, cooldown: int = 12):
        self.cooldown = cooldown
        self.history = []
        self.session_start = datetime.datetime.now()
        self.request_count = 0
        self.last_request_time = None
        
    def add_interaction(self, query: str, response: str, timestamp: datetime.datetime):
        """記錄互動歷史"""
        self.history.append({
            'timestamp': timestamp.isoformat(),
            'query': query,
            'response': response
        })
        self.request_count += 1
        self.last_request_time = timestamp
    
    def get_stats(self) -> Dict[str, Any]:
        """獲取會話統計資訊"""
        duration = datetime.datetime.now() - self.session_start
        return {
            'session_duration': str(duration).split('.')[0],
            'total_requests': self.request_count,
            'history_size': len(self.history)
        }
    
    def save_history(self, filepath: str = "session_history.json"):
        """保存會話歷史到文件"""
        try:
            data = {
                'session_start': self.session_start.isoformat(),
                'session_end': datetime.datetime.now().isoformat(),
                'stats': self.get_stats(),
                'history': self.history
            }
            with open(filepath, 'w', encoding='utf-8') as f:
                json.dump(data, f, ensure_ascii=False, indent=2)
            return True
        except Exception as e:
            print(f"⚠️ Failed to save history: {e}")
            return False
    
    def should_cooldown(self) -> bool:
        """檢查是否需要冷卻"""
        if self.last_request_time is None:
            return False
        elapsed = (datetime.datetime.now() - self.last_request_time).total_seconds()
        return elapsed < self.cooldown


class ColoredOutput:
    """終端機彩色輸出"""
    HEADER = '\033[95m'
    BLUE = '\033[94m'
    CYAN = '\033[96m'
    GREEN = '\033[92m'
    YELLOW = '\033[93m'
    RED = '\033[91m'
    ENDC = '\033[0m'
    BOLD = '\033[1m'
    
    @staticmethod
    def print_header(text: str):
        print(f"{ColoredOutput.HEADER}{ColoredOutput.BOLD}{text}{ColoredOutput.ENDC}")
    
    @staticmethod
    def print_info(text: str):
        print(f"{ColoredOutput.CYAN}{text}{ColoredOutput.ENDC}")
    
    @staticmethod
    def print_success(text: str):
        print(f"{ColoredOutput.GREEN}{text}{ColoredOutput.ENDC}")
    
    @staticmethod
    def print_warning(text: str):
        print(f"{ColoredOutput.YELLOW}{text}{ColoredOutput.ENDC}")
    
    @staticmethod
    def print_error(text: str):
        print(f"{ColoredOutput.RED}{text}{ColoredOutput.ENDC}")


def print_banner():
    """顯示啟動橫幅"""
    banner = """
╔══════════════════════════════════════════════════╗
║   🤖 Smart Scheduling Agent - Interactive Mode   ║
║     (Rate Limit Protection: 12s cooldown)        ║
╚══════════════════════════════════════════════════╝
"""
    ColoredOutput.print_header(banner)


def print_help():
    """顯示幫助信息"""
    help_text = """
📋 Available Commands:
  • exit/quit/bye    - Exit the program
  • help             - Show this help message
  • stats            - Show session statistics
  • history          - Show recent interaction history
  • save             - Save session history to file
  • clear            - Clear screen
  • status           - Show agent status

💡 Usage Tips:
  • Ask in natural language (English or Chinese)
  • Examples:
    - "Schedule a meeting tomorrow at 3 PM"
    - "Show my calendar for next week"
    - "Find free time slots this afternoon"
"""
    ColoredOutput.print_info(help_text)


def print_stats(session: SchedulingSession):
    """顯示會話統計"""
    stats = session.get_stats()
    ColoredOutput.print_info(f"""
📊 Session Statistics:
  • Duration: {stats['session_duration']}
  • Total Requests: {stats['total_requests']}
  • History Entries: {stats['history_size']}
""")


def print_history(session: SchedulingSession, limit: int = 5):
    """顯示最近的互動歷史"""
    if not session.history:
        ColoredOutput.print_warning("📝 No interaction history yet.")
        return
    
    ColoredOutput.print_info(f"\n📜 Recent History (last {limit} entries):")
    for entry in session.history[-limit:]:
        timestamp = datetime.datetime.fromisoformat(entry['timestamp'])
        time_str = timestamp.strftime("%H:%M:%S")
        print(f"\n[{time_str}]")
        print(f"  Q: {entry['query'][:80]}{'...' if len(entry['query']) > 80 else ''}")
        print(f"  A: {entry['response'][:80]}{'...' if len(entry['response']) > 80 else ''}")


def clear_screen():
    """清除螢幕"""
    import os
    os.system('cls' if os.name == 'nt' else 'clear')


def handle_command(command: str, session: SchedulingSession) -> bool:
    """處理特殊命令，返回 True 表示應該繼續循環"""
    cmd = command.lower().strip()
    
    if cmd in ['exit', 'quit', 'bye']:
        return False
    elif cmd == 'help':
        print_help()
    elif cmd == 'stats':
        print_stats(session)
    elif cmd == 'history':
        print_history(session)
    elif cmd == 'save':
        if session.save_history():
            ColoredOutput.print_success("✅ History saved to session_history.json")
        else:
            ColoredOutput.print_error("❌ Failed to save history")
    elif cmd == 'clear':
        clear_screen()
        print_banner()
    elif cmd == 'status':
        ColoredOutput.print_success("✅ Agent is ready and operational")
        print_stats(session)
    else:
        return None  # 不是命令，是正常查詢
    
    return True


def main():
    # 初始化
    print_banner()
    ColoredOutput.print_info("Type 'help' for available commands")
    print("-" * 52)
    
    session = SchedulingSession(cooldown=12)
    
    try:
        calendar_tool = CalendarTool()
        my_agent = SchedulingAgent(tools=[calendar_tool])
        ColoredOutput.print_success("✅ Agent initialized successfully\n")
    except Exception as e:
        ColoredOutput.print_error(f"❌ Initialization Error: {e}")
        return
    
    # 主循環
    while True:
        try:
            # 獲取當前時間
            now = datetime.datetime.now()
            today_str = now.strftime("%Y-%m-%d (%A)")
            current_time_str = now.strftime("%H:%M")
            
            # 獲取用戶輸入
            print(f"\n[{today_str} {current_time_str}]")
            user_input = input("👤 You: ").strip()
            
            if not user_input:
                continue
            
            # 檢查是否為命令
            cmd_result = handle_command(user_input, session)
            if cmd_result is False:
                ColoredOutput.print_success("👋 Goodbye! Thanks for using the scheduling agent.")
                if session.history:
                    save_prompt = input("\n💾 Save session history? (y/n): ").strip().lower()
                    if save_prompt == 'y':
                        session.save_history()
                        ColoredOutput.print_success("✅ History saved!")
                break
            elif cmd_result is True:
                continue
            
            # 正常查詢處理
            full_query = f"Current Date/Time: {today_str} {current_time_str}. User Query: {user_input}"
            
            ColoredOutput.print_info("🤖 Agent is thinking...")
            
            # 執行 Agent
            query_start = time.time()
            response = my_agent(full_query)
            query_duration = time.time() - query_start
            
            # 記錄互動
            session.add_interaction(user_input, response, now)
            
            # 顯示結果
            print(f"\n🤖 Agent: {response}")
            ColoredOutput.print_info(f"⏱️  Response time: {query_duration:.2f}s")
            
            # 冷卻機制
            if session.should_cooldown():
                remaining = session.cooldown - (datetime.datetime.now() - session.last_request_time).total_seconds()
                if remaining > 0:
                    ColoredOutput.print_warning(f"\n⏳ Cooling down for {remaining:.1f}s to avoid rate limits...")
                    time.sleep(remaining)
            else:
                ColoredOutput.print_warning(f"\n⏳ Cooling down for {session.cooldown}s to avoid rate limits...")
                time.sleep(session.cooldown)
            
            ColoredOutput.print_success("✅ Ready for next command!")
            
        except KeyboardInterrupt:
            print("\n")
            ColoredOutput.print_warning("⚠️  Interrupted by user")
            break
        except Exception as e:
            ColoredOutput.print_error(f"\n❌ Error: {e}")
            ColoredOutput.print_warning("Type 'help' for available commands or 'status' to check agent status")


if __name__ == "__main__":
    main()