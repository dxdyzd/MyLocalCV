import streamlit as st
import PyPDF2
import io
import os
from openai import OpenAI
from dotenv import load_dotenv

load_dotenv()

st.set_page_config(page_title='MyLocalCV', layout='centered')
st.title('MyLocalCV')
st.markdown('Platform terbuka gratis dan open-source untuk review CV menggunakan AI.')

LLAMA_API_KEY = os.getenv('LLAMA_API_KEY')

uploaded_file = st.file_uploader("Upload PDF atau docx", type=['docx', 'pdf'])
job_role = st.text_input('Tulis nama role yang kalian lamar (Opsional): ')

analyze = st.button('Analyze')

def extract_text_from_pdf(pdf_file):
    pdf_reader = PyPDF2.PdfReader(pdf_file)
    text = ""
    for page in pdf_reader.pages:
        text += page.extract_text() + "\n"
    return text

def extract_text_from_file(uploaded_file):
    if uploaded_file.type == "application/pdf":
        return extract_text_from_pdf(io.BytesIO(uploaded_file.read()))
    return uploaded_file.read().decode("utf-8")

if analyze and uploaded_file:
    try:
        file_content = extract_text_from_file(uploaded_file)
        
        if not file_content.strip():
            st.error("File does not have any contnet...")
            st.stop()
        
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
            api_key=LLAMA_API_KEY,
            base_url="https://openrouter.ai/api/v1"
        )

        with st.spinner("Loading Analisis..."):
            response = client.chat.completions.create(
                model="meta-llama/llama-3.3-8b-instruct:free",
                messages=[
                    {"role": "system", "content": "You are an expert and wise senior resume reviewer with 5 years of experience in HR and recruitment."},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.7,
                max_tokens=1000
            )
        st.markdown("### Analysis Results")
        st.markdown(response.choices[0].message.content)
    
    except Exception as e:
        st.error(f"An error occured: {str(e)}")