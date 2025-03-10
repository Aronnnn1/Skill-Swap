from flask import Flask, render_template, request, jsonify, redirect, url_for, flash, session
from flask_pymongo import PyMongo
from flask_cors import CORS
from werkzeug.security import generate_password_hash, check_password_hash
from bson import ObjectId
from flask_login import LoginManager, UserMixin, login_user, logout_user, login_required
from werkzeug.utils import secure_filename
import os, secrets, datetime, logging
from moviepy.editor import VideoFileClip

app = Flask(__name__)

app.config['SECRET_KEY'] = secrets.token_hex(16)
app.config['SESSION_COOKIE_HTTPONLY'] = True
app.config["MONGO_URI"] = "mongodb://localhost:27017/skill_swap"
mongo = PyMongo(app)
CORS(app)  # Enable CORS for all routes

login_manager = LoginManager()
login_manager.init_app(app)

# Dummy User class
class User(UserMixin):
    def __init__(self, id):
        self.id = id

def generate_thumbnail(video_path):
    # Load the video
    video = VideoFileClip(video_path)
    
    # Take a screenshot at the middle of the video (you can change the time to your preference)
    thumbnail_path = video_path.rsplit('.', 1)[0] + '.jpg'
    video.save_frame(thumbnail_path, t=video.duration / 2)
    return thumbnail_path

# Load user (for Flask-Login)
@login_manager.user_loader
def load_user(user_id):
    return User(user_id)

# Routes
@app.route('/')
def home():
    return render_template('home.html', title="Home Page - Skill-Swap")

@app.route('/about')
def about():
    return render_template('about.html', title="About Us Page - Skill-Swap")

@app.route('/comp_skills')
def comp_skills():
    # Logic to display computer skills services
    return render_template('comp_skills.html', title="Computer Skills Page - Skill-Swap")

@app.route('/music')
def music():
    # Logic to display music services
    return render_template('music.html', title="Music Page - Skill-Swap")

@app.route('/health')
def health():
    # Logic to display health and wellness services
    return render_template('health.html', title="Health Page - Skill-Swap")

@app.route('/java')
def java():
    return render_template('java.html', title="Java Page - Skill-Swap")

@app.route('/python')
def python():
    return render_template('python.html', title="Python Page - Skill-Swap")

@app.route('/mysql')
def mysql():
    return render_template('mysql.html', title="MySQL Page - Skill-Swap")

@app.route('/excel')
def excel():
    return render_template('excel.html', title="Excel Page - Skill-Swap")

@app.route('/guitar')
def guitar():
    return render_template('guitar.html', title="Guitar Page - Skill-Swap")

@app.route('/piano')
def piano():
    return render_template('piano.html', title="Piano Page - Skill-Swap")

@app.route('/drums')
def drums():
    return render_template('drums.html', title="Drums Page - Skill-Swap")

@app.route('/yoga')
def yoga():
    return render_template('yoga.html', title="Yoga Page - Skill-Swap")

@app.route('/fitness')
def fitness():
    return render_template('fitness.html', title="Fitness Page - Skill-Swap")

@app.route('/upload')
def upload():
    return render_template('upload.html', title="Upload Page - Skill-Swap")

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']
        
        # Check in both students and teachers collections
        user = mongo.db.students.find_one({"email": email}) or mongo.db.teachers.find_one({"email": email})
        
        if user and check_password_hash(user['password'], password):
            user_obj = User(str(user['_id']))
            login_user(user_obj)
            session['email'] = email
            session['role'] = 'student' if mongo.db.students.find_one({"email": email}) else 'teacher'
            flash('Successfully logged in!', 'success')
            return redirect(url_for('home'))
        else:
            flash('Login failed. Invalid email or password.', 'danger')
    
    return render_template('login.html', title="Login Page - Skill-Swap")

@app.route('/logout')
@login_required
def logout():
    logging.debug(f"Session before logout: {dict(session)}")
    
    # Remove email and role from the session
    session.pop('email', None)
    session.pop('role', None)

    # Invalidate the session cookie (optional)
    response = redirect(url_for('home'))
    response.set_cookie(app.config['SESSION_COOKIE_NAME'], '', expires=0)
    
    logout_user()  # Logs out the user from Flask-Login
    
    logging.debug(f"Session after logout: {dict(session)}")
    return response  # Redirects to the home page

