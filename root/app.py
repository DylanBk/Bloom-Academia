from modules import * 

app = Flask(__name__)

# Secret key for session management.
app.secret_key = 'supersecretkey' 

# Allowed extensions for file uploads
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif', 'jfif'}

def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS


# --- ERROR HANDLING ---

@app.errorhandler(400) # bad request
def err400(error):
    return render_template('error.html', error_type="Bad Request", error_title="Sorry! We cannot process your request.", error_subtitle="Double check your inputs and try again.")

@app.errorhandler(401) # no authorisation
def err401(error):
    return render_template('error.html', error_type="Unauthorised Access", error_title="You do not have authorisation to view this content.", error_subtitle="Please log in to access this page.")

@app.errorhandler(403) # forbidden resource
def err403(error):
    return render_template('error.html', error_type="Forbidden", error_title="You do not have access to view this content.", error_subtitle="Please contact us if you believe this to be a mistake.")

@app.errorhandler(404) # resource not found
def err404(error):
    return render_template('error.html', error_type="Resource Not Found", error_title="Sorry! We could not find that page.", error_subtitle="Check the URL or return to the <a href='" + url_for('home') + "'>home page</a>.")

@app.errorhandler(500) # internal server error
def err500(error):
    return render_template('error.html', error_type="Internal Server Error", error_title="Sorry, something went wrong on our end.", error_subtitle="Check back later or report the issue at <a href='" + url_for('home') + "'>email or something</a>.")


# --- ROUTES ---

# --- HOME/LANDING ---
@app.route('/')
@app.route('/home')
def home():
    name = session.get('name')
    return render_template('index.html', name=name)


# --- COURSE ROUTES ---

@app.route('/createcourse', methods=['GET', 'POST'])
def create_course():
    if request.method == 'POST':
        if session:
            authorID = session['user_id']
            if 'course-img' not in request.files:
                return redirect(request.url)

            file = request.files['course-img']
            if file and allowed_file(file.filename):
                try:
                    img_data = file.read()  # Read the file contents as bytes
                    title = request.form['course-title']
                    description = request.form['course-description']

                    with db.connect("././instance/users.db") as conn:
                        cursor = conn.cursor()
                        db.upload_course(conn, title, description, img_data, authorID)
                        conn.commit()
                        return redirect(url_for('success', message='Course uploaded successfully!'))
                except db.DatabaseError as db_err:
                    return render_template('error.html', error_type="Database Error", error_title="Database Error", error_subtitle=str(db_err))
                except Exception as e:
                    return render_template('error.html', error_type="Internal Server Error", error_title="Sorry, something went wrong.", error_subtitle=str(e))
    return render_template('/course-pages/createcourse.html', name=name, role=role)

@app.route('/courses')
def list_courses():
    try:
        with db.connect("./instance/users.db") as conn:
            courses = db.get_courses(conn)

            # Convert binary image data to base64
            updated_courses = []
            for course in courses:
                title, description, img_data, cid = course

                if img_data:
                    img_base64 = base64.b64encode(img_data).decode('utf-8')
                else:
                    img_base64 = None
                updated_courses.append((title, description, img_base64, cid))

        message = request.args.get('message', '')
        return render_template('/course-pages/courses.html', courses=updated_courses, message=message)
    except db.DatabaseError as db_err:
        return render_template('error.html', error_type="Database Error", error_title="Database Error", error_subtitle=str(db_err))
    except Exception as e:
        return render_template('error.html', error_type="Internal Server Error", error_title="Sorry, something went wrong.", error_subtitle=str(e))
    
@app.route('/courses/<int:cid>')
def view_course(cid):
    try:
        with db.connect("./instance/users.db") as conn:
            course = db.get_course(conn, cid)
            tasks = db.get_tasks(conn, cid)
            title, description, img_data, cid, uid = course
            if img_data:
                img_base64 = base64.b64encode(img_data).decode('utf-8')
            else:
                img_base64 = None
            if uid == session['user_id'] or db.check_admin(conn, session['user_id']):
                return render_template('/course-pages/course.html', title=title, description=description, img_base64=img_data, cid=cid, tasks=tasks, isAuthor=True)
            else:
                return render_template('/course-pages/course.html', title=title, description=description, img_base64=img_base64, cid=cid, tasks=tasks, isAuthor=False)
    except db.DatabaseError as db_err:
        return render_template('error.html', error_type="Database Error", error_title="Database Error", error_subtitle=str(db_err))
    except Exception as e:
        return render_template('error.html', error_type="Internal Server Error", error_title="Sorry, something went wrong.", error_subtitle=str(e))

@app.route('/add_task/<int:cid>', methods=['POST'])
def add_task(cid):
    if 'user_id' not in session:
        return redirect(url_for('login'))

    task_title = request.form['task_title']
    task_description = request.form['task_description']

    with db.connect("./instance/users.db") as conn:
        db.add_task(conn, cid, task_title, task_description)

    return redirect(url_for('view_course', cid=cid))

@app.route('/remove_task/<int:cid>', methods=['POST'])
def remove_task(cid):
    if 'user_id' not in session:
        return redirect(url_for('login'))

    tid = request.form.get('tid')  # Get tid from the form
    if tid is not None:  # Check if tid is provided
        with db.connect("./instance/users.db") as conn:
            db.remove_task(conn, cid, tid)

    return redirect(url_for('view_course', cid=cid))

