from models import db, Student, Admin, Tasks, Floor, Collections, Student_Data, ShelfReading, Problem, ProblemList, Shelving, InHouse, HoldList, RmList, ILLList
import os
from flask import Flask, jsonify, render_template, request, redirect, url_for, flash
from flask_login import LoginManager, login_user, login_required, logout_user, current_user
from werkzeug.utils import secure_filename
from werkzeug.security import check_password_hash
from models import User 
from authorize import role_required 
from datetime import datetime , timedelta
import pandas as pd
from datetime import date
from sqlalchemy.orm.exc import NoResultFound
import numpy as np
import re
from sqlalchemy.orm import aliased
from sqlalchemy import func, or_, desc

basedir = os.path.abspath(os.path.dirname(__file__))

app = Flask(__name__, template_folder='template') 
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///' + os.path.join(basedir, 'oogway.db')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SECRET_KEY'] = b'oogway'

app.config['UPLOAD_FOLDER'] = 'uploads/'
app.config['ALLOWED_EXTENSIONS'] = {'xlsx'}
app.secret_key = 'oogway'  # To use flashing messages

db.init_app(app)


login_supervisor = LoginManager()
login_supervisor.init_app(app)
login_supervisor.login_view = 'login'

login_manager = LoginManager()
login_manager.init_app(app)


def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in app.config['ALLOWED_EXTENSIONS']

@app.route('/upload_excel', methods=['GET', 'POST'])
def upload_excel():
    if request.method == 'POST':
        # Ensure the file is part of the request
        if 'file' not in request.files:
            flash('No file part', 'danger')
            return redirect(request.url)
        
        file = request.files['file']
        
        if file.filename == '':
            flash('No selected file', 'danger')
            return redirect(request.url)

        if file and allowed_file(file.filename):
            filename = secure_filename(file.filename)
            filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
            file.save(filepath)

            # Process the Excel file
            try:
                df = pd.read_excel(filepath)

                # Clean the data
                df = clean_data(df)

                # Insert cleaned data into the database
                insert_data_into_db(df)

                flash('File successfully uploaded, cleaned, and data imported!', 'success')
                return redirect(url_for('index'))  # Redirect to a page of your choice
            except Exception as e:
                flash(f'Error: {str(e)}', 'danger')
                return redirect(request.url)

    return render_template('supervisor-input-data.html')  # Render the upload form

def clean_data(df):
    # Example cleaning steps
    # 1. Drop rows with missing values
    df = df.dropna()

    # 2. Remove duplicate rows
    df = df.drop_duplicates()

    # 3. Convert column names to match the database schema
    df.columns = [col.strip().lower().replace(' ', '_') for col in df.columns]

    # 4. Convert specific columns to appropriate types
    # For example, if you need to convert a column to datetime:
    if 'date_column' in df.columns:
        df['date_column'] = pd.to_datetime(df['date_column'], errors='coerce')

    # 5. Handle any other necessary transformations here

    return df

def insert_data_into_db(df):
    # Loop through each row in the DataFrame and add it to the database
    for index, row in df.iterrows():
        # Assuming your model has columns like 'shelf_number', 'book_id', 'status'
        record = ShelfReading(
            shelf_number=row['shelf_number'],  # Adjust based on your model fields
            book_id=row['book_id'],
            book_title=row['book_title'],
            status=row['status'],
            # Add any other fields as necessary
        )

        # Add the record to the session
        db.session.add(record)

    # Commit the session to save the changes
    db.session.commit()



@login_supervisor.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))  


@app.route('/')
def home():
    return redirect(url_for('login'))

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

@app.route('/admin-dashboard')
@login_required
@role_required(['ADMIN'])
def admin_dashboard():
    return render_template('admin-dashboard.html') 



def visualization():
    try:
        # Database query logic
        today = datetime.today().date()
        one_week_ago = today - timedelta(days=7)

        # Query to sum total holds for each day within the past week
        records = (
            db.session.query(HoldList.date, func.sum(HoldList.total_holds))
            .filter(HoldList.date.between(one_week_ago, today))
            .group_by(HoldList.date)
            .order_by(HoldList.date)
            .all()
        )

        # Generate the list of dates from today to one week ago
        all_dates = [today - timedelta(days=i) for i in range(8)]
        all_dates.reverse()  # Ensure the order is from past to present
        date_labels = [date.strftime('%Y-%m-%d') for date in all_dates]

        # Initialize holdlist data for each day with 0
        holdlist_data = [0] * 8

        # Populate the holdlist data with queried totals
        for record in records:
            date_str = record[0].strftime('%Y-%m-%d')
            if date_str in date_labels:
                holdlist_data[date_labels.index(date_str)] = record[1]

        # Return data as a dictionary
        return {
            'dates': date_labels,
            'total_holds': holdlist_data,
        }
    
    except Exception as e:
        print(f"Error in visualization: {e}")
        return {'dates': [], 'total_holds': []} 
    

