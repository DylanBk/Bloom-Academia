from modules import * 

app = Flask(__name__)

# Secret key for session management.
app.secret_key = 'supersecretkey' 

db_path = "././instance/users.db"

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
    return render_template('error.html', error_type="Resource Not Found", error_title="Sorry! We could not find that page.", error_subtitle="Check the URL or return to the &nbsp;<a href='" + url_for('home') + "'>home page</a>.")

@app.errorhandler(500) # internal server error
def err500(error): # !!! REPLACE MY EMAIL WITH SITE EMAIL ONCE SET UP !!!
    return render_template('error.html', error_type="Internal Server Error", error_title="Sorry, something went wrong on our end.", error_subtitle="Check back later or report the issue &nbsp; <a href='mailto: dylan.bullock.965@accesscreative.ac.uk'>here</a> &nbsp; by email.")


# --- ROUTES ---

# --- HOME/LANDING ---
@app.route('/')
@app.route('/home')
def home():
    name = session.get('name')
    return render_template('index.html', name=name)

@app.route('/aboutus')
@app.route('/about')
def about():
    return render_template('about-us.html')


# --- COURSE ROUTES ---

@app.route('/createcourse', methods=['GET', 'POST'])
def create_course():
    if not session or session.get('role') not in ['Author', 'Admin']: # Authentication & Authorization
        return render_template('error.html', error_type="No Access", error_title="Unauthorized", error_subtitle="You do not have permission to create courses. To get access, please <a href='" + url_for('apply_author') + "'>click here</a>.", name=session.get('name'))
    
    if request.method == 'POST':  # Corrected method check
        if 'course-img' not in request.files:
            return redirect(request.url)

        file = request.files['course-img']
        if file and allowed_file(file.filename):
            try:
                img_data = file.read()
                title = request.form['course-title']
                description = request.form['course-description']
                authorID = session['user_id']

                with db.connect(db_path) as conn:
                    cursor = conn.cursor()
                    db.upload_course(conn, title, description, img_data, authorID)
                    conn.commit()
                    return redirect(url_for('success', message='Course uploaded successfully!', name=session.get('name')))

            except db.DatabaseError as db_err:
                return render_template('error.html', error_type="Database Error", error_title="Database Error", error_subtitle=str(db_err))

            except Exception as e:
                return render_template('error.html', error_type="Internal Server Error", error_title="Sorry, something went wrong.", error_subtitle=str(e))

    return render_template('/course-pages/createcourse.html', name=session.get('name'))

@app.route('/courses')
def list_courses():
    try:
        with db.connect(db_path) as conn:
            courses = db.get_courses(conn)
            name = session.get('name')

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
        return render_template('/course-pages/courses.html', courses=updated_courses, message=message, name=name)
    except db.DatabaseError as db_err:
        return render_template('error.html', error_type="Database Error", error_title="Database Error", error_subtitle=str(db_err), name=name)
    except Exception as e:
        return render_template('error.html', error_type="Internal Server Error", error_title="Sorry, something went wrong.", error_subtitle=str(e), name=name)
    
@app.route('/courses/<int:cid>')
def view_course(cid):
    if not session:
        return redirect(url_for('login'))
    
    try:
        with db.connect(db_path) as conn:
            user_id = session['user_id']
            name = session.get('name')
            course = db.get_course(conn, cid)
            tasks = db.get_tasks(conn, cid)
            title, description, img_data, cid, author_id = course
            course_creator = db.get_user_name(conn, author_id)  # New function to get user name

            if img_data:
                img_base64 = base64.b64encode(img_data).decode('utf-8')
            else:
                img_base64 = None

            isAuthor = session.get('role') in ["Author", "Admin"]
            completed_tasks = db.get_completed_tasks(conn, user_id, cid)

            return render_template('/course-pages/course.html',
                                   title=title,
                                   description=description,
                                   img_base64=img_base64, 
                                   cid=cid, 
                                   tasks=tasks, 
                                   isAuthor=isAuthor, 
                                   name=name,
                                   course_creator=course_creator,
                                   completed_tasks=completed_tasks)
                                   
    except db.DatabaseError as db_err:
        return render_template('error.html', error_type="Database Error", error_title="Database Error", error_subtitle=str(db_err), name=name)
    except Exception as e:
        return render_template('error.html', error_type="Internal Server Error", error_title="Sorry, something went wrong.", error_subtitle=str(e), name=name)

