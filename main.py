from flask import Flask, render_template


app = Flask(__name__, template_folder="frontEnd", static_folder="frontEnd")


@app.route("/")
def home():
    return "<h1>Hello World</h1>;"
@app.route("/user")
def userIndex():
    return render_template("frontEndUser.html")

@app.route("/management")
def managementIndex():
    return render_template("frontEndUser.html")

if __name__ == '__main__':
    app.run(debug=True)