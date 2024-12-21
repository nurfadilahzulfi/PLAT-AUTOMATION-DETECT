from flask import Flask, render_template, request, redirect, url_for, Response, flash, send_from_directory
from flask_login import LoginManager, login_user, login_required, logout_user, current_user, UserMixin
import mysql.connector
from werkzeug.security import check_password_hash
import cv2
import numpy as np
import logging
import pytesseract
from PIL import Image
import os

# Inisialisasi aplikasi Flask
app = Flask(__name__)
app.config['SECRET_KEY'] = 'your_secret_key'  # Kunci rahasia untuk keamanan sesi Flask

# Konfigurasi database MySQL
db_config = {
    'host': 'localhost',     # Alamat host database
    'user': 'root',          # Username untuk koneksi database
    'password': '',          # Password database
    'database': 'platex'     # Nama database yang digunakan
}

# Konfigurasi logging untuk pencatatan aktivitas aplikasi
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

# Konfigurasi lokasi Tesseract OCR
pytesseract.pytesseract.tesseract_cmd = r'C:\Program Files\Tesseract-OCR\tesseract.exe'

# Direktori penyimpanan gambar dan teks hasil OCR
minArea = 500  # Area minimum untuk mendeteksi pelat nomor
image_folder = './data/images'  # Folder penyimpanan gambar asli
processed_image_folder = './data/processed_images'  # Folder penyimpanan gambar yang telah diproses
output_text_folder = './data/plates_text'  # Folder untuk menyimpan teks hasil OCR

# Membuat folder jika belum ada
os.makedirs(image_folder, exist_ok=True)
os.makedirs(processed_image_folder, exist_ok=True)
os.makedirs(output_text_folder, exist_ok=True)

# Pengaturan ukuran frame kamera
frameWidth = 1000  # Lebar frame kamera
frameHeight = 480  # Tinggi frame kamera

# Load Haar Cascade untuk mendeteksi pelat nomor kendaraan
cascade_path = "./static/tool/haarcascade_russian_plate_number.xml"
plateCascade = cv2.CascadeClassifier(cascade_path)  # Menggunakan file cascade untuk mendeteksi pelat

# Kelas User untuk mewakili data pengguna (dengan Flask-Login)
class User(UserMixin):
    def __init__(self, id, username, password, nama):
        self.id = id
        self.username = username
        self.password = password
        self.nama = nama

# Fungsi untuk menghubungkan ke database MySQL
def get_db_connection():
    try:
        connection = mysql.connector.connect(**db_config)  # Koneksi ke database
        if connection.is_connected():
            logging.info("Terhubung ke database MySQL.")
        return connection
    except mysql.connector.Error as e:
        logging.error(f"Tidak Terhubung ke database MySQL: {e}")
        return None

# Fungsi untuk mendapatkan data pengguna berdasarkan ID
def get_user_by_id(user_id):
    conn = get_db_connection()
    if conn:
        try:
            cursor = conn.cursor(dictionary=True)  # Menggunakan cursor dengan hasil berupa dictionary
            cursor.execute("SELECT * FROM users WHERE id = %s", (user_id,))  # Query untuk mendapatkan user
            user_data = cursor.fetchone()  # Ambil data user
            cursor.close()
            conn.close()
            if user_data:  # Jika data user ditemukan, buat instance User
                return User(
                    id=user_data['id'],
                    username=user_data['username'],
                    password=user_data['password'],
                    nama=user_data['nama']
                )
        except mysql.connector.Error as e:
            logging.error(f"Error: {e}")
    return None  # Kembalikan None jika tidak ditemukan

# Fungsi untuk mendapatkan data pengguna berdasarkan username
def get_user_by_username(username):
    conn = get_db_connection()
    if conn:
        try:
            cursor = conn.cursor(dictionary=True)
            cursor.execute("SELECT * FROM users WHERE username = %s", (username,))
            user_data = cursor.fetchone()
            cursor.close()
            conn.close()
            if user_data:
                return User(
                    id=user_data['id'],
                    username=user_data['username'],
                    password=user_data['password'],
                    nama=user_data['nama']
                )
        except mysql.connector.Error as e:
            logging.error(f"Error: {e}")
    return None

# Setup Flask-Login untuk autentikasi
login_manager = LoginManager()  # Inisialisasi LoginManager
login_manager.login_view = 'login'  # Menentukan halaman login default
login_manager.init_app(app)  # Menghubungkan LoginManager ke aplikasi Flask

