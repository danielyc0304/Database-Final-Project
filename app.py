from flask import Flask, render_template

app = Flask(__name__)


@app.route("/")
def index():
    return "<p>Hello World</p>"


@app.route("/about/<user_id>")
def about(user_id):
    return render_template("about.html")


if __name__ == "__main__":
    app.run(debug=True, port=8080)