@app.route('/supervisor-dashboard')
@login_required
@role_required(['supervisor'])
def supervisor_dashboard():
    today = date.today()

    # Query for total tasks completed for today
    total_shelfreads = db.session.query(db.func.sum(ShelfReading.shelfreads_completed)) \
        .filter(ShelfReading.date == today).scalar() or 0

    total_problems = db.session.query(db.func.sum(Problem.total_problems)) \
        .filter(Problem.date == today).scalar() or 0

    total_in_house = db.session.query(db.func.sum(InHouse.total_in_house)) \
        .filter(InHouse.date == today).scalar() or 0

    total_shelving = db.session.query(db.func.sum(Shelving.total_shelving)) \
        .filter(Shelving.date == today).scalar() or 0

    total_holds = db.session.query(db.func.sum(HoldList.total_holds)) \
        .filter(HoldList.date == today).scalar() or 0

    total_ill = db.session.query(db.func.sum(ILLList.total_ill)) \
        .filter(ILLList.date == today).scalar() or 0

    total_tasks = {
        'Shelf Reads': total_shelfreads,
        'Problems': total_problems,
        'In House': total_in_house,
        'Shelving': total_shelving,
        'Holds': total_holds,
        'ILL': total_ill
    }

    # Hold list data for the line chart (from visualization function)
    holdlist_data = visualization()

    return render_template('supervisor-dashboard.html',
                           total_shelfreads=total_shelfreads,
                           total_problems=total_problems,
                           total_in_house=total_in_house,
                           total_shelving=total_shelving,
                           total_holds=total_holds,
                           total_ill=total_ill,
                           total_tasks=total_tasks,
                           holdlist_data=holdlist_data)



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
            student.student_hours = request.form['student_hours']  # Update scheduled hours here

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

@app.route('/supervisor-input-data/1', methods=['GET', 'POST'])
@login_required
@role_required(['supervisor'])
def supervisor_input_data_1():
    if request.method == 'POST':
        # Retrieve form data
        student_id = request.form.get('student_id')
        date_string = request.form.get('date')
        date = datetime.strptime(date_string, '%Y-%m-%d').date()
        start_time_string = request.form.get('start_time')
        end_time_string = request.form.get('end_time')  
        start_time = datetime.strptime(start_time_string, '%H:%M')
        end_time = datetime.strptime(end_time_string, '%H:%M')
        shelfreads_completed = int(request.form.get('shelfreads_completed'))  
        start_call = request.form.get('start_call')
        end_call = request.form.get('end_call')
        floor_id = request.form.get('floor_id')
        collection_id = request.form.get('collection_id')
        duration = (end_time - start_time).total_seconds() / 3600.0
        
        student = Student.query.filter_by(student_id=student_id).first()
        
        new_shelfread = ShelfReading(
            date=date,
            start_time=start_time,
            end_time=end_time,
            shelfreads_completed=shelfreads_completed,
            start_call=start_call,
            end_call=end_call,
            student_id=student_id,
            floor_id=floor_id,
            collection_id=collection_id,
            duration = duration
        )

        # Add and commit to the database
        db.session.add(new_shelfread)
        db.session.commit()
        flash(f'Shelfreads record for student {student.student_fname} added successfully!', 'success')
        return redirect(url_for('supervisor_input_data'))  # Replace 'some_view_name' with the appropriate route

    # GET request, load student and floor data
    students = Student.query.all()
    floors = Floor.query.all()
    collections = Collections.query.all()

    # Log data for troubleshooting
    print("Students:", students)
    print("Floors:", floors)

    return render_template('supervisor-input-data/1.html', students=students, floors=floors, collections=collections)




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
        total_problems = 1
        
        student = Student.query.filter_by(student_id=student_id).first()
        
        if not call_no:
            flash('Call number is required!', 'danger')
            return redirect(request.url)  # Redirect back to the form with error

        # Create a new Problem record
        problem = Problem(
            student_id=student_id,
            date=date,
            call_no=call_no,
            problem_id=problem_id,
            total_problems=total_problems
        )

        # Add and commit to the database
        db.session.add(problem)
        db.session.commit()
        flash(f'Problem item record for student {student.student_fname} added successfully!', 'success')
        return redirect(url_for('supervisor_input_data'))  # Replace with appropriate route

    # GET request, load student and floor data
    students = Student.query.all()
    problems = Problem.query.all()
    problems_list = ProblemList.query.all()

    return render_template('supervisor-input-data/2.html', students=students, problems=problems, problems_list=problems_list)


