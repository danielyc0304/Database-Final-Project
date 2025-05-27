from flask import Flask, render_template, request, redirect, url_for, jsonify, session

from dotenv import load_dotenv
import os
from supabase import create_client

from datetime import timedelta

import bcrypt
import datetime


load_dotenv()

app = Flask(__name__)
app.secret_key = os.getenv("SECRET_KEY")
app.permanent_session_lifetime = timedelta(days=7)

@app.before_request
def make_session_permanent():
    session.permanent = True

url: str = os.environ.get("SUPABASE_URL") or ""
key: str = os.environ.get("SUPABASE_KEY") or ""
supabase = create_client(url, key)


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

<<<<<<< HEAD
    # 查詢所有圖片
    media_list = supabase.table("house_media").select("*").eq("house_id", house_id).order("order_index").execute().data
    return render_template("house.html", house=house, landlord=landlord, media_list=media_list)
=======
>>>>>>> danielyc0304/main


@app.route("/")
def home():
    # 假設 home.html 存在
    return render_template("home.html")


@app.route("/logout")
def logout():
    session.clear()
    return redirect(url_for("home"))


@app.route("/api/login", methods=["POST"])
def api_login():
    data = request.json  # 接收 JSON 格式的請求
    if not data:
        return jsonify({"error": "No data provided."}), 400

    username = data.get("username")
    password = data.get("password")

    # 查詢 user_login 表
    res = (
        supabase.table("user_login")
        .select("user_password")
        .eq("user_account", username)
        .execute()
    )
    if not res.data:
        return jsonify({"error": "Invalid credentials. Try again."}), 401

    hashed_password = res.data[0]["user_password"]

    if bcrypt.checkpw(password.encode("utf-8"), hashed_password.encode("utf-8")):
        # 更新狀態與登入時間
        now = datetime.datetime.now(datetime.timezone.utc).isoformat()
        supabase.table("user_login").update(
            {"account_status": "ACTIVE", "last_login_time": now}
        ).eq("user_account", username).execute()

        # 先查 user_login 拿 user_id
        login_res = (
            supabase.table("user_login")
            .select("user_id")
            .eq("user_account", username)
            .execute()
        )
        if not login_res.data:
            return jsonify({"error": "Invalid credentials. Try again."}), 401

        user_id = login_res.data[0]["user_id"]
        session["user_id"] = user_id
        session["username"] = username

        # 再查 users 拿 user_role
        role_res = (
            supabase.table("users").select("user_role").eq("user_id", user_id).execute()
        )
        if role_res.data:
            session["role"] = role_res.data[0]["user_role"]
            return (
                jsonify(
                    {"message": f"Welcome back, {username}!", "role": session["role"]}
                ),
                200,
            )
        else:
            return jsonify({"error": "No role found."}), 401
    else:
        return jsonify({"error": "Invalid credentials. Try again."}), 401


@app.route("/signup", methods=["GET"])
def signup_page():
    return render_template("signup.html")


@app.route("/api/check_username", methods=["POST"])
def check_username():
    data = request.json
    if not data:
        return jsonify({"error": "No data provided."}), 400

    username = data.get("username")
    # 查詢 user_login 是否有這個 user_account
    exist = (
        supabase.table("user_login")
        .select("user_account")
        .eq("user_account", username)
        .execute()
    )
    if exist.data:
        return jsonify({"exists": True})
    else:
        return jsonify({"exists": False})


