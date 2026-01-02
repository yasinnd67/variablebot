import tweepy
import google.generativeai as genai
import os
import random
import time
import json
import logging
import sys

# Hata veren kütüphaneler (Yüklü değilse try-except ile kullanıcıyı uyarır)
try:
    import yfinance as yf
    import matplotlib.pyplot as plt
    import feedparser
except ImportError as e:
    print(f"KRİTİK HATA: Kütüphaneler eksik! Lütfen terminale şunu yazın: pip install yfinance matplotlib feedparser")
    sys.exit()

from datetime import datetime
from dotenv import load_dotenv

# --- AYARLAR ---
load_dotenv()

# Matplotlib için ekran kartı olmayan sunucu ayarı (Hata önleyici)
plt.switch_backend('Agg')

# Loglama Ayarları (Hem dosyaya hem terminale yazar)
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - [%(levelname)s] - %(message)s',
    handlers=[
        logging.StreamHandler(sys.stdout) # Terminale yazdır
    ]
)

# API Anahtarları Kontrolü
required_vars = ["GEMINI_API_KEY", "TWITTER_BEARER_TOKEN", "TWITTER_API_KEY", "TWITTER_API_SECRET", "TWITTER_ACCESS_TOKEN", "TWITTER_ACCESS_TOKEN_SECRET"]
missing_vars = [var for var in required_vars if not os.getenv(var)]
if missing_vars:
    logging.error(f"Eksik .env değişkenleri: {missing_vars}")
    sys.exit()

# Gemini Ayarları
genai.configure(api_key=os.getenv("GEMINI_API_KEY"))
model = genai.GenerativeModel('gemini-2.5-flash')

# Twitter Client Başlatma
try:
    client = tweepy.Client(
        bearer_token=os.getenv("TWITTER_BEARER_TOKEN"),
        consumer_key=os.getenv("TWITTER_API_KEY"),
        consumer_secret=os.getenv("TWITTER_API_SECRET"),
        access_token=os.getenv("TWITTER_ACCESS_TOKEN"),
        access_token_secret=os.getenv("TWITTER_ACCESS_TOKEN_SECRET")
    )
    
    # Medya yükleme için v1.1 yetkisi
    auth = tweepy.OAuth1UserHandler(
        os.getenv("TWITTER_API_KEY"), os.getenv("TWITTER_API_SECRET"),
        os.getenv("TWITTER_ACCESS_TOKEN"), os.getenv("TWITTER_ACCESS_TOKEN_SECRET")
    )
    api = tweepy.API(auth)
    print(">>> ✅ Twitter Bağlantısı Başarılı!")
except Exception as e:
    print(f">>> ❌ Twitter Bağlantı Hatası: {e}")
    sys.exit()

# --- YARDIMCI FONKSİYONLAR ---

def temiz_json_al(prompt):
    """Gemini'den gelen cevabı saf JSON'a çevirir."""
    logging.info("Gemini'ye istek gönderiliyor...")
    try:
        response = model.generate_content(prompt)
        text = response.text.strip()
        
        # Markdown (```json ... ```) temizliği
        if "```" in text:
            import re
            text = re.search(r'\{.*\}', text, re.DOTALL).group()
        
        return json.loads(text)
    except Exception as e:
        logging.error(f"JSON Çözme Hatası veya Yapay Zeka Cevap Vermedi: {e}")
        return None

def grafik_ciz(veri, baslik, sembol):
    """Matplotlib ile grafik çizer ve kaydeder."""
    dosya_adi = f"chart_{sembol}.png"
    try:
        logging.info(f"Grafik çiziliyor: {baslik}")
        plt.figure(figsize=(10, 6))
        
        # Son 30 günü çiz
        plt.plot(veri.index, veri['Close'], color='#1DA1F2', linewidth=2.5)
        
        # Tasarım
        plt.title(baslik, fontsize=16, fontweight='bold', color='#333333')
        plt.xlabel('Tarih', fontsize=10)
        plt.ylabel('Fiyat (TRY)', fontsize=10)
        plt.grid(True, linestyle='--', alpha=0.5)
        plt.tight_layout()
        
        plt.savefig(dosya_adi)
        plt.close()
        return dosya_adi
    except Exception as e:
        logging.error(f"Grafik Oluşturma Hatası: {e}")
        return None

# --- MOD 1: HİKAYE (FLOOD) MODU ---

