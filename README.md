# Trip Sync Web Application

Trip Sync is a web application built using Flask, providing seamless travel planning and trip management features.

## Features

- **User Authentication:** Register, log in, and log out functionality for users.
- **Trip Creation:** Create and manage trips with details like pickup location, destination, date, etc.
- **View Trips:** View and manage existing trips, including trip details and options to edit or delete.
- **Responsive Design:** User-friendly interface compatible with various devices.

## Technologies Used

- **Flask:** Micro web framework for Python.
- **HTML/CSS:** Frontend development for the user interface.
- **Bootstrap:** Frontend framework for responsive design.
- **MongoDB:** Database management for storing user and trip data.

## Installation

1. Clone the repository:

    ```bash
    git clone https://github.com/yourusername/trip-sync.git
    cd trip-sync
    ```

2. Create a virtual environment:

    ```bash
    python -m venv venv
    source venv/bin/activate  # For Windows: venv\Scripts\activate
    ```

3. Install dependencies:

    ```bash
    pip install -r requirements.txt
    ```

4. Set up the database:

    ```bash
    flask db init
    flask db migrate
    flask db upgrade
    ```

5. Run the application:

    ```
    python/python3 app.py
    ```

The application will be running at `http://localhost:5000`.

## Usage

- Register an account or log in with existing credentials.
- Create a new trip by providing details such as pickup location, destination, date, etc.
- View and manage trips from the dashboard.
- Log out to end the session.
