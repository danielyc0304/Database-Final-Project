import datetime
import os
import uuid
from datetime import timedelta

import bcrypt
from dotenv import load_dotenv
from flask import Flask, jsonify, render_template, request, session
from supabase import create_client

load_dotenv()

url: str = os.environ.get("SUPABASE_URL") or ""
key: str = os.environ.get("SUPABASE_KEY") or ""
supabase = create_client(url, key)

app = Flask(__name__)
app.secret_key = os.getenv("SECRET_KEY")
app.permanent_session_lifetime = timedelta(days=7)


@app.before_request
def make_session_permanent():
    session.permanent = True


def get_user(user_id):
    user = supabase.table("users").select("*").eq("user_id", user_id).execute().data[0]

    login = (
        supabase.table("user_login")
        .select("*")
        .eq("user_id", user_id)
        .execute()
        .data[0]
    )

    return user, login


def get_houses(user_id=None, house_id=None, limit=None, photo_limit=None, address=None):
    query = supabase.table("house").select("*")

    if user_id:
        query.eq("owner_id", user_id)
    elif house_id:
        query.eq("house_id", house_id)

    if limit:
        query.limit(limit)

    houses = query.execute().data

    for house in houses:
        if address:
            house["address"] = (
                supabase.table("address")
                .select("*")
                .eq("address_id", house["house_address_id"])
                .execute()
                .data[0]
            )
        else:
            house["full_address"] = (
                supabase.table("address")
                .select("full_address")
                .eq("address_id", house["house_address_id"])
                .execute()
                .data[0]["full_address"]
            )
        house["price_per_month"] = f"{house['price_per_month']:,}"
        house["media_url"] = (
            supabase.table("house_media")
            .select("media_url")
            .eq("house_id", house["house_id"])
            .order("order_index")
            .execute()
            .data
        )
        house["media_url"] = [media["media_url"] for media in house["media_url"]]

        if photo_limit:
            house["media_url"] = house["media_url"][:photo_limit]

    return houses


def get_notes(house_id, user_id):
    notes = (
        supabase.table("view_note")
        .select("*")
        .eq("house_id", house_id)
        .eq("user_id", user_id)
        .execute()
        .data
    )

    return notes


@app.route("/", methods=["GET"])
def home_page():
    return render_template("home.html")


@app.route("/about/<user_id>", methods=["GET"])
def about_page(user_id):
    user, login = get_user(user_id)
    houses = get_houses(user_id=user_id, limit=3, photo_limit=1)

    rates = (
        supabase.table("landlord_profile")
        .select("rating")
        .eq("landlord_id", user_id)
        .execute()
        .data
    )
    print(rates)
    if rates:
        score = sum([rate['rating'] for rate in rates]) / len(rates)
        user["rating"] = f"{score:.1f} - {len(rates)} 位使用者"
    else:
        user["rating"] = "暫無使用者評價"

    return render_template("about.html", user=user, login=login, houses=houses)


@app.route("/about/<user_id>/edit", methods=["GET"])
def edit_about_page(user_id):
    # TODO 改到前端判斷，如果不是本人就不顯示編輯按鈕
    if "user_id" not in session:
        return "Not logged in.", 401
    if int(user_id) != session.get("user_id"):
        return "Unauthorized.", 403

    user = (
        supabase.table("users")
        .select("*")
        .eq("user_id", int(user_id))
        .execute()
        .data[0]
    )

    return render_template("edit_profile.html", user=user)


@app.route("/house/<house_id>", methods=["GET"])
def house_page(house_id):
    house = get_houses(house_id=house_id)[0]
    landlord, _ = get_user(house["owner_id"])
    notes = get_notes(house_id, session.get("user_id"))

    return render_template("house.html", house=house, landlord=landlord, notes=notes)


