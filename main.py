import streamlit as st
import PyPDF2
import io
import os
from openai import OpenAI
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Page configuration
st.set_page_config(
    page_title='MyLocalCV',
    layout='centered'
)

# Custom CSS untuk styling yang lebih menarik
st.markdown("""
<style>
    /* Global Styles */
    .stApp {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
    }
    
    /* Main container styling */
    .main .block-container {
        background: rgba(255, 255, 255, 0.95);
        border-radius: 20px;
        padding: 2rem;
        margin: 2rem auto;
        box-shadow: 0 8px 32px rgba(0, 0, 0, 0.1);
        backdrop-filter: blur(10px);
        border: 1px solid rgba(255, 255, 255, 0.2);
        max-width: 800px;
    }
    
    /* Header styling */
    .stTitle h1 {
        color: #2d3748;
        font-size: 2.5rem !important;
        font-weight: 700;
        text-align: center;
        margin-bottom: 0.5rem;
        background: linear-gradient(45deg, #667eea, #764ba2);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        background-clip: text;
    }
    
    /* Subheader */
    .stMarkdown h1 {
        color: #4a5568;
        text-align: center;
        font-size: 1.1rem !important;
        font-weight: 400;
        margin-bottom: 2rem;
    }
    
    /* File uploader styling */
    .stFileUploader > div > div {
        background: white;
        border: 2px dashed #cbd5e0 !important;
        border-radius: 15px !important;
        padding: 2rem !important;
        transition: all 0.3s ease !important;
    }
    
    .stFileUploader > div > div:hover {
        border-color: #667eea !important;
        background: #f7fafc !important;
    }
    
    /* Text input styling */
    .stTextInput input {
        border: 2px solid #e2e8f0 !important;
        border-radius: 12px !important;
        padding: 0.75rem 1rem !important;
        font-size: 1rem !important;
        transition: all 0.3s ease !important;
    }
    
    .stTextInput input:focus {
        border-color: #667eea !important;
        box-shadow: 0 0 0 3px rgba(102, 126, 234, 0.1) !important;
    }
    
    /* Button styling */
    .stButton button {
        background: linear-gradient(45deg, #667eea, #764ba2) !important;
        color: white !important;
        border: none !important;
        border-radius: 12px !important;
        padding: 0.75rem 2rem !important;
        font-size: 1.1rem !important;
        font-weight: 600 !important;
        transition: all 0.3s ease !important;
        width: 100% !important;
        margin: 1rem 0 !important;
        box-shadow: 0 4px 15px rgba(102, 126, 234, 0.3) !important;
    }
    
    .stButton button:hover {
        transform: translateY(-2px) !important;
        box-shadow: 0 6px 20px rgba(102, 126, 234, 0.4) !important;
    }
    
    /* Results header */
    .stMarkdown h3 {
        color: #2d3748 !important;
        font-size: 1.5rem !important;
        font-weight: 600 !important;
        margin: 2rem 0 1rem 0 !important;
        border-bottom: 3px solid #667eea !important;
        padding-bottom: 0.5rem !important;
    }
    
    /* Custom divider */
    hr {
        border: none !important;
        height: 3px !important;
        background: linear-gradient(90deg, #667eea, #764ba2) !important;
        border-radius: 10px !important;
        margin: 2rem 0 !important;
    }
    
    /* Alert boxes */
    .stAlert {
        border-radius: 12px !important;
        padding: 1rem !important;
    }
    
    /* Spinner color */
    .stSpinner > div {
        border-color: #667eea transparent transparent transparent !important;
    }
</style>
""", unsafe_allow_html=True)

# Header section
st.title('MyLocalCV')
st.markdown('Platform terbuka gratis dan open-source untuk review CV menggunakan AI.')

# Configuration
OPENAI_API_KEY = os.getenv('OPENAI_API_KEY')

def extract_text_from_pdf(pdf_file):
    """Extract text from PDF file"""
    pdf_reader = PyPDF2.PdfReader(pdf_file)
    text = ""
    for page in pdf_reader.pages:
        text += page.extract_text() + "\n"
    return text

def extract_text_from_file(uploaded_file):
    """Extract text from uploaded file based on file type"""
    if uploaded_file.type == "application/pdf":
        return extract_text_from_pdf(io.BytesIO(uploaded_file.read()))
    else:
        # For text-based files like docx
        return uploaded_file.read().decode("utf-8")

def analyze_resume(file_content, job_role=""):
    """Analyze resume using AI model"""
    prompt = f"""
    Analisislah CV atau resume di bawah ini dan memberikan masukan yang membangun. 
    Fokuslah pada hal-hal berikut:
    1. Kejelasan dan dampak dari isi CV
    2. Cara penyajian keterampilan (skills)
    3. Deskripsi pengalaman kerja
    4. Saran spesifik untuk meningkatkan CV agar lebih sesuai dengan posisi {job_role if job_role else 'lamaran kerja secara umum'}

    Berikan hasil analisis dalam format yang rapi dan terstruktur yaitu berupa poin berikut:
    1. Penjelasan mengenai tentang apa sih CV tersebut?
    2. tulislah kekurangan kekurangan dalam bentuk nomor
    3. Tulislah kelebihan kelebihan dalam bentuk nomor
    4. Sertakan juga hal apa saja yang dapat direkomendasikan untuk dilakukan sehingga CV nya menjadi lebih bagus dan profesional.   
    Gunakan bahasa Indonesia yang alami dan mudah dipahami manusia — hindari bahasa yang terlalu kaku atau terdengar seperti mesin.

    Konten CV:
    {file_content}
    """
    
    client = OpenAI(
        api_key=OPENAI_API_KEY,
        base_url="https://openrouter.ai/api/v1"
    )

    response = client.chat.completions.create(
        model="OPENAI/gpt-oss-20b:free",
        messages=[
            {
                "role": "system", 
                "content": "You are an expert and wise senior resume reviewer with 5 years of experience in HR and recruitment."
            },
            {
                "role": "user", 
                "content": prompt
            }
        ],
        temperature=0.7,
        max_tokens=1000
    )
    
    return response.choices[0].message.content

# Main application
def main():
    # File upload section
    uploaded_file = st.file_uploader(
        "Upload PDF atau docx", 
        type=['docx', 'pdf']
    )
    
    # Job role input
    job_role = st.text_input(
        'Tulis nama role yang kalian lamar (Opsional): '
    )
    
    # Analyze button
    analyze = st.button('Analyze', type='primary')
    
    # Process analysis when button is clicked
    if analyze and uploaded_file:
        try:
            # Extract text from file
            file_content = extract_text_from_file(uploaded_file)
            
            # Validate file content
            if not file_content.strip():
                st.error("File tidak berisi teks yang dapat dibaca...")
                return
            
            # Show loading spinner during analysis
            with st.spinner("Sedang menganalisis CV Anda..."):
                analysis_result = analyze_resume(file_content, job_role)
            
            # Display results
            st.markdown("### Hasil Analisis")
            st.markdown("---")
            st.markdown(analysis_result)
            
        except Exception as e:
            st.error(f"Terjadi kesalahan: {str(e)}")
            st.info("Pastikan file yang diupload valid dan coba lagi.")

# Run the application
if __name__ == "__main__":
    main()