@app.route('/supervisor-input-data/3', methods=['GET', 'POST'])
@login_required
@role_required(['supervisor'])
def supervisor_input_data_3():
    if request.method == 'POST':
        # Retrieve form data
        student_id = request.form.get('student_id')
        date_string = request.form.get('date')
        date = datetime.strptime(date_string, '%Y-%m-%d').date()
        total_in_house = request.form.get('total_in_house')
   
        student = Student.query.filter_by(student_id=student_id).first()
        
        in_house = InHouse(
            student_id=student_id,
            date=date,
            total_in_house = total_in_house
        )

        # Add and commit to the database
        db.session.add(in_house)
        db.session.commit()
        flash(f'In-House item record for student {student.student_fname} added successfully!', 'success')
        return redirect(url_for('supervisor_input_data'))  # Replace with appropriate route

    # GET request, load student and floor data
    students = Student.query.all()
    inhouse = InHouse.query.all()

    return render_template('supervisor-input-data/3.html', students=students, inhouse=inhouse)



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
        total_shelving = request.form.get('total_shelving')
        
        student = Student.query.filter_by(student_id=student_id).first()
 
        new_shelving = Shelving(
            date=date,
            student_id=student_id,
            total_shelving=total_shelving
        )

        # Add and commit to the database
        db.session.add(new_shelving)
        db.session.commit()
        flash(f'Shelving record for student {student.student_fname} added successfully!', 'success')
        return redirect(url_for('supervisor_input_data'))  # Replace 'some_view_name' with the appropriate route

    # GET request, load student and floor data
    students = Student.query.all()
    new_shelving = Shelving.query.all()

    return render_template('supervisor-input-data/4.html', students=students, new_shelving=new_shelving)


@app.route('/supervisor-input-data/5', methods=['GET', 'POST'])
@login_required
@role_required(['supervisor'])
def supervisor_input_data_5():
    if request.method == 'POST':
        student_id = request.form.get('student_id')
        date_string = request.form.get('date')
        date = datetime.strptime(date_string, '%Y-%m-%d').date()
        total_holds = request.form.get('total_holds')
        
        student = Student.query.filter_by(student_id=student_id).first()
        
        new_holds = HoldList(
            date=date,
            student_id=student_id,
            total_holds=total_holds
        )
        db.session.add(new_holds)
        db.session.commit()
        flash(f'Hold List record for student {student.student_fname} added successfully!', 'success')
        return redirect(url_for('supervisor_input_data')) 

    students = Student.query.all()
    holds = HoldList.query.all()

    return render_template('supervisor-input-data/5.html', students=students, holds=holds)


@app.route('/supervisor-input-data/6', methods=['GET', 'POST'])
@login_required
@role_required(['supervisor'])
def supervisor_input_data_6():
    if request.method == 'POST':
        # Retrieve form data
        student_id = request.form.get('student_id')
        date_string = request.form.get('date')
        date = datetime.strptime(date_string, '%Y-%m-%d').date()
        total_rm = request.form.get('total_rm')
        
        student = Student.query.filter_by(student_id=student_id).first()
        
        new_rm = RmList(
            date=date,
            student_id=student_id,
            total_rm=total_rm
        )

        # Add and commit to the database
        db.session.add(new_rm)
        db.session.commit()
        flash(f'Hold List record for student {student.student_fname} added successfully!', 'success')
        return redirect(url_for('supervisor_input_data'))  # Replace 'some_view_name' with the appropriate route

    # GET request, load student and floor data
    students = Student.query.all()
    rm = RmList.query.all()

    return render_template('supervisor-input-data/6.html', students=students, rm=rm)


@app.route('/supervisor-shelving-floor/<int:floor_id>.html')
def show_floor_shelfreading_data(floor_id):
    # Get the specific floor based on the floor_id
    floor = Floor.query.get(floor_id)  # Fetch the floor with the given floor_id

    # Get the collections for this floor
    collections = Collections.query.filter_by(floor_id=floor_id).all()

    # Get the shelfreading data for this floor, joined with student and collection
    shelfreadings = ShelfReading.query.filter_by(floor_id=floor_id).join(Student).join(Collections).all()

    # Render the template with the floor object and related data
    return render_template('supervisor-shelving-floor/1.html', 
                           collections=collections, 
                           shelfreadings=shelfreadings, 
                           floor=floor)  # Pass the specific floor object


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


    
    
    
    
#STUDENT VIEW
@app.route('/student-input-data/<int:task_id>')
@login_required
@role_required(['student'])
def student_task_page(task_id):
    tasks = Tasks.query.all()
    return render_template(f'student-input-data/{task_id}.html')


@app.route('/student-input-data', methods=['GET', 'POST'])
@login_required
@role_required(['student'])
def student_input_data():
    if request.method == 'POST':
    
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
    return render_template('student-input-data.html', students=students, tasks=tasks, floors=floors, collections=collections, action='create')




@app.route('/error')
def error():
    return render_template('error.html')

# Student Routes
@app.route('/student-home')
def student_home():
    tasks = Tasks.query.all()
    return render_template('student-home.html', tasks=tasks)


UPLOAD_FOLDER = 'uploads'
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.config['ALLOWED_EXTENSIONS'] = {'xls', 'xlsx'}

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in app.config['ALLOWED_EXTENSIONS']