@app.route("/api/signup", methods=["POST"])
def api_signup():
    # 支援 multipart/form-data
    if request.content_type.startswith("multipart/form-data"):
        data = request.form
        files = request.files
    else:
        data = request.json
        files = None
    if not data:
        return jsonify({"error": "No data provided."}), 400

    user_account = data.get("account")
    user_password = data.get("password")
    last_name = data.get("last_name")
    first_name = data.get("first_name")
    nickname = data.get("nickname")
    email = data.get("email")
    role = data.get("role")

    # 檢查必填
    required_fields = [last_name, first_name, nickname, email, role]
    if not all(required_fields):
        return jsonify({"error": "請完整填寫所有必填欄位"}), 400
    if user_password is None:
        return jsonify({"error": "密碼為必填欄位"}), 400

    # 產生鹽值並加密密碼
    salt = bcrypt.gensalt()
    hashed_password = bcrypt.hashpw(user_password.encode("utf-8"), salt).decode("utf-8")
    salt_str = salt.decode("utf-8")

    account_status = "ACTIVE"
    created_time = datetime.datetime.now(datetime.timezone.utc).isoformat()
    last_login_time = created_time

    # 檢查帳號是否已存在
    exist = (
        supabase.table("user_login")
        .select("user_account")
        .eq("user_account", user_account)
        .execute()
    )
    if exist.data:
        return jsonify({"error": "User account already exists!"}), 400

    # 處理頭像（這裡僅示範，實際應上傳到 Supabase Storage 並取得 URL）
    avatar_url = None
    if files and "avatar" in files:
        avatar = files["avatar"]
        # 產生唯一檔名
<<<<<<< HEAD
=======
        if avatar.filename and "." in avatar.filename:
            ext = avatar.filename.rsplit(".", 1)[-1]
        else:
            ext = "jpg"  # default extension if filename is missing or has no extension
        filename = f"{user_account}_{int(datetime.datetime.now().timestamp())}.{ext}"
        # 上傳到 Supabase Storage
>>>>>>> danielyc0304/main
        file_bytes = avatar.read()  # 讀成 bytes
        res_upload = supabase.storage.from_("dbfinal-avatars").upload(
            filename, file_bytes, {"content-type": avatar.mimetype}
        )
        if not res_upload:
            return jsonify({"error": "頭像上傳失敗"}), 500
        avatar_url = supabase.storage.from_("dbfinal-avatars").get_public_url(filename)

    # 1. 先插入 users，讓 user_id 自動產生
    user_data = {
        "user_name": nickname,
        "user_lname": last_name,
        "user_fname": first_name,
        "user_email": email,
        "user_role": role,
        "user_avatar_url": avatar_url,
    }
    res_user = supabase.table("users").insert(user_data).execute()
    if not res_user.data:
        return jsonify({"error": "Signup failed (user insert)."}), 500

    # 取得新 user_id
    user_id = res_user.data[0]["user_id"]

    # 2. 再插入 user_login，user_id 當 FK
    login_data = {
        "user_id": user_id,
        "user_account": user_account,
        "user_password": hashed_password,
        "user_salt": salt_str,
        "account_status": account_status,
        "created_time": created_time,
        "last_login_time": last_login_time,
    }
    res_login = supabase.table("user_login").insert(login_data).execute()
    if not res_login.data:
        return jsonify({"error": "Signup failed (login insert)."}), 500

    return jsonify({"message": "Signup successful!"}), 201


# 新增房屋
@app.route("/api/houses", methods=["POST"])
def add_house():
    if "user_id" not in session or session.get("role") != "Landlord":
        return jsonify({"error": "未授權"}), 403

<<<<<<< HEAD
    # 支援 multipart/form-data
    if request.content_type.startswith("multipart/form-data"):
        data = request.form
        files = request.files.getlist("media_list")
    else:
        data = request.json
        files = []

    landlord_account = session["username"]

    full_address = (
        (data.get('city') or '') +
        (data.get('district') or '') +
        (data.get('road') or '') +
        (data.get('lane') or '') +
        (data.get('alley') or '') +
        (data.get('number') or '')
    )