def hikaye_modu():
    print("\n>>> 📖 MOD: HİKAYE/FLOOD SEÇİLDİ")
    topics = [
        "Tarihte az bilinen bir ihanet",
        "Dünyayı değiştiren bir bilimsel kaza",
        "Çözülememiş gizemli bir suç (True Crime)",
        "İlham verici bir başarı öyküsü",
        "Efsanevi bir mitolojik olay"
    ]
    secilen_konu = random.choice(topics)
    logging.info(f"Seçilen Konu: {secilen_konu}")
    
    prompt = f"""
    Sen usta bir hikaye anlatıcısısın. Konu: '{secilen_konu}'.
    Bu konuyu Twitter için 3 tweetlik sürükleyici bir zincir (flood) haline getir.
    
    KURALLAR:
    1. 'İşte hikaye', 'Yapay zeka cevabı' gibi cümleler ASLA kurma.
    2. Sürükleyici, merak uyandırıcı ve duygusal bir dil kullan.
    3. Bol emoji kullan.
    4. SADECE geçerli bir JSON formatında cevap ver:
    {{
        "tweet1": "Hikayenin başı...",
        "tweet2": "Gelişme kısmı...",
        "tweet3": "Sonuç ve düşündürücü final..."
    }}
    """
    
    data = temiz_json_al(prompt)
    if not data:
        logging.warning("İçerik üretilemedi, işlem iptal.")
        return

    try:
        # 1. Tweet
        t1 = client.create_tweet(text=data['tweet1'])
        logging.info(f"✅ 1. Tweet Gönderildi ID: {t1.data['id']}")
        time.sleep(3) # Spam olmaması için bekle
        
        # 2. Tweet (Reply)
        t2 = client.create_tweet(text=data['tweet2'], in_reply_to_tweet_id=t1.data['id'])
        logging.info(f"✅ 2. Tweet Gönderildi ID: {t2.data['id']}")
        time.sleep(3)
        
        # 3. Tweet (Reply)
        client.create_tweet(text=data['tweet3'], in_reply_to_tweet_id=t2.data['id'])
        logging.info("✅ 3. Tweet Gönderildi. Flood Tamamlandı!")
        
    except Exception as e:
        logging.error(f"Tweet Gönderme Hatası: {e}")

# --- MOD 2: HABER VE GRAFİK MODU ---

def finans_haber_modu():
    print("\n>>> 📈 MOD: HABER VE GRAFİK SEÇİLDİ")
    
    # Sadece İstenen Varlıklar
    semboller = {
        "USDTRY=X": "Dolar/TL",
        "EURTRY=X": "Euro/TL",
        "GC=F": "Altın (Ons)",
        "SI=F": "Gümüş (Ons)"
    }
    
    sembol_kodu = random.choice(list(semboller.keys()))
    isim = semboller[sembol_kodu]
    
    try:
        # 1. Finans Verisi Çek
        logging.info(f"{isim} verisi çekiliyor...")
        ticker = yf.Ticker(sembol_kodu)
        hist = ticker.history(period="1mo")
        
        if hist.empty:
            logging.error("Finans verisi boş geldi!")
            return

        son_fiyat = hist['Close'].iloc[-1]
        grafik_yolu = grafik_ciz(hist, f"{isim} Son 30 Gün", sembol_kodu.replace("=X", ""))
        
        # 2. Türkiye Haberleri Çek
        logging.info("Türkiye haberleri taranıyor...")
        rss_url = "[https://news.google.com/rss?hl=tr&gl=TR&ceid=TR:tr](https://news.google.com/rss?hl=tr&gl=TR&ceid=TR:tr)"
        feed = feedparser.parse(rss_url)
        
        haber_basligi = "Ekonomik Gündem"
        if feed.entries:
            # Rastgele bir haber seç (İlk 10 arasından)
            haber = random.choice(feed.entries[:10])
            haber_basligi = haber.title
            logging.info(f"Seçilen Haber: {haber_basligi}")
        
        # 3. Yorumlat
        prompt = f"""
        Rolün: Ciddi ve güvenilir bir finans/haber yorumcusu.
        Veriler:
        - Varlık: {isim}
        - Fiyat: {son_fiyat:.2f}
        - Türkiye Gündem Haberi: "{haber_basligi}"
        
        Görevin:
        Bu finansal durumu ve gündemdeki haberi harmanlayarak (veya ayrı ayrı değinerek)
        ilgi çekici, bilgi verici tek bir tweet yaz.
        
        Kurallar:
        1. ASLA 'Ben bir yapay zekayım' veya 'İşte tweetin' deme.
        2. #sondakika etiketini kullan.
        3. Konuyla ilgili 1 tane daha popüler etiket ekle (örn: #ekonomi, #altın, #siyaset).
        4. SADECE şu JSON formatında cevap ver:
        {{
            "tweet_text": "Yazılacak tweet metni..."
        }}
        """
        
        data = temiz_json_al(prompt)
        if not data: return
        
        tweet_metni = data['tweet_text']
        
        # 4. Paylaş
        if grafik_yolu and os.path.exists(grafik_yolu):
            media = api.media_upload(grafik_yolu)
            client.create_tweet(text=tweet_metni, media_ids=[media.media_id])
            logging.info(f"✅ Tweet (Görselli) Gönderildi: {tweet_metni[:30]}...")
            os.remove(grafik_yolu) # Temizlik
        else:
            client.create_tweet(text=tweet_metni)
            logging.info("✅ Tweet (Görselsiz) Gönderildi.")
            
    except Exception as e:
        logging.error(f"Finans Modu Hatası: {e}")

# --- TEST VE BAŞLATMA ---

if __name__ == "__main__":
    print("="*40)
    print("   🤖 GELİŞMİŞ TWITTER BOTU BAŞLATILIYOR")
    print("="*40)
    
    # 30 Dakikalık Döngü Simülasyonu (GitHub Actions'da tek sefer çalışır, burada test amaçlı)
    # Eğer GitHub Actions kullanacaksan sadece tek fonksiyon çağırılır.
    # Biz burada test için rastgele birini seçip çalıştırıyoruz.
    
    try:
        zar = random.random()
        if zar < 0.5:
            hikaye_modu()
        else:
            finans_haber_modu()
            
        print("\n>>> ✅ İŞLEM BAŞARIYLA TAMAMLANDI.")
        
    except KeyboardInterrupt:
        print("\n>>> 🛑 Bot durduruldu.")
    except Exception as e:
        print(f"\n>>> 💥 BEKLENMEYEN HATA: {e}")