@app.route('/student_register', methods=['GET', 'POST'])
def student_register():
    if request.method == 'POST':
        try:
            data = request.get_json()
            name = data['name']
            username = data['username']
            email = data['email']
            dob = data['dob']
            password = generate_password_hash(data['password'])

            student_collection = mongo.db.students
            if student_collection.find_one({"email": email}):
                return jsonify({"message": "Email already exists."}), 400

            student_collection.insert_one({
                "name": name,
                "username": username,
                "email": email,
                "dob": dob,
                "password": password,
                "subscription": None
            })

            return jsonify({"message": "Registration successful."}), 200
        except Exception as e:
            print(f"Error: {e}")
            return jsonify({"message": "Something went wrong during registration."}), 500
    else:
        return render_template('student_register.html', title="Student Registration Page - Skill-Swap")

@app.route('/teacher_register', methods=['GET', 'POST'])
def teacher_register():
    if request.method == 'POST':
        try:
            data = request.get_json()
            # Check for necessary fields
            if not all(key in data for key in ['name', 'username', 'email', 'dob', 'password', 'subjects', 'experience']):
                return jsonify({'message': 'Missing required fields'}), 400
            # Create teacher data
            teacher_data = {
                'name': data['name'],
                'username': data['username'],
                'email': data['email'],
                'dob': datetime.datetime.strptime(data['dob'], '%Y-%m-%d'),  # Converting string to date
                'password': generate_password_hash(data['password']),
                'subjects': data['subjects'],  # Storing subjects as a list
                'experience': data['experience'],  # Storing the experience description
                'date_joined': datetime.datetime.now()
            }
            mongo.db.teachers.insert_one(teacher_data)
            return jsonify({"message": "Teacher registration successful."}), 200
        except Exception as e:
            print(f"Error: {e}")
            return jsonify({"message": "Something went wrong during registration."}), 500
    else:
        return render_template('teacher_register.html', title="Teacher Registration Page - Skill-Swap")

@app.route('/get_teacher_subjects', methods=['GET'])
@login_required
def get_teacher_subjects():
    teacher_email = session.get('email')  # Ensure email is saved in session upon login
    teacher = mongo.db.teachers.find_one({"email": teacher_email})

    if teacher:
        return jsonify(teacher['subjects']), 200
    else:
        return jsonify({"message": "Teacher not found."}), 404

@app.route('/upload_video', methods=['POST'])
@login_required
def upload_video():
    if 'video' not in request.files:
        return jsonify({"message": "No file part"}), 400
    video = request.files['video']
    caption = request.form['caption']
    subject = request.form.get('subject', '').strip().lower()

    if video.filename == '':
        return jsonify({"message": "No selected file"}), 400

    email = session.get('email')
    # Check if the user is logged in
    if not email:
        return jsonify({"message": "User not authenticated."}), 401

    # Define the path where videos will be saved
    upload_folder = os.path.join(os.getcwd(), 'static', 'videos')
    if not os.path.exists(upload_folder):
        os.makedirs(upload_folder)  # Create the folder if it doesn't exist

    # Save the video file
    filename = secure_filename(video.filename)
    video_path = os.path.join(upload_folder, filename)
    video.save(video_path)  # Store in the "backend/videos" folder

    thumbnail_path = generate_thumbnail(video_path)
    thumbnail_filename = os.path.basename(thumbnail_path)

    # Save the video metadata to the database
    mongo.db.videos.insert_one({
        "caption": caption,
        "subject": subject,
        "video_path": filename,
        "thumbnail_path": thumbnail_filename,
        "uploaded_by": session.get('email'),
        "timestamp": datetime.datetime.now()
    })

    return jsonify({"message": "Video uploaded successfully!"}), 200

@app.route('/signup')
def signup():
    return render_template('signup.html', title="Signup Page - Skill-Swap")