# Route to upload the file
@app.route('/upload', methods=['GET', 'POST'])
def upload_file():
    # Check if the 'uploads' directory exists, if not, create it
    if not os.path.exists(app.config['UPLOAD_FOLDER']):
        os.makedirs(app.config['UPLOAD_FOLDER'])

    if request.method == 'POST':
        if 'file' not in request.files:
            flash('No file part')
            return redirect(request.url)
        file = request.files['file']
        if file.filename == '':
            flash('No selected file')
            return redirect(request.url)
        if file and allowed_file(file.filename):
            # Save the file to the server
            filename = os.path.join(app.config['UPLOAD_FOLDER'], file.filename)
            file.save(filename)

            # Process the file
            process_excel_file(filename)

            flash(f'File was successfully added!', 'success')
            return redirect(url_for('upload_file'))

    return render_template('supervisor-input-data.html')



def process_excel_file(excel_file_path):
    all_sheets = pd.read_excel(excel_file_path, sheet_name=None)

    folder_name = os.path.splitext(os.path.basename(excel_file_path))[0]
    parent_directory = "processed_files"
    folder_path = os.path.join(parent_directory, folder_name)

    if not os.path.exists(folder_path):
        os.makedirs(folder_path)

    for sheet_name, df in all_sheets.items():
        file_path = os.path.join(folder_path, f"{sheet_name}.csv")
        df.to_csv(file_path, index=False)

    print(f"All sheets saved as CSV files in the folder: {folder_path}")

    edited_folder_name = folder_name + "_edited"
    edited_folder_path = os.path.join(parent_directory, edited_folder_name)

    if not os.path.exists(edited_folder_path):
        os.makedirs(edited_folder_path)

    for sheet_name, df in all_sheets.items():
        new_df = edit_sheet(df)
        collection_name = sheet_name.replace("_edited", "")  
        file_path = os.path.join(edited_folder_path, f"{collection_name}_edited.csv")
        new_df.to_csv(file_path, index=False)
        print(f"Edited sheet '{sheet_name}' saved to: {file_path}")
        
        insert_data_to_db(file_path, excel_file_path)


def edit_sheet(df):
    default_datetime = pd.to_datetime('1900-01-01 00:00:00')

    temp_df = df.iloc[:, [0, 1, 2, 3, 5, 6, 7]]
    temp_df.columns = ['Name', 'date', 'start_time', 'end_time', 'shelfreads_completed', 'start_call', 'end_call']

    cleaned_temp_df = temp_df.dropna(how='all').reset_index(drop=True)

    cleaned_temp_df['date'] = pd.to_datetime(cleaned_temp_df['date'], errors='coerce')

    cleaned_temp_df['start_time'] = pd.to_datetime(cleaned_temp_df['start_time'], format='%H:%M:%S', errors='coerce').dt.time
    cleaned_temp_df['end_time'] = pd.to_datetime(cleaned_temp_df['end_time'], format='%H:%M:%S', errors='coerce').dt.time

    cleaned_temp_df['Start DateTime'] = cleaned_temp_df.apply(
        lambda row: datetime.combine(row['date'].date(), row['start_time']) if pd.notnull(row['date']) and pd.notnull(row['start_time']) else default_datetime,
        axis=1
    )
    cleaned_temp_df['End DateTime'] = cleaned_temp_df.apply(
        lambda row: datetime.combine(row['date'].date(), row['end_time']) if pd.notnull(row['date']) and pd.notnull(row['end_time']) else default_datetime,
        axis=1
    )

    cleaned_temp_df['Duration'] = cleaned_temp_df.apply(
        lambda row: row['End DateTime'] - row['Start DateTime'] if pd.notnull(row['End DateTime']) and pd.notnull(row['Start DateTime']) else pd.NaT,
        axis=1
    )

    cleaned_temp_df['Duration'] = cleaned_temp_df['Duration'].apply(
        lambda x: round(x.total_seconds() / 3600, 2) if isinstance(x, pd.Timedelta) else "Error, missing value"
    )

    cleaned_temp_df = cleaned_temp_df.dropna(subset=['Name'])

    cleaned_temp_df['student_id'] = cleaned_temp_df['Name'].apply(
        lambda name: get_student_id_from_db(name) if isinstance(name, str) else np.nan
    )

    cleaned_temp_df = cleaned_temp_df.dropna(subset=['student_id'])
    
    cleaned_temp_df = cleaned_temp_df.drop(columns=['Name'])
    cleaned_temp_df['Start DateTime'] = cleaned_temp_df['Start DateTime'].fillna(default_datetime)
    cleaned_temp_df['End DateTime'] = cleaned_temp_df['End DateTime'].fillna(default_datetime)
    cleaned_temp_df['date'] = cleaned_temp_df['date'].fillna(default_datetime)
    cleaned_temp_df = cleaned_temp_df.fillna("Missing")

    cleaned_temp_df = cleaned_temp_df[['student_id', 'date', 'Start DateTime', 'End DateTime', 
                                       'shelfreads_completed', 'start_call', 'end_call', 'Duration']]
    return cleaned_temp_df




