from flask import Flask, render_template, request, jsonify, session, redirect
from flask_cors import CORS
import os
import threading
import time
from datetime import datetime
import firebase_admin
from firebase_admin import credentials, auth
import qrcode

# Initialize Firebase
cred = credentials.Certificate("attendmax07-firebase-adminsdk-fbsvc-294d4f6521.json")
try:
    firebase_admin.initialize_app(cred)
except ValueError:
    # App already initialized
    pass

app = Flask(__name__)
app.secret_key = os.urandom(12)
CORS(app)

# Ensure the templates directory exists
os.makedirs('templates', exist_ok=True)
os.makedirs('static', exist_ok=True)
os.makedirs('static/css', exist_ok=True)
os.makedirs('static/js', exist_ok=True)
os.makedirs('static/qr_codes', exist_ok=True)

# Keep the existing QR code generation logic
current_qr_data = None
valid_qr_codes = set()

def generate_qr_codes():
    global current_qr_data
    while True:
        current_qr_data = f"ATTENDMAX_{datetime.now().strftime('%Y%m%d%H%M%S')}"
        valid_qr_codes.add(current_qr_data)
        if len(valid_qr_codes) > 1:
            old_code = next(iter(valid_qr_codes))
            valid_qr_codes.remove(old_code)
        time.sleep(15)

@app.route('/')
def home():
    return render_template('index.html')

@app.route('/about')
def about():
    return render_template('about.html')

@app.route('/login')
def login_page():
    return render_template('login.html')

@app.route('/get-qr-code')
def get_qr_code():
    return jsonify({'qr_data': current_qr_data})

@app.route('/auth/login', methods=['POST'])
def auth_login():
    try:
        data = request.get_json()
        if not data:
            print("No JSON data received")
            return jsonify({
                'status': 'error',
                'message': 'No data received'
            }), 400

        username = data.get('username')
        password = data.get('password')
        role = data.get('role')

        if not all([username, password, role]):
            print(f"Missing required fields: {data}")
            return jsonify({
                'status': 'error',
                'message': 'Missing required fields'
            }), 400

        print(f"Attempting login for user: {username} with role: {role}")
        
        try:
            user = auth.get_user_by_email(username)
            print(f"User found: {user.uid}")
            
            # Create a session for the user
            session['user_id'] = user.uid
            session['role'] = role
            session['email'] = username
            
            print(f"Session created for user: {session['user_id']}")
            
            return jsonify({
                'status': 'success',
                'message': 'Login successful',
                'role': role
            })
        except auth.UserNotFoundError as e:
            print(f"User not found error: {str(e)}")
            return jsonify({
                'status': 'error',
                'message': 'Invalid email or password'
            }), 401
            
    except Exception as e:
        print(f"Login error: {str(e)}")
        return jsonify({
            'status': 'error',
            'message': 'An error occurred during login'
        }), 500

@app.route('/admin/dashboard')
def admin_dashboard():
    if 'user_id' not in session or session.get('role') != 'admin':
        return redirect('/login')
    return render_template('admin_dashboard.html')

@app.route('/student/dashboard')
def student_dashboard():
    if 'user_id' not in session or session.get('role') != 'student':
        return redirect('/login')
    return render_template('student_dashboard.html')

# Admin API endpoints
@app.route('/api/admin/stats')
def admin_stats():
    if 'user_id' not in session or session.get('role') != 'admin':
        return jsonify({'error': 'Unauthorized'}), 401
    
    # Here you would typically fetch real stats from your database
    return jsonify({
        'totalStudents': len(auth.list_users().users),
        'todayAttendance': 0,  # Replace with actual count
        'activeSessions': 0  # Replace with actual count
    })

@app.route('/api/admin/recent-activity')
def admin_recent_activity():
    if 'user_id' not in session or session.get('role') != 'admin':
        return jsonify({'error': 'Unauthorized'}), 401
    
    # Here you would typically fetch real activity data from your database
    return jsonify({
        'activities': []  # Replace with actual activities
    })

@app.route('/api/admin/generate-qr', methods=['POST'])
def admin_generate_qr():
    if 'user_id' not in session or session.get('role') != 'admin':
        return jsonify({'error': 'Unauthorized'}), 401
    
    data = request.get_json()
    department = data.get('department')
    year = data.get('year')
    
    # Generate QR code
    qr = qrcode.QRCode(version=1, box_size=10, border=5)
    qr_data = f"{department}_{year}_{datetime.now().strftime('%Y%m%d%H%M%S')}"
    qr.add_data(qr_data)
    qr.make(fit=True)
    
    # Create QR code image
    qr_img = qr.make_image(fill_color="black", back_color="white")
    
    # Save QR code to static directory
    img_path = os.path.join('static', 'qr_codes', f'{qr_data}.png')
    os.makedirs(os.path.dirname(img_path), exist_ok=True)
    qr_img.save(img_path)
    
    return jsonify({
        'qrCodeUrl': f'/static/qr_codes/{qr_data}.png',
        'qrData': qr_data
    })

# Student API endpoints
@app.route('/api/student/stats')
def student_stats():
    if 'user_id' not in session or session.get('role') != 'student':
        return jsonify({'error': 'Unauthorized'}), 401
    
    # Here you would typically fetch real stats from your database
    return jsonify({
        'totalClasses': 0,  # Replace with actual count
        'classesAttended': 0  # Replace with actual count
    })

@app.route('/api/student/attendance-history')
def student_attendance_history():
    if 'user_id' not in session or session.get('role') != 'student':
        return jsonify({'error': 'Unauthorized'}), 401
    
    # Here you would typically fetch real attendance history from your database
    return jsonify({
        'history': []  # Replace with actual history
    })

@app.route('/api/student/mark-attendance', methods=['POST'])
def student_mark_attendance():
    if 'user_id' not in session or session.get('role') != 'student':
        return jsonify({'error': 'Unauthorized'}), 401
    
    data = request.get_json()
    qr_data = data.get('qrData')
    
    # Verify QR code and mark attendance
    # Here you would typically:
    # 1. Verify the QR code is valid and not expired
    # 2. Check if attendance hasn't already been marked
    # 3. Mark attendance in the database
    
    success = True  # Replace with actual verification result
    
    return jsonify({
        'success': success,
        'message': 'Attendance marked successfully' if success else 'Invalid QR code'
    })

@app.route('/logout')
def logout():
    session.clear()
    return redirect('/')

if __name__ == '__main__':
    # Start QR code generation in background
    qr_thread = threading.Thread(target=generate_qr_codes, daemon=True)
    qr_thread.start()
    
    app.run(debug=True)