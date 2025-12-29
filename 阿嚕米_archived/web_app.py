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
    data = request.get_json()
    user_text = data.get('text', '').strip()

    if not user_text:
        return jsonify({'error': '沒有輸入文字'}), 400

    try:
        result = parse_with_ai(user_text)
        # ✅ 一律回 200，不管是 AI 還是 fallback
        return jsonify(result)

    except Exception as e:
        print("[PARSE_NL ERROR]", e)
        return jsonify({'error': '解析失敗'}), 500

@app.route('/schedule', methods=['POST'])
@login_required
def schedule():
    if request.method == 'POST':
        try:
            service = get_calendar_service()

            # ---------- 來自前端的基本資料 ----------
            summary = request.form.get('summary', '').strip()
            hours = float(request.form.get('hours', 1.0) or 1.0)
            target_date = request.form.get('date') or datetime.now().strftime('%Y-%m-%d')
            start_time_str = request.form.get('start_time')
            recurrence = request.form.get('recurrence') or None
            is_flexible = request.form.get('is_flexible') == 'true'

            inserted_events = []
            errors = []

            # ---------- 情況 A：彈性行程 ----------
            if is_flexible:
                planned = plan_week_schedule(
                    service,
                    summary,
                    hours,
                    start_from=target_date
                )

                if not planned:
                    return render_template(
                        'schedule.html',
                        error="找不到可用的空檔，請嘗試其他日期或縮短時數。"
                    )

                for p in planned:
                    event_body = {
                        'summary': summary,
                        'start': {
                            'dateTime': p['start'].isoformat(),
                            'timeZone': 'Asia/Taipei'
                        },
                        'end': {
                            'dateTime': p['end'].isoformat(),
                            'timeZone': 'Asia/Taipei'
                        },
                        'description': 'AI 自動排入（彈性行程）'
                    }

                    service.events().insert(
                        calendarId='primary',
                        body=event_body
                    ).execute()

                    inserted_events.append({
                        'time': p['start'].strftime('%Y-%m-%d %H:%M'),
                        'result': '彈性行程已新增'
                    })

            # ---------- 情況 B：固定行程 ----------
            else:
                if not start_time_str:
                    raise ValueError("固定行程必須指定開始時間")

                start_dt = datetime.strptime(
                    f"{target_date} {start_time_str}",
                    '%Y-%m-%d %H:%M'
                )
                end_dt = start_dt + timedelta(hours=hours)

                event_body = {
                    'summary': summary,
                    'start': {
                        'dateTime': start_dt.isoformat(),
                        'timeZone': 'Asia/Taipei'
                    },
                    'end': {
                        'dateTime': end_dt.isoformat(),
                        'timeZone': 'Asia/Taipei'
                    }
                }

                # recurrence（正確套用）
                if recurrence == 'DAILY':
                    event_body['recurrence'] = ['RRULE:FREQ=DAILY']
                elif recurrence == 'WEEKLY':
                    event_body['recurrence'] = ['RRULE:FREQ=WEEKLY']

                service.events().insert(
                    calendarId='primary',
                    body=event_body
                ).execute()

                inserted_events.append({
                    'time': f"{target_date} {start_time_str}",
                    'result': '固定行程已新增'
                })

            return render_template(
                'schedule.html',
                success=True,
                events=inserted_events
            )

        except Exception as e:
            return render_template('schedule.html', error=str(e))

    # GET
    return render_template('schedule.html')

if __name__ == '__main__':
    app.run(debug=True, port=5000)