def get_student_id_from_db(first_name):
    student = Student.query.filter_by(student_fname=first_name).first()
    
    if student:
        return student.student_id
    else:
        print(f"Warning: Student with first name {first_name} not found in the database!")
        return np.nan

def normalize_floor_name(name):
    # Convert ordinals (e.g., '6th', '3rd') to cardinal numbers ('6', '3')
    name = re.sub(r'(\d+)(st|nd|rd|th)', r'\1', name.lower())
    # Remove common terms to standardize
    name = re.sub(r'\b(floor|copy|sr)\b', '', name).strip()
    return name

def get_floor_id_from_path(excel_file_path):
    file_name = os.path.basename(excel_file_path).replace(".xlsx", "").lower()
    file_name_normalized = normalize_floor_name(file_name)

    all_floors = Floor.query.all()
    for floor in all_floors:
        floor_name_normalized = normalize_floor_name(floor.floor)
        if floor_name_normalized in file_name_normalized:
            return floor.floor_id

    raise ValueError(f"No matching floor name found in the FLOOR table for '{file_name}'.")

def insert_data_to_db(csv_file_path, excel_file_path):
    floor_id = int(get_floor_id_from_path(excel_file_path))

    collection_name = os.path.basename(csv_file_path).split('.')[0].replace('_edited', '')

    collection = Collections.query.filter_by(collection=collection_name).first()
    if collection is None:
        print(f"Warning: Collection with name {collection_name} not found!")
        collection_id = None
    else:
        collection_id = collection.collection_id

    df = pd.read_csv(csv_file_path)
    inserted_count = 0 

    for _, row in df.iterrows():
        if 'student_id' not in row or pd.isna(row['student_id']):
            print(f"Error: Missing student ID in row for {row['Name']}")
            continue 

        student_id = row['student_id']

        try:
            date = datetime.strptime(str(row['date']), '%Y-%m-%d').date()
            start_time = datetime.strptime(str(row['Start DateTime']), '%Y-%m-%d %H:%M:%S')
            end_time = datetime.strptime(str(row['End DateTime']), '%Y-%m-%d %H:%M:%S')
        except ValueError as e:
            print(f"Error parsing date/time for student {student_id}: {e}")
            continue 

        existing_record = ShelfReading.query.filter_by(
            date=date,
            start_time=start_time,
            student_id=student_id
        ).first()

        if existing_record is None:
            new_record = ShelfReading(
                date=date,
                start_time=start_time,
                end_time=end_time,
                duration=row['Duration'],
                shelfreads_completed=row['shelfreads_completed'],
                start_call=row['start_call'],
                end_call=row['end_call'],
                student_id=row['student_id'],
                floor_id=floor_id,
                collection_id=collection_id
            )
            db.session.add(new_record) 
            db.session.commit()
            print(f"Inserted new record for student ID {row['student_id']} at floor {floor_id} and collection {collection_name}.")
            inserted_count += 1 
        else:
            print(f"Duplicate found for student {row['student_id']} on {row['date']} at {row['Start DateTime']} - Skipping insert.")

    return f"{inserted_count} records successfully inserted into the database."


#All student data
def update_student_data(student_id):
    student = db.session.query(Student).filter(Student.student_id == student_id).first()

    if not student:
        total_shelfreads = 0
        total_problem_items = 0
        total_in_house = 0
        total_shelving = 0
        total_holds_list = 0
        total_ill = 0
    else:
        total_shelfreads = db.session.query(func.count(ShelfReading.student_id)).filter(ShelfReading.student_id == student_id).scalar()
        total_problem_items = db.session.query(func.count(Problem.student_id)).filter(Problem.student_id == student_id).scalar()
        total_in_house = db.session.query(func.count(InHouse.student_id)).filter(InHouse.student_id == student_id).scalar()
        total_shelving = db.session.query(func.count(Shelving.student_id)).filter(Shelving.student_id == student_id).scalar()
        total_holds_list = db.session.query(func.count(HoldList.student_id)).filter(HoldList.student_id == student_id).scalar()
        total_ill = db.session.query(func.count(ILLList.student_id)).filter(ILLList.student_id == student_id).scalar()

    task_id = 1  # Update with the correct task ID if needed
    
    student_data = Student_Data(
        student_id=student_id,  # Correctly use the student_id here
        task_id=task_id,
        total_shelfreads=total_shelfreads,
        total_problem_items=total_problem_items,
        total_in_house=total_in_house,
        total_shelving=total_shelving,
        total_holds_list=total_holds_list,
        total_ill=total_ill
    )

    db.session.add(student_data)
    db.session.commit()

    return f"Data for student {student_id} has been updated successfully!"


