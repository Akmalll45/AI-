import streamlit as st
import requests
from bs4 import BeautifulSoup
import random
import re
import time
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager

# Daftar nama depan Indonesia
NAMA_DEPAN = [
    "Budi", "Siti", "Ahmad", "Rina", "Dedi", "Dewi", "Agus", "Sri", 
    "Wati", "Joko", "Ani", "Rudi", "Lina", "Eko", "Yuni", "Hadi",
    "Fitri", "Bambang", "Sari", "Andi", "Nur", "Ika", "Wawan", "Maya",
    "Rizki", "Dian", "Hendra", "Tuti", "Bayu", "Indah", "Cahya", "Ratna",
    "Putra", "Ayu", "Fajar", "Lilis", "Arif", "Nisa", "Doni", "Sinta"
]

NAMA_BELAKANG = [
    "Santoso", "Wijaya", "Pratama", "Putri", "Saputra", "Wati", "Kusuma",
    "Permata", "Handoko", "Lestari", "Setiawan", "Anggraini", "Nugroho",
    "Rahayu", "Gunawan", "Maharani", "Hidayat", "Pertiwi", "Susanto",
    "Purnama", "Dharma", "Sari", "Pranoto", "Dewi", "Utomo", "Indah",
    "Wibowo", "Cahyani", "Kurniawan", "Safitri"
]

EMAIL_DOMAINS = ["gmail.com", "yahoo.com", "outlook.com", "hotmail.com"]

# Template jawaban essay berdasarkan konteks
ESSAY_TEMPLATES = {
    'pengalaman': [
        "Pengalaman saya sangat berkesan dan memberikan banyak pembelajaran berharga. Saya merasa puas dengan pelayanan yang diberikan.",
        "Secara keseluruhan pengalaman yang saya dapatkan cukup memuaskan. Ada beberapa hal yang perlu ditingkatkan namun secara umum sudah baik.",
        "Saya memiliki pengalaman yang luar biasa. Semuanya berjalan lancar dan sesuai dengan ekspektasi saya.",
        "Pengalaman yang saya rasakan cukup baik meskipun ada beberapa kekurangan kecil yang bisa diperbaiki di masa mendatang.",
        "Sangat memuaskan! Saya mendapatkan lebih dari yang saya harapkan dan akan merekomendasikan kepada teman-teman."
    ],
    'saran': [
        "Saran saya adalah untuk terus meningkatkan kualitas layanan dan mempertahankan standar yang sudah baik ini.",
        "Mungkin bisa ditambahkan lebih banyak pilihan dan variasi. Secara keseluruhan sudah sangat baik.",
        "Pertahankan kualitas yang sudah ada dan terus berinovasi untuk memberikan pengalaman terbaik.",
        "Tingkatkan komunikasi dan responsivitas terhadap kebutuhan pengguna. Sudah bagus tapi masih bisa lebih baik.",
        "Saran saya untuk mempercepat proses dan menambah fitur-fitur baru yang lebih user-friendly."
    ],
    'pendapat': [
        "Menurut saya ini sudah sangat baik dan memenuhi harapan. Saya puas dengan hasil yang diberikan.",
        "Pendapat saya cukup positif. Ada beberapa aspek yang menonjol dan membuat pengalaman menjadi menyenangkan.",
        "Saya berpendapat bahwa masih ada ruang untuk perbaikan meskipun secara umum sudah cukup memuaskan.",
        "Menurut pandangan saya, ini adalah salah satu yang terbaik. Sangat direkomendasikan untuk dicoba.",
        "Pendapat saya adalah perlu ada peningkatan di beberapa area, namun fondasi yang ada sudah sangat solid."
    ],
    'komentar': [
        "Komentar saya secara umum positif. Terus pertahankan dan tingkatkan kualitas yang sudah ada.",
        "Saya ingin memberikan apresiasi untuk kerja keras yang sudah dilakukan. Hasilnya terlihat jelas.",
        "Beberapa catatan kecil perlu diperhatikan namun secara keseluruhan sudah sangat baik dan memuaskan.",
        "Komentar saya adalah lanjutkan inovasi dan jangan berhenti untuk berkembang menjadi lebih baik lagi.",
        "Sangat bagus! Saya tidak memiliki keluhan berarti dan akan terus mendukung ke depannya."
    ],
    'default': [
        "Sangat baik dan memuaskan. Saya mendapatkan hasil yang sesuai dengan harapan.",
        "Cukup baik secara keseluruhan. Ada beberapa hal yang bisa ditingkatkan untuk pengalaman lebih baik.",
        "Memuaskan dan memenuhi ekspektasi. Akan terus menggunakan dan merekomendasikan.",
        "Pengalaman yang positif dengan hasil yang bagus. Terima kasih atas layanan yang diberikan.",
        "Sudah sangat baik namun masih ada ruang untuk perbaikan dan peningkatan kualitas."
    ]
}

