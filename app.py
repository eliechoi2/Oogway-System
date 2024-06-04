from flask import Flask, redirect, render_template, url_for, request
app = Flask(__name__, template_folder='template')
from models import db
import os


basedir = os.path.abspath(os.path.dirname(__file__))

app = Flask(__name__, template_folder='./templates')
# Initializing connection to database
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///' + os.path.join(basedir, 'oogway.db')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SECRET_KEY'] = 'OogwaySecretKey'
db.init_app(app)


#Authentication Routes
@app.route('/')
def login():
    return render_template('/admin-dashboard.html')

#Admin Routes
@app.route('/admin-dashboard')
def admin_dashboard():
    return render_template('/admin-dashboard.html')

@app.route('/admin-student-list-view')
def admin_student_list_view():
    return render_template('/admin-student-list-view.html')

@app.route('/admin-student-overall-view')
def admin_overall_view():
    return render_template('/admin-student-overall-view.html')

@app.route('/admin-student')
def admin_student():
    return render_template('/admin-student.html')

@app.route('/admin-floor')
def admin_floor():
    return render_template('/admin-floor.html')

#Student Routes
@app.route('/home')
def home():
    return render_template('/student-home.html')

if __name__ == '__main__':
    app.run(debug=True)