# Fungsi untuk memuat pengguna berdasarkan ID (diperlukan oleh Flask-Login)
@login_manager.user_loader
def load_user(user_id):
    return get_user_by_id(user_id)  # Memanggil fungsi untuk mendapatkan pengguna berdasarkan ID

# Rute halaman utama (mengalihkan langsung ke login)
@app.route('/')
def index():
    return redirect(url_for('login'))  # Halaman utama diarahkan ke halaman login

# Rute untuk login
@app.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:  # Jika sudah login
        return redirect(url_for('dashboard'))  # Arahkan ke dashboard

    if request.method == 'POST':  # Jika form login dikirimkan
        username = request.form.get('username')  # Ambil username dari form
        password = request.form.get('password')  # Ambil password dari form

        user = get_user_by_username(username)  # Cari pengguna berdasarkan username
        if user and check_password_hash(user.password, password):  # Verifikasi password
            login_user(user)  # Login pengguna
            return redirect(url_for('dashboard'))  # Arahkan ke dashboard setelah login berhasil
        else:
            flash("Invalid username or password", "error")  # Pesan error jika login gagal

    return render_template('login.html')  # Tampilkan halaman login

# Rute untuk dashboard (hanya bisa diakses setelah login)
@app.route('/dashboard')
@login_required
def dashboard():
    return render_template('dashboard.html', name=current_user.nama)  # Tampilkan halaman dashboard

# Rute untuk halaman kamera
@app.route('/camera')
@login_required
def camera():
    return render_template('camera.html', name=current_user.nama)  # Tampilkan halaman kamera

