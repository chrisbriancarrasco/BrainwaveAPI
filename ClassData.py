import re

class ClassData:
    def is_valid_difficulty(difficulty):
        return 1 <= difficulty <= 10
    
    def __init__(self, difficulty, current_grade, study_hours): 
        if not ClassData.is_valid_difficulty(difficulty):
            raise ValueError("Difficulty must be between 1 and 10.")
        if not self.is_valid_current_grade(current_grade):
            raise ValueError("Current grade must be between 0 and 100.")
        if not self.is_valid_study_hours(study_hours):
            raise ValueError("Study hours must be between 0 and 99.")
        
        self.difficulty = difficulty
        self.current_grade = current_grade
        self.study_hours = study_hours

    def is_valid_current_grade(self, current_grade):
        return 0 <= current_grade <= 100

    def is_valid_study_hours(self, study_hours):
        return 0 <= study_hours < 100

    def is_valid_course_name(course_name):
        pattern = r'^[A-Z]{1,4}[0-9]{1,3}[A-Za-z]?$'
        return bool(re.match(pattern, course_name))