@app.route('/add_task/<int:cid>', methods=['POST'])
def add_task(cid):
    if not session or session.get('role') not in ['Author', 'Admin']:
        return redirect(url_for('login'))

    task_title = request.form['task_title']
    task_description = request.form['task_description']
    task_content = request.form['task_content']

    with db.connect(db_path) as conn:
        db.add_task(conn, cid, task_title, task_description, task_content)

    return redirect(url_for('view_course', cid=cid))

@app.route('/remove_task/<int:cid>', methods=['POST'])
def remove_task(cid):
    if not session:
        return redirect(url_for('login'))

    tid = request.form.get('tid')  # Get tid from the form
    if tid is not None:  # Check if tid is provided
        with db.connect(db_path) as conn:
            db.remove_task(conn, cid, tid)

    return redirect(url_for('view_course', cid=cid))

@app.route('/searchcourse', methods=['GET', 'POST'])
def search_course():
    if request.method == 'POST':
        query = request.form['search-bar-input']

        with db.connect(db_path) as conn:
            courses = db.find_course(conn, query)
            name = session.get('name')

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


            return render_template('/course-pages/courseresults.html', courses=updated_courses, name=name)
        return render_template('/course-pages/courseresults.html', message="Course not found", name=name)
    return render_template('/course-pages/courseresults.html', message="Please enter a search term", name=name)

@app.route('/admin/changerole/<int:uid>', methods=['GET', 'POST'])
def change_role(uid):
    if not session or session.get('role') != 'Admin': # Authentication & Authorization
        return render_template('error.html', error_type="No Access", error_title="Unauthorized", error_subtitle="You do not have permission to view this page.", name=session.get('name'))
    if request.method == 'POST':
        role = request.form['role']
        uid = request.form['uid']

        with db.connect(db_path) as conn:
            db.change_role(conn, uid, role)

        return redirect(url_for('success', message="Role changed successfully!", name=session.get('name')))
    return render_template('/admin-pages/changerole.html', uid=uid, name=session.get('name'))

@app.route('/applyforauthor', methods=['GET', 'POST'])
def apply_author():
    if not session:
        return redirect(url_for('login'))

    if session.get('role') != 'User':
        return render_template('error.html', error_type="Bad Request", error_title="You cannot apply for a role you already have.", error_subtitle="It looks like you already have the author role, if you think this is a mistake please contact us.", name=session.get('name'))

    if request.method == 'POST':
        print("data retrieved")
        user_id = session['user_id']
        print(user_id)
        email = request.form['user-email']
        print(email)
        reason = request.form['user-reason']
        print(reason)
        area = request.form['user-specialty']
        print(user_id, email, reason, area)

        with db.connect(db_path) as conn:
            print("connected to db")
            db.request_author(conn, user_id, email, reason, area)
            print("passed into db func")

        return redirect(url_for('success', message="Your request has been submitted successfully", name=session.get('name')))
    print("GET request")
    return render_template('applyforauthor.html', name=session.get('name'))

