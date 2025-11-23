import tweepy
import google.generativeai as genai
import os
import random
import time
import logging
import requests
from datetime import datetime
from dotenv import load_dotenv
from PIL import Image, ImageDraw, ImageFont
import textwrap
import json

# --- AYARLAR ---
load_dotenv()

# API Modelleri
API_MODEL = 'gemini-2.5-flash'
MAX_RETRIES = 3
RETRY_DELAY = 60  # seconds

# Twitter API v2
client = tweepy.Client(
    bearer_token=os.getenv("TWITTER_BEARER_TOKEN"),
    consumer_key=os.getenv("TWITTER_API_KEY"),
    consumer_secret=os.getenv("TWITTER_API_SECRET"),
    access_token=os.getenv("TWITTER_ACCESS_TOKEN"),
    access_token_secret=os.getenv("TWITTER_ACCESS_TOKEN_SECRET")
)

# Gemini Client
genai.configure(api_key=os.getenv("GEMINI_API_KEY"))
model = genai.GenerativeModel(API_MODEL)

# Loglama Ayarları
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('bot_log.txt', encoding='utf-8'),
        logging.StreamHandler()
    ]
)

# --- GELİŞMİŞ İÇERİK FONKSİYONLARI ---

def karakter_kontrol(text, max_length=280):
    """Tweet metnini karakter sınırına uygun hale getirir"""
    if len(text) <= max_length:
        return text
    
    # Son kelimeyi kesmeden kısalt
    words = text.split()
    shortened = ""
    for word in words:
        if len(shortened + " " + word) <= max_length - 3:  # "..." için yer bırak
            shortened += " " + word if shortened else word
        else:
            break
    
    return shortened.strip() + "..."

def guvenli_icerik_uret(prompt_func, *args):
    """İçerik üretiminde hata yönetimi"""
    for attempt in range(MAX_RETRIES):
        try:
            content = prompt_func(*args)
            if content and len(content.strip()) > 10:  # Boş veya çok kısa içerik kontrolü
                return karakter_kontrol(content.strip())
        except Exception as e:
            logging.warning(f"İçerik üretim hatası (deneme {attempt + 1}): {e}")
            if attempt < MAX_RETRIES - 1:
                time.sleep(RETRY_DELAY)
    
    # Yedek içerik
    yedek_icerikler = [
        "Bugün harika bir gün! 🎉 Pozitif enerjinizi koruyun ve güzelliklere odaklanın. #Motivasyon",
        "Küçük adımlar büyük yolculukların başlangıcıdır. 🌟 Bugün neye adım atacaksınız?",
        "Doğanın sesine kulak verin. 🌿 Bazen en derin cevaplar en sade anlarda gelir."
    ]
    return random.choice(yedek_icerikler)

def icerik_yapay_zeka_hikaye():
    prompt = """Twitter için ilgi çekici, kısa (maksimum 250 karakter) ve az bilinen bir bilimsel gerçeği veya tarihi olayı anlat. 
    Alakasız bir emoji ekle ve akılda kalıcı olsun. Örnek: "Romalılar diş macununu idrar ile yapardı. 😅 #Tarih" """
    response = model.generate_content(prompt)
    return response.text

def icerik_romantik_soz():
    prompt = """Twitter için kısa, duygusal ve özgün bir romantik şiir dizesi veya aşk sözü yaz. 
    Maximum 250 karakter olmalı. #Aşk etiketini kullan ve kalbe dokunan bir dil kullan."""
    response = model.generate_content(prompt)
    return response.text

def icerik_burc_yorumu():
    burclar = ["Koç", "Boğa", "İkizler", "Yengeç", "Aslan", "Başak", "Terazi", "Akrep", "Yay", "Oğlak", "Kova", "Balık"]
    rastgele_burc = random.choice(burclar)
    prompt = f"""Twitter için {rastgele_burc} burcunun bu haftaki kısa, pozitif ve motive edici yorumunu yaz. 
    Maximum 250 karakter. 'Bu hafta {rastgele_burc} burcu' diye başla. Enerjik ve ümit verici olsun. #{rastgele_burc} #Burçlar"""
    response = model.generate_content(prompt)
    return response.text

def icerik_secim_anketi():
    prompt = """Twitter için eğlenceli ve düşündürücü bir "Hangisini Seçerdin?" sorusu hazırla. 
    İki zor seçenek sun. Maximum 200 karakter. Cevabı metinde verme, sadece soruyu sor."""
    response = model.generate_content(prompt)
    return response.text