def generate_indonesian_email():
    """Generate email dengan nama Indonesia"""
    nama_depan = random.choice(NAMA_DEPAN).lower()
    nama_belakang = random.choice(NAMA_BELAKANG).lower()
    domain = random.choice(EMAIL_DOMAINS)
    
    formats = [
        f"{nama_depan}.{nama_belakang}@{domain}",
        f"{nama_depan}{nama_belakang}@{domain}",
        f"{nama_depan}.{nama_belakang}{random.randint(1, 99)}@{domain}",
        f"{nama_depan[0]}.{nama_belakang}@{domain}",
    ]
    
    return random.choice(formats)

def generate_indonesian_name():
    """Generate nama lengkap Indonesia"""
    return f"{random.choice(NAMA_DEPAN)} {random.choice(NAMA_BELAKANG)}"

def generate_phone():
    """Generate nomor telepon Indonesia"""
    return f"08{random.randint(10, 99)}{random.randint(1000, 9999)}{random.randint(1000, 9999)}"

def generate_essay_answer(question_text):
    """Generate jawaban essay yang natural berdasarkan konteks pertanyaan"""
    q_lower = question_text.lower()
    
    # Deteksi konteks pertanyaan
    if any(word in q_lower for word in ['pengalaman', 'experience', 'cerita']):
        return random.choice(ESSAY_TEMPLATES['pengalaman'])
    elif any(word in q_lower for word in ['saran', 'suggestion', 'masukan', 'kritik']):
        return random.choice(ESSAY_TEMPLATES['saran'])
    elif any(word in q_lower for word in ['pendapat', 'opinion', 'menurut']):
        return random.choice(ESSAY_TEMPLATES['pendapat'])
    elif any(word in q_lower for word in ['komentar', 'comment', 'tanggapan']):
        return random.choice(ESSAY_TEMPLATES['komentar'])
    else:
        return random.choice(ESSAY_TEMPLATES['default'])

def scrape_google_form(url):
    """Scrape pertanyaan dari Google Form"""
    try:
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        }
        response = requests.get(url, headers=headers)
        soup = BeautifulSoup(response.text, 'html.parser')
        
        questions = []
        question_divs = soup.find_all('div', {'role': 'listitem'})
        
        for div in question_divs:
            question_text = div.find('span')
            if question_text:
                text = question_text.get_text().strip()
                if text and len(text) > 3:
                    q_type = "text"
                    options = []
                    
                    # Multiple choice
                    radio_options = div.find_all('span', {'class': 'aDTYNe'})
                    if radio_options:
                        q_type = "multiple_choice"
                        options = [opt.get_text().strip() for opt in radio_options]
                    
                    # Checkbox
                    checkbox_options = div.find_all('span', {'class': 'n5vBHf'})
                    if checkbox_options:
                        q_type = "checkbox"
                        options = [opt.get_text().strip() for opt in checkbox_options]
                    
                    # Detect textarea/paragraph
                    if div.find('textarea') or 'paragraph' in str(div):
                        q_type = "essay"
                    
                    questions.append({
                        'text': text,
                        'type': q_type,
                        'options': options
                    })
        
        return questions
    except Exception as e:
        st.error(f"Error scraping form: {e}")
        return []

def generate_answer(question, response_style="random"):
    """Generate jawaban untuk pertanyaan"""
    q_text = question['text'].lower()
    q_type = question['type']
    options = question['options']
    
    # Email
    if 'email' in q_text or 'e-mail' in q_text:
        return generate_indonesian_email()
    
    # Nama
    if 'nama' in q_text:
        return generate_indonesian_name()
    
    # Umur/Usia
    if 'umur' in q_text or 'usia' in q_text:
        return str(random.randint(18, 45))
    
    # Telepon
    if any(word in q_text for word in ['telepon', 'hp', 'whatsapp', 'wa', 'phone', 'nomor']):
        return generate_phone()
    
    # Essay/Paragraph
    if q_type == "essay" or any(word in q_text for word in ['ceritakan', 'jelaskan', 'deskripsikan', 'pendapat', 'saran', 'komentar']):
        return generate_essay_answer(question['text'])
    
    # Multiple choice
    if q_type == "multiple_choice" and options:
        if response_style == "positive":
            return options[-1] if len(options) > 0 else options[0]
        elif response_style == "negative":
            return options[0]
        else:
            return random.choice(options)
    
    # Checkbox
    if q_type == "checkbox" and options:
        num_choices = random.randint(1, min(3, len(options)))
        return random.sample(options, num_choices)
    
    # Default text
    return "Baik dan memuaskan"