@app.route("/api/add_house", methods=["POST"])
def api_add_house():
    data = request.form
    files = request.files.getlist("media_list")

    full_address = (
        (data.get("city") or "")
        + (data.get("district") or "")
        + (data.get("road") or "")
        + (data.get("lane") or "")
        + (data.get("alley") or "")
        + (data.get("number") or "")
    )

    address_data = {
        "country": "台灣",
        "city": data.get("city"),
        "distrit": data.get("district"),
        "road": data.get("road"),
        "lane": data.get("lane"),
        "alley": data.get("alley"),
        "number": data.get("number"),
        "zip_code": data.get("zip_code"),
        "full_address": full_address,
    }
    res_address = supabase.table("address").insert(address_data).execute().data
    if not res_address:
        return jsonify({"message": "Address insert failed."}), 500
    house_address_id = res_address[0]["address_id"]

    house_data = {
        "owner_id": session.get("user_id"),
        "house_address_id": house_address_id,
        "house_title": data.get("house_title"),
        "house_desc": data.get("house_desc"),
        "house_price": 0,
        "house_area": 0,
        "house_floor": 0,
        "house_type": data.get("house_type"),
        "house_status": data.get("house_status"),
        "price_per_month": data.get("price_per_month"),
        "max_months": data.get("max_months"),
        "views_count": 0,
        "created_time": datetime.datetime.now(datetime.timezone.utc)
        .replace(microsecond=0)
        .isoformat(),
    }
    res_house = supabase.table("house").insert(house_data).execute().data
    if not res_house:
        return jsonify({"message": "House insert failed."}), 500
    house_id = res_house[0]["house_id"]

    for idx, file in enumerate(files):
        if file.filename:
            filename = f"{uuid.uuid4().hex}.{file.filename.split('.')[-1]}"
            file_bytes = file.read()
            res = supabase.storage.from_("dbfinal-housemedia").upload(
                filename, file_bytes, {"content-type": file.mimetype}
            )
            if not res:
                return jsonify({"message": "Media upload failed"}), 500
            house_media_url = supabase.storage.from_(
                "dbfinal-housemedia"
            ).get_public_url(filename)

            media_data = {
                "house_id": house_id,
                "media_type": "Image",
                "media_url": house_media_url,
                "thumbnail_url": house_media_url,
                "order_index": idx,
                "created_time": datetime.datetime.now(datetime.timezone.utc)
                .replace(microsecond=0)
                .isoformat(),
            }
            res_media = supabase.table("house_media").insert(media_data).execute()
            if not res_media.data:
                return jsonify({"message": "Media insert failed."}), 500

    return jsonify({"message": "Add house successfully"}), 201


@app.route("/api/check_account", methods=["POST"])
def api_check_account():
    req = request.get_json()
    username = req.get("username")

    user = (
        supabase.table("user_login")
        .select("user_account")
        .eq("user_account", username)
        .execute()
        .data
    )

    if user:
        return jsonify({"exists": True}), 200
    else:
        return jsonify({"exists": False}), 200


@app.route("/api/login", methods=["POST"])
def api_login():
    req = request.get_json()
    username = req.get("username")
    password = req.get("password")

    user = (
        supabase.table("user_login")
        .select("user_password")
        .eq("user_account", username)
        .execute()
        .data
    )
    if not user:
        return jsonify({"message": "Account doesn't exist."}), 401

    hashed_password = user[0]["user_password"]
    if not bcrypt.checkpw(password.encode("utf-8"), hashed_password.encode("utf-8")):
        return jsonify({"message": "Wrong password."}), 401

    now = (
        datetime.datetime.now(datetime.timezone.utc).replace(microsecond=0).isoformat()
    )
    supabase.table("user_login").update(
        {"account_status": "ACTIVE", "last_login_time": now}
    ).eq("user_account", username).execute()

    user_id = (
        supabase.table("user_login")
        .select("user_id")
        .eq("user_account", username)
        .execute()
        .data[0]["user_id"]
    )
    user_role = (
        supabase.table("users")
        .select("user_role")
        .eq("user_id", user_id)
        .execute()
        .data[0]["user_role"]
    )

    session["user_id"] = user_id
    session["username"] = username
    session["role"] = user_role

    return jsonify({"message": "Logged in successfully", "role": session["role"]}), 200


@app.route("/api/logout", methods=["POST"])
def api_logout():
    session.clear()

    return jsonify({"message": "Logged out successfully."}), 200


