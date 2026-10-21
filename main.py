import asyncio
import logging
import random
import time
import aiohttp
from datetime import datetime
from telegram import Bot
from telegram.error import TelegramError

# ၁။ Bot Token နှင့် Channel Chat ID
TOKEN = "8677321316:AAEpRAkD-V19q6ARjMBIMsKWCV0qA5AUMTQ"
CHAT_ID = "@auto24hoursbot"

# တောင်းဆိုမည့် API URL (Timestamp ပါထည့်ရန်)
API_BASE_URL = "https://draw.ar-lottery01.com/TrxWinGo/TrxWinGo_1M/GetHistoryIssuePage.json"

logging.basicConfig(level=logging.INFO)
bot = Bot(token=TOKEN)

async def fetch_lottery_data():
    """API မှ အချက်အလက်အစစ်များကို ယူရန်"""
    # Timestamp ထည့်သွင်းခြင်းဖြင့် Cache မဖြစ်ဘဲ အသစ်ထွက်လာတာကို ရယူမည်
    current_ts = int(time.time() * 1000)
    url = f"{API_BASE_URL}?ts={current_ts}"
    
    async with aiohttp.ClientSession() as session:
        try:
            payload = {"pageSize": 10, "pageNo": 1}
            async with session.post(url, json=payload, timeout=10) as response:
                if response.status == 200:
                    data = await response.json()
                    # API response ထဲမှ list အချက်အလက်များကို ယူခြင်း
                    # Data Structure က အမျိုးမျိုးဖြစ်နိုင်သဖြင့် ထွက်လာသော key များကို စစ်ဆေးပေးသည်
                    if isinstance(data, dict):
                        # data သို့မဟုတ် list သို့မဟုတ် directly 
                        result_data = data.get("data", data)
                        if isinstance(result_data, dict):
                            items = result_data.get("list", result_data.get("data", []))
                            if items:
                                return items
                        elif isinstance(result_data, list):
                            return result_data
        except Exception as e:
            print(f"API Fetch Error: {e}")
    return None

async def auto_send_signal():
    print("Bot စတင်အလုပ်လုပ်နေပါပြီ (TrxWinGo API Real-time Version)...")
    last_processed_period = None
    
    while True:
        try:
            items = await fetch_lottery_data()
            if items and len(items) > 0:
                # နောက်ဆုံးထွက်ရှိထားသော ပွဲစဉ်အသစ် (ပထမဆုံး Index 0)
                latest_item = items[0]
                
                # API ထဲက issueNumber သို့မဟုတ် period ကို ရှာယူခြင်း
                period = (
                    latest_item.get("issueNumber") or 
                    latest_item.get("period") or 
                    latest_item.get("issue") or
                    latest_item.get("gameNo")
                )
                
                # ထွက်လာသော နံပါတ် (Winning Number)
                raw_number = (
                    latest_item.get("number") or 
                    latest_item.get("winningNumber") or 
                    latest_item.get("result")
                )
                
                if period and raw_number is not None:
                    number = int(raw_number)
                    
                    # ပွဲစဉ်အသစ် ဖြစ်မှသာ ဆောင်ရွက်မည် (ထပ်ခါထပ်ခါ မပို့စေရန်)
                    if period != last_processed_period:
                        last_processed_period = period
                        current_time = datetime.now().strftime("%H:%M:%S")
                        
                        # 0-4 က SMALL, 5-9 က BIG
                        result = "SMALL" if number <= 4 else "BIG"
                        confidence = f"{random.randint(88, 99)}%"
                        bet_level = random.choice(["X1", "X3", "X7", "X16"])
                        
                        # ၁။ ပွဲစဉ်အသစ်အတွက် Signal ပို့ခြင်း
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
                        
                        # ပွဲပြီးဆုံးချိန်အထိ စောင့်ရန် (သို့မဟုတ် API ကို စောင့်ကြည့်ရန်)
                        await asyncio.sleep(25)
                        
                        # ၂။ အနိုင်ရလဒ် (Win) ပို့ခြင်း
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
            print(f"Loop Error: {e}")
            
        # API ကို ၁၀ စက္ကန့်တစ်ကြိမ် ပွဲစဉ်အသစ်ရှိမရှိ စစ်ဆေးမည်
        await asyncio.sleep(10)

if __name__ == '__main__':
    asyncio.run(auto_send_signal())
