from flask import Flask, render_template, request, jsonify, session
from googletrans import Translator
import openai
import os
import logging

app = Flask(__name__)
app.secret_key = os.environ.get('SECRET_KEY', 'your_default_secret_key')
openai.api_key = os.environ.get('OPENAI_API_KEY')  # کلید API را از متغیر محیطی بخوان
translator = Translator()

logging.basicConfig(level=logging.INFO)

def process_input(user_input):
    user_input = user_input.strip()

    if 'history' not in session:
        session['history'] = []

    session['history'].append(user_input)

    # پاسخ‌های ساده برای برخی دستورات فارسی
    if user_input == "اسم من چیست؟":
        name = session.get('name', "نامی به من نگفتید لطفا نام خود را جهت آشنایی به من بگویید.")
        return f"نام شما: {name}"
    
    elif user_input == "وضعیت سلامتی من چیست؟":
        health = session.get('health', 'وضعیت سلامتی ثبت نشده است.')
        return f"وضعیت سلامتی شما: {health}"
    
    elif user_input == "من در کجا هستم؟":
        location = session.get('location', 'محل زندگی ثبت نشده است.')
        return f"محل زندگی شما: {location}"

    if user_input.startswith("اسم من "):
        name = user_input.replace("اسم من ", "").strip()
        session['name'] = name
        return f"نام شما به {name} تغییر یافت."
    
    elif user_input.startswith("من سالم هستم"):
        session['health'] = "سالم"
        return "وضعیت سلامتی شما ثبت شد."
    
    elif user_input.startswith("من در "):
        location = user_input.replace("من در ", "").strip()
        session['location'] = location
        return f"محل زندگی شما به {location} تغییر یافت."

    # ترجمه پرسش به انگلیسی برای ارسال به GPT
    try:
        translated_input = translator.translate(user_input, dest='en').text
    except Exception as e:
        logging.error(f"Translation error: {e}")
        return "متاسفانه در ترجمه سوال مشکل پیش آمد."

    try:
        response = openai.ChatCompletion.create(
            model="gpt-4",  # یا gpt-3.5-turbo در صورت محدودیت
            messages=[
                {"role": "system", "content": "You are a helpful assistant."},
                {"role": "user", "content": translated_input}
            ]
        )
        ai_response = response['choices'][0]['message']['content']
    except Exception as e:
        logging.error(f"OpenAI API error: {e}")
        return "در ارتباط با هوش مصنوعی مشکلی پیش آمد."

    # ترجمه پاسخ به فارسی
    try:
        translated_response = translator.translate(ai_response, dest='fa').text
    except Exception as e:
        logging.error(f"Translation error: {e}")
        return "متاسفانه در ترجمه پاسخ مشکل پیش آمد."

    return translated_response

@app.route('/')
def home():
    session.clear()
    return render_template('index.html')

@app.route('/ask', methods=['POST'])
def ask():
    user_input = request.form['user_input']
    response = process_input(user_input)
    return jsonify({'response': response})

@app.route('/history', methods=['GET'])
def history():
    history = session.get('history', [])
    return jsonify({'history': history})

if __name__ == "__main__":
    app.run(debug=True)
