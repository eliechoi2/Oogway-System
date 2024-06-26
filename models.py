# from . import db

# class User(db.Model):
#     id = db.Column(db.Integer, primary_key=True)
#     email = db.Column(db.String(100), unique=True)
#     password = db.Column(db.String(100))
#     fname = db.Column(db.String(1000))
#     lname = db.Column(db.String(1000))

# importing packages
from flask_sqlalchemy import SQLAlchemy
db = SQLAlchemy()


# table for manager information
class Manager(db.Model):
    __tablename__ = 'MANAGER'
    # student id will be used as PK and a main login identifier
    manager_id = db.Column(db.Integer, primary_key=True)
    manager_fname = db.Column(db.VARCHAR(50), nullable=False)
    manager_lname = db.Column(db.VARCHAR(50), nullable=False)
    manager_email = db.Column(db.VARCHAR(100), nullable=False, unique=True)
    manager_phone = db.Column(db.CHAR(12), nullable=True)
    manager_password = db.Column(db.VARCHAR(30), nullable=False)

    # constructor for Manager object
    def __init__(self, manager_id, manager_fname, manager_lname, manager_email, manager_phone, manager_password):
        self.manager_id = manager_id
        self.manager_fname = manager_fname
        self.manager_lname = manager_lname
        self.manager_email = manager_email
        self.manager_phone = manager_phone
        self.manager_password = manager_password

    # flask_login needs a get_id function to provide who is logged in
    # def get_id(self):
    #     return self.manager_id
    def __repr__(self):
        return f"User ID: {self.manager_fname} {self.manager_lname}"



# table for student information
class Student(db.Model):
    __tablename__ = 'STUDENT'
    # student id will be used as PK and a main login identifier
    student_id = db.Column(db.CHAR(10), primary_key=True)
    student_fname = db.Column(db.VARCHAR(50), nullable=False)
    student_lname = db.Column(db.VARCHAR(50), nullable=False)
    student_email = db.Column(db.VARCHAR(100), nullable=False, unique=True)
    student_phone = db.Column(db.CHAR(12), nullable=True)
    student_password = db.Column(db.VARCHAR(30), nullable=False)
    # xp leveling information
    xp_current = db.Column(db.Integer, nullable=False)
    xp_needed = db.Column(db.Integer, nullable=False)
    # FK referencing xp levels table
    student_lvl = db.Column(db.Integer, db.ForeignKey('LEVELS.level'), nullable=False)

    # constructor for Student object
    def __init__(self, student_id, student_fname, student_lname, student_email, student_phone, student_password, xp_current, xp_needed, student_lvl):
        self.student_id = student_id
        self.student_fname = student_fname
        self.student_lname = student_lname
        self.student_email = student_email
        self.student_phone = student_phone
        self.student_password = student_password
        self.xp_current = xp_current
        self.xp_needed = xp_needed
        self.student_lvl = student_lvl

    # flask_login needs a get_id function to provide who is logged in
    def get_id(self):
        return self.student_id
    def __repr__(self):
        return f'User ID: {self.student_id}'



# table for Levels
class Levels(db.Model):
    __tablename__ = 'LEVELS'
    # level used as PK
    level = db.Column(db.Integer, primary_key=True)
    xp_total_needed = db.Column(db.Integer, nullable=False)
    level_id = db.Column(db.VARCHAR(20), nullable=False)

    # constuctor for Levels object
    def __init__(self, level, xp_total_needed, level_id):
        self.level = level
        self.xp_total_needed = xp_total_needed
        self.level_id = level_id

    # string representation of created Levels object
    def __repr__(self):
        return f'{self.level}: {self.xp_total_needed} {self.level_id}'



class Collection(db.Model):
    __tablename__ = 'COLLECTION'
    collection_id = db.Column(db.CHAR(5), primary_key=True)
    category = db.Column(db.VARCHAR(20), nullable=False)
    # can be null as alphabet only pertains to collections of stacks
    stack_alph = db.Column(db.VARCHAR(10), nullable=True)

    # constructor for Collection object
    def __init__(self, collection_id, category, stack_alph):
        self.collection_id = collection_id
        self.category = category
        self.stack_alph = stack_alph

    # string representation
    def __repr__(self):
        return f'{self.collection_id}: {self.category} {self.stack_alph}'