# Fungsi untuk menghasilkan frame video secara langsung
def generate_frames():
    cap = cv2.VideoCapture(0)  # Membuka kamera
    cap.set(3, frameWidth)  # Atur lebar frame
    cap.set(4, frameHeight)  # Atur tinggi frame
    cap.set(10, 150)  # Atur kecerahan
    count = 0  # Counter untuk menyimpan gambar

    while True:
        success, frame = cap.read()  # Membaca frame dari kamera
        if not success:  # Jika gagal membaca frame, keluar dari loop
            break

        # Deteksi pelat nomor menggunakan Haar Cascade
        imgGray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)  # Konversi ke grayscale
        imgBlur = cv2.GaussianBlur(imgGray, (5, 5), 0)  # Aplikasi blur untuk mengurangi noise
        numberPlates = plateCascade.detectMultiScale(imgBlur, 1.1, 4)  # Deteksi pelat nomor

        for (x, y, w, h) in numberPlates:
            cv2.rectangle(frame, (x, y), (x + w, y + h), (255, 0, 0), 2)  # Gambar kotak di sekitar pelat nomor
            cv2.putText(frame, "Number Plate", (x, y - 5), cv2.FONT_HERSHEY_COMPLEX, 1, (0, 0, 255), 2)

            # Ambil area pelat nomor (ROI)
            imgRoi = frame[y:y + h, x:x + w]

            # Simpan gambar pelat nomor
            plate_img_path = os.path.join(image_folder, f"plate_{str(count)}.jpg")
            cv2.imwrite(plate_img_path, imgRoi)

            # Preprocessing untuk OCR
            imgRoi_gray = cv2.cvtColor(imgRoi, cv2.COLOR_BGR2GRAY)
            _, imgRoi_thresh = cv2.threshold(imgRoi_gray, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)

            # Simpan gambar yang sudah diproses
            processed_plate_path = os.path.join(processed_image_folder, f"processed_plate_{str(count)}.jpg")
            cv2.imwrite(processed_plate_path, imgRoi_thresh)

            try:
                # Ekstraksi teks dari pelat nomor menggunakan OCR
                pil_img = Image.fromarray(imgRoi_thresh)
                plate_text = pytesseract.image_to_string(pil_img, config='--psm 6 -c tessedit_char_whitelist=ABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789')
                plate_text = plate_text.strip().replace('\n', '').replace('\r', '')

                if plate_text:
                    # Simpan teks ke file
                    text_file_path = os.path.join(output_text_folder, f"plate_{str(count)}.txt")
                    with open(text_file_path, 'w') as f:
                        f.write(plate_text)

                    # Simpan teks ke database
                    conn = get_db_connection()
                    if conn:
                        try:
                            cursor = conn.cursor()
                            cursor.execute("INSERT INTO plates (plate_text) VALUES (%s)", (plate_text,))
                            conn.commit()
                            logging.info(f"Plat nomor '{plate_text}' berhasil disimpan ke database.")
                        except mysql.connector.Error as e:
                            logging.error(f"Error saving plate to database: {e}")
                        finally:
                            cursor.close()
                            conn.close()

                    print(f"Plat nomor terdeteksi: {plate_text}")
                    print(f"Teks disimpan di: {text_file_path}")

            except Exception as e:
                print(f"Gagal mengekstrak teks: {e}")

            count += 1

            # Tampilkan teks pada frame
            cv2.putText(frame, plate_text, (x, y - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.9, (0, 255, 0), 2)

        # Encode frame untuk streaming
        _, buffer = cv2.imencode('.jpg', frame)
        frame = buffer.tobytes()

        # Kirim frame sebagai stream
        yield (b'--frame\r\n'
               b'Content-Type: image/jpeg\r\n\r\n' + frame + b'\r\n')

    cap.release()  # Tutup kamera

# Rute untuk streaming video langsung
@app.route('/video_feed')
@login_required
def video_feed():
    return Response(generate_frames(), mimetype='multipart/x-mixed-replace; boundary=frame')  # Stream video


# Rute untuk mengakses file gambar asli
@app.route('/images/<filename>')
def images(filename):
    # Mengembalikan file gambar dari folder `image_folder`
    return send_from_directory(image_folder, filename)

# Rute untuk mengakses file gambar yang telah diproses
@app.route('/processed_images/<filename>')
def processed_images(filename):
    # Mengembalikan file gambar dari folder `processed_image_folder`
    return send_from_directory(processed_image_folder, filename)

# Rute untuk halaman capture, yang menampilkan daftar gambar asli dan gambar hasil proses
@app.route('/capture')
@login_required  # Hanya dapat diakses oleh pengguna yang telah login
def capture():
    try:
        # Ambil daftar semua file dalam folder `image_folder` dan `processed_image_folder`
        image_files = os.listdir(image_folder)
        processed_image_files = os.listdir(processed_image_folder)

        # Filter hanya file dengan ekstensi gambar (.jpg, .png, .jpeg)
        image_files = [img for img in image_files if img.endswith(('.jpg', '.png', '.jpeg'))]
        processed_image_files = [img for img in processed_image_files if img.endswith(('.jpg', '.png', '.jpeg'))]

        # Buat URL untuk setiap file agar dapat diakses melalui rute Flask
        image_files = [f"/images/{img}" for img in image_files]
        processed_image_files = [f"/processed_images/{img}" for img in processed_image_files]

        # Render template `capture.html` dengan daftar gambar dan nama pengguna yang login
        return render_template('capture.html', name=current_user.nama, 
                               images=image_files, processed_images=processed_image_files)
    except Exception as e:
        # Log error jika ada masalah saat mengambil file gambar
        logging.error(f"Error fetching images: {e}")
        return f"Error: {str(e)}"  # Kembalikan pesan error ke pengguna

# Rute untuk halaman data, menampilkan daftar data pelat nomor dari database
@app.route('/data')
@login_required  # Hanya dapat diakses oleh pengguna yang telah login
def data():
    try:
        # Buat koneksi ke database
        conn = get_db_connection()
        if conn:
            # Mengambil data pelat nomor dari tabel `plates`
            cursor = conn.cursor(dictionary=True)
            cursor.execute("SELECT id, plate_text, detected_at FROM plates ORDER BY detected_at DESC")
            plates = cursor.fetchall()  # Ambil semua hasil query
            cursor.close()
            conn.close()

            # Render template `data.html` dengan daftar data pelat dan nama pengguna yang login
            return render_template('data.html', name=current_user.nama, plates=plates)
    except Exception as e:
        # Log error jika ada masalah saat mengambil data dari database
        logging.error(f"Error fetching plates data: {e}")
        flash("Unable to fetch data from database.", "error")  # Tampilkan pesan error ke pengguna
        # Render halaman dengan data kosong jika terjadi error
        return render_template('data.html', name=current_user.nama, plates=[])

# Rute untuk logout pengguna
@app.route('/logout')
@login_required  # Hanya dapat diakses oleh pengguna yang telah login
def logout():
    # Logout pengguna yang sedang login
    logout_user()
    # Arahkan kembali ke halaman login setelah logout
    return redirect(url_for('login'))

@app.after_request
def add_header(response):
    response.headers['Cache-Control'] = 'no-store, no-cache, must-revalidate, post-check=0, pre-check=0, max-age=0'
    response.headers['Pragma'] = 'no-cache'
    response.headers['Expires'] = '0'
    return response

# Main: Jalankan aplikasi Flask
if __name__ == '__main__':
    app.run(debug=True)  # Mode debug diaktifkan untuk mempermudah pengembangan