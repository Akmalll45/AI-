import streamlit as st
import requests
from bs4 import BeautifulSoup
import random
import re
import time

# Daftar nama Indonesia
NAMA_DEPAN = [
    "Budi", "Siti", "Ahmad", "Rina", "Dedi", "Dewi", "Agus", "Sri", 
    "Wati", "Joko", "Ani", "Rudi", "Lina", "Eko", "Yuni", "Hadi",
    "Fitri", "Bambang", "Sari", "Andi", "Nur", "Ika", "Wawan", "Maya",
    "Rizki", "Dian", "Hendra", "Tuti", "Bayu", "Indah", "Cahya", "Ratna",
    "Putra", "Ayu", "Fajar", "Lilis", "Arif", "Nisa", "Doni", "Sinta",
    "Hari", "Dewi", "Yanto", "Ningsih", "Amin", "Wulan"
]

NAMA_BELAKANG = [
    "Santoso", "Wijaya", "Pratama", "Putri", "Saputra", "Wati", "Kusuma",
    "Permata", "Handoko", "Lestari", "Setiawan", "Anggraini", "Nugroho",
    "Rahayu", "Gunawan", "Maharani", "Hidayat", "Pertiwi", "Susanto",
    "Purnama", "Dharma", "Sari", "Pranoto", "Utomo", "Wibowo", "Kurniawan"
]

EMAIL_DOMAINS = ["gmail.com", "yahoo.com", "outlook.com", "hotmail.com"]

ESSAY_TEMPLATES = [
    "Sangat baik dan memuaskan. Saya mendapatkan hasil yang sesuai dengan harapan dan akan merekomendasikan kepada orang lain.",
    "Pengalaman yang saya dapatkan cukup memuaskan secara keseluruhan. Ada beberapa hal yang bisa ditingkatkan namun sudah baik.",
    "Saya merasa puas dengan layanan yang diberikan. Semuanya berjalan lancar dan sesuai ekspektasi saya.",
    "Cukup baik dan memenuhi kebutuhan. Akan lebih baik jika ada peningkatan di beberapa aspek tertentu.",
    "Memuaskan dan profesional. Terima kasih atas pelayanan yang telah diberikan dengan baik.",
]

def generate_indonesian_email():
    nama_depan = random.choice(NAMA_DEPAN).lower()
    nama_belakang = random.choice(NAMA_BELAKANG).lower()
    domain = random.choice(EMAIL_DOMAINS)
    formats = [
        f"{nama_depan}.{nama_belakang}@{domain}",
        f"{nama_depan}{nama_belakang}@{domain}",
        f"{nama_depan}.{nama_belakang}{random.randint(1, 99)}@{domain}",
    ]
    return random.choice(formats)

def generate_indonesian_name():
    return f"{random.choice(NAMA_DEPAN)} {random.choice(NAMA_BELAKANG)}"

def generate_phone():
    return f"08{random.randint(10, 99)}{random.randint(1000, 9999)}{random.randint(1000, 9999)}"

def generate_address():
    cities = ["Jakarta", "Bandung", "Surabaya", "Medan", "Semarang", 
              "Yogyakarta", "Malang", "Makassar", "Denpasar", "Palembang"]
    streets = ["Jl. Sudirman", "Jl. Gatot Subroto", "Jl. Thamrin", 
               "Jl. Ahmad Yani", "Jl. Diponegoro"]
    return f"{random.choice(streets)} No.{random.randint(1, 200)}, {random.choice(cities)}"

