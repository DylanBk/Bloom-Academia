from modules import * 

app = Flask(__name__)

# Secret key for session management.
app.secret_key = 'supersecretkey' 

# Allowed extensions for image uploads
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif', 'jfif'}

def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

# Error Handlers
@app.errorhandler(400)
def err400(error):
    return render_template('error.html', error_type="Bad Request", error_title="Sorry! We cannot process your request.", error_subtitle="Double check your inputs and try again.")

@app.errorhandler(401)
def err401(error):
    return render_template('error.html', error_type="Unauthorised Access", error_title="You do not have authorisation to view this content.", error_subtitle="Please log in to access this page.")

@app.errorhandler(403)
def err403(error):
    return render_template('error.html', error_type="Forbidden", error_title="You do not have access to view this content.", error_subtitle="Please contact us if you believe this to be a mistake.")

@app.errorhandler(404)
def err404(error):
    return render_template('error.html', error_type="Resource Not Found", error_title="Sorry! We could not find that page.", error_subtitle="Check the URL or return to the <a href='" + url_for('home') + "'>home page</a>.")

@app.errorhandler(500)
def err500(error):
    return render_template('error.html', error_type="Internal Server Error", error_title="Sorry, something went wrong on our end.", error_subtitle="Check back later or report the issue at <a href='" + url_for('home') + "'>email or something</a>.")

# Routes
@app.route('/')
@app.route('/home')
def home():
    name = session.get('name')
    return render_template('index.html', name=name)

@app.route('/createcourse', methods=['GET', 'POST'])
def create_course():
    if request.method == 'POST':
        if 'course-img' not in request.files:
            return redirect(request.url)

        file = request.files['course-img']
        if file and allowed_file(file.filename):
            try:
                img_data = file.read()  # Read the file contents as bytes
                title = request.form['course-title']
                description = request.form['course-description']

                with db.connect("root/instance/users.db") as conn:
                    cursor = conn.cursor()
                    db.upload_course(conn, title, description, img_data)
                    conn.commit()
                    return redirect(url_for('success', message='Course uploaded successfully!'))
            except db.DatabaseError as db_err:
                return render_template('error.html', error_type="Database Error", error_title="Database Error", error_subtitle=str(db_err))
            except Exception as e:
                return render_template('error.html', error_type="Internal Server Error", error_title="Sorry, something went wrong.", error_subtitle=str(e))
    return render_template('createcourse.html')

@app.route('/courses')
def list_courses():
    try:
        with db.connect("root/instance/users.db") as conn:
            courses = db.get_courses(conn)

            # Convert binary image data to base64
            updated_courses = []
            for course in courses:
                title, description, img_data, course_id = course
                if img_data:
                    img_base64 = base64.b64encode(img_data).decode('utf-8')
                else:
                    img_base64 = None
                updated_courses.append((title, description, img_base64, course_id))

        message = request.args.get('message', '')
        return render_template('courses.html', courses=updated_courses, message=message)
    except db.DatabaseError as db_err:
        return render_template('error.html', error_type="Database Error", error_title="Database Error", error_subtitle=str(db_err))
    except Exception as e:
        return render_template('error.html', error_type="Internal Server Error", error_title="Sorry, something went wrong.", error_subtitle=str(e))
    
@app.route('/courses/<int:course_id>')
def view_course(course_id):
    try:
        with db.connect("root/instance/users.db") as conn:
            course = db.get_course(conn, course_id)
            tasks = db.get_tasks(conn, course_id)
            title, description, img_data, course_id = course
            if img_data:
                img_base64 = base64.b64encode(img_data).decode('utf-8')
            else:
                img_base64 = None
            return render_template('course.html', title=title, description=description, img_base64=img_base64, course_id=course_id, tasks=tasks)
    except db.DatabaseError as db_err:
        return render_template('error.html', error_type="Database Error", error_title="Database Error", error_subtitle=str(db_err))
    except Exception as e:
        return render_template('error.html', error_type="Internal Server Error", error_title="Sorry, something went wrong.", error_subtitle=str(e))

