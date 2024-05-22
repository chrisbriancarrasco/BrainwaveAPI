import csv
from flask import Flask, request, jsonify
from flask_cors import CORS
from sklearn.neural_network import MLPRegressor
from sklearn.preprocessing import StandardScaler
from datetime import datetime
from pytz import timezone
import nltk

# Download necessary NLTK data
nltk.download('punkt')
nltk.download('averaged_perceptron_tagger')

app = Flask(__name__)
CORS(app, origins="http://localhost:5173")

class Data:
    def __init__(self, course_name, credits, difficulty, current_grade, study_hours, recommended_hours=0):
        self.course_name = course_name
        self.credits = credits
        self.difficulty = difficulty
        self.current_grade = current_grade
        self.study_hours = study_hours
        self.recommended_hours = recommended_hours

def read_csv(file_path):
    data_list = []
    with open(file_path, newline='') as csvfile:
        reader = csv.DictReader(csvfile)
        for row in reader:
            data_list.append(Data(
                row['course_name'],
                float(row['credits']),
                float(row['difficulty']),
                float(row['current_grade']),
                float(row['study_hours'])
            ))
    return data_list

def write_csv(file_path, data_list):
    with open(file_path, 'w', newline='') as csvfile:
        fieldnames = ['course_name', 'credits', 'difficulty', 'current_grade', 'study_hours', 'recommended_hours']
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)

        writer.writeheader()
        for data in data_list:
            writer.writerow({
                'course_name': data.course_name,
                'credits': data.credits,
                'difficulty': data.difficulty,
                'current_grade': data.current_grade,
                'study_hours': data.study_hours,
                'recommended_hours': data.recommended_hours
            })

def train_model(data_list):
    X = [[d.credits, d.difficulty, d.current_grade] for d in data_list]
    y = [d.study_hours for d in data_list]

    scaler = StandardScaler()
    X_scaled = scaler.fit_transform(X)

    model = MLPRegressor(max_iter=1000)
    model.fit(X_scaled, y)
    
    return model, scaler

def get_study_hours_recommendations(model, scaler, credits, difficulty, current_grade, study_hours):
    input_features = scaler.transform([[credits, difficulty, current_grade]])
    recommended_hours = model.predict(input_features)[0]

    grade_gap = 100 - current_grade
    difficulty_factor = difficulty / 10
    additional_hours = grade_gap * 0.5 * difficulty_factor
    recommended_hours = max(recommended_hours + additional_hours, study_hours + 1)

    # Round off the recommended hours by half-hour intervals
    rounded_hours = round(recommended_hours * 2) / 2

    return rounded_hours

# Read data from CSV and train the model
file_path = 'class_data.csv'
data_list = read_csv(file_path)
model, scaler = train_model(data_list)
is_fitted = True

@app.route('/recommended_study_hours', methods=['POST'])
def recommended_study_hours():
    data = request.json
    course_name = data.get('course_ID')
    credits = data.get('credits')
    difficulty = data.get('difficulty_level')
    current_grade = data.get('current_grade')
    study_hours = data.get('actual_study_hours')

    if not is_fitted:
        return jsonify({"error": "Model is not fitted. Please add some class data first!"}), 500

    recommended_hours = get_study_hours_recommendations(model, scaler, credits, difficulty, current_grade, study_hours)
    
    # Update the data_list and write to CSV
    for d in data_list:
        if d.course_name == course_name:
            d.recommended_hours = recommended_hours
            break
    else:
        # If course not found, add it
        data_list.append(Data(course_name, credits, difficulty, current_grade, study_hours, recommended_hours))

    write_csv(file_path, data_list)
    
    return jsonify({"recommended_hours": recommended_hours})

if __name__ == '__main__':
    app.run(debug=True)
