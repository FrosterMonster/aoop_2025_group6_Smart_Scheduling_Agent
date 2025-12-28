"""Flask web application for Smart Scheduling Agent."""
from flask import Flask, render_template, request, redirect, url_for, session, jsonify
from functools import wraps
import os
from datetime import datetime, timedelta

# 確保這些 import 指向你正確的檔案
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
    data = request.get_json()
    user_text = data.get('text', '')
    if not user_text:
        return jsonify({'error': '沒有輸入文字'}), 400

    ai_result = parse_with_ai(user_text)
    if ai_result:
        # 確保 AI 回傳的 JSON 包含 date (YYYY-MM-DD), start_time (HH:mm), is_flexible (bool)
        return jsonify(ai_result)
    else:
        return jsonify({'error': 'AI 解析失敗'}), 500

@app.route('/schedule', methods=['POST'])
@login_required
def schedule():
    summary = request.form.get('summary')
    hours = float(request.form.get('hours', 1.0))
    is_flexible = request.form.get('is_flexible') == 'true'
    start_time_str = request.form.get('start_time')
    recurrence = request.form.get('recurrence')
    
    # 修正：從前端接收 AI 解析的日期，若無則預設今天
    target_date = request.form.get('date') or datetime.now().strftime('%Y-%m-%d')

    try:
        service = get_calendar_service()
        
        if is_flexible:
            # 模式 A: 彈性找空檔 (現在會從 target_date 開始找)
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
                
                # 格式化顯示時間
                for p in planned_events:
                    p['time'] = p['start'].strftime('%Y-%m-%d %H:%M')
                return render_template('schedule.html', success=True, events=planned_events)
            else:
                return render_template('schedule.html', error="所有日曆都滿了，找不到空檔！")

        else:
            # 模式 B: 固定時間 (使用正確的日期)
            start_dt = datetime.strptime(f"{target_date} {start_time_str}", '%Y-%m-%d %H:%M')
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
                                   events=[{'time': f"{target_date} {start_time_str}", 'result': '固定行程已新增'}])

    except Exception as e:
        return render_template('schedule.html', error=str(e))

if __name__ == '__main__':
    app.run(debug=True, port=5000)