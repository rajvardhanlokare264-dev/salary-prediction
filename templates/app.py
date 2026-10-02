from flask import Flask, render_template, request, redirect, url_for, flash, session, jsonify
from database import register_user, verify_user
from model import predict_salary, get_companies_for_role, get_job_roles_by_education
import re
import logging

app = Flask(__name__)
app.secret_key = 'your-secret-key-here'  # Change this to a secure secret key

# Set up logging
logging.basicConfig(level=logging.INFO)
app.logger.setLevel(logging.INFO)

@app.route('/')
def home():
    if 'username' in session:
        return redirect(url_for('dashboard'))
    return render_template('home page.html')

@app.route('/about')
def about():
    return render_template('about.html')

@app.route('/prediction')
def prediction():
    if 'username' not in session:
        return redirect(url_for('login'))
    return render_template('prediction.html')

@app.route('/predict_salary', methods=['POST'])
def predict():
    if 'username' not in session:
        app.logger.error('User not logged in')
        return jsonify({'error': 'Please log in first'}), 401
    
    try:
        # Get form data
        data = request.form
        experience = data.get('experience')
        education = data.get('education')
        job_role = data.get('job_role')
        location = data.get('location')
        
        # Validate inputs
        if not all([experience, education, job_role, location]):
            app.logger.error('Missing form data')
            return jsonify({'error': 'All fields are required'}), 400
        
        # Convert experience to float
        experience = float(experience)
        if experience < 0:
            app.logger.error('Invalid experience value')
            return jsonify({'error': 'Experience cannot be negative'}), 400
        
        # Get salary prediction and companies
        predicted_salary = predict_salary(experience, education, job_role, location)
        companies = get_companies_for_role(job_role)
        
        # Format salary with lakhs and thousands
        formatted_salary = f"{predicted_salary:,.2f} LPA"
        
        return jsonify({
            'predicted_salary': formatted_salary,
            'companies': companies
        })
    except ValueError as e:
        app.logger.error(f"Value error: {str(e)}")
        return jsonify({'error': str(e)}), 400
    except Exception as e:
        app.logger.error(f"Error in prediction: {str(e)}")
        return jsonify({'error': 'An error occurred during prediction'}), 500

@app.route('/mnc')
def mnc():
    return render_template('mnc.html')

@app.route('/contact', methods=['GET', 'POST'])
def contact():
    if request.method == 'POST':
        try:
            data = request.json
            name = data.get('name')
            email = data.get('email')
            message = data.get('message')

            # Validate inputs
            if not all([name, email, message]):
                app.logger.error('Missing contact form data')
                return jsonify({'message': 'Please fill in all fields'}), 400

            # Validate email format
            if not re.match(r"[^@]+@[^@]+\.[^@]+", email):
                app.logger.error('Invalid email format')
                return jsonify({'message': 'Please enter a valid email address'}), 400

            # Here you would typically send the email or store the message
            # For now, we'll just log it
            app.logger.info(f'Contact form submission from {name} ({email}): {message}')
            
            return jsonify({'message': 'Thank you for your message! We will get back to you soon.'}), 200
        except Exception as e:
            app.logger.error(f'Error processing contact form: {str(e)}')
            return jsonify({'message': 'An error occurred. Please try again.'}), 500

    return render_template('contact.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        
        if not username or not password:
            app.logger.error('Missing login credentials')
            return render_template('login.html', error='Please fill in all fields')
        
        if verify_user(username, password):
            session['username'] = username
            return redirect(url_for('dashboard'))
        else:
            app.logger.error('Invalid login credentials')
            return render_template('login.html', error='Invalid username or password')
    
    return render_template('login.html')

@app.route('/signup', methods=['GET', 'POST'])
def signup():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        confirm_password = request.form['confirm_password']
        email = request.form['email']

        # Validation
        if not username or not password or not confirm_password or not email:
            app.logger.error('Missing signup information')
            return render_template('signup.html', error='Please fill in all fields')

        if len(password) < 8:
            app.logger.error('Password too short')
            return render_template('signup.html', error='Password must be at least 8 characters long')

        if not re.match(r'^[a-zA-Z0-9_]+$', username):
            app.logger.error('Invalid username')
            return render_template('signup.html', error='Username can only contain letters, numbers, and underscores')

        if not re.match(r'^[\w\.-]+@[\w\.-]+\.\w+$', email):
            app.logger.error('Invalid email')
            return render_template('signup.html', error='Please enter a valid email address')

        if password != confirm_password:
            app.logger.error('Passwords do not match')
            return render_template('signup.html', error='Passwords do not match')

        if register_user(username, password, email):
            return redirect(url_for('login'))
        else:
            app.logger.error('Username or email already exists')
            return render_template('signup.html', error='Username or email already exists')

    return render_template('signup.html')

@app.route('/dashboard')
def dashboard():
    if 'username' not in session:
        app.logger.error('User not logged in')
        return redirect(url_for('login'))
    return render_template('dashboard.html')

@app.route('/get_jobs_by_education/<education>')
def get_jobs_by_education(education):
    jobs = get_job_roles_by_education(education)
    return jsonify(jobs)

@app.route('/logout')
def logout():
    session.pop('username', None)
    return redirect(url_for('home'))

if __name__ == '__main__':
    app.run(debug=True)
