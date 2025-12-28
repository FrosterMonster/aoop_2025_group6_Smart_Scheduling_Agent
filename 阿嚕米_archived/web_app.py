"""Flask web application for Smart Scheduling Agent."""
from flask import Flask, render_template, request, redirect, url_for, session, jsonify
from functools import wraps
import os

# 確保這些 import 正確指向你的檔案
from calendar_tools import plan_week_schedule, get_calendar_service
from calendar_service import TOKEN_FILE
from calendar_time_parser import parse_with_ai  # 這是 AI 解析的核心

from datetime import datetime, timedelta

app = Flask(__name__)
app.secret_key = os.urandom(24)

def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        # 如果 Token 檔案存在，我們視為已登入
        if not os.path.exists(TOKEN_FILE):
            return redirect(url_for('login'))
        return f(*args, **kwargs)
    return decorated_function

@app.route('/')
def index():
    is_logged_in = os.path.exists(TOKEN_FILE)
    return render_template('index.html', is_logged_in=is_logged_in)

@app.route('/login')
def login():
    if os.path.exists(TOKEN_FILE):
        os.remove(TOKEN_FILE)
    get_calendar_service()  # 觸發瀏覽器授權
    return redirect(url_for('index'))

# --- 關鍵修正：新增 AI 解析 API 端點 ---
@app.route('/api/parse_nl', methods=['POST'])
def api_parse_nl():
    """處理前端傳來的自然語言，呼叫 Gemini 並回傳 JSON"""
    data = request.get_json()
    user_text = data.get('text', '')
    
    if not user_text:
        return jsonify({'error': '沒有輸入文字'}), 400

    # 呼叫你寫好的 Gemini 解析邏輯
    ai_result = parse_with_ai(user_text)
    
    if ai_result:
        return jsonify(ai_result)
    else:
        return jsonify({'error': 'AI 解析失敗，請檢查 API Key'}), 500

@app.route('/schedule', methods=['POST'])
@login_required
def schedule():
    summary = request.form.get('summary')
    hours = float(request.form.get('hours', 1.0))
    is_flexible = request.form.get('is_flexible') == 'true'
    start_time_str = request.form.get('start_time')
    recurrence = request.form.get('recurrence')

    try:
        service = get_calendar_service()
        
        # --- 模式 A: 彈性找空檔 ---
        if is_flexible:
            # 1. 先找出空檔 (回傳 list)
            planned_events = plan_week_schedule(service, summary, hours)
            
            # 2. 關鍵修正：將找到的空檔正式「寫入」Google 日曆
            if planned_events:
                for p in planned_events:
                    event_body = {
                        'summary': summary,
                        'start': {'dateTime': p['start'].isoformat(), 'timeZone': 'Asia/Taipei'},
                        'end': {'dateTime': p['end'].isoformat(), 'timeZone': 'Asia/Taipei'},
                        'description': 'AI 自動尋找空檔排入'
                    }
                    service.events().insert(calendarId='primary', body=event_body).execute()
                
                # 為了讓前端顯示正確時間，我們格式化一下顯示字串
                for p in planned_events:
                    p['time'] = p['start'].strftime('%Y-%m-%d %H:%M')
                
                return render_template('schedule.html', success=True, events=planned_events)
            else:
                return render_template('schedule.html', error="找不到合適的空檔")

        # --- 模式 B: 固定時間 ---
        else:
            # (這部分你原本應該已經成功了，保持原樣即可)
            today_str = datetime.now().strftime('%Y-%m-%d')
            start_dt = datetime.strptime(f"{today_str} {start_time_str}", '%Y-%m-%d %H:%M')
            end_dt = start_dt + timedelta(hours=hours)

            event_body = {
                'summary': summary,
                'start': {'dateTime': start_dt.isoformat(), 'timeZone': 'Asia/Taipei'},
                'end': {'dateTime': end_dt.isoformat(), 'timeZone': 'Asia/Taipei'},
            }
            if recurrence == 'DAILY':
                event_body['recurrence'] = ['RRULE:FREQ=DAILY']

            service.events().insert(calendarId='primary', body=event_body).execute()
            return render_template('schedule.html', success=True, 
                                   events=[{'time': f"{start_time_str}", 'result': '固定行程已新增'}])

    except Exception as e:
        return render_template('schedule.html', error=str(e))
if __name__ == '__main__':
    app.run(debug=True, port=5000)