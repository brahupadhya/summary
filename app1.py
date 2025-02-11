import os
import streamlit as st
import google.generativeai as genai
import fitz  # PyMuPDF untuk ekstraksi teks dari PDF
from dotenv import load_dotenv

# Load API Key dari .env
load_dotenv()
api_key = os.getenv("GEMINI_API_KEY")

# Konfigurasi Google Gemini AI
genai.configure(api_key=api_key)

# Fungsi untuk ekstrak teks dari PDF
def extract_text_from_pdf(pdf_file):
    """Mengekstrak teks dari file PDF yang diunggah."""
    with fitz.open(stream=pdf_file.read(), filetype="pdf") as doc:
        text = ""
        for page in doc:
            text += page.get_text("text") + "\n"
    return text.strip()

# Fungsi untuk membuat ringkasan menggunakan Gemini AI
def summarize_text(text):
    """Menggunakan Google Gemini AI untuk merangkum teks."""
    model = genai.GenerativeModel("gemini-pro")
    response = model.generate_content(f"Ringkas artikel ilmiah berikut dalam bahasa Indonesia:\n\n{text}")
    
    return response.text if response and response.text else "Ringkasan tidak dapat dibuat."

# UI dengan Streamlit
st.set_page_config(page_title="AI Ringkasan PDF", layout="centered")

st.title("📄 AI Ringkasan Otomatis dari PDF")
st.write("Unggah artikel ilmiah dalam format PDF, dan sistem akan menampilkan ringkasan otomatis menggunakan **Google Gemini AI**.")

# Upload file PDF
uploaded_file = st.file_uploader("Unggah file PDF", type=["pdf"])

if uploaded_file:
    st.success("📂 File berhasil diunggah! Memproses...")
    
    # Ekstrak teks dari PDF
    with st.spinner("📖 Mengekstrak teks dari PDF..."):
        extracted_text = extract_text_from_pdf(uploaded_file)
    
    # Tampilkan teks asli jika diinginkan
    with st.expander("📜 Lihat teks asli dari PDF"):
        st.text_area("Teks Asli", extracted_text, height=300)

    # Buat ringkasan
    if st.button("🔍 Buat Ringkasan"):
        with st.spinner("🤖 Menghasilkan ringkasan dengan AI..."):
            summary = summarize_text(extracted_text)
        st.subheader("📌 Ringkasan:")
        st.write(summary)

st.sidebar.markdown("🔹 **Dibuat dengan Streamlit & Google Gemini AI**")
st.sidebar.markdown("📌 **Fitur:**")
st.sidebar.markdown("- Upload PDF 📂")
st.sidebar.markdown("- Ekstraksi teks dari PDF 📖")
st.sidebar.markdown("- Ringkasan otomatis dengan AI 🤖")
