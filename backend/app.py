from flask import Flask, request, jsonify, send_file, session
from flask_cors import CORS
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager, UserMixin, login_user, logout_user, login_required, current_user
from werkzeug.security import generate_password_hash, check_password_hash

import datetime
import io
import matplotlib.pyplot as plt
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import letter
from reportlab.lib.utils import ImageReader
import pandas as pd

from backend.python_complexity import analyze_python_code
from backend.java_complexity import calculate_java_complexity
from backend.cpp_complexity import analyze_cpp_code
from backend.export_pdf import generate_pdf
from backend.export_csv import generate_csv  


# ------------------ App Setup ------------------ #
app = Flask(__name__)
app.secret_key = 'your_secret_key'
CORS(app, supports_credentials=True)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///complexity.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)


# ------------------ Flask-Login Setup ------------------ #
login_manager = LoginManager()
login_manager.init_app(app)


# ------------------ Models ------------------ #
class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(150), unique=True)
    password = db.Column(db.String(150))


class ComplexityResult(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    filename = db.Column(db.String(100))
    language = db.Column(db.String(50))
    dc = db.Column(db.Float)
    cc = db.Column(db.Float)
    code = db.Column(db.Text)
    timestamp = db.Column(db.DateTime, default=datetime.datetime.utcnow)


# ------------------ User Loader ------------------ #
@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))


# ------------------ Signup ------------------ #
@app.route('/signup', methods=['POST'])
def signup():
    email = request.form.get('email')
    password = request.form.get('password')
    if User.query.filter_by(email=email).first():
        return jsonify({'error': 'User already exists'}), 409
    hashed_password = generate_password_hash(password)
    new_user = User(email=email, password=hashed_password)
    db.session.add(new_user)
    db.session.commit()
    return jsonify({'message': 'User created successfully'}), 201


# ------------------ Login ------------------ #
@app.route('/login', methods=['POST'])
def login():
    email = request.form.get('email')
    password = request.form.get('password')
    user = User.query.filter_by(email=email).first()
    if user and check_password_hash(user.password, password):
        login_user(user)
        return jsonify({'message': 'Login successful'}), 200
    return jsonify({'error': 'Invalid credentials'}), 401


# ------------------ Logout ------------------ #
@app.route('/logout', methods=['POST'])
@login_required
def logout():
    logout_user()
    return jsonify({'message': 'Logged out'}), 200


# ------------------ Analyze Code ------------------ #
@app.route('/analyze', methods=['POST'])
@login_required
def analyze():
    data = request.get_json()
    code = data.get('code', '')
    language = data.get('language', '').lower()
    filename = data.get('filename', 'untitled')

    if not code:
        return jsonify({'error': 'No code submitted'}), 400

    try:
        line_dc_map = {}
        method_breakdown = {}
        class_breakdown = {}
        structure_summary = {}

        if language == 'python':
            result = analyze_python_code(code)
            dc = result['total_dc']
            cc = result['total_cc']
            line_dc_map = result['line_scores']
            method_breakdown = result['methods']
            class_breakdown = result['classes']
            structure_summary = result.get('structures', {})

        elif language == 'java':
            result = calculate_java_complexity(code)
            dc = result.get('decisional_complexity', 0)
            cc = result.get('cyclomatic_complexity', 0)
            line_dc_map = result.get('line_scores', {})
            method_breakdown = result.get('methods', {})
            class_breakdown = result.get('classes', {})
            structure_summary = result.get('structures', {})  

        elif language == 'c++':
            result = analyze_cpp_code(code)
            dc = result.get('decisional_complexity', 0)
            cc = result.get('cyclomatic_complexity', 0)
            line_dc_map = result.get('line_scores', {})
            method_breakdown = result.get('methods', {})
            class_breakdown = result.get('classes', {})
            structure_summary = result.get('structures', {})
              

        else:
            return jsonify({'error': 'Unsupported language'}), 400

        # Save to DB
        result_entry = ComplexityResult(
            user_id=current_user.id,
            filename=filename,
            language=language,
            dc=dc,
            cc=cc,
            code=code
        )
        db.session.add(result_entry)
        db.session.commit()

        # Save to session
        session['latest_result'] = {
            'filename': filename,
            'language': language,
            'dc': dc,
            'cc': cc,
            'code': code,
            'line_dc_map': line_dc_map
        }

        return jsonify({
            'dc': dc,
            'cc': cc,
            'line_dc_map': line_dc_map,
            'methods': method_breakdown,
            'classes': class_breakdown,
            'structures': structure_summary
        })

    except Exception as e:
        return jsonify({'error': str(e)}), 500



