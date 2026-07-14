import streamlit as st
import google.generativeai as genai
import pandas as pd
import json
import os
from datetime import datetime, timedelta
from pathlib import Path

# ──────────────────────────────────────────────
#  Luvén — Kişisel Diyet & Kalori Takip Uygulaması
# ──────────────────────────────────────────────

# ---------- sayfa ayarı ----------
st.set_page_config(
    page_title="Luvén",
    page_icon="🌿",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ---------- özel CSS ----------
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700;800;900&display=swap');

    /* Global */
    .stApp {
        font-family: 'Inter', sans-serif;
    }

    /* Sidebar */
    section[data-testid="stSidebar"] {
        background: linear-gradient(180deg, #0f0f0f 0%, #1a1a2e 100%);
    }
    section[data-testid="stSidebar"] .stMarkdown p,
    section[data-testid="stSidebar"] .stMarkdown h1,
    section[data-testid="stSidebar"] .stMarkdown h2,
    section[data-testid="stSidebar"] .stMarkdown h3 {
        color: #e0e0e0;
    }

    /* Başlık */
    .luven-title {
        font-size: 3rem;
        font-weight: 900;
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        text-align: center;
        margin-bottom: 0;
        letter-spacing: -1px;
    }
    .luven-subtitle {
        text-align: center;
        color: #888;
        font-size: 0.95rem;
        margin-top: -8px;
        margin-bottom: 30px;
        letter-spacing: 2px;
    }

    /* Metrik kartları */
    .metric-card {
        background: linear-gradient(135deg, #1a1a2e 0%, #16213e 100%);
        border: 1px solid rgba(102, 126, 234, 0.2);
        border-radius: 20px;
        padding: 28px;
        text-align: center;
        transition: all 0.3s ease;
        box-shadow: 0 8px 32px rgba(0,0,0,0.15);
    }
    .metric-card:hover {
        transform: translateY(-4px);
        box-shadow: 0 12px 40px rgba(102,126,234,0.2);
        border-color: rgba(102, 126, 234, 0.5);
    }
    .metric-value {
        font-size: 2.8rem;
        font-weight: 800;
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        margin: 8px 0;
    }
    .metric-label {
        font-size: 0.85rem;
        color: #999;
        text-transform: uppercase;
        letter-spacing: 2px;
        font-weight: 600;
    }
    .metric-sub {
        font-size: 0.8rem;
        color: #667eea;
        margin-top: 6px;
        font-weight: 500;
    }

    /* Hoşgeldin kartı */
    .welcome-card {
        background: linear-gradient(135deg, #0f0f23 0%, #1a1a2e 50%, #16213e 100%);
        border: 1px solid rgba(102,126,234,0.3);
        border-radius: 24px;
        padding: 40px;
        text-align: center;
        box-shadow: 0 20px 60px rgba(0,0,0,0.3);
        position: relative;
        overflow: hidden;
    }
    .welcome-card::before {
        content: '';
        position: absolute;
        top: 0; left: 0; right: 0;
        height: 3px;
        background: linear-gradient(90deg, #667eea, #764ba2, #f093fb);
    }
    .welcome-name {
        font-size: 2.4rem;
        font-weight: 800;
        color: #fff;
        margin-bottom: 4px;
    }
    .welcome-greeting {
        font-size: 1.1rem;
        color: #aaa;
        margin-bottom: 20px;
    }

    /* Kalori çemberi */
    .calorie-ring {
        width: 200px;
        height: 200px;
        border-radius: 50%;
        margin: 0 auto 20px;
        display: flex;
        align-items: center;
        justify-content: center;
        flex-direction: column;
        position: relative;
    }
    .calorie-ring-value {
        font-size: 2.6rem;
        font-weight: 900;
        color: #fff;
    }
    .calorie-ring-label {
        font-size: 0.75rem;
        color: #aaa;
        text-transform: uppercase;
        letter-spacing: 2px;
    }

    /* Progress bar */
    .progress-container {
        background: rgba(255,255,255,0.05);
        border-radius: 12px;
        height: 14px;
        overflow: hidden;
        margin: 12px 0;
    }
    .progress-fill {
        height: 100%;
        border-radius: 12px;
        transition: width 0.6s ease;
    }

    /* Yemek kartı */
    .food-item {
        background: rgba(255,255,255,0.03);
        border: 1px solid rgba(255,255,255,0.08);
        border-radius: 14px;
        padding: 16px 20px;
        margin: 8px 0;
        display: flex;
        justify-content: space-between;
        align-items: center;
    }
    .food-name {
        font-weight: 600;
        color: #e0e0e0;
        font-size: 1rem;
    }
    .food-cal {
        color: #667eea;
        font-weight: 700;
        font-size: 1.1rem;
    }

    /* Gelişim kartları */
    .progress-card-up {
        background: linear-gradient(135deg, #0a2e1a 0%, #0f3d22 100%);
        border: 1px solid rgba(34,197,94,0.3);
        border-radius: 18px;
        padding: 24px;
        text-align: center;
    }
    .progress-card-down {
        background: linear-gradient(135deg, #2e0a0a 0%, #3d0f0f 100%);
        border: 1px solid rgba(239,68,68,0.3);
        border-radius: 18px;
        padding: 24px;
        text-align: center;
    }
    .progress-card-neutral {
        background: linear-gradient(135deg, #1a1a2e 0%, #16213e 100%);
        border: 1px solid rgba(102,126,234,0.2);
        border-radius: 18px;
        padding: 24px;
        text-align: center;
    }

    /* Chat */
    .chat-msg-user {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        border-radius: 18px 18px 4px 18px;
        padding: 14px 20px;
        margin: 8px 0;
        color: #fff;
        font-size: 0.95rem;
        max-width: 80%;
        margin-left: auto;
    }
    .chat-msg-ai {
        background: rgba(255,255,255,0.05);
        border: 1px solid rgba(255,255,255,0.08);
        border-radius: 18px 18px 18px 4px;
        padding: 14px 20px;
        margin: 8px 0;
        color: #e0e0e0;
        font-size: 0.95rem;
        max-width: 80%;
    }

    /* Tab styling */
    .stTabs [data-baseweb="tab-list"] {
        gap: 8px;
        justify-content: center;
    }
    .stTabs [data-baseweb="tab"] {
        border-radius: 12px;
        padding: 10px 24px;
        font-weight: 600;
    }

    /* Genel düzeltmeler */
    div[data-testid="stMetric"] {
        background: rgba(255,255,255,0.03);
        border: 1px solid rgba(255,255,255,0.08);
        border-radius: 14px;
        padding: 16px;
    }

    /* Su takibi */
    .water-glass {
        font-size: 2rem;
        cursor: pointer;
        transition: transform 0.2s;
    }
    .water-glass:hover {
        transform: scale(1.2);
    }

    /* Hide streamlit branding */
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    header {visibility: hidden;}
</style>
""", unsafe_allow_html=True)


# ──────────────────────────────────────────────
#  Veri yönetimi (JSON tabanlı, hafif)
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
    if path.exists():
        with open(path, "r", encoding="utf-8") as f:
            return json.load(f)
    return default


def save_json(path, data):
    with open(path, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2, default=str)


def load_profile():
    return load_json(PROFILE_FILE, {
        "name": "Murat",
        "height": 178,
        "weight": 80,
        "age": 28,
        "gender": "Erkek",
        "activity": "Orta Düzey",
        "goal": "Kilo Verme",
        "daily_calorie_target": 2200,
    })


def load_meals():
    return load_json(MEALS_FILE, {})


def load_body_metrics():
    return load_json(BODY_FILE, {})


def load_water():
    return load_json(WATER_FILE, {})


def load_diet_plan():
    return load_json(DIET_FILE, {})


# ---------- Kalori hesaplama ----------
def calculate_bmr(profile):
    """Mifflin-St Jeor denklemi ile BMR hesapla."""
    w = profile.get("weight", 80)
    h = profile.get("height", 178)
    a = profile.get("age", 28)
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
    h_m = profile.get("height", 178) / 100
    w = profile.get("weight", 80)
    return round(w / (h_m ** 2), 1)


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
    api_key = st.session_state.get("gemini_api_key", "")
    if not api_key:
        return None
    try:
        genai.configure(api_key=api_key)
        model = genai.GenerativeModel("gemini-2.0-flash")
        return model
    except Exception:
        return None


def ask_gemini(prompt, system_instruction=""):
    model = get_gemini_model()
    if not model:
        return "⚠️ Gemini API anahtarı gerekli. Lütfen sol menüden API anahtarınızı girin."
    try:
        full_prompt = f"{system_instruction}\n\n{prompt}" if system_instruction else prompt
        response = model.generate_content(full_prompt)
        return response.text
    except Exception as e:
        return f"❌ Hata: {str(e)}"


def estimate_calories(food_text):
    """Gemini ile yemek kalori tahmini yap."""
    prompt = f"""Aşağıdaki yemek/yiyecek için tahmini kalori değerini hesapla.
Sadece JSON formatında yanıt ver, başka hiçbir şey yazma.
Format: {{"food": "yemek adı", "calories": sayı, "protein": sayı, "carbs": sayı, "fat": sayı, "portion": "porsiyon bilgisi"}}

Yemek: {food_text}"""

    result = ask_gemini(prompt, "Sen bir beslenme uzmanısın. Türk mutfağını çok iyi biliyorsun. Kalori değerlerini ortalama porsiyon boyutuna göre hesapla. Yanıtını kesinlikle sadece JSON formatında ver.")

    try:
        clean = result.strip()
        if clean.startswith("```"):
            clean = clean.split("\n", 1)[1] if "\n" in clean else clean[3:]
            if clean.endswith("```"):
                clean = clean[:-3]
            clean = clean.strip()
            if clean.startswith("json"):
                clean = clean[4:].strip()
        return json.loads(clean)
    except (json.JSONDecodeError, Exception):
        return {"food": food_text, "calories": 0, "protein": 0, "carbs": 0, "fat": 0, "portion": "Bilinmiyor"}


# ──────────────────────────────────────────────
#  Sidebar
# ──────────────────────────────────────────────
with st.sidebar:
    st.markdown('<p class="luven-title" style="font-size:2rem;">🌿 Luvén</p>', unsafe_allow_html=True)
    st.markdown('<p class="luven-subtitle" style="font-size:0.75rem;">KİŞİSEL DİYET ASİSTANI</p>', unsafe_allow_html=True)

    st.divider()

    # Gemini API Key
    api_key = st.text_input("🔑 Gemini API Anahtarı", type="password", help="Google AI Studio'dan alabilirsiniz")
    if api_key:
        st.session_state["gemini_api_key"] = api_key
        st.success("✓ API bağlandı", icon="✅")

    st.divider()

    # Profil ayarları
    st.markdown("### ⚙️ Profil Ayarları")

    profile = load_profile()

    with st.expander("Profili Düzenle", expanded=False):
        name = st.text_input("İsim", value=profile.get("name", "Murat"))
        height = st.number_input("Boy (cm)", value=profile.get("height", 178), min_value=100, max_value=250)
        weight = st.number_input("Kilo (kg)", value=float(profile.get("weight", 80)), min_value=30.0, max_value=300.0, step=0.1)
        age = st.number_input("Yaş", value=profile.get("age", 28), min_value=10, max_value=100)
        gender = st.selectbox("Cinsiyet", ["Erkek", "Kadın"], index=0 if profile.get("gender", "Erkek") == "Erkek" else 1)
        activity = st.selectbox("Aktivite Seviyesi", ["Hareketsiz", "Az Hareketli", "Orta Düzey", "Aktif", "Çok Aktif"],
                                index=["Hareketsiz", "Az Hareketli", "Orta Düzey", "Aktif", "Çok Aktif"].index(
                                    profile.get("activity", "Orta Düzey")))
        goal = st.selectbox("Hedef", ["Kilo Verme", "Kilo Koruma", "Kas Yapma"],
                            index=["Kilo Verme", "Kilo Koruma", "Kas Yapma"].index(profile.get("goal", "Kilo Verme")))

        if st.button("💾 Kaydet", use_container_width=True):
            profile = {
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
            save_json(PROFILE_FILE, profile)
            st.success("Profil kaydedildi!")
            st.rerun()

    # Bilgiler
    profile = load_profile()
    profile["daily_calorie_target"] = calculate_tdee(profile)
    bmi = get_bmi(profile)
    bmi_cat, bmi_icon = get_bmi_category(bmi)

    st.markdown(f"""
    **{profile['name']}** | {profile['height']}cm | {profile['weight']}kg
    BMI: **{bmi}** {bmi_icon} {bmi_cat}
    Günlük Hedef: **{profile['daily_calorie_target']} kcal**
    """)

    st.divider()
    st.markdown("""
    <div style="text-align:center; color:#555; font-size:0.7rem; margin-top:20px;">
        Luvén v1.0 — Powered by Gemini AI<br>
        Kişisel kullanım için tasarlandı
    </div>
    """, unsafe_allow_html=True)


# ──────────────────────────────────────────────
#  Ana Sayfa
# ──────────────────────────────────────────────
st.markdown('<p class="luven-title">Luvén</p>', unsafe_allow_html=True)
st.markdown('<p class="luven-subtitle">KİŞİSEL DİYET & KALORİ TAKİP</p>', unsafe_allow_html=True)

tab1, tab2, tab3, tab4, tab5 = st.tabs([
    "🏠 Ana Sayfa",
    "🍽️ Yemek Takibi",
    "📊 Vücut Ölçüleri",
    "🤖 Diyet Programı",
    "💧 Su Takibi"
])

# ──────────────────────────────────────────────
#  TAB 1: ANA SAYFA
# ──────────────────────────────────────────────
with tab1:
    profile = load_profile()
    profile["daily_calorie_target"] = calculate_tdee(profile)
    today = get_today()
    meals = load_meals()
    today_meals = meals.get(today, [])
    total_cal_today = sum(m.get("calories", 0) for m in today_meals)
    target = profile["daily_calorie_target"]
    remaining = max(0, target - total_cal_today)
    pct = min(100, round((total_cal_today / target) * 100)) if target > 0 else 0

    total_protein = sum(m.get("protein", 0) for m in today_meals)
    total_carbs = sum(m.get("carbs", 0) for m in today_meals)
    total_fat = sum(m.get("fat", 0) for m in today_meals)

    # Hoşgeldin kartı
    greeting_time = "Günaydın" if datetime.now().hour < 12 else ("İyi Günler" if datetime.now().hour < 18 else "İyi Akşamlar")

    if remaining > 0:
        calorie_msg = f"🟢 {remaining} Kalori Daha Alabilirsin"
        ring_color = "linear-gradient(135deg, #667eea 0%, #764ba2 100%)"
    else:
        calorie_msg = f"🔴 Günlük Kalori Limitini Aştın! (+{abs(target - total_cal_today)} kcal)"
        ring_color = "linear-gradient(135deg, #ef4444 0%, #dc2626 100%)"

    # Progress bar rengi
    if pct < 70:
        bar_color = "linear-gradient(90deg, #667eea, #764ba2)"
    elif pct < 100:
        bar_color = "linear-gradient(90deg, #f59e0b, #ef4444)"
    else:
        bar_color = "linear-gradient(90deg, #ef4444, #dc2626)"

    st.markdown(f"""
    <div class="welcome-card">
        <div class="welcome-greeting">{greeting_time}</div>
        <div class="welcome-name">Hoşgeldin {profile['name']}! 👋</div>
        <div style="margin: 30px auto; max-width: 400px;">
            <div class="calorie-ring" style="background: {ring_color}; box-shadow: 0 0 40px rgba(102,126,234,0.3);">
                <div class="calorie-ring-value">{remaining}</div>
                <div class="calorie-ring-label">kalan kcal</div>
            </div>
            <div style="font-size: 1.3rem; color: {'#22c55e' if remaining > 0 else '#ef4444'}; font-weight: 700; margin-bottom: 16px;">
                {calorie_msg}
            </div>
            <div style="display:flex; justify-content:space-between; color:#888; font-size:0.85rem; margin-bottom:4px;">
                <span>Alınan: {total_cal_today} kcal</span>
                <span>Hedef: {target} kcal</span>
            </div>
            <div class="progress-container">
                <div class="progress-fill" style="width: {pct}%; background: {bar_color};"></div>
            </div>
            <div style="color:#667eea; font-size:0.85rem; margin-top:8px;">%{pct} tamamlandı</div>
        </div>
    </div>
    """, unsafe_allow_html=True)

    st.markdown("<br>", unsafe_allow_html=True)

    # Makro kartları
    col1, col2, col3, col4 = st.columns(4)

    with col1:
        st.markdown(f"""
        <div class="metric-card">
            <div class="metric-label">🔥 Kalori</div>
            <div class="metric-value">{total_cal_today}</div>
            <div class="metric-sub">/ {target} kcal</div>
        </div>
        """, unsafe_allow_html=True)

    with col2:
        st.markdown(f"""
        <div class="metric-card">
            <div class="metric-label">🥩 Protein</div>
            <div class="metric-value">{total_protein}g</div>
            <div class="metric-sub">Hedef: ~{round(profile['weight'] * 1.6)}g</div>
        </div>
        """, unsafe_allow_html=True)

    with col3:
        st.markdown(f"""
        <div class="metric-card">
            <div class="metric-label">🍞 Karbonhidrat</div>
            <div class="metric-value">{total_carbs}g</div>
            <div class="metric-sub">Makro dağılım</div>
        </div>
        """, unsafe_allow_html=True)

    with col4:
        st.markdown(f"""
        <div class="metric-card">
            <div class="metric-label">🧈 Yağ</div>
            <div class="metric-value">{total_fat}g</div>
            <div class="metric-sub">Makro dağılım</div>
        </div>
        """, unsafe_allow_html=True)

    st.markdown("<br>", unsafe_allow_html=True)

    # Bugünün yemekleri özet
    if today_meals:
        st.markdown("### 📋 Bugün Yediklerin")
        for meal in today_meals:
            st.markdown(f"""
            <div class="food-item">
                <div>
                    <span class="food-name">{meal.get('food', 'Bilinmiyor')}</span>
                    <span style="color:#666; font-size:0.8rem; margin-left:8px;">{meal.get('portion', '')}</span>
                </div>
                <span class="food-cal">{meal.get('calories', 0)} kcal</span>
            </div>
            """, unsafe_allow_html=True)
    else:
        st.info("Henüz bugün yemek girişi yapılmadı. 🍽️ sekmesinden yemek ekleyebilirsin.")


# ──────────────────────────────────────────────
#  TAB 2: YEMEK TAKİBİ
# ──────────────────────────────────────────────
with tab2:
    st.markdown("### 🍽️ Yemek Takibi")
    st.markdown("Yediğin yemeği yaz, Gemini AI kalori ve besin değerlerini hesaplasın.")

    today = get_today()
    meals = load_meals()

    # Tarih seçici
    selected_date = st.date_input("📅 Tarih", value=datetime.now(), max_value=datetime.now())
    date_key = selected_date.strftime("%Y-%m-%d")

    col_input, col_info = st.columns([2, 1])

    with col_input:
        food_input = st.text_input("🍕 Yemek gir (örn: 1 porsiyon karnıyarık, 1 bardak ayran)",
                                   placeholder="Ne yedin?")

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
                    st.warning("Kalori hesaplanamadı. Lütfen yemeği daha detaylı yazın veya API anahtarını kontrol edin.")
            else:
                st.warning("Lütfen bir yemek girin.")

    with col_info:
        day_meals = meals.get(date_key, [])
        day_total = sum(m.get("calories", 0) for m in day_meals)
        st.markdown(f"""
        <div class="metric-card">
            <div class="metric-label">📅 {date_key}</div>
            <div class="metric-value">{day_total}</div>
            <div class="metric-sub">Toplam kcal</div>
        </div>
        """, unsafe_allow_html=True)

    st.divider()

    # Bugünün yemek listesi
    day_meals = meals.get(date_key, [])
    if day_meals:
        st.markdown(f"### 📋 {date_key} Yemek Listesi")

        for i, meal in enumerate(day_meals):
            c1, c2, c3, c4, c5, c6 = st.columns([3, 1, 1, 1, 1, 1])
            with c1:
                st.markdown(f"**{meal.get('food', '?')}** <span style='color:#888'>({meal.get('portion', '')})</span>",
                            unsafe_allow_html=True)
            with c2:
                st.metric("Kalori", f"{meal.get('calories', 0)}")
            with c3:
                st.metric("Protein", f"{meal.get('protein', 0)}g")
            with c4:
                st.metric("Karb.", f"{meal.get('carbs', 0)}g")
            with c5:
                st.metric("Yağ", f"{meal.get('fat', 0)}g")
            with c6:
                if st.button("🗑️", key=f"del_{date_key}_{i}"):
                    meals[date_key].pop(i)
                    save_json(MEALS_FILE, meals)
                    st.rerun()

        # Toplam satırı
        st.divider()
        tc1, tc2, tc3, tc4, tc5 = st.columns([3, 1, 1, 1, 1])
        with tc1:
            st.markdown("**TOPLAM**")
        with tc2:
            st.metric("Kalori", sum(m.get("calories", 0) for m in day_meals))
        with tc3:
            st.metric("Protein", f"{sum(m.get('protein', 0) for m in day_meals)}g")
        with tc4:
            st.metric("Karb.", f"{sum(m.get('carbs', 0) for m in day_meals)}g")
        with tc5:
            st.metric("Yağ", f"{sum(m.get('fat', 0) for m in day_meals)}g")

        # Haftalık grafik
        st.divider()
        st.markdown("### 📈 Son 7 Gün Kalori Grafiği")

        chart_data = []
        for i in range(6, -1, -1):
            d = (datetime.now() - timedelta(days=i)).strftime("%Y-%m-%d")
            d_meals = meals.get(d, [])
            total = sum(m.get("calories", 0) for m in d_meals)
            chart_data.append({"Tarih": d, "Kalori": total})

        df_chart = pd.DataFrame(chart_data)
        df_chart = df_chart.set_index("Tarih")
        st.bar_chart(df_chart, color="#667eea")
    else:
        st.info(f"{date_key} tarihinde henüz yemek girişi yok.")


# ──────────────────────────────────────────────
#  TAB 3: VÜCUT ÖLÇÜLERİ
# ──────────────────────────────────────────────
with tab3:
    st.markdown("### 📊 Vücut Ölçüleri Takibi")
    st.markdown("Kilo, yağ oranı, kas oranı ve su yüzdesini girerek gelişimini takip et.")

    body_data = load_body_metrics()
    today = get_today()

    col_form, col_display = st.columns([1, 1])

    with col_form:
        st.markdown("#### ➕ Yeni Ölçüm Ekle")

        measure_date = st.date_input("📅 Ölçüm Tarihi", value=datetime.now(), max_value=datetime.now(),
                                     key="body_date")
        measure_date_key = measure_date.strftime("%Y-%m-%d")

        m_weight = st.number_input("⚖️ Kilo (kg)", value=float(profile.get("weight", 80)),
                                   min_value=30.0, max_value=300.0, step=0.1)
        m_fat = st.number_input("🔴 Yağ Oranı (%)", value=20.0, min_value=1.0, max_value=60.0, step=0.1)
        m_muscle = st.number_input("💪 Kas Oranı (%)", value=40.0, min_value=10.0, max_value=70.0, step=0.1)
        m_water = st.number_input("💧 Su Yüzdesi (%)", value=55.0, min_value=20.0, max_value=80.0, step=0.1)

        if st.button("📏 Ölçüm Kaydet", use_container_width=True, type="primary"):
            body_data[measure_date_key] = {
                "weight": m_weight,
                "fat": m_fat,
                "muscle": m_muscle,
                "water": m_water,
            }
            save_json(BODY_FILE, body_data)
            st.success(f"✅ {measure_date_key} ölçümü kaydedildi!")
            st.rerun()

    with col_display:
        st.markdown("#### 📈 Gelişim Durumu")

        if len(body_data) >= 1:
            # Bugüne en yakın ölçüm
            sorted_dates = sorted(body_data.keys(), reverse=True)
            latest_date = sorted_dates[0]
            latest = body_data[latest_date]

            # Dün veya bir önceki ölçüm
            prev_data = None
            prev_date = None
            if len(sorted_dates) >= 2:
                prev_date = sorted_dates[1]
                prev_data = body_data[prev_date]

            # Ay önceki ölçüm
            month_ago = (datetime.now() - timedelta(days=30)).strftime("%Y-%m-%d")
            month_data = None
            month_date = None
            for d in sorted(body_data.keys()):
                if d <= month_ago:
                    month_date = d
                    month_data = body_data[d]

            def calc_change(current, previous, label, reverse=False):
                """Değişim yüzdesini hesapla. reverse=True ise düşüş iyi."""
                if previous is None or previous == 0:
                    return 0, "neutral"
                change = ((current - previous) / previous) * 100
                if reverse:
                    direction = "up" if change < 0 else ("down" if change > 0 else "neutral")
                else:
                    direction = "up" if change > 0 else ("down" if change < 0 else "neutral")
                return round(change, 1), direction

            # Önceki ölçüme göre karşılaştırma
            st.markdown(f"**Son Ölçüm:** {latest_date}")

            metrics = [
                ("⚖️ Kilo", "weight", "kg", True),
                ("🔴 Yağ", "fat", "%", True),
                ("💪 Kas", "muscle", "%", False),
                ("💧 Su", "water", "%", False),
            ]

            if prev_data:
                st.markdown(f"###### Önceki ölçüme göre ({prev_date})")
                for label, key, unit, reverse in metrics:
                    current_val = latest.get(key, 0)
                    prev_val = prev_data.get(key, 0)
                    change, direction = calc_change(current_val, prev_val, label, reverse)

                    card_class = "progress-card-up" if direction == "up" else (
                        "progress-card-down" if direction == "down" else "progress-card-neutral")

                    arrow = "↗️" if change > 0 else ("↘️" if change < 0 else "➡️")
                    color = "#22c55e" if direction == "up" else ("#ef4444" if direction == "down" else "#667eea")
                    good_bad = "Gelişme ✓" if direction == "up" else ("Gerileme ✗" if direction == "down" else "Değişim yok")

                    st.markdown(f"""
                    <div class="{card_class}" style="margin-bottom:8px;">
                        <div style="display:flex; justify-content:space-between; align-items:center;">
                            <div style="text-align:left;">
                                <div style="color:#aaa; font-size:0.8rem;">{label}</div>
                                <div style="color:#fff; font-size:1.4rem; font-weight:700;">{current_val}{unit}</div>
                            </div>
                            <div style="text-align:right;">
                                <div style="color:{color}; font-size:1.3rem; font-weight:700;">{arrow} %{abs(change)}</div>
                                <div style="color:{color}; font-size:0.75rem;">{good_bad}</div>
                            </div>
                        </div>
                    </div>
                    """, unsafe_allow_html=True)

            if month_data:
                st.markdown(f"###### Aylık karşılaştırma ({month_date})")
                for label, key, unit, reverse in metrics:
                    current_val = latest.get(key, 0)
                    m_val = month_data.get(key, 0)
                    change, direction = calc_change(current_val, m_val, label, reverse)

                    card_class = "progress-card-up" if direction == "up" else (
                        "progress-card-down" if direction == "down" else "progress-card-neutral")
                    arrow = "↗️" if change > 0 else ("↘️" if change < 0 else "➡️")
                    color = "#22c55e" if direction == "up" else ("#ef4444" if direction == "down" else "#667eea")
                    good_bad = "Gelişme ✓" if direction == "up" else ("Gerileme ✗" if direction == "down" else "Değişim yok")

                    st.markdown(f"""
                    <div class="{card_class}" style="margin-bottom:8px;">
                        <div style="display:flex; justify-content:space-between; align-items:center;">
                            <div style="text-align:left;">
                                <div style="color:#aaa; font-size:0.8rem;">{label} (Aylık)</div>
                                <div style="color:#fff; font-size:1.4rem; font-weight:700;">{current_val}{unit}</div>
                            </div>
                            <div style="text-align:right;">
                                <div style="color:{color}; font-size:1.3rem; font-weight:700;">{arrow} %{abs(change)}</div>
                                <div style="color:{color}; font-size:0.75rem;">{good_bad}</div>
                            </div>
                        </div>
                    </div>
                    """, unsafe_allow_html=True)

            if not prev_data and not month_data:
                st.info("Karşılaştırma için en az 2 ölçüm gerekli.")

        else:
            st.info("Henüz ölçüm girişi yapılmadı. Sol taraftan ilk ölçümünü ekle!")

    # Grafik
    if len(body_data) >= 2:
        st.divider()
        st.markdown("### 📈 Trend Grafikleri")

        sorted_dates = sorted(body_data.keys())
        df_body = pd.DataFrame([
            {
                "Tarih": d,
                "Kilo (kg)": body_data[d].get("weight", 0),
                "Yağ (%)": body_data[d].get("fat", 0),
                "Kas (%)": body_data[d].get("muscle", 0),
                "Su (%)": body_data[d].get("water", 0),
            }
            for d in sorted_dates
        ])
        df_body = df_body.set_index("Tarih")

        chart_col1, chart_col2 = st.columns(2)
        with chart_col1:
            st.markdown("**⚖️ Kilo Trendi**")
            st.line_chart(df_body[["Kilo (kg)"]], color="#667eea")
        with chart_col2:
            st.markdown("**🔴 Yağ / 💪 Kas Trendi**")
            st.line_chart(df_body[["Yağ (%)", "Kas (%)"]], color=["#ef4444", "#22c55e"])

    # Tüm ölçümler tablosu
    if body_data:
        st.divider()
        with st.expander("📋 Tüm Ölçümler", expanded=False):
            sorted_dates = sorted(body_data.keys(), reverse=True)
            table_data = []
            for d in sorted_dates:
                entry = body_data[d]
                table_data.append({
                    "Tarih": d,
                    "Kilo (kg)": entry.get("weight", 0),
                    "Yağ (%)": entry.get("fat", 0),
                    "Kas (%)": entry.get("muscle", 0),
                    "Su (%)": entry.get("water", 0),
                })
            st.dataframe(pd.DataFrame(table_data), use_container_width=True, hide_index=True)

            if st.button("🗑️ Tüm Ölçümleri Sil", type="secondary"):
                save_json(BODY_FILE, {})
                st.rerun()


# ──────────────────────────────────────────────
#  TAB 4: DİYET PROGRAMI (Gemini AI)
# ──────────────────────────────────────────────
with tab4:
    st.markdown("### 🤖 AI Diyet Asistanı")
    st.markdown("Gemini AI sana özel sorular sorarak kişiselleştirilmiş diyet programı oluşturur.")

    if "diet_chat" not in st.session_state:
        st.session_state.diet_chat = []

    if "diet_step" not in st.session_state:
        st.session_state.diet_step = 0

    if "diet_answers" not in st.session_state:
        st.session_state.diet_answers = {}

    # Hızlı diyet oluştur
    col_quick, col_chat = st.columns([1, 1])

    with col_quick:
        st.markdown("#### ⚡ Hızlı Diyet Programı")
        st.markdown("Profilindeki bilgiler kullanılarak anında diyet programı oluşturulur.")

        diet_type = st.selectbox("Diyet Tipi", [
            "Dengeli Beslenme",
            "Düşük Karbonhidrat",
            "Yüksek Protein",
            "Akdeniz Diyeti",
            "Aralıklı Oruç (16:8)",
            "Vejeteryan",
        ])

        diet_duration = st.selectbox("Süre", ["1 Günlük", "3 Günlük", "1 Haftalık"])

        allergies = st.text_input("🚫 Alerjiler / Sevmediğin Yiyecekler", placeholder="örn: süt ürünleri, fıstık...")

        if st.button("🤖 Diyet Programı Oluştur", use_container_width=True, type="primary"):
            profile = load_profile()
            prompt = f"""Benim için kişiselleştirilmiş bir diyet programı oluştur.

Bilgilerim:
- İsim: {profile['name']}
- Boy: {profile['height']} cm
- Kilo: {profile['weight']} kg
- Yaş: {profile['age']}
- Cinsiyet: {profile['gender']}
- Aktivite: {profile['activity']}
- Hedef: {profile['goal']}
- Günlük kalori hedefi: {calculate_tdee(profile)} kcal
- BMI: {get_bmi(profile)}

Diyet tipi: {diet_type}
Süre: {diet_duration}
Alerjiler/Sevmediğim yiyecekler: {allergies if allergies else 'Yok'}

Lütfen:
1. Her öğün için detaylı yemek listesi ver (kahvaltı, ara öğün, öğle, ara öğün, akşam)
2. Her yemeğin yaklaşık kalorisi
3. Günlük toplam makro değerleri (protein, karb, yağ)
4. Pratik tarifler veya hazırlık ipuçları
5. Market alışveriş listesi

Türk mutfağına uygun öneriler yap. Programı güzel ve okunaklı formatla."""

            with st.spinner("🤖 Gemini diyet programını hazırlıyor..."):
                result = ask_gemini(prompt, "Sen uzman bir diyetisyensin. Türk mutfağını çok iyi biliyorsun. Sağlıklı ve uygulanabilir programlar oluşturuyorsun.")

            st.session_state.generated_diet = result
            diet_plan = {"date": today, "type": diet_type, "plan": result}
            save_json(DIET_FILE, diet_plan)

        if "generated_diet" in st.session_state:
            st.markdown("---")
            st.markdown(st.session_state.generated_diet)

    with col_chat:
        st.markdown("#### 💬 Soru-Cevap ile Özel Program")
        st.markdown("Sorulara yanıt vererek sana en uygun programı oluşturalım.")

        # Diyet asistanı soruları
        diet_questions = [
            "Günde kaç öğün yemek yemeyi tercih ediyorsun? (3 ana + 2 ara öğün vs)",
            "Sağlık problemlerin var mı? (diyabet, tansiyon, kolesterol vb.)",
            "Hangi yemekleri çok seviyorsun? (favorilerin)",
            "Yemek pişirmeye günde ne kadar zaman ayırabilirsin?",
            "Dışarıda yemek yeme sıklığın nedir? (her gün, haftada 2-3 vs)",
            "Herhangi bir supplement/takviye kullanıyor musun?",
            "Egzersiz rutinin nedir? (haftada kaç gün, ne tür?)",
        ]

        # Chat geçmişi göster
        for msg in st.session_state.diet_chat:
            if msg["role"] == "ai":
                st.markdown(f'<div class="chat-msg-ai">{msg["content"]}</div>', unsafe_allow_html=True)
            else:
                st.markdown(f'<div class="chat-msg-user">{msg["content"]}</div>', unsafe_allow_html=True)

        step = st.session_state.diet_step

        if step < len(diet_questions):
            # Soruyu göster
            if not st.session_state.diet_chat or st.session_state.diet_chat[-1].get("content") != diet_questions[step]:
                if not any(m["content"] == diet_questions[step] for m in st.session_state.diet_chat):
                    st.session_state.diet_chat.append({"role": "ai", "content": f"📝 Soru {step + 1}/{len(diet_questions)}: {diet_questions[step]}"})
                    st.rerun()

            answer = st.text_input(f"Yanıtın (Soru {step + 1}/{len(diet_questions)})", key=f"diet_q_{step}")

            if st.button("Yanıtla →", key=f"diet_btn_{step}"):
                if answer:
                    st.session_state.diet_answers[f"q{step}"] = answer
                    st.session_state.diet_chat.append({"role": "user", "content": answer})
                    st.session_state.diet_step += 1
                    st.rerun()

        elif step == len(diet_questions) and st.session_state.diet_answers:
            st.markdown("✅ Tüm sorular yanıtlandı! Program oluşturuluyor...")

            if st.button("🤖 Programı Oluştur", type="primary"):
                profile = load_profile()
                answers_text = "\n".join([
                    f"- {diet_questions[i]}: {st.session_state.diet_answers.get(f'q{i}', 'Yanıt yok')}"
                    for i in range(len(diet_questions))
                ])

                prompt = f"""Benim için çok detaylı ve kişiselleştirilmiş haftalık diyet programı oluştur.

Profilim:
- İsim: {profile['name']}
- Boy: {profile['height']} cm, Kilo: {profile['weight']} kg, Yaş: {profile['age']}
- Cinsiyet: {profile['gender']}, Aktivite: {profile['activity']}, Hedef: {profile['goal']}
- Günlük kalori: {calculate_tdee(profile)} kcal, BMI: {get_bmi(profile)}

Yanıtlarım:
{answers_text}

Lütfen:
1. 7 günlük detaylı program (her öğün + kaloriler)
2. Her gün için makro hedefleri
3. Market listesi
4. Pratik meal-prep önerileri
5. Motivasyon ipuçları

Programı güzel formatla, Türk mutfağına uygun yap."""

                with st.spinner("🤖 Kişisel programın hazırlanıyor..."):
                    result = ask_gemini(prompt, "Sen Türkiye'nin en iyi diyetisyenisin. Kişiye özel, uygulanabilir ve lezzetli programlar yapıyorsun.")

                st.session_state.diet_chat.append({"role": "ai", "content": result})
                save_json(DIET_FILE, {"date": today, "type": "Kişisel", "plan": result})
                st.rerun()

        # Sıfırla butonu
        if st.session_state.diet_chat:
            if st.button("🔄 Sohbeti Sıfırla"):
                st.session_state.diet_chat = []
                st.session_state.diet_step = 0
                st.session_state.diet_answers = {}
                st.rerun()

    # Kayıtlı diyet planı
    saved_plan = load_diet_plan()
    if saved_plan and saved_plan.get("plan"):
        st.divider()
        with st.expander("📄 Son Kaydedilen Diyet Planı", expanded=False):
            st.markdown(f"**Tarih:** {saved_plan.get('date', '?')} | **Tip:** {saved_plan.get('type', '?')}")
            st.markdown(saved_plan["plan"])


# ──────────────────────────────────────────────
#  TAB 5: SU TAKİBİ
# ──────────────────────────────────────────────
with tab5:
    st.markdown("### 💧 Su Takibi")
    st.markdown("Günlük su tüketimini takip et. Hedef: günde en az 2.5 litre!")

    today = get_today()
    water_data = load_water()

    if today not in water_data:
        water_data[today] = 0

    current_water = water_data[today]
    water_target = 2500  # ml

    col_w1, col_w2 = st.columns([1, 1])

    with col_w1:
        st.markdown(f"""
        <div class="welcome-card" style="padding: 30px;">
            <div style="font-size: 4rem; margin-bottom: 10px;">💧</div>
            <div style="font-size: 2.5rem; font-weight: 800; color: #38bdf8;">{current_water} ml</div>
            <div style="color: #888; margin-bottom: 16px;">/ {water_target} ml hedef</div>
            <div class="progress-container" style="max-width: 300px; margin: 0 auto;">
                <div class="progress-fill" style="width: {min(100, round(current_water / water_target * 100))}%;
                     background: linear-gradient(90deg, #38bdf8, #667eea);"></div>
            </div>
            <div style="color: #38bdf8; margin-top: 8px; font-size: 0.9rem;">
                %{min(100, round(current_water / water_target * 100))} tamamlandı —
                {max(0, water_target - current_water)} ml kaldı
            </div>
        </div>
        """, unsafe_allow_html=True)

    with col_w2:
        st.markdown("#### Hızlı Ekle")

        water_amounts = [
            ("🥛 1 Bardak (200ml)", 200),
            ("🍶 Küçük Şişe (330ml)", 330),
            ("🧴 Büyük Şişe (500ml)", 500),
            ("🫗 Büyük Bardak (300ml)", 300),
            ("☕ Çay/Kahve (150ml)", 150),
        ]

        for label, amount in water_amounts:
            if st.button(label, use_container_width=True, key=f"water_{amount}"):
                water_data[today] = water_data.get(today, 0) + amount
                save_json(WATER_FILE, water_data)
                st.rerun()

        st.divider()
        custom_water = st.number_input("Özel miktar (ml)", min_value=50, max_value=2000, value=250, step=50)
        if st.button("➕ Ekle", use_container_width=True):
            water_data[today] = water_data.get(today, 0) + custom_water
            save_json(WATER_FILE, water_data)
            st.rerun()

        if st.button("🔄 Sıfırla", use_container_width=True):
            water_data[today] = 0
            save_json(WATER_FILE, water_data)
            st.rerun()

    # Su geçmişi grafiği
    st.divider()
    st.markdown("### 📈 Son 7 Gün Su Tüketimi")

    water_chart = []
    for i in range(6, -1, -1):
        d = (datetime.now() - timedelta(days=i)).strftime("%Y-%m-%d")
        water_chart.append({"Tarih": d, "Su (ml)": water_data.get(d, 0)})

    df_water = pd.DataFrame(water_chart).set_index("Tarih")
    st.bar_chart(df_water, color="#38bdf8")
