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
    user = supabase.table("users").select("*").eq("user_id", user_id).execute().data[0]
    login = (
        supabase.table("user_login")
        .select("*")
        .eq("user_id", user_id)
        .execute()
        .data[0]
    )
    houses = (
        supabase.table("house")
        .select("*")
        .eq("owner_id", user_id)
        .limit(5)
        .execute()
        .data
    )
    for house in houses:
        house["full_address"] = (
            supabase.table("address")
            .select("full_address")
            .eq("address_id", house["house_address_id"])
            .execute()
            .data[0]["full_address"]
        )
        house["price_per_month"] = f"{house['price_per_month']:,}"

    return render_template("about.html", user=user, login=login, houses=houses)


@app.route("/house/<house_id>")
def house(house_id):
    house = (
        supabase.table("house").select("*").eq("house_id", house_id).execute().data[0]
    )
    house["full_address"] = (
        supabase.table("address")
        .select("full_address")
        .eq("address_id", house["house_address_id"])
        .execute()
        .data[0]["full_address"]
    )
    house["price_per_month"] = f"{house['price_per_month']:,}"
    landlord = (
        supabase.table("users")
        .select("*")
        .eq("user_id", house["owner_id"])
        .execute()
        .data[0]
    )

    return render_template("house.html", house=house, landlord=landlord)


if __name__ == "__main__":
    app.run(debug=True, port=8080)
