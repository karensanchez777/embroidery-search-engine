import os
from flask import Blueprint, render_template, request, redirect, url_for, flash
from werkzeug.utils import secure_filename

from app.ocr import ABCNetPredictions
from app.db import insert_design, search_in_db

UPLOAD_FOLDER = 'uploads/'
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg'}

bp = Blueprint('main', __name__)

if not os.path.exists(UPLOAD_FOLDER):
    os.makedirs(UPLOAD_FOLDER)

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

@bp.route('/')
def home():
    return render_template('home.html')

@bp.route('/search', methods=['GET', 'POST'])
def search():
    results = []
    if request.method == 'POST':
        query = request.form.get('query', '')
        results = search_in_db(query)
    return render_template('home.html', results=results)

@bp.route('/admin')
def admin():
    message = request.args.get('msg', '')
    return render_template('admin.html', message=message)

@bp.route('/index', methods=['POST'])
def index():
    if 'image' not in request.files:
        flash('No file part')
        return redirect(url_for('main.admin', msg='No file uploaded'))
    
    file = request.files['image']
    if file.filename == '':
        return redirect(url_for('main.admin', msg='No file selected'))

    if file and allowed_file(file.filename):
        filename = secure_filename(file.filename)
        filepath = os.path.join(UPLOAD_FOLDER, filename)
        file.save(filepath)

        try:
            extracted_texts = ABCNetPredictions(filepath)
            design_text = ' '.join(extracted_texts)
            insert_design(filename, design_text)
            return redirect(url_for('main.admin', msg='Upload successful!'))
        except Exception as e:
            return redirect(url_for('main.admin', msg=f'Failed: {str(e)}'))
    else:
        return redirect(url_for('main.admin', msg='Invalid file type'))
