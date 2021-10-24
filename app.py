from flask import Flask, render_template, request, redirect, url_for, jsonify, session
from authlib.integrations.flask_client import OAuth
import config
import databases
from loginpass import create_flask_blueprint, GitHub, Google, Gitlab, Discord
import pyrebase
from uuid import uuid4

app = Flask(__name__)

app.config.from_pyfile('config.py')
backends = [GitHub, Google, Gitlab, Discord]
firebaseConfig = config.FIREBASE_CONFIG

oauth = OAuth(app)
firebase = pyrebase.initialize_app(firebaseConfig)
fireDB = firebase.database()
fireStrg = firebase.storage()
database = databases.Database(config.MONGO_URI, fireStrg, fireDB)


@app.route('/')
def home():
    if 'user' in session:
        return redirect(url_for('dashboard'))
    return render_template('index.html')

@app.route('/home')
def dashboard():
    if 'user' in session:
        return render_template('home.html', user=session['user'])
    return redirect(url_for('home'))

@app.route('/login')
def login():
    return render_template('login.html')

@app.route('/logout')
def logout():
    session.pop('user')
    return redirect(url_for('home'))

@app.route('/changeName', methods=['POST'])
def changeName():
    if 'user' in session:
        name = request.form.get('name')
        if name == '':
            return 'please enter a valid username'
        elif len(name) > 20:
            return 'username too long'
        user = session['user']
        user['username'] = name
        session['user'] = user
        database.updateName(user['email'], name)
        return "Updated!"
    return abort(404)

@app.route('/classes')
def classes():
    if 'user' in session:
        classes = database.getUserClasses(session['user']['email'])
        classes = [database.getClass(c) for c in classes]
        return render_template('classes.html', classes=classes, user=session['user'])

@app.route('/classes/new', methods=['GET', 'POST'])
def newclass():
    if 'user' in session:
        if request.method == 'POST':
            name = request.form.get('name')
            description = request.form.get('description')
            database.createClass(session['user']['_id'], name, description)
            return redirect(url_for('classes'))
        classes = database.getUserClasses(session['user']['email'])
        classes = [database.getClass(c) for c in classes]
        return render_template('addclass.html', classes=classes, user=session['user'])

@app.route('/class/<class_id>')
def classPage(class_id):
        if 'user' in session:
            if database.classExists(class_id):
                class_ = database.getClass(class_id)
                if session['user']['_id'] in class_['members']:
                    return redirect(url_for('assignments', class_id=class_id))
                else:
                    return redirect(url_for('home'))
            else:
                return "class doesn't exist"
        return redirect(url_for('home'))
    
@app.route('/class/<class_id>/assignments')
def assignments(class_id):
    if 'user' in session:
        if database.classExists(class_id):
            class_ = database.getClass(class_id)
            assignments = database.getAssignments(class_id)
            answerers = {}
            for a in assignments:
                answerers[a['_id']] = [list(l.keys())[0] for l in [j for j in a['answers']]]
            return render_template('assignments.html', class_=class_, 
                                   assignments=assignments, answerers=answerers,
                                   user=session['user'])
        else:
            return "class doesn't exist"
    else:
        return redirect(url_for('home'))
    
@app.route('/class/<class_id>/assignments/new', methods=['GET', 'POST'])
def newAssignments(class_id):
    if 'user' in session:
        if request.method == 'GET':
            if database.classExists(class_id):
                class_ = database.getClass(class_id)
                if session['user']['_id'] == class_['by']:
                    assignments = database.getAssignments(class_id)
                    return render_template('newAssignment.html', class_=class_, assignments=assignments, user=session['user'])
                else:
                    return redirect(url_for('home'))
            else:
                return "class doesn't exist"
        else:
            data = request.form.to_dict()
            database.addAssignment(class_id, data['name'], data['description'], data['type'])            
            return redirect(url_for('assignments', class_id=class_id))
    else:
        return redirect(url_for('home'))
    
