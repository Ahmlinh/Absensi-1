from flask import Flask, render_template, request, redirect, url_for
from datetime import datetime
import os
from supabase import create_client, Client
from dotenv import load_dotenv
import pytz

# Load environment variables
load_dotenv()

app = Flask(__name__)
app.secret_key = os.environ.get('SECRET_KEY', 'absensi-secret-key-2024')

# Initialize Supabase client dengan credentials Anda
def get_supabase_client():
    url: str = os.environ.get("SUPABASE_URL")
    key: str = os.environ.get("SUPABASE_KEY")
    
    if not url or not key:
        raise Exception("Supabase credentials not found. Please check your .env file")
    
    print(f"Connecting to Supabase: {url}")
    return create_client(url, key)

# Cek apakah sudah absen hari ini
def sudah_absen_hari_ini(user_id):
    try:
        supabase = get_supabase_client()
        
        # Get today's date in Asia/Jakarta timezone
        tz = pytz.timezone('Asia/Jakarta')
        today_start = datetime.now(tz).strftime('%Y-%m-%d 00:00:00')
        today_end = datetime.now(tz).strftime('%Y-%m-%d 23:59:59')
        
        print(f"Checking attendance for {user_id} on {today_start}")
        
        # Query database untuk cek absensi hari ini
        response = supabase.table('absensi') \
            .select('*') \
            .eq('user_id', user_id) \
            .gte('waktu', today_start) \
            .lte('waktu', today_end) \
            .execute()
        
        print(f"Found {len(response.data)} records for today")
        return len(response.data) > 0
        
    except Exception as e:
        print(f"Error checking attendance: {e}")
        return False

@app.route('/')
def home():
    return redirect(url_for('absen'))

@app.route('/absen')
def absen():
    user_id = request.args.get('id', '').strip()
    
    if not user_id:
        return render_template('absen.html', 
                             status='error',
                             message='❌ Parameter ID tidak ditemukan. Pastikan QR code valid.')
    
    print(f"Attendance attempt for user: {user_id}")
    
    # Cek apakah sudah absen hari ini
    if sudah_absen_hari_ini(user_id):
        return render_template('absen.html', 
                             status='already',
                             message='⚠️ Kamu sudah melakukan absensi hari ini.',
                             user_id=user_id)
    
    # Simpan data absensi ke Supabase
    try:
        supabase = get_supabase_client()
        
        # Get current time in Asia/Jakarta timezone
        tz = pytz.timezone('Asia/Jakarta')
        waktu_sekarang = datetime.now(tz)
        waktu_str = waktu_sekarang.strftime('%Y-%m-%d %H:%M:%S')
        tanggal_str = waktu_sekarang.strftime('%d %B %Y')
        jam_str = waktu_sekarang.strftime('%H:%M:%S')
        
        print(f"Saving attendance for {user_id} at {waktu_str}")
        
        # Data untuk disimpan
        data = {
            'user_id': user_id,
            'nama': user_id,  # Bisa diganti dengan lookup table nanti
            'waktu': waktu_str,
            'status': 'Hadir'
        }
        
        # Insert ke Supabase
        response = supabase.table('absensi').insert(data).execute()
        
        if response.data:
            print(f"Attendance saved successfully for {user_id}")
            return render_template('absen.html',
                                 status='success',
                                 message='✅ Absensi Berhasil',
                                 waktu=waktu_str,
                                 tanggal=tanggal_str,
                                 jam=jam_str,
                                 user_id=user_id)
        else:
            print(f"Failed to save attendance for {user_id}")
            return render_template('absen.html',
                                 status='error',
                                 message='❌ Gagal menyimpan absensi. Silakan coba lagi.')
    
    except Exception as e:
        print(f"Error saving attendance: {e}")
        return render_template('absen.html',
                             status='error',
                             message='❌ Error sistem: Gagal menyimpan absensi. Silakan hubungi admin.')

@app.route('/rekap')
def rekap():
    try:
        supabase = get_supabase_client()
        
        print("Fetching all attendance records...")
        
        # Get semua data absensi, urutkan dari yang terbaru
        response = supabase.table('absensi') \
            .select('*') \
            .order('waktu', desc=True) \
            .execute()
        
        records = response.data
        print(f"Retrieved {len(records)} records")
        
        return render_template('rekap.html', records=records)
        
    except Exception as e:
        print(f"Error retrieving records: {e}")
        return render_template('rekap.html', 
                             records=[],
                             error='Gagal mengambil data dari database')

@app.route('/rekap/<user_id>')
def rekap_user(user_id):
    """Halaman rekap untuk user tertentu"""
    try:
        supabase = get_supabase_client()
        
        print(f"Fetching records for user: {user_id}")
        
        response = supabase.table('absensi') \
            .select('*') \
            .eq('user_id', user_id) \
            .order('waktu', desc=True) \
            .execute()
        
        records = response.data
        print(f"Retrieved {len(records)} records for {user_id}")
        
        return render_template('rekap.html', 
                             records=records,
                             user_filter=user_id)
        
    except Exception as e:
        print(f"Error retrieving user records: {e}")
        return render_template('rekap.html', 
                             records=[],
                             error=f'Gagal mengambil data untuk user {user_id}')

@app.route('/stats')
def stats():
    """Halaman statistik"""
    try:
        supabase = get_supabase_client()
        
        # Total absensi
        total_response = supabase.table('absensi') \
            .select('id', count='exact') \
            .execute()
        
        # Absensi hari ini
        tz = pytz.timezone('Asia/Jakarta')
        today_start = datetime.now(tz).strftime('%Y-%m-%d 00:00:00')
        today_end = datetime.now(tz).strftime('%Y-%m-%d 23:59:59')
        
        today_response = supabase.table('absensi') \
            .select('id', count='exact') \
            .gte('waktu', today_start) \
            .lte('waktu', today_end) \
            .execute()
        
        # Unique users
        users_response = supabase.table('absensi') \
            .select('user_id') \
            .execute()
        
        unique_users = len(set([user['user_id'] for user in users_response.data]))
        
        stats_data = {
            'total_absensi': total_response.count,
            'absensi_hari_ini': today_response.count,
            'unique_users': unique_users
        }
        
        return render_template('rekap.html', 
                             records=[],
                             stats=stats_data,
                             show_stats=True)
        
    except Exception as e:
        print(f"Error retrieving stats: {e}")
        return render_template('rekap.html', 
                             records=[],
                             error='Gagal mengambil statistik')

if __name__ == '__main__':
    # Check if Supabase credentials are available
    if not os.environ.get("SUPABASE_URL") or not os.environ.get("SUPABASE_KEY"):
        print("❌ ERROR: Supabase credentials not found!")
        print("Please make sure .env file exists with SUPABASE_URL and SUPABASE_KEY")
    else:
        print("✅ Supabase credentials found!")
        print("🚀 Starting Flask application...")
    
    port = int(os.environ.get('PORT', 5000))
    app.run(debug=True, host='0.0.0.0', port=port)