import os
import re
from flask import Flask, request, url_for
from markupsafe import escape
from werkzeug.utils import secure_filename

app = Flask(__name__)
app.config["UPLOAD_FOLDER"] = os.path.join(app.root_path, "static", "uploads")
app.config["MAX_CONTENT_LENGTH"] = 5 * 1024 * 1024
os.makedirs(app.config["UPLOAD_FOLDER"], exist_ok=True)

ALLOWED_EXTENSIONS = {"jpg", "jpeg", "png", "webp"}

cars = [
    {"name": "Renault Clio 4", "year": "2018", "city": "الجزائر",
     "price": "1800000", "phone": "", "origin": "أوروبية", "photo": ""},
    {"name": "Hyundai i10", "year": "2020", "city": "وهران",
     "price": "2000000", "phone": "", "origin": "كورية", "photo": ""}
]



def save_comment(car_name, author, content):
    import sqlite3
    db_path = os.path.join(app.root_path, "cars.db")
    with sqlite3.connect(db_path) as conn:
        conn.execute(
            "INSERT INTO comments (car_name, author, content) VALUES (?, ?, ?)",
            (car_name, author, content)
        )


def get_comments(car_name):
    import sqlite3
    db_path = os.path.join(app.root_path, "cars.db")
    with sqlite3.connect(db_path) as conn:
        conn.row_factory = sqlite3.Row
        rows = conn.execute(
            "SELECT author, content, created_at FROM comments "
            "WHERE car_name = ? ORDER BY id DESC",
            (car_name,)
        ).fetchall()
    return [dict(row) for row in rows]

def allowed_file(filename):
    return (
        "." in filename
        and filename.rsplit(".", 1)[1].lower() in ALLOWED_EXTENSIONS
    )


def whatsapp_number(phone):
    digits = re.sub(r"\D", "", phone)
    if digits.startswith("0"):
        digits = "213" + digits[1:]
    elif not digits.startswith("213"):
        digits = "213" + digits
    return digits


