from flask import Flask, request, jsonify
from flask_cors import CORS
# from datetime import datetime
# import re
# import pytz

app = Flask(__name__)
# pst = pytz.timezone('America/Los_Angeles')
CORS(app, origins="http://localhost:5173")

@app.route('/recommended_study_hours', methods=['POST'])
def collect_schedule():
    data = request.json
    print(data)
    
    result = dict()
    result["hours"] = 5
    return jsonify(result)

if __name__ == '__main__':
    app.run(debug=True)