# table for floor
class Floor(db.Model):
    __tablename__ = 'FLOOR'
    floor_id = db.Column(db.CHAR(2), primary_key=True)

    # constructor for Floor object
    def __init__(self, floor_id):
        self.floor_id = floor_id

    # string representation
    def __repr__(self):
        return f'{self.floor_id}'



# table for location
class Location(db.Model):
    __tablename__ = 'LOCATION'
    location_id = db.Column(db.CHAR(5), primary_key=True)
    # both collection_id and floor_id are FKs
    collection_id = db.Column(db.CHAR(5), db.ForeignKey('COLLECTION.collection_id'))
    floor_id = db.Column(db.CHAR(2), db.ForeignKey('FLOOR.floor_id'))

    # constructor for Location object
    def __init__(self, location_id, collection_id, floor_id):
        self.location_id = location_id
        self.collection_id = collection_id
        self.floor_id = floor_id

    # string representation
    def __repr__(self):
        return f'{self.location_id}: {self.collection_id} {self.floor_id}'



# table for in house
class InHouse(db.Model):
    __tablename__ = 'IN_HOUSE'
    date = db.Column(db.DATE, primary_key=True, nullable=False)
    start_time = db.Column(db.DateTime, primary_key=True, nullable=False)
    end_time = db.Column(db.DateTime, nullable=False)
    total_retrieved = db.Column(db.Integer, nullable=False)
    # student_id FK referencing STUDENT table
    student_id = db.Column(db.CHAR(10), db.ForeignKey('STUDENT.student_id'), primary_key=True, nullable=False)
    # location_id FK referencing LOCATION table
    location_id = db.Column(db.CHAR(5), db.ForeignKey('LOCATION.location_id'), nullable=False)

    # creating In House logging object
    def __init__(self, date, start_time, end_time, total_retrieved, student_id, location_id):
        self.date = date
        self.start_time = start_time
        self.end_time = end_time
        self.total_retrieved = total_retrieved
        self.student_id = student_id
        self.location_id = location_id

    # string representation
    def __repr__(self):
        return f'{self.student_id}: {self.date} {self.start_time} {self.end_time} {self.total_retrieved} {self.location_id}'



# table for shelf reading
class ShelfReading(db.Model):
    __tablename__ = 'SHELF_READING'
    date = db.Column(db.DATE, primary_key=True, nullable=False)
    start_time = db.Column(db.DateTime, primary_key=True, nullable=False)
    end_time = db.Column(db.DateTime, nullable=False)
    shelves_completed = db.Column(db.Integer, nullable=False)
    start_call = db.Column(db.VARCHAR(20), nullable=False)
    end_call = db.Column(db.VARCHAR(20), nullable=False)
    # student_id FK referencing STUDENT table
    student_id = db.Column(db.CHAR(10), db.ForeignKey('STUDENT.student_id'), primary_key=True, nullable=False)
    # location_id FK referencing LOCATION table
    location_id = db.Column(db.CHAR(5), db.ForeignKey('LOCATION.location_id'), nullable=False)

    # creating Shelf Reading logging object
    def __init__(self, date, start_time, end_time, shelves_completed, start_call, end_call, student_id, location_id):
        self.date = date
        self.start_time = start_time
        self.end_time = end_time
        self.shelves_completed = shelves_completed
        self.start_call = start_call
        self.end_call = end_call
        self.student_id = student_id
        self.location_id = location_id

    # string representation
    def __repr__(self):
        return (f'{self.student_id}: {self.date} {self.start_time} {self.end_time} '
                f'{self.shelves_completed} {self.start_call} {self.end_call} {self.location_id}')



# table for shelving
class Shelving(db.Model):
    __tablename__ = 'SHELVING'
    date = db.Column(db.DATE, primary_key=True, nullable=False)
    start_time = db.Column(db.DateTime, primary_key=True, nullable=False)
    end_time = db.Column(db.DateTime, nullable=False)
    total_shelving = db.Column(db.Integer, nullable=False)
    # student_id FK referencing STUDENT table
    student_id = db.Column(db.CHAR(10), db.ForeignKey('STUDENT.student_id'), primary_key=True, nullable=False)
    # location_id FK referencing LOCATION table
    location_id = db.Column(db.CHAR(5), db.ForeignKey('LOCATION.location_id'), nullable=False)

    # creating shelving logging object
    def __init__(self, date, start_time, end_time, total_shelving, student_id, location_id):
        self.date = date
        self.start_time = start_time
        self.end_time = end_time
        self.total_shelving = total_shelving
        self.student_id = student_id
        self.location_id = location_id

    # string representation
    def __repr__(self):
        return f'{self.student_id}: {self.date} {self.start_time} {self.end_time} {self.total_shelving} {self.location_id}'



