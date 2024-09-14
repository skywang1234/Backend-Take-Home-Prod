
# Workout Tracker API

This API allows users to manage workout records, including the ability to add, retrieve, update, and delete workouts. It also provides aggregated data and the ability to reset the database.

## Major Design Decisions
- **Choice of Language:** Originally, I planned to use Python's TensorFlow library to implement computer vision to "read" workout images, but due to time constraints, I decided to scrap the idea. I have working proficiency with Node and Java.
- **Use of Generative AI:** I utilized ChatGPT to write comments, handle errors, and write the documentation for my API. This was mainly due to time constraints in combination with my other responsibilities. The code itself is not AI-generated.
- **Use of Query:** According to SQLAlchemy's documentation, the use of the query interface is legacy and has been replaced with 'session.execute(select())'. I chose to stick with the query interface simply because it was easier. However, I believe it also demonstrates my ability to work with legacy codebases 😉.
- **Image Handling:** I chose Base64 encoding for image handling because it retains the image data, allowing the image to be accessible on multiple devices as opposed to saving the image and its path locally. Obviously, this severely limits the size of the images that can be saved; however, it is a heuristic solution.

## Minor Design Decisions
- **Read-only Values:** Some values, like date and weather, cannot be updated or set and are automatically filled with current date/time and weather values. This is because I wanted this API to be a workout tracker, and removing some flexibility prevents beginners from "cheesing" their workouts 😆.
- **Lack of Fuzzy String Matching:** I considered utilizing fuzzy string matching when searching for the Route Name; however, I decided against it due to time constraints and the fact that, in my experience, most people name their runs with similar names every time.

## Choice of Tools
- **Flask:** A Python micro-framework ideal for small to medium-sized web applications and APIs.
- **SQLAlchemy:** A Python SQL toolkit and Object-Relational Mapping (ORM) library that provides a full suite of well-known enterprise-level persistence patterns.
- **OpenWeatherMap API:** Provides current weather data which is useful for context in workout records.
- **SQLite:** A simple and lightweight database that is integrated with Flask, suitable for development and small-scale production.

## Running the API
1. **Clone the Repository:**
   ```bash
   git clone <repository-url>
   ```
2. **Navigate to the Project Directory:**
   ```bash
   cd workout-tracker-api
   ```
3. **Create a Virtual Environment:**
   ```bash
   python -m venv venv
   ```
4. **Activate the Virtual Environment:**
   - On Windows:
     ```bash
     venv\Scripts\activate
     ```
   - On macOS/Linux:
     ```bash
     source venv/bin/activate
     ```
5. **Install the Dependencies:**
   ```bash
   pip install -r requirements.txt
   ```
6. **Set Up the Database:**
   - Initialize the database by running:
     ```bash
     flask shell
     >>> from app import db
     >>> db.create_all()
     >>> exit()
     ```
7. **Run the Application:**
   ```bash
   python app.py
   ```
   The API will be available at `http://localhost:5000`.

## Testing the API
- **Manual Testing:** Use tools like Postman or cURL to manually send requests to the API and verify responses.
- **Automated Testing:** Implement unit tests using a testing framework like `pytest` to automate the validation of API functionality.

## Environment Variables
- The application uses OpenWeatherMap API for fetching weather data. Set your API key as an environment variable named `OPENWEATHER_API_KEY`.

```bash
export OPENWEATHER_API_KEY='your_openweathermap_api_key'
```

---

## API Documentation

### Base URL
```
http://localhost:5000
```

### 1. Get All Workouts
- **Endpoint:** `/workouts`
- **Method:** `GET`
- **Description:** Retrieves a list of workouts with optional filtering based on route name, start date, end date, minimum distance, and maximum distance.
- **Parameters:**
  - `route_name` (optional): Filter workouts by route name (string).
  - `start_date` (optional): Filter workouts that occurred on or after this date (format: `YYYY-MM-DD`).
  - `end_date` (optional): Filter workouts that occurred on or before this date (format: `YYYY-MM-DD`).
  - `min_distance` (optional): Filter workouts with a minimum distance (float).
  - `max_distance` (optional): Filter workouts with a maximum distance (float).
