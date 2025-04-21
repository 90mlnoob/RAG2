from flask import Flask, jsonify, request

app = Flask(__name__)

@app.route('/api/merchant/create', methods=['POST'])
def create_merchant():
    data = request.json
    return jsonify({"status": "success", "message": f"Merchant {data['name']} created."}), 201

@app.route('/api/merchant/update', methods=['PUT'])
def update_merchant():
    data = request.json
    return jsonify({"status": "success", "message": f"Merchant {data['merchant_id']} updated."})

@app.route('/api/merchant/<merchant_id>', methods=['GET'])
def get_merchant(merchant_id):
    return jsonify({"status": "success", "merchant_id": merchant_id, "name": "Merchant Name", "address": "Merchant Address"})

if __name__ == '__main__':
    app.run(debug=True, port=8123)
