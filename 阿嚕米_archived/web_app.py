"""Flask web application for Smart Scheduling Agent."""
from flask import Flask, render_template, request, redirect, url_for, session, jsonify
from functools import wraps
import os
from datetime import datetime, timedelta

# 確保引用路徑正確
from calendar_tools import plan_week_schedule, get_calendar_service
from calendar_service import TOKEN_FILE
from calendar_time_parser import parse_with_ai 

app = Flask(__name__)
app.secret_key = os.urandom(24)

def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
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
    get_calendar_service()
    return redirect(url_for('index'))

@app.route('/api/parse_nl', methods=['POST'])
def api_parse_nl():
    """處理前端傳來的自然語言，呼叫 Gemini 解析日期、時間與彈性標籤"""
    data = request.get_json()
    user_text = data.get('text', '')
    if not user_text:
        return jsonify({'error': '沒有輸入文字'}), 400

    ai_result = parse_with_ai(user_text)
    if ai_result:
        # ai_result 應包含 date, start_time, title, is_flexible, is_recurring
        return jsonify(ai_result)
    else:
        return jsonify({'error': 'AI 解析失敗'}), 500

@app.route('/schedule', methods=['GET', 'POST'])
@login_required
def schedule():
    if request.method == 'POST':
        summary = request.form.get('summary')
        hours = float(request.form.get('hours', 1.0))
        is_flexible = request.form.get('is_flexible') == 'true'
        start_time_str = request.form.get('start_time')
        recurrence = request.form.get('recurrence')
        
        # 接收解析日期，若無則預設為今天
        target_date = request.form.get('date') or datetime.now().strftime('%Y-%m-%d')

        try:
            service = get_calendar_service()
            
            if is_flexible:
                # 模式 A: 跨日曆自動搜尋空檔
                # 傳入 target_date 讓搜尋從指定的日期開始
                planned_events = plan_week_schedule(service, summary, hours, start_from=target_date)
                
                if planned_events:
                    for p in planned_events:
                        event_body = {
                            'summary': summary,
                            'start': {'dateTime': p['start'].isoformat(), 'timeZone': 'Asia/Taipei'},
                            'end': {'dateTime': p['end'].isoformat(), 'timeZone': 'Asia/Taipei'},
                            'description': 'AI 跨日曆偵測後自動排入'
                        }
                        service.events().insert(calendarId='primary', body=event_body).execute()
                    
                    # 格式化前端顯示的時間
                    for p in planned_events:
                        p['time'] = p['start'].strftime('%Y-%m-%d %H:%M')
                    return render_template('schedule.html', success=True, events=planned_events)
                else:
                    return render_template('schedule.html', error="抱歉，所選日期的所有日曆皆已客滿，找不到空檔。")

            else:
                # 模式 B: 固定時間行程
                start_dt = datetime.strptime(f"{target_date} {start_time_str}", '%Y-%m-%d %H:%M')
                end_dt = start_dt + timedelta(hours=hours)

                event_body = {
                    'summary': summary,
                    'start': {'dateTime': start_dt.isoformat(), 'timeZone': 'Asia/Taipei'},
                    'end': {'dateTime': end_dt.isoformat(), 'timeZone': 'Asia/Taipei'},
                }
                
                # 處理重複性行程（如每天、每週）
                if recurrence == 'DAILY':
                    event_body['recurrence'] = ['RRULE:FREQ=DAILY']
                elif recurrence == 'WEEKLY':
                    event_body['recurrence'] = ['RRULE:FREQ=WEEKLY']

                service.events().insert(calendarId='primary', body=event_body).execute()
                return render_template('schedule.html', success=True, 
                                       events=[{'time': f"{target_date} {start_time_str}", 'result': '固定行程已成功新增'}])

        except Exception as e:
            return render_template('schedule.html', error=str(e))

    # GET 請求時直接返回排程頁面
    return render_template('schedule.html')

if __name__ == '__main__':
    app.run(debug=True, port=5000)