- **Response:**
  - `200 OK`: Returns a list of workouts in JSON format.
  - Example:
    ```json
    [
      {
        "id": 1,
        "routeName": "Morning Run",
        "description": "Easy morning jog",
        "date": "2024-09-14",
        "distance": 5.0,
        "duration": 30,
        "heartRate": 120,
        "weather": "clear sky, 20°C",
        "image": null
      }
    ]
    ```

### 2. Add a New Workout
- **Endpoint:** `/workouts`
- **Method:** `POST`
- **Description:** Adds a new workout to the database.
- **Request Body:**
  - `routeName` (string, required): Name of the workout route.
  - `description` (string, required): Description of the workout.
  - `distance` (float, optional): Distance covered in kilometers.
  - `duration` (float, optional): Duration of the workout in minutes.
  - `heartRate` (integer, optional): Average heart rate during the workout.
  - `image` (string, optional): Base64 encoded image data associated with the workout.
- **Response:**
  - `200 OK`: Returns a success message.
  - Example:
    ```json
    {
      "message": "Workout added successfully"
    }
    ```
  - `400 Bad Request`: If `routeName` or `description` is missing.
  - Example:
    ```json
    {
      "error": "Name or Description must be provided"
    }
    ```

### 3. Update a Workout
- **Endpoint:** `/workouts/<id>`
- **Method:** `PUT`
- **Description:** Updates the details of a workout with the specified ID.
- **Parameters:**
  - `id` (integer, required): The ID of the workout to update.
- **Request Body:** (All fields are optional)
  - `routeName` (string): Name of the workout route.
  - `description` (string): Description of the workout.
  - `distance` (float): Distance covered in kilometers.
  - `duration` (float): Duration of the workout in minutes.
  - `heartRate` (integer): Average heart rate during the workout.
  - `weather` (string): Weather description during the workout.
  - `image` (string): Base64 encoded image data associated with the workout.
- **Response:**
  - `200 OK`: Returns a success message.
  - Example:
    ```json
    {
      "message": "Workout updated"
    }
    ```
  - `404 Not Found`: If the workout with the specified ID is not found.
  - Example:
    ```json
    {
      "error": "Workout not found"
    }
    ```

### 4. Delete a Workout
- **Endpoint:** `/workouts/<id>`
- **Method:** `DELETE`
- **Description:** Deletes a workout with the specified ID.
- **Parameters:**
  - `id` (integer, required): The ID of the workout to delete.
- **Response:**
  - `200 OK`: Returns a success message.
  - Example:
    ```json
    {
      "message": "Workout deleted"
    }
    ```
  - `404 Not Found`: If the workout with the specified ID is not found.
  - Example:
    ```json
    {
      "error": "Workout not found"
    }
    ```

### 5. Get Aggregated Workout Data
- **Endpoint:** `/workouts/aggregate`
- **Method:** `GET`
- **Description:** Retrieves aggregated workout data including total distance, average heart rate, average duration, and total count of workouts.
- **Parameters:**
  - `start_date` (optional): Filter workouts that occurred on or after this date (format: `YYYY-MM-DD`).
  - `end_date` (optional): Filter workouts that occurred on or before this date (format: `YYYY-MM-DD`).
- **Response:**
  - `200 OK`: Returns aggregated data in JSON format.
  - Example:
    ```json
    {
      "totalDist": 100.0,
      "avgHeartRate": 130,
      "avgDuration": 45,
      "totalWorkouts": 10
    }
    ```

### 6. Reset Database
- **Endpoint:** `/reset`
- **Method:** `GET`
- **Description:** Resets the database by dropping all tables and recreating them.
- **Response:**
  - `200 OK`: Returns a success message.
  - Example:
    ```json
    {
      "message": "Database successfully reset"
    }
    ```
