from flask import session

from app import app, db
from models import *
import datetime as dt

with app.app_context():
    db.drop_all()
    db.create_all()

    # creating test variables for the student table
    student = [
        ['1234567890', 'Eric', 'Kim', 'email@gmail.com', '3012335483', 'password', 0, 50, 1],
        ['1239997890', 'Elie', 'Choi', 'elie@gmail.com', '3943890' , 'password2', 0, 50, 1]
    ]

    for i in student:
        print(i[0], 'inserted into table')
        in_student = Student(
            student_id = i[0],
            student_fname = i[1],
            student_lname = i[2],
            student_email = i[3],
            student_phone = i[4],
            student_password = i[5],
            xp_current = i[6],
            xp_needed = i[7],
            student_lvl = i[8]
        )
        db.session.add(in_student)
        db.session.commit()


    # test variables for manager table

    # print(manager[0], 'inserted into table')
    # in_manager = Manager(
    #     manager_id=manager[0],
    #     manager_fname=manager[1],
    #     manager_lname=manager[2],
    #     manager_email=manager[3],
    #     manager_phone=manager[4],
    #     manager_password=manager[5],
    # )
    
    for each_manager in manager:
        print(f'{each_manager["manager_fname"]} {each_manager["manager_lname"]} inserted into Manager')
        a_manager = Manager(manager_id=each_manager["manager_id"],manager_fname=each_manager["manager_fname"],
                            manager_lname=each_manager["manager_lname"], manager_email=each_manager["manager_email"],
                            manager_phone=each_manager["manager_phone"], manager_password=each_manager["manager_password"])
        db.session.add(a_manager)
        db.session.commit()


