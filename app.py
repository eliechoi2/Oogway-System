from models import db, Student, Admin, Tasks, Floor, Collections, Student_Data, ShelfReading, Problem, ProblemList, Shelving
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


# supervisor Routes
@app.route('/supervisor-student-list-view')
def supervisor_student_list_view():
    students = Student.query.order_by(Student.student_id).all()
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
    
    
#supervisor input data 
# @app.route('/supervisor-input-data', methods=['GET', 'POST'])
# @login_required
# @role_required(['supervisor'])
# def supervisor_input_data():
#     tasks = Tasks.query.all()  # Retrieve all tasks from the database

#     if request.method == 'POST':
#         task_id = request.form.get('task_id')
#         # You can handle the task_id as needed here
#         return render_template('supervisor-input-data.html', tasks=tasks, task_id=task_id)

#     return render_template('supervisor-input-data.html', tasks=tasks)  # Render tasks in GET request


@app.route('/supervisor-input-data/<int:task_id>')
@login_required
@role_required(['supervisor'])
def supervisor_task_page(task_id):
    # You can perform any additional logic here if needed, e.g., retrieving task details
    return render_template(f'supervisor-input-data/{task_id}.html')  # Render the specific task page


@app.route('/supervisor-input-data', methods=['GET', 'POST'])
@login_required
@role_required(['supervisor'])
def supervisor_input_data():
    if request.method == 'POST':
        # Retrieve form data
        student_id = request.form.get('student_id')
        student_fname = request.form.get('student_fname')
        student_lname = request.form.get('student_lname')
        
        task_id = request.form.get('task_id')
        total_shelfreads = int(request.form.get('total_shelfreads', 0))
        total_problem_items = int(request.form.get('total_problem_items', 0))
        total_in_house = int(request.form.get('total_in_house', 0))
        total_shelving = int(request.form.get('total_shelving', 0))
        total_holds_list = int(request.form.get('total_holds_list', 0))
        total_rm_list = int(request.form.get('total_rm_list', 0))

        # Check if a record already exists
        student_data = Student_Data.query.filter_by(student_id=student_id, task_id=task_id).first()

        if student_data:
            # Update existing record
            student_data.total_shelfreads = total_shelfreads
            student_data.total_problem_items = total_problem_items
            student_data.total_in_house = total_in_house
            student_data.total_shelving = total_shelving
            student_data.total_holds_list = total_holds_list
            student_data.total_rm_list = total_rm_list
            flash(f'Student data successfully updated for student ID {student_id}', 'success')
        else:
            # Create a new Student_Data record
            student_data = Student_Data(
                student_id=student_id,
                task_id=task_id, 
                total_shelfreads=total_shelfreads,
                total_problem_items=total_problem_items,
                total_in_house=total_in_house,
                total_shelving=total_shelving,
                total_holds_list=total_holds_list,
                total_rm_list=total_rm_list
            )
            db.session.add(student_data)
            flash(f'Student data successfully added for student ID {student_id}', 'success')

        db.session.commit()
        return redirect(url_for('supervisor_input_data'))

    # If it's a GET request
    students = Student.query.all() 
    tasks = Tasks.query.all()
    floors = Floor.query.all()
    collections = Collections.query.all()
    return render_template('supervisor-input-data.html', students=students, tasks=tasks, floors=floors, collections=collections, action='create')



from datetime import datetime

#shelfreading
@app.route('/supervisor-input-data/1', methods=['GET', 'POST'])
@login_required
@role_required(['supervisor'])
def supervisor_input_data_1():
    if request.method == 'POST':
        # Retrieve form data
        student_id = request.form.get('student_id')
        date_string = request.form.get('date')
        date = datetime.strptime(date_string, '%Y-%m-%d').date()
        start_time_string = request.form.get('start_time')  # e.g., '2024-11-08 11:11:00'
        end_time_string = request.form.get('end_time')  # e.g., '2024-11-08 12:00:00'
        start_time = datetime.strptime(start_time_string, '%H:%M')
        end_time = datetime.strptime(end_time_string, '%H:%M')
        shelves_completed = int(request.form.get('shelves_completed'))
        start_call = request.form.get('start_call')
        end_call = request.form.get('end_call')
        floor_id = request.form.get('floor_id')
        
        # Create a new ShelfReading record
        new_shelf_reading = ShelfReading(
            date=date,
            start_time=start_time,
            end_time=end_time,
            shelves_completed=shelves_completed,
            start_call=start_call,
            end_call=end_call,
            student_id=student_id,
            floor_id=floor_id
        )

        # Add and commit to the database
        db.session.add(new_shelf_reading)
        db.session.commit()
        flash(f'Shelf reading record for student {student_id} added successfully!', 'success')
        return redirect(url_for('supervisor_input_data'))  # Replace 'some_view_name' with the appropriate route

    # GET request, load student and floor data
    students = Student.query.all()
    floors = Floor.query.all()

    # Log data for troubleshooting
    print("Students:", students)
    print("Floors:", floors)

    return render_template('supervisor-input-data/1.html', students=students, floors=floors)



