from flask import Flask, request, jsonify
from flask_cors import CORS
import logging
from ClassData import ClassData
from Chatbot import Chatbot

app = Flask(__name__)
CORS(app, origins=["http://localhost:5173"])

logging.basicConfig(level=logging.INFO)    

chatbot = Chatbot()


@app.route('/recommended_study_hours', methods=['POST'])
def recommended_study_hours():
    global chatbot
    data = request.json

    if not isinstance(data, list):
        return jsonify({"error": "Input data should be a list of courses!"}), 400

    recommended_hours_list = []

    for course in data:
        course_name = course.get('course_name')
        difficulty = course.get('difficulty_level')
        current_grade = course.get('current_grade')
        study_hours = course.get('actual_study_hours')

        if not all([course_name, difficulty, current_grade, study_hours]): 
            return jsonify({"error": "Missing or invalid data fields for course: {}".format(course_name)}), 400

        temp_data = ClassData(difficulty, current_grade, study_hours) 
        
        
        try:
            chatbot.load(course_name)
            chatbot.update_model()
            temp_data.recommended_hours = chatbot.get_study_hours_recommendations(temp_data)
        except Exception as e:
            logging.error(f"Error in getting study hours recommendations for course {course_name}: {e}")
            return jsonify({"error": str(e)}), 500

        recommended_hours_list.append({
            "course_name": course_name,
            "recommended_hours": temp_data.recommended_hours
        })

    return jsonify({"recommended_hours": recommended_hours_list})

@app.route('/evaluate_error', methods=['POST'])
def evaluate_error():
    global chatbot
    data = request.json

    if not isinstance(data, list):
        return jsonify({"error": "Input data should be a list of courses!"}), 400

    prediction_errors = dict()

    for course_name in data:
        try:
            chatbot.load(course_name)
            prediction_errors[course_name] = round(chatbot.calculate_error(), 3)
        except Exception as e:
            logging.error(f"{course_name} has no data.")
            return jsonify({"error": str(e)}), 500       
             
    return jsonify({"prediction_errors": prediction_errors})

@app.route('/add_course_data', methods=['POST'])
def add_course_data():
    global chatbot
    course = request.json

    course_name = course.get('course_name')
    difficulty = course.get('difficulty_level')
    current_grade = course.get('current_grade')
    study_hours = course.get('actual_study_hours')

    if not all([course_name, difficulty, current_grade, study_hours]): 
        return jsonify({"error": "Missing or invalid data fields for course: {}".format(course_name)}), 400

    temp_data = ClassData(difficulty, current_grade, study_hours) 
    chatbot.add_data(course_name, temp_data)
    
    return jsonify({"Messsage": "Data added."})


if __name__ == '__main__':
    app.run(debug=True)