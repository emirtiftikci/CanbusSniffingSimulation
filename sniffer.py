import can
import json
import os
import argparse
import logging
from datetime import datetime

# Genel günlük kaydı (log) ayarları: Hata ve bilgi mesajları için
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    handlers=[
        logging.FileHandler("can_listener.log"),  # Hata ve bilgi logları
        logging.StreamHandler()  # Ekrana yaz
    ]
)
logger = logging.getLogger(__name__)

# Mesajlar için ayrı bir log dosyası ayarları
message_logger = logging.getLogger("message_logger")
message_handler = logging.FileHandler("messages.log")  # Mesajlar için ayrı log dosyası
message_handler.setFormatter(logging.Formatter("%(asctime)s [%(levelname)s] %(message)s"))
message_logger.addHandler(message_handler)
message_logger.setLevel(logging.INFO)

# Komut satırı argümanları: CAN arayüzü, veritabanı ve mesaj dosyalarını ayarlar
parser = argparse.ArgumentParser(description="CAN veri yolu mesaj dinleyici ve gönderici")
parser.add_argument("--channel", default="vcan0", help="Kullanılacak CAN arayüzü (varsayılan: vcan0)")
parser.add_argument("--database", default="database.json", help="Veritabanı dosyası (varsayılan: database.json)")
parser.add_argument("--messages", default="messages.json", help="Mesaj eşleme dosyası (varsayılan: messages.json)")
args = parser.parse_args()

DATABASE_FILE = args.database
MESSAGES_FILE = args.messages

# Varsayılan mesaj eşlemeleri (messages.json yoksa kullanılır)
DEFAULT_MESSAGE_MAPPINGS = {
    "0x123": {
        "1122334455667788": "Kapı açma komutu",
        "2200000000000000": "Far açma komutu",
        "default": "Bilinmeyen alt komut"
    },
    "0x124": {
        "default": "Cam açma komutu"
    }
}

# Veritabanını yükle veya boş bir sözlük oluştur
database = {}
if os.path.exists(DATABASE_FILE):
    try:
        with open(DATABASE_FILE, "r") as file:
            database = json.load(file)
            if not isinstance(database, dict):
                logger.error(f"{DATABASE_FILE} dosyası geçerli bir JSON nesnesi değil. Boş veritabanı başlatılıyor.")
                database = {}
            # Eski formatta (metin) girişleri yeni formata çevir
            for can_id in list(database.keys()):
                if isinstance(database[can_id], str):
                    logger.warning(f"Eski formatta veri bulundu: {can_id}. Yeni formata çevriliyor.")
                    database[can_id] = {
                        "description": database[can_id],
                        "first_seen": datetime.now().isoformat(),
                        "last_seen": datetime.now().isoformat(),
                        "count": 1
                    }
    except json.JSONDecodeError as e:
        logger.error(f"{DATABASE_FILE} dosyası geçersiz JSON formatında: {e}. Boş veritabanı başlatılıyor.")
        database = {}
else:
    logger.info(f"{DATABASE_FILE} dosyası bulunamadı. Yeni veritabanı oluşturuluyor.")

# Mesaj eşlemelerini yükle veya varsayılanı kullan
message_mappings = DEFAULT_MESSAGE_MAPPINGS
if os.path.exists(MESSAGES_FILE):
    try:
        with open(MESSAGES_FILE, "r") as file:
            message_mappings = json.load(file)
            if not isinstance(message_mappings, dict):
                logger.warning(f"{MESSAGES_FILE} dosyası geçerli bir JSON nesnesi değil. Varsayılan eşlemeler kullanılıyor.")
                message_mappings = DEFAULT_MESSAGE_MAPPINGS
    except json.JSONDecodeError as e:
        logger.warning(f"{MESSAGES_FILE} dosyası geçersiz JSON formatında: {e}. Varsayılan eşlemeler kullanılıyor.")
else:
    logger.info(f"{MESSAGES_FILE} dosyası bulunamadı. Varsayılan mesaj eşlemeleri kullanılıyor.")

def save_database():
    """Veritabanını JSON dosyasına kaydet."""
    try:
        with open(DATABASE_FILE, "w") as file:
            json.dump(database, file, indent=4)
        logger.debug(f"Veritabanı {DATABASE_FILE} dosyasına kaydedildi.")
    except Exception as e:
        logger.error(f"Veritabanı kaydedilemedi: {e}")