@app.route('/join_course/<int:cid>', methods=['POST'])
def join_course(cid):
    if not session:
        return redirect(url_for('login'))

    user_id = session['user_id']

    with db.connect(db_path) as conn:
        cursor = conn.cursor()
        # Check if the user is already joined
        cursor.execute("SELECT * FROM course_users WHERE cid = ? AND uid = ?", (cid, user_id))
        existing_join = cursor.fetchone()
        if not existing_join:
            cursor.execute("INSERT INTO course_users (cid, uid) VALUES (?, ?)", (cid, user_id))
            conn.commit()
            return redirect(url_for('list_courses', message='Successfully joined the course!', name=session.get('name')))
        else:
            return redirect(url_for('list_courses', message='Already enrolled in the course!', name=session.get('name')))

@app.route('/leave_course/<int:cid>', methods=['POST'])
def leave_course(cid):
    if not session:
        return redirect(url_for('login'))
    user_id = session['user_id']
    
    with db.connect(db_path) as conn:
        cursor = conn.cursor()
        cursor.execute("DELETE FROM course_users WHERE cid = ? AND uid = ?", (cid, user_id))
        conn.commit()
        return redirect(url_for('list_courses', message='Successfully left the course!', name=session.get('name')))
        
@app.route('/deletecourse/<int:cid>', methods=['GET', 'POST'])
def delete_course(cid):
    if not session or session.get('role') not in ['Author', 'Admin']:  # Authentication & Authorization
        return render_template('error.html', error_type="No Access", error_title="Unauthorized", error_subtitle="You do not have permission to delete courses.", name=session.get('name'))
    if request.method == 'POST':
        with db.connect(db_path) as conn:
            db.delete_course(conn, cid)
        return redirect(url_for('success', message="Course deleted successfully!", name=session.get('name')))
    return render_template('/course-pages/deletecourse.html', name=session.get('name'))


# --- USER ROUTES ---

@app.route('/register', methods=['GET', 'POST'])
def register():
    if session:
        return render_template('error.html', error_type="Already Logged In", error_title="You are already logged in!", error_subtitle="Please log out and try again.", name=session.get('name'))
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']
        name = request.form['name']

        with db.connect(db_path) as conn:
            db.create_user(conn, name, email, password, role="User")

        return redirect(url_for('success', message="User created successfully!"))
    return render_template('/login-signup-pages/register.html')

def get_profile_data():
    if not session:
        return(url_for('login'))

    user_id = session['user_id']

    with db.connect(db_path) as conn:
        user_profile = db.get_user_profile(conn, user_id)
        courses = db.get_user_courses(conn, user_id)

    name, email, role = user_profile
    # Convert binary image data to base64
    updated_courses = []
    for course in courses:
        title, description, img_data, cid = course

        if img_data:
            img_base64 = base64.b64encode(img_data).decode('utf-8')
        else:
            img_base64 = None
        updated_courses.append((title, description, img_base64, cid))

    return name, email, role, updated_courses

@app.route('/settings')
@app.route('/profile')
def profile():
    if not session:
        return redirect(url_for('login'))

    user_id = session['user_id']
    
    with db.connect(db_path) as conn:
        name, email, role = db.get_user_profile(conn, user_id)
        courses = db.get_user_courses(conn, user_id)

        # Process courses and calculate completion rates
        updated_courses = []
        for course in courses:
            title, description, img_data, cid = course
            if img_data:
                img_base64 = base64.b64encode(img_data).decode('utf-8')
            else:
                img_base64 = None
            
            # Calculate completion rate for this course
            completion_rate = db.calculate_completion_rate(conn, user_id, cid)
            
            updated_courses.append((title, description, img_base64, cid, completion_rate))

    return render_template('profile.html', name=name, email=email, role=role, courses=updated_courses)



@app.route('/profile/changeusername', methods=['GET', 'POST'])
@app.route('/settings/changeusername', methods=['GET', 'POST'])
def change_username():
    if not session:
        return redirect(url_for('login'))

    if request.method == 'POST':
        user_id = session['user_id']
        new_username = request.form['new-username']

        with db.connect(db_path) as conn:
            db.change_username(conn, user_id, new_username)

        return redirect(url_for('success', message="Username changed successfully!", name=session.get('name')))

    name, email, role, courses = get_profile_data()

    return render_template('profile.html', name=name, email=email, role=role, courses=courses)

