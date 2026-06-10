# Dashboard Sebaran Parameter Kualitas Air India

Dashboard ini dibuat menggunakan **Python dan Streamlit** untuk menampilkan sebaran lokasi/wilayah yang tercatat terdampak parameter kualitas air di India. Dashboard ditujukan sebagai alat bantu eksplorasi data dan bahan paparan kepada pimpinan/stakeholder.

## 1. Sumber Data

Dataset yang digunakan bersumber dari Kaggle:

**India Water Quality Data**  
https://www.kaggle.com/datasets/venkatramakrishnan/india-water-quality-data/data

File data utama yang digunakan dalam dashboard:

```text
IndiaAffectedWaterQualityAreas.csv
```

## 2. Tujuan Dashboard

Dashboard ini bertujuan untuk:

- Melihat jumlah lokasi terdampak berdasarkan parameter kualitas air.
- Mengidentifikasi negara bagian, distrik, desa, dan permukiman dengan jumlah lokasi terdampak terbanyak.
- Membandingkan sebaran parameter kualitas air seperti Iron, Salinity, Fluoride, Arsenic, dan Nitrate.
- Menyediakan ringkasan otomatis sebagai bahan awal pengambilan keputusan.
- Menyediakan tabel data dan file unduhan untuk analisis lanjutan.

## 3. Catatan Interpretasi

Dashboard ini menghitung **jumlah lokasi/wilayah yang tercatat terdampak** dalam dataset.

Angka yang ditampilkan **bukan menunjukkan kadar kimia air**, **bukan tingkat bahaya secara langsung**, dan **bukan status hukum pencemaran**. Untuk penetapan tingkat risiko atau status pencemaran, diperlukan data tambahan seperti kadar parameter, baku mutu, koordinat lokasi, jumlah penduduk terdampak, serta hasil uji laboratorium.

## 4. Struktur Folder

Pastikan struktur folder aplikasi seperti berikut:

```text
india_water_quality_streamlit_app_saja/
│
├── app.py
├── README.md
└── data/
    └── IndiaAffectedWaterQualityAreas.csv
```

## 5. Cara Menjalankan Dashboard

Buka terminal, Command Prompt, atau Anaconda Prompt, lalu masuk ke folder aplikasi:

```bash
cd india_water_quality_streamlit_app_saja
```

Jalankan dashboard dengan perintah:

```bash
streamlit run app.py
```

Setelah dijalankan, dashboard akan terbuka melalui browser.

## 6. Catatan Library

Aplikasi ini menggunakan library utama:

- streamlit
- pandas

Apabila muncul error bahwa Streamlit belum tersedia, install terlebih dahulu dengan:

```bash
pip install streamlit pandas
```

Setelah itu jalankan kembali:

```bash
streamlit run app.py
```

## 7. Fitur Dashboard

Dashboard terdiri dari beberapa bagian utama:

### Ringkasan Nasional

Menampilkan gambaran umum jumlah lokasi terdampak berdasarkan parameter kualitas air, negara bagian, dan tren tahunan.

### Analisis Wilayah

Menampilkan negara bagian, distrik, desa, dan permukiman dengan jumlah lokasi terdampak terbanyak.

### Parameter Kualitas Air

Menampilkan komposisi parameter kualitas air, negara bagian utama pada tiap parameter, dan tabel peta warna negara bagian terhadap parameter.

### Ringkasan Otomatis

Menampilkan narasi otomatis yang merangkum kondisi data berdasarkan filter yang dipilih.

### Tabel & Unduh Data

Menampilkan data hasil filter dan menyediakan tombol unduh untuk data detail maupun tabel ringkasan.

## 8. Filter yang Tersedia

Dashboard menyediakan filter berikut:

- Negara Bagian
- Distrik
- Parameter Kualitas Air
- Tahun
- Jumlah peringkat yang ditampilkan

Filter dapat dikosongkan untuk menampilkan seluruh data.

## 9. Pembersihan Data

Pembersihan data yang dilakukan dalam aplikasi meliputi:

- Penyeragaman huruf menjadi kapital.
- Penghapusan spasi berlebih.
- Pembacaan kolom tanggal dan tahun.
- Standardisasi nama negara bagian tertentu.
- Pemisahan nama distrik dan kode distrik bila tersedia.
- Penghapusan data duplikat.

## 10. Rekomendasi Pemanfaatan

Dashboard dapat digunakan untuk:

- Menentukan wilayah prioritas monitoring kualitas air.
- Mengidentifikasi parameter kualitas air yang paling sering tercatat.
- Menyusun bahan paparan berbasis data untuk pimpinan.
- Menyiapkan daftar lokasi prioritas untuk verifikasi lapangan.
- Menjadi dasar awal pengembangan dashboard kualitas air yang lebih lengkap.

## 11. Tindak Lanjut yang Disarankan

Berdasarkan hasil dashboard, tindak lanjut yang disarankan adalah:

- Fokus monitoring pada wilayah dengan jumlah lokasi terdampak terbanyak.
- Prioritaskan parameter Iron, Salinity, dan Fluoride karena paling banyak tercatat.
- Lakukan verifikasi lapangan dan uji laboratorium pada wilayah prioritas.
- Lengkapi data dengan kadar pencemar, baku mutu, koordinat lokasi, dan jumlah penduduk terdampak.
- Gunakan dashboard sebagai alat bantu pemantauan dan pengambilan keputusan.

## 12. Kredit

© 2026 Raihan Ferdyanza • Pusdatin KLH/BPLH