def setup_driver(headless=True):
    """Setup Selenium WebDriver"""
    chrome_options = Options()
    if headless:
        chrome_options.add_argument("--headless")
    chrome_options.add_argument("--no-sandbox")
    chrome_options.add_argument("--disable-dev-shm-usage")
    chrome_options.add_argument("--disable-gpu")
    chrome_options.add_argument("--window-size=1920,1080")
    chrome_options.add_argument("user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36")
    
    try:
        service = Service(ChromeDriverManager().install())
        driver = webdriver.Chrome(service=service, options=chrome_options)
        return driver
    except Exception as e:
        st.error(f"Error setting up Chrome driver: {e}")
        return None

def fill_google_form_selenium(url, questions, response_style="random", progress_callback=None):
    """Fill Google Form menggunakan Selenium"""
    driver = setup_driver(headless=True)
    if not driver:
        return False, "Failed to setup Chrome driver"
    
    try:
        driver.get(url)
        time.sleep(2)
        
        wait = WebDriverWait(driver, 10)
        email = generate_indonesian_email()
        responses_data = {'email': email}
        
        for i, question in enumerate(questions):
            try:
                answer = generate_answer(question, response_style)
                responses_data[question['text'][:30]] = str(answer)[:50]
                
                q_text_lower = question['text'].lower()
                
                # Text input & Essay
                if question['type'] in ["text", "essay"]:
                    # Try textarea first (for essay)
                    textareas = driver.find_elements(By.CSS_SELECTOR, "textarea")
                    if textareas and question['type'] == "essay":
                        textareas[0].send_keys(str(answer))
                        time.sleep(0.3)
                    else:
                        # Regular text input
                        text_inputs = driver.find_elements(By.CSS_SELECTOR, "input[type='text'], input[type='email']")
                        if i < len(text_inputs):
                            text_inputs[i].send_keys(str(answer))
                            time.sleep(0.3)
                
                # Multiple choice
                elif question['type'] == "multiple_choice":
                    radio_buttons = driver.find_elements(By.CSS_SELECTOR, "div[role='radio']")
                    if radio_buttons:
                        for rb in radio_buttons:
                            if answer in rb.text:
                                rb.click()
                                time.sleep(0.3)
                                break
                
                # Checkbox
                elif question['type'] == "checkbox":
                    checkboxes = driver.find_elements(By.CSS_SELECTOR, "div[role='checkbox']")
                    if isinstance(answer, list):
                        for ans in answer:
                            for cb in checkboxes:
                                if ans in cb.text:
                                    cb.click()
                                    time.sleep(0.3)
                                    break
                
                if progress_callback:
                    progress_callback((i + 1) / len(questions))
                    
            except Exception as e:
                st.warning(f"Skipping question {i+1}: {str(e)[:100]}")
                continue
        
        # Submit
        submit_buttons = driver.find_elements(By.CSS_SELECTOR, "span[class*='NPEfkd']")
        for btn in submit_buttons:
            if 'kirim' in btn.text.lower() or 'submit' in btn.text.lower():
                btn.click()
                time.sleep(2)
                break
        
        driver.quit()
        return True, responses_data
        
    except Exception as e:
        if driver:
            driver.quit()
        return False, str(e)

# Demo Mode - Generate sample questions
def get_demo_questions():
    """Generate demo questions untuk testing"""
    return [
        {
            'text': 'Nama Lengkap',
            'type': 'text',
            'options': []
        },
        {
            'text': 'Alamat Email',
            'type': 'text',
            'options': []
        },
        {
            'text': 'Nomor Telepon/WhatsApp',
            'type': 'text',
            'options': []
        },
        {
            'text': 'Usia Anda',
            'type': 'text',
            'options': []
        },
        {
            'text': 'Bagaimana pendapat Anda tentang layanan kami?',
            'type': 'multiple_choice',
            'options': ['Sangat Tidak Puas', 'Tidak Puas', 'Netral', 'Puas', 'Sangat Puas']
        },
        {
            'text': 'Pilih fitur yang Anda gunakan (boleh pilih lebih dari satu)',
            'type': 'checkbox',
            'options': ['Fitur A', 'Fitur B', 'Fitur C', 'Fitur D', 'Fitur E']
        },
        {
            'text': 'Ceritakan pengalaman Anda menggunakan layanan kami',
            'type': 'essay',
            'options': []
        },
        {
            'text': 'Apa saran Anda untuk perbaikan ke depan?',
            'type': 'essay',
            'options': []
        }
    ]

