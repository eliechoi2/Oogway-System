from flask_sqlalchemy import SQLAlchemy 
from flask_login import UserMixin
db = SQLAlchemy()

# table for admin information
class Admin(db.Model):
    __tablename__ = 'ADMIN'
    # student id will be used as PK and a main login identifier
    admin_id = db.Column(db.Integer, primary_key=True)
    admin_fname = db.Column(db.VARCHAR(50), nullable=False)
    admin_lname = db.Column(db.VARCHAR(50), nullable=False)
    admin_email = db.Column(db.VARCHAR(100), nullable=False, unique=True)
    admin_phone = db.Column(db.CHAR(12), nullable=True)
    admin_password = db.Column(db.VARCHAR(30), nullable=False)

    # constructor for admin object
    def __init__(self, admin_id, admin_fname, admin_lname, admin_email, admin_phone, admin_password):
        self.admin_id = admin_id
        self.admin_fname = admin_fname
        self.admin_lname = admin_lname
        self.admin_email = admin_email
        self.admin_phone = admin_phone
        self.admin_password = admin_password

    def __repr__(self):
        return f"User ID: {self.admin_fname} {self.admin_lname}"

# table for admin information
class supervisor(db.Model):
    __tablename__ = 'supervisor'
    # student id will be used as PK and a main login identifier
    supervisor_id = db.Column(db.Integer, primary_key=True)
    supervisor_fname = db.Column(db.VARCHAR(50), nullable=False)
    supervisor_lname = db.Column(db.VARCHAR(50), nullable=False)
    supervisor_email = db.Column(db.VARCHAR(100), nullable=False, unique=True)
    supervisor_phone = db.Column(db.CHAR(12), nullable=True)
    supervisor_password = db.Column(db.VARCHAR(30), nullable=False)

    # constructor for supervisor object
    def __init__(self, supervisor_id, supervisor_fname, supervisor_lname, supervisor_email, supervisor_phone, supervisor_password):
        self.supervisor_id = supervisor_id
        self.supervisor_fname = supervisor_fname
        self.supervisor_lname = supervisor_lname
        self.supervisor_email = supervisor_email
        self.supervisor_phone = supervisor_phone
        self.supervisor_password = supervisor_password

    def __repr__(self):
        return f"User ID: {self.supervisor_fname} {self.supervisor_lname}"



class Student(db.Model):
    __tablename__ = 'STUDENT'
    student_id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    student_fname = db.Column(db.VARCHAR(50), nullable=False)
    student_lname = db.Column(db.VARCHAR(50), nullable=False)
    student_email = db.Column(db.VARCHAR(100), nullable=False, unique=True)
    student_username = db.Column(db.VARCHAR(100), nullable=False, unique=True)
    student_password = db.Column(db.VARCHAR(30), nullable=False)
    student_hours = db.Column(db.Integer, nullable=False)
    
    def __repr__(self):
        return f'User ID: {self.student_id}, Name: {self.student_fname} {self.student_lname}'

    def get_id(self):
        return self.student_id

    
    
class Student_Data(db.Model):
    __tablename__ = 'STUDENT_DATA'
    data_id = db.Column(db.Integer, primary_key=True, autoincrement=True)   
    student_id = db.Column(db.Integer, db.ForeignKey("STUDENT.student_id", ondelete="CASCADE"), nullable=False)
    task_id = db.Column(db.Integer, db.ForeignKey("TASKS.task_id"), nullable=False)  # New field for task association
    total_shelfreads = db.Column(db.Integer, nullable=False)
    total_problem_items = db.Column(db.Integer, nullable=False)
    total_in_house = db.Column(db.Integer, nullable=False)
    total_shelving = db.Column(db.Integer, nullable=False)
    total_holds_list = db.Column(db.Integer, nullable=False)
    total_ill = db.Column(db.Integer, nullable=False)

    def __init__(self, student_id, task_id, total_shelfreads, total_problem_items, total_in_house, total_shelving, total_holds_list, total_ill):
        self.student_id = student_id
        self.task_id = task_id
        self.total_shelfreads = total_shelfreads
        self.total_problem_items = total_problem_items
        self.total_in_house = total_in_house
        self.total_shelving = total_shelving
        self.total_holds_list = total_holds_list
        self.total_ill = total_ill

    def __repr__(self):
        return f'Student_Data ID: {self.data_id}, Student ID: {self.student_id}, Task ID: {self.task_id}'

    

