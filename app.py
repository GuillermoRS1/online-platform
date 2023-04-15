from flask import Flask, render_template, request, url_for, redirect
from pymongo import MongoClient
from bson.objectid import ObjectId
from flask_login import LoginManager, UserMixin, login_user, login_required, logout_user

# Create a Flask web application instance
app = Flask(__name__)
app.secret_key = 'superKey341'

# Set up Flask-Login
login_manager = LoginManager()
login_manager.init_app(app)

# Connect to MongoDB server running localhost service
client = MongoClient('localhost', 27017)

# Access the 'flask_db' database in MongoDB
db = client.flask_db
# Access the 'users' collection in the 'flask_db' database
users = db.users
# Access the 'todos' collection in the 'flask_db' database
todos = db.todos

# Define a route for '/hello' URL that returns a string saying Hello, World
@app.route('/hello')
def hello():
    return 'Hello, World!'

# User model for Flask-Login
class User(UserMixin):
    def __init__(self, user):
        self.id = user['_id']
        self.username = user['username']
        self.password = user['password']

    def get_id(self):
        return str(self.id)

# Load user from user_id
@login_manager.user_loader
def load_user(user_id):
    # Check if the user exist in the database
    user = users.find_one({'_id': ObjectId(user_id)})
    if user:
        # Return the information of the user selected
        return User(user)
    return None

# Define a route for the index page
@app.route('/')
def index():
    return render_template('index.html')

# Define a route for the login page
@app.route('/login', methods=('GET', 'POST'))
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        # Check if the user exist or not in the database
        user = users.find_one({'username': username})
        # Check if the password of the user is correct
        if user and user['password'] == password:
            user_obj = User(user)
            login_user(user_obj)
            return redirect(url_for('dashboard'))
        else:
            return render_template('login.html', error='Invalid username or password')
    return render_template('login.html')

# Define a route for the registration page
@app.route('/register', methods=('GET', 'POST'))
def register():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        # Check if the user already exist in the database
        user = users.find_one({'username': username})
        if user:
            return render_template('register.html', error='Username already taken')
        else:
            # Insert the user to the database saving the id assigned
            user_id = users.insert_one({'username': username, 'password': password}).inserted_id
            # Search the user using the id
            user = User(users.find_one({'_id': user_id}))
            login_user(user)
            return redirect(url_for('dashboard'))
    return render_template('register.html')

# Define a route for the dashboard page
@app.route('/dashboard', methods=('GET', 'POST'))
@login_required
def dashboard():
    # Check if the request method is POST
    if request.method=='POST':
        # Retrieve the 'content' value from the submitted form
        content = request.form['content']
        # Retrieve the 'degree' value from the submitted form
        degree = request.form['degree']
        # Retrieve the 'mark' value from the submitted form
        mark = request.form['mark']
        # Insert a new document into the 'todos' collection with 'content' and 'degree' fields
        todos.insert_one({'content': content, 'degree': degree, 'mark': mark})
        # Redirect to the index route after adding a new todo item
        return redirect(url_for('dashboard'))

    # Retrieve all documents from the 'todos' collection
    all_todos = todos.find()
    # Render the 'index.html' template with the retrieved todo items
    return render_template('dashboard.html', todos=all_todos)

@app.post('/<id>/delete/')
def delete(id):
    # Delete a todo item from the 'todos' collection based on the given id
    todos.delete_one({"_id": ObjectId(id)})
    # Redirect to the index route after deleting a todo item
    return redirect(url_for('dashboard'))

@app.route('/<id>/complete/', methods=['POST'])
def complete(id):
    # Update the 'completed' field of a todo item in the 'todos' collection based on the given id
    todos.update_one({"_id": ObjectId(id)}, {"$set": {"degree": "Complete"}})
    # Redirect to the index route after marking a todo item as completed
    return redirect(url_for('dashboard'))

@app.route('/<id>/uncomplete/', methods=['POST'])
def uncomplete(id):
    # Update the 'completed' field of a todo item in the 'todos' collection based on the given id
    todos.update_one({"_id": ObjectId(id)}, {"$set": {"degree": "Uncomplete"}})
    # Redirect to the index route after marking a todo item as completed
    return redirect(url_for('dashboard'))

# Define a route for logging out
@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('login'))

if __name__ == '__main__':
    # Start the Flask app in debug mode if this script is executed directly
    app.run(debug=True)