@app.route("/", methods=["GET", "POST"])
def home():
    message = ""

    if request.method == "POST" and request.form.get("action") == "comment":
        car_name = request.form.get("car_name", "").strip()
        author = request.form.get("author", "").strip()
        content = request.form.get("content", "").strip()

        if car_name and author and content and len(author) <= 60 and len(content) <= 1000:
            save_comment(car_name, author, content)
            message = "تم حفظ تعليقك بنجاح!"
        else:
            message = "يرجى إدخال الاسم والتعليق، مع الالتزام بالحد المسموح."

    elif request.method == "POST":
        name = request.form.get("name", "").strip()
        year = request.form.get("year", "").strip()
        city = request.form.get("city", "").strip()
        price = request.form.get("price", "").strip()
        km = request.form.get("km", "").strip()
        phone = request.form.get("phone", "").strip()
        origin = request.form.get("origin", "أخرى").strip()
        photo = request.files.get("photo")
        photo_name = ""

        if not all([name, year, city, price, phone]):
            message = "يرجى ملء جميع الخانات."
        elif not year.isdigit() or not price.isdigit():
            message = "يرجى إدخال سنة وسعر صحيحين."
        elif photo and photo.filename and not allowed_file(photo.filename):
            message = "الصورة يجب أن تكون JPG أو PNG أو WEBP."
        else:
            if photo and photo.filename:
                safe_name = secure_filename(photo.filename)
                photo_name = safe_name
                base, ext = os.path.splitext(safe_name)
                counter = 1
                while os.path.exists(os.path.join(app.config["UPLOAD_FOLDER"], photo_name)):
                    photo_name = f"{base}_{counter}{ext}"
                    counter += 1
                photo.save(os.path.join(app.config["UPLOAD_FOLDER"], photo_name))

            cars.insert(0, {
                "name": name,
                "year": year,
                "city": city,
                "price": price,
                "km": km,
                "phone": phone,
                "origin": origin,
                "photo": photo_name
            })
            message = "تمت إضافة إعلانك بنجاح!"

    cards = ""
    for car in cars:
        photo_html = ""
        if car.get("photo"):
            photo_url = url_for("static", filename="uploads/" + car["photo"])
            photo_html = (
                f'<img class="car-photo" src="{photo_url}" '
                f'alt="صورة {escape(car["name"])}">'
            )

        phone_digits = whatsapp_number(car["phone"]) if car["phone"] else ""
        whatsapp_html = ""
        if phone_digits:
            whatsapp_html = (
                f'<a class="whatsapp" href="https://wa.me/{phone_digits}" '
                f'target="_blank" rel="noopener">تواصل عبر واتساب</a>'
            )

        comments = get_comments(car["name"])
        comments_html = "".join(
            f'<p><strong>{escape(c["author"])}</strong>: {escape(c["content"])}</p>'
            for c in comments
        )
        safe_car_name = escape(car["name"])

        cards += f"""
        <section class="card">
            {photo_html}
            <h3>{safe_car_name}</h3>
            <p>🚘 المنشأ: {escape(car["origin"])}</p>
            <p>📅 سنة الصنع: {escape(car["year"])}</p>
            <p>📍 الولاية: {escape(car["city"])}</p>
            <p>🛣️ المسافة المقطوعة: {escape(car.get("km", "غير محددة"))} كم</p>
            <p class="price">{escape(car["price"])} دج</p>
            <p>📞 {escape(car["phone"]) if car["phone"] else "إعلان تجريبي"}</p>
            {whatsapp_html}
            <h4>التعليقات</h4>
            {comments_html}
            <form method="POST">
                <input type="hidden" name="action" value="comment">
                <input type="hidden" name="car_name" value="{safe_car_name}">
                <label>اسمك</label>
                <input name="author" maxlength="60" required>
                <label>تعليقك</label>
                <input name="content" maxlength="1000" required>
                <button type="submit">إرسال التعليق</button>
            </form>
        </section>
        """

    return f"""
    <!DOCTYPE html>
    <html lang="ar" dir="rtl">
    <head>
      <meta name="google-site-verification" content="21yc-t0xU1MFJINwGsWZQjsgjVJwoS8nYO2C2gT_PVU" />
      <meta charset="UTF-8">
      <meta name="viewport" content="width=device-width, initial-scale=1">
      <meta name="description" content="سيارات للبيع في الجزائر، تصفح الإعلانات وتواصل مع البائعين.">
      <title>سيارات الجزائر | بيع وشراء السيارات</title>
      <style>
        * {{ box-sizing: border-box; }}
        body {{ margin:0; font-family:Arial,sans-serif; background:#f1f5f3; color:#24312b; }}
        header {{ background:linear-gradient(135deg,#075b38,#10965b); color:white; padding:30px 16px; text-align:center; }}
        header h1 {{ margin:0 0 10px; font-size:30px; }}
        header p {{ margin:0; }}
        main {{ padding:20px 14px; max-width:720px; margin:auto; }}
        .formbox,.card {{ background:white; border-radius:16px; padding:18px; margin-bottom:18px; box-shadow:0 4px 14px #0000000d; }}
        h2 {{ color:#087443; }}
        h3 {{ color:#087443; margin-bottom:8px; }}
        label {{ display:block; font-weight:bold; margin-top:12px; }}
        input,select {{ width:100%; padding:12px; margin:7px 0; border:1px solid #ccd5cf; border-radius:9px; font-size:16px; background:white; }}
        button {{ background:#087443; color:white; border:0; padding:13px; border-radius:9px; font-size:17px; width:100%; margin-top:12px; }}
        .price {{ color:#087443; font-size:22px; font-weight:bold; }}
        .car-photo {{ width:100%; max-height:300px; object-fit:cover; border-radius:12px; }}
        .whatsapp {{ display:block; text-align:center; background:#168b49; color:white; text-decoration:none; padding:12px; border-radius:9px; margin-top:12px; font-weight:bold; }}
        .notice {{ background:#e7f5ec; padding:12px; border-radius:9px; }}
        footer {{ text-align:center; color:#65736b; padding:20px; }}
      </style>
    </head>
    <body>
      <header>
        <h1>🚗 سيارات الجزائر 🇩🇿</h1>
        <p>اعثر على سيارتك القادمة أو اعرض سيارتك للبيع</p>
      </header>
      <main>
        <section class="formbox">
          <h2>أضف سيارتك للبيع</h2>
          <p class="notice">{message}</p>
          <form method="POST" enctype="multipart/form-data">
            <label>منشأ السيارة</label>
            <select name="origin" required>
              <option value="أوروبية">أوروبية</option>
              <option value="ألمانية">ألمانية</option>
              <option value="صينية">صينية</option>
              <option value="كورية">كورية</option>
              <option value="يابانية">يابانية</option>
              <option value="أخرى">أخرى</option>
            </select>
            <label>اسم السيارة والموديل</label>
            <input name="name" placeholder="مثال: Renault Clio 4" required>
            <label>سنة الصنع</label>
            <input name="year" type="number" min="1950" max="2027" placeholder="2020" required>
            <label>الولاية</label>
            <input name="city" placeholder="مثال: أدرار" required>
            <label>المسافة المقطوعة (كم)</label>
            <input name="km" type="number" min="0" placeholder="مثال: 150000" required>
            <label>السعر بالدينار الجزائري</label>
            <input name="price" type="number" min="1" placeholder="1800000" required>
            <label>رقم هاتف البائع</label>
            <input name="phone" type="tel" placeholder="مثال: 0550123456" required>
            <label>صورة السيارة (اختيارية حاليًا)</label>
            <input name="photo" type="file" accept=".jpg,.jpeg,.png,.webp,image/jpeg,image/png,image/webp">
            <button type="submit">نشر الإعلان</button>
          </form>
        </section>
        <h2>🚘 سيارات معروضة</h2>
        {cards}
      </main>
      <footer>سيارات الجزائر 🇩🇿 — بيع وشراء السيارات</footer>
    </body>
    </html>
    """


@app.errorhandler(413)
def file_too_large(error):
    return "حجم الصورة كبير. اختر صورة أصغر من 5 ميغابايت.", 413


if __name__ == "__main__":
    app.run(host="127.0.0.1", port=5000, debug=False)
