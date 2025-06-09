<div align="center">
  <img src="https://img.shields.io/github/languages/count/emirtiftikci/CanbusSniffingSimulation?style=flat-square&color=blueviolet" alt="Language Count">
  <img src="https://img.shields.io/github/languages/top/emirtiftikci/CanbusSniffingSimulation?style=flat-square&color=1e90ff" alt="Top Language">
  <img src="https://img.shields.io/github/last-commit/emirtiftikci/CanbusSniffingSimulation?style=flat-square&color=ff69b4" alt="Last Commit">
  <img src="https://img.shields.io/github/license/emirtiftikci/CanbusSniffingSimulation?style=flat-square&color=yellow" alt="License">
  <img src="https://img.shields.io/badge/Status-Active-green?style=flat-square" alt="Status">
  <img src="https://img.shields.io/badge/Contributions-Welcome-brightgreen?style=flat-square" alt="Contributions">
</div>

# CAN Bus Sniffing Projesi (Sanal Ortam)


Bu proje, Controller Area Network (CAN Bus) sistemlerinin veri iletişim mantığını sanal ortamda taklit ederek analiz etmeyi amaçlar. Gerçek bir araca bağlanmadan, sanal bir CAN ağı (`vcan0`) üzerinden gönderilen mesajları dinleyip analiz ederek tersine mühendislik pratiği kazandırır.

---

## Proje Amacı

- CAN Bus sistemini yazılım düzeyinde anlamak
- Araç içi veri paketlerinin yapısını çözümlemek
- Python ile terminal tabanlı bir **CAN sniffer** geliştirmek
- Gerçek araçlara geçmeden önce simülasyon ortamında test yapmak
---

## Proje Dosya Yapısı
canbus_proje/
├── sniffer.py # Python ile yazılmış CAN dinleyici scripti
├── database.json # Tanınan CAN ID'lerini açıklayan JSON verisi
├── README.md # Proje açıklama dosyası


---


## Kurulum ve Ortam Hazırlığı

1. Gerekli paketlerin kurulması:
   ```bash
   sudo apt install can-utils
   python3 -m venv venv
   source venv/bin/activate
   pip install python-can

2. Sanal CAN arayüzünü aktif hale getirmek:
    sudo modprobe vcan
    sudo ip link add dev vcan0 type vcan
    sudo ip link set up vcan0

▶ Projeyi Çalıştırma

1. Sniffer betiğini çalıştırın:
    python sniffer.py

2. Farklı bir terminalde cansend ile örnek veri gönderin:
    cansend vcan0 123#1122334455667788

3. sniffer.py çıktısı (örnek):
    [✓] vcan0 arayüzünden veri dinleniyor...
    [0x123] Kapı açma komutu -> 1122334455667788


Nasıl Çalışır?
sniffer.py, vcan0 arayüzünden gelen her CAN mesajını dinler.

Gelen mesajın ID'si, database.json içinde eşleşirse açıklama terminale yazılır.

Eşleşmeyen mesajlar "Bilinmeyen mesaj" olarak listelenir.


UYARI!!
Bu proje tamamen sanal test ortamı amacıyla geliştirilmiştir. Gerçek araçlara bağlanmadan önce mutlaka güvenlik önlemleri alınmalı, araç üreticisinin teknik belgeleri incelenmelidir.


Emegi gecenler=======
Emirhan Atar 2320191075
Emirhan Tiftikci 2320191068
Lutfu Dikici 2320191083
