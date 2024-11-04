from models import db, Student, Admin, Tasks, Floor, Collections, Student_Data
import os
from flask import Flask, jsonify, render_template, request, redirect, url_for, flash
from flask_login import LoginManager, login_user, login_required, logout_user, current_user
from werkzeug.security import generate_password_hash, check_password_hash
from models import User 
from authorize import role_required
from datetime import datetime as dt

basedir = os.path.abspath(os.path.dirname(__file__))

app = Flask(__name__, template_folder='template') 
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///' + os.path.join(basedir, 'oogway.db')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SECRET_KEY'] = b'oogway'


db.init_app(app)


login_supervisor = LoginManager()
login_supervisor.init_app(app)
login_supervisor.login_view = 'login'


@login_supervisor.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))  


@app.route('/')
def home():
    return redirect(url_for('login'))

@app.route('/admin-dashboard')
@login_required
@role_required(['ADMIN'])
def admin_dashboard():
    return render_template('admin-dashboard.html') 

@app.route('/supervisor-dashboard')
@login_required
@role_required(['supervisor'])
def supervisor_dashboard():
    return render_template('supervisor-dashboard.html') 


@app.route('/login', methods=['GET', 'POST'])
def login():
    admin_route_function = 'admin_dashboard'
    supervisor_route_function = 'supervisor_dashboard'
    student_route_function = 'student_home'

    if request.method == 'GET':
        if current_user and current_user.is_authenticated:
            if current_user.role == 'ADMIN':
                return redirect(url_for(admin_route_function))
            if current_user.role == 'supervisor':
                return redirect(url_for(supervisor_route_function))
            elif current_user.role == 'STUDENT':
                return redirect(url_for(student_route_function))
        else:
            redirect_route = request.args.get('next', None)  # Handle default case with None
            return render_template('login.html', redirect_route=redirect_route)

    elif request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        redirect_route = request.form.get('redirect_route')

        user = User.query.filter_by(username=username).first()

        if user and check_password_hash(user.password, password):
            login_user(user)
            if current_user.role == 'ADMIN':
                return redirect(redirect_route if redirect_route else url_for(admin_route_function))
            if current_user.role == 'supervisor':
                return redirect(redirect_route if redirect_route else url_for(supervisor_route_function))
            elif current_user.role == 'STUDENT':
                return redirect(redirect_route if redirect_route else url_for(student_route_function))
        else:
            flash('Your login information was not correct. Please try again.', 'error')
    return render_template('login.html')

@app.route('/logout')
@login_required
def logout():
    logout_user()
    flash(f'You have been logged out.', 'success')
    return redirect(url_for('home'))

# @app.route('/student-view/<int:student_id>')
# def student_viewers(student_id):
#     return render_template('student-viewer.html', student_id=student_id)

# supervisor Routes
@app.route('/supervisor-student-list-view')
def supervisor_student_list_view():
    students = Student.query.order_by(Student.student_lname, Student.student_fname).all()
    return render_template('supervisor-student-list-view.html', students=students)

@app.route('/supervisor-student-overall-view')
def supervisor_overall_view():
    return render_template('supervisor-student-overall-view.html')

@app.route('/supervisor-student')
def supervisor_student():
    return render_template('supervisor-student.html') 

@app.route('/supervisor-floor')
def supervisor_floor():
    return render_template('supervisor-floor.html') 

@app.route('/student/view/<int:student_id>')
@login_required
@role_required(['supervisor'])
def student_view(student_id):
    if current_user.role in ['supervisor']:
        student = Student.query.order_by(student_id=student_id.asc()).all()
        if student:
            return render_template('student-home.html', student=student, action='read')

        else:
            flash(f'Student attempting to be viewed could not be found!', 'error')
            return redirect(url_for('supervisor-student-list-view.html'))

    elif current_user.role == 'STUDENT':
        student = Student.query.filter_by(student_email=current_user.student_email).first()
        if student:
            return render_template('student-home.html', student=student, action='read')

        else:
            flash(f'Your record could not be located. Please contact advising.', 'error')
            return redirect(url_for('error'))

    else:
        flash(f'Invalid request. Please contact support if this problem persists.', 'error')
        return render_template('error.html')

