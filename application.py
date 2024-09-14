from flask import Flask, jsonify, request
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import select, func
from datetime import datetime

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

    def __repr__(self):
        return f"{self.routeName} - {self.description}"
    
    def toJson(self):
        return {
            "id": self.id,
            "routeName": self.routeName,
            "description": self.description,
            "date": self.date.strftime('%Y-%m-%d'),
            "distance": self.distance,
            "duration": self.duration,
            "heartRate": self.heartRate,
        }

@app.route('/')
def index():
    return 'Welcome to the Workouts Tracker API'

@app.route('/workouts', methods=['POST'])   
def add_workout():
    workout = Workout(routeName=request.json['routeName'], description=request.json['description'])
    db.session.add(workout)
    db.session.commit()
    return "200"

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
    return jsonify([workout.toJson() for workout in workouts])

if __name__ == '__main__':
    app.run(debug=True) #remove debug=True