@app.route('/class/<class_id>/assignments/answer/<assignment_id>', methods=['GET', 'POST'])
def assignmentAnswers(class_id, assignment_id):
    if 'user' in session:
        if request.method == 'GET':
            if database.classExists(class_id):
                class_ = database.getClass(class_id)
                if session['user']['_id'] == class_['by']:
                    assignment = database.getAssignment(assignmentID=assignment_id)
                    for answer in assignment['answers']:
                        answer['by'] = database.getUserWithID(list(answer.keys())[0])
                        answer['answer'] = list(answer.values())[0]
                    return render_template('answers.html', class_=class_, assignment=assignment, user=session['user'])
                else:
                    return redirect(url_for('home'))
            else:
                return "class doesn't exist"
        else:
            data = request.form.to_dict()
            database.addAssignment(class_id, data['name'], data['description'], data['type'])            
            return redirect(url_for('assignments', class_id=class_id))
    else:
        return redirect(url_for('home'))

@app.route('/answer/<assignment_id>', methods=['POST'])
def answer(assignment_id):
    if 'user' in session:
        assignment = database.getAssignment(assignment_id)
        if assignment is None:
            return "assignment doesn't exist"
        class_ = database.getClass(assignment['class'])
        print([list(l.keys())[0] for l in [j for j in assignment['answers']]])
        if session['user']['_id'] in class_['members'] and session['user']['_id'] not in [list(l.keys())[0] for l in [j for j in assignment['answers']]]:
            if assignment['type'] == 'Text':
                data = request.form.to_dict()
                database.addAnswer(assignment_id, session['user']['_id'], data['answer'])
                return redirect(url_for('assignments', class_id=class_['_id']))
            else:
                file = request.files['answer']
                ext = file.filename.split('.')[-1]
                fireStrg.child('answers/' + assignment_id + '/' + session['user']['email'] + f".{ext}").put(file)
                url = fireStrg.child('answers/' + assignment_id + '/' + session['user']['email'] + f".{ext}").get_url(None)
                database.addAnswer(assignment_id, session['user']['_id'], url)
                return redirect(url_for('assignments', class_id=class_['_id']))
        else:
            return redirect(url_for('assignments', class_id=class_['_id']))

@app.route('/class/<class_id>/resources')
def resources(class_id):
    if 'user' in session:
        if database.classExists(class_id):
            class_ = database.getClass(class_id)
            resources = database.getResources(class_id)
            print(resources)
            return render_template('resources.html', resources=resources, user=session['user'], class_=class_)

@app.route('/class/<class_id>/resources/new', methods=['GET', 'POST'])
def newResources(class_id):
    if 'user' in session:
        if request.method == 'GET':
            if database.classExists(class_id):
                class_ = database.getClass(class_id)
                if session['user']['_id'] == class_['by']:
                    return render_template('newResource.html', class_=class_, user=session['user'])
                else:
                    return redirect(url_for('home'))
            else:
                return "class doesn't exist"
        else:
            data = request.form.to_dict()
            ID = str(uuid4())
            file = request.files['resource']
            if file.filename == '':
                database.addResource(ID ,class_id, data['name'], data['description'])
                print(data['description'])
                return redirect(url_for('resources', class_id=class_id))
            ext = file.filename.split('.')[-1]
            fireStrg.child('resources/' + ID + f".{ext}").put(file)
            url = fireStrg.child('resources/' + ID + f".{ext}").get_url(None)
            database.addResource(ID ,class_id, data['name'], data['description'], url)
            return redirect(url_for('resources', class_id=class_id))
        
@app.route('/class/<class_id>/resources/resource/<resource_id>')
def resource(class_id, resource_id):
    if 'user' in session:
        if database.classExists(class_id):
            class_ = database.getClass(class_id)
            resource = database.getResource(resource_id)
            return render_template('resource.html', resource=resource, user=session['user'], class_=class_)

@app.route('/join', methods=['GET', 'POST'])
def joinClass():
    if 'user' in session:        
        if request.method == 'POST':
            class_code = request.form.get('code')
            joined = database.joinClass(session['user']['_id'], class_code)
            if joined:
                return redirect(url_for('classes'))
            else: 
                return "class doesn't exist"
        else:
            return render_template('joinClass.html')
    else:
        return redirect(url_for('login'))

def handle_authorize(remote, token, user_info):
    if database.userExists(user_info['email']):
        session['user'] = database.getUser(user_info['email'])
    else:
        database.addUser(user_info['email'])
        session['user'] = database.getUser(user_info['email'])
    return redirect(url_for('home'))


bp = create_flask_blueprint(backends, oauth, handle_authorize)
app.register_blueprint(bp, url_prefix='/')


if __name__ == '__main__':
    app.run(debug=True)