#THIS IS COMPLETED MWAHAHAHA YEEEEE!!! just gotta style this page
@app.route('/student/create', methods=['GET', 'POST'])
@login_required
@role_required(['supervisor'])
def student_create():
    if request.method == 'GET':
        return render_template('supervisor-student-entry.html', action='create')
    elif request.method == 'POST':
        student_id = generate_student_id()
        student_fname = request.form['student_fname']
        student_lname = request.form['student_lname']
        student_email = request.form['student_email']
        student_username = request.form['student_username']
        student_password = request.form['student_password']

        student = Student(
            student_id=student_id,
            student_fname=student_fname,
            student_lname=student_lname, 
            student_email=student_email,
            student_username=student_username,
            student_password=student_password
        )
        db.session.add(student)
        db.session.commit()
        flash(f'{student_fname} {student_lname} was successfully added!', 'success')
        return redirect(url_for('supervisor_student_list_view'))

    flash(f'Invalid request. Please contact support if this problem persists.', 'error')
    return redirect(url_for('supervisor_student_list_view'))

def generate_student_id():
    last_student = Student.query.order_by(Student.student_id.desc()).first()
    if last_student:
        return str(int(last_student.student_id) + 1).zfill(10)  
    else:
        return '001' 

#IT WORKESSSEFES
@app.route('/student/update/<int:student_id>', methods=['GET', 'POST'])
@login_required
@role_required(['supervisor'])
def student_edit(student_id):
    if request.method == 'GET':
        student = Student.query.filter_by(student_id=student_id).first()

        if student:
            return render_template('supervisor-student-entry.html', student=student, action='update')

        else:
            flash(f'Student attempting to be edited could not be found!', 'error')

    elif request.method == 'POST':
        student = Student.query.filter_by(student_id=student_id).first()

        if student:
            student.student_fname = request.form['student_fname']
            student.student_lname = request.form['student_lname']
            student.student_email = request.form['student_email']
            student.student_username = request.form['student_username']
            student.student_password = request.form['student_password']

            db.session.commit()
            flash(f'{student.student_fname} {student.student_lname} was successfully updated!', 'success')
        else:
            flash(f'Student attempting to be edited could not be found!', 'error')

        return redirect(url_for('supervisor_student_list_view'))

    flash(f'Invalid request. Please contact support if this problem persists.', 'error')
    return redirect(url_for('supervisor_student_list_view'))

@app.route('/student/delete/<int:student_id>')
@login_required
@role_required(['supervisor'])
def student_delete(student_id):
    student = Student.query.filter_by(student_id=student_id).first()
    print(student_id)
    if student:
        db.session.delete(student)
        db.session.commit()
        flash(f'{student} was successfully deleted!', 'success')
    else:
        flash(f'Delete failed! Student could not be found.', 'error')

    return redirect(url_for('supervisor_student_list_view'))
    
    
@app.route('/supervisor-input-data', methods=['GET', 'POST'])
@login_required
@role_required(['supervisor'])
def supervisor_student_entry():
    if request.method == 'POST':
        # Retrieve form data
        student_id = request.form.get('student_id')
        task_id = request.form.get('task_id')
        total_shelfreads = int(request.form.get('total_shelfreads', 0))
        total_problem_items = int(request.form.get('total_problem_items', 0))
        total_in_house = int(request.form.get('total_in_house', 0))
        total_shelving = int(request.form.get('total_shelving', 0))
        total_holds_list = int(request.form.get('total_holds_list', 0))
        total_rm_list = int(request.form.get('total_rm_list', 0))

        # Create a new Student_Data record
        student_data = Student_Data(
            student_id=student_id,
            task_id=task_id,  # Associate the selected task ID
            total_shelfreads=total_shelfreads,
            total_problem_items=total_problem_items,
            total_in_house=total_in_house,
            total_shelving=total_shelving,
            total_holds_list=total_holds_list,
            total_rm_list=total_rm_list
        )
        db.session.add(student_data)
        db.session.commit()

        flash(f'Student data successfully added for student ID {student_id}', 'success')
        return redirect(url_for('supervisor_student_entry'))

    students = Student.query.all() 
    tasks = Tasks.query.all()
    floors = Floor.query.all()
    collections = Collections.query.all()
    return render_template('supervisor-input-data.html', students=students, tasks=tasks, floors=floors, collections=collections, action='create')

    
    
@app.route('/get_collections/<int:floor_id>', methods=['GET'])
@login_required
@role_required(['supervisor'])
def get_collections(floor_id):
    collections = Collections.query.filter_by(floor_id=floor_id).all()
    collections_list = [{'collection_id': col.collection_id, 'collection': col.collection} for col in collections]
    return jsonify(collections_list)


@app.route('/error')
def error():
    return render_template('error.html')

# Student Routes
@app.route('/student-home')
def student_home():
    return render_template('student-home.html')


if __name__ == '__main__':
    app.run(debug=True)