@app.route('/supervisor-student-overall-view', methods=['GET', 'POST'])
def supervisor_student_overall_view():
    # Get the search query from the URL parameters
    search_query = request.args.get('search_query', '').lower()

    # Update data for all students
    students = db.session.query(Student).all()  # Get all students
    for student in students:
        update_student_data(student.student_id)  # Update data for each student

    # Build the query for filtering students
    query = db.session.query(
        Student.student_id,
        Student.student_fname,
        Student.student_lname,
        db.func.sum(Student_Data.total_shelfreads).label('total_shelfreads'),
        db.func.sum(Student_Data.total_problem_items).label('total_problem_items'),
        db.func.sum(Student_Data.total_in_house).label('total_in_house'),
        db.func.sum(Student_Data.total_shelving).label('total_shelving'),
        db.func.sum(Student_Data.total_holds_list).label('total_holds_list'),
        db.func.sum(Student_Data.total_ill).label('total_ill')
    ).join(Student_Data, Student.student_id == Student_Data.student_id)

    if search_query:
        # Filter by the student's first or last name
        query = query.filter(
            or_(
                Student.student_fname.ilike(f"%{search_query}%"),
                Student.student_lname.ilike(f"%{search_query}%")
            )
        )

    # Group by student_id to ensure each student appears only once
    query = query.group_by(Student.student_id, Student.student_fname, Student.student_lname, Student.student_hours)

    # Order by student_id
    students_data = query.order_by(Student.student_id).all()

    # Define XP values for each task
    XP_VALUES = {
        'total_shelfreads': 10,
        'total_problem_items': 5,
        'total_in_house': 2,
        'total_shelving': 8,
        'total_holds_list': 3,
        'total_ill': 4
    }

    # Calculate total XP for each student and keep the original data
    student_xp_data = []
    for student in students_data:
        # Extract the task counts for each student
        total_shelfreads = student.total_shelfreads
        total_problem_items = student.total_problem_items
        total_in_house = student.total_in_house
        total_shelving = student.total_shelving
        total_holds_list = student.total_holds_list
        total_ill = student.total_ill

        # Calculate total XP for the student
        total_xp = (
            total_shelfreads * XP_VALUES['total_shelfreads'] +
            total_problem_items * XP_VALUES['total_problem_items'] +
            total_in_house * XP_VALUES['total_in_house'] +
            total_shelving * XP_VALUES['total_shelving'] +
            total_holds_list * XP_VALUES['total_holds_list'] +
            total_ill * XP_VALUES['total_ill']
        )

        # Append calculated XP along with other data, including student_hours
        student_xp_data.append({
            'student_id': student.student_id,
            'student_fname': student.student_fname,
            'student_lname': student.student_lname,
            'total_shelfreads': total_shelfreads,
            'total_problem_items': total_problem_items,
            'total_in_house': total_in_house,
            'total_shelving': total_shelving,
            'total_holds_list': total_holds_list,
            'total_ill': total_ill,
            'total_xp': total_xp
        })
    
    # Return the data to the template
    return render_template('supervisor-student-overall-view.html', students_data=student_xp_data)






# @app.route('/supervisor-student-overall-view', methods=['GET', 'POST'])
# def supervisor_student_overall_view():
#     # Get the search query from the URL parameters
#     search_query = request.args.get('search_query', '').lower()

#     # Update data for all students
#     students = db.session.query(Student).all()  # Get all students
#     for student in students:
#         update_student_data(student.student_id)  # Update data for each student

#     # Build the query for filtering students
#     query = db.session.query(
#         Student.student_id,
#         Student.student_fname,
#         Student.student_lname,
#         Student_Data.total_shelfreads,
#         Student_Data.total_problem_items,
#         Student_Data.total_in_house,
#         Student_Data.total_shelving,
#         Student_Data.total_holds_list,
#         Student_Data.total_rm_list
#     ).join(Student_Data, Student.student_id == Student_Data.student_id)

#     if search_query:
#         # Filter by the student's first or last name
#         query = query.filter(
#             or_(
#                 Student.student_fname.ilike(f"%{search_query}%"),
#                 Student.student_lname.ilike(f"%{search_query}%")
#             )
#         )

#     # Make sure the results are distinct and ordered by student_id
#     students_data = query.distinct().order_by(Student.student_id).all()

#     return render_template('supervisor-student-overall-view.html', students_data=students_data)


            
@app.route('/supervisor-student-list-view')
def supervisor_student_list_view():
    students = Student.query.order_by(Student.student_id).all()
    search_query = request.args.get('search_query', '').lower()
    
    if search_query:
        query = query.filter(
            or_(
                Student.student_fname.ilike(f"%{search_query}%"),
                Student.student_lname.ilike(f"%{search_query}%")
            )
        )
    return render_template('supervisor-student-list-view.html', students=students)

import plotly.graph_objects as go
import plotly.express as px
from flask import render_template

