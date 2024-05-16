from flask import Flask, redirect, render_template, url_for, request, models, create_app, db
db.create_all(app=create_app())

app = Flask(__name__)

#Authentication Routes
@app.route('/')
def login():
    return render_template('/login.html')

@app.route('/login', methods=['POST'])
def login_post():
    return redirect(url_for('main.profile'))

#Administrator Routs
@app.route('/admin-dashboard')
def dashboard ():
    return render_template('/admin-dashboard.html')

if __name__ == '__main__':
    app.run(debug=True)