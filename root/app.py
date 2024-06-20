from flask import Flask, render_template, url_for
import databases
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


# --- MAIN ---
if __name__ == "__main__":
    app.run()
    # ---TABLE CREATIONS---
        
    # --- USERS ---
    connection = databases.connect("users.db")
    databases.create_table(connection, "users", ["uid INTEGER PRIMARY KEY AUTOINCREMENT", "uname TEXT", "email TEXT", "password TEXT"])


    # --- COURSES ---
    databases.create_table(connection, "courses", ["cid INTEGER PRIMARY KEY AUTOINCREMENT", "cname TEXT", "description TEXT", "course_image TEXT"])
    databases.create_table(connection, "course_users", ["cid INTEGER", "uid INTEGER"])

    # --- PRINT TABLES ---
    databases.print_table(connection, "users")
    databases.print_table(connection, "courses")
    databases.print_table(connection, "course_users")