def plot_top_students_holdlist():
    # Query data for Hold List
    holdlist_data = db.session.query(HoldList.student_id, db.func.sum(HoldList.total_holds).label('total_holds')) \
                             .group_by(HoldList.student_id) \
                             .order_by(db.func.sum(HoldList.total_holds).desc()) \
                             .limit(3).all()
    
    # Prepare data for the bar chart
    students = [student[0] for student in holdlist_data]
    total_holds = [student[1] for student in holdlist_data]

    # Query for first and last names
    student_names = []
    for student_id in students:
        student = db.session.query(Student).filter_by(student_id=student_id).first()  # Assuming Student table contains student names
        if student:
            student_names.append(f"{student.student_fname} {student.student_lname}")
        else:
            student_names.append(f"Student {student_id}")

    # Create the Plotly bar chart
    fig = go.Figure(data=[go.Bar(x=student_names, y=total_holds, marker_color='blue')])
    fig.update_layout(title='Top 3 Students with the Most Holds',
                      xaxis_title='Students',
                      yaxis_title='Total Holds')

    # Return the figure as HTML
    return fig.to_html(full_html=False)

def plot_top_students_ill():
    # Query data for ILL slips
    ill_data = db.session.query(ILLList.student_id, db.func.sum(ILLList.total_ill).label('total_ill')) \
                        .group_by(ILLList.student_id) \
                        .order_by(db.func.sum(ILLList.total_ill).desc()) \
                        .limit(3).all()
    
    # Prepare data for the bar chart
    students = [student[0] for student in ill_data]
    total_ill = [student[1] for student in ill_data]

    # Query for first and last names
    student_names = []
    for student_id in students:
        student = db.session.query(Student).filter_by(student_id=student_id).first()  # Assuming Student table contains student names
        if student:
            student_names.append(f"{student.student_fname} {student.student_lname}")
        else:
            student_names.append(f"Student {student_id}")

    # Create the Plotly bar chart
    fig = go.Figure(data=[go.Bar(x=student_names, y=total_ill, marker_color='green')])
    fig.update_layout(title='Top 3 Students with the Most ILL Slips',
                      xaxis_title='Students',
                      yaxis_title='Total ILL Slips')

    # Return the figure as HTML
    return fig.to_html(full_html=False)

def plot_top_students_inhouse():
    # Query data for In House
    inhouse_data = db.session.query(InHouse.student_id, db.func.sum(InHouse.total_in_house).label('total_in_house')) \
                             .group_by(InHouse.student_id) \
                             .order_by(db.func.sum(InHouse.total_in_house).desc()) \
                             .limit(3).all()
    
    # Prepare data for the bar chart
    students = [student[0] for student in inhouse_data]
    total_in_house = [student[1] for student in inhouse_data]

    # Query for first and last names
    student_names = []
    for student_id in students:
        student = db.session.query(Student).filter_by(student_id=student_id).first()  # Assuming Student table contains student names
        if student:
            student_names.append(f"{student.student_fname} {student.student_lname}")
        else:
            student_names.append(f"Student {student_id}")

    # Create the Plotly bar chart
    fig = go.Figure(data=[go.Bar(x=student_names, y=total_in_house, marker_color='orange')])
    fig.update_layout(title='Top 3 Students with the Most In House',
                      xaxis_title='Students',
                      yaxis_title='Total In House')

    # Return the figure as HTML
    return fig.to_html(full_html=False)

def plot_top_students_shelving():
    # Query data for Shelving
    shelving_data = db.session.query(Shelving.student_id, db.func.sum(Shelving.total_shelving).label('total_shelving')) \
                              .group_by(Shelving.student_id) \
                              .order_by(db.func.sum(Shelving.total_shelving).desc()) \
                              .limit(3).all()
    
    # Prepare data for the bar chart
    students = [student[0] for student in shelving_data]
    total_shelving = [student[1] for student in shelving_data]

    # Query for first and last names
    student_names = []
    for student_id in students:
        student = db.session.query(Student).filter_by(student_id=student_id).first()  # Assuming Student table contains student names
        if student:
            student_names.append(f"{student.student_fname} {student.student_lname}")
        else:
            student_names.append(f"Student {student_id}")

    # Create the Plotly bar chart
    fig = go.Figure(data=[go.Bar(x=student_names, y=total_shelving, marker_color='red')])
    fig.update_layout(title='Top 3 Students with the Most Shelving',
                      xaxis_title='Students',
                      yaxis_title='Total Shelving')

    # Return the figure as HTML
    return fig.to_html(full_html=False)