@app.route('/profile/changeemail', methods=['GET', 'POST'])
@app.route('/settings/changeemail', methods=['GET', 'POST'])
def change_email():
    if not session:
        return redirect(url_for('login'))

    if request.method == 'POST':
        user_id = session['user_id']
        new_email = request.form['new-email']

        with db.connect(db_path) as conn:
            db.change_email(conn, user_id, new_email)

        return redirect(url_for('success', message="Email changed successfully!", name=session.get('name')))

    name, email, role, courses = get_profile_data()

    return render_template('settings.html', name=name, email=email, role=role, courses=courses)

@app.route('/profile/changepassword', methods=['GET', 'POST'])
@app.route('/settings/changepassword', methods=['GET', 'POST'])
def change_password():
    if not session:
        return redirect(url_for('login'))

    if request.method == 'POST':
        user_id = session['user_id']
        new_password = request.form['new-password']

        with db.connect(db_path) as conn:
            db.change_password(conn, user_id, new_password)

        return redirect(url_for('success', message="Password changed successfully!", name=session.get('name')))

    name, email, role, courses = get_profile_data()

    return render_template('profile.html', name=name, email=email, role=role, courses=courses)

@app.route('/profile/deleteacccount', methods=['GET', 'POST'])
@app.route('/settings/deleteaccount', methods=['GET', 'POST'])
def delete_account():
    if not session:
        return redirect(url_for('login'))

    name, email, role, courses = get_profile_data()

    if request.method == 'POST':
        user_id = session['user_id']
        form_email = request.form['delete-account-email']
        form_password = request.form['delete-account-password']
        email = session.get('email')

        with db.connect(db_path) as conn:
            user = db.find_user_by_email(conn, email)

        if form_email == email and bcrypt.checkpw(form_password.encode('utf-8'), user[3]):
            with db.connect(db_path) as conn:
                db.delete_account(conn, user_id)
                session.pop('user_id', None)
                session.pop('role', None)
                session.pop('name', None)
                session.pop('email', None)
            print("account deleted")
            
            return redirect(url_for('success', message="Account deleted successfully!"))
        return render_template('profile.html', name=name, email=email, role=role, courses=courses, delete_account_error="Incorrect email or password")
    return render_template('profile.html', name=name, email=email, role=role, courses=courses)
        

@app.route('/searchuser', methods=['GET', 'POST'])
def search_user():
    if not session:
        return redirect(url_for('login'))

    if request.method == 'POST':
        username = request.form['user-search-input']

        with db.connect(db_path) as conn:
            users = db.find_user_by_name(conn, username)

        if users:
            return render_template('user_results.html', users=users, name=session.get('name'))
        return render_template('user_results.html', message="User not found", name=session.get('name'))
    return redirect(url_for('admin'))

@app.route('/login', methods=['GET', 'POST'])
def login():
    if session:
        return render_template('error.html', error_type="Already Logged In", error_title="You are already logged in!", error_subtitle="Please log out and try again.", name=session.get('name'))
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']

        with db.connect(db_path) as conn:
            user = db.find_user_by_email(conn, email)

        if user and bcrypt.checkpw(password.encode('utf-8'), user[3]):  # 'password' is at index 3
            session['user_id'] = user[0]  # 'id' is at index 0 in the tuple
            session['role'] = user[4]  # 'role' is at index 4 in the tuple
            session['name'] = user[1]  # 'name' is at index 1 in the tuple
            session['email'] = user[2]  # 'email' is at index 2 in the tuple
            return redirect(url_for('home'))
        return render_template('/login-signup-pages/login.html', message="Invalid email or password")
    return render_template('/login-signup-pages/login.html')

@app.route('/logout')
def logout():
    session.pop('user_id', None)
    session.pop('role', None)
    session.pop('name', None)
    session.pop('email', None)
    return redirect(url_for('home'))

