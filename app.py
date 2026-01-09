from flask import Flask, request, jsonify, send_from_directory
from flask_cors import CORS
import sqlite3
import datetime
import os

# Configure app to serve static files from the current directory
app = Flask(__name__, static_url_path='', static_folder='.')
CORS(app)  # Enable CORS for frontend

DB_NAME = 'civic_sense.db'

def get_db_connection():
    conn = sqlite3.connect(DB_NAME)
    conn.row_factory = sqlite3.Row
    return conn

# --- Frontend Routes ---

@app.route('/')
def index():
    # Serve index.html as the landing page
    return send_from_directory('.', 'index.html')

@app.route('/<path:path>')
def serve_static(path):
    return send_from_directory('.', path)

# --- API Routes ---

@app.route('/register', methods=['POST'])
def register():
    data = request.json
    user_id = data.get('id')
    password = data.get('password')
    name = data.get('name')
    email = data.get('email') # Added email
    role = data.get('role')
    domain = data.get('domain') # Optional, for admins

    if not all([user_id, password, name, role]):
        return jsonify({'error': 'Missing fields'}), 400

    conn = get_db_connection()
    try:
        conn.execute('INSERT INTO users (id, password, name, email, role, domain) VALUES (?, ?, ?, ?, ?, ?)',
                     (user_id, password, name, email, role, domain))
        conn.commit()
    except sqlite3.IntegrityError:
        conn.close()
        return jsonify({'error': 'User ID already exists'}), 409
    
    conn.close()
    return jsonify({'message': 'Registration successful'}), 201

@app.route('/login', methods=['POST'])
def login():
    data = request.json
    user_id = data.get('id')
    password = data.get('password')
    role = data.get('role') # Optional verification

    conn = get_db_connection()
    user = conn.execute('SELECT * FROM users WHERE id = ? AND password = ?', (user_id, password)).fetchone()
    conn.close()

    if user:
        if role and user['role'] != role:
             return jsonify({'error': 'Role mismatch'}), 403
             
        return jsonify({
            'message': 'Login successful',
            'user': {
                'id': user['id'],
                'name': user['name'],
                'role': user['role'],
                'domain': user['domain']
            }
        }), 200
    else:
        return jsonify({'error': 'Invalid credentials'}), 401

@app.route('/forgot-password', methods=['POST'])
def forgot_password():
    data = request.json
    email = data.get('email')
    
    if not email:
        return jsonify({'error': 'Email is required'}), 400
        
    conn = get_db_connection()
    # In a real app, we would verify against ID too if provided, but email-only is common
    user = conn.execute('SELECT * FROM users WHERE email = ?', (email,)).fetchone()
    conn.close()
    
    if user:
        # SIMULATION: In a real app, send email here.
        # For this hackathon/demo, we return success and log it.
        print(f"PASSWORD RECOVERY for {email}: Password is '{user['password']}'")
        return jsonify({'message': f'Password sent to {email}'}), 200
    else:
        # Security practice: Don't explicitly reveal if email exists, but for this internal tool it helps
        return jsonify({'error': 'Email not registered'}), 404

@app.route('/api/reports', methods=['GET', 'POST'])
def handle_reports():
    conn = get_db_connection()
    
    if request.method == 'POST':
        data = request.json
        student_id = data.get('student_id')
        report_type = data.get('type')
        location = data.get('location')
        description = data.get('description')
        image_url = data.get('image') # Base64 string usually
        date = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")

        conn.execute('INSERT INTO reports (student_id, type, location, description, image_url, status, date) VALUES (?, ?, ?, ?, ?, ?, ?)',
                     (student_id, report_type, location, description, image_url, 'Pending', date))
        conn.commit()
        conn.close()
        return jsonify({'message': 'Report submitted successfully'}), 201

    elif request.method == 'GET':
        student_id = request.args.get('student_id')
        admin_domain = request.args.get('domain')
        
        query = 'SELECT * FROM reports'
        params = []
        
        if student_id:
            query += ' WHERE student_id = ?'
            params.append(student_id)
        elif admin_domain:
            if admin_domain in ['Cleanliness', 'Maintenance']:
                query += ' WHERE type = ?'
                params.append(admin_domain)
            elif admin_domain != 'All Reports':
                query += ' WHERE location = ?'
                params.append(admin_domain)
        
        query += ' ORDER BY date DESC'
        
        reports = conn.execute(query, params).fetchall()
        conn.close()
        
        reports_list = [dict(row) for row in reports]
        return jsonify(reports_list), 200

@app.route('/api/reports/<int:report_id>', methods=['PUT', 'DELETE'])
def update_report(report_id):
    conn = get_db_connection()
    
    if request.method == 'DELETE':
         conn.execute('DELETE FROM reports WHERE id = ?', (report_id,))
         conn.commit()
         conn.close()
         return jsonify({'message': 'Report deleted'}), 200
         
    if request.method == 'PUT':
        data = request.json
        new_status = data.get('status')
        
        if new_status:
            resolved_date = None
            if new_status == 'Resolved':
                resolved_date = datetime.datetime.now().strftime("%Y-%m-%d")
                conn.execute('UPDATE reports SET status = ?, resolved_date = ? WHERE id = ?', (new_status, resolved_date, report_id))
            else:
                conn.execute('UPDATE reports SET status = ? WHERE id = ?', (new_status, report_id))
            
            conn.commit()
            conn.close()
            return jsonify({'message': 'Status updated'}), 200
            
    return jsonify({'error': 'Invalid request'}), 400

if __name__ == '__main__':
    app.run(debug=True, port=5000)
