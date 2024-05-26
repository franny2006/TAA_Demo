from flask import Flask, request, jsonify
import mysql.connector
from datetime import datetime

appWs = Flask(__name__)

@appWs.route('/validate_insurance', methods=['POST'])
def validate_insurance():
    data = request.json
    if data['insurance_type'] not in ['vollkasko', 'teilkasko']:
        return jsonify({'message': 'Invalid insurance type'}), 400
    if data['coverage_amount'] < 1000 or data['coverage_amount'] > 1000000:
        return jsonify({'message': 'Coverage amount must be between 1000 and 1000000'}), 400
    return jsonify({'message': 'Valid'}), 200

@appWs.route('/validate_car', methods=['POST'])
def validate_car():
    data = request.json
    current_year = datetime.now().year
    if data['year'] < 1900 or data['year'] > current_year:
        return jsonify({'message': f'Year must be between 1900 and {current_year}'}), 400
    return jsonify({'message': 'Valid'}), 200

@appWs.route('/validate_usage', methods=['POST'])
def validate_usage():
    data = request.json
    if data['annual_mileage'] < 0 or data['annual_mileage'] > 100000:
        return jsonify({'message': 'Annual mileage must be between 0 and 100000'}), 400
    return jsonify({'message': 'Valid'}), 200

@appWs.route('/validate_applicant', methods=['POST'])
def validate_applicant():
    data = request.json
    try:
        birthdate = datetime.strptime(data['birthdate'], '%Y-%m-%d')
    except ValueError:
        return jsonify({'message': 'Invalid birthdate format'}), 400
    return jsonify({'message': 'Valid'}), 200

@appWs.route('/validate_previous_insurance', methods=['POST'])
def validate_previous_insurance():
    data = request.json
    if data.get('no_claim_bonus') is not None:
        if data['no_claim_bonus'] < 0 or data['no_claim_bonus'] > 100:
            return jsonify({'message': 'No claim bonus must be between 0 and 100'}), 400
    return jsonify({'message': 'Valid'}), 200

if __name__ == '__main__':
    appWs.run(debug=True, port=5001)
