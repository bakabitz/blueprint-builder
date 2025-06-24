from flask import Flask, render_template, request, url_for, send_file
from werkzeug.utils import secure_filename
import os, random
from xhtml2pdf import pisa
from io import BytesIO

app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = 'static/uploads'
os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)

categories = {
    "Vehicle": ["Chassis", "Engine", "Wheels", "Steering System", "Brakes"],
    "Building": ["Foundation", "Walls", "Roof", "Doors", "Windows"],
    "Weapon": ["Barrel", "Trigger", "Magazine", "Scope", "Stock"],
    "Jet": ["Fuselage", "Jet Engine", "Wings", "Landing Gear", "Cockpit"],
    "Phone": ["Screen", "Battery", "Camera", "Processor", "Casing"]
}

part_sources = [
    "https://www.aliexpress.com",
    "https://www.amazon.com",
    "https://www.alibaba.com",
    "https://www.ebay.com",
    "https://www.digikey.com"
]

@app.route("/")
def index():
    return render_template("index.html", categories=categories.keys())

@app.route("/blueprint", methods=["POST"])
def blueprint():
    category = request.form["category"]
    parts = categories.get(category, [])
    parts_with_links = [{"name": part, "link": random.choice(part_sources)} for part in parts]

    uploaded_image = request.files.get("custom_image")
    if uploaded_image and uploaded_image.filename != "":
        filename = secure_filename(uploaded_image.filename)
        path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        uploaded_image.save(path)
        image_path = url_for("static", filename=f"uploads/{filename}")
    else:
        image_path = url_for("static", filename=f"images/{category.lower()}.png")

    return render_template("blueprint.html", category=category, parts=parts_with_links, image=image_path)

@app.route("/download_pdf", methods=["POST"])
def download_pdf():
    category = request.form["category"]
    parts = categories.get(category, [])
    parts_with_links = [{"name": part, "link": random.choice(part_sources)} for part in parts]
    image_path = url_for("static", filename=f"images/{category.lower()}.png")

    html = render_template("pdf_template.html", category=category, parts=parts_with_links, image=image_path)

    pdf = BytesIO()
    pisa.CreatePDF(html, dest=pdf)
    pdf.seek(0)
    return send_file(pdf, mimetype='application/pdf', download_name=f'{category}_blueprint.pdf', as_attachment=True)

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=81)