# table for ILL
class ILL(db.Model):
    __tablename__ = 'ILL'
    date = db.Column(db.DATE, primary_key=True, nullable=False)
    start_time = db.Column(db.DateTime, primary_key=True, nullable=False)
    end_time = db.Column(db.DateTime, nullable=False)
    total_ill = db.Column(db.Integer, nullable=False)
    # student_id FK referencing STUDENT table
    student_id = db.Column(db.CHAR(10), db.ForeignKey('STUDENT.student_id'), primary_key=True, nullable=False)
    # location_id FK referencing LOCATION table
    location_id = db.Column(db.CHAR(5), db.ForeignKey('LOCATION.location_id'), nullable=False)

    # creating In House logging object
    def __init__(self, date, start_time, end_time, total_ill, student_id, location_id):
        self.date = date
        self.start_time = start_time
        self.end_time = end_time
        self.total_ill = total_ill
        self.student_id = student_id
        self.location_id = location_id

    # string representation
    def __repr__(self):
        return f'{self.student_id}: {self.date} {self.start_time} {self.end_time} {self.total_ill} {self.location_id}'



# table for rm list
class RmList(db.Model):
    __tablename__ = 'RM_LIST'
    date = db.Column(db.DATE, primary_key=True, nullable=False)
    start_time = db.Column(db.DateTime, primary_key=True, nullable=False)
    end_time = db.Column(db.DateTime, nullable=False)
    total_rm = db.Column(db.Integer, nullable=False)
    # student_id FK referencing STUDENT table
    student_id = db.Column(db.CHAR(10), db.ForeignKey('STUDENT.student_id'), primary_key=True, nullable=False)
    # location_id FK referencing LOCATION table
    location_id = db.Column(db.CHAR(5), db.ForeignKey('LOCATION.location_id'), nullable=False)

    # creating rm logging object
    def __init__(self, date, start_time, end_time, total_rm, student_id, location_id):
        self.date = date
        self.start_time = start_time
        self.end_time = end_time
        self.total_rm = total_rm
        self.student_id = student_id
        self.location_id = location_id

    # string representation
    def __repr__(self):
        return f'{self.student_id}: {self.date} {self.start_time} {self.end_time} {self.total_rm} {self.location_id}'



# table for hold list
class HoldList(db.Model):
    __tablename__ = 'HOLD_LIST'
    date = db.Column(db.DATE, primary_key=True, nullable=False)
    start_time = db.Column(db.DateTime, primary_key=True, nullable=False)
    end_time = db.Column(db.DateTime, nullable=False)
    total_holds = db.Column(db.Integer, nullable=False)
    # student_id FK referencing STUDENT table
    student_id = db.Column(db.CHAR(10), db.ForeignKey('STUDENT.student_id'), primary_key=True, nullable=False)
    # location_id FK referencing LOCATION table
    location_id = db.Column(db.CHAR(5), db.ForeignKey('LOCATION.location_id'), nullable=False)

    # creating hold list logging object
    def __init__(self, date, start_time, end_time, total_holds, student_id, location_id):
        self.date = date
        self.start_time = start_time
        self.end_time = end_time
        self.total_holds = total_holds
        self.student_id = student_id
        self.location_id = location_id

    # string representation
    def __repr__(self):
        return f'{self.student_id}: {self.date} {self.start_time} {self.end_time} {self.total_holds} {self.location_id}'



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
    student_id = db.Column(db.CHAR(10), db.ForeignKey('STUDENT.student_id'), primary_key=True, nullable=False)
    date = db.Column(db.DATE, primary_key=True, nullable=False)
    call_no = db.Column(db.VARCHAR, primary_key=True, nullable=False)
    problem_id = db.Column(db.CHAR(5), db.ForeignKey('PROBLEM_LIST.problem_id'), nullable=True)
    comments = db.Column(db.VARCHAR(100), nullable=True)

    # creating problem object
    def __init__(self, student_id, date, call_no, problem_id, comments):
        self.student_id = student_id
        self.date = date
        self.call_no = call_no
        self.problem_id = problem_id
        self.comments = comments

    # string representation
    def __repr__(self):
        return f'{self.student_id}: {self.date} {self.call_no} {self.problem_id} {self.comments}'

