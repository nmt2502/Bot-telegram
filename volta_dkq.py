
import asyncio
import aiohttp
import logging
import math
from telegram import Bot
from telegram.constants import ParseMode

# --- CẤU HÌNH (ĐÃ TÍCH SẴN TOKEN + CHAT_ID) ---
TOKEN = "8595477726:AAFVWI0G1ytx56K5pJrUs801dex5_SOlYz8"
CHAT_ID = "8213006748"
API_URL = "https://voltasun.onrender.com/api/volta/sun"

logging.basicConfig(format='%(asctime)s - %(levelname)s - %(message)s', level=logging.INFO)

class VoltaBot:
    def __init__(self):
        self.bot = Bot(token=TOKEN)
        self.last_md5 = None
        self.last_prediction = None
        self.is_checked_result = True

    async def fetch_data(self):
        try:
            async with aiohttp.ClientSession() as session:
                async with session.get(API_URL, timeout=5) as response:
                    return await response.json()
        except Exception:
            return None

    def pro_analyze_md5(self, md5_str):
        hex_values = [int(char, 16) for char in md5_str]
        total_sum = sum(hex_values)
        core_weight = (hex_values[0] + hex_values[-1] + hex_values[15])

        if (total_sum + core_weight) % 2 == 0:
            raw_prediction = "Đội nhà thắng"
        else:
            raw_prediction = "Đội khách thắng"

        prediction = "Đội nhà thắng" if raw_prediction == "Đội khách thắng" else "Đội khách thắng"

        variance = sum((x - (total_sum/32))**2 for x in hex_values) / 32
        confidence = 65 + (math.sqrt(variance) % 30)

        return prediction, f"{confidence:.1f}%"

    async def run(self):
        print("🚀 Volta Bot đang chạy (TOKEN đã tích sẵn trong code)")

        while True:
            data = await self.fetch_data()
            if data and "md5_hien_tai" in data:
                current_md5 = data.get("md5_hien_tai")

                if current_md5 != self.last_md5:
                    if self.last_md5 is not None and not self.is_checked_result:
                        ket_qua_that = data.get("ket_qua", "")
                        danh_gia = "✅ ĐÚNG" if self.last_prediction in ket_qua_that else "❌ SAI"

                        msg_kq = (
                            f"📋 *KẾT QUẢ PHIÊN TRƯỚC*\n\n"
                            f"🔑 MD5: `{data.get('md5_truoc')}`\n"
                            f"📊 Kết quả thật: *{ket_qua_that}*\n"
                            f"🎯 Dự đoán: *{self.last_prediction}*\n"
                            f"📋 Đánh giá: {danh_gia}"
                        )
                        await self.bot.send_message(chat_id=CHAT_ID, text=msg_kq, parse_mode=ParseMode.MARKDOWN)
                        self.is_checked_result = True
                        await asyncio.sleep(1.5)

                    self.last_md5 = current_md5
                    prediction, confidence = self.pro_analyze_md5(current_md5)
                    self.last_prediction = prediction
                    self.is_checked_result = False

                    msg_predict = (
                        f"📡 *TÍN HIỆU MỚI*\n\n"
                        f"🔑 MD5: `{current_md5}`\n"
                        f"🔮 Dự đoán: `{prediction}`\n"
                        f"📈 Độ tin cậy: `{confidence}`"
                    )
                    await self.bot.send_message(chat_id=CHAT_ID, text=msg_predict, parse_mode=ParseMode.MARKDOWN)

            await asyncio.sleep(3)

if __name__ == "__main__":
    asyncio.run(VoltaBot().run())
