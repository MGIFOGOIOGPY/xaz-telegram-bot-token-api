from flask import Flask, request, jsonify
import telebot
import threading
import requests
import os

app = Flask(__name__)

# تخزين البوتات (Dictionary لتخزين كائنات البوتات)
bots = {}

# مفتاح سري لاستعادة التوكنات
SECRET_KEY = os.getenv("SECRET_KEY", "xazow9wowgowwy29wi282r30wyw0wuoewgwowfepwpwy19192828827297282738383eueo")

# دالة للتحقق من صحة التوكن
def is_valid_token(token):
    try:
        url = f"https://api.telegram.org/bot{token}/getMe"
        response = requests.get(url)
        response.raise_for_status()
        return response.json().get("ok", False)
    except requests.RequestException as e:
        print(f"❌ Error validating token: {e}")
        return False

# دالة لبدء تشغيل البوت
def start_bot(token):
    bot_instance = telebot.TeleBot(token)
    
    @bot_instance.message_handler(commands=['xaz'])
    def handle_xaz_command(message):
        response_text = (
            "**✅ تم إرسال طلب للسيرفر، سيتم إضافة هذا البوت قريبًا لسيرفر XAZ. يُرجى الانتظار! 🤖**\n\n"
            "**🔹 XAZ Team Official Links 🔹**\n"
            "🌍 **Source Group:** [XAZ Team Source](https://t.me/xazteam)\n"
            "🌍 **New Team Group:** [Join XAZ Team](https://t.me/+nuACUoH_xn05NjE0)\n"
            "🌍 **XAZ Team Official Website:** [Visit Website](https://xaz-team-website.free.bg/)\n\n"
            "**🌍 XAZ Team Official Website 🌍**\n"
            "⚠ **Note:** إذا لم تعمل الصفحة بشكل صحيح، قم بتفعيل **PC Mode** لأفضل تجربة."
        )
        bot_instance.reply_to(message, response_text, parse_mode='Markdown', disable_web_page_preview=True)

    # تخزين كائن البوت في القاموس
    bots[token] = bot_instance

    bot_instance.polling(none_stop=True, skip_pending=True)

# API لإضافة توكن
@app.route('/add_bot', methods=['POST'])
def add_bot():
    data = request.json
    token = data.get('token')

    if not token:
        return jsonify({'error': 'Token is required'}), 400

    if not is_valid_token(token):
        return jsonify({'error': 'Invalid token'}), 400

    if token in bots:
        return jsonify({'error': 'Bot already running'}), 400

    # تشغيل البوت في Thread منفصل
    thread = threading.Thread(target=start_bot, args=(token,), daemon=True)
    thread.start()

    return jsonify({'message': 'Bot added successfully', 'token': token})

# API لاستعادة جميع التوكنات باستخدام مفتاح سري
@app.route('/get_tokens', methods=['GET'])
def get_tokens():
    provided_key = request.args.get('key')
    if provided_key != SECRET_KEY:
        return jsonify({'error': 'Unauthorized'}), 401

    return jsonify({'tokens': list(bots.keys())})

# API لإيقاف جميع البوتات
@app.route('/stop_bots', methods=['POST'])
def stop_bots():
    provided_key = request.json.get('key')
    if provided_key != SECRET_KEY:
        return jsonify({'error': 'Unauthorized'}), 401

    for token, bot_instance in bots.items():
        bot_instance.stop_polling()

    bots.clear()

    return jsonify({'message': 'All bots stopped successfully'})

# تشغيل سيرفر Flask
if __name__ == '__main__':
    app.run(port=5000)
