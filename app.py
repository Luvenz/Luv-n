import streamlit as st
import google.generativeai as genai
import pandas as pd
import json
from datetime import datetime, timedelta
from pathlib import Path

# ──────────────────────────────────────────────
#  Luvén — Kişisel Diyet & Kalori Takip Uygulaması
# ──────────────────────────────────────────────

# Sayfa ayarı - EN BAŞTA olmalı
st.set_page_config(
    page_title="Luvén",
    page_icon="🌿",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ──────────────────────────────────────────────
#  Gemini API Key - Secrets'tan al
# ──────────────────────────────────────────────
def get_api_key():
    """Streamlit secrets'tan API key al."""
    try:
        return st.secrets["GEMINI_API_KEY"]
    except Exception:
        return None

API_KEY = get_api_key()

# ──────────────────────────────────────────────
#  Veri yönetimi (JSON tabanlı)
# ──────────────────────────────────────────────
DATA_DIR = Path("data")
DATA_DIR.mkdir(exist_ok=True)

PROFILE_FILE = DATA_DIR / "profile.json"
MEALS_FILE = DATA_DIR / "meals.json"
BODY_FILE = DATA_DIR / "body_metrics.json"
WATER_FILE = DATA_DIR / "water.json"
DIET_FILE = DATA_DIR / "diet_plan.json"


def load_json(path, default=None):
    if default is None:
        default = {}
    try:
        if path.exists():
            with open(path, "r", encoding="utf-8") as f:
                return json.load(f)
    except Exception:
        pass
    return default


def save_json(path, data):
    try:
        with open(path, "w", encoding="utf-8") as f:
            json.dump(data, f, ensure_ascii=False, indent=2, default=str)
    except Exception:
        pass


def load_profile():
    default = {
        "name": "Murat",
        "height": 178,
        "weight": 80,
        "age": 28,
        "gender": "Erkek",
        "activity": "Orta Düzey",
        "goal": "Kilo Verme",
        "daily_calorie_target": 2200,
    }
    return load_json(PROFILE_FILE, default)


def load_meals():
    return load_json(MEALS_FILE, {})


def load_body_metrics():
    return load_json(BODY_FILE, {})


def load_water():
    return load_json(WATER_FILE, {})


def load_diet_plan():
    return load_json(DIET_FILE, {})


# ──────────────────────────────────────────────
#  Hesaplama fonksiyonları
# ──────────────────────────────────────────────
def calculate_bmr(profile):
    w = float(profile.get("weight", 80))
    h = float(profile.get("height", 178))
    a = int(profile.get("age", 28))
    g = profile.get("gender", "Erkek")
    if g == "Erkek":
        bmr = 10 * w + 6.25 * h - 5 * a + 5
    else:
        bmr = 10 * w + 6.25 * h - 5 * a - 161
    return bmr


def calculate_tdee(profile):
    bmr = calculate_bmr(profile)
    multipliers = {
        "Hareketsiz": 1.2,
        "Az Hareketli": 1.375,
        "Orta Düzey": 1.55,
        "Aktif": 1.725,
        "Çok Aktif": 1.9,
    }
    m = multipliers.get(profile.get("activity", "Orta Düzey"), 1.55)
    tdee = bmr * m
    
    goal = profile.get("goal", "Kilo Koruma")
    if goal == "Kilo Verme":
        tdee -= 500
    elif goal == "Kas Yapma":
        tdee += 300
    
    return round(tdee)


def get_today():
    return datetime.now().strftime("%Y-%m-%d")


def get_bmi(profile):
    h_m = float(profile.get("height", 178)) / 100
    w = float(profile.get("weight", 80))
    if h_m > 0:
        return round(w / (h_m ** 2), 1)
    return 0


def get_bmi_category(bmi):
    if bmi < 18.5:
        return "Zayıf", "⚠️"
    elif bmi < 25:
        return "Normal", "✅"
    elif bmi < 30:
        return "Fazla Kilolu", "⚠️"
    else:
        return "Obez", "🔴"


# ──────────────────────────────────────────────
#  Gemini AI
# ──────────────────────────────────────────────
def get_gemini_model():
    if not API_KEY:
        return None
    try:
        genai.configure(api_key=API_KEY)
        model = genai.GenerativeModel("gemini-2.0-flash")
        return model
    except Exception:
        return None


def ask_gemini(prompt, system_instruction=""):
    model = get_gemini_model()
    if not model:
        return "⚠️ Gemini API anahtarı bulunamadı. Lütfen Streamlit secrets'a GEMINI_API_KEY ekleyin."
    try:
        full_prompt = f"{system_instruction}\n\n{prompt}" if system_instruction else prompt
        response = model.generate_content(full_prompt)
        return response.text
    except Exception as e:
        return f"❌ Hata: {str(e)}"


def estimate_calories(food_text):
    prompt = f"""Aşağıdaki yemek için tahmini kalori değerini hesapla.
Sadece JSON formatında yanıt ver, başka hiçbir şey yazma.
Format: {{"food": "yemek adı", "calories": sayı, "protein": sayı, "carbs": sayı, "fat": sayı, "portion": "porsiyon bilgisi"}}

Yemek: {food_text}"""

    result = ask_gemini(prompt, "Sen bir beslenme uzmanısın. Türk mutfağını çok iyi biliyorsun. Kalori değerlerini ortalama porsiyon boyutuna göre hesapla. Yanıtını kesinlikle sadece JSON formatında ver.")
    
    try:
        clean = result.strip()
        if clean.startswith("```"):
            lines = clean.split("\n")
            clean = "\n".join(lines[1:-1]) if len(lines) > 2 else clean[3:-3]
        if clean.startswith("json"):
            clean = clean[4:].strip()
        return json.loads(clean)
    except Exception:
        return {"food": food_text, "calories": 0, "protein": 0, "carbs": 0, "fat": 0, "portion": "Bilinmiyor"}


# ──────────────────────────────────────────────
#  CSS Stilleri
# ──────────────────────────────────────────────
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700;800;900&display=swap');

.stApp {
    font-family: 'Inter', sans-serif;
}

section[data-testid="stSidebar"] {
    background: linear-gradient(180deg, #0f0f0f 0%, #1a1a2e 100%);
}

.luven-title {
    font-size: 2.5rem;
    font-weight: 900;
    background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
    background-clip: text;
    text-align: center;
    margin-bottom: 0;
}

.luven-subtitle {
    text-align: center;
    color: #888;
    font-size: 0.85rem;
    margin-top: 0;
    margin-bottom: 20px;
    letter-spacing: 3px;
}

.metric-card {
    background: linear-gradient(135deg, #1a1a2e 0%, #16213e 100%);
    border: 1px solid rgba(102, 126, 234, 0.2);
    border-radius: 16px;
    padding: 20px;
    text-align: center;
    margin: 8px 0;
}

.metric-value {
    font-size: 2rem;
    font-weight: 800;
    background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
    background-clip: text;
}

.metric-label {
    font-size: 0.75rem;
    color: #999;
    text-transform: uppercase;
    letter-spacing: 1px;
}

.metric-sub {
    font-size: 0.7rem;
    color: #667eea;
    margin-top: 4px;
}

.welcome-card {
    background: linear-gradient(135deg, #0f0f23 0%, #1a1a2e 50%, #16213e 100%);
    border: 1px solid rgba(102,126,234,0.3);
    border-radius: 20px;
    padding: 30px;
    text-align: center;
    margin-bottom: 20px;
}

.welcome-name {
    font-size: 1.8rem;
    font-weight: 800;
    color: #fff;
}

.calorie-display {
    font-size: 3rem;
    font-weight: 900;
    background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
    background-clip: text;
}

.food-item {
    background: rgba(255,255,255,0.03);
    border: 1px solid rgba(255,255,255,0.08);
    border-radius: 12px;
    padding: 12px 16px;
    margin: 6px 0;
}

.progress-up {
    background: linear-gradient(135deg, #0a2e1a 0%, #0f3d22 100%);
    border: 1px solid rgba(34,197,94,0.3);
    border-radius: 12px;
    padding: 16px;
    margin: 6px 0;
}

.progress-down {
    background: linear-gradient(135deg, #2e0a0a 0%, #3d0f0f 100%);
    border: 1px solid rgba(239,68,68,0.3);
    border-radius: 12px;
    padding: 16px;
    margin: 6px 0;
}

.progress-neutral {
    background: linear-gradient(135deg, #1a1a2e 0%, #16213e 100%);
    border: 1px solid rgba(102,126,234,0.2);
    border-radius: 12px;
    padding: 16px;
    margin: 6px 0;
}
</style>
""", unsafe_allow_html=True)


# ──────────────────────────────────────────────
#  Sidebar
# ──────────────────────────────────────────────
with st.sidebar:
    st.markdown("# 🌿 Luvén")
    st.caption("KİŞİSEL DİYET ASİSTANI")
    
    st.divider()
    
    # API durumu
    if API_KEY:
        st.success("✓ Gemini API Bağlı", icon="🔑")
    else:
        st.error("✗ API Key bulunamadı", icon="🔑")
        st.caption("secrets.toml'a GEMINI_API_KEY ekleyin")
    
    st.divider()
    
    # Profil ayarları
    st.markdown("### ⚙️ Profil")
    
    profile = load_profile()
    
    with st.expander("Profili Düzenle", expanded=False):
        name = st.text_input("İsim", value=profile.get("name", "Murat"))
        height = st.number_input("Boy (cm)", value=int(profile.get("height", 178)), min_value=100, max_value=250)
        weight = st.number_input("Kilo (kg)", value=float(profile.get("weight", 80)), min_value=30.0, max_value=300.0, step=0.1)
        age = st.number_input("Yaş", value=int(profile.get("age", 28)), min_value=10, max_value=100)
        gender = st.selectbox("Cinsiyet", ["Erkek", "Kadın"], index=0 if profile.get("gender") == "Erkek" else 1)
        activity = st.selectbox("Aktivite", ["Hareketsiz", "Az Hareketli", "Orta Düzey", "Aktif", "Çok Aktif"], 
                               index=["Hareketsiz", "Az Hareketli", "Orta Düzey", "Aktif", "Çok Aktif"].index(profile.get("activity", "Orta Düzey")))
        goal = st.selectbox("Hedef", ["Kilo Verme", "Kilo Koruma", "Kas Yapma"],
                           index=["Kilo Verme", "Kilo Koruma", "Kas Yapma"].index(profile.get("goal", "Kilo Verme")))
        
        if st.button("💾 Kaydet", use_container_width=True):
            new_profile = {
                "name": name,
                "height": height,
                "weight": weight,
                "age": age,
                "gender": gender,
                "activity": activity,
                "goal": goal,
                "daily_calorie_target": calculate_tdee({
                    "weight": weight, "height": height, "age": age,
                    "gender": gender, "activity": activity, "goal": goal
                }),
            }
            save_json(PROFILE_FILE, new_profile)
            st.success("Kaydedildi!")
            st.rerun()
    
    # Profil özeti
    profile = load_profile()
    bmi = get_bmi(profile)
    bmi_cat, bmi_icon = get_bmi_category(bmi)
    daily_target = calculate_tdee(profile)
    
    st.markdown(f"""
    **{profile['name']}**  
    📏 {profile['height']}cm | ⚖️ {profile['weight']}kg  
    BMI: **{bmi}** {bmi_icon} {bmi_cat}  
    🎯 Günlük: **{daily_target} kcal**
    """)


# ──────────────────────────────────────────────
#  Ana Sayfa Başlık
# ──────────────────────────────────────────────
st.markdown('<p class="luven-title">🌿 Luvén</p>', unsafe_allow_html=True)
st.markdown('<p class="luven-subtitle">KİŞİSEL DİYET & KALORİ TAKİP</p>', unsafe_allow_html=True)

# ──────────────────────────────────────────────
#  Sekmeler
# ──────────────────────────────────────────────
tab1, tab2, tab3, tab4, tab5 = st.tabs([
    "🏠 Ana Sayfa",
    "🍽️ Yemek Takibi", 
    "📊 Vücut Ölçüleri",
    "🤖 Diyet Programı",
    "💧 Su Takibi"
])


# ═══════════════════════════════════════════════
#  TAB 1: ANA SAYFA
# ═══════════════════════════════════════════════
with tab1:
    profile = load_profile()
    today = get_today()
    meals = load_meals()
    today_meals = meals.get(today, [])
    
    total_cal = sum(m.get("calories", 0) for m in today_meals)
    target = calculate_tdee(profile)
    remaining = max(0, target - total_cal)
    pct = min(100, round((total_cal / target) * 100)) if target > 0 else 0
    
    # Selamlama
    hour = datetime.now().hour
    if hour < 12:
        greeting = "Günaydın"
    elif hour < 18:
        greeting = "İyi Günler"
    else:
        greeting = "İyi Akşamlar"
    
    # Hoşgeldin kartı
    if remaining > 0:
        calorie_msg = f"🟢 {remaining} Kalori Daha Alabilirsin!"
        msg_color = "#22c55e"
    else:
        over = total_cal - target
        calorie_msg = f"🔴 Kalori Limitini {over} kcal Aştın!"
        msg_color = "#ef4444"
    
    st.markdown(f"""
    <div class="welcome-card">
        <div style="color: #888; font-size: 1rem;">{greeting}</div>
        <div class="welcome-name">Hoşgeldin {profile['name']}! 👋</div>
        <div style="margin: 25px 0;">
            <div class="calorie-display">{remaining}</div>
            <div style="color: #888; font-size: 0.85rem;">KALAN KALORİ</div>
        </div>
        <div style="color: {msg_color}; font-size: 1.1rem; font-weight: 700;">
            {calorie_msg}
        </div>
        <div style="margin-top: 15px;">
            <div style="background: rgba(255,255,255,0.1); border-radius: 10px; height: 10px; overflow: hidden;">
                <div style="width: {pct}%; height: 100%; background: linear-gradient(90deg, #667eea, #764ba2); border-radius: 10px;"></div>
            </div>
            <div style="display: flex; justify-content: space-between; color: #888; font-size: 0.75rem; margin-top: 5px;">
                <span>Alınan: {total_cal} kcal</span>
                <span>%{pct}</span>
                <span>Hedef: {target} kcal</span>
            </div>
        </div>
    </div>
    """, unsafe_allow_html=True)
    
    # Makrolar
    total_protein = sum(m.get("protein", 0) for m in today_meals)
    total_carbs = sum(m.get("carbs", 0) for m in today_meals)
    total_fat = sum(m.get("fat", 0) for m in today_meals)
    
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.markdown(f"""
        <div class="metric-card">
            <div class="metric-label">🔥 Kalori</div>
            <div class="metric-value">{total_cal}</div>
            <div class="metric-sub">/ {target} kcal</div>
        </div>
        """, unsafe_allow_html=True)
    
    with col2:
        st.markdown(f"""
        <div class="metric-card">
            <div class="metric-label">🥩 Protein</div>
            <div class="metric-value">{total_protein}g</div>
            <div class="metric-sub">hedef ~{round(float(profile['weight']) * 1.6)}g</div>
        </div>
        """, unsafe_allow_html=True)
    
    with col3:
        st.markdown(f"""
        <div class="metric-card">
            <div class="metric-label">🍞 Karbonhidrat</div>
            <div class="metric-value">{total_carbs}g</div>
            <div class="metric-sub">makro</div>
        </div>
        """, unsafe_allow_html=True)
    
    with col4:
        st.markdown(f"""
        <div class="metric-card">
            <div class="metric-label">🧈 Yağ</div>
            <div class="metric-value">{total_fat}g</div>
            <div class="metric-sub">makro</div>
        </div>
        """, unsafe_allow_html=True)
    
    # Bugünün yemekleri
    st.markdown("### 📋 Bugün Yediklerin")
    
    if today_meals:
        for meal in today_meals:
            st.markdown(f"""
            <div class="food-item">
                <span style="font-weight: 600; color: #e0e0e0;">{meal.get('food', '?')}</span>
                <span style="color: #888; font-size: 0.85rem;"> — {meal.get('portion', '')}</span>
                <span style="float: right; color: #667eea; font-weight: 700;">{meal.get('calories', 0)} kcal</span>
            </div>
            """, unsafe_allow_html=True)
    else:
        st.info("Henüz bugün yemek girişi yok. 🍽️ Yemek Takibi sekmesinden ekle!")


# ═══════════════════════════════════════════════
#  TAB 2: YEMEK TAKİBİ
# ═══════════════════════════════════════════════
with tab2:
    st.markdown("### 🍽️ Yemek Takibi")
    st.markdown("Yediğin yemeği yaz, Gemini AI kalori hesaplasın.")
    
    meals = load_meals()
    
    # Tarih seçimi
    selected_date = st.date_input("📅 Tarih", value=datetime.now(), max_value=datetime.now(), key="meal_date")
    date_key = selected_date.strftime("%Y-%m-%d")
    
    # Yemek girişi
    col_input, col_total = st.columns([3, 1])
    
    with col_input:
        food_input = st.text_input("🍕 Ne yedin?", placeholder="örn: 1 porsiyon karnıyarık, 1 bardak ayran")
        
        if st.button("📊 Kalori Hesapla & Ekle", use_container_width=True, type="primary"):
            if food_input:
                with st.spinner("🤖 Gemini analiz ediyor..."):
                    result = estimate_calories(food_input)
                
                if result.get("calories", 0) > 0:
                    result["time"] = datetime.now().strftime("%H:%M")
                    
                    if date_key not in meals:
                        meals[date_key] = []
                    meals[date_key].append(result)
                    save_json(MEALS_FILE, meals)
                    
                    st.success(f"✅ {result['food']} — **{result['calories']} kcal** eklendi!")
                    st.rerun()
                else:
                    st.warning("Kalori hesaplanamadı. Daha detaylı yazın veya API'yi kontrol edin.")
            else:
                st.warning("Lütfen bir yemek girin.")
    
    with col_total:
        day_meals = meals.get(date_key, [])
        day_total = sum(m.get("calories", 0) for m in day_meals)
        st.metric("📅 Toplam", f"{day_total} kcal")
    
    st.divider()
    
    # Günün yemek listesi
    day_meals = meals.get(date_key, [])
    
    if day_meals:
        st.markdown(f"### 📋 {date_key} Yemek Listesi")
        
        for i, meal in enumerate(day_meals):
            cols = st.columns([4, 1, 1, 1, 1, 0.5])
            with cols[0]:
                st.write(f"**{meal.get('food', '?')}** ({meal.get('portion', '')})")
            with cols[1]:
                st.write(f"🔥 {meal.get('calories', 0)}")
            with cols[2]:
                st.write(f"🥩 {meal.get('protein', 0)}g")
            with cols[3]:
                st.write(f"🍞 {meal.get('carbs', 0)}g")
            with cols[4]:
                st.write(f"🧈 {meal.get('fat', 0)}g")
            with cols[5]:
                if st.button("🗑️", key=f"del_{date_key}_{i}"):
                    meals[date_key].pop(i)
                    save_json(MEALS_FILE, meals)
                    st.rerun()
        
        # Toplamlar
        st.divider()
        tot_cols = st.columns([4, 1, 1, 1, 1, 0.5])
        with tot_cols[0]:
            st.write("**TOPLAM**")
        with tot_cols[1]:
            st.write(f"**{sum(m.get('calories', 0) for m in day_meals)}**")
        with tot_cols[2]:
            st.write(f"**{sum(m.get('protein', 0) for m in day_meals)}g**")
        with tot_cols[3]:
            st.write(f"**{sum(m.get('carbs', 0) for m in day_meals)}g**")
        with tot_cols[4]:
            st.write(f"**{sum(m.get('fat', 0) for m in day_meals)}g**")
        
        # Haftalık grafik
        st.divider()
        st.markdown("### 📈 Son 7 Gün")
        
        chart_data = []
        for i in range(6, -1, -1):
            d = (datetime.now() - timedelta(days=i)).strftime("%Y-%m-%d")
            d_meals = meals.get(d, [])
            total = sum(m.get("calories", 0) for m in d_meals)
            chart_data.append({"Tarih": d[-5:], "Kalori": total})
        
        df = pd.DataFrame(chart_data)
        st.bar_chart(df.set_index("Tarih"), color="#667eea")
    else:
        st.info(f"{date_key} için yemek girişi yok.")


# ═══════════════════════════════════════════════
#  TAB 3: VÜCUT ÖLÇÜLERİ
# ═══════════════════════════════════════════════
with tab3:
    st.markdown("### 📊 Vücut Ölçüleri")
    st.markdown("Kilo, yağ, kas ve su yüzdesini takip et.")
    
    body_data = load_body_metrics()
    profile = load_profile()
    
    col_form, col_results = st.columns([1, 1])
    
    with col_form:
        st.markdown("#### ➕ Yeni Ölçüm")
        
        measure_date = st.date_input("📅 Tarih", value=datetime.now(), max_value=datetime.now(), key="body_date")
        measure_key = measure_date.strftime("%Y-%m-%d")
        
        m_weight = st.number_input("⚖️ Kilo (kg)", value=float(profile.get("weight", 80)), min_value=30.0, max_value=300.0, step=0.1)
        m_fat = st.number_input("🔴 Yağ Oranı (%)", value=20.0, min_value=1.0, max_value=60.0, step=0.1)
        m_muscle = st.number_input("💪 Kas Oranı (%)", value=40.0, min_value=10.0, max_value=70.0, step=0.1)
        m_water = st.number_input("💧 Su Yüzdesi (%)", value=55.0, min_value=20.0, max_value=80.0, step=0.1)
        
        if st.button("📏 Ölçüm Kaydet", use_container_width=True, type="primary"):
            body_data[measure_key] = {
                "weight": m_weight,
                "fat": m_fat,
                "muscle": m_muscle,
                "water": m_water,
            }
            save_json(BODY_FILE, body_data)
            st.success(f"✅ {measure_key} ölçümü kaydedildi!")
            st.rerun()
    
    with col_results:
        st.markdown("#### 📈 Gelişim Analizi")
        
        if len(body_data) >= 1:
            sorted_dates = sorted(body_data.keys(), reverse=True)
            latest_date = sorted_dates[0]
            latest = body_data[latest_date]
            
            st.markdown(f"**Son Ölçüm:** {latest_date}")
            
            # Önceki ölçüm
            prev_data = None
            if len(sorted_dates) >= 2:
                prev_date = sorted_dates[1]
                prev_data = body_data[prev_date]
                
                st.markdown(f"##### Önceki ölçüme göre ({prev_date})")
                
                metrics = [
                    ("⚖️ Kilo", "weight", "kg", True),
                    ("🔴 Yağ", "fat", "%", True),
                    ("💪 Kas", "muscle", "%", False),
                    ("💧 Su", "water", "%", False),
                ]
                
                for label, key, unit, reverse in metrics:
                    curr = latest.get(key, 0)
                    prev = prev_data.get(key, 0)
                    
                    if prev > 0:
                        change = ((curr - prev) / prev) * 100
                    else:
                        change = 0
                    
                    if reverse:
                        is_good = change < 0
                    else:
                        is_good = change > 0
                    
                    if change == 0:
                        card_class = "progress-neutral"
                        arrow = "➡️"
                        status = "Değişim yok"
                        color = "#667eea"
                    elif is_good:
                        card_class = "progress-up"
                        arrow = "↗️" if change > 0 else "↘️"
                        status = "Gelişme ✓"
                        color = "#22c55e"
                    else:
                        card_class = "progress-down"
                        arrow = "↗️" if change > 0 else "↘️"
                        status = "Gerileme ✗"
                        color = "#ef4444"
                    
                    st.markdown(f"""
                    <div class="{card_class}">
                        <div style="display: flex; justify-content: space-between; align-items: center;">
                            <div>
                                <div style="color: #888; font-size: 0.75rem;">{label}</div>
                                <div style="color: #fff; font-size: 1.2rem; font-weight: 700;">{curr}{unit}</div>
                            </div>
                            <div style="text-align: right;">
                                <div style="color: {color}; font-size: 1.1rem; font-weight: 700;">{arrow} %{abs(round(change, 1))}</div>
                                <div style="color: {color}; font-size: 0.7rem;">{status}</div>
                            </div>
                        </div>
                    </div>
                    """, unsafe_allow_html=True)
            
            # Aylık karşılaştırma
            month_ago = (datetime.now() - timedelta(days=30)).strftime("%Y-%m-%d")
            month_data = None
            month_date = None
            
            for d in sorted(body_data.keys()):
                if d <= month_ago:
                    month_date = d
                    month_data = body_data[d]
            
            if month_data:
                st.markdown(f"##### Aylık karşılaştırma ({month_date})")
                
                for label, key, unit, reverse in metrics:
                    curr = latest.get(key, 0)
                    m_val = month_data.get(key, 0)
                    
                    if m_val > 0:
                        change = ((curr - m_val) / m_val) * 100
                    else:
                        change = 0
                    
                    if reverse:
                        is_good = change < 0
                    else:
                        is_good = change > 0
                    
                    if change == 0:
                        card_class = "progress-neutral"
                        status = "Değişim yok"
                        color = "#667eea"
                    elif is_good:
                        card_class = "progress-up"
                        status = "Gelişme ✓"
                        color = "#22c55e"
                    else:
                        card_class = "progress-down"
                        status = "Gerileme ✗"
                        color = "#ef4444"
                    
                    arrow = "↗️" if change > 0 else ("↘️" if change < 0 else "➡️")
                    
                    st.markdown(f"""
                    <div class="{card_class}">
                        <div style="display: flex; justify-content: space-between; align-items: center;">
                            <div>
                                <div style="color: #888; font-size: 0.75rem;">{label} (Aylık)</div>
                                <div style="color: #fff; font-size: 1.2rem; font-weight: 700;">{curr}{unit}</div>
                            </div>
                            <div style="text-align: right;">
                                <div style="color: {color}; font-size: 1.1rem; font-weight: 700;">{arrow} %{abs(round(change, 1))}</div>
                                <div style="color: {color}; font-size: 0.7rem;">{status}</div>
                            </div>
                        </div>
                    </div>
                    """, unsafe_allow_html=True)
        else:
            st.info("İlk ölçümünü ekle!")
    
    # Grafikler
    if len(body_data) >= 2:
        st.divider()
        st.markdown("### 📈 Trend Grafikleri")
        
        sorted_dates = sorted(body_data.keys())
        df = pd.DataFrame([
            {
                "Tarih": d,
                "Kilo": body_data[d].get("weight", 0),
                "Yağ %": body_data[d].get("fat", 0),
                "Kas %": body_data[d].get("muscle", 0),
            }
            for d in sorted_dates
        ])
        df = df.set_index("Tarih")
        
        c1, c2 = st.columns(2)
        with c1:
            st.markdown("**⚖️ Kilo Trendi**")
            st.line_chart(df[["Kilo"]], color="#667eea")
        with c2:
            st.markdown("**🔴 Yağ / 💪 Kas**")
            st.line_chart(df[["Yağ %", "Kas %"]])


# ═══════════════════════════════════════════════
#  TAB 4: DİYET PROGRAMI
# ═══════════════════════════════════════════════
with tab4:
    st.markdown("### 🤖 AI Diyet Asistanı")
    st.markdown("Gemini AI ile kişisel diyet programı oluştur.")
    
    profile = load_profile()
    
    # Hızlı program
    st.markdown("#### ⚡ Hızlı Diyet Programı")
    
    col_opts, col_gen = st.columns([1, 2])
    
    with col_opts:
        diet_type = st.selectbox("Diyet Tipi", [
            "Dengeli Beslenme",
            "Düşük Karbonhidrat", 
            "Yüksek Protein",
            "Akdeniz Diyeti",
            "Aralıklı Oruç (16:8)",
            "Vejetaryen",
        ])
        
        diet_duration = st.selectbox("Süre", ["1 Günlük", "3 Günlük", "1 Haftalık"])
        allergies = st.text_input("🚫 Alerji / Sevmediğin", placeholder="örn: süt, fıstık...")
        
        gen_btn = st.button("🤖 Program Oluştur", use_container_width=True, type="primary")
    
    with col_gen:
        if gen_btn:
            prompt = f"""Benim için kişiselleştirilmiş diyet programı oluştur.

Bilgilerim:
- İsim: {profile['name']}
- Boy: {profile['height']} cm, Kilo: {profile['weight']} kg, Yaş: {profile['age']}
- Cinsiyet: {profile['gender']}, Aktivite: {profile['activity']}, Hedef: {profile['goal']}
- Günlük kalori: {calculate_tdee(profile)} kcal, BMI: {get_bmi(profile)}

Diyet tipi: {diet_type}
Süre: {diet_duration}
Alerji/Sevmediğim: {allergies if allergies else 'Yok'}

Her öğün için:
1. Detaylı yemek listesi (kahvaltı, ara öğün, öğle, ara öğün, akşam)
2. Her yemeğin kalorisi
3. Günlük toplam makro (protein, karb, yağ)
4. Pratik tarifler
5. Market listesi

Türk mutfağına uygun öneriler yap."""

            with st.spinner("🤖 Program hazırlanıyor..."):
                result = ask_gemini(prompt, "Sen uzman diyetisyensin. Türk mutfağını biliyorsun. Sağlıklı programlar yapıyorsun.")
            
            st.session_state["diet_result"] = result
            save_json(DIET_FILE, {"date": get_today(), "type": diet_type, "plan": result})
        
        if "diet_result" in st.session_state:
            st.markdown(st.session_state["diet_result"])
    
    st.divider()
    
    # Soru-cevap modu
    st.markdown("#### 💬 Beslenme Soruları")
    
    question = st.text_input("Gemini'ye bir şey sor:", placeholder="örn: Akşam yemeğinde ne yesem?")
    
    if st.button("Sor", key="ask_diet"):
        if question:
            context = f"""Kullanıcı bilgileri:
- Boy: {profile['height']}cm, Kilo: {profile['weight']}kg, Yaş: {profile['age']}
- Hedef: {profile['goal']}, Günlük kalori: {calculate_tdee(profile)} kcal

Soru: {question}"""
            
            with st.spinner("Düşünüyorum..."):
                answer = ask_gemini(context, "Sen Türk beslenme uzmanısın. Kısa ve pratik cevaplar ver.")
            
            st.markdown(answer)
    
    # Kayıtlı plan
    saved = load_diet_plan()
    if saved and saved.get("plan"):
        with st.expander("📄 Son Kaydedilen Plan", expanded=False):
            st.markdown(f"**Tarih:** {saved.get('date')} | **Tip:** {saved.get('type')}")
            st.markdown(saved["plan"])


# ═══════════════════════════════════════════════
#  TAB 5: SU TAKİBİ
# ═══════════════════════════════════════════════
with tab5:
    st.markdown("### 💧 Su Takibi")
    st.markdown("Günlük 2.5 litre su hedefi!")
    
    today = get_today()
    water_data = load_water()
    
    if today not in water_data:
        water_data[today] = 0
    
    current = water_data[today]
    target = 2500
    pct = min(100, round((current / target) * 100))
    remaining = max(0, target - current)
    
    col_display, col_add = st.columns([1, 1])
    
    with col_display:
        st.markdown(f"""
        <div class="welcome-card">
            <div style="font-size: 3rem;">💧</div>
            <div class="calorie-display" style="color: #38bdf8;">{current} ml</div>
            <div style="color: #888;">/ {target} ml hedef</div>
            <div style="margin-top: 15px;">
                <div style="background: rgba(255,255,255,0.1); border-radius: 10px; height: 10px;">
                    <div style="width: {pct}%; height: 100%; background: linear-gradient(90deg, #38bdf8, #667eea); border-radius: 10px;"></div>
                </div>
                <div style="color: #38bdf8; margin-top: 8px;">%{pct} — {remaining} ml kaldı</div>
            </div>
        </div>
        """, unsafe_allow_html=True)
    
    with col_add:
        st.markdown("#### Hızlı Ekle")
        
        amounts = [
            ("🥛 Bardak (200ml)", 200),
            ("🍶 Küçük Şişe (330ml)", 330),
            ("🧴 Büyük Şişe (500ml)", 500),
            ("☕ Çay/Kahve (150ml)", 150),
        ]
        
        for label, amount in amounts:
            if st.button(label, use_container_width=True, key=f"w_{amount}"):
                water_data[today] = water_data.get(today, 0) + amount
                save_json(WATER_FILE, water_data)
                st.rerun()
        
        st.divider()
        
        custom = st.number_input("Özel (ml)", min_value=50, max_value=2000, value=250, step=50)
        if st.button("➕ Ekle", use_container_width=True):
            water_data[today] = water_data.get(today, 0) + custom
            save_json(WATER_FILE, water_data)
            st.rerun()
        
        if st.button("🔄 Sıfırla", use_container_width=True):
            water_data[today] = 0
            save_json(WATER_FILE, water_data)
            st.rerun()
    
    # Haftalık grafik
    st.divider()
    st.markdown("### 📈 Son 7 Gün")
    
    chart = []
    for i in range(6, -1, -1):
        d = (datetime.now() - timedelta(days=i)).strftime("%Y-%m-%d")
        chart.append({"Tarih": d[-5:], "Su (ml)": water_data.get(d, 0)})
    
    df = pd.DataFrame(chart)
    st.bar_chart(df.set_index("Tarih"), color="#38bdf8")


# ──────────────────────────────────────────────
#  Footer
# ──────────────────────────────────────────────
st.divider()
st.caption("🌿 Luvén v1.0 — Powered by Gemini AI | Kişisel kullanım için")
