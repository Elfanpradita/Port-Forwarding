-----

# Flask Port Forwarding Dashboard 🚀

Sebuah dashboard web sederhana yang dibangun dengan **Flask** dan berjalan di **Docker** untuk mengelola aturan port forwarding (menggunakan `socat`) secara dinamis tanpa perlu mengakses terminal.

Proyek ini dirancang untuk mempermudah proses *exposing* layanan internal ke port tertentu, dengan manajemen yang terpusat dan persistensi data menggunakan MySQL.

-----

## ✨ Fitur Utama

  * **Antarmuka Web Dinamis:** Tambah, lihat, dan hapus aturan port forwarding secara *real-time* melalui browser.
  * **Sistem Login:** Mengamankan dashboard agar hanya bisa diakses oleh admin.
  * **Persistensi Database:** Semua aturan disimpan di database **MySQL** eksternal, sehingga data aman dan tidak akan hilang.
  * **Otomatis Aktif Saat Restart:** Aturan forwarding secara otomatis dijalankan kembali setiap kali server atau container di-restart.
  * **Mudah Dijalankan:** Dikelola sepenuhnya menggunakan **Docker Compose** untuk setup yang cepat dan terisolasi.

-----

## ⚙️ Teknologi yang Digunakan

  * **Backend:** Flask
  * **WSGI Server:** Gunicorn
  * **Database:** MySQL
  * **Containerization:** Docker & Docker Compose
  * **Core Forwarding:** `socat`

-----

## 🔧 Panduan Instalasi dan Setup

Berikut adalah cara untuk menjalankan proyek ini dari awal.

### 1\. Prasyarat

Pastikan Anda sudah menginstall perangkat lunak berikut di server Anda:

  * [Docker](https://docs.docker.com/engine/install/)
  * [Docker Compose](https://docs.docker.com/compose/install/)

### 2\. Buat Database

Login ke server MySQL Anda dan buat database baru untuk aplikasi ini.

```sql
CREATE DATABASE forwarding_db;
```

### 3\. Konfigurasi Lingkungan

Proyek ini menggunakan file `.env` untuk menyimpan konfigurasi database dan kredensial lainnya.

a. **Buat file `.env`** di dalam direktori utama proyek. Anda bisa menyalin dari contoh:

```bash
cp .env.example .env
```

*(Jika Anda tidak punya `.env.example`, cukup buat file baru bernama `.env`)*

b. **Isi file `.env`** tersebut dengan informasi koneksi ke database MySQL Anda:

```env
# /proyek-forwarding-docker/.env

# Kredensial untuk koneksi ke Database MySQL
DB_HOST=192.168.0.xx
DB_USER=root
DB_PASSWORD=xxxxxxxx
DB_NAME=forwarding_db
```

### 4\. Jalankan Aplikasi

Setelah semua konfigurasi selesai, jalankan aplikasi menggunakan Docker Compose.

a. Buka terminal di direktori utama proyek (`/proyek-forwarding-docker/`).

b. Jalankan perintah berikut untuk membangun image dan menjalankan container di background:

```bash
docker-compose up --build -d
```

  * `--build`: Diperlukan saat pertama kali menjalankan atau jika ada perubahan pada `Dockerfile` dan `requirements.txt`.
  * `-d`: Menjalankan container dalam mode *detached* (background).

-----

## 💻 Cara Menggunakan

1.  **Akses Dashboard**
    Buka browser dan navigasi ke alamat IP server Anda pada port 5000:
    `http://<IP_SERVER_ANDA>:5000`

2.  **Login**
    Gunakan kredensial default yang dibuat saat aplikasi pertama kali berjalan:

      * **Username:** `admin`
      * **Password:** `admin`

3.  **Kelola Aturan**

      * Gunakan formulir "Tambah Aturan Forwarding Baru" untuk membuat aturan baru.
      * Semua aturan yang aktif akan ditampilkan di tabel.
      * Klik tombol "Hapus" untuk menghentikan proses forwarding dan menghapus aturan dari database.

-----

## 📜 File Konfigurasi Tambahan

Untuk mempermudah, Anda bisa membuat file `  .env.example ` ini di proyek Anda agar orang lain tahu variabel apa saja yang dibutuhkan.

**File:** `.env.example`

```env
# Kredensial untuk koneksi ke Database MySQL
DB_HOST=
DB_USER=
DB_PASSWORD=
DB_NAME=
```
