
from flask import Flask, request
from markupsafe import escape

app = Flask(__name__)

cars = [
    {"name": "Renault Clio 4", "year": "2018", "city": "الجزائر", "price": "1800000", "phone": ""},
    {"name": "Hyundai i10", "year": "2020", "city": "وهران", "price": "2000000", "phone": ""}
]

@app.route("/", methods=["GET", "POST"])
def home():
    message = ""

    if request.method == "POST":
        name = request.form.get("name", "").strip()
        year = request.form.get("year", "").strip()
        city = request.form.get("city", "").strip()
        price = request.form.get("price", "").strip()
        phone = request.form.get("phone", "").strip()

        if name and year and city and price and phone:
            cars.insert(0, {
                "name": name, "year": year, "city": city,
                "price": price, "phone": phone
            })
            message = "تمت إضافة إعلانك بنجاح!"
        else:
            message = "يرجى ملء جميع الخانات."

    cards = ""
    for car in cars:
        cards += f"""
        <section class="card">
            <h3>{escape(car['name'])}</h3>
            <p>📅 السنة: {escape(car['year'])}</p>
            <p>📍 الولاية: {escape(car['city'])}</p>
            <p class="price">{escape(car['price'])} دج</p>
            <p>{'📞 ' + escape(car['phone']) if car['phone'] else 'إعلان تجريبي'}</p>
        </section>
        """

    return f"""
    <!DOCTYPE html>
    <html lang="ar" dir="rtl">
    <head>
    <meta name="google-site-verification" content="21yc-t0xU1MFJINwGsWZQjsgjVJwoS8nYO2C2gT_PVU" />
      <meta charset="UTF-8">
      <meta name="viewport" content="width=device-width, initial-scale=1">
      <title>سيارات الجزائر</title>
      <style>
        body {{ margin:0; font-family:Arial,sans-serif; background:#f2f4f7; color:#222; }}
        header {{ background:#087443; color:white; padding:25px 15px; text-align:center; }}
        main {{ padding:18px; max-width:650px; margin:auto; }}
        .card,.formbox {{ background:white; border-radius:14px; padding:18px; margin-bottom:16px; }}
        h3 {{ color:#087443; }}
        .price {{ font-size:21px; font-weight:bold; }}
        input {{ box-sizing:border-box; width:100%; padding:12px; margin:7px 0 14px; border:1px solid #ccc; border-radius:8px; font-size:16px; }}
        button {{ background:#087443; color:white; border:0; padding:12px 18px; border-radius:8px; font-size:16px; width:100%; }}
        label {{ font-weight:bold; }}
      </style>
    </head>
    <body>
      <header><h1>🚗 سيارات الجزائر 🇩🇿</h1><p>ابحث عن سيارتك القادمة</p></header>
      <main>
        <section class="formbox">
          <h2>أضف سيارتك للبيع</h2>
          <p>{message}</p>
          <form method="POST">
            <label>اسم السيارة والموديل</label>
           

<label>منشأ السيارة</label>
<select name="origin" required>
<option value="أوروبية">أوروبية</option>
<option value="ألمانية">ألمانية</option>
<option value="صينية">صينية</option>
<option value="كورية">كورية</option>
<option value="يابانية">يابانية</option>
<option value="أخرى">أخرى</option>
</select>
 <input name="name" placeholder="مثال: Renault Clio 4" required>
            <label>سنة الصنع</label>
            <input name="year" type="number" min="1950" max="2027" placeholder="2020" required>
            <label>الولاية</label>
            <input name="city" placeholder="مثال: أدرار" required>
            <label>السعر بالدينار الجزائري</label>
            <input name="price" type="number" min="1" placeholder="1800000" required>
            <label>رقم هاتف البائع</label>
            <input name="phone" type="tel" placeholder="رقم للتواصل" required>
            <button type="submit">نشر الإعلان</button>
          </form>
        </section>
        <h2>سيارات معروضة</h2>
        {cards}
        <p>الإعلانات المضافة الآن مؤقتة، وقد تختفي عند إعادة تشغيل الخادم.</p>
      </main>
    </body>
    </html>
    """

if __name__ == "__main__":
    app.run(host="127.0.0.1", port=5000, debug=False)
