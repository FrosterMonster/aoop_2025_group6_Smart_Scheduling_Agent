"""Flask web application for Smart Scheduling Agent."""
from flask import Flask, render_template, request, redirect, url_for, session, jsonify
from functools import wraps
import os

# 確保這些 import 正確指向你的檔案
from calendar_tools import plan_week_schedule, get_calendar_service
from calendar_service import TOKEN_FILE
from calendar_time_parser import parse_with_ai  # 這是 AI 解析的核心

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
    summary = request.form['summary']
    hours = float(request.form['hours'])
    start_time = request.form.get('start_time') # 拿到 21:00
    recurrence = request.form.get('recurrence') # 拿到 DAILY
    
    try:
        service = get_calendar_service()
        
        # 這裡需要修改你的 calendar_tools.py 或是直接在這邊呼叫 Google API
        # 如果有 start_time，就建立固定時間的行程
        # 如果沒有，才跑 plan_week_schedule 找空檔
        
        # 範例：簡單處理固定時間與重複
        event = {
            'summary': summary,
            'start': {
                'dateTime': f'2025-12-28T{start_time}:00', # 這裡日期要處理，可用 datetime.now()
                'timeZone': 'Asia/Taipei',
            },
            'end': {
                'dateTime': f'2025-12-28T22:00:00', # 計算結束時間
                'timeZone': 'Asia/Taipei',
            }
        }
        
        if recurrence == 'DAILY':
            event['recurrence'] = ['RRULE:FREQ=DAILY']
            
        service.events().insert(calendarId='primary', body=event).execute()
        return render_template('schedule.html', success=True)
        
    except Exception as e:
        return render_template('schedule.html', error=str(e))
if __name__ == '__main__':
    app.run(debug=True, port=5000)