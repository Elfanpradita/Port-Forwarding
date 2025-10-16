# /proyek-forwarding-docker/flask_app/app.py

import os
import subprocess
import signal
import socket
from flask import Flask, render_template, request, redirect, url_for, flash
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager, UserMixin, login_user, logout_user, login_required, current_user
from flask_bcrypt import Bcrypt

# --- Konfigurasi Aplikasi ---
app = Flask(__name__)
app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY', 'default-secret-key-change-me')

# AMBIL KREDENSIAL DB DARI ENVIRONMENT VARIABLES
db_user = os.environ.get('DB_USER')
db_password = os.environ.get('DB_PASSWORD')
db_host = os.environ.get('DB_HOST')
db_name = os.environ.get('DB_NAME')
default_user = os.getenv('DEFAULT_ADMIN_USER', 'admin')
default_pass = os.getenv('DEFAULT_ADMIN_PASS', 'admin')

# BUAT KONEKSI STRING UNTUK MySQL
# Format: mysql+pymysql://user:password@host/dbname
app.config['SQLALCHEMY_DATABASE_URI'] = f"mysql+pymysql://{db_user}:{db_password}@{db_host}/{db_name}"

app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)
bcrypt = Bcrypt(app)
login_manager = LoginManager(app)
login_manager.login_view = 'login'

# --- Model Database ---
class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    password = db.Column(db.String(120), nullable=False)

class ForwardingRule(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    listen_port = db.Column(db.Integer, nullable=False)
    target_ip = db.Column(db.String(100), nullable=False)
    target_port = db.Column(db.Integer, nullable=False)
    pid = db.Column(db.Integer, nullable=False) # Process ID dari socat
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

# --- Rute Aplikasi ---
@app.route('/')
def index():
    if current_user.is_authenticated:
        return redirect(url_for('dashboard'))
    return redirect(url_for('login'))

@app.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('dashboard'))
    if request.method == 'POST':
        user = User.query.filter_by(username=request.form['username']).first()
        if user and bcrypt.check_password_hash(user.password, request.form['password']):
            login_user(user)
            return redirect(url_for('dashboard'))
        else:
            flash('Login Gagal. Cek kembali username dan password.', 'danger')
    return render_template('login.html')

@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('login'))

@app.route('/dashboard')
@login_required
def dashboard():
    rules = ForwardingRule.query.filter_by(user_id=current_user.id).all()
    return render_template('dashboard.html', rules=rules)

@app.route('/add_rule', methods=['POST'])
@login_required
def add_rule():
    listen_port = request.form['listen_port']
    target_ip = request.form['target_ip']
    target_port = request.form['target_port']

    # Jalankan perintah socat di background
    command = f"socat TCP-LISTEN:{listen_port},fork TCP:{target_ip}:{target_port}"
    try:
        process = subprocess.Popen(command.split())
        
        # Simpan aturan ke database
        new_rule = ForwardingRule(
            listen_port=listen_port,
            target_ip=target_ip,
            target_port=target_port,
            pid=process.pid,
            user_id=current_user.id
        )
        db.session.add(new_rule)
        db.session.commit()
        flash('Aturan forwarding berhasil ditambahkan!', 'success')
    except Exception as e:
        flash(f'Gagal menambahkan aturan: {e}', 'danger')
        
    return redirect(url_for('dashboard'))

@app.route('/delete_rule/<int:rule_id>', methods=['POST'])
@login_required
def delete_rule(rule_id):
    rule = ForwardingRule.query.get_or_404(rule_id)
    if rule.user_id != current_user.id:
        flash('Tidak diizinkan menghapus aturan ini.', 'danger')
        return redirect(url_for('dashboard'))

    try:
        # Hentikan proses socat menggunakan PID
        os.kill(rule.pid, signal.SIGTERM)
        
        # Hapus dari database
        db.session.delete(rule)
        db.session.commit()
        flash('Aturan forwarding berhasil dihapus.', 'success')
    except ProcessLookupError:
        # Jika prosesnya sudah tidak ada, hapus saja dari DB
        db.session.delete(rule)
        db.session.commit()
        flash('Proses tidak ditemukan, aturan tetap dihapus dari database.', 'warning')
    except Exception as e:
        flash(f'Gagal menghapus aturan: {e}', 'danger')

    return redirect(url_for('dashboard'))


# --- Fungsi Inisialisasi ---
def initialize_app(app):
    with app.app_context():
        db.create_all()
        # Buat user default jika belum ada
        if not User.query.filter_by(username=default_user).first():
            hashed_password = bcrypt.generate_password_hash(default_pass).decode('utf-8')
            admin_user = User(username=default_user, password=hashed_password)
            db.session.add(admin_user)
            db.session.commit()
            print("User 'admin' dengan password 'admin' telah dibuat.")

        # --- LOGIKA STARTUP YANG DIPERBAIKI ---
        print("======================================================")
        print("Mencoba mengaktifkan kembali aturan forwarding dari database...")
        rules_to_reactivate = ForwardingRule.query.all()

        if not rules_to_reactivate:
            print("Tidak ada aturan untuk diaktifkan kembali.")
        
        for rule in rules_to_reactivate:
            # LANGSUNG COBA AKTIFKAN KEMBALI
            command = f"socat TCP-LISTEN:{rule.listen_port},fork TCP:{rule.target_ip}:{rule.target_port}"
            try:
                process = subprocess.Popen(command.split())
                # Jika berhasil, langsung update PID baru di database
                rule.pid = process.pid
                db.session.commit()
                print(f"-> Berhasil: port {rule.listen_port} -> {rule.target_ip}:{rule.target_port} (PID: {process.pid})")
            except Exception as e:
                # Jika gagal (misal port sudah dipakai proses lain), cukup cetak error
                # Jangan hapus aturannya, biarkan user yang memutuskan
                print(f"-> GAGAL mengaktifkan port {rule.listen_port}: {e}. Aturan tetap di database.")

        print("======================================================")


# Panggil fungsi inisialisasi
initialize_app(app)

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)