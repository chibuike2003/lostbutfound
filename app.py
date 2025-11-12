from flask import Flask, render_template, redirect, url_for, flash, request
from flask_sqlalchemy import SQLAlchemy
from flask_login import UserMixin, login_user, LoginManager, login_required, current_user, logout_user
from werkzeug.security import generate_password_hash, check_password_hash
from functools import wraps
from datetime import datetime
from PIL import Image
import imagehash
import os
import uuid

# --- Flask App Configuration ---
app = Flask(__name__)
app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY', 'default_secret_key_change_me')
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///search.sqlite'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['UPLOAD_FOLDER'] = os.path.join('static', 'uploads')

os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)

# --- Extensions Setup ---
db = SQLAlchemy(app)
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'
login_manager.login_message_category = 'info'

# --- User Loader ---
@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

# --- Database Models ---
class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(100), unique=True, nullable=False)
    password_hash = db.Column(db.String(200), nullable=False)
    email = db.Column(db.String(100), unique=True, nullable=False)
    is_admin = db.Column(db.Boolean, default=False)
    found_items = db.relationship('Item', backref='finder', lazy=True, foreign_keys='Item.finder_id')
    claimed_items = db.relationship('Item', backref='owner', lazy=True, foreign_keys='Item.owner_id')

class Item(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    item_name = db.Column(db.String(100), nullable=False)
    category = db.Column(db.String(50), nullable=False)
    description = db.Column(db.Text, nullable=False)
    location_found = db.Column(db.String(100))
    date_found = db.Column(db.String(10), default=lambda: datetime.now().strftime('%Y-%m-%d'))
    is_claimed = db.Column(db.Boolean, default=False)
    finder_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    owner_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=True)
    owner_contact = db.Column(db.String(100))
    image_filename = db.Column(db.String(200))
    image_hash = db.Column(db.String(50))

# --- Utility Decorator ---
def admin_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not current_user.is_authenticated or not current_user.is_admin:
            flash('Access denied: Admin privileges required.', 'danger')
            return redirect(url_for('index'))
        return f(*args, **kwargs)
    return decorated_function

# --- Routes ---
@app.route('/')
def index():
    return render_template('index.html')