#This is complete
class User(UserMixin, db.Model):
    __tablename__ = "USER"

    user_id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(100), unique=True)
    first_name = db.Column(db.String(30))
    last_name = db.Column(db.String(50))
    email = db.Column(db.String(100), unique=True)
    password = db.Column(db.String(100))
    role = db.Column(db.String(20))

    def __init__(self, username, first_name, last_name, email, password, role='PUBLIC'):
        self.username = username
        self.first_name = first_name
        self.last_name = last_name
        self.email = email
        self.password = password
        self.role = role

    # Function for flask_login supervisor to provider a user ID to know who is logged in
    def get_id(self):
        return(self.user_id)

    def __repr__(self):
        return f"{self.first_name} {self.last_name} ({self.username})"

# table for Levels
# DONEEE
class Levels(db.Model):
    __tablename__ = 'LEVELS'
    level_id = db.Column(db.Integer, primary_key=True)
    level = db.Column(db.String(50), nullable=False)
    xp_total_needed = db.Column(db.Integer, nullable=False)

    # constuctor for Levels object
    def __init__(self, level, xp_total_needed, level_id):
        self.level = level
        self.xp_total_needed = xp_total_needed
        self.level_id = level_id

    # string representation of created Levels object
    def __repr__(self):
        return f'{self.level}: {self.xp_total_needed} {self.level_id}'

#need to populate the collection database from the admin side
class Collections(db.Model):
    __tablename__ = 'COLLECTIONS'
    collection_id = db.Column(db.CHAR(5), primary_key=True)
    collection = db.Column(db.VARCHAR(20), nullable=False) 
    floor_id = db.Column(db.Integer, db.ForeignKey('FLOOR.floor_id'))

    # constructor for Collection object
    def __init__(self, collection_id, collection, floor_id):
        self.collection_id = collection_id
        self.collection = collection 
        self.floor_id = floor_id

    def __repr__(self):
        return f'{self.collection_id}: {self.collection} {self.floor_id}'

# table for floor
#Need to populate the floor database from the admin side
class Floor(db.Model):
    __tablename__ = 'FLOOR'
    floor_id = db.Column(db.Integer, primary_key=True)
    floor = db.Column(db.VARCHAR(100), nullable=False)

    # constructor for Floor object
    def __init__(self, floor_id, floor):
        self.floor_id = floor_id
        self.floor = floor

    # string representation
    def __repr__(self):
        return f'{self.floor_id}'


# table for location
class Location(db.Model):
    __tablename__ = 'LOCATION'
    location_id = db.Column(db.CHAR(5), primary_key=True)
    # both collection_id and floor_id are FKs
    collection_id = db.Column(db.CHAR(5), db.ForeignKey('COLLECTIONS.collection_id'))
    floor_id = db.Column(db.CHAR(2), db.ForeignKey('FLOOR.floor_id'))

    # constructor for Location object
    def __init__(self, location_id, collection_id, floor_id):
        self.location_id = location_id
        self.collection_id = collection_id
        self.floor_id = floor_id

    # string representation
    def __repr__(self):
        return f'{self.location_id}: {self.collection_id} {self.floor_id}'

# table for tasks
#DONE!!
class Tasks(db.Model):
    __tablename__ = 'TASKS'
    task_id = db.Column(db.Integer, primary_key=True, nullable=False)
    task = db.Column(db.String(50), nullable=False)

    def __init__(self, task_id, task):
        self.task_id = task_id
        self.task = task

    def __repr__(self):
        return f'{self.task_id}: {self.task}'


class InHouse(db.Model):
    __tablename__ = 'IN_HOUSE'
    date = db.Column(db.DATE, primary_key=True, nullable=False)
    total_in_house = db.Column(db.Integer, nullable=False)
    student_id = db.Column(db.Integer, db.ForeignKey('STUDENT.student_id'), primary_key=True, nullable=False)

    def __init__(self, date, total_in_house, student_id):
        self.date = date
        self.total_in_house = total_in_house
        self.student_id = student_id

    def __repr__(self):
        return f'{self.student_id}: {self.date} {self.total_in_house}'



# table for shelf reading
class ShelfReading(db.Model):
    __tablename__ = 'SHELF_READING'
    date = db.Column(db.DATE, primary_key=True, nullable=False)
    start_time = db.Column(db.DateTime, primary_key=True, nullable=False)
    end_time = db.Column(db.DateTime, nullable=False)
    duration = db.Column(db.Float, nullable=False)
    shelfreads_completed = db.Column(db.Integer, nullable=False)
    start_call = db.Column(db.VARCHAR(20), nullable=False)
    end_call = db.Column(db.VARCHAR(20), nullable=False)
    # student_id FK referencing STUDENT table
    student_id = db.Column(db.Integer, db.ForeignKey('STUDENT.student_id'), primary_key=True, nullable=False)
    # location_id FK referencing LOCATION table
    floor_id = db.Column(db.CHAR(5), db.ForeignKey('FLOOR.floor_id'), nullable=False)
    collection_id = db.Column(db.CHAR(5), db.ForeignKey('COLLECTIONS.collection_id'), nullable=False)

    # creating Shelf Reading logging object
    def __init__(self, date, start_time, end_time, duration, shelfreads_completed, start_call, end_call, student_id, floor_id, collection_id):
        self.date = date
        self.start_time = start_time
        self.end_time = end_time
        self.duration = duration
        self.shelfreads_completed = shelfreads_completed
        self.start_call = start_call
        self.end_call = end_call
        self.student_id = student_id
        self.floor_id = floor_id
        self.collection_id = collection_id

    student = db.relationship('Student', backref='shelf_readings', lazy='joined')
    collection = db.relationship('Collections', backref='shelf_readings', lazy='joined')
    
    # string representation
    def __repr__(self):
        return (f'{self.student_id}: {self.date} {self.start_time} {self.end_time} {self.duration} '
                f'{self.shelfreads_completed} {self.start_call} {self.end_call} {self.floor_id} {self.collection_id}')