@app.route('/success')
def success():
    message = request.args.get('message', 'Success!')  # Get message, default to "Success!"
    return render_template('/login-signup-pages/success.html', message=message, name=session.get('name'))

@app.route('/admin')
def admin():
    if not session or session.get('role') != 'Admin':
        return render_template('error.html', error_type="No Access", error_title="Unauthorized", error_subtitle="You do not have permission to access the admin dashboard.")
    with db.connect(db_path) as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM users ORDER BY uid DESC")
        users = cursor.fetchall()
        cursor.execute("SELECT * FROM author_requests ORDER BY uid DESC")
        author_requests = cursor.fetchall()

    return render_template('admin-pages/dashboard.html', users=users, author_requests=author_requests, name=session.get('name'))

@app.route('/admin/giveauthor/<int:uid>', methods=['GET', 'POST'])
def clear_author_request(uid):
    if not session:
        print("no session")
        return redirect(url_for('login'))

    if session.get('role') != 'Admin':
        print("no admin")
        return render_template('error.html', error_type="Unauthorised Access", error_title="You do not have authorisation to view this content.", error_subtitle="If you think this is a mistake, please contact us.")

    with db.connect(db_path) as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM users ORDER BY uid DESC")
        users = cursor.fetchall()
        cursor.execute("SELECT * FROM author_requests ORDER BY uid DESC")
        author_requests = cursor.fetchall()

    if request.method == 'POST':
        print("POST request")
        accept_btn = request.form.get('accept-author-request')
        decline_btn = request.form.get('decline-author-request')

        if 'accept-author-request' in request.form:
            db.change_role(conn, uid, 'Author')
            conn.commit()
            print(f"Accepted author request for UID: {uid}")
        elif 'decline-author-request' in request.form:
            print(f"Declined author request for UID: {uid}")
        else:
            print("No valid action specified")

        with db.connect(db_path) as conn:
            cursor = conn.cursor()
            cursor.execute("DELETE FROM author_requests WHERE uid = ?", (uid,))
            conn.commit()
            print("authorised")

        return redirect(url_for('admin'))

    print("GET request")
    return redirect(url_for('admin'))
    # return render_template('/admin-pages/dashboard.html', users=users, author_requests=author_requests, name=session.get('name'))

@app.route('/admin/delete_user/<int:uid>', methods=['GET', 'POST'])
def delete_user(uid):
    if not session or session.get('role') != 'Admin':
        return render_template('error.html', error_type="No Access", error_title="Unauthorized", error_subtitle="You do not have permission to access the admin dashboard.")

    with db.connect(db_path) as conn:
        db.delete_user(conn, uid)

    return redirect(url_for('admin'))

@app.route('/courses/<int:cid>/tasks/<int:tid>', methods=['GET', 'POST'])
def view_task(cid, tid):
    if not session:
        return redirect(url_for('login'))
    
    user_id = session['user_id']
    
    with db.connect(db_path) as conn:
        task = db.get_task(conn, tid)
        course = db.get_course(conn, cid)
        is_completed = db.is_task_completed(conn, user_id, cid, tid)

    if request.method == 'POST':
        db.mark_task_as_complete(conn, user_id, cid, tid)
        return redirect(url_for('view_course', cid=cid))

    return render_template('course-pages/task.html', task=task, course=course, is_completed=is_completed, cid=cid, tid=tid)

@app.route('/complete_task/<int:cid>/<int:tid>', methods=['POST'])
def complete_task(cid, tid):
    if not session:
        return redirect(url_for('login'))
    
    return redirect(url_for('view_task', cid=cid, tid=tid))


# --- EMAIL CODE ---





# --- MAIN PROGRAM ---

db.create()
with db.connect(db_path) as conn:
    db.default_admin(conn)
    db.default_author(conn)

if __name__ == "__main__":
    app.run()
