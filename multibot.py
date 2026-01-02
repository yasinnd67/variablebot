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
from dotenv import load_dotenv

warnings.filterwarnings("ignore", category=FutureWarning)

try:
    import yfinance as yf
    import feedparser
except ImportError:
    print("Eksik kütüphaneler: pip install yfinance feedparser")

load_dotenv()

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - [%(levelname)s] - %(message)s",
    handlers=[logging.StreamHandler(sys.stdout)]
)

GEMINI_MODEL = "gemini-2.5-flash"
genai.configure(api_key=os.getenv("GEMINI_API_KEY"))
model = genai.GenerativeModel(GEMINI_MODEL)

# --- TWITTER BAĞLANTISI (OAuth 1.0a User Context) ---

try:
    client = tweepy.Client(
        consumer_key=os.getenv("TWITTER_API_KEY"),
        consumer_secret=os.getenv("TWITTER_API_SECRET"),
        access_token=os.getenv("TWITTER_ACCESS_TOKEN"),
        access_token_secret=os.getenv("TWITTER_ACCESS_TOKEN_SECRET"),
        wait_on_rate_limit=True
    )
    print(">>> ✅ Twitter bağlantısı başarılı")
except Exception as e:
    print(f">>> ❌ Twitter bağlantı hatası: {e}")
    sys.exit()


# --- Yardımcı Fonksiyon ---

def temiz_json_al(prompt):
    try:
        r = model.generate_content(prompt)
        text = r.text.strip()

        if "```" in text:
            m = re.search(r"\{.*\}", text, re.DOTALL)
            if m:
                text = m.group()

        return json.loads(text)

    except Exception as e:
        logging.error(f"Gemini JSON hatası: {e}")
        return None


# --- HASHTAG ÜRETİCİ ---

def finans_hashtagleri():
    secenekler = [
        ["#dolar", "#euro", "#altın"],
        ["#piyasa", "#finans", "#ekonomi"],
        ["#gramaltın", "#gümüş", "#kur"]
    ]
    return " ".join(random.choice(secenekler))


def haber_hashtagleri(baslik):
    kelimeler = [w for w in baslik.split() if len(w) > 4]
    kelimeler = kelimeler[:2] if len(kelimeler) >= 2 else kelimeler
    etiketler = ["#" + re.sub(r"[^a-zA-ZğüşöçıİĞÜŞÖÇ0-9]", "", k.lower()) for k in kelimeler]
    return "#sondakika " + " ".join(etiketler)


# --- FLOOD MODU ---

def hikaye_modu():
    konular = [
        "Tarihte az bilinen bir ihanet",
        "Dünyayı değiştiren bir bilimsel kaza",
        "Çözülememiş gizemli bir suç",
        "İlham verici bir başarı öyküsü"
    ]
    konu = random.choice(konular)

    prompt = f"""
    Konu: {konu}
    3 tweetlik sürükleyici bir flood yaz.
    JSON ver:
    {{
        "tweet1":"...",
        "tweet2":"...",
        "tweet3":"..."
    }}
    """

    data = temiz_json_al(prompt)
    if not data:
        return

    try:
        t1 = client.create_tweet(text=data["tweet1"], user_auth=True)
        time.sleep(3)
        t2 = client.create_tweet(text=data["tweet2"], in_reply_to_tweet_id=t1.data["id"], user_auth=True)
        time.sleep(3)
        client.create_tweet(text=data["tweet3"], in_reply_to_tweet_id=t2.data["id"], user_auth=True)

        logging.info("✅ Flood gönderildi")

    except Exception as e:
        logging.error(f"Flood hatası: {e}")


# --- FİNANS + HABER (TEK TWEETTE TOPLU) ---

def finans_haber_modu():
    print(">>> 📈 Finans & Haber modu çalışıyor")

    try:
        usd = yf.Ticker("USDTRY=X").history(period="1d")["Close"].iloc[-1]
        eur = yf.Ticker("EURTRY=X").history(period="1d")["Close"].iloc[-1]
        ons = yf.Ticker("GC=F").history(period="1d")["Close"].iloc[-1]
        gumus_usd = yf.Ticker("XAGUSD=X").history(period="1d")["Close"].iloc[-1]

        gram_altin = (ons / 31.1035) * usd
        ceyrek_altin = gram_altin * 1.75
        gumus_tl = (gumus_usd / 31.1035) * usd

        rss = "https://news.google.com/rss?hl=tr&gl=TR&ceid=TR:tr"
        feed = feedparser.parse(rss)
        haber = feed.entries[0].title if feed.entries else "Gündem hareketli"

        tweet = (
            f"Döviz & Değerli Madenler\n"
            f"💵 Dolar: {usd:.2f} TL\n"
            f"💶 Euro: {eur:.2f} TL\n"
            f"🥇 Gram Altın: {gram_altin:.2f} TL\n"
            f"🪙 Çeyrek Altın: {ceyrek_altin:.2f} TL\n"
            f"🥈 Gümüş: {gumus_tl:.2f} TL\n\n"
            f"Gündem: {haber}\n\n"
            f"{finans_hashtagleri()}"
        )

        client.create_tweet(text=tweet, user_auth=True)
        logging.info("✅ Finans tweeti gönderildi")

        # Ayrı haber tweeti (zorunlu #sondakika)
        haber_tweet = f"{haber}\n\n{haber_hashtagleri(haber)}"
        client.create_tweet(text=haber_tweet, user_auth=True)

        logging.info("✅ Haber tweeti gönderildi")

    except Exception as e:
        logging.error(f"Finans mod hatası: {e}")


# --- ANA ÇALIŞTIRMA ---

if __name__ == "__main__":
    print("=" * 40)
    print(f"🤖 BOT ÇALIŞIYOR — Model: {GEMINI_MODEL}")
    print("=" * 40)

    try:
        if random.random() < 0.5:
            hikaye_modu()
        else:
            finans_haber_modu()

        print(">>> ✅ İşlem tamamlandı")

    except Exception as e:
        print(f">>> 💥 Kritik hata: {e}")