def plot_top_students_problem_items():
    # Query data for Problem Items
    problem_items_data = db.session.query(Problem.student_id, db.func.sum(Problem.total_problems).label('total_problems')) \
                                  .group_by(Problem.student_id) \
                                  .order_by(db.func.sum(Problem.total_problems).desc()) \
                                  .limit(3).all()
    
    # Prepare data for the bar chart
    students = [student[0] for student in problem_items_data]
    total_problems = [student[1] for student in problem_items_data]

    # Query for first and last names
    student_names = []
    for student_id in students:
        student = db.session.query(Student).filter_by(student_id=student_id).first()  # Assuming Student table contains student names
        if student:
            student_names.append(f"{student.student_fname} {student.student_lname}")
        else:
            student_names.append(f"Student {student_id}")

    # Create the Plotly bar chart
    fig = go.Figure(data=[go.Bar(x=student_names, y=total_problems, marker_color='purple')])
    fig.update_layout(title='Top 3 Students with the Most Problem Items',
                      xaxis_title='Students',
                      yaxis_title='Total Problem Items')

    # Return the figure as HTML
    return fig.to_html(full_html=False)

def plot_top_students_shelf_reading():
    # Query data for Shelf Reading
    shelf_reading_data = db.session.query(ShelfReading.student_id, db.func.sum(ShelfReading.shelfreads_completed).label('shelfreads_completed')) \
                                  .group_by(ShelfReading.student_id) \
                                  .order_by(db.func.sum(ShelfReading.shelfreads_completed).desc()) \
                                  .limit(3).all()
    
    # Prepare data for the bar chart
    students = [student[0] for student in shelf_reading_data]
    shelfreads_completed = [student[1] for student in shelf_reading_data]

    # Query for first and last names
    student_names = []
    for student_id in students:
        student = db.session.query(Student).filter_by(student_id=student_id).first()  # Assuming Student table contains student names
        if student:
            student_names.append(f"{student.student_fname} {student.student_lname}")
        else:
            student_names.append(f"Student {student_id}")

    # Create the Plotly bar chart
    fig = go.Figure(data=[go.Bar(x=student_names, y=shelfreads_completed, marker_color='brown')])
    fig.update_layout(title='Top 3 Students with the Most Shelf Reads Completed',
                      xaxis_title='Students',
                      yaxis_title='Total Shelf Reads Completed')

    # Return the figure as HTML
    return fig.to_html(full_html=False)

def plot_top_students_overall():
    # Query data for all activities combined (holds, ILL, in-house, shelving, problem items, shelf reads)
    activity_data = db.session.query(
        Student.student_id,
        (db.func.sum(HoldList.total_holds) +
         db.func.sum(ILLList.total_ill) +
         db.func.sum(InHouse.total_in_house) +
         db.func.sum(Shelving.total_shelving) +
         db.func.sum(Problem.total_problems) +
         db.func.sum(ShelfReading.shelfreads_completed)
        ).label('total_activity')
    ) \
    .join(HoldList, HoldList.student_id == Student.student_id) \
    .join(ILLList, ILLList.student_id == Student.student_id) \
    .join(InHouse, InHouse.student_id == Student.student_id) \
    .join(Shelving, Shelving.student_id == Student.student_id) \
    .join(Problem, Problem.student_id == Student.student_id) \
    .join(ShelfReading, ShelfReading.student_id == Student.student_id) \
    .group_by(Student.student_id) \
    .order_by(db.func.sum(HoldList.total_holds + ILLList.total_ill + InHouse.total_in_house + Shelving.total_shelving + Problem.total_problems + ShelfReading.shelfreads_completed).desc()) \
    .limit(3) \
    .all()

    # Prepare data for the bar chart
    students = [student[0] for student in activity_data]
    total_activity = [student[1] for student in activity_data]

    # Query for first and last names
    student_names = []
    for student_id in students:
        student = db.session.query(Student).filter_by(student_id=student_id).first()
        if student:
            student_names.append(f"{student.student_fname} {student.student_lname}")
        else:
            student_names.append(f"Student {student_id}")

    # Create the Plotly bar chart
    fig = go.Figure(data=[go.Bar(x=student_names, y=total_activity, marker_color='cyan')])
    fig.update_layout(title='Top 3 Students with the Most Combined Activity',
                      xaxis_title='Students',
                      yaxis_title='Total Activity',
                      template="plotly_dark",
                      plot_bgcolor='white',
                      paper_bgcolor='white')

    # Return the figure as HTML
    return fig.to_html(full_html=False)


@app.route('/supervisor-analytics')
def supervisor_analytics():
    # Generate the base64-encoded images for all the plots
    holdlist_image = plot_top_students_holdlist()
    ill_image = plot_top_students_ill()
    inhouse_image = plot_top_students_inhouse()
    shelving_image = plot_top_students_shelving()
    problem_items_image = plot_top_students_problem_items()
    shelf_reading_image = plot_top_students_shelf_reading()
    overall_image = plot_top_students_overall()  # New graph for overall top 3 students

    # Pass the images to the template
    return render_template('supervisor-analytics.html', 
                           holdlist_image=holdlist_image,
                           ill_image=ill_image,
                           inhouse_image=inhouse_image,
                           shelving_image=shelving_image,
                           problem_items_image=problem_items_image,
                           shelf_reading_image=shelf_reading_image,
                           overall_image=overall_image)  # Pass the new graph




if __name__ == '__main__':
    app.run(debug=True)

