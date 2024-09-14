from flask import Flask, jsonify, request
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import select, func
from datetime import datetime
import requests

# Initialize the Flask application
app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///workouts.db'

db = SQLAlchemy(app)

# Define the Workout model
class Workout(db.Model):
    id = db.Column(db.Integer, primary_key=True)  # Unique ID for each workout
    routeName = db.Column(db.String(80), unique=True, nullable=False)  # Name of the workout route, must be unique
    description = db.Column(db.String(150), nullable=False)  # Description of the workout
    date = db.Column(db.DateTime, default=datetime.now())  # Date of the workout, default is the current time
    distance = db.Column(db.Float)  # Distance covered in the workout in km
    duration = db.Column(db.Float)  # Duration of the workout in min
    heartRate = db.Column(db.Integer)  # Average heart rate during the workout
    weather = db.Column(db.String(150))  # Weather description during the workout
    image = db.Column(db.LargeBinary)  # Image associated with the workout (stored as binary)

    # String representation of the Workout object
    def __repr__(self):
        return f"{self.routeName} - {self.description}"
    
    # Convert the Workout object to JSON format
    def to_Json(self):
        return {
            "id": self.id,
            "routeName": self.routeName,
            "description": self.description,
            "date": self.date.strftime('%Y-%m-%d'),  # Format the date as a string
            "distance": self.distance,
            "duration": self.duration,
            "heartRate": self.heartRate,
            "weather": self.weather,
            "image": self.image.decode('utf-8') if self.image else None,  # Decode image to UTF-8 if present
        }

# Basic route to test the API
@app.route('/')
def index():
    return 'Welcome to the Workouts Tracker API'

# Function to get weather information using OpenWeatherMap API
def get_weather(api_key, city):
    # Construct the URL for the API request
    url = f"http://api.openweathermap.org/data/2.5/weather?q={city}&appid={api_key}&units=metric"

    try:
        response = requests.get(url)  # Make the API request
        response.raise_for_status()
        data = response.json()
        weather_description = data['weather'][0]['description']  # Extract weather description
        temperature = data['main']['temp']  # Extract temperature
        return f"{weather_description}, {temperature}°C"  # Return formatted weather info
    except requests.RequestException as e:
        print("Failed to fetch weather data")  # Print error message if request fails

# Route to add a new workout to the database
@app.route('/workouts', methods=['POST'])   
def add_workout():
    # Extract data from the request JSON
    routeName = request.json.get('routeName')
    description = request.json.get('description')
    distance = request.json.get('distance')
    duration = request.json.get('duration')
    heartRate = request.json.get('heartRate')

    # Check if routeName or description is missing
    if not routeName or not description:
        return jsonify({'error': 'Name or Description must be provided'}), 400

    # Fetch weather data for the given city
    api_key = "2b45f5be9acc8615953d62cb45ff8114"
    city = "Cary"
    weather = get_weather(api_key, city)

    # Get image data and encode it
    image = request.json.get('image')
    imageBinary = image.encode('utf-8') if image else None

    # Create a new Workout object with the provided data
    workout = Workout(routeName=routeName, description=description,
        distance=distance, duration=duration, heartRate=heartRate, weather=weather, image=imageBinary)

    db.session.add(workout)  # Add the workout
    db.session.commit()
    return jsonify({'message': 'Workout added successfully'}), 200

# Route to retrieve workouts with optional filtering
@app.route('/workouts', methods=['GET'])
def get_filtered_workouts():
    workoutsQuery = Workout.query  # Initialize the query
    routeName = request.args.get('route_name')  # Get filter parameters from request
    startDate = request.args.get('start_date')
    endDate = request.args.get('end_date')
    minDist = request.args.get('min_distance')
    maxDist = request.args.get('max_distance')

    # Apply filters to the query if parameters are provided
    if routeName:
        workoutsQuery = workoutsQuery.filter(func.lower(Workout.routeName) == routeName.lower())
    if startDate:
        workoutsQuery = workoutsQuery.filter(Workout.date >= datetime.strptime(startDate, '%Y-%m-%d').date())
    if endDate:
        workoutsQuery = workoutsQuery.filter(Workout.date <= datetime.strptime(endDate, '%Y-%m-%d').date())
    if minDist:
        workoutsQuery = workoutsQuery.filter(Workout.distance >= float(minDist))
    if maxDist:
        workoutsQuery = workoutsQuery.filter(Workout.distance <= float(maxDist))

    workouts = workoutsQuery.all()
    return jsonify([workout.to_Json() for workout in workouts])  # Return the results as JSON

# Route to get aggregated workout data
@app.route('/workouts/aggregate', methods=['GET'])
def get_aggregate_data():
    startDate = request.args.get('start_date')  # Get filter parameters from request
    endDate = request.args.get('end_date')

    # Aggregate query to calculate total distance, average heart rate, average duration, and total count of workouts
    workoutsQuery = db.session.query(
        func.sum(Workout.distance).label('totalDist'),
        func.avg(Workout.heartRate).label('avgHeartRate'),
        func.avg(Workout.duration).label('avgDuration'),
        func.count(Workout.id).label('totalWorkouts')
    )

    # Apply date filters to the query if parameters are provided
    if startDate:
        workoutsQuery = workoutsQuery.filter(Workout.date >= datetime.strptime(startDate, '%Y-%m-%d').date())
    if endDate:
        workoutsQuery = workoutsQuery.filter(Workout.date <= datetime.strptime(endDate, '%Y-%m-%d').date())

    results = workoutsQuery.one()  # Execute the query and fetch the result

    # Prepare aggregated data in a dictionary
    aggregateData = {
        'totalDist': results.totalDist if results.totalDist else 0,
        'avgHeartRate': results.avgHeartRate if results.avgHeartRate else 0,
        'avgDuration': results.avgDuration if results.avgDuration else 0,
        'totalWorkouts': results.totalWorkouts if results.totalWorkouts else 0,
    }

    return jsonify(aggregateData), 200  # Return aggregated data as JSON

# Route to reset the database by dropping all tables and recreating them
@app.route('/reset')
def reset():
    db.drop_all()
    db.create_all()
    return jsonify({'message': 'Database successfully reset'}), 200

# Run the Flask app
if __name__ == '__main__':
    app.run(debug=True)  # Run the app in debug mode (remove debug=True in production)
