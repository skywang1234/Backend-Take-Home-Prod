from flask import Flask, jsonify, request
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import select, func
from datetime import datetime
import requests

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///workouts.db'

db = SQLAlchemy(app)

class Workout(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    routeName = db.Column(db.String(80), unique=True, nullable=False)
    description = db.Column(db.String(150), nullable=False)

    date = db.Column(db.DateTime, default=datetime.now())
    distance = db.Column(db.Float)
    duration = db.Column(db.Float)
    heartRate = db.Column(db.Integer)

    weather = db.Column(db.String(150))
    image = db.Column(db.LargeBinary)

    def __repr__(self):
        return f"{self.routeName} - {self.description}"
    
    def to_Json(self):
        return {
            "id": self.id,
            "routeName": self.routeName,
            "description": self.description,
            "date": self.date.strftime('%Y-%m-%d'),
            "distance": self.distance,
            "duration": self.duration,
            "heartRate": self.heartRate,
            "weather": self.weather,
            "image": self.image.decode('utf-8') if self.image else None,
        }

@app.route('/')
def index():
    return 'Welcome to the Workouts Tracker API'

def get_weather(api_key, city):
    url = f"http://api.openweathermap.org/data/2.5/weather?q={city}&appid={api_key}&units=metric"

    try:
        response = requests.get(url)
        response.raise_for_status()
        data = response.json()
        weather_description = data['weather'][0]['description']
        temperature = data['main']['temp']
        return f"{weather_description}, {temperature}°C"
    except requests.RequestException as e:
        print("Failed to fetch weather data")

@app.route('/workouts', methods=['POST'])   
def add_workout():
    routeName = request.json.get('routeName')
    description = request.json.get('description')
    distance = request.json.get('distance')
    duration = request.json.get('duration')
    heartRate = request.json.get('heartRate')

    if not routeName or not description:
        return jsonify({'error': 'Name or Description must be provided'}), 400

    api_key = "2b45f5be9acc8615953d62cb45ff8114"
    city = "Cary"
    weather = get_weather(api_key, city)

    image = request.json.get('image')
    imageBinary = image.encode('utf-8') if image else None

        
    workout = Workout(routeName=routeName, description=description,
        distance=distance, duration=duration, heartRate=heartRate, weather=weather, image=imageBinary)

    db.session.add(workout)
    db.session.commit()
    return jsonify({'message': 'Workout added successfully'}), 200

@app.route('/workouts', methods=['GET'])
def get_filtered_workouts():
    workoutsQuery = Workout.query
    routeName = request.args.get('route_name')
    startDate = request.args.get('start_date')
    endDate = request.args.get('end_date')
    minDist = request.args.get('min_distance')
    maxDist = request.args.get('max_distance')

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
    return jsonify([workout.to_Json() for workout in workouts])

@app.route('/workouts/aggregate', methods=['GET'])
def get_aggregate_data():
    startDate = request.args.get('start_date')
    endDate = request.args.get('end_date')

    workoutsQuery = db.session.query(
        func.sum(Workout.distance).label('totalDist'),
        func.avg(Workout.heartRate).label('avgHeartRate'),
        func.avg(Workout.duration).label('avgDuration'),
        func.count(Workout.id).label('totalWorkouts')
    )

    if startDate:
        workoutsQuery = workoutsQuery.filter(Workout.date >= datetime.strptime(startDate, '%Y-%m-%d').date())
    if endDate:
        workoutsQuery = workoutsQuery.filter(Workout.date <= datetime.strptime(endDate, '%Y-%m-%d').date())

    results = workoutsQuery.one()

    aggregateData = {
        'totalDist': results.totalDist if results.totalDist else 0,
        'avgHeartRate': results.avgHeartRate if results.avgHeartRate else 0,
        'avgDuration': results.avgDuration if results.avgDuration else 0,
        'totalWorkouts': results.totalWorkouts if results.totalWorkouts else 0,
    }

    return jsonify(aggregateData), 200

@app.route('/reset')
def reset():
    db.drop_all()
    db.create_all()
    return jsonify({'message': 'Database successfully reset'}), 200

if __name__ == '__main__':
    app.run(debug=True) #remove debug=True