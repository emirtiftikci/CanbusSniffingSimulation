import can

INTERFACE = 'vcan0'  # Gerçek araçta 'can0' olabilir

try:
    bus = can.interface.Bus(channel=INTERFACE, bustype='socketcan')
    msg = can.Message(arbitration_id=0x123, data=[0x11,0x22,0x33,0x44,0x55,0x66,0x77,0x88], is_extended_id=False)
    bus.send(msg)
    print("[✓] Replay mesajı başarıyla gönderildi.")
except Exception as e:
    print(f"[!] Mesaj gönderilemedi: {e}")
