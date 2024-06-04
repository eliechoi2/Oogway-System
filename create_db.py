from flask import session

from app import app, db
from models import *
import datetime as dt
#from werkzeug.security import generate_password_hash
import numpy as np

with app.app_context():
    db.drop_all()
    db.create_all()

    # creating test variables for the student table
    student = [
        ['1234567890', 'Eric', 'Kim', 'email@gmail.com', '3012335483', 'password', 0, 50, 1],
        ['1239997890', 'Elie', 'Choi', 'elie@gmail.com', np.nan , 'password2', 0, 50, 1]
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

    manager = [1, 'Man', 'Ager', 'manager@gmail.com', '2934935483', 'man_password']

    print(manager[0], 'inserted into table')
    in_manager = Manager(
        manager_id=manager[0],
        manager_fname=manager[1],
        manager_lname=manager[2],
        manager_email=manager[3],
        manager_phone=manager[4],
        manager_password=manager[5]
    )

    db.session.add(in_manager)
    db.session.commit()


# test variables for levels table ( will likely translate to final)

    levels = [
        [1, 100, 'Bronze I'],
        [2, 150, 'Bronze II'],
        [3, 200, 'Bronze III']
    ]

    for i in levels:
        print(i[2], 'inserted into table')
        in_levels = Levels(
            level = i[0],
            xp_total_needed = i[1],
            level_id = i[2]
        )

        db.session.add(in_levels)
        db.session.commit()

    # test variables for collection table
    collections = [
        ['st_PR', 'Stack', 'PR'],
        ['st_PS', 'Stack', 'PS']
    ]

    for i in collections:
        print(i[0], 'inserted into table')
        in_collection = Collection(
            collection_id=i[0],
            category=i[1],
            stack_alph=i[2]
        )

        db.session.add(in_collection)
        db.session.commit()


    # creating test variables for floor table
    floors = ['01', '02', '03', '04', '05', '06', '07']
    for i in floors:
        in_floor = Floor(i)
        db.session.add(in_floor)
        db.session.commit()

    # creating test variables for location table
    location = [
        ['7stPR', 'st_PR', '07'],
        ['7stPS', 'st_PS', '07']
    ]

    for i in location:
        in_location = Location(
            location_id=i[0],
            collection_id=i[1],
            floor_id=i[2]
        )
        db.session.add(in_location)
        db.session.commit()


    # creating test variables for in house table
    in_house = [
        ['2024-01-01', 600, 1000, 10, '1234567890', '7stPR'],
        ['2024-01-02', 700, 1500, 5, '1239997890', '7stPS']
    ]


    for i in in_house:
        in_in_house = InHouse(
            date=dt.datetime.strptime(i[0], '%Y-%m-%d').date(),
            start_time=dt.timedelta(i[1]),
            end_time=dt.timedelta(i[2]),
            total_retrieved=i[3],
            student_id=i[4],
            location_id=i[5]
        )
        db.session.add(in_in_house)
        db.session.commit()