def extract_form_info(url):
    """Extract form action URL and entry IDs"""
    try:
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
        }
        
        response = requests.get(url, headers=headers, timeout=10)
        response.raise_for_status()
        
        html = response.text
        soup = BeautifulSoup(html, 'html.parser')
        
        # Extract form ID from URL or HTML
        form_id = None
        
        # Method 1: From URL
        match = re.search(r'/forms/d/e/([^/]+)/', url)
        if match:
            form_id = match.group(1)
        else:
            # Method 2: From HTML
            match = re.search(r'"(/forms/d/e/[^/]+/formResponse)"', html)
            if match:
                form_id = match.group(1).split('/')[-2]
        
        if not form_id:
            return None, []
        
        form_action_url = f"https://docs.google.com/forms/d/e/{form_id}/formResponse"
        
        # Extract questions and entry IDs
        questions = []
        
        # Find all entry points
        entry_pattern = re.compile(r'entry\.(\d+)')
        entries_found = entry_pattern.findall(html)
        
        # Get question texts
        question_divs = soup.find_all('div', {'role': 'listitem'})
        
        for idx, div in enumerate(question_divs):
            question_span = div.find('span')
            if not question_span:
                continue
                
            text = question_span.get_text().strip()
            if not text or len(text) < 2:
                continue
            
            # Find corresponding entry ID
            entry_id = None
            
            # Look for input/textarea with entry name
            inputs = div.find_all(['input', 'textarea'], {'name': re.compile(r'entry\.\d+')})
            if inputs:
                entry_id = inputs[0].get('name')
            
            if not entry_id and idx < len(entries_found):
                entry_id = f"entry.{entries_found[idx]}"
            
            if not entry_id:
                continue
            
            # Determine question type
            q_type = "text"
            options = []
            
            # Check for radio (multiple choice)
            radio_spans = div.find_all('span', {'class': 'aDTYNe'})
            if radio_spans:
                q_type = "multiple_choice"
                options = [span.get_text().strip() for span in radio_spans if span.get_text().strip()]
            
            # Check for checkbox
            checkbox_spans = div.find_all('span', {'class': 'n5vBHf'})
            if checkbox_spans:
                q_type = "checkbox"
                options = [span.get_text().strip() for span in checkbox_spans if span.get_text().strip()]
            
            # Check for textarea
            if div.find('textarea'):
                q_type = "paragraph"
            
            questions.append({
                'text': text,
                'type': q_type,
                'options': options,
                'entry_id': entry_id
            })
        
        return form_action_url, questions
        
    except Exception as e:
        st.error(f"Error extracting form: {str(e)}")
        return None, []

def generate_answer(question, style="random"):
    """Generate answer based on question"""
    q_text = question['text'].lower()
    q_type = question['type']
    options = question['options']
    
    # Email
    if 'email' in q_text or 'e-mail' in q_text or 'surel' in q_text:
        return generate_indonesian_email()
    
    # Name
    if 'nama' in q_text and 'lengkap' not in q_text:
        return generate_indonesian_name()
    
    if 'nama lengkap' in q_text:
        return generate_indonesian_name()
    
    # Phone
    if any(word in q_text for word in ['telepon', 'hp', 'whatsapp', 'wa', 'phone', 'nomor', 'ponsel']):
        return generate_phone()
    
    # Address
    if any(word in q_text for word in ['alamat', 'address', 'domisili', 'tinggal']):
        return generate_address()
    
    # Age
    if any(word in q_text for word in ['umur', 'usia', 'age']):
        return str(random.randint(20, 50))
    
    # Paragraph/Essay
    if q_type == "paragraph":
        return random.choice(ESSAY_TEMPLATES)
    
    # Multiple choice
    if q_type == "multiple_choice" and options:
        if style == "positive":
            return options[-1] if options else "Ya"
        elif style == "negative":
            return options[0] if options else "Tidak"
        else:
            return random.choice(options)
    
    # Checkbox
    if q_type == "checkbox" and options:
        num_select = random.randint(1, min(3, len(options)))
        return random.sample(options, num_select)
    
    # Default
    return "Baik"

def submit_form(form_url, questions, style="random"):
    """Submit form via POST request"""
    try:
        form_data = {}
        email_used = None
        
        for question in questions:
            answer = generate_answer(question, style)
            
            # Track email
            if '@' in str(answer):
                email_used = answer
            
            # Handle checkbox (multiple values)
            if question['type'] == 'checkbox' and isinstance(answer, list):
                form_data[question['entry_id']] = answer
            else:
                form_data[question['entry_id']] = str(answer)
        
        # Submit
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
            'Content-Type': 'application/x-www-form-urlencoded',
            'Referer': form_url.replace('/formResponse', '/viewform')
        }
        
        response = requests.post(
            form_url, 
            data=form_data, 
            headers=headers,
            allow_redirects=True,
            timeout=10
        )
        
        # Success if status 200 or redirected to confirmation page
        success = response.status_code == 200 or 'formResponse' in response.url
        
        return success, email_used, form_data
        
    except Exception as e:
        return False, None, str(e)

