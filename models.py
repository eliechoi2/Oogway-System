# from . import db

# class User(db.Model):
#     id = db.Column(db.Integer, primary_key=True)
#     email = db.Column(db.String(100), unique=True)
#     password = db.Column(db.String(100))
#     fname = db.Column(db.String(1000))
#     lname = db.Column(db.String(1000))

# importing packages
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import CheckConstraint
from flask_login import UserMixin
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

    # constructor for Manager object
    def __init__(self, manager_id, manager_fname, manager_lname, manager_email, manager_phone):
        self.manager_id = manager_id
        self.manager_fname = manager_fname
        self.manager_lname = manager_lname
        self.manager_email = manager_email
        self.manager_phone = manager_phone

    # string representation of created Manager object
    def __repr__(self):
        return f'{self.manager_id}: {self.manager_fname} {self.manager_lname}'



# table for student information
class Student(db.Model):
    __tablename__ = 'STUDENT'
    # student id will be used as PK and a main login identifier
    student_id = db.Column(db.Integer, primary_key=True)
    student_fname = db.Column(db.VARCHAR(50), nullable=False)
    student_lname = db.Column(db.VARCHAR(50), nullable=False)
    student_email = db.Column(db.VARCHAR(100), nullable=False, unique=True)
    student_phone = db.Column(db.CHAR(12), nullable=True)
    # xp leveling information
    xp_current = db.Column(db.Integer, nullable=False)
    xp_needed = db.Column(db.Integer, nullable=False)
    # FK referencing xp levels table
    student_lvl = db.Column(db.Integer, db.ForeignKey('LEVELS.level'), nullable=False)

    # constructor for Student object
    def __init__(self, student_id, student_fname, student_lname, student_email, student_phone):
        self.student_id = student_id
        self.student_fname = student_fname
        self.student_lname = student_lname
        self.student_email = student_email
        self.student_phone = student_phone

    # string representation of created Student object
    def __repr__(self):
        return f'{self.student_id}: {self.student_fname} {self.student_lname}'



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



# table for Floors
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
    student_id = db.Column(db.Integer, db.ForeignKey('STUDENT.student_id'), primary_key=True, nullable=False)
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
    student_id = db.Column(db.Integer, db.ForeignKey('STUDENT.student_id'), primary_key=True, nullable=False)
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



# table for shalving
class Shelving(db.Model):
    __tablename__ = 'SHELVING'
    date = db.Column(db.DATE, primary_key=True, nullable=False)
    start_time = db.Column(db.DateTime, primary_key=True, nullable=False)
    end_time = db.Column(db.DateTime, nullable=False)
    total_shelving = db.Column(db.Integer, nullable=False)
    # student_id FK referencing STUDENT table
    student_id = db.Column(db.Integer, db.ForeignKey('STUDENT.student_id'), primary_key=True, nullable=False)
    # location_id FK referencing LOCATION table
    location_id = db.Column(db.CHAR(5), db.ForeignKey('LOCATION.location_id'), nullable=False)

    # creating In House logging object
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