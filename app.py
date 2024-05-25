import csv
from flask import Flask, request, jsonify
from flask_cors import CORS
from sklearn.neural_network import MLPRegressor
from sklearn.preprocessing import StandardScaler
import nltk
import logging
import joblib
import os

nltk.download('punkt')
nltk.download('averaged_perceptron_tagger')

app = Flask(__name__)
CORS(app, origins=["http://localhost:5173"])

logging.basicConfig(level=logging.INFO)

class ClassData:
    def __init__(self, credits, difficulty, current_grade, study_hours):
        self.credits = credits
        self.difficulty = difficulty
        self.current_grade = current_grade
        self.study_hours = study_hours
        self.recommended_hours = 0  

class Chatbot:
    def __init__(self):
        self.model = MLPRegressor(hidden_layer_sizes=(100,), activation='relu', solver='adam', max_iter=1000, random_state=42)
        self.scaler = StandardScaler()
        self.is_fitted = False
        self.classes = []
    
    def read_csv(self, file_path):
        self.classes = []  
        with open(file_path, newline='') as csvfile:
            reader = csv.DictReader(csvfile)
            for row in reader:
                self.classes.append(ClassData(
                    float(row['credits']),
                    float(row['difficulty']),
                    float(row['current_grade']),
                    float(row['study_hours'])
                ))

    def update_model(self):
        X = [[data.credits, data.difficulty, data.current_grade] for data in self.classes]
        y = [data.study_hours for data in self.classes]
        self.scaler.fit(X)  
        X_scaled = self.scaler.transform(X)
        self.model.fit(X_scaled, y)
        self.is_fitted = True

    def get_study_hours_recommendations(self, data):
        if not self.is_fitted:
            raise Exception("Model is not fitted. Please add some class data first!")
        
        input_features = self.scaler.transform([[data.credits, data.difficulty, data.current_grade]])
        data.recommended_hours = self.model.predict(input_features)[0]
        grade_gap = 100 - data.current_grade
        difficulty_factor = data.difficulty / 10
        additional_hours = grade_gap * 0.5 * difficulty_factor
        recommended_hours = max(data.recommended_hours + additional_hours, data.study_hours + 1)
        rounded_hours = round(recommended_hours * 2) / 2

        return rounded_hours

chatbot = Chatbot()
file_path = 'data.csv'

@app.route('/recommended_study_hours', methods=['POST'])
def recommended_study_hours():
    global chatbot, file_path
    data = request.json

    if not isinstance(data, list):
        return jsonify({"error": "Input data should be a list of courses!"}), 400

    recommended_hours_list = []

    for course in data:
        course_name = course.get('course_ID')
        credits = course.get('credits')
        difficulty = course.get('difficulty_level')
        current_grade = course.get('current_grade')
        study_hours = course.get('actual_study_hours')

        if not all([course_name, credits, difficulty, current_grade, study_hours]):
            return jsonify({"error": "Missing or invalid data fields for course: {}".format(course_name)}), 400

        temp_data = ClassData(credits, difficulty, current_grade, study_hours)
        
        chatbot.read_csv(course_name + '_' + file_path)
        chatbot.update_model()
        
        try:
            temp_data.recommended_hours = chatbot.get_study_hours_recommendations(temp_data)
        except Exception as e:
            logging.error(f"Error in getting study hours recommendations for course {course_name}: {e}")
            return jsonify({"error": str(e)}), 500

        recommended_hours_list.append({
            "course_ID": course_name,
            "recommended_hours": temp_data.recommended_hours
        })

    return jsonify({"recommended_hours": recommended_hours_list})

if __name__ == '__main__':
    app.run(debug=True)
