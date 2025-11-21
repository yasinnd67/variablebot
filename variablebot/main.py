import tweepy
import google.generativeai as genai
import os
import random
from dotenv import load_dotenv

# --- AYARLAR ---
load_dotenv()
API_MODEL = 'gemini-2.5-flash'  # Çalışan model ismini buraya yazıyoruz

# Twitter Client
client = tweepy.Client(
    consumer_key=os.getenv("TWITTER_API_KEY"),
    consumer_secret=os.getenv("TWITTER_API_SECRET"),
    access_token=os.getenv("TWITTER_ACCESS_TOKEN"),
    access_token_secret=os.getenv("TWITTER_ACCESS_TOKEN_SECRET")
)

# Gemini Client
genai.configure(api_key=os.getenv("GEMINI_API_KEY"))
model = genai.GenerativeModel(API_MODEL)

# --- İÇERİK ÜRETİM FONKSİYONLARI ---

def icerik_yapay_zeka_hikaye():
    # 1. Hikaye/Bilgi Botu
    prompt = "Twitter için ilgi çekici, kısa ve az bilinen bir bilimsel gerçeği veya tarihi olayı, alakasız bir emoji ekleyerek tivit olarak hazırla. (Maksimum 280 karakter)"
    response = model.generate_content(prompt)
    return response.text

def icerik_romantik_soz():
    # 2. Romantik Söz/Şiir Botu
    prompt = "Twitter'da paylaşılmak üzere, kısa ve duygusal, özgün bir romantik şiir dizesini veya derin anlamlı bir sözü yaz. #Aşk etiketini kullan."
    response = model.generate_content(prompt)
    return response.text

def icerik_burc_yorumu():
    # 3. Haftalık Burç Yorumu
    burclar = ["Koç", "Boğa", "İkizler", "Yengeç", "Aslan", "Başak", "Terazi", "Akrep", "Yay", "Oğlak", "Kova", "Balık"]
    rastgele_burc = random.choice(burclar)
    prompt = f"Twitter için {rastgele_burc} burcunun bu haftaki ruh hali ve kariyer yorumunu (kısa, pozitif ve ilgi çekici) bir tivit metni olarak yaz. 'Bu hafta {rastgele_burc} burcu' diye başla."
    response = model.generate_content(prompt)
    return response.text

def icerik_secim_anketi():
    # 4. Hangisini Seçerdin?
    prompt = "Twitter kullanıcılarının yorum yapmasını sağlamak için, iki zor ve eğlenceli seçenek sunan (Örn: A mı B mi?) bir 'Hangisini Seçerdin?' tivit metni hazırla. Cevabı metin içinde verme."
    response = model.generate_content(prompt)
    return response.text

def icerik_gunun_kelimesi():
    # 5. Günün Kelimesi
    prompt = "Twitter için az bilinen, güzel bir Türkçe kelime (Örn: Yeğlemek) ve onun kısa, anlaşılır tanımını içeren bir tivit metni yaz. #GününKelimesi etiketini ekle."
    response = model.generate_content(prompt)
    return response.text

def icerik_burc_listesi():
    # 6. Burç Listesi (Kin, Titizlik vb.)
    konular = ["En Kinci", "En Titiz", "En Sakin", "En Kararsız"]
    rastgele_konu = random.choice(konular)
    prompt = f"Twitter için '{rastgele_konu} olan 3 burç' listesini, mizahi ve ilgi çekici bir tonda, emojilerle birlikte tivit metni olarak hazırla."
    response = model.generate_content(prompt)
    return response.text

# --- ZAR ATMA VE ÇALIŞTIRMA MANTIĞI ---

def botu_calistir():
    # 1'den 6'ya kadar rastgele bir sayı seç
    zar = random.randint(1, 6)
    
    # Seçilen sayıya göre doğru fonksiyonu çağır
    if zar == 1:
        tweet_text = icerik_yapay_zeka_hikaye()
        print(f"Zar: {zar}. İçerik: Hikaye/Bilgi.")
    elif zar == 2:
        tweet_text = icerik_romantik_soz()
        print(f"Zar: {zar}. İçerik: Romantik Söz.")
    elif zar == 3:
        tweet_text = icerik_burc_yorumu()
        print(f"Zar: {zar}. İçerik: Burç Yorumu.")
    elif zar == 4:
        tweet_text = icerik_secim_anketi()
        print(f"Zar: {zar}. İçerik: Seçim Anketi.")
    elif zar == 5:
        tweet_text = icerik_gunun_kelimesi()
        print(f"Zar: {zar}. İçerik: Günün Kelimesi.")
    elif zar == 6:
        tweet_text = icerik_burc_listesi()
        print(f"Zar: {zar}. İçerik: Burç Listesi.")
    else:
        # Normalde buraya düşmemeli, ama düşerse hata tiviti atsın
        tweet_text = "Bir hata oluştu, zar 1 ile 6 arasında değil. Bot resetleniyor. 🤖"
        print(f"❌ Hata: Zar beklenenin dışında.")


    # Sonuç Tivitini At
    if tweet_text:
        try:
            client.create_tweet(text=tweet_text) 
            print("✅ BAŞARILI! Tivit atıldı. İçerik:")
            print("---")
            print(tweet_text)
            print("---")
        except Exception as e:
            print(f"❌ Twitter Hatası: Tivit atılamadı. Hata: {e}")

# Botu çalıştır
if __name__ == "__main__":
    botu_calistir()