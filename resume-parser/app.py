"""
app.py

Small Flask web app: upload a resume (PDF/DOCX/TXT), see the parsed
fields rendered back in the browser. Run with:

    python app.py

Then open http://127.0.0.1:5000
"""

import os
from flask import Flask, render_template, request, flash, redirect, url_for
from werkzeug.utils import secure_filename

from resume_parser import parse_resume

ALLOWED_EXTENSIONS = {"pdf", "docx", "txt"}
UPLOAD_FOLDER = os.path.join(os.path.dirname(__file__), "uploads")
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

app = Flask(__name__)
app.config["UPLOAD_FOLDER"] = UPLOAD_FOLDER
app.config["MAX_CONTENT_LENGTH"] = 10 * 1024 * 1024  # 10 MB
app.secret_key = "dev-secret-key"  # replace before deploying publicly


def allowed_file(filename: str) -> bool:
    return "." in filename and filename.rsplit(".", 1)[1].lower() in ALLOWED_EXTENSIONS


@app.route("/", methods=["GET"])
def index():
    return render_template("index.html", result=None)


@app.route("/parse", methods=["POST"])
def parse():
    if "resume" not in request.files:
        flash("No file part in the request.")
        return redirect(url_for("index"))

    file = request.files["resume"]

    if file.filename == "":
        flash("No file selected.")
        return redirect(url_for("index"))

    if not allowed_file(file.filename):
        flash("Unsupported file type. Please upload a PDF, DOCX, or TXT file.")
        return redirect(url_for("index"))

    filename = secure_filename(file.filename)
    save_path = os.path.join(app.config["UPLOAD_FOLDER"], filename)
    file.save(save_path)

    try:
        result = parse_resume(save_path)
    except Exception as exc:
        flash(f"Couldn't parse that file: {exc}")
        return redirect(url_for("index"))
    finally:
        # Remove the uploaded file after parsing; nothing is retained on disk.
        if os.path.exists(save_path):
            os.remove(save_path)

    return render_template("index.html", result=result, filename=filename)


if __name__ == "__main__":
    app.run(debug=True)
