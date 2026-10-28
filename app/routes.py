import os
from flask import render_template, url_for, redirect, request, current_app
from werkzeug.utils import secure_filename
from flask import current_app as app
from app import db
from app.models import User, Grievance
from app.utils.analytics import generate_city_insights

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in current_app.config['ALLOWED_EXTENSIONS']

@app.route('/')
def index():
    grievances = Grievance.query.order_by(Grievance.date_posted.desc()).all()
    return render_template('index.html', grievances=grievances)

@app.route('/submit', methods=['GET', 'POST'])
def submit_grievance():
    if request.method == 'POST':
        title = request.form.get('title')
        description = request.form.get('description')
        category = request.form.get('category')
        location = request.form.get('location')
        
        user = User.query.filter_by(username='citizen_user').first()
        if not user:
            user = User(username='citizen_user', role='citizen')
            db.session.add(user)
            db.session.commit()

        image_filename = None
        if 'image' in request.files:
            file = request.files['image']
            if file and file.filename != '' and allowed_file(file.filename):
                filename = secure_filename(file.filename)
                os.makedirs(current_app.config['UPLOAD_FOLDER'], exist_ok=True)
                file.save(os.path.join(current_app.config['UPLOAD_FOLDER'], filename))
                image_filename = filename

        new_grievance = Grievance(
            title=title,
            description=description,
            category=category,
            location=location,
            image_file=image_filename,
            author=user
        )
        
        db.session.add(new_grievance)
        db.session.commit()
        return redirect(url_for('index'))

    return render_template('submit.html')

@app.route('/analytics')
def analytics():
    insights = generate_city_insights()
    return render_template('analytics.html', insights=insights)

@app.route('/update_status/<int:id>', methods=['POST'])
def update_status(id):
    grievance = Grievance.query.get_or_404(id)
    new_status = request.form.get('status')
    if new_status in ['Pending', 'In Progress', 'Resolved']:
        grievance.status = new_status
        db.session.commit()
    return redirect(url_for('index'))