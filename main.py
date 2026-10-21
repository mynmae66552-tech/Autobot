
import asyncio
import logging
import random
from datetime import datetime
from telegram import Bot
from telegram.error import TelegramError

# ၁။ Bot Token နှင့် Channel Chat ID
TOKEN = "8677321316:AAEpRAkD-V19q6ARjMBIMsKWCV0qA5AUMTQ"
CHAT_ID = "@auto24hoursbot"

logging.basicConfig(level=logging.INFO)
bot = Bot(token=TOKEN)

async def auto_send_signal():
    period = 5100010569  # စတင်မည့် Period နံပါတ်
    
    # သင်တောင်းဆိုထားသော ဖော်မြူလာ အစဉ်လိုက် (S, B, S, B, S, S, B, B)
    formula_pattern = ["SMALL", "BIG", "SMALL", "BIG", "SMALL", "SMALL", "BIG", "BIG"]
    pattern_index = 0
    
    print("Bot စတင်အလုပ်လုပ်နေပါပြီ...")
    
    while True:
        period += 1
        current_time = datetime.now().strftime("%H:%M:%S")
        
        # ဖော်မြူလာအတိုင်း Small / Big တစ်ခုချင်းစီ ယူရန်
        result = formula_pattern[pattern_index]
        pattern_index = (pattern_index + 1) % len(formula_pattern)
        
        confidence = f"{random.randint(8, 25)}%"
        
        # လောင်းကြေးအဆင့်များ
        bet_level = random.choice(["X1", "X3", "X7", "X16", "X36", "X76"])
        
        # ၂။ ပထမဆုံး Signal မက်ဆေ့ပို့ခြင်း
        signal_msg = (
            f"⏰ ပွဲစဉ်အချိန် : {current_time}\n"
            f"✅ PERIOD : {period}\n"
            f"💰 လောင်းကြေးအဆင့် = {bet_level}\n"
            f"🎯 စနစ်ခန့်မှန်း : {result}\n"
            f"📊 နိုင်ခြေ ရာခိုင်နှုန်း : {confidence}\n\n"
            "Ai Developer : @flash687"
        )
        
        try:
            await bot.send_message(chat_id=CHAT_ID, text=signal_msg)
            print(f"Period {period} Signal ({result}) ပို့ပြီးပါပြီ။")
        except TelegramError as e:
            print(f"Error sending signal: {e}")
            
        # ပွဲပြီးဆုံးချိန်အထိ (၄၅ စက္ကန့်) စောင့်မည်
        await asyncio.sleep(45)
        
        # ၃။ Result နှင့် ညီမျှသော Winning Number ကို သတ်မှတ်ခြင်း
        if result == "SMALL":
            winning_number = random.randint(0, 4)  # 0 မှ 4 အတွင်း (Small)
        else:
            winning_number = random.randint(5, 9)  # 5 မှ 9 အတွင်း (Big)
            
        win_msg = (
            "🏆 WIN – အနိုင်ရလဒ် 🎉\n\n"
            f"✅ PERIOD : {period}\n"
            f"🎯 ခန့်မှန်းချက် : {result}\n"
            f"📌 အမှန့်ရလဒ် : {result}\n"
            f"🔢 NUMBER : {winning_number}\n"
            f"💯 CONFIDENCE : {confidence}\n\n"
            "Ai Developer : @flash687"
        )
        
        try:
            # WIN ပုံလင့်ခ်
            photo_url = "https://images.unsplash.com/photo-1518609878373-06d740f60d8b?w=500"
            await bot.send_photo(chat_id=CHAT_ID, photo=photo_url, caption=win_msg, parse_mode='Markdown')
            print(f"Period {period} Win ရလဒ် ပို့ပြီးပါပြီ။")
        except TelegramError as e:
            print(f"Error sending win message: {e}")
            
        # နောက်ထပ် ပွဲစဉ်အသစ်အတွက် ၁၅ စက္ကန့် စောင့်ပါ
        await asyncio.sleep(15)

if __name__ == '__main__':
    asyncio.run(auto_send_signal())
