from flask import Flask, render_template, request, redirect, url_for, flash
from flask_wtf import FlaskForm
from wtforms import StringField, IntegerField, DateField, SubmitField, SelectField
from wtforms.validators import DataRequired, Length, NumberRange, Optional
import requests
import mysql.connector

appFrontend = Flask(__name__)
appFrontend.config['SECRET_KEY'] = 'your_secret_key'
appFrontend.config['MYSQL_HOST'] = 'localhost'
appFrontend.config['MYSQL_USER'] = 'your_mysql_user'
appFrontend.config['MYSQL_PASSWORD'] = 'your_mysql_password'
appFrontend.config['MYSQL_DB'] = 'insurance'

# MySQL connection
#db = mysql.connector.connect(
#    host=app.config['MYSQL_HOST'],
#    user=app.config['MYSQL_USER'],
#    password=app.config['MYSQL_PASSWORD'],
#    database=app.config['MYSQL_DB']
#)
# cursor = db.cursor()

class InsuranceForm(FlaskForm):
    insurance_type = SelectField('Versicherungsschutz', choices=[('vollkasko', 'Vollkasko'), ('teilkasko', 'Teilkasko')], validators=[DataRequired()])
    coverage_amount = IntegerField('Coverage Amount', validators=[DataRequired(), NumberRange(min=1000, max=1000000)])
    submit = SubmitField('Next')

class CarForm(FlaskForm):
    make = StringField('Car Make', validators=[DataRequired(), Length(max=50)])
    model = StringField('Car Model', validators=[DataRequired(), Length(max=50)])
    year = IntegerField('Year', validators=[DataRequired(), NumberRange(min=1900, max=2024)])
    submit = SubmitField('Next')

class UsageForm(FlaskForm):
    annual_mileage = IntegerField('Annual Mileage', validators=[DataRequired(), NumberRange(min=0, max=100000)])
    usage_type = StringField('Usage Type', validators=[DataRequired(), Length(max=50)])
    submit = SubmitField('Next')

class ApplicantForm(FlaskForm):
    name = StringField('Name', validators=[DataRequired(), Length(max=100)])
    birthdate = DateField('Birthdate', validators=[DataRequired()])
    submit = SubmitField('Next')

class PreviousInsuranceForm(FlaskForm):
    previous_insurer = StringField('Previous Insurer', validators=[Optional(), Length(max=50)])
    no_claim_bonus = IntegerField('No Claim Bonus', validators=[Optional(), NumberRange(min=0, max=100)])
    submit = SubmitField('Next')

@appFrontend.route('/', methods=['GET', 'POST'])
def insurance():
    form = InsuranceForm()
    if form.validate_on_submit():
        data = {
            'insurance_type': form.insurance_type.data,
            'coverage_amount': form.coverage_amount.data
        }
        response = requests.post('http://localhost:5001/validate_insurance', json=data)
        if response.ok:
            return redirect(url_for('car'))
        else:
            flash(response.json().get('message', 'An error occurred'), 'danger')
    return render_template('insurance.html', form=form)


@appFrontend.route('/car', methods=['GET', 'POST'])
def car():
    form = CarForm()
    if form.validate_on_submit():
        data = {
            'make': form.make.data,
            'model': form.model.data,
            'year': form.year.data
        }
        response = requests.post('http://localhost:5001/validate_car', json=data)
        if response.status_code == 200:
            return redirect(url_for('usage'))
        else:
            flash(response.json()['message'], 'danger')
    return render_template('car.html', form=form)

@appFrontend.route('/usage', methods=['GET', 'POST'])
def usage():
    form = UsageForm()
    if form.validate_on_submit():
        data = {
            'annual_mileage': form.annual_mileage.data,
            'usage_type': form.usage_type.data
        }
        response = requests.post('http://localhost:5001/validate_usage', json=data)
        if response.status_code == 200:
            return redirect(url_for('applicant'))
        else:
            flash(response.json()['message'], 'danger')
    return render_template('usage.html', form=form)

@appFrontend.route('/applicant', methods=['GET', 'POST'])
def applicant():
    form = ApplicantForm()
    if form.validate_on_submit():
        data = {
            'name': form.name.data,
            'birthdate': form.birthdate.data.strftime('%Y-%m-%d')
        }
        response = requests.post('http://localhost:5001/validate_applicant', json=data)
        if response.status_code == 200:
            return redirect(url_for('previous_insurance'))
        else:
            flash(response.json()['message'], 'danger')
    return render_template('applicant.html', form=form)

@appFrontend.route('/previous_insurance', methods=['GET', 'POST'])
def previous_insurance():
    form = PreviousInsuranceForm()
    if form.validate_on_submit():
        data = {
            'previous_insurer': form.previous_insurer.data,
            'no_claim_bonus': form.no_claim_bonus.data
        }
        response = requests.post('http://localhost:5001/validate_previous_insurance', json=data)
        if response.status_code == 200:
            # Save to database
            save_to_db()
            flash('Application submitted successfully!', 'success')
            return redirect(url_for('insurance'))
        else:
            flash(response.json()['message'], 'danger')
    return render_template('previous_insurance.html', form=form)

def save_to_db():
    # This function should be called to save the entire application data to the database
    pass

if __name__ == '__main__':
    appFrontend.run(debug=True, port=5000)
