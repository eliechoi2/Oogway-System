from flask import Flask, redirect, render_template, url_for, request
app = Flask(__name__, template_folder='template') 

#Authentication Routes
@app.route('/')
def login():
    return render_template('/admin-dashboard.html')

#Admin Routes
@app.route('/admin-dashboard')
def admin_dashboard():
    return render_template('/admin-dashboard.html')

@app.route('/admin-student-list-view')
def admin_student_list_view():
    return render_template('/admin-student-list-view.html')

@app.route('/admin-overall-view')
def admin_overall_view():
    return render_template('/admin-overall-view.html')

#Student Routes
@app.route('/home')
def home():
    return render_template('/student-home.html')

if __name__ == '__main__':
    app.run(debug=True)