# Streamlit App
st.set_page_config(page_title="Auto Fill Google Forms", page_icon="📝", layout="wide")

st.title("📝 Google Forms Auto-Fill")
st.markdown("**Direct POST Method - No Selenium Required**")

# Sidebar
with st.sidebar:
    st.header("⚙️ Settings")
    num_responses = st.number_input("Jumlah Responden", 1, 100, 5)
    response_style = st.selectbox("Gaya Jawaban", ["random", "positive", "negative"])
    delay = st.slider("Delay (detik)", 0, 5, 1)
    
    st.markdown("---")
    st.success("✅ Pure POST request\n✅ No browser needed\n✅ Fast & reliable")

# Main
url = st.text_input(
    "🔗 Google Forms URL",
    placeholder="https://docs.google.com/forms/d/e/...",
    help="Paste your Google Forms link here"
)

col1, col2 = st.columns([1, 3])

with col1:
    analyze = st.button("🔍 Analyze", type="primary", use_container_width=True)

with col2:
    submit = st.button("🚀 Auto Submit", type="secondary", use_container_width=True, disabled=not url)

# Analyze
if analyze and url:
    with st.spinner("Analyzing form..."):
        form_url, questions = extract_form_info(url)
        
        if form_url and questions:
            st.success(f"✅ Found {len(questions)} questions")
            
            # Show form URL
            st.code(form_url, language="text")
            
            # Show questions
            st.markdown("### 📋 Questions")
            for i, q in enumerate(questions, 1):
                icon = {"text": "📝", "multiple_choice": "⭕", "checkbox": "☑️", "paragraph": "📄"}.get(q['type'], "❓")
                with st.expander(f"{icon} {i}. {q['text'][:60]}..."):
                    st.write(f"**Question:** {q['text']}")
                    st.write(f"**Type:** {q['type']}")
                    st.write(f"**Entry ID:** `{q['entry_id']}`")
                    if q['options']:
                        st.write(f"**Options:** {', '.join(q['options'][:5])}{'...' if len(q['options']) > 5 else ''}")
            
            st.session_state['form_url'] = form_url
            st.session_state['questions'] = questions
        else:
            st.error("❌ Failed to extract form data. Check if the URL is correct and form is public.")

# Submit
if submit and url:
    if 'form_url' not in st.session_state:
        st.warning("⚠️ Please analyze the form first!")
    else:
        form_url = st.session_state['form_url']
        questions = st.session_state['questions']
        
        st.markdown("### 🚀 Submitting...")
        
        progress = st.progress(0)
        status = st.empty()
        
        results = []
        success_count = 0
        
        for i in range(num_responses):
            status.text(f"📤 Submitting {i+1}/{num_responses}...")
            
            success, email, data = submit_form(form_url, questions, response_style)
            
            if success:
                success_count += 1
                results.append({
                    'No': i + 1,
                    'Status': '✅ Success',
                    'Email': email or 'N/A'
                })
            else:
                results.append({
                    'No': i + 1,
                    'Status': '❌ Failed',
                    'Email': 'N/A'
                })
            
            st.dataframe(results, use_container_width=True, height=250)
            progress.progress((i + 1) / num_responses)
            
            if i < num_responses - 1:
                time.sleep(delay)
        
        status.text("✅ Done!")
        
        # Summary
        col1, col2, col3 = st.columns(3)
        col1.metric("Total", num_responses)
        col2.metric("✅ Success", success_count)
        col3.metric("❌ Failed", num_responses - success_count)
        
        if success_count > 0:
            st.balloons()
            st.success(f"🎉 Successfully submitted {success_count}/{num_responses} responses!")
            st.info("📊 Check your Google Forms → Responses tab to see the results!")
        else:
            st.error("❌ All submissions failed. Please check form settings.")

st.markdown("---")
st.caption("💡 Make sure your form accepts responses and doesn't require sign-in")