# Streamlit UI
st.set_page_config(page_title="AI Kuesioner Auto-Fill", page_icon="📝", layout="wide")

st.title("📝 AI Kuesioner Auto-Fill + Auto Submit")
st.markdown("**Isi kuesioner secara otomatis dengan responden berbeda (Email Indonesia) + Support Checkbox & Essay**")

# Tabs
tab1, tab2 = st.tabs(["📋 Real Form", "🧪 Demo Mode"])

with tab2:
    st.markdown("### 🧪 Demo Mode - Testing Tanpa Google Form")
    st.info("Mode ini untuk testing fitur tanpa perlu link Google Form. Lihat bagaimana AI generate jawaban untuk berbagai tipe pertanyaan.")
    
    col1, col2 = st.columns([2, 1])
    with col1:
        demo_responses = st.number_input("Jumlah Responden Demo", 1, 20, 5, key="demo_num")
    with col2:
        demo_style = st.selectbox("Gaya Jawaban", ["random", "positive", "negative"], key="demo_style")
    
    if st.button("🎲 Generate Demo Data", type="primary", use_container_width=True):
        demo_questions = get_demo_questions()
        
        st.markdown("### 📋 Preview Pertanyaan Demo")
        for i, q in enumerate(demo_questions, 1):
            with st.expander(f"❓ {q['text']}", expanded=False):
                st.write(f"**Tipe:** `{q['type']}`")
                if q['options']:
                    st.write(f"**Opsi:** {', '.join(q['options'])}")
        
        st.markdown("### 🤖 Generated Responses")
        
        progress_bar = st.progress(0)
        results_data = []
        
        for i in range(demo_responses):
            email = generate_indonesian_email()
            
            row_data = {
                'No': i + 1,
                'Email': email
            }
            
            for q in demo_questions:
                answer = generate_answer(q, demo_style)
                # Truncate for display
                if isinstance(answer, list):
                    display_answer = ', '.join(answer[:2]) + ('...' if len(answer) > 2 else '')
                else:
                    display_answer = str(answer)[:60] + ('...' if len(str(answer)) > 60 else '')
                
                row_data[q['text'][:25]] = display_answer
            
            results_data.append(row_data)
            progress_bar.progress((i + 1) / demo_responses)
        
        st.dataframe(results_data, use_container_width=True, height=400)
        
        # Sample detailed view
        st.markdown("### 📝 Contoh Detail Jawaban Essay")
        sample_q = [q for q in demo_questions if q['type'] == 'essay'][0]
        sample_answer = generate_answer(sample_q, demo_style)
        
        st.text_area(
            f"Pertanyaan: {sample_q['text']}", 
            sample_answer,
            height=100,
            disabled=True
        )
        
        st.success(f"✅ Berhasil generate {demo_responses} responden demo!")