class Shelving(db.Model):
    __tablename__ = 'SHELVING'
    date = db.Column(db.DATE, primary_key=True, nullable=False)
    total_shelving = db.Column(db.Integer, nullable=False)
    student_id = db.Column(db.Integer, db.ForeignKey('STUDENT.student_id'), primary_key=True, nullable=False)

    def __init__(self, date, total_shelving, student_id):
        self.date = date
        self.total_shelving = total_shelving
        self.student_id = student_id

    def __repr__(self):
        return f'{self.student_id}: {self.date} {self.total_shelving}'



# table for ILL
class ILLList(db.Model):
    __tablename__ = 'ILL'
    date = db.Column(db.DATE, primary_key=True, nullable=False)
    total_ill = db.Column(db.Integer, nullable=False)
    student_id = db.Column(db.Integer, db.ForeignKey('STUDENT.student_id'), primary_key=True, nullable=False)

    # creating In House logging object
    def __init__(self, date, total_ill, student_id):
        self.date = date
        self.total_ill = total_ill
        self.student_id = student_id

    # string representation
    def __repr__(self):
        return f'{self.student_id}: {self.date} {self.total_ill}'



# table for rm list
class RmList(db.Model):
    __tablename__ = 'RM_LIST'
    date = db.Column(db.DATE, primary_key=True, nullable=False)
    total_rm = db.Column(db.Integer, nullable=False)
    student_id = db.Column(db.Integer, db.ForeignKey('STUDENT.student_id'), primary_key=True, nullable=False)

    # creating rm logging object
    def __init__(self, date, total_rm, student_id):
        self.date = date
        self.total_rm = total_rm
        self.student_id = student_id

    # string representation
    def __repr__(self):
        return f'{self.student_id}: {self.date} {self.total_rm}'



# table for hold list
class HoldList(db.Model):
    __tablename__ = 'HOLD_LIST'
    date = db.Column(db.DATE, primary_key=True, nullable=False)
    total_holds = db.Column(db.Integer, nullable=False)
    student_id = db.Column(db.Integer, db.ForeignKey('STUDENT.student_id'), primary_key=True, nullable=False)

    # creating hold list logging object
    def __init__(self, date, total_holds, student_id):
        self.date = date
        self.total_holds = total_holds
        self.student_id = student_id

    # string representation
    def __repr__(self):
        return f'{self.student_id}: {self.date}{self.total_holds}'



# table for problem list
class ProblemList(db.Model):
    __tablename__ = 'PROBLEM_LIST'
    problem_id = db.Column(db.CHAR(5), primary_key=True, nullable=False)
    problem_description = db.Column(db.VARCHAR(100), nullable=False)

    # creating problem list object
    def __init__(self, problem_id, problem_description):
        self.problem_id = problem_id
        self.problem_description = problem_description

    # string representation
    def __repr__(self):
        return f'{self.problem_id}: {self.problem_description}'


# table for problem logging
class Problem(db.Model):
    __tablename__ = 'PROBLEM'
    student_id = db.Column(db.Integer, db.ForeignKey('STUDENT.student_id'), primary_key=True, nullable=False)
    date = db.Column(db.DATE, primary_key=True, nullable=False)
    call_no = db.Column(db.VARCHAR, primary_key=True, nullable=False)
    problem_id = db.Column(db.CHAR(5), db.ForeignKey('PROBLEM_LIST.problem_id'), nullable=True)
    total_problems = db.Column(db.Integer, nullable=False)

    # creating problem object
    def __init__(self, student_id, date, call_no, problem_id, total_problems):
        self.student_id = student_id
        self.date = date
        self.call_no = call_no
        self.problem_id = problem_id
        self.total_problems = total_problems

    # string representation
    def __repr__(self):
        return f'{self.student_id}: {self.date} {self.call_no} {self.problem_id}'

