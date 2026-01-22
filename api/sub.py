import telebot
import requests
import json
import base64
from datetime import datetime, timedelta

# ТВОИ ДАННЫЕ
TOKEN = '8028112233:AAEFVmd_dDtHoKOWOxuS224O-sP3fQXfDMQ'
GITHUB_TOKEN = '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'
REPO = 'matvei-droid/zuubackvpn'
FILE_PATH = 'api/users.json'
ADMIN_ID = 8096288610  # ВСТАВЬ СВОЙ ID СЮДА

bot = telebot.TeleBot(TOKEN)

def get_github_file():
    url = f"https://api.github.com/repos/{REPO}/contents/{FILE_PATH}"
    headers = {"Authorization": f"token {GITHUB_TOKEN}"}
    r = requests.get(url, headers=headers)
    content = r.json()
    data = json.loads(base64.b64decode(content['content']).decode('utf-8'))
    return data, content['sha']

@bot.message_handler(commands=['add'])
def add_user(message):
    # ПРОВЕРКА НА АДМИНА
    if message.from_user.id != ADMIN_ID:
        bot.reply_to(message, "❌ Тебе нельзя управлять этим ботом!")
        return

    try:
        args = message.text.split()
        new_user = args[1]
        days = int(args[2]) if len(args) > 2 else 30
        
        # Считаем дату удаления
        expire_date = (datetime.now() + timedelta(days=days)).strftime("%Y-%m-%d")
        
        data, sha = get_github_file()
        
        # Добавляем юзера с датой истечения
        data[new_user] = {
            "status": "active",
            "expire": expire_date,
            "total": 10737418240  # 10 ГБ
        }
        
        updated_content = base64.b64encode(json.dumps(data, indent=2).encode('utf-8')).decode('utf-8')
        url = f"https://api.github.com/repos/{REPO}/contents/{FILE_PATH}"
        headers = {"Authorization": f"token {GITHUB_TOKEN}"}
        payload = {"message": f"Add user {new_user} for {days} days", "content": updated_content, "sha": sha}
        
        requests.put(url, headers=headers, json=payload)
        bot.reply_to(message, f"✅ Юзер {new_user} добавлен на {days} дней (до {expire_date})!\n🔗 https://zuubackvpn.vercel.app/api/sub?user={new_user}")
    except Exception as e:
        bot.reply_to(message, f"❌ Ошибка: {e}\nПример: /add ivan 30")

bot.polling()