@app.route("/api/signup", methods=["POST"])
def api_signup():
    data = request.form
    files = request.files

    username = data.get("username")
    password: str = data.get("password") or ""
    last_name = data.get("last_name")
    first_name = data.get("first_name")
    nickname = data.get("nickname")
    email = data.get("email")
    role = data.get("role")

    avatar_url = None
    if files:
        avatar = files.get("avatar")

        if avatar and avatar.filename:
            filename = f"{uuid.uuid4().hex}.{avatar.filename.split('.')[-1]}"
            file_bytes = avatar.read()

            res = supabase.storage.from_("dbfinal-avatars").upload(
                filename, file_bytes, {"content-type": avatar.mimetype}
            )
            if not res:
                return jsonify({"error": "Media upload failed"}), 500

            avatar_url = supabase.storage.from_("dbfinal-avatars").get_public_url(
                filename
            )

    user_data = {
        "user_lname": last_name,
        "user_fname": first_name,
        "user_name": nickname,
        "user_email": email,
        "user_role": role,
        "user_avatar_url": avatar_url,
    }
    res_user = supabase.table("users").insert(user_data).execute().data
    if not res_user:
        return jsonify({"message": "User insert failed."}), 500

    salt = bcrypt.gensalt()
    hashed_password = bcrypt.hashpw(password.encode("utf-8"), salt).decode("utf-8")
    salt_str = salt.decode("utf-8")

    created_time = (
        datetime.datetime.now(datetime.timezone.utc).replace(microsecond=0).isoformat()
    )

    login_data = {
        "user_id": res_user[0]["user_id"],
        "user_account": username,
        "user_password": hashed_password,
        "user_salt": salt_str,
        "account_status": "ACTIVE",
        "created_time": created_time,
        "last_login_time": created_time,
    }
    res_login = supabase.table("user_login").insert(login_data).execute().data
    if not res_login:
        return jsonify({"error": "Login insert failed."}), 500

    return jsonify({"message": "Signup successful!"}), 201


@app.route("/api/houses", methods=["GET"])
def api_houses():
    houses = get_houses(user_id=session.get("user_id"), photo_limit=1)

    return jsonify(houses), 200


# 房東點選編輯房屋
@app.route("/api/house/<house_id>/edit", methods=["GET", "PUT"])
def api_get_and_update_house(house_id):
    if request.method == "GET":
        house = get_houses(house_id=house_id, address=True)[0]

        return jsonify(house), 200
    else:
        data = request.form
        files = request.files.getlist("media_list")

        full_address = (
            (data.get("city") or "")
            + (data.get("district") or "")
            + (data.get("road") or "")
            + (data.get("lane") or "")
            + (data.get("alley") or "")
            + (data.get("number") or "")
        )

        address_data = {
            "city": data.get("city"),
            "distrit": data.get("district"),
            "road": data.get("road"),
            "lane": data.get("lane"),
            "alley": data.get("alley"),
            "number": data.get("number"),
            "zip_code": data.get("zip_code"),
            "full_address": full_address,
        }
        address_id = (
            supabase.table("house")
            .select("house_address_id")
            .eq("house_id", house_id)
            .execute()
            .data[0]["house_address_id"]
        )
        res = (
            supabase.table("address")
            .update(address_data)
            .eq("address_id", address_id)
            .execute()
            .data
        )
        if not res:
            return jsonify({"message": "Address update failed"}), 500

        house_data = {
            "house_title": data.get("house_title"),
            "house_desc": data.get("house_desc"),
            "price_per_month": data.get("price_per_month"),
            "house_type": data.get("house_type"),
            "house_status": data.get("house_status"),
        }
        res = (
            supabase.table("house")
            .update(house_data)
            .eq("house_id", house_id)
            .execute()
            .data
        )
        if not res:
            return jsonify({"message": "House update failed"}), 500

        if len(files) == 0:
            return jsonify({"message": "House update successfully"}), 200

        # TODO 改成可以留著舊的圖片，然後加新的
        old_urls = [
            url["media_url"].split("/")[-1][:-1]
            for url in supabase.table("house_media")
            .select("media_url")
            .eq("house_id", house_id)
            .execute()
            .data
        ]
        res = supabase.storage.from_("dbfinal-housemedia").remove(old_urls)
        if not res:
            return jsonify({"message": "Old media delete failed"}), 500
        res = (
            supabase.table("house_media")
            .delete()
            .eq("house_id", house_id)
            .execute()
            .data
        )
        if not res:
            return jsonify({"message": "House media delete failed"}), 500

        for idx, file in enumerate(files):
            if file.filename:
                filename = f"{uuid.uuid4().hex}.{file.filename.split('.')[-1]}"
                file_bytes = file.read()
                res = supabase.storage.from_("dbfinal-housemedia").upload(
                    filename, file_bytes, {"content-type": file.mimetype}
                )
                if not res:
                    return jsonify({"message": "Media upload failed"}), 500
                house_media_url = supabase.storage.from_(
                    "dbfinal-housemedia"
                ).get_public_url(filename)

                media_data = {
                    "house_id": house_id,
                    "media_type": "Image",
                    "media_url": house_media_url,
                    "thumbnail_url": house_media_url,
                    "order_index": idx,
                    "created_time": datetime.datetime.now(datetime.timezone.utc)
                    .replace(microsecond=0)
                    .isoformat(),
                }
                res_media = supabase.table("house_media").insert(media_data).execute()
                if not res_media.data:
                    return jsonify({"message": "Media insert failed."}), 500

        return jsonify({"message": "House update successfully"}), 200


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
        address_query = address_query.eq(
            "distrit", district
        )  # 注意你的欄位名是 distrit
    address_ids = [a["address_id"] for a in address_query.execute().data]

    query = supabase.table("house").select(
        "house_id, house_title, price_per_month, house_type, house_address_id, address:house_address_id(full_address)"
    )
    if city or district:
        if address_ids:
            query = query.in_("house_address_id", address_ids)
        else:
            return jsonify({"houses": [], "total": 0})

    total = len(query.execute().data)
    res = (
        query.order("created_time", desc=True)
        .range((page - 1) * page_size, page * page_size - 1)
        .execute()
    )

    for house in res.data:
        media = (
            supabase.table("house_media")
            .select("*")
            .eq("house_id", house["house_id"])
            .order("order_index")
            .limit(1)
            .execute()
            .data
        )
        house["main_image_url"] = (
            media[0]["media_url"] if media else "/static/images/placeholder.jpg"
        )

    return jsonify({"houses": res.data, "total": total})


