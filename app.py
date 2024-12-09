from flask import Flask, render_template, request, jsonify
import folium
import json
from geopy.distance import geodesic
from flask_socketio import SocketIO, emit

app = Flask(__name__)
socketio = SocketIO(app)

# Mock user data and global lock
with open("data/users.json") as f:
    users = json.load(f)

lock = {"is_locked": False, "accepted_by": None, "accepted_role": None}

# Alert and responder data
alerts = [
    {"location": [12.972442, 77.580643], "severity": "Minor", "details": "MG Road"},
    {"location": [12.975557, 77.592731], "severity": "Severe", "details": "Cubbon Park"}
]

ambulances = [
    {"location": [12.9611159, 77.638732], "id": "Ambulance 1"},
    {"location": [12.981654, 77.594679], "id": "Ambulance 2"},
    {"location": [12.965925, 77.610116], "id": "Ambulance 3"},
    {"location": [12.945665, 77.601267], "id": "Ambulance 4"},
]

@app.route("/")
def login():
    return render_template("login.html")

@app.route("/dashboard", methods=["POST"])
def dashboard():
    role = request.form.get("role")
    username = request.form.get("username")
    password = request.form.get("password")

    if role in users and users[role]["username"] == username and users[role]["password"] == password:
        # Initialize map
        folium_map = folium.Map(location=[12.9716, 77.5946], zoom_start=13)

        # Add accident markers
        for alert in alerts:
            color = "orange" if alert["severity"] == "Minor" else "red"
            folium.Marker(
                alert["location"],
                tooltip=f"Accident - {alert['severity']}",
                popup=f"<b>Severity:</b> {alert['severity']}<br><b>Location:</b> {alert['details']}",
                icon=folium.Icon(color=color)
            ).add_to(folium_map)

        # Add ambulance markers
        for ambulance in ambulances:
            folium.Marker(
                ambulance["location"],
                tooltip=f"{ambulance['id']} - Starting Point",
                popup=f"{ambulance['id']} Dispatch Location",
                icon=folium.Icon(color="blue", icon="ambulance", prefix="fa")
            ).add_to(folium_map)

        # Generate map HTML
        map_html = folium_map._repr_html_()
        return render_template("dashboard.html", role=role, map_html=map_html)
    else:
        return "Invalid login credentials", 401


@app.route("/respond", methods=["POST", "GET"])
def respond():
    """
    Handles response from any responder role and broadcasts real-time updates.
    """
    if request.method == "GET":
        return render_template(
            "respond.html",
            responder_role=None,
            response=None,
            message="Waiting for responder input",
        )

    responder_role = request.form.get("responder_role")
    response = request.form.get("response")

    if not responder_role:
        return jsonify({"message": "Responder role is required"}), 400

    if response == "accept":
        if not lock["is_locked"]:
            # Update lock to mark the request as accepted
            lock["is_locked"] = True
            lock["accepted_by"] = responder_role
            lock["accepted_role"] = responder_role

            # Emit acceptance update to all connected clients
            socketio.emit(
                "response_update",
                {"responder": responder_role, "response": "accepted"},
                to="/",  # Broadcast to all clients
            )

            return jsonify({"message": f"Request accepted by {responder_role}"}), 200
        else:
            return jsonify(
                {
                    "message": f"Request already accepted by {lock['accepted_by']} ({lock['accepted_role']})"
                }
            ), 403

    elif response == "reject":
        # Emit rejection update to all connected clients
        socketio.emit(
            "response_update",
            {"responder": responder_role, "response": "rejected"},
            to="/",  # Broadcast to all clients
        )
        return jsonify({"message": f"Request declined by {responder_role}"}), 200

    return jsonify({"message": "Invalid response"}), 400

    

@socketio.on("connect")
def handle_connect():
    """
    Handles a new client connection.
    """
    print("Client connected")

@socketio.on("disconnect")
def handle_disconnect():
    """
    Handles client disconnection.
    """
    print("Client disconnected")

if __name__ == "__main__":
    socketio.run(app, debug=True)
