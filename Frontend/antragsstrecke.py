from flask import Flask, render_template, request, redirect, url_for, flash, session
from flask_wtf import FlaskForm
from wtforms import StringField, IntegerField, DateField, SubmitField, SelectField, RadioField
from wtforms.validators import DataRequired, Length, NumberRange, Optional
from wtforms.widgets import ListWidget, CheckboxInput
from datetime import datetime
import requests
import mysql.connector

app = Flask(__name__)
app.config['SECRET_KEY'] = 'your_secret_key'
app.config['MYSQL_HOST'] = 'localhost'
app.config['MYSQL_USER'] = 'your_mysql_user'
app.config['MYSQL_PASSWORD'] = 'your_mysql_password'
app.config['MYSQL_DB'] = 'insurance'

# Server
serviceValidation = "http://127.0.0.1:5001"
serviceBackend = "http://127.0.0.1:5010"

# MySQL connection
#db = mysql.connector.connect(
#    host=app.config['MYSQL_HOST'],
#    user=app.config['MYSQL_USER'],
#    password=app.config['MYSQL_PASSWORD'],
#    database=app.config['MYSQL_DB']
#)
# cursor = db.cursor()

class VersicherungsForm(FlaskForm):
    grund = SelectField('Grund der Versicherung', choices=[('', 'Bitte auswählen'), ('Versicherungswechsel', 'Versicherung wechseln'), ('Neues Fahrzeug', 'Neu angeschafftes Fahrzeug')], validators=[DataRequired()])
    versicherungsbeginn = DateField('Versicherungsbeginn', validators=[DataRequired()])
    versicherungsart = SelectField('Versicherungsart', choices=[('', 'Bitte auswählen'), ('Vollkasko', 'Vollkasko'), ('Teilkasko', 'Teilkasko'), ('KFZ-Haftpflicht', 'KFZ-Haftpflicht')], validators=[DataRequired()])
    deckungssumme = IntegerField('Deckungssumme', validators=[DataRequired(), NumberRange(min=1000, max=1000000)])
    submit = SubmitField('Weiter')

class AutoForm(FlaskForm):
    hersteller = StringField('Hersteller', validators=[DataRequired(), Length(max=50)])
    modell = SelectField('Modell', choices=[('', 'Bitte auswählen')], validators=[DataRequired()])
    hsn = StringField('HSN', render_kw={'readonly': True})
    tsn = StringField('TSN', render_kw={'readonly': True})
    baujahr = IntegerField('Baujahr', validators=[DataRequired(), NumberRange(min=1900, max=2024)])
    submit = SubmitField('Weiter')

class NutzungsForm(FlaskForm):
    jahresfahrleistung = IntegerField('jährliche Fahrleistung', validators=[DataRequired(), NumberRange(min=0, max=100000)])
    nutzungsart = RadioField('Verwendung', choices=[('nur privat', 'nur privat'), ('nur gewerblich', 'nur gewerblich'), ('privat und gewerblich', 'Privat und gewerblich')], validators=[DataRequired()])
    submit = SubmitField('Weiter')

class VersicherungsnehmerForm(FlaskForm):
    anrede = SelectField('Anrede', choices=[('', 'Bitte auswählen'), ('Frau', 'Frau'), ('Herr', 'Herr'), ('Divers', 'Divers')], validators=[DataRequired()])
    name = StringField('Name', validators=[DataRequired(), Length(max=100)])
    vorname = StringField('Vorname', validators=[DataRequired(), Length(max=100)])
    strasse = StringField('Strasse', validators=[DataRequired(), Length(max=100)])
    plz = StringField('PLZ', validators=[DataRequired(), Length(max=100)])
    ort = StringField('Ort', validators=[DataRequired(), Length(max=100)])
    geburtsdatum = DateField('Geburtsdatum', validators=[DataRequired()])
    fuehrerschein = DateField('Führerschein erworben am', validators=[DataRequired()])
 #   rolle = RadioField('Nutzungsart', choices=[('privat', 'Privat'), ('gewerblich', 'Gewerblich')], validators=[DataRequired()])
    submit = SubmitField('Weiter')

class VorversicherungForm(FlaskForm):
    vorversicherer = StringField('Vorversicherer', validators=[Optional(), Length(max=50)])
    schadenfreiheitsrabatt = SelectField('Schadenfreiheitsrabatt TK', choices=[('', 'Bitte auswählen')], validators=[Optional()])
    schadenfreiheitsrabatt_vk = SelectField('Schadenfreiheitsrabatt VK', choices=[('', 'Bitte auswählen')], validators=[Optional()])
    submit = SubmitField('Weiter')