@app.route("/api/add_note", methods=["POST"])
def add_note_route():
    data = request.get_json()
    house_id = data.get("house_id")
    content = data.get("content")
    user_id = session.get("user_id")  # 從 session 獲取 user_id

    if not user_id:
        return jsonify({"message": "使用者未登入"}), 401  # Unauthorized

    if not house_id or not content:
        return jsonify({"message": "缺少房屋ID或備註內容"}), 400

    try:
        note_data = {
            "house_id": house_id,
            "user_id": user_id,
            "note_content": content,
            "created_time": datetime.datetime.now(datetime.timezone.utc).isoformat(),
        }

        res_note = supabase.table("view_note").insert(note_data).execute()

        if not res_note.data:
            return jsonify({"message": "新增備註時資料庫錯誤"}), 500

        new_note = res_note.data[0]
        return (
            jsonify(
                {
                    "id": new_note.get("note_id"),
                    "content": new_note.get("note_content"),
                    "created_at": new_note.get("created_time"),
                    "user_id": new_note.get("user_id"),
                }
            ),
            201,
        )
    except Exception as e:
        # Log the exception for debugging
        app.logger.error(f"Error adding note: {e}")
        return jsonify({"message": f"新增備註時發生伺服器錯誤: {e}"}), 500


@app.route("/api/profile/update", methods=["POST"])
def api_update_profile():
    if "user_id" not in session:
        return jsonify({"error": "Unauthorized"}), 401

    user_id = session["user_id"]
    data = request.form
    files = request.files

    update_data = {
        "user_fname": data.get("user_fname"),
        "user_lname": data.get("user_lname"),
        "user_name": data.get("user_name"),  # 假設 nickname 對應 user_name
        "user_email": data.get("user_email"),
        "user_desc": data.get("user_desc"),  # 新增 user_desc
    }

    # 過濾掉值為 None 的欄位，避免清空資料庫中已有值的欄位
    # 調整：如果欄位是 user_desc 且其值為空字串，我們可能希望將其更新為空，而不是保留舊值
    filtered_update_data = {}
    for k, v in update_data.items():
        if v is not None:  # 保留所有非 None 的值
            if k == "user_desc" and v == "":  # 如果是 user_desc 且為空字串，也加入
                filtered_update_data[k] = v
            elif (
                v != ""
            ):  # 其他欄位，如果不是空字串才加入 (避免空字串覆蓋原有值，除非是 user_desc)
                filtered_update_data[k] = v
        # 如果 v is None，則不加入 filtered_update_data，即保留資料庫原始值

    update_data = filtered_update_data

    new_avatar_url = None
    if "avatar" in files and files["avatar"].filename != "":
        avatar = files["avatar"]
        # 確保使用者帳號存在於 session 中，用於產生檔名
        user_account = session.get("username", "default_user")
        filename = f"avatar_{user_id}_{user_account}_{int(datetime.datetime.now().timestamp())}.{avatar.filename.split('.')[-1]}"

        try:
            file_bytes = avatar.read()
            # 上傳到 Supabase Storage 的 'dbfinal-avatars' bucket
            upload_response = supabase.storage.from_("dbfinal-avatars").upload(
                path=filename,
                file=file_bytes,
                file_options={"content-type": avatar.mimetype},
            )

            # 檢查上傳是否成功 (Supabase Python client v2 可能不直接返回 HTTP 狀態碼，而是拋出異常或返回特定結構)
            # 這裡假設成功時 upload_response 是一個包含 key 的對象或字典，失敗則可能拋異常或返回 None/Error
            # 根據 Supabase client 的實際行為調整
            # if upload_response and hasattr(upload_response, 'key'): # 假設成功時有 key 屬性
            new_avatar_url = supabase.storage.from_("dbfinal-avatars").get_public_url(
                filename
            )
            update_data["user_avatar_url"] = new_avatar_url
            # else:
            #     # 處理上傳失敗的情況，可以記錄錯誤或返回錯誤訊息
            #     app.logger.error(f"Avatar upload failed: {upload_response})")
            #     return jsonify({"error": "頭像上傳失敗"}), 500

        except Exception as e:
            app.logger.error(f"Error uploading avatar: {e}")
            return jsonify({"error": f"頭像上傳時發生錯誤: {str(e)}"}), 500

    if update_data:
        try:
            res = (
                supabase.table("users")
                .update(update_data)
                .eq("user_id", user_id)
                .execute()
            )
            if (
                not res.data and not new_avatar_url
            ):  # 如果沒有資料更新且沒有新頭像 (可能沒有任何變更)
                return jsonify({"message": "沒有變更"}), 200
            if (
                not res.data
                and new_avatar_url
                and update_data.keys() == {"user_avatar_url"}
            ):
                # 只有頭像更新成功
                return (
                    jsonify(
                        {
                            "message": "個人檔案更新成功！",
                            "new_avatar_url": new_avatar_url,
                        }
                    ),
                    200,
                )
            if not res.data:
                # 有其他欄位嘗試更新但失敗
                return jsonify({"error": "更新個人檔案時資料庫錯誤"}), 500

        except Exception as e:
            app.logger.error(f"Error updating profile in DB: {e}")
            return jsonify({"error": f"更新個人檔案時發生資料庫錯誤: {str(e)}"}), 500

    response_data = {"message": "個人檔案更新成功！"}
    if new_avatar_url:
        response_data["new_avatar_url"] = new_avatar_url

    return jsonify(response_data), 200


