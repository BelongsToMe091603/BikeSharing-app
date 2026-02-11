# 🚲 Bike Sharing Dashboard

Dashboard analisis data Bike Sharing menggunakan Streamlit.

---

## 📦 Setup Environment (Shell/Terminal)

### 1️⃣ Clone Repository

```bash
git clone https://github.com/username/nama-repo.git
cd nama-repo
```

### 2️⃣ Buat Virtual Environment (Opsional tapi disarankan)

```bash
python -m venv venv
```

Aktifkan virtual environment:

**Windows:**
```bash
venv\Scripts\activate
```

**Mac/Linux:**
```bash
source venv/bin/activate
```

### 3️⃣ Install Dependencies

Pastikan sudah ada file `requirements.txt`, lalu jalankan:

```bash
pip install -r requirements.txt
```

---

## ▶️ Run Streamlit App

Masuk ke folder dashboard (jika perlu):

```bash
cd dashboard
```

Jalankan aplikasi:

```bash
streamlit run dashboard.py
```

Jika berhasil, akan muncul tampilan seperti ini:

```
Local URL: http://localhost:8501
```

Buka link tersebut di browser.

---

## 📊 Features

- Peak hour rental analysis
- Casual vs Registered comparison
- Monthly rental trends
- Bike recommendation system (rule-based)
- Interactive dashboard filter

---

## 🛠 Tech Stack

- Python
- Pandas
- Seaborn
- Matplotlib
- Streamlit
