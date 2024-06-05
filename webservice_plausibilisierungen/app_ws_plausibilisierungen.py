from flask import Flask, request, jsonify
import mysql.connector
from datetime import datetime, date
import json
import uuid

appWs = Flask(__name__)

db = mysql.connector.connect(
    host='localhost',
    user='TAA',
    password='FinconReply',
    database='TAA_Demo'
)
cursor = db.cursor()

def generate_erfassung_id():
    return str(uuid.uuid4())

def db_inserts(query, params):
    print(query, params)
    cursor.execute(query, params)
    db.commit()

def db_execute(query):
    cursor.execute(query)
    db.commit()

def db_select(query):
    print(query)
    cursor.execute(query)
    # Abfrageergebnisse in ein Dictionary umwandeln
    columns = [desc[0] for desc in cursor.description]
    results = [dict(zip(columns, row)) for row in cursor.fetchall()]

    print(results)

    # Felder mit None entfernen
    cleaned_results = []
    for result in results:
        cleaned_result = {k: v for k, v in result.items() if v is not None}
        for key, value in cleaned_result.items():
            if isinstance(value, date):
                cleaned_result[key] = value.strftime("%d.%m.%Y")
        cleaned_results.append(cleaned_result)
    return cleaned_results

@appWs.route('/validate_insurance', methods=['GET', 'POST'])
def validate_insurance():
    data = request.json
    erfassung_id = generate_erfassung_id()
    if data['grund'] not in ['Versicherungswechsel', 'Neues Fahrzeug']:
        return jsonify({'message': 'Fehler bei der Art der Versicherung'}), 400
    try:
        versicherungsbeginn = datetime.strptime(data['versicherungsbeginn'], '%Y-%m-%d')
    except ValueError:
        return jsonify({'message': 'Versicherungsbeginn ungültig'}), 400

    sql = "INSERT INTO versicherung (erfassung_id, grund, versicherungsbeginn, versicherungsart, deckungssumme) VALUES (%s, %s, %s, %s, %s)"
    params = (erfassung_id, data['grund'], data['versicherungsbeginn'], data['versicherungsart'], data['deckungssumme'])
    db_inserts(sql, params)
    return jsonify({'message': 'Valide', 'erfassung_id': erfassung_id}), 200

@appWs.route('/validate_car', methods=['POST'])
def validate_car():
    data = request.json
    erfassung_id = data.get('erfassung_id')
    current_year = datetime.now().year
    if data['baujahr'] < 1900 or data['baujahr'] > current_year:
        return jsonify({'message': f'Baujahr muss zwischen 1900 and {current_year} liegen'}), 400

    sql = "INSERT INTO auto (erfassung_id, hersteller, modell, hsn, tsn, baujahr) VALUES (%s, %s, %s, %s, %s, %s)"
    params = (erfassung_id, data['hersteller'], data['modell'], data['hsn'], data['tsn'], data['baujahr'])
    db_inserts(sql, params)

    return jsonify({'message': 'Valid'}), 200

@appWs.route('/validate_usage', methods=['POST'])
def validate_usage():
    data = request.json
    erfassung_id = data.get('erfassung_id')
    if data['jahresfahrleistung'] < 0 or data['jahresfahrleistung'] > 100000:
        return jsonify({'message': 'Jahresfahrleistung muss zwischen 0 and 100.000 Kilometern liegen'}), 400

    sql = "INSERT INTO nutzung (erfassung_id, jahresfahrleistung, nutzungsart) VALUES (%s, %s, %s)"
    params = (erfassung_id, data['jahresfahrleistung'], data['nutzungsart'])
    db_inserts(sql, params)

    return jsonify({'message': 'Valid'}), 200

