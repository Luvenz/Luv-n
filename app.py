import streamlit as st
import google.generativeai as genai
import sqlite3
import pandas as pd
import json
from datetime import date

# 1. SAYFA YAPILANDIRMASI VE KOYU TEMA DETAYLARI
st.set_page_config(
    page_title="Metabolik Takip & Diyet Asistanı",
    page_icon="🍏",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# Minimalist Koyu Tema ve Tasarım için CSS Enjeksiyonu
st.markdown("""
<style>
    /* Arka plan ve genel metin rengi */
    .stApp {
        background-color: #0b0f19;
        color: #f3f4f6;
        font-family: 'Inter', -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif;
    }
    
    /* Başlıklar */
    h1 {
        font-weight: 800;
        letter-spacing: -0.05em;
        color: #10b981 !important; /* Neon Yeşil tonu */
        margin-bottom: 10px;
    }
    h2, h3 {
        font-weight: 600;
        color: #e5e7eb !important;
        border-bottom: 1px solid #1f2937;
        padding-bottom: 8px;
    }
    
    /* Girdi Kutuları */
    div[data-baseweb="input"] {
        background-color: #111827 !important;
        border: 1px solid #374151 !important;
        border-radius: 8px !important;
    }
    input {
        color: #f3f4f6 !important;
    }
    
    /* Buton Tasarımları */
    .stButton>button {
        background: linear-gradient(135deg, #10b981 0%, #059669 100%) !important;
        color: #ffffff !important;
        border: none !important;
        border-radius: 8px !important;
        font-weight: 600 !important;
        padding: 0.5rem 1.5rem !important;
        transition: all 0.2s ease-in-out !important;
        box-shadow: 0 4px 6px -1px rgba(16, 185, 129, 0.2) !important;
    }
    .stButton>button:hover {
        transform: translateY(-1px) !important;
        box-shadow: 0 10px 15px -3px rgba(16, 185, 129, 0.4) !important;
    }
    
    /* Bilgi kartları ve Kalori Kutuları */
    .metric-container {
        background-color: #111827;
        padding: 20px;
        border-radius: 12px;
        border: 1px solid #1f2937;
        margin-bottom: 15px;
    }
    
    /* DataFrame tablosu */
    .stDataFrame {
        background-color: #111827;
        border-radius: 12px;
        overflow: hidden;
    }
</style>
""", unsafe_allow_html=True)

# 2. VERİTABANI BAĞLANTISI (Local SQLite3)
conn = sqlite3.connect("metabolizma_verisi.db", check_same_thread=False)
c = conn.cursor()
c.execute('''CREATE TABLE IF NOT EXISTS meals (date TEXT, food TEXT, portion TEXT, calories INTEGER)''')
c.execute('''CREATE TABLE IF NOT EXISTS metrics (date TEXT, weight REAL, mood TEXT)''')
conn.commit()
bugun = str(date.today())

# 3. GEMINI API ENTEGRASYONU
try:
    # Streamlit Secrets üzerinden API anahtarını güvenle alıyoruz
    genai.configure(api_key=st.secrets["GEMINI_API_KEY"])
    model = genai.GenerativeModel('gemini-1.5-flash')
except Exception as e:
    st.warning("⚠️ Lütfen Streamlit Cloud ayarlarından 'GEMINI_API_KEY' anahtarınızı tanımlayın.")
    st.info("Yerel çalıştırma yapıyorsanız, .streamlit/secrets.toml dosyasına API anahtarınızı ekleyin.")
    st.stop()

# Yapay Zeka Kalori Hesaplama Fonksiyonu
def yemek_kalorisi_hesapla(metin):
    prompt = f"""
    Görev: Kullanıcının girdiği yiyecek ifadesini analiz et. 
    İfade: '{metin}'
    
    Kurallar:
    1. Yiyeceğin ortalama kalorisini hesapla.
    2. Şeker hastası (diyabet) ve insülin direnci olan biri için porsiyon büyüklüğünü dikkate alarak gerçekçi ol.
    3. Yanıtı SADECE aşağıdaki JSON formatında ver. Başka hiçbir açıklama, markdown işareti veya ek metin ekleme.
    
    JSON Formatı:
    {{"yemek": "Düzgünleştirilmiş Yemek Adı", "porsiyon": "Porsiyon/Miktar", "kalori": 250}}
    """
    try:
        response = model.generate_content(prompt)
        text_reply = response.text.replace('```json', '').replace('```', '').strip()
        data = json.loads(text_reply)
        return data
    except Exception as e:
        # Hata durumunda fallback (geri çekilme) mekanizması
        return {"yemek": metin, "porsiyon": "Belirtilmedi", "kalori": 0}

# Yapay Zeka Özel Diyabet ve İnsülin Diyetisyeni Fonksiyonu
def diyetisyen_yanitla(soru, bugun_yenilenler):
    prompt = f"""
    Sen insülin direncini kırma, kan şekerini optimize etme ve diyabet yönetiminde uzmanlaşmış profesyonel bir tıp diyetisyenisin.
    Amacın kullanıcının kan şekerini stabilize etmek ve en iyi metabolik haline ulaşmasını sağlamaktır.
    
    Bugün kullanıcının yediği şeyler: {bugun_yenilenler}
    
    Kullanıcının Sorusu: '{soru}'
    
    Yanıt Kuralları:
    - Son derece destekleyici, bilimsel ama sade ve anlaşılır bir dil kullan.
    - Düşük glisemik indeksli alternatifler öner.
    - Kan şekerini dalgalandırmayacak karbonhidrat-protein-yağ dengesine odaklan.
    - Yanıtını çok uzun tutma, doğrudan uygulanabilir pratik tavsiyeler ver.
    """
    try:
        response = model.generate_content(prompt)
        return response.text
    except Exception as e:
        return "Üzgünüm, şu anda yanıt üretemiyorum. Lütfen internet bağlantınızı veya API anahtarınızı kontrol edin."

# 4. ARAYÜZ TASARIMI VE KULLANICI DENEYİMİ
st.title("🍏 METABOLİK TAKİP")
st.write("Şeker Hastalığı & İnsülin Direnci Yönetimi için Kişisel Akıllı Panelin.")

# Sol ve Sağ Kolon Düzeni
col1, col2 = st.columns([5, 3], gap="large")

with col1:
    st.subheader("🍽️ Ne Yedin?")
    yemek_girdisi = st.text_input("", placeholder="Örn: 1 porsiyon tavuk şiş ve bol yeşil salata, 1 kase yoğurt", key="input_yemek")
    
    if st.button("Listeme Ekle ⚡"):
        if yemek_girdisi.strip() != "":
            with st.spinner("Gemini besin değerlerini analiz ediyor..."):
                analiz = yemek_kalorisi_hesapla(yemek_girdisi)
                c.execute("INSERT INTO meals VALUES (?, ?, ?, ?)", (bugun, analiz['yemek'], analiz['porsiyon'], analiz['kalori']))
                conn.commit()
                st.success(f"Eklendi! {analiz['yemek']} ({analiz['porsiyon']}) -> {analiz['kalori']} Kalori")
        else:
            st.warning("Lütfen yediğiniz bir şeyi yazın.")

    st.subheader("📋 Bugünün Menüsü")
    df_meals = pd.read_sql_query(f"SELECT food as 'Yemek', portion as 'Porsiyon', calories as 'Kalori' FROM meals WHERE date='{bugun}'", conn)
    
    if not df_meals.empty:
        st.dataframe(df_meals, use_container_width=True, hide_index=True)
        toplam_kalori = df_meals['Kalori'].sum()
        
        # Kalori Göstergesi
        st.markdown(f"""
        <div class="metric-container">
            <h4 style="margin:0; color:#10b981;">🔥 Bugün Alınan Enerji</h4>
            <p style="font-size:28px; font-weight:bold; margin:5px 0 0 0;">{toplam_kalori} <span style="font-size:16px;">Kalori</span></p>
        </div>
        """, unsafe_allow_html=True)
    else:
        st.info("Bugün henüz bir yemek eklemedin. Sağlıklı seçimler yapmaya hazır ol!")

with col2:
    st.subheader("📊 Durum & Kilo Takibi")
    
    col_kilo, col_duygu = st.columns(2)
    with col_kilo:
        kilo = st.number_input("Kilo (kg)", min_value=30.0, max_value=250.0, value=75.0, step=0.1)
    with col_duygu:
        duygu = st.selectbox("Kendini Nasıl Hissediyorsun?", ["Enerjik ⚡", "Normal 😊", "Halsiz/Yorgun 😴", "Açlık Krizinde 🚨", "Şekerim Düştü/Yükseldi 🩸"])
        
    if st.button("Bugünü Kaydet 💾"):
        c.execute("INSERT INTO metrics VALUES (?, ?, ?)", (bugun, kilo, duygu))
        conn.commit()
        st.success("Durumunuz başarıyla günlüğe eklendi!")

    st.subheader("👩‍⚕️ İnsülin & Diyabet Asistanı")
    st.caption("Kan şekerini dengelemek, insülin direncini düşürmek için aklındaki her şeyi sor.")
    
    asistan_sorusu = st.text_area("", placeholder="Örn: Akşam canım çok tatlı çekti, şekerimi fırlatmadan ne yiyebilirim?", height=100)
    
    if st.button("Soruyu Sor 💬"):
        if asistan_sorusu.strip() != "":
            # Bugün yediklerini asistanın görmesi için listeliyoruz
            yenilenler_str = ", ".join(df_meals['Yemek'].tolist()) if not df_meals.empty else "Henüz bir şey girilmedi."
            
            with st.spinner("Uzman Diyetisyeniniz yanıt hazırlıyor..."):
                cevap = diyetisyen_yanitla(asistan_sorusu, yenilenler_str)
                st.info(cevap)
        else:
            st.warning("Lütfen asistanınıza bir soru yazın.")
