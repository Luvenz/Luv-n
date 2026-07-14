# 🍏 Akıllı Metabolik Takip & Diyet Asistanı

Bu uygulama, şeker hastaları ve insülin direnci olan bireyler için özel olarak geliştirilmiş, tamamen ücretsiz çalışan bir kalori takip ve yapay zeka diyetisyen asistanıdır. Google Gemini API gücüyle çalışır.

## 🚀 Bilgisayarına Python Kurmadan, Tamamen Ücretsiz Canlıya Alma (Hosting) Adımları:

Bilgisayarına Python yüklemene gerek yok! Bu uygulamayı internete yükleyip kendi telefonundan veya bilgisayarından bir web sitesi gibi girmek için şu adımları takip et:

### 1. Adım: GitHub Hesabı Aç ve Kodları Yükle
1. [GitHub](https://github.com/) sitesine git ve ücretsiz bir hesap aç.
2. Sağ üstteki **"+"** butonuna basıp **"New repository"** (Yeni Depo) seçeneğine tıkla.
3. Depoya bir isim ver (Örn: `metabolik-takip`) ve **"Public"** (Açık) olarak işaretle. **"Create repository"** butonuna bas.
4. Açılan sayfadaki **"uploading an existing file"** (mevcut bir dosyayı yükle) linkine tıkla.
5. Bu ZIP dosyasından çıkardığın `app.py` ve `requirements.txt` dosyalarını sürükleyip buraya bırak.
6. Sayfanın altındaki yeşil **"Commit changes"** butonuna bas. Dosyaların artık internette!

### 2. Adım: Gemini API Anahtarını Al (Tamamen Ücretsiz)
1. [Google AI Studio](https://aistudio.google.com/) adresine Google hesabınla giriş yap.
2. Sol üstteki mavi **"Get API key"** butonuna bas.
3. **"Create API Key"** seçeneğine tıkla ve sana verilen uzun kodu (API Anahtarını) kopyalayıp bir yere not et.

### 3. Adım: Uygulamayı Yayına Al (Streamlit Share)
1. [Streamlit Community Cloud](https://share.streamlit.io/) sitesine git.
2. **"Continue with GitHub"** butonuna basarak GitHub hesabınla giriş yap.
3. Giriş yaptıktan sonra sağ üstteki **"New app"** (Yeni Uygulama) butonuna tıkla.
4. Karşına çıkan formda:
   - **Repository:** GitHub'da açtığın depoyu seç (`kullanici_adin/metabolik-takip`).
   - **Branch:** `main` veya `master` olarak kalacak.
   - **Main file path:** `app.py` yaz.
5. **ÖNEMLİ AYAR (API Bağlantısı):**
   - Sayfanın sağ alt köşesindeki **"Advanced settings..."** (Gelişmiş Ayarlar) yazısına tıkla.
   - **Secrets (Sırlar)** kutusuna şu satırı yapıştır ve tırnak içindeki kısma 2. Adımda aldığın Gemini API anahtarını yaz:
     ```toml
     GEMINI_API_KEY = "BURAYA_ALDIĞIN_API_ANAHTARINI_YAPIŞTIR"
     ```
   - **Save** butonuna basarak kaydet.
6. Şimdi büyük mavi **"Deploy!"** butonuna bas.

Uygulaman 1-2 dakika içinde hazır olacak ve sana özel, sürekli kullanabileceğin bir **web linki** verilecek. Bu linki telefonuna kaydedip her gün kullanabilirsin!
