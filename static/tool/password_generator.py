# Mengimpor fungsi generate_password_hash dari modul werkzeug.security
# Fungsi ini digunakan untuk membuat hash password yang aman untuk disimpan di database.
from werkzeug.security import generate_password_hash

# Fungsi untuk membuat hash dari sebuah password
def create_password_hash(password):
    # Hash password menggunakan fungsi generate_password_hash
    # Fungsi ini menggunakan algoritma hashing yang kuat (default menggunakan PBKDF2).
    hashed_password = generate_password_hash(password)
    # Mengembalikan hash password
    return hashed_password

# Penggunaan contoh fungsi hashing
if __name__ == '__main__':
    # Meminta pengguna untuk memasukkan password
    password = input("Masukkan password yang ingin di-hash: ")
    # Memanggil fungsi untuk membuat hash password
    hashed_password = create_password_hash(password)
    # Menampilkan hasil hash yang dihasilkan ke pengguna
    print("Hash password yang dihasilkan:", hashed_password)
