import requests

def send_msg(text):
    token = '6467771760:AAE7Cf8TBNW8aZ1RI99Y7ShzMRRhgAvRTGM'
    chat_id = '-4288017681'
    url = f'https://api.telegram.org/bot{token}/sendMessage?chat_id={chat_id}&text={text}'
    requests.get(url)


message_text = 'Hello from your bot! Captech'
send_msg(message_text)
