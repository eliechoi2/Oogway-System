from app import app, db
from models import User, Levels, Tasks, Floor, Collections, ProblemList, Student
from werkzeug.security import generate_password_hash

with app.app_context():
    db.drop_all()
    db.create_all()

    users = [
        {'username': 'student', 'email': 'student@umd.edu', 'first_name':'student', 'last_name':'student',
            'password': generate_password_hash('studentpw', method='pbkdf2:sha256'), 'role':'STUDENT'},
        {'username': 'amykim', 'email': 'amykim@umd.edu', 'first_name':'Amy', 'last_name':'Kim',
            'password': generate_password_hash('amykim', method='pbkdf2:sha256'), 'role':'supervisor'},
        {'username': 'admin', 'email': 'admin@umd.edu', 'first_name':'admin', 'last_name':'admin',
            'password': generate_password_hash('adminpw', method='pbkdf2:sha256'), 'role':'ADMIN'},
    ]

    for each_user in users:
        print(f'{each_user["username"]} inserted into user')
        a_user = User(username=each_user["username"], email=each_user["email"], first_name=each_user["first_name"],
                      last_name=each_user["last_name"], password=each_user["password"], role=each_user["role"])
        db.session.add(a_user)
    db.session.commit()
    
    levels = [
    {'level': 'Average', 'xp_total_needed': 0, 'level_id': 1},
    {'level': 'Excellent', 'xp_total_needed': 100, 'level_id': 2},
    {'level': 'CMR Superstar', 'xp_total_needed': 500, 'level_id': 3}
    ]

    for each_level in levels:
        print(f'{each_level["level"]} inserted into levels')
        a_level = Levels(level=each_level["level"], xp_total_needed=each_level["xp_total_needed"], level_id=each_level["level_id"])
        db.session.add(a_level) 
    db.session.commit()
    
    tasks = [
        {'task_id' : 1, 'task' : 'Shelfreads'},
        {'task_id' : 2, 'task' : 'Problem Items'},
        {'task_id' : 3, 'task' : 'In-House'},
        {'task_id' : 4, 'task' : 'Shelving'},
        {'task_id' : 5, 'task' : 'Holds List'},
        {'task_id' : 6, 'task' : 'RM List'}
    ]
    
    for each_task in tasks:
        print(f'{each_task["task"]} inserted into tasks')
        a_task = Tasks(task_id=each_task["task_id"], task=each_task["task"])
        db.session.add(a_task)
    db.session.commit()
    
    floors = [
        {'floor_id' : 1, 'floor' : '3rd Floor'},
        {'floor_id' : 2, 'floor' : '4th Floor'},
        {'floor_id' : 3, 'floor' : '5th Floor'},
        {'floor_id' : 4, 'floor' : '6th Floor'},
        {'floor_id' : 5, 'floor' : '7th Floor'},
        {'floor_id' : 6, 'floor' : 'Others SR'}
    ]
    
    for each_floor in floors:
        print(f'{each_floor["floor"]} inserted into floors')
        a_floor = Floor(floor_id=each_floor["floor_id"], floor=each_floor["floor"])
        db.session.add(a_floor)
    db.session.commit()
    
    collections = [
        {'collection_id': '1', 'collection': 'Folio', 'floor_id': 1},
        {'collection_id': '2', 'collection': 'A Stacks', 'floor_id': 1},
        {'collection_id': '3', 'collection': 'B-BH Stacks', 'floor_id': 1},
        {'collection_id': '4', 'collection': 'BJ-BL Stacks', 'floor_id': 1},
        {'collection_id': '5', 'collection': 'BM-BX Stacks', 'floor_id': 1},
        {'collection_id': '6', 'collection': 'C Stacks', 'floor_id': 1},
        {'collection_id': '7', 'collection': 'D-DE Stacks', 'floor_id': 1},
        {'collection_id': '8', 'collection': 'DF-DX Stacks', 'floor_id': 1},
        {'collection_id': '9', 'collection': 'DS Stacks', 'floor_id': 1},
        {'collection_id': '10', 'collection': 'E Stacks', 'floor_id': 1},
        {'collection_id': '11', 'collection': 'F Stacks', 'floor_id': 1},
        {'collection_id': '12', 'collection': 'East Asia, China', 'floor_id': 1},
        {'collection_id': '13', 'collection': 'East Asia, Japan', 'floor_id': 1},
        {'collection_id': '14', 'collection': 'East Asia, Korea', 'floor_id': 1},
        
        {'collection_id': '15', 'collection': 'G-HN', 'floor_id': 3},

        {'collection_id': '16', 'collection': 'Folio', 'floor_id': 4},
        {'collection_id': '17', 'collection': 'HQ-HT Stacks', 'floor_id': 4},
        {'collection_id': '18', 'collection': 'HV-HX Stacks', 'floor_id': 4},
        {'collection_id': '19', 'collection': 'J Stacks', 'floor_id': 4},
        {'collection_id': '20', 'collection': 'K Stacks', 'floor_id': 4},
        {'collection_id': '21', 'collection': 'L', 'floor_id': 4},
        {'collection_id': '22', 'collection': 'M-N Stacks', 'floor_id': 4},
        {'collection_id': '23', 'collection': 'P Stacks', 'floor_id': 4},
        {'collection_id': '24', 'collection': 'PA-PF Stacks', 'floor_id': 4},
        {'collection_id': '25', 'collection': 'PG-PM Stacks', 'floor_id': 4},
        {'collection_id': '26', 'collection': 'PN-PQ Stacks', 'floor_id': 4},
 
        {'collection_id': '27', 'collection': 'Folio', 'floor_id': 5},
        {'collection_id': '28', 'collection': 'PN Stacks', 'floor_id': 5},
        {'collection_id': '29', 'collection': 'PQ Stacks', 'floor_id': 5},
        {'collection_id': '30', 'collection': 'PR Stacks', 'floor_id': 5},
        {'collection_id': '31', 'collection': 'PS Stacks', 'floor_id': 5},
        {'collection_id': '32', 'collection': 'PT Stacks', 'floor_id': 5},
        {'collection_id': '33', 'collection': 'PZ Stacks', 'floor_id': 5},
        {'collection_id': '34', 'collection': 'Q Stacks', 'floor_id': 5},
        {'collection_id': '35', 'collection': 'R Stacks', 'floor_id': 5},
        {'collection_id': '36', 'collection': 'S-Y Stacks', 'floor_id': 5},
        {'collection_id': '37', 'collection': 'Z Stacks', 'floor_id': 5},

        {'collection_id': '38', 'collection': 'Reference', 'floor_id': 6},
        {'collection_id': '39', 'collection': 'Media', 'floor_id': 6},
        {'collection_id': '40', 'collection': 'various places PQ 6000', 'floor_id': 6},
        {'collection_id': '41', 'collection': 'Popular', 'floor_id': 6},
        {'collection_id': '42', 'collection': 'Juvenile', 'floor_id': 6},
    ]

    for each_collection in collections:
        print(f'{each_collection["collection"]} inserted into collections')
        a_collection = Collections(
            collection_id=each_collection["collection_id"],
            collection=each_collection['collection'],
            floor_id=each_collection['floor_id']
        )
        db.session.add(a_collection)
    db.session.commit()
    
    problems_list = [
        {'problem_id' : 1, 'problem_description' : 'Faded Call Number'},
        {'problem_id' : 2, 'problem_description' : 'Peeling Call Number'},
        {'problem_id' : 3, 'problem_description' : 'Damaged/Ripped Call Number'},
        {'problem_id' : 4, 'problem_description' : 'Missing Call Number'}
    ]
    
    for each_problems_list in problems_list:
        print(f'{each_problems_list["problem_description"]} inserted into problems_list')
        a_problems_list = ProblemList (
            problem_id=each_problems_list["problem_id"],
            problem_description=each_problems_list["problem_description"],
        )
        db.session.add(a_problems_list)
    db.session.commit()
    
    students = [
        {'student_id': 1, 'student_fname': 'Dayri', 'student_lname': 'Almonte', 'student_email': 'dayri.almonte@gmail.com', 'student_username': 'dayri1', 'student_password': 'password1', 'student_hours' : 1},
        {'student_id': 2, 'student_fname': 'Kate', 'student_lname': 'Bartolotta', 'student_email': 'kate.bartolotta@gmail.com', 'student_username': 'kate2', 'student_password': 'password2', 'student_hours' : 1},
        {'student_id': 3, 'student_fname': 'Jane', 'student_lname': 'DeLashmutt', 'student_email': 'jane.delashmutt@gmail.com', 'student_username': 'jane3', 'student_password': 'password3', 'student_hours' : 1},
        {'student_id': 4, 'student_fname': 'Ella', 'student_lname': 'Gawitt', 'student_email': 'ella.gawitt@gmail.com', 'student_username': 'ella4', 'student_password': 'password4', 'student_hours' : 1},
        {'student_id': 5, 'student_fname': 'Mary', 'student_lname': 'Gunn', 'student_email': 'mary.gunn@gmail.com', 'student_username': 'mary5', 'student_password': 'password5', 'student_hours' : 1},
        {'student_id': 6, 'student_fname': 'Mohamed', 'student_lname': 'Kamara', 'student_email': 'mohamed.kamara@gmail.com', 'student_username': 'mohamed6', 'student_password': 'password6', 'student_hours' : 1},
        {'student_id': 7, 'student_fname': 'Kai', 'student_lname': 'Liang', 'student_email': 'kai.liang@gmail.com', 'student_username': 'kai7', 'student_password': 'password7', 'student_hours' : 1},
        {'student_id': 8, 'student_fname': 'Sophia', 'student_lname': 'Marrone', 'student_email': 'sophia.marrone@gmail.com', 'student_username': 'sophia8', 'student_password': 'password8', 'student_hours' : 1},
        {'student_id': 9, 'student_fname': 'Madison', 'student_lname': 'Pease', 'student_email': 'madison.pease@gmail.com', 'student_username': 'madison9', 'student_password': 'password9', 'student_hours' : 1},
        {'student_id': 10, 'student_fname': 'Nitish', 'student_lname': 'Sharma', 'student_email': 'nitish.sharma@gmail.com', 'student_username': 'nitish10', 'student_password': 'password10', 'student_hours' : 1},
        {'student_id': 11, 'student_fname': 'Adrienne', 'student_lname': 'Burns', 'student_email': 'adrienne.burns@gmail.com', 'student_username': 'adrienne11', 'student_password': 'password11', 'student_hours' : 1},
        {'student_id': 12, 'student_fname': 'Eliana', 'student_lname': 'Choi', 'student_email': 'eliana.choi@gmail.com', 'student_username': 'eliana12', 'student_password': 'password12', 'student_hours' : 1},
        {'student_id': 13, 'student_fname': 'Ryan', 'student_lname': 'Kim', 'student_email': 'ryan.kim@gmail.com', 'student_username': 'ryan13', 'student_password': 'password13', 'student_hours' : 1},
        {'student_id': 14, 'student_fname': 'Timothy', 'student_lname': 'Chung', 'student_email': 'timothy.chung@gmail.com', 'student_username': 'timothy14', 'student_password': 'password14', 'student_hours' : 1},
        {'student_id': 15, 'student_fname': 'Elisabeth', 'student_lname': 'Caruso', 'student_email': 'elisabeth.caruso@gmail.com', 'student_username': 'elisabeth15', 'student_password': 'password15', 'student_hours' : 1},
        {'student_id': 16, 'student_fname': 'Evony', 'student_lname': 'Salmeron', 'student_email': 'evony.salmeron@gmail.com', 'student_username': 'evony16', 'student_password': 'password16', 'student_hours' : 1},
        {'student_id': 17, 'student_fname': 'Manuel', 'student_lname': 'Custodio', 'student_email': 'manuel.custodio@gmail.com', 'student_username': 'manuel17', 'student_password': 'password17', 'student_hours' : 1},
        {'student_id': 18, 'student_fname': 'Shyazana', 'student_lname': 'Rahaman', 'student_email': 'shyazana.rahaman@gmail.com', 'student_username': 'shyazana18', 'student_password': 'password18', 'student_hours' : 1}
    ]
    
    for each_student in students:
        print(f'{each_student["student_fname"]} inserted into students')
        a_student = Student(
            student_id=each_student["student_id"],
            student_fname=each_student["student_fname"],
            student_lname=each_student["student_lname"],
            student_email=each_student["student_email"],
            student_username=each_student["student_username"],
            student_password=each_student["student_password"],
            student_hours=each_student["student_hours"]
        )
        
        db.session.add(a_student)
    db.session.commit()