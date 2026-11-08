from flask import Flask, render_template, request, session
from flask_sqlalchemy import SQLAlchemy
from flask_cors import CORS
from flask_restful import Resource, Api, reqparse, fields, marshal_with, abort

from routing import closest_hub, init as init_routing
from Dataparse import parse_json_file

(g_id, g_name, g_zoom, g_center, nodes, pois, edges, trucks, hubs) = parse_json_file()

# Hand routing the map data
init_routing(nodes, edges, pois, hubs)
app = Flask(__name__, template_folder="frontEnd", static_folder="frontEnd")

app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///data.db'
db = SQLAlchemy(app)
api = Api(app)
@app.route("/")
def requestIndex():
    return render_template("frontEndUser.html")

@app.route("/management")
def managementIndex():
    return render_template("frontEndManagement.html")

requestFields = {
    'dest_name': fields.String,
    'dest_type': fields.String,
    'num_people': fields.Integer,
    'address': fields.String,
    'hot_food_needed': fields.Integer,
    'hot_food_available': fields.Integer,
    'cold_food_needed': fields.Integer,
    'cold_food_available': fields.Integer,
    'delivery_deadline': fields.Integer,
    'urgency_level': fields.Integer,
}


class Person(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String)
    location = db.Column(db.String)
    requests = db.relationship('RequestModel', backref='person', lazy=True)


class RequestModel(db.Model):
    id = db.Column(db.Integer, primary_key=True)

    dest_name = db.Column(db.String(80), nullable=False)
    dest_type = db.Column(db.String(80), nullable=False)
    num_people = db.Column(db.Integer)
    address = db.Column(db.String(200))

    hot_food_needed = db.Column(db.Integer)
    hot_food_available = db.Column(db.Integer)
    cold_food_needed = db.Column(db.Integer)
    cold_food_available = db.Column(db.Integer)
    delivery_deadline = db.Column(db.Integer)
    urgency_level = db.Column(db.String(20))

    person_id = db.Column(
        db.Integer,
        db.ForeignKey('person.id'),
        nullable=True
    )

    def to_dict(self):
        return {
            "id": self.id,
            "dest_name": self.dest_name,
            "dest_type": self.dest_type,
            "num_people": self.num_people,
            "address": self.address,
            "hot_food_needed": self.hot_food_needed,
            "hot_food_available": self.hot_food_available,
            "cold_food_needed": self.cold_food_needed,
            "cold_food_available": self.cold_food_available,
            "delivery_deadline": self.delivery_deadline,
            "urgency_level": self.urgency_level,
            "person_id": self.person_id
        }

request_args = reqparse.RequestParser()

class Request(Resource):

    def post(self):

        data = request.get_json()

        print(data)

        new_request = RequestModel(
            dest_name=data['dest_name'],
            dest_type=data['dest_type'],
            num_people=data.get('num_people'),
            address=data.get('address'),
            hot_food_needed=data.get('hot_food_needed'),
            hot_food_available=data.get('hot_food_available'),
            cold_food_needed=data.get('cold_food_needed'),
            cold_food_available=data.get('cold_food_available'),
            delivery_deadline=data.get('delivery_deadline'),
            urgency_level=data.get('urgency_level'),
        )

        db.session.add(new_request)
        db.session.commit()

        path, edges_used, total_km, hub = closest_hub(data['dest_name'])

        path_json = [
            {
                "latitude": node.lat,
                "longitude": node.lng
            }
            for node in path
        ]

        return {
            "message": "Request saved",
            "id": new_request.id,
            "path": path_json,
        }, 201

class RequestByID(Resource):
    def get(self, request_id):
        request = RequestModel.query.get(request_id)

        if request is None:
            return {"error": "Request not found"}, 404

        return request.to_dict(), 200


api.add_resource(Request, '/api/request/')
api.add_resource(RequestByID, '/requests/<int:request_id>')

if __name__ == '__main__':
    app.run(debug=True)