@app.route('/searchcourse', methods=['GET', 'POST'])
def search_course():
    if request.method == 'POST':
        query = request.form['search-bar-input']

        with db.connect("./instance/users.db") as conn:
            courses = db.find_course(conn, query)

        if courses:
            updated_courses = []
            for course in courses:
                title, description, img_data, cid = course
                print(title)
                if img_data:
                    img_base64 = base64.b64encode(img_data).decode('utf-8')
                else:
                    img_base64 = None

                updated_course = ((title, description, img_base64, cid))
                updated_courses.append(updated_course)


            return render_template('/course-pages/courseresults.html', courses=updated_courses)
        return render_template('/course-pages/courseresults.html', message="Course not found")
    return render_template('/course-pages/courseresults.html', message="Please enter a search term")

@app.route('/admin/changerole', methods=['GET', 'POST'])
def change_role():
    if request.method == 'POST':
        uid = request.form['uid']
        role = request.form['role']
        with db.connect("./instance/users.db") as conn:
            db.change_role(conn, uid, role)

        return redirect(url_for('success', message="Role changed successfully!"))
    return render_template('/admin-pages/changerole.html')


@app.route('/join_course/<int:cid>', methods=['POST'])
def join_course(cid):
    if 'user_id' not in session:
        return redirect(url_for('login'))

    user_id = session['user_id']

    with db.connect("./instance/users.db") as conn:
        cursor = conn.cursor()
        # Check if the user is already joined
        cursor.execute("SELECT * FROM course_users WHERE cid = ? AND uid = ?", (cid, user_id))
        existing_join = cursor.fetchone()
        if not existing_join:
            cursor.execute("INSERT INTO course_users (cid, uid) VALUES (?, ?)", (cid, user_id))
            conn.commit()
            return redirect(url_for('list_courses', message='Successfully joined the course!'))
        else:
            return redirect(url_for('list_courses', message='Already enrolled in the course!'))

@app.route('/leave_course/<int:cid>', methods=['POST'])
def leave_course(cid):
    if 'user_id' not in session:
        return redirect(url_for('login'))
    user_id = session['user_id']
    
    with db.connect("./instance/users.db") as conn:
        cursor = conn.cursor()
        cursor.execute("DELETE FROM course_users WHERE cid = ? AND uid = ?", (cid, user_id))
        conn.commit()
        return redirect(url_for('list_courses', message='Successfully left the course!'))
        
@app.route('/deletecourse', methods=['GET', 'POST'])
def delete_course():
    if request.method == 'POST':
        cid = request.form['cid']
        with db.connect("./instance/users.db") as conn:
            db.delete_course(conn, cid)

        return redirect(url_for('success', message="Course deleted successfully!"))
    return render_template('/course-pages/deletecourse.html')


# --- USER ROUTES ---

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']
        name = request.form['name']

        code = ""
        for i in range(6):
            num = random.randit(0,9)
            code = code + num
        print(code)

        # check = '' # only create user once verified
        # if check:

        with db.connect("./instance/users.db") as conn:
            db.create_user(conn, name, email, password, role="1")

        return redirect(url_for('success', message="User created successfully!"))
    return render_template('/login-signup-pages/register.html')

@app.route('/profile')
def profile():
    if 'user_id' not in session:
        return redirect(url_for('login'))

    user_id = session['user_id']

    with db.connect("./instance/users.db") as conn:
        user_profile = db.get_user_profile(conn, user_id)
        user_courses = db.get_user_courses(conn, user_id)

    name, email, role_id = user_profile
    role_map = {1: 'User', 2: 'Author', 3: 'Admin'}
    role = role_map.get(role_id, 'unknown')  # Map role ID to role name, default to 'unknown' if not found

    return render_template('profile.html', name=name, email=email, role=role, courses=user_courses)

@app.route('/searchuser', methods=['GET', 'POST'])
def search_user():
    if request.method == 'POST':
        email = request.form['email']
        with db.connect("./instance/users.db") as conn:
            user = db.find_user(conn, email)

        if user:
            return render_template('user_results.html', user=user)
        return render_template('user_results.html', message="User not found")
    return render_template('searchuser.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']

        with db.connect("./instance/users.db") as conn:
            user = db.find_user(conn, email)

        if user and bcrypt.checkpw(password.encode('utf-8'), user[3]):  # 'password' is at index 3
            session['user_id'] = user[0]  # 'id' is at index 0 in the tuple
            session['role'] = user[4]  # 'role' is at index 4 in the tuple
            session['name'] = user[1]  # 'name' is at index 1 in the tuple
            return redirect(url_for('home'))
        return render_template('/login-signup-pages/login.html', message="Invalid email or password")
    return render_template('/login-signup-pages/login.html')

@app.route('/logout')
def logout():
    session.pop('user_id', None)
    session.pop('role', None)
    session.pop('name', None)
    return redirect(url_for('home'))

@app.route('/success')
def success():
    message = request.args.get('message', 'Success!')  # Get message, default to "Success!"
    return render_template('/login-signup-pages/success.html', message=message)


# --- MAIN PROGRAM ---

db.create()

if __name__ == "__main__":
    app.run()
