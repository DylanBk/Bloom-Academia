from modules import *


app = Flask(__name__)


# --- ERROR HANDLING ---

@app.errorhandler(400) # bad request
def err400(error):
    return render_template('error.html', error_type="Bad Request", error_title="Sorry! We cannot process your request.", error_subtitle="Double check your inputs and try again.")

@app.errorhandler(401) # unauthorised, requires login to view content
def err401(error):
    return render_template('error.html', error_type="Unauthorised Access", error_title="You do not have authorisation to view this content.", error_subtitle="Please log in to access this page.")

@app.errorhandler(403) # forbidden, only certain people can see content
def err403(error):
    return render_template('error.html', error_type="Forbidden", error_title="You do not have access to view this content.", error_subtitle="Please contact us if you believe this to be a mistake.")

@app.errorhandler(404) # resource not found
def err404(error):
    return render_template('error.html', error_type="Resource Not Found", error_title="Sorry! We could not find that page.", error_subtitle="Check the URL or return to the <a href='" + url_for('home') + "'>home page</a>.")

@app.errorhandler(500) # internal server error
def err500(error):
    return render_template('error.html', error_type="Internal Server Error", error_title="Sorry, something went wrong on our end.", error_subtitle="Check back later or report the issue at <a href='" + url_for('home') + "'>email or something</a>.")


# --- ROUTING ---

@app.route('/')
@app.route('/home')
def home():
    return render_template('index.html')



# --- CREATE COURSE ---
@app.route('/createcourse', methods=['GET', 'POST'])
def create_course():
    if request.form == 'POST':
        course_title = request.form['course-title']
        course_description = request.form['course-description']
        course_image = request.form['course-img']

        with db.connect("root/instance/users.db") as c:
            db.upload_course(c, course_title, course_description, course_image)

        return redirect(url_for('success')) # !!! replace with success for course creation !!!
    else:
        return render_template('createcourse.html')

# --- CREATE USER ROUTE ---
@app.route('/createuser', methods=['GET', 'POST'])
def create_user():
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']
        name = request.form['name']

        with db.connect("root/instance/users.db") as c:
            db.create_user(c, name, email, password, role="1")  # create user in database

        return redirect(url_for('success'))  # Redirect to a success page
    else:
        return render_template('createuser.html')  # Show the form on GET


# --- SEARCH USER ROUTE ---
@app.route('/searchuser', methods=['GET', 'POST'])
def search_user():
    if request.method == 'POST':
        email = request.form['email']
        with db.connect("root/instance/users.db") as c:
            user = db.find_user(c, email)

        if user:
            return render_template('user_results.html', user=user)
        else:
            return render_template('user_results.html', message="User not found")
    else:
        return render_template('searchuser.html')


# --- LOGIN ROUTE ---
@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']

        with db.connect("root/instance/users.db") as c:
            user = db.find_user(c, email)

        if user and bcrypt.checkpw(password.encode('utf-8'), user['password']):
            session['user_id'] = user['id']
            return redirect(url_for('home'))
        else:
            return render_template('login.html', message="Invalid email or password")
    else:
        return render_template('login.html')


# --- SUCCESS ROUTE ---
@app.route('/success')
def success():
    return render_template('success.html') 


# --- CREATE DATABASES ---
db.create()


# --- MAIN ---

if __name__ == "__main__":
    app.run()