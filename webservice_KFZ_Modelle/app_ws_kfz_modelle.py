from flask import Flask, request, jsonify
from datetime import datetime
import mysql.connector

app = Flask(__name__)

# MySQL connection
db = mysql.connector.connect(
    host='localhost',
    user='TAA',
    password='FinconReply',
    database='TAA_Demo'
)
cursor = db.cursor()

@app.route('/get_models', methods=['GET'])
def get_models():
    make = request.args.get('make')
    query = "SELECT hersteller, modell, hsn, tsn, anzahl FROM kfz_modelle WHERE hersteller like %s OR modell like %s"
    print(query, make)
    cursor.execute(query, ('%'+make+'%', '%'+make+'%'))
    models = [{'model': row[0] + ' Modell: ' + row[1] + ' (' + row[2] + ' / ' + row[3] + ') - Anzahl: ' + row[4] + ' -', 'hsn': row[2], 'tsn': row[3]} for row in cursor.fetchall()]
    response = jsonify(models)
    response.headers.add('Access-Control-Allow-Origin', '*')
    return response, 200

@app.route('/get_sf_options', methods=['GET'])
def get_sf_classes():
    make = request.args.get('make')
    query = "SELECT sf_klasse, schadenfreie_zeit FROM schadenfreiheitsklassen order by schadenfreie_zeit"
    cursor.execute(query)
    sf_klassen = [{'sf-lesbar': "SF " + str(row[0]) + " - " + str(row[1]) + " schadenfreie Jahre", 'sf': str(row[0])} for row in cursor.fetchall()]
    response = jsonify(sf_klassen)
    response.headers.add('Access-Control-Allow-Origin', '*')
    return response, 200


if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5010)