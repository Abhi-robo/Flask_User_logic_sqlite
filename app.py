from flask import Flask, jsonify, render_template, redirect, url_for, flash, request
from flask_login import LoginManager, login_user, logout_user, login_required, current_user
from models import db, User
from forms import LoginForm, RegistrationForm
import os
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

app = Flask(__name__)
app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY', 'your-secret-key-here')
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///users.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

# Initialize extensions
db.init_app(app)
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'

@login_manager.user_loader
def load_user(id):
    return User.query.get(int(id))

# Create database tables and admin user
with app.app_context():
    db.create_all()
    # Create admin user if it doesn't exist
    admin = User.query.filter_by(username='admin').first()
    if admin is None:
        admin = User(username='admin', email='admin@example.com', is_admin=True)
        admin.set_password('admin123')
        db.session.add(admin)
        db.session.commit()

@app.route('/')
def home():
    return render_template('home.html', title='Home')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('home'))
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(username=form.username.data).first()
        if user is None or not user.check_password(form.password.data):
            flash('Invalid username or password')
            return redirect(url_for('login'))
        login_user(user, remember=form.remember_me.data)
        return redirect(url_for('home'))
    return render_template('login.html', title='Sign In', form=form)

@app.route('/register', methods=['GET', 'POST'])
def register():
    if current_user.is_authenticated:
        return redirect(url_for('home'))
    form = RegistrationForm()
    if form.validate_on_submit():
        user = User(username=form.username.data, email=form.email.data)
        user.set_password(form.password.data)
        db.session.add(user)
        db.session.commit()
        flash('Congratulations, you are now a registered user!')
        return redirect(url_for('login'))
    return render_template('register.html', title='Register', form=form)

@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('home'))

@app.route('/profile')
@login_required
def profile():
    return render_template('profile.html', title='Profile', user=current_user)

# Admin routes
@app.route('/admin')
@login_required
def admin():
    if not current_user.is_admin:
        flash('You do not have permission to access this page.')
        return redirect(url_for('home'))
    users = User.query.all()
    return render_template('admin.html', title='Admin', users=users)

@app.route('/admin/user/<int:id>/toggle')
@login_required
def toggle_user(id):
    if not current_user.is_admin:
        return jsonify({'error': 'Unauthorized'}), 403
    user = User.query.get_or_404(id)
    user.is_active = not user.is_active
    db.session.commit()
    return redirect(url_for('admin'))

# Your existing routes
@app.route('/planets')
@login_required
def get_planets():
    planets = [
        {"name": "Mercury", "distance_from_sun": "57.91 million km"},
        {"name": "Venus", "distance_from_sun": "108.2 million km"},
        {"name": "Earth", "distance_from_sun": "149.6 million km"},
        {"name": "Mars", "distance_from_sun": "227.9 million km"},
        {"name": "Jupiter", "distance_from_sun": "778.5 million km"},
        {"name": "Saturn", "distance_from_sun": "1.434 billion km"},
        {"name": "Uranus", "distance_from_sun": "2.871 billion km"},
        {"name": "Neptune", "distance_from_sun": "4.495 billion km"}
    ]
    return jsonify(planets)

@app.route('/stars')
@login_required
def get_stars():
    stars = [
        {"name": "Sun", "type": "G-type main-sequence"},
        {"name": "Sirius", "type": "A-type main-sequence"},
        {"name": "Betelgeuse", "type": "Red supergiant"},
        {"name": "Proxima Centauri", "type": "Red dwarf"}
    ]
    return jsonify(stars)

@app.route('/galaxies')
@login_required
def get_galaxies():
    galaxies = [
        {"name": "Milky Way", "type": "Spiral"},
        {"name": "Andromeda", "type": "Spiral"},
        {"name": "Triangulum", "type": "Spiral"},
        {"name": "Messier 87", "type": "Elliptical"}
    ]
    return jsonify(galaxies)

@app.route('/moons')
@login_required
def get_moons():
    moons = [
        {"name": "Moon", "planet": "Earth"},
        {"name": "Phobos", "planet": "Mars"},
        {"name": "Europa", "planet": "Jupiter"},
        {"name": "Titan", "planet": "Saturn"}
    ]
    return jsonify(moons)

if __name__ == '__main__':
    app.run(debug=True)
