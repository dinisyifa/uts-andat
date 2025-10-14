# 🎬 Movie Booking System (FastAPI)

## 📘 Deskripsi Proyek
Proyek ini merupakan sistem backend **reservasi tiket bioskop online** yang dikembangkan menggunakan **FastAPI**.  
Sistem ini memungkinkan:
- **Admin** untuk mengelola data film, studio, dan jadwal tayang (CRUD).
- **User** untuk melihat katalog film, memilih kursi, menambah tiket ke keranjang, dan melakukan checkout.

Proyek ini dibuat sebagai bagian dari **UTS Kapita Selekta Analitika Data**  
📚 Dosen Pengampu: *Levina Michella, S.Si., M.Si.*  
👥 Kelompok 3:
- Carens Callista (6162201027)
- Justine Theresia Mangindaan (6162201049)
- Dini Laila Syifa Az Zahra (6162201051)
- Tiffany Shafakaziyah Aditia (6162201084)
- Ludio Mae Olona (6162201097)

---

## ⚙️ Asumsi Sistem
1. Semua data disimpan di **memori (list Python)**, tanpa database eksternal.  
2. Harga tiket konstan: **Rp40.000**.  
3. Format waktu sederhana, misal `"120 menit"`.  
4. Terdapat 5 film, 5 jadwal tayang, dan 5 studio (masing-masing 96 kursi).  
5. Tidak ada autentikasi user.  
6. ID film & studio dibuat manual dan unik.  
7. 1 user hanya dapat membeli 1 kursi per transaksi.  
8. Sistem hanya berlaku untuk satu hari (tidak ada pemilihan tanggal tayang).

---

## 🧩 Desain dan Arsitektur
Struktur proyek bersifat **modular**, terdiri dari 4 modul utama di folder `app/routers`:
app/
├── routers/
│ ├── admin_film.py
│ ├── admin_jadwal.py
│ ├── user_catalog.py
│ └── user_transaction.py
├── models.py
├── main.py
└── storage.py

tests/
├── test_admin_film.py
├── test_admin_jadwal.py
├── test_user_catalog.py
└── test_user_transaction.py

- Modul **Admin** → mengelola film, studio, jadwal tayang  
- Modul **User** → menampilkan katalog film & menangani transaksi  

Semua endpoint dijalankan melalui `main.py` yang menggabungkan semua router menjadi satu aplikasi FastAPI.

---

## 🧱 Model Data
Beberapa model utama:
- **Film** → menyimpan info film (judul, durasi, genre, rating usia, harga)
- **Studio** → menyimpan info studio dan kapasitas kursi
- **Jadwal** → menghubungkan film dan studio di waktu tertentu
- **Katalog** → tampilan daftar film & jadwal untuk user
- **Keranjang & Transaksi** → mengelola tiket yang dipilih, checkout, dan booking code

---

## 🚀 Modul API

### 🛠️ Admin API
#### 1. Film Management (`/movies`)
- `GET /movies` → melihat semua film  
- `POST /movies` → menambah film  
- `PUT /movies/{id}` → memperbarui film  
- `DELETE /movies/{id}` → menghapus film  

#### 2. Studio Management (`/studios`)
- `GET /studios`
- `POST /studios`
- `PUT /studios/{id}`
- `DELETE /studios/{id}`

#### 3. Jadwal Management (`/schedules`)
- `GET /schedules` → lihat semua jadwal  
- `POST /schedules` → tambah jadwal  
- `PUT /schedules/{id}` → update jadwal  
- `DELETE /schedules/{id}` → hapus jadwal  

---

### 🎟️ User API
#### 1. Katalog Film
- `GET /now_playing` → daftar film tayang  
- `GET /movies/{id}/details` → detail film & jadwal  
- `GET /schedules/{id}/seats` → peta kursi studio  

#### 2. Transaksi & Checkout
- `POST /cart/add` → tambah tiket ke keranjang  
- `GET /cart` → lihat isi keranjang  
- `DELETE /cart/remove/{id}` → hapus tiket  
- `POST /checkout/payment` → mulai pembayaran  
- `GET /checkout/{order_id}/confirm` → konfirmasi transaksi  

---

## 🧪 Pengujian

### Pengujian Manual
Dilakukan menggunakan **Swagger UI** dan **Postman** untuk:
- Memastikan endpoint CRUD admin berfungsi (film, studio, jadwal)
- Memastikan alur user lengkap dari pemilihan film → kursi → checkout berjalan dengan benar  

### Unit Testing (pytest)
Framework: **pytest + FastAPI TestClient**  
Cakupan pengujian:
- CRUD Film & Studio  
- CRUD Jadwal  
- View katalog & kursi  
- Add to cart, remove cart, checkout  

Semua pengujian **✅ PASSED (100%)**