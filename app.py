from flask import Flask, render_template, redirect, url_for, request, session, flash
from werkzeug.security import generate_password_hash, check_password_hash
from db_setup import init_db, query_db
import secrets
app = Flask(__name__)
app.secret_key = secrets.token_hex(16) 
@app.route('/')
def home():
    return render_template('home.html')


@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        name = request.form['name']
        blood_group = request.form['blood_group']
        email = request.form['email']
        dob = request.form['dob']
        password = generate_password_hash(request.form['password'])
        role = 'patient'  # Default role

        try:
            query_db('INSERT INTO users (name, blood_group, email, dob, password, role) VALUES (?, ?, ?, ?, ?, ?)',
                     (name, blood_group, email, dob, password, role))
            return redirect(url_for('login'))
        except:
            return "Email already registered.", 400
    return render_template('register.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']
        role = request.form['role']  # Role is selected from the dropdown in the login form
        user = query_db('SELECT * FROM users WHERE email = ?', [email], one=True)
        
        if user and check_password_hash(user['password'], password):  # Check if user exists and password matches
            # Ensure the selected role matches the user's role
            if user['role'] == role:
                session['user_id'] = user['id']
                session['role'] = user['role']
                
                # Redirect to the appropriate dashboard based on the role
                if user['role'] == 'doctor':
                    return redirect(url_for('doctor_dashboard'))
                elif user['role'] == 'patient':
                    return redirect(url_for('patient_dashboard'))
            else:
                flash('Invalid role selected. Please select the correct role.', 'danger')
                return render_template('login.html')  # Role mismatch
        else:
            flash('Invalid credentials. Please check your email and password.', 'danger')
            return render_template('login.html')  # Invalid credentials

    return render_template('login.html')



@app.route('/doctor_dashboard', methods=['GET', 'POST'])
def doctor_dashboard():
    if 'user_id' not in session or session['role'] != 'doctor':
        return redirect(url_for('login'))  # Ensure the user is logged in and is a doctor

    appointments = query_db('SELECT * FROM appointments')  # Get all appointments

    if request.method == 'POST':  # Handle prescription submission
        appointment_id = request.form['appointment_id']
        prescription = request.form['prescription']
        query_db('UPDATE appointments SET prescription = ? WHERE id = ?', (prescription, appointment_id))
        flash('Prescription added successfully!', 'success')

    return render_template('doctor_dashboard.html', appointments=appointments)
@app.route('/patient_dashboard', methods=['GET', 'POST'])
def patient_dashboard():
    if 'user_id' not in session or session['role'] != 'patient':
        return redirect(url_for('login'))  # Ensure the user is logged in and is a patient

    patient_id = session['user_id']
    appointments = query_db('''SELECT appointments.id, appointments.date_time, appointments.prescription, users.name AS doctor_name
                            FROM appointments
                            JOIN users ON appointments.doctor_id = users.id
                            WHERE appointments.patient_id = ?''', [patient_id])


    if request.method == 'POST':  # Handle appointment booking
        doctor_id = request.form['doctor_id']
        date_time = request.form['date_time']
        query_db('INSERT INTO appointments (patient_id, doctor_id, date_time) VALUES (?, ?, ?)',
                 (patient_id, doctor_id, date_time))
        flash('Appointment booked successfully!', 'success')

    doctors = query_db('SELECT * FROM users WHERE role = "doctor"')  # Get list of doctors
    return render_template('patient_dashboard.html', appointments=appointments, doctors=doctors)


@app.route('/logout')
def logout():
    session.clear()  # Clear session
    return redirect(url_for('login'))  # Redirect to login



if __name__ == '__main__':
    init_db()  # Ensure the database is initialized before running the app
    app.run(debug=True)
