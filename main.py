from flask import Flask, render_template, request, session
from flask_sqlalchemy import SQLAlchemy
from flask_cors import CORS
from flask_restful import Resource, Api, reqparse, fields, marshal_with, abort
from sqlalchemy import JSON

import databaseInfo
import dispatcher
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
    map_config = {
        "center": [43.6532, -79.3832],
        "zoom": 13
    }

    return render_template(
        "frontEndUser.html",
        map_config=map_config
    )

@app.route("/management")
def managementIndex():
    map_config = {
        "center": [43.6532, -79.3832],
        "zoom": 13
    }

    return render_template(
        "frontEndManagement.html",
        map_config=map_config
    )

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
    'status': fields.Integer,
}


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
    urgency_level = db.Column(db.Integer)
    path = db.Column(JSON, nullable=False)
    status = db.Column(db.Integer)

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
            "path": self.path,
            "status": self.status,
        }

request_args = reqparse.RequestParser()

class Request(Resource):

    def post(self):

        data = request.get_json()

        path, edges_used, total_km, hub = closest_hub(data['dest_name'])

        path_json = [
            {
                "latitude": node.lat,
                "longitude": node.lng
            }
            for node in path
        ]

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
            path = path_json,
            status = 1
        )

        db.session.add(new_request)
        db.session.commit()

        dispatcher.recalculatePriorities()

        return {
            "message": "Request saved",
            "id": new_request.id,
            "path": path_json,
        }, 201

    def get(self):
        return databaseInfo.get_all_requests()

class RequestByID(Resource):
    def get(self, request_id):
        request = RequestModel.query.get(request_id)

        if request is None:
            return {"error": "Request not found"}, 404

        return request.to_dict(), 200

class Routes(Resource):
    def get(self):
        nodes_json = [
            {
                "latitude": node.lat,
                "longitude": node.lng
            }
            for node in nodes
        ]
        return nodes_json

api.add_resource(Request, '/api/request/')
api.add_resource(RequestByID, '/requests/<int:request_id>')
api.add_resource(Routes, '/api/routes/')

if __name__ == '__main__':
    databaseInfo.set_model(app,db,RequestModel)
    app.run(debug=True)