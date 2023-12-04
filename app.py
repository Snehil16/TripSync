from flask import Flask, render_template, jsonify, request, session, redirect, flash
from pymongo import MongoClient
import bcrypt


# Establishing connection to the MongoDB database
uri = "mongodb+srv://tempuser:aryamaan@cluster0.10enjsp.mongodb.net/?retryWrites=true&w=majority"
client = MongoClient(uri)
db = client.get_database("TripSync")
user_details = db.get_collection("UserDetails")
trips = db.get_collection("Trips")
trip_details = db.get_collection("TripDetails")

app = Flask(__name__)
app.config['SECRET_KEY'] = 'aryamaan'  # For testing purposes only


## HTML
@app.route('/')
@app.route('/home')
def home():
    return render_template('home.html')

# Route to display mainpage
@app.route('/mainpage')
def mainpage():
    return render_template('mainpage.html')

# Route to display the signup form
@app.route('/signup', methods=['GET'])
def show_signup_form():
    return render_template('signup.html')

# POST API to create a user
@app.route('/signup', methods=['POST'])
def signup():
    # Ensure that the form field names match the ones in the HTML form
    name = request.form['name']
    email = request.form['email']
    password = request.form['password']

    # Check if the email already exists in the database
    signup_user = user_details.find_one({'email': email})
    if signup_user:
        flash('Email address already exists')
        return redirect('/signup')

    # Hash the password before storing it
    hashed_password = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt())
    hashed_password_str = hashed_password.decode('utf-8')
    # Store user data in the database
    user_details.insert_one({'name': name, 'email': email, 'password': hashed_password_str})

    # Redirect to the sign-in page upon successful signup
    return redirect('/signin')


#Route to display the signin form
@app.route('/signin', methods=['GET'])
def show_signin_form():
    return render_template('signin.html')

# Sign-in route handling
@app.route('/signin', methods=['POST'])
def signin():
    signin_user = user_details.find_one({'email': request.form['email']})
    if signin:
        if bcrypt.hashpw(request.form['password'].encode('utf-8'), signin_user['password'].encode('utf-8')) == \
                    signin_user['password'].encode('utf-8'):
            session['email'] = request.form['email']
            return redirect('/home')
    flash('Invalid email/password')
    return redirect('/signin')

@app.route('/logout')
def logout():
    session.pop('email', None)
    return redirect('/home')

# Route to display the home page
@app.route('/home', methods=['GET'])
def show_home_page():
    return render_template('home.html')

# Route to display the create trip form
@app.route('/tripnew', methods=['GET'])
def show_create_trip_form():
    return render_template('tripnew.html')

# POST API to create a trip
@app.route('/trip', methods=['POST'])
def create_trip():
    print(request.form)
    # Extracting trip details from the POST request
    name = request.form['name']  # Extract name from form
    email = request.form['email']  # Extract email from form
    phone = request.form['phone'] # Extract phone from form
    pickup_location = request.form['pickup_location']  # Extract pickup_location from form
    destination = request.form['destination']  # Extract destination from form
    pickup_date = request.form['pickup_date']  # Extract pickup_date from form
    num_people = request.form['num_people']  # Extract num_people from form
    amount = request.form['amount']  # Extract amount from form

    # Create a dictionary with extracted data
    trip_data = {
        'name': name,
        'email': email,
        'phone': phone,
        'pickup_location': pickup_location,
        'destination': destination,
        'pickup_date': pickup_date,
        'num_people': num_people,
        'amount': amount
    }

    inserted_trip = trips.insert_one(trip_data)

    trip_id = inserted_trip.inserted_id

    # Get the user ID of the trip owner (You may need to obtain this from the session or authentication)
    user_email = session['email']  # Replace this with your method to retrieve the user ID

    # Get the user ID of the trip owner
    user = user_details.find_one({'email': user_email})
    user_id = user['_id']

    trip = trip_details.find_one({'trip_id': trip_id})
    if trip:
        # If the trip exists, update the user_ids and count
        user_ids = trip.get('user_ids', [])
        if user_id not in user_ids:
            user_ids.append(user_id)
        count = len(user_ids)

        # Update the TripDetails collection with the new user_ids and count
        trip_details.update_one(
            {'trip_id': str(trip_id)},
            {'$set': {'user_ids': str(user_ids), 'count': count}}
        )
    else:
        # If the trip doesn't exist, create a new entry in TripDetails
        trip_details.insert_one({'trip_id': trip_id, 'user_ids': [user_id], 'count': 1})

    return redirect('/home')