class AntragForm(FlaskForm):
    grund = StringField('Grund der Versicherung', render_kw={'readonly': True})
    versicherungsbeginn = StringField('Versicherungsbeginn', render_kw={'readonly': True})
    versicherungsart = StringField('Versicherungsart', render_kw={'readonly': True})
    deckungssumme = StringField('Deckungssumme', render_kw={'readonly': True})
    hersteller = StringField('Hersteller', render_kw={'readonly': True})
    modell = StringField('Modell', render_kw={'readonly': True})
    hsn = StringField('HSN', render_kw={'readonly': True})
    tsn = StringField('TSN', render_kw={'readonly': True})
    baujahr = StringField('Baujahr', render_kw={'readonly': True})
    jahresfahrleistung = StringField('jährliche Fahrleistung', render_kw={'readonly': True})
    nutzungsart = StringField('Verwendung', render_kw={'readonly': True})
    anrede = StringField('Anrede', render_kw={'readonly': True})
    name = StringField('Name', render_kw={'readonly': True})
    vorname = StringField('Vorname', render_kw={'readonly': True})
    strasse = StringField('Strasse', render_kw={'readonly': True})
    plz = StringField('PLZ', render_kw={'readonly': True})
    ort = StringField('Ort', render_kw={'readonly': True})
    geburtsdatum = StringField('Geburtsdatum', render_kw={'readonly': True})
    fuehrerschein = StringField('Führerschein erworben am', render_kw={'readonly': True})
    vorversicherer = StringField('Vorversicherer', render_kw={'readonly': True})
    schadenfreiheitsrabatt = StringField('Schadenfreiheitsrabatt', render_kw={'readonly': True})
    schadenfreiheitsrabatt_vk = StringField('Schadenfreiheitsrabatt VK', render_kw={'readonly': True})


def get_car_models(hersteller):
    response = requests.get(serviceBackend + '/get_models', params={'make': hersteller})
    if response.ok:
        models = response.json()
        return [('', 'Bitte auswählen')] + [(model['model'], model['model']) for model in models]
    return []

def get_schadenfreiheitsrabatt_options():
    response = requests.get(serviceBackend + '/get_sf_options')
    if response.ok:
        options = response.json()
        return [('', 'Bitte auswählen')] + [(str(option['sf']), str(option['sf-lesbar'])) for option in options]
    return [('', 'Bitte auswählen')]

@app.route('/', methods=['GET', 'POST'])
def versicherung():
    form = VersicherungsForm()
    if form.validate_on_submit():
        data = {
            'grund': form.grund.data,
            'versicherungsbeginn': form.versicherungsbeginn.data.strftime('%Y-%m-%d'),
            'versicherungsart': form.versicherungsart.data,
            'deckungssumme': form.deckungssumme.data
        }
        response = requests.post('http://127.0.0.1:5001/validate_insurance', json=data)
        if response.ok:
            session['erfassung_id'] = response.json()['erfassung_id']
            return redirect(url_for('auto'))
        else:
            print("response", response)
            flash(response.json().get('message', 'An error occurred'), 'danger')
    return render_template('versicherung.html', form=form)

@app.route('/auto', methods=['GET', 'POST'])
def auto():
    form = AutoForm()
    if request.method == 'POST':
        form.modell.choices = get_car_models(form.hersteller.data)
        if form.validate_on_submit():
            data = {
                'erfassung_id': session.get('erfassung_id'),
                'hersteller': form.hersteller.data,
                'modell': form.modell.data,
                'hsn': form.hsn.data,
                'tsn': form.tsn.data,
                'baujahr': form.baujahr.data
            }
            response = requests.post(serviceValidation+'/validate_car', json=data)
            if response.ok:
                return redirect(url_for('nutzung'))
            else:
                flash(response.json().get('message', 'An error occurred'), 'danger')
    else:
        form.modell.choices = []
    return render_template('auto.html', form=form)

@app.route('/nutzung', methods=['GET', 'POST'])
def nutzung():
    form = NutzungsForm()
    if form.validate_on_submit():
        data = {
            'erfassung_id': session.get('erfassung_id'),
            'jahresfahrleistung': form.jahresfahrleistung.data,
            'nutzungsart': form.nutzungsart.data
        }
        response = requests.post(serviceValidation+'/validate_usage', json=data)
        if response.ok:
            return redirect(url_for('versicherungsnehmer'))
        else:
            flash(response.json().get('message', 'An error occurred'), 'danger')
    return render_template('nutzung.html', form=form)