@appWs.route('/validate_applicant', methods=['POST'])
def validate_applicant():
    data = request.json
    erfassung_id = data.get('erfassung_id')
    try:
        geburtsdatum = datetime.strptime(data['geburtsdatum'], '%Y-%m-%d')
        fuehrerschein = datetime.strptime(data['fuehrerschein'], '%Y-%m-%d')
        print(geburtsdatum, fuehrerschein)
    except ValueError:
        return jsonify({'message': 'Falsches Datumsformat'}), 400

    if data['edit'] != 'true':
        sql = "INSERT INTO versicherungsnehmer (erfassung_id, anrede, name, vorname, strasse, plz, ort, geburtsdatum, fuehrerschein) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)"
        params = (erfassung_id, data['anrede'], data['name'], data['vorname'], data['strasse'], data['plz'], data['ort'], data['geburtsdatum'], data['fuehrerschein'])
    else:
        sql = "update versicherungsnehmer set erfassung_id = %s, anrede = %s, name = %s, vorname = %s, strasse = %s, plz = %s, ort = %s, geburtsdatum = %s, fuehrerschein = %s where id = %s"
        params = (erfassung_id, data['anrede'], data['name'], data['vorname'], data['strasse'], data['plz'], data['ort'], data['geburtsdatum'], data['fuehrerschein'], data['id'])

    db_inserts(sql, params)

    return jsonify({'message': 'Valid'}), 200

@appWs.route('/validate_previous_insurance', methods=['POST'])
def validate_previous_insurance():
    data = request.json
    erfassung_id = data.get('erfassung_id')
    if data.get('schadenfreiheitsrabatt') is not None:
        if len(data['schadenfreiheitsrabatt']) > 3:
            return jsonify({'message': 'Schadenfreiheitsrabatt ungueltig'}), 400

    sql = "INSERT INTO vorversicherung (erfassung_id, vorversicherer, schadenfreiheitsrabatt, schadenfreiheitsrabatt_vk) VALUES (%s, %s, %s, %s)"
    params = (erfassung_id, data['vorversicherer'], data['schadenfreiheitsrabatt'], data['schadenfreiheitsrabatt_vk'])
    db_inserts(sql, params)

    return jsonify({'message': 'Valid'}), 200

@appWs.route('/get_applications', methods=['GET', 'POST'])
def get_applications():
    sql = "select * from versicherung v " \
          "left outer join nutzung n " \
          "on v.erfassung_id = n.erfassung_id " \
          "left outer join versicherungsnehmer vn " \
          "on v.erfassung_id = vn.erfassung_id " \
          "left outer join auto a " \
          "on v.erfassung_id = a.erfassung_id " \
          "left outer join vorversicherung vv " \
          "on v.erfassung_id = vv.erfassung_id " \
          "order by v.erfassung_id desc"
    payload = db_select(sql)
    print(payload)
    return jsonify(payload)

@appWs.route('/get_application', methods=['GET', 'POST'])
def get_application():
    data = request.json
    sql = "select * from versicherung v " \
          "left outer join nutzung n " \
          "on v.erfassung_id = n.erfassung_id " \
          "left outer join versicherungsnehmer vn " \
          "on v.erfassung_id = vn.erfassung_id " \
          "left outer join auto a " \
          "on v.erfassung_id = a.erfassung_id " \
          "left outer join vorversicherung vv " \
          "on v.erfassung_id = vv.erfassung_id " \
          "where v.erfassung_id = '" + str(data['erfassung_id'] + "'")
    payload = db_select(sql)
    print(payload)
    return jsonify(payload)

@appWs.route('/get_customers', methods=['GET', 'POST'])
def get_customers():
    sql = "select * from versicherungsnehmer v " \
          "order by name asc"
    payload = db_select(sql)
    print(payload)
    return jsonify(payload)

@appWs.route('/get_customer', methods=['GET', 'POST'])
def get_customer():
    data = request.json
    print(data)
    sql = "select * from versicherungsnehmer v where id = '" + data['id'] + "' " \
          "order by name asc"
    payload = db_select(sql)
    print(payload)
    return jsonify(payload)

@appWs.route('/reset_tables', methods=['GET', 'POST'])
def reset_tables():
    tables_to_delete = ['versicherung', 'auto', 'nutzung', 'versicherungsnehmer', 'vorversicherung']
    for table in tables_to_delete:
        sql = (f"DELETE FROM {table}")
        db_execute(sql)
    return jsonify({'message': 'Ok'}), 200


if __name__ == '__main__':
    appWs.run(debug=True, host='0.0.0.0', port=5001)