=======
>>>>>>> danielyc0304/main

    # 1. 先新增 ADDRESS
    address_data = {
        'country': "台灣",
        'city': data.get('city'),
        'distrit': data.get('district'),
        'road': data.get('road'),
        'lane': data.get('lane'),
        'alley': data.get('alley'),
        'number': data.get('number'),
        'zip_code': data.get('zip_code'),
        'full_address': full_address
    }
    res_address = supabase.table("address").insert(address_data).execute()
    if not res_address.data:
        return jsonify({"error": "新增地址失敗"}), 500
    house_address_id = res_address.data[0]["address_id"]

    # 1. 先用 landlord_account (user_account) 去 users table 查 user_id
    user_res = (
        supabase.table("user_login")
        .select("user_id")
        .eq("user_account", landlord_account)
        .execute()
    )
    if not user_res.data:
        return jsonify({"error": "找不到使用者"}), 404
    user_id = user_res.data[0]["user_id"]

    # 2. 再新增 HOUSE
    house_data = {
        "owner_id": user_id,  # 房東帳號
        "house_address_id": house_address_id,
        "house_title": data.get("house_title"),
        "house_desc": data.get("house_desc"),
        "house_price": 0,  # 預設為 0，後續可更新
        "house_area": 0,  # 預設為 0，後續可更新
        "house_floor": 0,  # 預設為 0，後續可更新
        "house_type": data.get("house_type"),  # APARTMENT, SUITE, ROOM, HOUSE, OTHER
        "house_status": data.get(
            "house_status"
        ),  # DRAFT, PUBLISHED, RENTED, OFFLINE, ARCHIVED
        "price_per_month": data.get("price_per_month"),
        "max_months": data.get("max_months"),
        "views_count": 0,  # 新增 view_count，預設值為 0
        "created_time": datetime.datetime.now(datetime.timezone.utc).isoformat(),
    }
    res_house = supabase.table("house").insert(house_data).execute()
    if not res_house.data:
        return jsonify({"error": "新增房屋失敗"}), 500
    house_id = res_house.data[0]["house_id"]

    # 3. 處理 HOUSE_MEDIA
    for idx, file in enumerate(files):
        filename = f"house_{house_id}_{int(datetime.datetime.now().timestamp())}_{idx}.{file.filename.rsplit('.', 1)[-1]}"
        file_bytes = file.read()
        res_upload = supabase.storage.from_("dbfinal-housemedia").upload(
            filename, file_bytes, {"content-type": file.mimetype}
        )
        if not res_upload:
            return jsonify({"error": "圖片上傳失敗"}), 500
        url = supabase.storage.from_("dbfinal-housemedia").get_public_url(filename)
        media_data = {
            "house_id": house_id,
            "media_type": "Image",
            "media_url": url,
            "thumbnail_url": url,
            "order_index": idx,
            "created_time": datetime.datetime.now(datetime.timezone.utc).isoformat(),
        }
        res_media = supabase.table("house_media").insert(media_data).execute()
        if not res_media.data:
            return jsonify({"error": "新增媒體失敗"}), 500

    return jsonify({"message": "房屋新增成功"}), 201


# 查詢房東的房屋列表
@app.route("/api/houses", methods=["GET"])
def get_houses():
    #print("session:", dict(session))  # 新增
    if "user_id" not in session or session.get("role") != "Landlord":
        return jsonify({"error": "未授權"}), 403

    landlord_account = session["username"]
    #print("landlord_account:", landlord_account)  # 新增

    # 1. 先用 landlord_account (user_account) 去 users table 查 user_id
    user_res = (
        supabase.table("user_login")
        .select("user_id")
        .eq("user_account", landlord_account)
        .execute()
    )
    #print("user_res:", user_res.data)  # 新增
    if not user_res.data:
        return jsonify({"error": "找不到使用者"}), 404
    user_id = user_res.data[0]["user_id"]

    # 2. 再用 user_id 去 HOUSE table 查房屋列表，並 join address 拿 full_address
    res = (
        supabase.table("house")
        .select("*, address:house_address_id(full_address)")
        .eq("owner_id", user_id)
        .execute()
    )
    #print("house_res:", res.data)  # 新增
    for house in res.data:
        media = supabase.table("house_media").select("*").eq("house_id", house["house_id"]).order("order_index").limit(1).execute().data
        house["main_image_url"] = media[0]["media_url"] if media else "/static/images/placeholder.jpg"
    return jsonify(res.data)

#房東點選編輯房屋
@app.route("/api/houses/<house_id>", methods=["GET"])
def get_house(house_id):
    if "user_id" not in session or session.get("role") != "Landlord":
        return jsonify({"error": "未授權"}), 403

    res = (
        supabase.table("house")
        .select("*, address:house_address_id(*)")
        .eq("house_id", house_id)
        .execute()
    )
    if not res.data:
        return jsonify({"error": "找不到房屋"}), 404
    return jsonify(res.data[0])