# --- User Routes ---
@app.route('/register', methods=['GET', 'POST'])
def register():
    if current_user.is_authenticated:
        return redirect(url_for('index'))
    if request.method == 'POST':
        username = request.form.get('username')
        email = request.form.get('email')
        password = request.form.get('password')
        if not all([username, email, password]):
            flash('All fields are required.', 'danger')
            return redirect(url_for('register'))
        user_exists = User.query.filter((User.username == username) | (User.email == email)).first()
        if user_exists:
            flash('Username or Email already exists.', 'warning')
            return redirect(url_for('register'))
        hashed_password = generate_password_hash(password, method='scrypt')
        new_user = User(username=username, email=email, password_hash=hashed_password)
        if User.query.count() == 0:
            new_user.is_admin = True
            flash('First user registered as Admin.', 'info')
        try:
            db.session.add(new_user)
            db.session.commit()
            flash('Account created successfully! Please log in.', 'success')
            return redirect(url_for('login'))
        except Exception as e:
            db.session.rollback()
            flash(f'Error during registration: {e}', 'danger')
    return render_template('register.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('index'))
    if request.method == 'POST':
        identifier = request.form.get('identifier')
        password = request.form.get('password')
        user = User.query.filter((User.username == identifier) | (User.email == identifier)).first()
        if user and check_password_hash(user.password_hash, password) and not user.is_admin:
            login_user(user, remember=True)
            flash('Logged in successfully.', 'success')
            return redirect(url_for('index'))
        flash('Invalid username/email or password.', 'danger')
    return render_template('login.html')

@app.route('/logout')
@login_required
def logout():
    logout_user()
    flash('You have been logged out.', 'success')
    return redirect(url_for('index'))

# --- Admin Routes ---
@app.route('/admin_signup', methods=['GET', 'POST'])
def admin_signup():
    if current_user.is_authenticated:
        return redirect(url_for('admin_dashboard'))
    if request.method == 'POST':
        username = request.form.get('username')
        email = request.form.get('email')
        password = request.form.get('password')
        if not all([username, email, password]):
            flash('All fields are required.', 'danger')
            return redirect(url_for('admin_signup'))
        user_exists = User.query.filter((User.username == username) | (User.email == email)).first()
        if user_exists:
            flash('Username or Email already exists.', 'warning')
            return redirect(url_for('admin_signup'))
        hashed_password = generate_password_hash(password, method='scrypt')
        new_admin = User(username=username, email=email, password_hash=hashed_password, is_admin=True)
        try:
            db.session.add(new_admin)
            db.session.commit()
            flash('Admin account created. Please log in.', 'success')
            return redirect(url_for('admin_login'))
        except Exception as e:
            db.session.rollback()
            flash(f'Error: {e}', 'danger')
    return render_template('admin_signup.html')

@app.route('/admin_login', methods=['GET', 'POST'])
def admin_login():
    if current_user.is_authenticated:
        return redirect(url_for('admin_dashboard'))
    if request.method == 'POST':
        identifier = request.form.get('identifier')
        password = request.form.get('password')
        admin = User.query.filter((User.username == identifier) | (User.email == identifier)).first()
        if admin and check_password_hash(admin.password_hash, password) and admin.is_admin:
            login_user(admin, remember=True)
            flash('Admin logged in successfully.', 'success')
            return redirect(url_for('admin_dashboard'))
        flash('Invalid credentials.', 'danger')
    return render_template('admin_login.html')

@app.route('/admin')
@admin_required
def admin_dashboard():
    all_users = User.query.all()
    all_items = Item.query.all()
    return render_template('admin.html', users=all_users, items=all_items)

# --- Core Item Logic ---
@app.route('/report', methods=['GET', 'POST'])
@login_required
def report_found():
    if request.method == 'POST':
        item_name = request.form.get('item_name')
        category = request.form.get('category')
        description = request.form.get('description')
        location_found = request.form.get('location_found')
        image_file = request.files.get('item_image')
        if not all([item_name, category, description, location_found, image_file]):
            flash('All fields including image are required.', 'danger')
            return redirect(url_for('report_found'))

        filename = str(uuid.uuid4()) + os.path.splitext(image_file.filename)[1]
        filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        image_file.save(filepath)
        img_hash = str(imagehash.average_hash(Image.open(filepath)))

        new_item = Item(
            item_name=item_name,
            category=category,
            description=description,
            location_found=location_found,
            finder_id=current_user.id,
            image_filename=filename,
            image_hash=img_hash
        )
        try:
            db.session.add(new_item)
            db.session.commit()
            flash(f'Item "{item_name}" reported successfully!', 'success')
            return redirect(url_for('index'))
        except Exception:
            db.session.rollback()
            flash('Error saving item.', 'danger')
    return render_template('report_found.html')

@app.route('/search', methods=['GET', 'POST'])
def search_item():
    matches = []
    search_term = ""
    if request.method == 'POST':
        search_term = request.form.get('search_term', '').strip()
        search_image = request.files.get('search_image')
        if search_term:
            matches = Item.query.filter(
                (Item.item_name.ilike(f'%{search_term}%')) |
                (Item.description.ilike(f'%{search_term}%')),
                Item.is_claimed == False
            ).all()
        elif search_image:
            filepath = os.path.join(app.config['UPLOAD_FOLDER'], str(uuid.uuid4()) + os.path.splitext(search_image.filename)[1])
            search_image.save(filepath)
            img_hash = imagehash.average_hash(Image.open(filepath))
            all_items = Item.query.filter(Item.is_claimed == False).all()
            for item in all_items:
                if item.image_hash and img_hash - imagehash.hex_to_hash(item.image_hash) <= 5:
                    matches.append(item)
    return render_template('search.html', matches=matches, search_term=search_term)

@app.route('/claim/<int:item_id>', methods=['POST'])
@login_required
def claim_item(item_id):
    item = Item.query.get(item_id)
    if not item:
        flash('Item not found.', 'danger')
        return redirect(url_for('search_item'))
    if item.is_claimed:
        flash('This item has already been claimed.', 'warning')
        return redirect(url_for('search_item'))
    finder = User.query.get(item.finder_id)
    item.is_claimed = True
    item.owner_contact = current_user.email
    item.owner_id = current_user.id
    try:
        db.session.commit()
        flash(f"Claim successful! Finder contact: Email {finder.email}, Username {finder.username}", 'success')
    except Exception:
        db.session.rollback()
        flash('Error processing claim.', 'danger')
    return redirect(url_for('index'))

# --- App Entry Point ---
if __name__ == '__main__':
    with app.app_context():
        db.create_all()
    app.run(debug=True)
