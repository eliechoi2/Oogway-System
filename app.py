from flask import Flask, redirect, render_template, url_for, request
app = Flask(__name__, template_folder='template') 

#Authentication Routes
@app.route('/')
def login():
    return render_template('/admin-dashboard.html')

#Student Routes
@app.route('/home')
def home():
    return render_template('/student-home.html')

if __name__ == '__main__':
    app.run(debug=True)