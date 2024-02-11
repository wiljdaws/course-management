# app.py
import os
from flask import Flask, redirect, render_template, request, url_for
from flask_sqlalchemy import SQLAlchemy

basedir = os.path.abspath(os.path.dirname(__file__))

app = Flask(__name__)

app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///' + os.path.join(basedir, 'test.db')
db = SQLAlchemy(app)

class Course(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(50), nullable=False)
    description = db.Column(db.String(200), nullable=False)
    professor = db.Column(db.String(50), nullable=False)
    semester = db.Column(db.String(50), nullable=False)
    
    with app.app_context():
        db.create_all()

@app.route('/', methods=['GET', 'POST'])
def index():
    if request.method == 'POST':
        name = request.form.get('name')
        description = request.form.get('description')
        professor = request.form.get('professor')
        semester = request.form.get('semester')

        if name and description and professor and semester:
            course = Course(name=name, description=description, professor=professor, semester=semester)
            db.session.add(course)
            db.session.commit()

        return redirect('/')
    else:
        courses = Course.query.all()
        return render_template('index.html', courses=courses)
    
@app.route('/edit/<int:id>', methods=['GET', 'POST'])
def edit(id):
    course = Course.query.get(id)
    if course is None:
        return "Course not found", 404
    if request.method == 'POST':
        course.name = request.form.get('name')
        course.description = request.form.get('description')
        course.professor = request.form.get('professor')
        course.semester = request.form.get('semester')
        db.session.commit()
        return redirect(url_for('index'))
    return render_template('edit.html', course=course)

@app.route('/delete/<int:id>', methods=['GET', 'POST'])
def delete(id):
    course = Course.query.get(id)
    if course is None:
        return "Course not found", 404
    if request.method == 'POST':
        db.session.delete(course)
        db.session.commit()
        return redirect(url_for('index'))
    return render_template('delete.html', course=course)

if __name__ == '__main__':
    app.run(debug=True)