#房東確認更新房屋資訊
@app.route("/api/houses/<house_id>", methods=["PUT"])
def update_house(house_id):
    if "user_id" not in session or session.get("role") != "Landlord":
        return jsonify({"error": "未授權"}), 403

    if request.content_type.startswith("multipart/form-data"):
        data = request.form
        files = request.files.getlist("media_list")
    else:
        data = request.json
        files = []

    full_address = (
        (data.get('city') or '') +
        (data.get('district') or '') +
        (data.get('road') or '') +
        (data.get('lane') or '') +
        (data.get('alley') or '') +
        (data.get('number') or '')
    )

    # 先更新 address
    address_data = {
        'city': data.get('city'),
        'distrit': data.get('district'),
        'road': data.get('road'),
        'lane': data.get('lane'),
        'alley': data.get('alley'),
        'number': data.get('number'),
        'zip_code': data.get('zip_code'),
        'full_address': full_address
    }
    # 查出 house_address_id
    house_res = supabase.table("house").select("house_address_id").eq("house_id", house_id).execute()
    if not house_res.data:
        return jsonify({"error": "找不到房屋"}), 404
    address_id = house_res.data[0]["house_address_id"]
    supabase.table("address").update(address_data).eq("address_id", address_id).execute()

    # 再更新 house
    house_data = {
        "house_title": data.get("house_title"),
        "house_desc": data.get("house_desc"),
        "price_per_month": data.get("price_per_month"),
        "house_type": data.get("house_type"),
        "house_status": data.get("house_status")
    }
    supabase.table("house").update(house_data).eq("house_id", house_id).execute()

    # 覆蓋舊圖片：先刪除舊的，再新增這次上傳的
    if files:
        # 刪除舊的 house_media
        supabase.table("house_media").delete().eq("house_id", house_id).execute()

        for idx, file in enumerate(files):
            filename = f"house_{house_id}_{int(datetime.datetime.now().timestamp())}_{idx}.{file.filename.rsplit('.', 1)[-1]}"
            file_bytes = file.read()
            res_upload = supabase.storage.from_("dbfinal-housemedia").upload(
                filename, file_bytes, {"content-type": file.mimetype}
            )
            if not res_upload:
                return jsonify({"error": "圖片上傳失敗"}), 500
            url = supabase.storage.from_("dbfinal-housemedia").get_public_url(filename)
            media_data = {
                "house_id": house_id,
                "media_type": "Image",
                "media_url": url,
                "thumbnail_url": url,
                "order_index": idx,
                "created_time": datetime.datetime.now(datetime.timezone.utc).isoformat(),
            }
            res_media = supabase.table("house_media").insert(media_data).execute()
            if not res_media.data:
                return jsonify({"error": "媒體新增失敗"}), 500

    return jsonify({"message": "房屋更新成功"})

#首頁顯示房屋
@app.route("/api/home_houses", methods=["GET"])
def get_home_houses():
    page = int(request.args.get("page", 1))
    page_size = int(request.args.get("page_size", 6))
    city = request.args.get("city")
    district = request.args.get("district")

    # 先查 address_id
    address_query = supabase.table("address").select("address_id")
    if city:
        address_query = address_query.eq("city", city)
    if district:
        address_query = address_query.eq("distrit", district)  # 注意你的欄位名是 distrit
    address_ids = [a["address_id"] for a in address_query.execute().data]

    query = supabase.table("house").select("house_id, house_title, price_per_month, house_type, house_address_id, address:house_address_id(full_address)")
    if city or district:
        if address_ids:
            query = query.in_("house_address_id", address_ids)
        else:
            return jsonify({"houses": [], "total": 0})

    total = len(query.execute().data)
    res = query.order("created_time", desc=True).range((page-1)*page_size, page*page_size-1).execute()

    for house in res.data:
        media = supabase.table("house_media").select("*").eq("house_id", house["house_id"]).order("order_index").limit(1).execute().data
        house["main_image_url"] = media[0]["media_url"] if media else "/static/images/placeholder.jpg"

    return jsonify({"houses": res.data, "total": total})

if __name__ == "__main__":
    app.run(debug=True, port=8080)