@app.route("/api/rating/<landlord_id>", methods=["GET", "POST"])
def rating(landlord_id):
    if request.method == "GET":
        if "user_id" not in session:
            return jsonify({"rate": 0}), 200

        rate = (
            supabase.table("landlord_profile")
            .select("rating")
            .eq("landlord_id", landlord_id)
            .eq("user_id", session.get("user_id"))
            .execute()
            .data
        )
        print(landlord_id, session.get("user_id"), rate)
        if rate:
            return jsonify({"rate": rate[0]["rating"]}), 200
        else:
            return jsonify({"rate": 0}), 200
    else:
        if "user_id" not in session:
            return jsonify({"message": "Not logged in."}), 401

        req = request.get_json()
        user_id = session.get("user_id")
        rate = req.get("rate")

        rating_existed = (
            supabase.table("landlord_profile")
            .select("*")
            .eq("landlord_id", landlord_id)
            .eq("user_id", user_id)
            .execute()
            .data
        )

        if rating_existed:
            res = (
                supabase.table("landlord_profile")
                .update({"rating": rate})
                .eq("user_id", user_id)
                .execute()
                .data
            )
            if not res:
                return jsonify({"message": "Update rate failed."}), 500
        else:
            res = (
                supabase.table("landlord_profile")
                .insert(
                    {"landlord_id": landlord_id, "user_id": user_id, "rating": rate}
                )
                .execute()
                .data
            )
            if not res:
                return jsonify({"message": "Insert new rate failed."}), 500

        return jsonify({"message": "Rating successfully."}), 201


if __name__ == "__main__":
    app.run(debug=True, port=8080)