def icerik_gunun_kelimesi():
    prompt = """Twitter için az bilinen, güzel bir Türkçe kelime ve kısa tanımını yaz. 
    Maximum 230 karakter. Örnek: "Yeğlemek: Tercih etmek, bir şeyi diğerine üstün tutmak. #GününKelimesi" """
    response = model.generate_content(prompt)
    return response.text

def icerik_burc_listesi():
    konular = ["En Kinci", "En Titiz", "En Sakin", "En Kararsız", "En Eğlenceli", "En Romantik", "En Çalışkan"]
    rastgele_konu = random.choice(konular)
    prompt = f"""Twitter için '{rastgele_konu} olan 3 burç' listesini mizahi ve ilgi çekici bir dille yaz. 
    Maximum 270 karakter. Emojiler kullan. #Burçlar #{rastgele_konu.replace(' ', '')}"""
    response = model.generate_content(prompt)
    return response.text

def icerik_motivasyon():
    prompt = """Twitter için kısa, etkili ve ilham verici bir motivasyon sözü yaz. 
    Maximum 240 karakter. Günlük hayata uygulanabilir ve pozitif enerji veren bir mesaj olsun. #Motivasyon #Başarı"""
    response = model.generate_content(prompt)
    return response.text

def icerik_bilim_teknoloji():
    prompt = """Twitter için kısa, şaşırtıcı bir bilim veya teknoloji haberi/bilgisini paylaş. 
    Maximum 260 karakter. Güncel ve ilgi çekici olsun. #Bilim #Teknoloji"""
    response = model.generate_content(prompt)
    return response.text

def icerik_eglence():
    prompt = """Twitter için komik, eğlenceli ve günlük hayattan bir espri veya gözlem paylaş. 
    Maximum 250 karakter. Mizahi dil kullan ve gülümsetsin. #Eğlence #Komik"""
    response = model.generate_content(prompt)
    return response.text

# --- GÖRSEL ÜRETİM SİSTEMİ ---

def basit_grafik_olustur(metin, dosya_adi="tweet_gorsel.png"):
    """Tweet için basit bir grafik oluşturur"""
    try:
        # Görsel boyutları
        genislik, yukseklik = 800, 400
        
        # Arka plan renkleri
        renkler = [
            (25, 25, 112),   # Midnight Blue
            (47, 79, 79),    # Dark Slate Gray
            (139, 0, 139),   # Dark Magenta
            (178, 34, 34),   # Firebrick
            (0, 100, 0)      # Dark Green
        ]
        arka_plan, yazi_rengi = random.choice(renkler), (255, 255, 255)
        
        # Görsel oluştur
        img = Image.new('RGB', (genislik, yukseklik), color=arka_plan)
        draw = ImageDraw.Draw(img)
        
        # Basit font (varsayılan kullan)
        try:
            font = ImageFont.truetype("arial.ttf", 24)
        except:
            font = ImageFont.load_default()
        
        # Metni wrap et
        satirlar = textwrap.wrap(metin, width=40)
        y_pozisyon = 50
        
        for satir in satirlar:
            bbox = draw.textbbox((0, 0), satir, font=font)
            satir_genislik = bbox[2] - bbox[0]
            x_pozisyon = (genislik - satir_genislik) // 2
            draw.text((x_pozisyon, y_pozisyon), satir, fill=yazi_rengi, font=font)
            y_pozisyon += 40
        
        img.save(dosya_adi)
        return dosya_adi
    except Exception as e:
        logging.error(f"Görsel oluşturma hatası: {e}")
        return None

# --- GELİŞMİŞ TWEET SİSTEMİ ---

def tweet_gonder(metin, gorsel_yolu=None):
    """Güvenli tweet gönderme fonksiyonu"""
    try:
        if gorsel_yolu and os.path.exists(gorsel_yolu):
            # Medya yükleme
            media = tweepy.MediaUpload(gorsel_yolu)
            tweet = client.create_tweet(text=metin, media_ids=[media.media_id])
        else:
            tweet = client.create_tweet(text=metin)
        
        logging.info(f"Tweet başarıyla gönderildi: {metin[:50]}...")
        return True
        
    except tweepy.TweepyException as e:
        logging.error(f"Twitter API Hatası: {e}")
        return False
    except Exception as e:
        logging.error(f"Beklenmeyen hata: {e}")
        return False

