import tweepy
import google.generativeai as genai
import os
import random
import time
import json
import logging
import sys
import warnings

# Gereksiz uyarıları kapat
warnings.filterwarnings("ignore", category=FutureWarning)

# Hata veren kütüphaneler
try:
    import yfinance as yf
    import matplotlib.pyplot as plt
    import feedparser
except ImportError:
    print(f"KRİTİK HATA: Kütüphaneler eksik! Lütfen terminale şunu yazın: pip install yfinance matplotlib feedparser")
    sys.exit()

from datetime import datetime
from dotenv import load_dotenv

# --- AYARLAR ---
load_dotenv()

# Matplotlib için ekran kartı olmayan sunucu ayarı
plt.switch_backend('Agg')

# Loglama Ayarları
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - [%(levelname)s] - %(message)s',
    handlers=[logging.StreamHandler(sys.stdout)]
)

# API Anahtarları Kontrolü
required_vars = ["GEMINI_API_KEY", "TWITTER_BEARER_TOKEN", "TWITTER_API_KEY", "TWITTER_API_SECRET", "TWITTER_ACCESS_TOKEN", "TWITTER_ACCESS_TOKEN_SECRET"]
if not all(os.getenv(var) for var in required_vars):
    logging.error("Eksik .env veya GitHub Secret değişkenleri!")
    sys.exit()

# Gemini Ayarları
genai.configure(api_key=os.getenv("GEMINI_API_KEY"))
model = genai.GenerativeModel('gemini-2.5-flash')

# --- TWITTER BAĞLANTI (403 HATASI ÇÖZÜMÜ) ---
try:
    # GitHub sunucularında 403 hatasını engellemek için anahtarları OAuth1.0a (User Context) moduna zorluyoruz
    client = tweepy.Client(
        bearer_token=os.getenv("TWITTER_BEARER_TOKEN"),
        consumer_key=os.getenv("TWITTER_API_KEY"),
        consumer_secret=os.getenv("TWITTER_API_SECRET"),
        access_token=os.getenv("TWITTER_ACCESS_TOKEN"),
        access_token_secret=os.getenv("TWITTER_ACCESS_TOKEN_SECRET"),
        wait_on_rate_limit=True
    )
    
    auth = tweepy.OAuth1UserHandler(
        os.getenv("TWITTER_API_KEY"), os.getenv("TWITTER_API_SECRET"),
        os.getenv("TWITTER_ACCESS_TOKEN"), os.getenv("TWITTER_ACCESS_TOKEN_SECRET")
    )
    api = tweepy.API(auth, wait_on_rate_limit=True)
    print(">>> ✅ Twitter Bağlantısı Kuruldu!")
except Exception as e:
    print(f">>> ❌ Twitter Bağlantı Hatası: {e}")
    sys.exit()

# --- YARDIMCI FONKSİYONLAR ---

def temiz_json_al(prompt):
    try:
        response = model.generate_content(prompt)
        text = response.text.strip()
        if "```" in text:
            import re
            text = re.search(r'\{.*\}', text, re.DOTALL).group()
        return json.loads(text)
    except Exception as e:
        logging.error(f"AI Cevap Hatası: {e}")
        return None

def grafik_ciz(veri, baslik, sembol):
    dosya_adi = f"chart_{sembol}.png"
    try:
        plt.figure(figsize=(10, 6))
        plt.plot(veri.index, veri['Close'], color='#1DA1F2', linewidth=2.5)
        plt.title(baslik, fontsize=16, fontweight='bold')
        plt.grid(True, linestyle='--', alpha=0.5)
        plt.tight_layout()
        plt.savefig(dosya_adi)
        plt.close()
        return dosya_adi
    except Exception as e:
        logging.error(f"Grafik Hatası: {e}")
        return None

# --- TWEET GÖNDERME MOTORU (KRİTİK DÜZELTME) ---

def güvenli_tweet_at(metin, gorsel=None):
    """GitHub Actions'daki 403 hatasını aşmak için user_auth=True zorunluluğu getirildi"""
    try:
        if gorsel and os.path.exists(gorsel):
            # Görselli tweet (OAuth 1.0a kullanır)
            media = api.media_upload(filename=gorsel)
            client.create_tweet(text=metin, media_ids=[media.media_id], user_auth=True)
            logging.info("✅ Görselli tweet GitHub üzerinden başarıyla atıldı.")
        else:
            # Görselsiz tweet
            client.create_tweet(text=metin, user_auth=True)
            logging.info("✅ Tweet GitHub üzerinden başarıyla atıldı.")
        return True
    except Exception as e:
        logging.error(f"❌ TWEET ATILAMADI (403 veya Yetki Hatası): {e}")
        return False

# --- MODLAR ---

def hikaye_modu():
    print("\n>>> 📖 MOD: HİKAYE SEÇİLDİ")
    prompt = """Twitter için 3 tweetlik sürükleyici bir zincir hazırla. Konu: Rastgele gizemli bir olay. JSON formatında ver: {"tweet1": "...", "tweet2": "...", "tweet3": "..."}"""
    data = temiz_json_al(prompt)
    if data:
        t1 = client.create_tweet(text=data['tweet1'], user_auth=True)
        time.sleep(2)
        t2 = client.create_tweet(text=data['tweet2'], in_reply_to_tweet_id=t1.data['id'], user_auth=True)
        time.sleep(2)
        client.create_tweet(text=data['tweet3'], in_reply_to_tweet_id=t2.data['id'], user_auth=True)

def finans_haber_modu():
    print("\n>>> 📈 MOD: HABER VE GRAFİK SEÇİLDİ")
    semboller = {"USDTRY=X": "Dolar/TL", "GC=F": "Altın (Ons)"}
    sembol, isim = random.choice(list(semboller.items()))
    
    try:
        ticker = yf.Ticker(sembol)
        hist = ticker.history(period="1mo")
        fiyat = hist['Close'].iloc[-1]
        grafik = grafik_ciz(hist, f"{isim} Analizi", sembol)
        
        prompt = f"Varlık: {isim}, Fiyat: {fiyat:.2f}. Bu ekonomik durum hakkında kısa, ilgi çekici bir tweet yaz. JSON: {'tweet_text': '...'}"
        data = temiz_json_al(prompt)
        
        if data:
            güvenli_tweet_at(data['tweet_text'], grafik)
            if grafik and os.path.exists(grafik): os.remove(grafik)
    except Exception as e:
        logging.error(f"Finans Modu Hatası: {e}")

# --- ÇALIŞTIR ---

if __name__ == "__main__":
    print("="*40)
    print("   🤖 GİTHUB UYUMLU BOT BAŞLATILDI")
    print("="*40)
    
    if random.random() < 0.5:
        hikaye_modu()
    else:
        finans_haber_modu()
    
    print("\n>>> ✅ İŞLEM TAMAMLANDI.")
