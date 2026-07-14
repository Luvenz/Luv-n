import streamlit as st
import google.generativeai as genai
import sqlite3
import pandas as pd
import json
from datetime import date

# 1. SAYFA YAPILANDIRMASI VE PREMIUM KOYU TEMA
st.set_page_config(
    page_title="Luvén - Metabolik Takip",
    page_icon="🍏",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# Geliştirilmiş Minimalist & Premium Koyu Tema CSS Yapısı
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:wght@400;500;600;700;800&display=swap');
    
    /* Genel Uygulama Alanı */
    .stApp {
        background-color: #080c14;
        color: #f3f4f6;
        font-family: 'Plus Jakarta Sans', sans-serif;
    }
    
    /* Üst Logo ve Marka Alttabanı */
    .luven-header {
        text-align: center;
        padding: 20px 0 5px 0;
    }
    .luven-title {
        font-size: 52px;
        font-weight: 800;
        background: linear-gradient(135deg, #10b981 0%, #3b82f6 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        letter-spacing: -2px;
        margin-bottom: 0px;
    }
    .luven-subtitle {
        color: #9ca3af;
        font-size: 14px;
        letter-spacing: 1px;
        text-transform: uppercase;
        font-weight: 500;
    }
    
    /* Alt Karşılama Paneli */
    .luven-footer {
        text-align: center;
        padding: 40px 0 20px 0;
        border-top: 1px solid #1f2937;
        margin-top: 50px;
    }
    .luven-welcome {
        font-size: 20px;
        font-weight: 600;
        color: #10b981;
        margin-bottom: 5px;
    }
    
    /* Kart Yapıları (Glassmorphism esintili) */
    .metric-container {
        background: rgba(17, 24, 39, 0.8);
        padding: 24px;
        border-radius: 16px;
        border: 1px solid rgba(255, 255, 255, 0.05);
        box-shadow: 0 10px 15px -3px rgba(0, 0, 0, 0.3);
        margin-bottom: 20px;
    }
    
    /* Form ve Girdi Kutuları */
    div[data-baseweb="input"], div[data-baseweb="textarea"], div[data-baseweb="select"] {
        background-color: #111827 !important;
        border: 1px solid #27272a !important;
        border-radius: 12px !important;
        padding: 2px !important;
    }
    input, textarea {
        color: #f3f4f6 !important;
    }
    
    /* Sekme (Tabs) Özelleştirmeleri */
    button[data-baseweb="tab"] {
        font-size: 16px !important;
        font-weight: 600 !important;
        color: #9ca3af !important;
        transition: all 0.3s ease;
    }
    button[aria-selected="true"] {
        color: #10b981 !important;
        border-bottom-color: #10b981 !important;
    }
    
    /* Gelişmiş Buton Tasarımları */
    .stButton>button {
        background: linear-gradient(135deg, #10b981 0%, #059669 100%) !important;
        color: #ffffff !important;
        border: none !important;
        border-radius: 12px !important;
        font-weight: 600 !important;
        padding: 0.6rem 1.8rem !important;
        transition: all 0.2s ease-in-out !important;
        box-shadow: 0 4px 12px rgba(16, 185, 129, 0.2) !important;
        width: 100%;
    }
    .stButton>button:hover {
        transform: translateY(-2px) !important;
        box-shadow: 0 12px 20px rgba(16, 185, 129, 0.4) !important;
    }
</style>
""", unsafe_allow_html=True)

# ÜST BAŞLIK (Luvén İkon & Logosu)
st.markdown("""
<div class="luven-header">
    <div class="luven-title">🍏 Luvén</div>
    <div class="luven-subtitle">Metabolik Optimizasyon & İnsülin Yönetimi</div>
</div>
""", unsafe_allow_html=True)

# 2. VERİTABANI BAĞLANTISI
conn = sqlite3.connect("metabolizma_verisi.db", check_same_thread=False)
c = conn.cursor()
c.execute('''CREATE TABLE IF NOT EXISTS meals (date TEXT, food TEXT, portion TEXT, calories INTEGER)''')
c.execute('''CREATE TABLE IF NOT EXISTS metrics (date TEXT, weight REAL, mood TEXT)''')
conn.commit()
bugun = str(date.today())

# 3. GEMINI API BAĞLANTISI
try:
    genai.configure(api_key=st.secrets["GEMINI_API_KEY"])
    model = genai.GenerativeModel('gemini-1.5-flash')
except Exception as e:
    st.warning("⚠️ Lütfen Streamlit Cloud ayarlarından 'GEMINI_API_KEY' anahtarınızı tanımlayın.")
    st.stop()

# Fonksiyonlar
def yemek_kalorisi_hesapla(metin):
    prompt = f"""
    Görev: Kullanıcının girdiği yiyecek ifadesini analiz et. İfade: '{metin}'
    Şeker hastası ve insülin direnci olan biri için porsiyonu dikkate alarak ortalama kalorisini hesapla.
    Aşağıdaki JSON formatında döndür:
    {{"yemek": "Yemek Adı", "porsiyon": "Porsiyon/Miktar", "kalori": 250}}
    """
    try:
        response = model.generate_content(prompt, generation_config={"response_mime_type": "application/json"})
        return json.loads(response.text)
    except:
        return {"yemek": metin, "porsiyon": "Belirtilmedi", "kalori": 0}

def diyetisyen_yanitla(soru, bugun_yenilenler):
    prompt = f"Sen insülin direncini kırma uzmanı bir tıp diyetisyenisin. Bugün yenilenler: {bugun_yenilenler}. Soru: '{soru}'"
    try:
        return model.generate_content(prompt).text
    except:
        return "Yanıt üretilemedi."

def diyet_listesi_uret(guncel_kilo, duygu_durumu, bugun_tuketilenler):
    prompt = f"""
    Sen şeker hastalığı ve insülin direnci tedavisi üzerine çalışan elit bir diyetisyensin.
    Kullanıcının Adı: Murat
    Mevcut Kilosu: {guncel_kilo} kg
    Bugünkü Duygu Durumu/Sağlık Durumu: {duygu_durumu}
    Bugün şu ana kadar tükettikleri: {bugun_tuketilenler}
    
    Murat için anlık, kan şekerini dalgalandırmayacak, insülin hassasiyetini artıracak mükemmel bir günlük diyet listesi oluştur.
    Öğünleri (Kahvaltı, Öğle, Ara Öğün, Akşam) net makroları ve glisemik indeks uyarılarıyla yaz. Başlığı 'Murat'a Özel Metabolik Diyet Listesi' yap.
    """
    try:
        return model.generate_content(prompt).text
    except:
        return "Diyet listesi şu an hazırlanamıyor."

# 4. SEKME SİSTEMİ (TAB DÜZENİ)
tab1, tab2 = st.tabs(["📊 Günlük Rapor & Takip", "📋 Kişiye Özel Diyet Listesi"])

# --- TAB 1: GÜNLÜK RAPOR VE GİRİŞLER ---
with tab1:
    col1, col2 = st.columns([5, 3], gap="large")

    with col1:
        st.markdown("<h3 style='color:#f3f4f6;'>🍽️ Ne Yedin?</h3>", unsafe_allow_html=True)
        yemek_girdisi = st.text_input("", placeholder="Örn: Yarım patlıcan karnıyarık ve 200 gram bulgur pilavı", key="input_yemek")
        
        if st.button("Listeme Ekle ⚡"):
            if yemek_girdisi.strip() != "":
                with st.spinner("Gemini besin değerlerini analiz ediyor..."):
                    analiz = yemek_kalorisi_hesapla(yemek_girdisi)
                    c.execute("INSERT INTO meals VALUES (?, ?, ?, ?)", (bugun, analiz['yemek'], analiz['porsiyon'], analiz['kalori']))
                    conn.commit()
                    st.success(f"Eklendi! {analiz['yemek']} ({analiz['porsiyon']}) -> {analiz['kalori']} Kalori")
                    st.rerun()
        
        st.markdown("<h3 style='color:#f3f4f6;'>📋 Bugünün Menüsü</h3>", unsafe_allow_html=True)
        df_meals = pd.read_sql_query(f"SELECT food as 'Yemek', portion as 'Porsiyon', calories as 'Kalori' FROM meals WHERE date='{bugun}'", conn)
        
        if not df_meals.empty:
            st.dataframe(df_meals, use_container_width=True, hide_index=True)
            toplam_kalori = df_meals['Kalori'].sum()
            
            st.markdown(f"""
            <div class="metric-container">
                <h4 style="margin:0; color:#10b981;">🔥 Bugün Alınan Enerji</h4>
                <p style="font-size:32px; font-weight:bold; margin:5px 0 0 0;">{toplam_kalori} <span style="font-size:18px;">Kalori</span></p>
            </div>
            """, unsafe_allow_html=True)
        else:
            st.info("Bugün henüz bir yemek eklemedin. Sağlıklı seçimler yapmaya hazır ol!")

    with col2:
        st.markdown("<h3 style='color:#f3f4f6;'>📊 Durum & Kilo Takibi</h3>", unsafe_allow_html=True)
        col_kilo, col_duygu = st.columns(2)
        with col_kilo:
            kilo = st.number_input("Kilo (kg)", min_value=30.0, max_value=250.0, value=95.5, step=0.1)
        with col_duygu:
            duygu = st.selectbox("Kendini Nasıl Hissediyorsun?", ["Normal 😊", "Enerjik ⚡", "Halsiz/Yorgun 😴", "Açlık Krizinde 🚨", "Şekerim Düştü/Yükseldi 🩸"])
            
        col_save, col_clear = st.columns(2)
        with col_save:
            if st.button("Bugünü Kaydet 💾"):
                c.execute("INSERT INTO metrics VALUES (?, ?, ?)", (bugun, kilo, duygu))
                conn.commit()
                st.success("Kaydedildi!")
        with col_clear:
            if st.button("🗑️ Günlük Verileri Sıfırla"):
                c.execute("DELETE FROM meals WHERE date=?", (bugun,))
                c.execute("DELETE FROM metrics WHERE date=?", (bugun,))
                conn.commit()
                st.success("Gün temizlendi!")
                st.rerun()

        st.markdown("<h3 style='color:#f3f4f6;'>👩‍⚕️ Akıllı Diyetisyen Asistanı</h3>", unsafe_allow_html=True)
        asistan_sorusu = st.text_area("", placeholder="Örn: Kan şekerimi fırlatmadan canımın tatlı isteğini nasıl bastırırım?", height=100)
        
        if st.button("Soruyu Sor 💬"):
            if asistan_sorusu.strip() != "":
                yenilenler_str = ", ".join(df_meals['Yemek'].tolist()) if not df_meals.empty else "Henüz bir şey girilmedi."
                with st.spinner("Uzman Diyetisyeniniz yanıt hazırlıyor..."):
                    cevap = diyetisyen_yanitla(asistan_sorusu, yenilenler_str)
                    st.info(cevap)

# --- TAB 2: ANLIK ÖZEL DİYET LİSTESİ OLUŞTURMA ---
with tab2:
    st.markdown("<h3 style='color:#10b981;'>📋 Kişiselleştirilmiş Akıllı Diyet Listesi</h3>", unsafe_allow_html=True)
    st.write("Mevcut kilonuz, duygu durumunuz ve bugün yediğiniz yemekler analiz edilerek insülin direncinizi en hızlı kıracak özel liste anlık hazırlanır.")
    
    if st.button("✨ Murat'a Özel Diyet Listesini Anlık Oluştur"):
        yenilenler_str = ", ".join(df_meals['Yemek'].tolist()) if not df_meals.empty else "Henüz bir şey girilmedi."
        with st.spinner("Gemini senin için metabolik haritayı çıkarıyor ve listeyi hazırlıyor..."):
            özel_liste = diyet_listesi_uret(kilo, duygu, yenilenler_str)
            st.markdown("---")
            st.markdown(özel_liste)
            st.markdown("---")

# ALT KARŞILAMA VE GÜVENLİ KAPANIŞ (Hoşgeldin Murat!)
st.markdown("""
<div class="luven-footer">
    <div class="luven-welcome">👋 Hoşgeldin Murat!</div>
    <div style="color: #6b7280; font-size: 13px;">Luvén ile kontrol senin elinde. En iyi haline ulaşmak için harika bir gün!</div>
</div>
""", unsafe_allow_html=True)