# home page displays all the trips
@app.route('/tripDetails')
def show_trip_details():
    formatted_trips = []

    # Fetch all trips from the 'Trips' collection
    trips_data = list(trips.find({}))

    for trip in trips_data:
        trip_id = str(trip['_id'])

        # Fetch corresponding trip details from TripDetails collection
        trip_details_data = trip_details.find_one({'trip_id': trip_id})
        print(f"Trip Details Data: {trip_details_data}")
        if trip_details_data:
            count = trip_details_data.get('count', 0)
            print(f"Trip ID: {trip_id}, Count: {count}")
        else:
            count = 0

        formatted_trip = {
            'trip_id': str(trip_id),
            'destination': trip['destination'],
            'num_people_joined': count,  # Use the count attribute for displaying people joined
        }
        formatted_trips.append(formatted_trip)

    return jsonify({'trips': formatted_trips})


# GET API to display join trip form
@app.route('/joinTrip', methods=['GET'])
def show_join_trip_form():
    return render_template('joinTrip.html')

# POST API to add user to a trip
@app.route('/trip/add_user', methods=['POST'])
def add_user_to_trip():
    trip_id = request.form['trip_id']
    user_id = request.form['user_id']

    # Find the trip in TripDetails collection
    trip = trip_details.find_one({'trip_id': trip_id})
    if trip:
        # Get the existing user IDs and count
        user_ids = trip.get('user_ids', [])
        count = trip.get('count', 0)

        # Check if the user_id is already in the user_ids list
        if user_id not in user_ids:
            # Append the user_id to user_ids list
            user_ids.append(user_id)
            count = len(user_ids)  # Update the count

            # Update TripDetails with the new user_ids and count
            trip_details.update_one(
                {'trip_id': str(trip_id)},
                {'$set': {'user_ids': str(user_ids), 'count': count}}
            )

            # Increment the count of people joined in the Trips collection
            trips.update_one(
                {'_id': str(trip_id)},
                {'$inc': {'num_people_joined': 1}}
            )

            return jsonify({'result': 'success'})
        else:
            return jsonify({'result': 'User already joined this trip'})
    else:
        # If the trip doesn't exist, create a new entry in TripDetails
        trip_details.insert_one({'trip_id': trip_id, 'user_ids': [user_id], 'count': 1})

        # Increment the count of people joined in the Trips collection
        trips.update_one(
            {'_id': str(trip_id)},
            {'$inc': {'num_people_joined': 1}}
        )

        return jsonify({'result': 'success'})


# GET API to retrieve trip details for a specific user
@app.route('/userTrips', methods=['GET'])
def get_user_trips():
    # Get the user ID using the method get_user_id()
    user_id = get_user_id()
    user_trip_details = list(trip_details.find({'user_id': user_id}))
    return jsonify({'result': 'success', 'user_trip_details': user_trip_details})

@app.route('/getUserId', methods=['GET'])
def get_user_id():
    # Fetch user ID based on the logged-in user's session or authentication
    user_email = session['email']  # Replace 'email' with the session key used for the user's email

    # Query the database to get the user ID based on the email
    user = user_details.find_one({'email': user_email})

    if user:
        user_id = str(user['_id'])  # Assuming user['_id'] is an ObjectId, converting it to string
        return jsonify({'user_id': user_id})
    else:
        return jsonify({'error': 'User not found'}), 404  # Return an error if user not found

if __name__ == '__main__':
    app.run('0.0.0.0', port=5000, debug=True)
