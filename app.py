from flask import Flask, render_template

from dotenv import load_dotenv
import os
from supabase import create_client

load_dotenv()

app = Flask(__name__)

url: str = os.environ.get("SUPABASE_URL") or ""
key: str = os.environ.get("SUPABASE_KEY") or ""
supabase = create_client(url, key)


@app.route("/")
def index():
    return "<p>Hello World</p>"


@app.route("/about/<user_id>")
def about(user_id):
    return render_template("about.html")


if __name__ == "__main__":
    app.run(debug=True, port=8080)