@app.route('/video_tiles/<subject>', methods=['GET'])
@login_required
def video_tiles(subject):
    student = mongo.db.students.find_one({"email": session.get('email')})
    if not student or not student.get('subscription'):
        flash('You need a valid subscription to watch videos. Please subscribe.', 'danger')
        return redirect(url_for('subscriptions'))  # Redirect to subscriptions page if no subscription
    
    # Fetch videos related to the subject from the database
    subject = subject.strip().lower()
    videos = list(mongo.db.videos.find({"subject": subject}))
    processed_videos = []
    for video in videos:
        video_path = video.get('video_path', '')
        thumbnail_path = video.get('thumbnail_path', '')
        if not os.path.exists(os.path.join('static', 'videos', thumbnail_path)):
            if os.path.exists(os.path.join('static', 'videos', video_path)):
                try:
                    thumbnail_full_path = generate_thumbnail(os.path.join('static', 'videos', video_path))
                    thumbnail_path = os.path.basename(thumbnail_full_path)
                    mongo.db.videos.update_one(
                        {"_id": video["_id"]},
                        {"$set": {"thumbnail_path": thumbnail_path}}
                    )
                except Exception as e:
                    print(f"Error generating thumbnail for {video_path}: {e}")
        
        processed_videos.append({
            "caption": video.get('caption', 'No caption available'),
            "video_path": video_path,
            "thumbnail_path": thumbnail_path,
        })

    return render_template('video_tiles.html', videos=videos, subject=subject, title="Videos Page - Skill-Swap")

@app.route('/subscriptions', methods=['GET', 'POST'])
@login_required
def subscriptions():
    email = session.get('email')
    student = mongo.db.students.find_one({"email": email})
    
    if request.method == 'POST':
        # Get selected plan from the form
        plan = request.form['plan']
        price = {
            '1 week': 500,
            '1 month': 1000,
            '6 months': 1500,
            '12 months': 2500
        }[plan]

        # Calculate the start and end dates
        start_date = datetime.datetime.now()
        if plan == '1 week':
            end_date = start_date + datetime.timedelta(weeks=1)
        elif plan == '1 month':
            end_date = start_date + datetime.timedelta(weeks=4)
        elif plan == '6 months':
            end_date = start_date + datetime.timedelta(weeks=26)
        elif plan == '12 months':
            end_date = start_date + datetime.timedelta(weeks=52)

        # Store the selected plan and price in session
        session['plan'] = plan
        session['price'] = price
        session['start_date'] = start_date
        session['end_date'] = end_date

        # Redirect to the payment page
        return redirect(url_for('payment'))

    return render_template('subscriptions.html', student=student, title="Subscriptions - Skill-Swap")

@app.route('/payment', methods=['GET', 'POST'])
@login_required
def payment():
    if 'plan' not in session:
        return redirect(url_for('subscriptions'))  # Redirect to subscriptions if no plan is selected

    # Show the QR code and confirm payment
    if request.method == 'POST':
        # Confirm payment (this can be more sophisticated based on your payment process)
        email = session.get('email')
        student = mongo.db.students.find_one({"email": email})

        # Update subscription in the database after payment
        mongo.db.students.update_one(
            {"email": email},
            {"$set": {"subscription": {
                "plan": session['plan'],
                "price": session['price'],
                "start_date": session['start_date'],
                "end_date": session['end_date']
            }}}
        )

        # Update session with new subscription data
        session['subscription'] = {
            "plan": session['plan'],
            "price": session['price'],
            "start_date": session['start_date'],
            "end_date": session['end_date']
        }
        
        # Clear session after updating the subscription
        session.pop('plan', None)
        session.pop('price', None)
        session.pop('start_date', None)
        session.pop('end_date', None)

        # Redirect back to home page after successful payment
        return redirect(url_for('home'))  # Redirect to home.html (or your home route)

    # Render the payment page with QR code
    return render_template('payment.html', plan=session['plan'], price=session['price'], title="Payments Page - Skill-Swap")


if __name__ == '__main__':
    app.run(debug=True, port=5000)