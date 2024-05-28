from sklearn.neural_network import MLPRegressor
from sklearn.preprocessing import StandardScaler
from sklearn.metrics import mean_squared_error
from sklearn.model_selection import train_test_split
import numpy as np
import csv
import os.path


from ClassData import ClassData

part_of_file_path = 'data.csv'

class Chatbot:
    def __init__(self):
        self.model = MLPRegressor(hidden_layer_sizes=(100,), activation='relu', solver='adam', max_iter=1000, random_state=42)
        self.scaler = StandardScaler()
        self.is_fitted = False
        self.classes = []
        
    def load(self, course_name):
        self.classes = []  
        file_path = course_name + '_' + part_of_file_path
        try:
            with open(file_path, newline='') as csvfile:
                reader = csv.DictReader(csvfile)
                for row in reader:
                    self.classes.append(ClassData(
                        float(row['difficulty']),
                        float(row['current_grade']),
                        float(row['study_hours'])
                    ))
        except:
            raise Exception(f"{course_name} has no data.")
            
    def add_data(self, course_name, study_data):
        file_path = course_name + '_' + part_of_file_path
        
        if not os.path.isfile(file_path):
            f = open(file_path, "w")
            f.write("difficulty,current_grade,study_hours\n")
            f.close()
            
        f = open(file_path, "a")
        f.write(f"{study_data.difficulty},{study_data.current_grade},{study_data.study_hours}\n")
        f.close()
        return 
            
        
    def update_model(self):
        X = np.array([[data.difficulty, data.current_grade] for data in self.classes]) 
        y = np.array([data.study_hours for data in self.classes])

        # Create the MLPRegressor model
        self.mlp = MLPRegressor(hidden_layer_sizes=(100,), activation='relu', solver='adam', max_iter=500, random_state=42)

        # Train the model
        self.mlp.fit(X, y)

    def get_study_hours_recommendations(self, difficulty):
        #given their assesment of difficulty, est
        X_input = np.array([[difficulty, 100.0]])
        y_pred = self.mlp.predict(X_input)
        
        rounded_hours = np.round(y_pred * 2) / 2  # Round to nearest half hour
        
        return float(rounded_hours[0])
    
    def calculate_error(self):
        X = np.array([[data.difficulty, data.current_grade] for data in self.classes]) 
        y = np.array([data.study_hours for data in self.classes])
        # Split the data into training and test sets
        X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)

        # Create the MLPRegressor model
        self.mlp = MLPRegressor(hidden_layer_sizes=(100,), activation='relu', solver='adam', max_iter=500, random_state=42)

        # Train the model
        self.mlp.fit(X_train, y_train)

        # Make predictions
        y_pred = self.mlp.predict(X_test)

        # Evaluate the model
        mse = mean_squared_error(y_test, y_pred)
        #print(f'Mean Squared Error: {mse}')
        return mse
    