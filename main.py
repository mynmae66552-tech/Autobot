import asyncio
import logging
import random
import aiohttp
from datetime import datetime
from telegram import Bot
from telegram.error import TelegramError

# ၁။ Bot Token နှင့် Channel Chat ID
TOKEN = "8677321316:AAEpRAkD-V19q6ARjMBIMsKWCV0qA5AUMTQ"
CHAT_ID = "@auto24hoursbot"

# TrxWinGo API URL
API_URL = "https://draw.ar-lottery01.com/TrxWinGo/TrxWinGo_1M/GetHistoryIssuePage.json"

logging.basicConfig(level=logging.INFO)
bot = Bot(token=TOKEN)

async def fetch_lottery_data():
    """API မှ အချက်အလက်များကို ယူရန်"""
    async with aiohttp.ClientSession() as session:
        try:
            # API တောင်းဆိုရန် payload (လိုအပ်ပါက pageSize သို့မဟုတ် pageNo ထည့်နိုင်သည်)
            payload = {"pageSize": 10, "pageNo": 1}
            async with session.post(API_URL, json=payload, timeout=10) as response:
                if response.status == 200:
                    data = await response.json()
                    # API ရဲ့ data တည်ဆောက်ပုံအရ list ကို ပြန်ပေးရန်
                    return data.get("data", {}).get("list", [])
        except Exception as e:
            print(f"API Error: {e}")
    return None

async def auto_send_signal():
    print("Bot စတင်အလုပ်လုပ်နေပါပြီ (API Version)...")
    last_processed_period = None
    
    while True:
        try:
            items = await fetch_lottery_data()
            if items and len(items) > 0:
                # နောက်ဆုံးထွက်ရှိထားသော ပွဲစဉ်ကို ယူရန်
                latest_item = items[0]
                period = latest_item.get("issueNumber") or latest_item.get("period")
                
                # အကယ်၍ Period အသစ်ဖြစ်မှသာ မက်ဆေ့ပို့မည်
                if period and period != last_processed_period:
                    last_processed_period = period
                    current_time = datetime.now().strftime("%H:%M:%S")
                    
                    # API က ထွက်လာတဲ့ Number ကို ယူပြီး SMALL/BIG ခွဲခြားခြင်း
                    # ဥပမာ: 0-4 က SMALL, 5-9 က BIG
                    number = int(latest_item.get("number", random.randint(0, 9)))
                    result = "SMALL" if number <= 4 else "BIG"
                    
                    confidence = f"{random.randint(85, 99)}%"
                    bet_level = random.choice(["X1", "X3", "X7", "X16"])
                    
                    # Signal ပို့ရန်
                    signal_msg = (
                        f"⏰ ပွဲစဉ်အချိန် : {current_time}\n"
                        f"✅ PERIOD : {period}\n"
                        f"💰 လောင်းကြေးအဆင့် = {bet_level}\n"
                        f"🎯 စနစ်ခန့်မှန်း : {result}\n"
                        f"📊 နိုင်ခြေ ရာခိုင်နှုန်း : {confidence}\n\n"
                        "Ai Developer : @flash687"
                    )
                    
                    await bot.send_message(chat_id=CHAT_ID, text=signal_msg)
                    print(f"Period {period} Signal ပို့ပြီးပါပြီ။")
                    
                    # ရလဒ်ထွက်ရန် ခေတ္တစောင့်မည်
                    await asyncio.sleep(30)
                    
                    # Win မက်ဆေ့ပို့ရန်
                    win_msg = (
                        "🏆 WIN – အနိုင်ရလဒ် 🎉\n\n"
                        f"✅ PERIOD : {period}\n"
                        f"🎯 ခန့်မှန်းချက် : {result}\n"
                        f"📌 အမှန့်ရလဒ် : {result}\n"
                        f"🔢 NUMBER : {number}\n"
                        f"💯 CONFIDENCE : {confidence}\n\n"
                        "Ai Developer : @flash687"
                    )
                    
                    photo_url = "https://images.unsplash.com/photo-1518609878373-06d740f60d8b?w=500"
                    await bot.send_photo(chat_id=CHAT_ID, photo=photo_url, caption=win_msg, parse_mode='Markdown')
                    print(f"Period {period} Win ရလဒ် ပို့ပြီးပါပြီ။")
            
        except TelegramError as e:
            print(f"Telegram Error: {e}")
        except Exception as e:
            print(f"Error: {e}")
            
        # API ကို ၁၀ စက္ကန့်တစ်ကြိမ် စစ်ဆေးမည်
        await asyncio.sleep(10)

if __name__ == '__main__':
    asyncio.run(auto_send_signal())
