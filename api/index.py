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
        # استخدام API Telegram للتحقق من صحة التوكن
        url = f"https://api.telegram.org/bot{token}/getMe"
        response = requests.get(url)
        return response.status_code == 200 and response.json().get("ok", False)
    except Exception as e:
        print(f"Error validating token: {e}")
        return False

# دالة لبدء تشغيل البوت
def start_bot(token):
    bot_instance = telebot.TeleBot(token)

    @bot_instance.message_handler(commands=['xaz'])
    def handle_xaz_command(message):
        # الرسالة الأساسية بالعربية
        response_text = (
            "**تم إرسال طلب للسيرفر، قريبًا سيتم إضافة هذا البوت لسيرفر XAZ، يُرجى الانتظار 🤖**\n\n"
            "**🔹 XAZ Team Official Links 🔹**\n"
            "🌍 **Source Group:** [XAZ Team Source](https://t.me/xazteam)\n"
            "🌍 **New Team Group:** [Join XAZ Team](https://t.me/+nuACUoH_xn05NjE0)\n"
            "🌍 **XAZ Team Official Website:** [Visit Website](https://xaz-team-website.free.bg/)\n\n"
            "**🌍 XAZ Team Official Website 🌍**\n"
            "⚠ **Note:** If the page doesn't load completely, try enabling PC Mode for the best experience.\n"
            "Stay safe and always verify official sources! 💙"
        )
        bot_instance.reply_to(message, response_text, parse_mode='Markdown', disable_web_page_preview=True)

    @bot_instance.message_handler(func=lambda message: True)
    def handle_message(message):
        # تجاهل الرسائل الأخرى
        pass

    # بدء الاستماع للرسائل
    bot_instance.polling(none_stop=True, skip_pending=True)

# API لإضافة توكن
@app.route('/add_bot', methods=['POST'])
def add_bot():
    data = request.json
    token = data.get('token')

    if not token:
        return jsonify({'error': 'Token is required'}), 400

    # التحقق من صحة التوكن
    if not is_valid_token(token):
        return jsonify({'error': 'Invalid token'}), 400

    # تخزين البوت وبدء تشغيله
    bots[token] = {'status': 'active'}
    threading.Thread(target=start_bot, args=(token,)).start()

    return jsonify({'message': 'Bot added successfully', 'token': token})

# API لاستعادة جميع التوكنات باستخدام مفتاح سري
@app.route('/get_tokens', methods=['GET'])
def get_tokens():
    # التحقق من المفتاح السري
    provided_key = request.args.get('key')
    if provided_key != SECRET_KEY:
        return jsonify({'error': 'Unauthorized'}), 401

    # إرجاع جميع التوكنات
    return jsonify({'tokens': list(bots.keys())})

# API لإيقاف جميع البوتات
@app.route('/stop_bots', methods=['POST'])
def stop_bots():
    # التحقق من المفتاح السري
    provided_key = request.json.get('key')
    if provided_key != SECRET_KEY:
        return jsonify({'error': 'Unauthorized'}), 401

    # إيقاف جميع البوتات
    for token in bots.keys():
        bot_instance = telebot.TeleBot(token)
        bot_instance.stop_polling()

    # مسح جميع التوكنات
    bots.clear()

    return jsonify({'message': 'All bots stopped successfully'})

# تشغيل سيرفر Flask
if __name__ == '__main__':
    app.run(port=5000)