def format_can_id(arac_id):
    """CAN ID'sini onaltılık (hex) formatına çevir."""
    try:
        return f"0x{arac_id:X}"
    except (TypeError, ValueError):
        logger.error(f"Geçersiz CAN ID: {arac_id}")
        return None

def interpret_message(can_id, data_hex):
    """CAN mesajını ID ve veriye göre yorumla."""
    if not isinstance(can_id, str) or not can_id.startswith("0x"):
        logger.warning(f"Geçersiz CAN ID formatı: {can_id}")
        return None
    if not all(c in "0123456789ABCDEFabcdef" for c in data_hex):
        logger.warning(f"Geçersiz veri formatı: {data_hex}")
        return None

    if can_id in message_mappings:
        return message_mappings[can_id].get(data_hex, message_mappings[can_id].get("default", None))
    return None

def send_message(bus, can_id, data):
    """CAN mesajı gönder ve logla."""
    try:
        # CAN ID'sini tamsayıya çevir
        can_id_int = int(can_id, 16) if isinstance(can_id, str) else can_id
        # Veriyi baytlara çevir
        data_bytes = bytes.fromhex(data) if isinstance(data, str) else data
        msg = can.Message(arbitration_id=can_id_int, data=data_bytes, is_extended_id=False)
        bus.send(msg)
        anlam = interpret_message(format_can_id(can_id_int), data_bytes.hex())
        log_message = f"GÖNDERİLDİ [{format_can_id(can_id_int)}] {anlam or 'Tanımsız mesaj'} | Veri: {data_bytes.hex()}"
        message_logger.info(log_message)
        logger.info(log_message)
    except Exception as e:
        logger.error(f"Mesaj gönderilemedi: {e}")

def main():
    """Ana fonksiyon: CAN arayüzünden mesajları dinler, yorumlar ve gönderir."""
    bus = None
    try:
        # CAN arayüzünü başlat
        bus = can.interface.Bus(channel=args.channel, interface='virtual')
        logger.info(f"{args.channel} arayüzünde dinleme başlatıldı.")

        # Örnek bir mesaj gönder (test için, isterseniz kaldırabilirsiniz)
        send_message(bus, "0x123", "1122334455667788")

        while True:
            # Mesajları 1 saniye zaman aşımıyla al
            mesaj = bus.recv(timeout=1.0)
            if mesaj is None:
                continue

            # CAN ID'sini formatla
            can_id = format_can_id(mesaj.arbitration_id)
            if can_id is None:
                continue

            # Veriyi onaltılık formata çevir
            data_hex = mesaj.data.hex()

            # Mesajı yorumla
            anlam = interpret_message(can_id, data_hex)

            # Mesajı logla
            log_message = f"GELEN [{can_id}] {anlam or 'Tanımsız mesaj'} | Veri: {data_hex}"
            message_logger.info(log_message)
            logger.info(log_message)

            # Veritabanını güncelle
            if anlam:
                logger.debug(f"Mesaj yorumlandı: {anlam}")
            elif can_id in database:
                # Veritabanında varsa, açıklamayı ve sayacı güncelle
                logger.debug(f"Veritabanında mevcut: {can_id}")
                database[can_id]["count"] = database[can_id].get("count", 0) + 1
                database[can_id]["last_seen"] = datetime.now().isoformat()
                save_database()
            else:
                # Yeni mesaj: Veritabanına ekle
                logger.info(f"Yeni mesaj eklendi: {can_id}")
                database[can_id] = {
                    "description": "Tanımsız mesaj",
                    "first_seen": datetime.now().isoformat(),
                    "last_seen": datetime.now().isoformat(),
                    "count": 1
                }
                save_database()

    except can.CanError as e:
        logger.error(f"CAN veri yolu hatası: {e}")
    except KeyboardInterrupt:
        logger.info("Dinleme kullanıcı tarafından durduruldu.")
    except Exception as e:
        logger.error(f"Beklenmeyen hata: {e}")
    finally:
        if bus is not None:
            try:
                bus.shutdown()
                logger.debug("CAN veri yolu başarıyla kapatıldı.")
            except Exception as e:
                logger.error(f"CAN veri yolu kapatılamadı: {e}")

if __name__ == "__main__":
    main()