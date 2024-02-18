from datetime import datetime
import os
from flask import Flask, flash, redirect, render_template, request, url_for, send_from_directory
from flask_sqlalchemy import SQLAlchemy

basedir = os.path.abspath(os.path.dirname(__file__))

app = Flask(__name__)

app.config['SQLALCHEMY_DATABASE_URI'] = (
        f"sqlite:///{os.path.join(basedir, 'courses.db')}"
        )
db = SQLAlchemy(app)


class Professor(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(50), nullable=False)
    courses = db.relationship('Course', backref='professor', lazy=True)


class Course(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(50), nullable=False)
    description = db.Column(db.String(200), nullable=False)
    professor_id = db.Column(db.Integer, db.ForeignKey('professor.id'), nullable=False)
    semester = db.Column(db.String(50), nullable=False)

with app.app_context():
    db.create_all()

@app.route('/')
def home():
    return render_template('home.html')

@app.route('/media/<path:filename>')
def serve_media(filename):
    return send_from_directory(os.path.join(os.getcwd(), 'tmp'), filename)


@app.route('/courses', methods=['GET', 'POST'])
def index():
    if request.method == 'POST':
        name = request.form.get('name')
        description = request.form.get('description')
        professor_id = request.form.get('professor_id')
        semester_type = request.form.get('semester_type')
        semester_year = request.form.get('semester_year')

        if name and description and professor_id and semester_type and semester_year:
            semester = f"{semester_type} {semester_year}"
            course = Course(name=name, description=description,
                            professor_id=professor_id, semester=semester)
            db.session.add(course)
            db.session.commit()

        return redirect('/courses')
    else:
        courses = Course.query.all()
        professors = Professor.query.all()
        current_year = datetime.now().year
        return render_template('courses.html', courses=courses, professors=professors, current_year=current_year)


@app.route('/edit_course/<int:id>', methods=['GET', 'POST'])
def edit_course(id):
    course = Course.query.get_or_404(id)
    professors = Professor.query.all()  # Fetch all professors
    
    if request.method == 'POST':
        course.name = request.form['name']
        course.description = request.form['description']
        course.semester = request.form['semester']
        professor_id = request.form.get('professor_id')
        if professor_id:
            course.professor_id = professor_id
        else:
            return render_template('edit_course.html', course=course, professors=professors, message='The professor_id field is required.', current_year=current_year)
        try:
            db.session.commit()
            return redirect('/courses')
        except:
            return render_template('edit_course.html', course=course, professors=professors, message='There was an issue updating your course')
    else:
        return render_template('edit_course.html', course=course, professors=professors)


@app.route('/delete_course/<int:id>', methods=['GET', 'POST'])
def delete(id):
    course = Course.query.get(id)
    if course is None:
        return "Course not found", 404
    if request.method == 'POST':
        db.session.delete(course)
        db.session.commit()
        return redirect('/courses')
    return render_template('delete_course.html', course=course)


@app.route('/professors', methods=['GET', 'POST'])
def professors():
    if request.method == 'POST':
        name = request.form.get('name')

        if name:
            professor = Professor(name=name)
            db.session.add(professor)
            db.session.commit()
        return redirect(url_for('professors'))
    else:
        professors = Professor.query.all()
        return render_template('professors.html', professors=professors)

@app.route('/edit_professor/<int:id>', methods=['GET', 'POST'])
def edit_professor(id):
    professor = Professor.query.get(id)
    if professor is None:
        return "Professor not found", 404
    if request.method == 'POST':
        professor.name = request.form.get('name')
        db.session.commit()
        return redirect(url_for('professors'))
    return render_template('edit_professor.html', professor=professor)


@app.route('/delete_professor/<int:id>', methods=['GET','POST'])
def delete_professor(id):
    professor = Professor.query.get(id)
    error_message = None
    if professor:
        if professor.courses: # to work on later, not working yet
            error_message = 'Cannot delete professor. They are still assigned to a course.'
        else:
            if request.method == 'POST':
                db.session.delete(professor)
                db.session.commit()
                return redirect(url_for('professors'))
        return render_template('delete_professor.html', professor=professor, error_message=error_message)


if __name__ == '__main__':
    app.run(debug=True)