with tab1:
    # Sidebar
    with st.sidebar:
        st.header("⚙️ Konfigurasi")
        
        num_responses = st.number_input(
            "Jumlah Responden",
            min_value=1,
            max_value=50,
            value=5,
            help="Berapa banyak responden yang akan di-generate dan submit"
        )
        
        response_style = st.selectbox(
            "Gaya Jawaban",
            ["random", "positive", "negative", "neutral"],
            help="Tipe jawaban yang akan di-generate"
        )
        
        submit_mode = st.radio(
            "Mode Pengisian",
            ["Preview Only", "Auto Submit"],
            help="Preview: hanya tampilkan data. Auto Submit: langsung kirim ke form"
        )
        
        delay_between = st.slider(
            "Delay antar submit (detik)",
            min_value=1,
            max_value=10,
            value=3,
            help="Jeda waktu antar submission"
        )
        
        st.markdown("---")
        st.markdown("### 📊 Info")
        st.info("✅ Email unik per responden\n✅ Support text, checkbox, essay\n✅ Jawaban essay natural")
    
    # Main content
    url_input = st.text_input(
        "🔗 Masukkan Link Kuesioner (Google Forms)",
        placeholder="https://forms.gle/xxxxx atau https://docs.google.com/forms/d/e/xxxxx",
        help="Paste link Google Forms di sini"
    )
    
    col1, col2 = st.columns([1, 4])
    
    with col1:
        analyze_btn = st.button("🔍 Analisis", type="primary", use_container_width=True)
    
    with col2:
        fill_btn = st.button("🚀 Mulai Proses", type="secondary", use_container_width=True, disabled=not url_input)
    
    # Analisis
    if analyze_btn and url_input:
        with st.spinner("Menganalisis kuesioner..."):
            questions = scrape_google_form(url_input)
            
            if questions:
                st.success(f"✅ Ditemukan {len(questions)} pertanyaan")
                
                # Count by type
                type_counts = {}
                for q in questions:
                    type_counts[q['type']] = type_counts.get(q['type'], 0) + 1
                
                col1, col2, col3, col4 = st.columns(4)
                col1.metric("📝 Text", type_counts.get('text', 0))
                col2.metric("⭕ Multiple Choice", type_counts.get('multiple_choice', 0))
                col3.metric("☑️ Checkbox", type_counts.get('checkbox', 0))
                col4.metric("📄 Essay", type_counts.get('essay', 0))
                
                st.markdown("### 📋 Preview Pertanyaan")
                for i, q in enumerate(questions, 1):
                    icon = "📝" if q['type'] == 'text' else "⭕" if q['type'] == 'multiple_choice' else "☑️" if q['type'] == 'checkbox' else "📄"
                    with st.expander(f"{icon} Pertanyaan {i}: {q['text'][:50]}..."):
                        st.write(f"**Teks:** {q['text']}")
                        st.write(f"**Tipe:** `{q['type']}`")
                        if q['options']:
                            st.write(f"**Opsi:** {', '.join(q['options'])}")
                
                st.session_state['questions'] = questions
            else:
                st.error("❌ Tidak dapat mengambil pertanyaan. Pastikan link benar dan form publik.")
    
    # Fill form
    if fill_btn and url_input:
        if 'questions' not in st.session_state:
            st.warning("⚠️ Silakan analisis form terlebih dahulu")
        else:
            questions = st.session_state['questions']
            
            if submit_mode == "Preview Only":
                st.markdown("### 🤖 Preview Responses")
                
                progress_bar = st.progress(0)
                results_data = []
                
                for i in range(num_responses):
                    email = generate_indonesian_email()
                    
                    answers = {'No': i + 1, 'Email': email}
                    for q in questions:
                        answer = generate_answer(q, response_style)
                        if isinstance(answer, list):
                            display = ', '.join(answer[:2]) + ('...' if len(answer) > 2 else '')
                        else:
                            display = str(answer)[:50] + ('...' if len(str(answer)) > 50 else '')
                        answers[q['text'][:25]] = display
                    
                    results_data.append(answers)
                    progress_bar.progress((i + 1) / num_responses)
                
                st.dataframe(results_data, use_container_width=True, height=400)
                st.success(f"✅ Preview {num_responses} responden berhasil!")
                
            else:  # Auto Submit
                st.markdown("### 🚀 Auto Submit")
                st.warning("⚠️ Proses berjalan... Jangan tutup browser!")
                
                progress_bar = st.progress(0)
                status_text = st.empty()
                results_container = st.container()
                
                results_data = []
                success_count = 0
                
                for i in range(num_responses):
                    status_text.text(f"📤 Submitting {i + 1}/{num_responses}...")
                    
                    def progress_cb(prog):
                        progress_bar.progress((i + prog) / num_responses)
                    
                    success, response_data = fill_google_form_selenium(url_input, questions, response_style, progress_cb)
                    
                    if success:
                        success_count += 1
                        results_data.append({
                            'No': i + 1,
                            'Email': response_data.get('email', 'N/A'),
                            'Status': "✅ Submitted"
                        })
                    else:
                        results_data.append({
                            'No': i + 1,
                            'Email': 'N/A',
                            'Status': f"❌ Failed"
                        })
                    
                    with results_container:
                        st.dataframe(results_data, use_container_width=True)
                    
                    if i < num_responses - 1:
                        time.sleep(delay_between)
                    
                    progress_bar.progress((i + 1) / num_responses)
                
                status_text.text("✅ Selesai!")
                
                col1, col2 = st.columns(2)
                col1.metric("Total", num_responses)
                col2.metric("Berhasil", success_count)
                
                st.success(f"🎉 Submit {success_count}/{num_responses} responden!")

st.markdown("---")
st.markdown("""
<div style='text-align: center; color: gray;'>
    <p>💡 Gunakan <b>Demo Mode</b> untuk testing tanpa Google Form | <b>Real Form</b> untuk auto-submit</p>
</div>
""", unsafe_allow_html=True)