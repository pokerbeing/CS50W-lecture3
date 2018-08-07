import os

from sqlalchemy import create_engine
from sqlalchemy.orm import scoped_session, sessionmaker

engine = create_engine(os.getenv("DATABASE_URL"))
db = scoped_session(sessionmaker(bind=engine))

def main():
    while True:
        # List all flights.
        flights = db.execute("SELECT id, origin, destination, duration FROM flights").fetchall()
        for flight in flights:
            print(f"Flight {flight.id}: {flight.origin} to {flight.destination}, {flight.duration} minutes.")

        # Prompt user to choose a flight.
        flight_id = int(input("\nFlight ID: "))
        if flight_id == 999:
            break
        flight = db.execute("SELECT origin, destination, duration FROM flights WHERE id = :id",
                            {"id": flight_id}).fetchone()

        # Make sure flight is valid.
        if flight is None:
            print("Error: No such flight.")
            continue

        # List passengers.
        passengers = db.execute("SELECT name FROM passengers WHERE flight_id = :flight_id",
                                {"flight_id": flight_id}).fetchall()
        print("\nPassengers:")
        for passenger in passengers:
            print(passenger.name)
        print()
        if len(passengers) == 0:
            print("No passengers.\n")

if __name__ == "__main__":
    main()