@app.route('/versicherungsnehmer', methods=['GET', 'POST'])
def versicherungsnehmer():
    form = VersicherungsnehmerForm()
    if form.validate_on_submit():
        data = {
            'erfassung_id': session.get('erfassung_id'),
            'anrede': form.anrede.data,
            'name': form.name.data,
            'vorname': form.vorname.data,
            'strasse': form.strasse.data,
            'plz': form.plz.data,
            'ort': form.ort.data,
            'geburtsdatum': form.geburtsdatum.data.strftime('%Y-%m-%d'),
            'fuehrerschein': form.fuehrerschein.data.strftime('%Y-%m-%d'),
            'edit': 'false'
        }
        response = requests.post(serviceValidation+'/validate_applicant', json=data)
        if response.ok:
            return redirect(url_for('vorversicherung'))
        else:
            flash(response.json().get('message', 'An error occurred'), 'danger')
    return render_template('versicherungsnehmer.html', form=form)

@app.route('/edit_versicherungsnehmer', methods=['GET', 'POST'])
def edit_versicherungsnehmer():
    kunde_id = request.args.get('kunde_id')
    payload = {
        'id': kunde_id
    }
    headers = {
        'Content-type': 'application/json'}
    r = requests.post(serviceValidation + '/get_customer', json=payload, headers=headers)
    data = r.json()
    data[0]['geburtsdatum'] = datetime.strptime(data[0]['geburtsdatum'], '%d.%m.%Y').strftime('%Y-%m-%d')
    data[0]['fuehrerschein'] = datetime.strptime(data[0]['fuehrerschein'], '%d.%m.%Y').strftime('%Y-%m-%d')


    form = VersicherungsnehmerForm(anrede=str(data[0]['anrede']))
    if form.validate_on_submit():
        data = {
            'id': kunde_id,
            'erfassung_id': session.get('erfassung_id'),
            'anrede': form.anrede.data,
            'name': form.name.data,
            'vorname': form.vorname.data,
            'strasse': form.strasse.data,
            'plz': form.plz.data,
            'ort': form.ort.data,
            'geburtsdatum': form.geburtsdatum.data.strftime('%Y-%m-%d'),
            'fuehrerschein': form.fuehrerschein.data.strftime('%Y-%m-%d'),
            'edit': 'true'
        }
        response = requests.post(serviceValidation+'/validate_applicant', json=data)
        data = response.json()
        if response.ok:
            return redirect(url_for('kundenuebersicht'))
        else:
            flash(response.json().get('message', 'An error occurred'), 'danger')
    return render_template('edit_versicherungsnehmer.html', form=form, data=data)

@app.route('/vorversicherung', methods=['GET', 'POST'])
def vorversicherung():
    form = VorversicherungForm()
    form.schadenfreiheitsrabatt.choices = get_schadenfreiheitsrabatt_options()
    form.schadenfreiheitsrabatt_vk.choices = get_schadenfreiheitsrabatt_options()
    if form.validate_on_submit():
        data = {
            'erfassung_id': session.get('erfassung_id'),
            'vorversicherer': form.vorversicherer.data,
            'schadenfreiheitsrabatt': form.schadenfreiheitsrabatt.data,
            'schadenfreiheitsrabatt_vk': form.schadenfreiheitsrabatt_vk.data
        }
        response = requests.post(serviceValidation+'/validate_previous_insurance', json=data)
        if response.ok:
            # Save to database
            save_to_db()
            flash('Antrag erfolgreich eingereicht!', 'success')
            return redirect(url_for('antragsuebersicht'))
        else:
            flash(response.json().get('message', 'An error occurred'), 'danger')
    return render_template('vorversicherung.html', form=form)

@app.route('/antragsuebersicht', methods=['GET', 'POST'])
def antragsuebersicht():
    response = requests.get(serviceValidation + '/get_applications')
    data = response.json()
    return render_template('antragsuebersicht.html', data=data)

@app.route('/kundenuebersicht', methods=['GET', 'POST'])
def kundenuebersicht():
    response = requests.get(serviceValidation + '/get_customers')
    data = response.json()
    return render_template('kundenuebersicht.html', data=data)

@app.route('/antrag_detail', methods=['GET', 'POST'])
def antrag_detail():
    erfassung_id = request.args.get('erfassung_id')
    payload = {
        'erfassung_id': erfassung_id
    }
    headers = {
        'Content-type': 'application/json'}
    r = requests.post(serviceValidation + '/get_application', json=payload, headers=headers)
    data = r.json()
    data[0]['geburtsdatum'] = datetime.strptime(data[0]['geburtsdatum'], '%d.%m.%Y').strftime('%Y-%m-%d')
    data[0]['fuehrerschein'] = datetime.strptime(data[0]['fuehrerschein'], '%d.%m.%Y').strftime('%Y-%m-%d')

    form = AntragForm(anrede=str(data[0]['anrede']))
    return render_template('antrag_detail.html', form=form, data=data[0])

@app.route('/admin_reset', methods=['GET', 'POST'])
def admin_reset():
    response = requests.get(serviceValidation + '/reset_tables')
    data = response.json()
    return render_template('antragsuebersicht.html', data=data)

def save_to_db():
    # This function should be called to save the entire application data to the database
    pass

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)
