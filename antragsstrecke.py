from flask import Flask, render_template, request

app = Flask(__name__)


@app.route('/')
def form():
    return render_template('form_demo.html')


@app.route('/submit', methods=['POST'])
def submit():
    name = request.form['name']
    address = request.form['address']
    birthdate = request.form['birthdate']
    license_number = request.form['license_number']
    car_model = request.form['car_model']
    car_year = request.form['car_year']
    insurance_type = request.form['insurance_type']

    # Hier kannst du die Daten weiterverarbeiten, z.B. in eine Datenbank speichern oder per E-Mail senden.

    return f"Versicherungsnehmer {name} erfolgreich erfasst!!"


if __name__ == '__main__':
    app.run(debug=True)