def bot_durumunu_kaydet(zar, icerik_turu, basarili):
    """Bot durumunu JSON dosyasına kaydeder"""
    try:
        data = {
            "son_calistirma": datetime.now().isoformat(),
            "son_zar": zar,
            "son_icerik": icerik_turu,
            "basarili": basarili,
            "toplam_calistirma": 0
        }
        
        # Eski verileri oku
        try:
            with open("bot_durum.json", "r", encoding="utf-8") as f:
                eski_data = json.load(f)
                data["toplam_calistirma"] = eski_data.get("toplam_calistirma", 0) + 1
        except:
            data["toplam_calistirma"] = 1
        
        with open("bot_durum.json", "w", encoding="utf-8") as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
            
    except Exception as e:
        logging.error(f"Durum kaydetme hatası: {e}")

# --- ANA BOT SİSTEMİ ---

def botu_calistir():
    """Geliştirilmiş bot çalıştırma sistemi"""
    
    # İçerik fonksiyonları sözlüğü
    icerik_fonksiyonlari = {
        1: ("🤖 Bilim/Tarih Hikayesi", icerik_yapay_zeka_hikaye, False),
        2: ("💖 Romantik Söz", icerik_romantik_soz, False),
        3: ("♈ Burç Yorumu", icerik_burc_yorumu, False),
        4: ("❓ Seçim Anketi", icerik_secim_anketi, False),
        5: ("📚 Günün Kelimesi", icerik_gunun_kelimesi, True),
        6: ("📊 Burç Listesi", icerik_burc_listesi, False),
        7: ("🚀 Motivasyon", icerik_motivasyon, True),
        8: ("🔬 Bilim/Teknoloji", icerik_bilim_teknoloji, False),
        9: ("😊 Eğlence", icerik_eglence, False)
    }
    
    # Zar at (1-9 arası)
    zar = random.randint(1, 9)
    icerik_adi, icerik_fonk, gorsel_ekle = icerik_fonksiyonlari[zar]
    
    logging.info(f"🎲 Zar: {zar} - İçerik: {icerik_adi}")
    
    # İçerik üret
    tweet_metni = guvenli_icerik_uret(icerik_fonk)
    
    if not tweet_metni:
        logging.error("❌ İçerik üretilemedi!")
        bot_durumunu_kaydet(zar, icerik_adi, False)
        return
    
    # Görsel oluştur (belirli içerikler için)
    gorsel_yolu = None
    if gorsel_ekle and random.random() < 0.6:  # %60 ihtimalle görsel ekle
        gorsel_yolu = basit_grafik_olustur(tweet_metni)
    
    # Tweet gönder
    basarili = tweet_gonder(tweet_metni, gorsel_yolu)
    
    # Temizlik
    if gorsel_yolu and os.path.exists(gorsel_yolu):
        try:
            os.remove(gorsel_yolu)
        except:
            pass
    
    # Durumu kaydet
    bot_durumunu_kaydet(zar, icerik_adi, basarili)
    
    if basarili:
        logging.info(f"✅ BAŞARILI! Tweet gönderildi: {tweet_metni[:60]}...")
    else:
        logging.error("❌ Tweet gönderilemedi!")

# --- OTOMATİK ZAMANLAYICI ---

def otomatik_mod():
    """Botu belirli aralıklarla otomatik çalıştırır"""
    calisma_saatleri = [9, 12, 15, 18, 21]  # Günde 5 kez
    
    while True:
        simdi = datetime.now()
        saat = simdi.hour
        
        if saat in calisma_saatleri and simdi.minute == 0:
            logging.info(f"⏰ Otomatik çalıştırma: {saat}:00")
            botu_calistir()
            time.sleep(61)  # Aynı saatte tekrar çalışmasın
        
        time.sleep(30)  # 30 saniyede bir kontrol et

# --- ANA PROGRAM ---

if __name__ == "__main__":
    logging.info("🤖 Twitter Bot başlatılıyor...")
    
    try:
        # Manuel çalıştırma
        botu_calistir()
        
        # Otomatik modu başlatmak için aşağıdaki satırın başındaki # işaretini kaldırın:
        # otomatik_mod()
        
    except KeyboardInterrupt:
        logging.info("⏹️ Bot kullanıcı tarafından durduruldu.")
    except Exception as e:
        logging.error(f"💥 Kritik hata: {e}")