# ------------------ Reset Password ------------------ #
@app.route('/reset-password', methods=['POST'])
def reset_password():
    email = request.form.get('email')
    new_password = request.form.get('new_password')
    user = User.query.filter_by(email=email).first()
    if not user:
        return jsonify({'error': 'No account found with that email'}), 404
    user.password = generate_password_hash(new_password)
    db.session.commit()
    return jsonify({'message': 'Password reset successful!'}), 200


# ------------------ Get Submission History ------------------ #
@app.route('/history', methods=['GET'])
@login_required
def get_history():
    results = ComplexityResult.query.filter_by(user_id=current_user.id).order_by(ComplexityResult.timestamp.desc()).all()
    data = [
        {
            'filename': r.filename,
            'id': r.id, 
            'language': r.language,
            'dc': r.dc,
            'cc': r.cc,
            'code': r.code,
            'timestamp': r.timestamp.strftime("%Y-%m-%d %H:%M:%S")
        }
        for r in results
    ]
    return jsonify(data)


@app.route('/history/<int:entry_id>', methods=['DELETE'])
@login_required
def delete_entry(entry_id):
    entry = ComplexityResult.query.filter_by(id=entry_id, user_id=current_user.id).first()
    if not entry:
        return jsonify({'error': 'Entry not found'}), 404
    db.session.delete(entry)
    db.session.commit()
    return jsonify({'message': 'Deleted successfully'}), 200


# ------------------ CSV Export ------------------ #
@app.route('/download/csv', methods=['GET'])
@login_required
def download_csv():
    latest = session.get('latest_result')
    if not latest:
        return jsonify({'error': 'No recent analysis found'}), 400

    if 'line_dc_map' not in latest or not latest['line_dc_map']:
        code = latest.get('code', '')
        language = latest.get('language', '').lower()
        if language == 'python':
            result = analyze_python_code(code)
            line_dc_map = result['line_scores']
        elif language == 'java':
            result = calculate_java_complexity(code)
            line_dc_map = result.get('line_scores', {})
        elif language == 'c++':
            result = analyze_cpp_code(code)
            line_dc_map = result.get('line_scores', {})
        else:
            line_dc_map = {}
        latest['line_dc_map'] = line_dc_map

    csv_stream = generate_csv(latest)
    return send_file(
        csv_stream,
        mimetype='text/csv',
        as_attachment=True,
        download_name='complexity_report.csv'
    )


# ------------------ PDF Export ------------------ #
@app.route('/download/pdf', methods=['GET'])
@login_required
def download_pdf():
    latest = session.get('latest_result')
    if not latest:
        return jsonify({'error': 'No recent analysis found'}), 400

    if 'line_dc_map' not in latest or not latest['line_dc_map']:
        code = latest.get('code', '')
        language = latest.get('language', '').lower()
        if language == 'python':
            result = analyze_python_code(code)
            line_dc_map = result['line_scores']
        elif language == 'java':
            result = calculate_java_complexity(code)
            line_dc_map = result.get('line_scores', {})
        elif language == 'c++':
            result = analyze_cpp_code(code)
            line_dc_map = result.get('line_scores', {})
        else:
            line_dc_map = {}
        latest['line_dc_map'] = line_dc_map

    pdf_stream = generate_pdf(latest)
    return send_file(
        pdf_stream,
        as_attachment=True,
        download_name='complexity_report.pdf',
        mimetype='application/pdf'
    )


# ------------------ App Runner ------------------ #
def start():
    with app.app_context():
        db.create_all()

if __name__ == '__main__':
    start()
    app.run(debug=True, threaded=False)
