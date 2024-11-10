from models import db, Student, Admin, Tasks, Floor, Collections, Student_Data, ShelfReading, Problem, ProblemList, Shelving
import os
from flask import Flask, jsonify, render_template, request, redirect, url_for, flash
from flask_login import LoginManager, login_user, login_required, logout_user, current_user
from werkzeug.utils import secure_filename
from werkzeug.security import check_password_hash
from models import User 
from authorize import role_required 
from datetime import datetime 
import pandas as pd
from datetime import datetime
from sqlalchemy.orm.exc import NoResultFound
import numpy as np

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



# @app.route('/supervisor-shelving-floor/<int:floor_id>.html')
# def show_floor_shelving_data(floor_id):
#     collections = Collections.query.filter_by(floor_id=floor_id).all()
#     shelvings = Shelving.query.filter_by(floor_id=floor_id).join(Student).all()
#     floors = Floor.query.all()
    
#     return render_template(f'supervisor-shelving-floor/{floor_id}.html', collections=collections, shelvings=shelvings, floor_id=floor_id, floors=floors)

@app.route('/supervisor-shelving-floor/<int:floor_id>.html')
def show_floor_shelving_data(floor_id):
    # Get the specific floor based on the floor_id
    floor = Floor.query.get(floor_id)  # Fetch the floor with the given floor_id

    # Get the collections and shelvings for this floor
    collections = Collections.query.filter_by(floor_id=floor_id).all()
    shelvings = Shelving.query.filter_by(floor_id=floor_id).join(Student).all()

    # Render the template with the floor object
    return render_template('supervisor-shelving-floor/1.html', 
                           collections=collections, 
                           shelvings=shelvings, 
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


# Define file upload path
UPLOAD_FOLDER = 'uploads'
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.config['ALLOWED_EXTENSIONS'] = {'xls', 'xlsx'}

# Helper function to check allowed file extensions
def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in app.config['ALLOWED_EXTENSIONS']

# Route to upload the file
@app.route('/upload', methods=['GET', 'POST'])
def upload_file():
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
            
            flash('File successfully uploaded and processed')
            return redirect(url_for('upload_file'))  # Redirect to another page

    return render_template('supervisor-input-data.html')  # Assuming you have an 'upload.html' template


def process_excel_file(excel_file_path):
    # Read the Excel file
    all_sheets = pd.read_excel(excel_file_path, sheet_name=None)

    # New file path folder based on Excel filename
    folder_name = os.path.splitext(os.path.basename(excel_file_path))[0]
    parent_directory = "processed_files"
    folder_path = os.path.join(parent_directory, folder_name)

    if not os.path.exists(folder_path):
        os.makedirs(folder_path)

    # Save each sheet as a separate CSV file
    for sheet_name, df in all_sheets.items():
        file_path = os.path.join(folder_path, f"{sheet_name}.csv")
        df.to_csv(file_path, index=False)

    print(f"All sheets saved as CSV files in the folder: {folder_path}")

    # Folder to save edited files
    edited_folder_name = folder_name + "_edited"
    edited_folder_path = os.path.join(parent_directory, edited_folder_name)

    if not os.path.exists(edited_folder_path):
        os.makedirs(edited_folder_path)

    # Process each sheet and save edited CSV files
    for sheet_name, df in all_sheets.items():
        new_df = edit_sheet(df)  # Use the updated edit_sheet function
        collection_name = sheet_name.replace("_edited", "")  # Ensure this matches the sheet's original name
        file_path = os.path.join(edited_folder_path, f"{collection_name}_edited.csv")
        new_df.to_csv(file_path, index=False)
        print(f"Edited sheet '{sheet_name}' saved to: {file_path}")
        
        # Insert data into the database
        insert_data_to_db(file_path, excel_file_path)  # Pass excel file path to insert data


def edit_sheet(df):
    default_datetime = pd.to_datetime('1900-01-01 00:00:00')

    # Select relevant columns from the input dataframe
    temp_df = df.iloc[:, [0, 1, 2, 3, 5, 6, 7]]
    temp_df.columns = ['Name', 'date', 'start_time', 'end_time', 'shelves_completed', 'start_call', 'end_call']

    # Remove rows with all NaN values and reset index
    cleaned_temp_df = temp_df.dropna(how='all').reset_index(drop=True)

    # Convert 'date' column to datetime64[ns] type
    cleaned_temp_df['date'] = pd.to_datetime(cleaned_temp_df['date'], errors='coerce')

    # Convert 'start_time' and 'end_time' to time format
    cleaned_temp_df['start_time'] = pd.to_datetime(cleaned_temp_df['start_time'], format='%H:%M:%S', errors='coerce').dt.time
    cleaned_temp_df['end_time'] = pd.to_datetime(cleaned_temp_df['end_time'], format='%H:%M:%S', errors='coerce').dt.time

    # Combine 'date' with 'start_time' and 'end_time' to form full datetime values
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

    # Drop rows where 'Name' is empty or doesn't contain both a first and last name
    cleaned_temp_df = cleaned_temp_df.dropna(subset=['Name'])

    # Get student IDs based on the first and last name
    cleaned_temp_df['student_id'] = cleaned_temp_df['Name'].apply(
        lambda name: get_student_id_from_db(name) if isinstance(name, str) else np.nan
    )

    # Drop rows where student_id is not found (None)
    cleaned_temp_df = cleaned_temp_df.dropna(subset=['student_id'])

    # Drop the 'Name' column and fill NaN values
    cleaned_temp_df = cleaned_temp_df.drop(columns=['Name'])
    cleaned_temp_df['Start DateTime'] = cleaned_temp_df['Start DateTime'].fillna(default_datetime)
    cleaned_temp_df['End DateTime'] = cleaned_temp_df['End DateTime'].fillna(default_datetime)
    cleaned_temp_df['date'] = cleaned_temp_df['date'].fillna(default_datetime)
    cleaned_temp_df = cleaned_temp_df.fillna("Missing")

    # Select relevant columns for the final DataFrame
    cleaned_temp_df = cleaned_temp_df[['student_id', 'date', 'Start DateTime', 'End DateTime', 
                                       'shelves_completed', 'start_call', 'end_call', 'Duration']]

    return cleaned_temp_df




def get_student_id_from_db(first_name):
    # Query the database using only the first name
    student = Student.query.filter_by(student_fname=first_name).first()
    
    if student:
        return student.student_id
    else:
        print(f"Warning: Student with first name {first_name} not found in the database!")
        return np.nan



def insert_data_to_db(csv_file_path, excel_file_path):
    # Extract floor ID from the excel file path
    floor_name = os.path.basename(excel_file_path).split('_')[1]
    floor_id = int(floor_name)

    # Extract collection name from the CSV file path (before the dot)
    collection_name = os.path.basename(csv_file_path).split('.')[0].replace('_edited', '')

    # Check if collection exists in the database
    collection = Collections.query.filter_by(collection=collection_name).first()
    if collection is None:
        print(f"Warning: Collection with name {collection_name} not found!")
        collection_id = None
    else:
        collection_id = collection.collection_id

    # Read the CSV file into a DataFrame
    df = pd.read_csv(csv_file_path)
    inserted_count = 0  # Counter for successfully inserted records

    # Iterate over the rows in the DataFrame
    for _, row in df.iterrows():
        # Ensure that 'student_id' is in the row and is not NaN
        if 'student_id' not in row or pd.isna(row['student_id']):
            print(f"Error: Missing student ID in row for {row['Name']}")
            continue  # Skip rows with missing student ID

        student_id = row['student_id']  # Use the student_id directly from the row

        # Convert the date and datetime columns to proper Python datetime objects
        try:
            date = datetime.strptime(str(row['date']), '%Y-%m-%d').date()  # Ensure date is in YYYY-MM-DD format
            start_time = datetime.strptime(str(row['Start DateTime']), '%Y-%m-%d %H:%M:%S')
            end_time = datetime.strptime(str(row['End DateTime']), '%Y-%m-%d %H:%M:%S')
        except ValueError as e:
            print(f"Error parsing date/time for student {student_id}: {e}")
            continue  # Skip rows with invalid date/time formats

        # Check if a record with the same student_id, date, and start_time already exists
        existing_record = ShelfReading.query.filter_by(
            date=date,
            start_time=start_time,
            student_id=student_id
        ).first()

        if existing_record is None:
            # Create a new record if no existing record was found
            new_record = ShelfReading(
                date=date,
                start_time=start_time,
                end_time=end_time,
                duration=row['Duration'],
                shelves_completed=row['shelves_completed'],
                start_call=row['start_call'],
                end_call=row['end_call'],
                student_id=row['student_id'],
                floor_id=floor_id,
                collection_id=collection_id
            )
            db.session.add(new_record)  # Add the new record to the session
            db.session.commit()
            print(f"Inserted new record for student ID {row['student_id']} at floor {floor_id} and collection {collection_name}.")
            inserted_count += 1  # Increment count for successful insertions
        else:
            # If a duplicate is found, skip inserting
            print(f"Duplicate found for student {row['student_id']} on {row['date']} at {row['Start DateTime']} - Skipping insert.")

    # Return a summary of the insertion process
    return f"{inserted_count} records successfully inserted into the database."

            
if __name__ == '__main__':
    app.run(debug=True)

