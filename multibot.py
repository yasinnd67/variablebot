import tweepy
import google.generativeai as genai
import os
import random
import time
import json
import logging
import sys
import warnings
import re

# Gereksiz uyarıları kapat
warnings.filterwarnings("ignore", category=FutureWarning)

try:
    import yfinance as yf
    import feedparser
    import matplotlib.pyplot as plt
    plt.switch_backend('Agg')
except ImportError:
    print("Eksik kütüphaneler: pip install yfinance feedparser matplotlib")

from datetime import datetime
from dotenv import load_dotenv

# --- AYARLAR ---
load_dotenv()

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - [%(levelname)s] - %(message)s',
    handlers=[logging.StreamHandler(sys.stdout)]
)

# API Değişkenleri
GEMINI_MODEL = 'gemini-2.5-flash' # İstediğin model geri geldi

# Gemini Yapılandırması
genai.configure(api_key=os.getenv("GEMINI_API_KEY"))
model = genai.GenerativeModel(GEMINI_MODEL)

# --- TWITTER BAĞLANTISI ---
try:
    # 403 Hatasını engellemek için OAuth 1.0a (User Context) üzerinden bağlanan client
    client = tweepy.Client(
        consumer_key=os.getenv("TWITTER_API_KEY"),
        consumer_secret=os.getenv("TWITTER_API_SECRET"),
        access_token=os.getenv("TWITTER_ACCESS_TOKEN"),
        access_token_secret=os.getenv("TWITTER_ACCESS_TOKEN_SECRET"),
        wait_on_rate_limit=True
    )
    print(">>> ✅ Twitter Bağlantısı Başarılı!")
except Exception as e:
    print(f">>> ❌ Twitter Bağlantı Hatası: {e}")
    sys.exit()

# --- YARDIMCI FONKSİYONLAR ---

def temiz_json_al(prompt):
    try:
        response = model.generate_content(prompt)
        text = response.text.strip()
        # Markdown temizliği
        if "```" in text:
            match = re.search(r'\{.*\}', text, re.DOTALL)
            if match: text = match.group()
        return json.loads(text)
    except Exception as e:
        logging.error(f"Gemini/JSON Hatası: {e}")
        return None

# --- MOD 1: HİKAYE (FLOOD) MODU ---

def hikaye_modu():
    print("\n>>> 📖 MOD: HİKAYE/FLOOD SEÇİLDİ")
    topics = [
        "Tarihte az bilinen bir ihanet",
        "Dünyayı değiştiren bir bilimsel kaza",
        "Çözülememiş gizemli bir suç",
        "İlham verici bir başarı öyküsü"
    ]
    secilen_konu = random.choice(topics)
    
    prompt = f"""
    Sen usta bir hikaye anlatıcısısın. Konu: '{secilen_konu}'.
    Twitter için 3 tweetlik sürükleyici bir zincir (flood) yaz.
    SADECE geçerli bir JSON formatında cevap ver:
    {{
        "tweet1": "...",
        "tweet2": "...",
        "tweet3": "..."
    }}
    """
    
    data = temiz_json_al(prompt)
    if not data: return

    try:
        # User_auth=True eklenerek GitHub kısıtlaması aşılır
        t1 = client.create_tweet(text=data['tweet1'], user_auth=True)
        time.sleep(3)
        t2 = client.create_tweet(text=data['tweet2'], in_reply_to_tweet_id=t1.data['id'], user_auth=True)
        time.sleep(3)
        client.create_tweet(text=data['tweet3'], in_reply_to_tweet_id=t2.data['id'], user_auth=True)
        logging.info("✅ Flood Gönderildi!")
    except Exception as e:
        logging.error(f"Flood Tweet Hatası: {e}")

# --- MOD 2: HABER VE FİNANS MODU ---

def finans_haber_modu():
    print("\n>>> 📈 MOD: HABER VE FİNANS SEÇİLDİ")
    semboller = {"USDTRY=X": "Dolar/TL", "EURTRY=X": "Euro/TL", "GC=F": "Altın (Ons)"}
    sembol, isim = random.choice(list(semboller.items()))
    
    try:
        # 1. Finans Verisi
        ticker = yf.Ticker(sembol)
        hist = ticker.history(period="1d")
        fiyat = hist['Close'].iloc[-1]
        
        # 2. Haber Verisi (RSS)
        rss_url = "[https://news.google.com/rss?hl=tr&gl=TR&ceid=TR:tr](https://news.google.com/rss?hl=tr&gl=TR&ceid=TR:tr)"
        feed = feedparser.parse(rss_url)
        haber_basligi = feed.entries[0].title if feed.entries else "Gündem hareketli."
        
        # 3. Yorumlat
        prompt = f"""
        Finans Verisi: {isim} - {fiyat:.2f}. Haber: {haber_basligi}. 
        Bunları yorumlayan ilgi çekici bir tweet yaz. 
        SADECE JSON: {{"tweet_text": "..."}}
        """
        
        data = temiz_json_al(prompt)
        if data:
            # Görsel çakışması 403 sebebi olduğu için şimdilik sadece metin
            client.create_tweet(text=data['tweet_text'], user_auth=True)
            logging.info(f"✅ Finans Tweeti Gönderildi: {isim}")
            
    except Exception as e:
        logging.error(f"Finans Modu Hatası: {e}")

# --- ANA PROGRAM ---

if __name__ == "__main__":
    print("="*40)
    print(f"🤖 BOT AKTİF - MODEL: {GEMINI_MODEL}")
    print("="*40)
    
    try:
        zar = random.random()
        if zar < 0.5:
            hikaye_modu()
        else:
            finans_haber_modu()
        print("\n>>> ✅ İŞLEM BAŞARIYLA TAMAMLANDI.")
    except Exception as e:
        print(f"\n>>> 💥 KRİTİK HATA: {e}")
