
import asyncio
import aiohttp
import logging
import math
from telegram import Bot
from telegram.constants import ParseMode

# --- CẤU HÌNH ---
TOKEN = "8595477726:AAFVWI0G1ytx56K5pJrUs801dex5_SOlYz8"
API_URL = "https://voltasun.onrender.com/api/volta/sun"
CHAT_ID = "8213006748" 

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
        """Thuật toán Volta-Pro Phân tích MD5"""
        # 1. Tính tổng giá trị Hex của toàn bộ chuỗi 32 ký tự
        hex_values = [int(char, 16) for char in md5_str]
        total_sum = sum(hex_values)
        
        # 2. Thuật toán xác định đội thắng (Cân bằng động)
        # Sử dụng vị trí trung tâm và trọng số cuối
        core_weight = (hex_values[0] + hex_values[-1] + hex_values[15])
        if (total_sum + core_weight) % 2 == 0:
            prediction = "Đội nhà thắng"
        else:
            prediction = "Đội khách thắng"
            
        # 3. Tính độ tin cậy dựa trên độ lệch chuẩn giả lập
        variance = sum((x - (total_sum/32))**2 for x in hex_values) / 32
        confidence = 65 + (math.sqrt(variance) % 30) # Dao động từ 65% - 95%
        
        return prediction, f"{confidence:.1f}%"

    async def run(self):
        print(f"🚀 Volta-Pro Bot đang quét... (ID: {CHAT_ID})")
        
        while True:
            data = await self.fetch_data()
            if data and "md5_hien_tai" in data:
                current_md5 = data.get("md5_hien_tai")
                
                if current_md5 != self.last_md5:
                    # GỬI KẾT QUẢ PHIÊN CŨ
                    if self.last_md5 is not None and not self.is_checked_result:
                        ket_qua_that = data.get("ket_qua", "")
                        # So khớp thông minh
                        danh_gia = "✅ ĐÚNG" if self.last_prediction in ket_qua_that else "❌ SAI"
                        
                        msg_kq = (
                            f"📋 **KẾT QUẢ PHIÊN TRƯỚC**\n\n"
                            f"🔑 MD5: `{data.get('md5_truoc')}`\n"
                            f"⚽ Trận: {data.get('doi_nha_van_truoc')} vs {data.get('doi_khach_van_truoc')}\n"
                            f"----------------------------\n"
                            f"📊 Kết quả thật: **{ket_qua_that}**\n"
                            f"🎯 Dự đoán: **{self.last_prediction}**\n"
                            f"📋 Đánh giá: {danh_gia}"
                        )
                        try:
                            await self.bot.send_message(chat_id=CHAT_ID, text=msg_kq, parse_mode=ParseMode.MARKDOWN)
                        except Exception as e:
                            logging.error(f"Lỗi gửi KQ: {e}")
                        
                        self.is_checked_result = True
                        await asyncio.sleep(1.5) # Delay nhỏ để tránh spam

                    # GỬI DỰ ĐOÁN PHIÊN MỚI
                    self.last_md5 = current_md5
                    prediction, confidence = self.pro_analyze_md5(current_md5)
                    self.last_prediction = prediction
                    self.is_checked_result = False

                    msg_predict = (
                        f"📡 **TÍN HIỆU MỚI**\n\n"
                        f"🔑 Mã MD5: `{current_md5}`\n"
                        f"⚽ Trận đấu: **{data.get('doi_nha')}** 🆚 **{data.get('doi_khach')}**\n"
                        f"----------------------------\n"
                        f"🔮 Dự đoán: `{prediction}`\n"
                        f"📈 Độ tin cậy: `{confidence}`\n"
                        f"⚠️ *Lưu ý: Phân tích dựa trên thuật toán MD5*"
                    )
                    try:
                        await self.bot.send_message(chat_id=CHAT_ID, text=msg_predict, parse_mode=ParseMode.MARKDOWN)
                    except Exception as e:
                        logging.error(f"Lỗi gửi Dự đoán: {e}")

            await asyncio.sleep(3)

if __name__ == "__main__":
    bot_logic = VoltaBot()
    try:
        asyncio.run(bot_logic.run())
    except KeyboardInterrupt:
        print("Bot Stopped.")
    