#problem items
@app.route('/supervisor-input-data/2', methods=['GET', 'POST'])
@login_required
@role_required(['supervisor'])
def supervisor_input_data_2():
    if request.method == 'POST':
        # Retrieve form data
        student_id = request.form.get('student_id')
        date_string = request.form.get('date')
        date = datetime.strptime(date_string, '%Y-%m-%d').date()
        call_no = request.form.get('call_no')
        problem_id = request.form.get('problem_id')
        
        # Check if call_no is provided
        if not call_no:
            flash('Call number is required!', 'danger')
            return redirect(request.url)  # Redirect back to the form with error

        # Create a new Problem record
        problem = Problem(
            student_id=student_id,
            date=date,
            call_no=call_no,
            problem_id=problem_id
        )

        # Add and commit to the database
        db.session.add(problem)
        db.session.commit()
        flash(f'Problem item record for student {student_id} added successfully!', 'success')
        return redirect(url_for('supervisor_input_data'))  # Replace with appropriate route

    # GET request, load student and floor data
    students = Student.query.all()
    problems = Problem.query.all()
    problems_list = ProblemList.query.all()

    return render_template('supervisor-input-data/2.html', students=students, problems=problems, problems_list=problems_list)




#shelving
@app.route('/supervisor-input-data/4', methods=['GET', 'POST'])
@login_required
@role_required(['supervisor'])
def supervisor_input_data_4():
    if request.method == 'POST':
        # Retrieve form data
        student_id = request.form.get('student_id')
        date_string = request.form.get('date')
        date = datetime.strptime(date_string, '%Y-%m-%d').date()
        start_time_string = request.form.get('start_time')  # e.g., '2024-11-08 11:11:00'
        end_time_string = request.form.get('end_time')  # e.g., '2024-11-08 12:00:00'
        start_time = datetime.strptime(start_time_string, '%H:%M')
        end_time = datetime.strptime(end_time_string, '%H:%M')
        total_shelving = int(request.form.get('shelves_completed'))  # Represents the number of shelves completed
        start_call = request.form.get('start_call')
        end_call = request.form.get('end_call')
        floor_id = request.form.get('floor_id')
        collection_id = request.form.get('collection_id')
        
        # Create a new Shelving record
        new_shelving = Shelving(
            date=date,
            start_time=start_time,
            end_time=end_time,
            total_shelving=total_shelving,
            start_call=start_call,
            end_call=end_call,
            student_id=student_id,
            floor_id=floor_id,
            collection_id=collection_id
        )

        # Add and commit to the database
        db.session.add(new_shelving)
        db.session.commit()
        flash(f'Shelving record for student {student_id} added successfully!', 'success')
        return redirect(url_for('supervisor_input_data'))  # Replace 'some_view_name' with the appropriate route

    # GET request, load student and floor data
    students = Student.query.all()
    floors = Floor.query.all()
    collections = Collections.query.all()

    # Log data for troubleshooting
    print("Students:", students)
    print("Floors:", floors)

    return render_template('supervisor-input-data/4.html', students=students, floors=floors, collections=collections)



@app.route('/supervisor-shelving-floor/<int:floor_id>.html')
def show_floor_shelving_data(floor_id):
    # Query the collections that belong to the specified floor_id
    collections = Collections.query.filter_by(floor_id=floor_id).all()

    # Query shelving data that also belongs to the specified floor_id
    shelvings = Shelving.query.filter_by(floor_id=floor_id).join(Student).all()

    # Pass the collections and shelvings to the template
    return render_template('supervisor-shelving-floor/{}.html'.format(floor_id), 
                           collections=collections, 
                           shelvings=shelvings, 
                           floor_id=floor_id)





@app.route('/get_collections/<int:floor_id>')
def get_collections(floor_id):
    # Query collections by floor_id
    collections = Collections.query.filter_by(floor_id=floor_id).all()
    
    # Create a response with the collections in JSON format
    return jsonify({
        'collections': [
            {'collection_id': collection.collection_id, 'collection': collection.collection}
            for collection in collections
        ]
    })

@app.route('/error')
def error():
    return render_template('error.html')

# Student Routes
@app.route('/student-home')
def student_home():
    return render_template('student-home.html')



if __name__ == '__main__':
    app.run(debug=True)

