import os

from flask import Flask, render_template, request
from sqlalchemy import create_engine
from sqlalchemy.orm import scoped_session, sessionmaker

app = Flask(__name__)

# This allows Python to communicate with the local PogreSQL server using
# Connection details included in the DATABASE_URL system variable.
# It's value is postgresql+psycopg2://postgres:michaele3@localhost/postgres
engine = create_engine(os.getenv("DATABASE_URL"))

#scoped_session allows multiple concurrent accesses by users to be independent.
db = scoped_session(sessionmaker(bind=engine))

# This route presents the index.html template which shows a selection dropdown
# list of all available flights for user to choose from
@app.route("/")
def index():
    # Puts rows from SQL query into a Python list named flights
    flights = db.execute("SELECT * FROM flights").fetchall()
    # Passes list of flights to index.html for display to dropdown list
    return render_template("index.html", flights=flights)

# This route is followed when user presses Book Flight button on index.html.
# It accepts the POST method from that form.
@app.route("/book", methods=["POST"])
def book():
    """Book a flight."""

    # Get form information. - First the name.
    name = request.form.get("name")
    try:
        # Then gets flight id
        flight_id = int(request.form.get("flight_id"))
    except ValueError:
        # if non-int flight_id entered then publish error.html with apppropriate error message
        return render_template("error.html", message="Invalid flight number.")

    # Make sure flight exists by looking up in table and check for 0 rowcount.
    if db.execute("SELECT * FROM flights WHERE id = :id", {"id": flight_id}).rowcount == 0:
        # If flight id not found, inform user.
        return render_template("error.html", message="No such flight with that id.")
    else:
        # Otherwise insert name into passenger table with reference to flight_id chosen
        # :name and :flight_id are placeholders during the SQL query
        db.execute("INSERT INTO passengers (name, flight_id) VALUES (:name, :flight_id)",
                # The placeholders are "filled-in" with Python variables using syntax below
                {"name": name, "flight_id": flight_id})
        # commits the transaction to the database, transaction is stored and database locked
        # until this is posted
        db.commit()
        # Publish success.html to let user know this posted
        return render_template("success.html")

# Route if user chooses /flights URL
@app.route("/flights")
def flights():
    """Lists all flights."""
    # Run SQL query to get all columns from flights table and store in Python list flights
    flights = db.execute("SELECT * FROM flights").fetchall()
    # When user lands on flights.html, publish list of flights there.
    return render_template("flights.html", flights=flights)

@app.route("/flights/<int:flight_id>")
def flight(flight_id):
    """Lists details about a single flight."""

    # Make sure flight exists.
    flight = db.execute("SELECT * FROM flights WHERE id = :id", {"id": flight_id}).fetchone()
    if flight is None:
        # Return error if it doesn't.
        return render_template("error.html", message="No such flight.")

    # Get all passengers on that particular flight and save to Python list passengers
    passengers = db.execute("SELECT name FROM passengers WHERE flight_id = :flight_id",
                            {"flight_id": flight_id}).fetchall()
    
    # Publish flight and passengers data to flight.html
    return render_template("flight.html", flight=flight, passengers=passengers)
