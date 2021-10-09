from flask import Flask, render_template, request, redirect, url_for, jsonify, session
from authlib.integrations.flask_client import OAuth
import config
import databases
from loginpass import create_flask_blueprint, GitHub, Google, Gitlab, Discord

app = Flask(__name__)
oauth = OAuth(app)
database = databases.Database(config.MONGO_URI)

app.config.from_pyfile('config.py')
backends = [GitHub, Google, Gitlab, Discord]

@app.route('/')
def home():
    if 'user' in session:
        return redirect(url_for('dashboard'))
    return render_template('index.html')

@app.route('/home')
def dashboard():
    if 'user' in session:
        return jsonify(session['user'])
        # if session['user']['type'] == 'teacher':
        #     return render_template('teacherHome.html', user=session['user'])
        # return render_template('studentHome.html', user=session['user'])
    return redirect(url_for('home'))

@app.route('/teacher')
def teacher():
    return render_template('teacher.html')
    
def handle_authorize(remote, token, user_info):
    if database.userExists(user_info['email']):
        user = database.getUser(user_info['email'])
        user['type'] = 'teacher'
        session['user'] = user
    else:
        database.addUser(user_info['email'])
        user = database.getUser(user_info['email'])
        user['type'] = 'teacher'
        session['user'] = user
    # return jsonify(user_info)
    return redirect(url_for('home'))


bp = create_flask_blueprint(backends, oauth, handle_authorize)
app.register_blueprint(bp, url_prefix='/')


if __name__ == '__main__':
    app.run(debug=True)
