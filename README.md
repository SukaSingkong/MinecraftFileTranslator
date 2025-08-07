# Penerjemah File Properties & YAML Minecraft oleh Louis Bryan

Aplikasi desktop dengan antarmuka grafis (GUI) untuk menerjemahkan file konfigurasi Minecraft berformat `.properties` dan `.yaml` menggunakan [Argos Translate](https://www.argosopentech.com/). Aplikasi ini mendukung penerjemahan multi-threaded dengan kontrol penggunaan CPU dan pengelompokan batch, serta dioptimalkan untuk menjaga format warna Minecraft dan struktur YAML kompleks.

---

## ✨ Fitur Utama

- 🖼️ Antarmuka GUI yang mudah digunakan
- 🔍 Deteksi otomatis atau pilih tipe file secara manual (`.properties` atau `.yaml`)
- 🎨 Menjaga format khusus seperti:
  - Kode warna Minecraft (`&a`, `§c`, dll)
  - Placeholder (`%player%`, `{nama}`, `<tag>`, dll)
- 🌐 Terintegrasi dengan [Argos Translate](https://www.argosopentech.com/)
- 🧵 Mendukung multi-threading dengan pengaturan penggunaan CPU
- 📦 Penerjemahan dalam batch & penundaan antar permintaan yang dapat diatur
- 💾 Simpan dan muat pengaturan penerjemahan
- 📈 Tampilan progress bar dan log waktu nyata
- 📘 Panduan instalasi bahasa & tombol refresh bahasa
- 🌍 Mendukung lebih dari 70+ bahasa (berdasarkan paket yang diinstal)

---

## 📦 Download Siap Pakai (.EXE)

Tidak ingin repot install Python?

➡️ Langsung download versi `.exe` siap pakai dari halaman **[Releases](https://github.com/SukaSingkong/MinecraftFileTranslator/releases/tag/Release)**

**Langkah-langkah:**

1. Kunjungi tab [Releases](https://github.com/SukaSingkong/MinecraftFileTranslator/releases/tag/Release)
2. Download file bernama `v.X.X.X_Release.zip`
3. Extract File dan Jalankan Langsung — tidak perlu Python atau setup tambahan
4. (Opsional) Install bahasa di Argos Translate dan klik *Refresh Languages*

---

## 🧑‍💻 Instalasi Manual (opsional)

Jika kamu ingin menjalankan dari kode sumber:

1. **Clone repository ini**

```bash
git clone https://github.com/usernameanda/minecraft-translator-gui.git
cd minecraft-translator-gui
````

2. **Install semua dependensi**

Pastikan Python 3.8 ke atas sudah terpasang.

```bash
pip install -r requirements.txt
```

Atau install manual:

```bash
pip install argostranslate pyyaml psutil tqdm
```

3. **Pasang paket bahasa Argos Translate**

Contoh: untuk menerjemahkan dari Inggris ke Indonesia:

```bash
argos-translate --install-package en id
```

---

## 🚀 Cara Penggunaan

Jalankan aplikasi:

```bash
python main.py
```

Atau klik `minecraft-translator.exe` jika menggunakan versi release.

Langkah-langkah:

1. Pilih file `.properties` atau `.yaml` sumber
2. Pilih lokasi untuk file hasil
3. Pilih bahasa asal dan tujuan (contoh: `en` → `id`)
4. Atur performa jika perlu
5. Klik tombol **Start Translation**

---

## 📂 Dukungan Tipe File

| Tipe File        | Didukung | Catatan                                |
| ---------------- | -------- | -------------------------------------- |
| `.properties`    | ✅        | Format konfigurasi Minecraft klasik    |
| `.yaml` / `.yml` | ✅        | Mendukung struktur bertingkat dan list |

---

## ⚙️ Pengaturan Lanjutan

* **Batch Size**: Jumlah teks yang diterjemahkan dalam satu waktu
* **Delay**: Waktu jeda (detik) antar batch
* **Mode Penggunaan CPU**:

  * Persentase (misal: gunakan 50% dari core CPU)
  * Jumlah thread tetap (misal: 4 thread)

---

## 💬 Bahasa yang Didukung

Bahasa yang muncul tergantung pada paket bahasa yang telah diinstal melalui Argos Translate.

Untuk memasang bahasa lain:

```bash
argos-translate --install-package en ja  # Inggris ke Jepang
```

Klik tombol **Refresh Languages** di dalam aplikasi setelah menginstal paket baru.

---

## 📦 Packaging ke .exe (Pengembang)

Untuk membuat versi `.exe` (Windows):

```bash
pip install pyinstaller
pyinstaller main.py --noconsole --onefile
```

---

## 📄 Lisensi

Lisensi: **MIT**

---

## 👤 Pengembang

**Louis Bryan**
Mahasiswa Artificial Intelligence Bina Nusantara

---

## ⭐ Beri bintang jika project ini bermanfaat bagi workflow server Minecraft-mu!