@app.route('/add_task/<int:course_id>', methods=['POST'])
def add_task(course_id):
    if 'user_id' not in session:
        return redirect(url_for('login'))

    task_description = request.form['task_description']

    with db.connect("root/instance/users.db") as conn:
        db.add_task(conn, course_id, task_description)

    return redirect(url_for('view_course', course_id=course_id))

@app.route('/join_course/<int:course_id>', methods=['POST'])
def join_course(course_id):
    if 'user_id' not in session:
        return redirect(url_for('login'))

    user_id = session['user_id']

    with db.connect("root/instance/users.db") as conn:
        cursor = conn.cursor()
        # Check if the user is already joined
        cursor.execute("SELECT * FROM course_users WHERE cid = ? AND uid = ?", (course_id, user_id))
        existing_join = cursor.fetchone()
        if not existing_join:
            cursor.execute("INSERT INTO course_users (cid, uid) VALUES (?, ?)", (course_id, user_id))
            conn.commit()
            return redirect(url_for('list_courses', message='Successfully joined the course!'))
        else:
            return redirect(url_for('list_courses', message='Already enrolled in the course!'))

@app.route('/leave_course/<int:course_id>', methods=['POST'])
def leave_course(course_id):
    if 'user_id' not in session:
        return redirect(url_for('login'))
    user_id = session['user_id']
    
    with db.connect("root/instance/users.db") as conn:
        cursor = conn.cursor()
        cursor.execute("DELETE FROM course_users WHERE cid = ? AND uid = ?", (course_id, user_id))
        conn.commit()
        return redirect(url_for('list_courses', message='Successfully left the course!'))
        
@app.route('/deletecourse', methods=['GET', 'POST'])
def delete_course():
    if request.method == 'POST':
        course_id = request.form['course_id']
        with db.connect("root/instance/users.db") as conn:
            db.delete_course(conn, course_id)

        return redirect(url_for('success', message="Course deleted successfully!"))
    return render_template('deletecourse.html')

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']
        name = request.form['name']

        with db.connect("root/instance/users.db") as conn:
            db.create_user(conn, name, email, password, role="1")

        return redirect(url_for('success', message="User created successfully!"))
    return render_template('register.html')

@app.route('/profile')
def profile():
    if 'user_id' not in session:
        return redirect(url_for('login'))

    user_id = session['user_id']

    with db.connect("root/instance/users.db") as conn:
        user_profile = db.get_user_profile(conn, user_id)
        user_courses = db.get_user_courses(conn, user_id)

    name, email, role_id = user_profile
    role_map = {1: 'user', 2: 'creator', 3: 'admin'}
    role = role_map.get(role_id, 'unknown')  # Map role ID to role name, default to 'unknown' if not found

    return render_template('profile.html', name=name, email=email, role=role, courses=user_courses)

@app.route('/searchuser', methods=['GET', 'POST'])
def search_user():
    if request.method == 'POST':
        email = request.form['email']
        with db.connect("root/instance/users.db") as conn:
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

        with db.connect("root/instance/users.db") as conn:
            user = db.find_user(conn, email)

        if user and bcrypt.checkpw(password.encode('utf-8'), user[3]):  # 'password' is at index 3
            session['user_id'] = user[0]  # 'id' is at index 0 in the tuple
            session['role'] = user[4]  # 'role' is at index 4 in the tuple
            session['name'] = user[1]  # 'name' is at index 1 in the tuple
            return redirect(url_for('home'))
        return render_template('login.html', message="Invalid email or password")
    return render_template('login.html')

@app.route('/logout')
def logout():
    session.pop('user_id', None)
    session.pop('role', None)
    session.pop('name', None)
    return redirect(url_for('home'))

@app.route('/success')
def success():
    message = request.args.get('message', 'Success!')  # Get message, default to "Success!"
    return render_template('success.html', message=message)

db.create()

if __name__ == "__main__":  
    app.run()