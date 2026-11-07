from flask import Flask, render_template
from flask_restful import Resource, Api, reqparse, fields, marshal_with, abort

app = Flask(__name__, template_folder="frontEnd", static_folder="frontEnd")
api = Api(app)
@app.route("/")
def userIndex():
    return render_template("frontEndUser.html")

@app.route("/management")
def managementIndex():
    return render_template("frontEndUser.html")

userFields = {
    'id': fields.Integer,
    'name': fields.String,
    'email': fields.String
}


class Requests(Resource):
    @marshal_with(userFields)
    def get(self):

        return


api.add_resource(Requests, '/api/users/')

if __name__ == '__main__':
    app.run(debug=True)