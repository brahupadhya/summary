import os
import re
import streamlit as st
import google.generativeai as genai
import fitz  # PyMuPDF untuk ekstrak teks
from dotenv import load_dotenv

# Load API Key dari .env
load_dotenv()
api_key = os.getenv("GEMINI_API_KEY")

# Konfigurasi Google Gemini AI
genai.configure(api_key=api_key)

# Fungsi ekstrak metadata berdasarkan pola teks artikel ilmiah
def extract_metadata_from_text(text):
    """Menentukan metadata berdasarkan pola teks PDF"""
    lines = text.split("\n")
    metadata = {}

    # Nama jurnal (baris pertama)
    if len(lines) > 0:
        metadata["Nama Jurnal"] = lines[0].strip()

    # Judul Artikel (baris yang full kapital)
    for line in lines[1:5]:  # Cek beberapa baris awal
        if line.isupper() and len(line) > 5:
            metadata["Judul Artikel"] = line.strip()
            break

    # Penulis (baris dengan angka atau karakter khusus seperti *)
    for line in lines[1:10]:  # Biasanya nama penulis ada di awal
        if re.search(r"\d|\*", line):
            metadata["Penulis"] = line.strip()
            break

    # Tahun Terbit (angka 4 digit dalam teks)
    tahun_match = re.search(r"\b(19|20)\d{2}\b", text)
    if tahun_match:
        metadata["Tahun Terbit"] = tahun_match.group()

    return metadata

# Fungsi ekstrak teks dari PDF
def extract_text_from_pdf(pdf_file):
    """Ekstraksi teks dari PDF"""
    with fitz.open(stream=pdf_file.read(), filetype="pdf") as doc:
        text = "\n".join([page.get_text("text") for page in doc])
    return text.strip()

# Fungsi ringkasan AI dengan Google Gemini (terstruktur)
def summarize_text(text):
    """Menggunakan Google Gemini AI untuk merangkum teks artikel dalam 4 bagian"""
    model = genai.GenerativeModel("gemini-pro")
    prompt = f"""
    Buat ringkasan terstruktur dari artikel ilmiah berikut dengan format:
    
    **Pendahuluan / Latar Belakang / Tujuan:**  
    (Jelaskan secara singkat tujuan dan latar belakang penelitian)
    
    **Studi Literatur / Metode:**  
    (Jelaskan pendekatan atau metode penelitian yang digunakan)
    
    **Hasil / Pembahasan:**  
    (Jelaskan hasil yang ditemukan dan interpretasinya)
    
    **Kesimpulan:**  
    (Simpulkan temuan utama dan implikasinya)

    Artikel Ilmiah:  
    {text}
    """
    
    response = model.generate_content(prompt)
    
    return response.text if response and response.text else "Ringkasan tidak dapat dibuat."

# UI Streamlit
st.set_page_config(page_title="AI Ringkasan PDF", layout="centered")

st.title("📄 AI Ringkasan Otomatis dari PDF")
st.write("Unggah artikel ilmiah dalam format PDF, dan sistem akan menampilkan metadata serta ringkasan otomatis menggunakan **Google Gemini AI**.")

# Upload file PDF
uploaded_file = st.file_uploader("Unggah file PDF", type=["pdf"])

if uploaded_file:
    st.success("📂 File berhasil diunggah! Memproses...")

    # Ekstrak teks dari PDF
    with st.spinner("📖 Mengekstrak teks dari PDF..."):
        extracted_text = extract_text_from_pdf(uploaded_file)

    # Ekstrak metadata dari teks
    with st.spinner("📋 Mengekstrak metadata jurnal..."):
        metadata = extract_metadata_from_text(extracted_text)

    # Tampilkan metadata jika tersedia
    if metadata:
        st.subheader("📌 Metadata Jurnal")
        for key, value in metadata.items():
            st.write(f"**{key}:** {value}")

    # Tampilkan teks asli jika diinginkan
    with st.expander("📜 Lihat teks asli dari PDF"):
        st.text_area("Teks Asli", extracted_text, height=300)

    # Buat ringkasan
    if st.button("🔍 Buat Ringkasan"):
        with st.spinner("🤖 Menghasilkan ringkasan dengan AI..."):
            summary = summarize_text(extracted_text)
        st.subheader("📌 Ringkasan Terstruktur:")
        st.markdown(summary, unsafe_allow_html=True)

st.sidebar.markdown("🔹 **Dibuat dengan Streamlit & Google Gemini AI**")
st.sidebar.markdown("📌 **Fitur:**")
st.sidebar.markdown("- Upload PDF 📂")
st.sidebar.markdown("- Ekstraksi metadata jurnal 📘")
st.sidebar.markdown("- Ekstraksi teks dari PDF 📖")
st.sidebar.markdown("- Ringkasan otomatis dengan AI 🤖 (terstruktur)")
