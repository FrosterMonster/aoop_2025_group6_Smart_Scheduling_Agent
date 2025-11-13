"""Flask web application for Smart Scheduling Agent."""
from flask import Flask, render_template, request, redirect, url_for, session, jsonify
from functools import wraps
import os
from datetime import datetime
import pytz

from calendar_tools import plan_week_schedule, get_calendar_service
from calendar_service import TOKEN_FILE

app = Flask(__name__)
app.secret_key = os.urandom(24)  # for session management

def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'credentials' not in session:
            return redirect(url_for('login'))
        return f(*args, **kwargs)
    return decorated_function

@app.route('/')
def index():
    """首頁：顯示登入狀態和功能選單。"""
    is_logged_in = os.path.exists(TOKEN_FILE)
    return render_template('index.html', is_logged_in=is_logged_in)

@app.route('/login')
def login():
    """Google OAuth 登入。"""
    if os.path.exists(TOKEN_FILE):
        os.remove(TOKEN_FILE)  # 清除舊的認證
    # 觸發 OAuth 流程
    get_calendar_service()
    return redirect(url_for('index'))

@app.route('/schedule', methods=['GET', 'POST'])
@login_required
def schedule():
    """排程表單和處理。"""
    if request.method == 'POST':
        summary = request.form['summary']
        hours = float(request.form['hours'])
        chunk = float(request.form.get('chunk', 2.0))
        
        # 執行排程
        try:
            planned = plan_week_schedule(
                summary=summary,
                total_hours=hours,
                chunk_hours=chunk,
                daily_window=(9, 22)  # 預設 9am-10pm
            )
            
            # 格式化結果
            events = []
            for p in planned:
                start = p['start'].strftime('%Y-%m-%d %H:%M')
                end = p['end'].strftime('%Y-%m-%d %H:%M')
                events.append({
                    'time': f'{start} - {end}',
                    'result': p['result']
                })
            
            return render_template('schedule.html', 
                                 success=True,
                                 summary=summary,
                                 hours=hours,
                                 events=events)
        
        except Exception as e:
            return render_template('schedule.html', 
                                 error=str(e))
    
    return render_template('schedule.html')

@app.route('/logout')
def logout():
    """登出（移除認證）。"""
    if os.path.exists(TOKEN_FILE):
        os.remove(TOKEN_FILE)
    session.clear()
    return redirect(url_for('index'))

if __name__ == '__main__':
    app.run(debug=True, port=5000)