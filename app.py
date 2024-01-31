import os
import random
import threading
import pytz
from flask import (
    Flask,
    render_template,
    request,
    flash,
    session,
    redirect,
    url_for,
    send_file,
)
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
from flask_mail import Mail, Message
from passlib.hash import sha256_crypt


EMAIL_DOMAIN = "@gmail.com"
UPLOAD_FOLDER = "./static/pdf/"
ALLOWED_EXTENSIONS = {"pdf"}

current_dir = os.path.abspath(os.path.dirname(__file__))
app = Flask(__name__)
app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///" + os.path.join(
    current_dir, "database.db"
)
app.config["UPLOAD_FOLDER"] = UPLOAD_FOLDER
app.config["DEBUG"] = True
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
app.config["SECRET_KEY"] = "qsrZ2bsRXDjMpvltRw5i7WxPZSWBi2C6p-1lz6Ce-NA"
app.config["MAIL_SERVER"] = "smtp.gmail.com"
app.config["MAIL_PORT"] = 587
app.config["MAIL_USERNAME"] = "shakthiraja5@gmail.com"
app.config["MAIL_PASSWORD"] = "ncbe tckf eels gpdl"
app.config["MAIL_USE_TLS"] = True
app.config["MAIL_USE_SSL"] = False

mail = Mail(app)
db = SQLAlchemy(app)


def get_current_time():
    return datetime.now(pytz.timezone("Asia/Kolkata"))


def send_email(subject, body, recipients, user_name, otp):
    with app.app_context():
        try:
            msg = Message(
                subject=subject,
                sender=app.config["MAIL_USERNAME"],
                recipients=recipients,
            )
            msg.html = render_template(
                "email_template.html", body=body, user_name=user_name, otp=otp
            )
            mail.send(msg)
            print("Email sent successfully.")
        except Exception as e:
            print(f"Error sending verification code: {e}")


def allowed_file(filename):
    return "." in filename and filename.rsplit(".", 1)[1].lower() in ALLOWED_EXTENSIONS


def generate_application_id():
    # Query the database for the latest application number
    latest_application = Application.query.order_by(
        Application.application_id.desc()
    ).first()
    if latest_application:
        new_application_id = latest_application.application_id + 1
    else:
        # If no applications exist, start from 1
        new_application_id = 1
    return new_application_id


class User(db.Model):
    __tablename__ = "user"
    user_id = db.Column(db.Integer, autoincrement=True, primary_key=True)
    user_name = db.Column(db.String, nullable=False)
    user_email = db.Column(db.String, unique=True, nullable=False)
    user_designation = db.Column(db.String, nullable=False)
    user_department = db.Column(db.String, nullable=False)
    user_password = db.Column(db.String, nullable=False)


class Admin(db.Model):
    __tablename__ = "admin"
    admin_id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    admin_email = db.Column(db.String, unique=True, nullable=False)
    admin_phone_no = db.Column(db.Integer, nullable=False)
    admin_name = db.Column(db.String, nullable=False)
    admin_password = db.Column(db.String, nullable=False)


class Application(db.Model):
    __tablename__ = "application"
    application_id = db.Column(db.Integer, autoincrement=True, primary_key=True)
    submitted_at = db.Column(db.DateTime, default=get_current_time)
    processed_at = db.Column(db.DateTime)
    application_email = db.Column(db.String, nullable=False)
    applicant_name = db.Column(db.String, nullable=False)
    applicant_dept = db.Column(db.String, nullable=False)
    paper_title = db.Column(db.String, nullable=False)
    journal_name = db.Column(db.String, nullable=False)
    sjr_website_link = db.Column(db.String, nullable=False)
    publication_month = db.Column(db.String, nullable=False)
    doi = db.Column(db.String, nullable=False)
    journal_category = db.Column(db.String, nullable=False)
    coverage_from = db.Column(db.String, nullable=False)
    coverage_to = db.Column(db.String, nullable=False)
    first_author_name = db.Column(db.String, nullable=False)
    first_author_category = db.Column(db.String, nullable=False)
    second_author_name = db.Column(db.String)
    second_author_category = db.Column(db.String)
    third_author_name = db.Column(db.String)
    third_author_category = db.Column(db.String)
    published_paper_pdf_filename = db.Column(db.String, nullable=False)
    application_status = db.Column(db.String, default="Pending")
    first_author_amount = db.Column(db.String)
    second_author_amount = db.Column(db.String)
    third_author_amount = db.Column(db.String)
    comments = db.Column(db.String)


with app.app_context():
    db.create_all()

# with app.app_context():
#     new_admin = Admin(
#         admin_email="shakthiraja5@gmail.com",
#         admin_phone_no=9071046425,
#         admin_name="Shakthi Raja",
#         admin_password=sha256_crypt.hash("abcd"),
#     )
#     db.session.add(new_admin)
#     db.session.commit()


@app.route("/", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        user_email = str(request.form["user_email"]) + EMAIL_DOMAIN
        user_password = request.form["user_password"]
        user_logged = User.query.filter_by(user_email=user_email).first()
        if user_logged:
            if sha256_crypt.verify(user_password, user_logged.user_password):
                session["user_email"] = user_email
                flash("Logged in Successfully!", "success")
                return redirect(url_for("application_form_1"))
            else:
                flash(
                    "The password you entered is incorrect. Please double-check and try again.",
                    "error",
                )
                return redirect(url_for("login"))
        else:
            flash(
                "The email address you entered is incorrect. Please double-check and try again",
                "error",
            )
            return redirect(url_for("login"))

    if "user_email" in session:
        flash("Logged in Successfully!", "success")
        return redirect(url_for("application_form_1"))
    else:
        return render_template("login.html", email_domain=EMAIL_DOMAIN)


@app.route("/signup", methods=["GET", "POST"])
def sign_up():
    if request.method == "POST":
        session["user_name"] = request.form["user_name"]
        session["sign_up_user_email"] = str(request.form["user_email"]) + EMAIL_DOMAIN
        session["user_designation"] = request.form["user_designation"]
        session["user_department"] = request.form["user_department"]
        session["user_password"] = sha256_crypt.hash(request.form["user_password"])
        session["otp"] = str(random.randint(100000, 999999))
        user_logged = User.query.filter_by(
            user_email=session["sign_up_user_email"]
        ).first()
        if user_logged:
            flash(
                "This email is already in use. Please choose a different one or log in with your existing account.",
                "warn",
            )
            return redirect(url_for("sign_up"))
        else:
            try:
                subject = "Confirm account creation | MSRIT"
                body = "Use the following OTP to complete the procedure to verify your email address. Do not share this code with others."
                recipients = [session["sign_up_user_email"]]
                email_thread = threading.Thread(
                    target=send_email,
                    args=(
                        subject,
                        body,
                        recipients,
                        session["user_name"],
                        session["otp"],
                    ),
                )
                email_thread.start()
                return redirect(url_for("verify_signup"))
            except Exception as e:
                print(f"Error starting thread: {e}")

    return render_template("signup.html", email_domain=EMAIL_DOMAIN)


@app.route("/verify-signup", methods=["GET", "POST"])
def verify_signup():
    if request.method == "POST":
        entered_code = request.form["otp"]
        if entered_code == session["otp"]:
            new_user = User(
                user_name=session.pop("user_name", None),
                user_email=session["sign_up_user_email"],
                user_designation=session.pop("user_designation", None),
                user_department=session.pop("user_department", None),
                user_password=session.pop("user_password", None),
            )
            session.pop("otp", None)
            session["user_email"] = session.pop("sign_up_user_email", None)
            db.session.add(new_user)
            db.session.commit()
            flash("Account Created Successfully!", "success")
            return redirect(url_for("application_form_1"))
        else:
            flash(
                "The OTP you entered is incorrect. Please double-check and try again.",
                "error",
            )
            return redirect(url_for("verify_signup"))

    if "sign_up_user_email" in session:
        return render_template("account_verification.html")
    else:
        flash("Email not found, please try again.", "warn")
        return redirect(url_for("login"))


@app.route("/forgot-password", methods=["GET", "POST"])
def forgot_password():
    if request.method == "POST":
        user_email = str(request.form["user_email"]) + EMAIL_DOMAIN
        user_logged = User.query.filter_by(user_email=user_email).first()
        if user_logged:
            try:
                session["otp_forgot_password"] = str(random.randint(100000, 999999))
                subject = "Account verification | MSRIT"
                recipients = [user_email]
                body = "Use the following OTP to complete the procedure to verify your email address. Do not share this code with others."
                email_thread = threading.Thread(
                    target=send_email,
                    args=(
                        subject,
                        body,
                        recipients,
                        user_logged.user_name,
                        session["otp_forgot_password"],
                    ),
                )
                email_thread.start()
                session["forgot_password_user_email"] = user_email
                return redirect(url_for("verify_forgot_password"))
            except Exception as e:
                print(f"Error starting thread: {e}")
        else:
            flash(
                "This email does not exists. Please choose a different one or signup with a new account.",
                "warn",
            )
            return redirect(url_for("forgot_password"))

    return render_template("forgot-password.html", email_domain=EMAIL_DOMAIN)


@app.route("/verify-forgot-password", methods=["GET", "POST"])
def verify_forgot_password():
    if request.method == "POST":
        entered_code = request.form["otp"]
        if entered_code == session["otp_forgot_password"]:
            session.pop("otp_forgot_password", None)
            session["forgot_password_user_email_final"] = session.pop(
                "forgot_password_user_email", None
            )
            return redirect(url_for("forgot_password_final"))
        else:
            flash(
                "The OTP you entered is incorrect. Please double-check and try again.",
                "error",
            )
            return redirect(url_for("verify_forgot_password"))

    if "forgot_password_user_email" in session:
        return render_template("account_verification.html")
    else:
        flash("Email not found, please try again.", "warn")
        return redirect(url_for("login"))


@app.route("/forgot-password-final", methods=["GET", "POST"])
def forgot_password_final():
    if request.method == "POST":
        user_obj = User.query.filter_by(
            user_email=session["forgot_password_user_email_final"]
        ).first()
        user_obj.user_password = sha256_crypt.hash(request.form["user_password"])
        db.session.commit()
        session.pop("forgot_password_user_email_final", None)
        flash(
            "Your password has been successfully changed. You can now login with your new password!",
            "success",
        )
        return redirect(url_for("login"))

    if "forgot_password_user_email_final" in session:
        return render_template(
            "forgot-password_final.html",
            user_email=session["forgot_password_user_email_final"],
        )
    else:
        flash("Email not found, please try again.", "warn")
        return redirect(url_for("login"))


@app.route("/application/form/1", methods=["GET", "POST"])
def application_form_1():
    if request.method == "POST":
        applicant_name = request.form["applicant_name"]
        applicant_dept = request.form["applicant_dept"]
        paper_title = request.form["paper_title"]
        journal_name = request.form["journal_name"]
        sjr_website_link = request.form["sjr_website_link"]
        publication_month = request.form["publication_month"]
        doi = request.form["doi"]
        journal_category = request.form["journal_category"]
        coverage_from = request.form["coverage_from"]
        coverage_to = request.form["coverage_to"]

        session["application_info"] = {
            "applicant_name": applicant_name,
            "applicant_dept": applicant_dept,
            "paper_title": paper_title,
            "journal_name": journal_name,
            "sjr_website_link": sjr_website_link,
            "publication_month": publication_month,
            "doi": doi,
            "journal_category": journal_category,
            "coverage_from": coverage_from,
            "coverage_to": coverage_to,
        }
        return redirect(url_for("application_form_2"))

    if "user_email" in session:
        return render_template("application1.html")
    else:
        flash("Login Required!", "warn")
        return redirect(url_for("login"))


# New route for the second step
@app.route("/application/form/2", methods=["GET", "POST"])
def application_form_2():
    if request.method == "POST":
        first_author_name = request.form.get("first_author_name", "")
        first_author_category = request.form.get("first_author_category", "")
        second_author_name = request.form.get("second_author_name", "")
        second_author_category = request.form.get("second_author_category", "")
        third_author_name = request.form.get("third_author_name", "")
        third_author_category = request.form.get("third_author_category", "")
        # check if the post request has the file part
        if "file" not in request.files:
            flash("No file uploaded", "error")
            return redirect(url_for("application_form_2"))
        file = request.files["file"]
        # If the user does not select a file, the browser submits an
        # empty file without a filename.
        if file.filename == "":
            flash("No selected file", "error")
            return redirect(url_for("application_form_2"))
        if file and allowed_file(file.filename):
            # Generate application number
            application_id = generate_application_id()
            filename = f"appl_{application_id}.pdf"
            file.save(os.path.join(current_dir, app.config["UPLOAD_FOLDER"], filename))
        else:
            flash("Only '.pdf' format is allowed", "error")
            return redirect(url_for("application_form_2"))
        application_info = session.pop("application_info", None)
        new_application = Application(
            application_email=session["user_email"],
            applicant_name=application_info.get("applicant_name"),
            applicant_dept=application_info.get("applicant_dept"),
            paper_title=application_info.get("paper_title"),
            journal_name=application_info.get("journal_name"),
            sjr_website_link=application_info.get("sjr_website_link"),
            publication_month=application_info.get("publication_month"),
            doi=application_info.get("doi"),
            journal_category=application_info.get("journal_category"),
            coverage_from=application_info.get("coverage_from"),
            coverage_to=application_info.get("coverage_to"),
            first_author_name=first_author_name,
            first_author_category=first_author_category,
            second_author_name=second_author_name,
            second_author_category=second_author_category,
            third_author_name=third_author_name,
            third_author_category=third_author_category,
            published_paper_pdf_filename=filename,
        )
        db.session.add(new_application)
        db.session.commit()
        flash(
            "You have successfully submitted your application.",
            "success",
        )
        return render_template("application_submitted.html")

    if "user_email" in session:
        if "application_info" in session:
            return render_template("application2.html")
        else:
            flash("Application not found! Please fill the first application.", "warn")
            return redirect(url_for("application_form_1"))
    else:
        flash("Login Required!", "warn")
        return redirect(url_for("login"))


@app.route("/download-pdf/<filename>")
def download_pdf(filename):
    file_path = app.config["UPLOAD_FOLDER"] + filename
    return send_file(file_path)


@app.route("/application/status", methods=["GET", "POST"])
def application_status():
    if request.method == "GET":
        all_appls = Application.query.filter_by(
            application_email=session["user_email"]
        ).all()
        if all_appls:
            L = []
            for appl in all_appls:
                dictt = {
                    "application_id": 0,
                    "applicant_name": 0,
                    "applicant_dept": 0,
                    "paper_title": 0,
                    "journal_name": 0,
                    "status": 0,
                }
                dictt["application_id"] = appl.application_id
                dictt["applicant_name"] = appl.applicant_name
                dictt["applicant_dept"] = appl.applicant_dept
                dictt["paper_title"] = appl.paper_title
                dictt["journal_name"] = appl.journal_name
                dictt["status"] = appl.application_status
                L.append(dictt)
            return render_template("application_status.html", L=L)

        if "user_email" in session:
            return render_template("no_applications.html")
        else:
            return redirect(url_for("login"))


@app.route("/application/details/<application_id>", methods=["GET", "POST"])
def application_details(application_id):
    if request.method == "GET":
        appl = Application.query.filter_by(application_id=application_id).first()
        if "user_email" in session:
            if appl:
                dictt = {
                    "application_id": 0,
                    "applicant_name": 0,
                    "applicant_dept": 0,
                    "paper_title": 0,
                    "journal_name": 0,
                    "sjr_website_link": 0,
                    "publication_month": 0,
                    "doi": 0,
                    "journal_category": 0,
                    "coverage_from": 0,
                    "coverage_to": 0,
                    "first_author_name": 0,
                    "first_author_category": 0,
                    "second_author_name": 0,
                    "second_author_category": 0,
                    "third_author_name": 0,
                    "third_author_category": 0,
                    "published_paper_pdf_filename": 0,
                    "status": 0,
                }
                dictt["application_id"] = appl.application_id
                dictt["submitted_at"] = appl.submitted_at
                dictt["applicant_name"] = appl.applicant_name
                dictt["applicant_dept"] = appl.applicant_dept
                dictt["paper_title"] = appl.paper_title
                dictt["journal_name"] = appl.journal_name
                dictt["sjr_website_link"] = appl.sjr_website_link
                dictt["publication_month"] = appl.publication_month
                dictt["doi"] = appl.doi
                dictt["journal_category"] = appl.journal_category
                dictt["coverage_from"] = appl.coverage_from
                dictt["coverage_to"] = appl.coverage_to
                dictt["first_author_name"] = appl.first_author_name
                dictt["first_author_category"] = appl.first_author_category
                dictt["second_author_name"] = appl.second_author_name
                dictt["second_author_category"] = appl.second_author_category
                dictt["third_author_name"] = appl.third_author_name
                dictt["third_author_category"] = appl.third_author_category
                dictt[
                    "published_paper_pdf_filename"
                ] = appl.published_paper_pdf_filename
                dictt["first_author_amount"] = appl.first_author_amount
                dictt["second_author_amount"] = appl.second_author_amount
                dictt["third_author_amount"] = appl.third_author_amount
                dictt["processed_at"] = appl.processed_at
                dictt["comments"] = appl.comments
                dictt["status"] = appl.application_status
                return render_template(
                    "application_details.html",
                    dictt=dictt,
                    filename=appl.published_paper_pdf_filename,
                )
            else:
                return render_template("no_applications.html")
        else:
            flash("Login Required!", "warn")
            return redirect(url_for("login"))


@app.route("/admin/login", methods=["GET", "POST"])
def admin_login():
    if request.method == "POST":
        admin_email = request.form["admin_email"]
        admin_password = request.form["admin_password"]
        admin_logged = Admin.query.filter_by(admin_email=admin_email).first()
        if admin_logged:
            if sha256_crypt.verify(admin_password, admin_logged.admin_password):
                session["admin_email"] = admin_email
                flash("Logged in Successfully!", "success")
                return redirect(url_for("admin_home"))
            else:
                flash(
                    "The password you entered is incorrect. Please double-check and try again.",
                    "error",
                )
                return redirect(url_for("admin_login"))
        else:
            flash(
                "The email address you entered is incorrect. Please double-check and try again",
                "error",
            )
            return redirect(url_for("admin_login"))

    if "admin_email" in session:
        flash("Logged in Successfully!", "success")
        return redirect(url_for("admin_home"))
    else:
        return render_template("admin_login.html")


@app.route("/admin/forgot-password", methods=["GET", "POST"])
def admin_forgot_password():
    if request.method == "POST":
        admin_email = str(request.form["admin_email"])
        admin_logged = Admin.query.filter_by(admin_email=admin_email).first()
        print(admin_logged)
        if admin_logged:
            try:
                session["admin_otp_forgot_password"] = str(
                    random.randint(100000, 999999)
                )
                subject = "Account verification | MSRIT"
                recipients = [admin_email]
                body = "Use the following OTP to complete the procedure to verify your email address. Do not share this code with others."
                email_thread = threading.Thread(
                    target=send_email,
                    args=(
                        subject,
                        body,
                        recipients,
                        admin_logged.admin_name,
                        session["admin_otp_forgot_password"],
                    ),
                )
                email_thread.start()
                session["forgot_password_admin_email"] = admin_email
                return redirect(url_for("admin_verify_forgot_password"))
            except Exception as e:
                print(f"Error starting thread: {e}")
        else:
            flash(
                "This email does not exists. Please choose a different one or signup with a new account.",
                "warn",
            )
            return redirect(url_for("admin_forgot_password"))

    return render_template("admin_forgot-password.html")


@app.route("/admin/verify-forgot-password", methods=["GET", "POST"])
def admin_verify_forgot_password():
    if request.method == "POST":
        entered_code = request.form["otp"]
        if entered_code == session["admin_otp_forgot_password"]:
            session.pop("otp_forgot_password", None)
            session["forgot_password_admin_email_final"] = session.pop(
                "forgot_password_admin_email", None
            )
            return redirect(url_for("admin_forgot_password_final"))
        else:
            flash(
                "The OTP you entered is incorrect. Please double-check and try again.",
                "error",
            )
            return redirect(url_for("admin_verify_forgot_password"))

    if "forgot_password_admin_email" in session:
        return render_template("account_verification.html")
    else:
        flash("Email not found, please try again.", "warn")
        return redirect(url_for("admin_login"))


@app.route("/admin/forgot-password-final", methods=["GET", "POST"])
def admin_forgot_password_final():
    if request.method == "POST":
        admin_obj = Admin.query.filter_by(
            admin_email=session["forgot_password_admin_email_final"]
        ).first()
        admin_obj.admin_password = sha256_crypt.hash(request.form["user_password"])
        db.session.commit()
        session.pop("forgot_password_admin_email_final", None)
        flash(
            "Your password has been successfully changed. You can now login with your new password!",
            "success",
        )
        return redirect(url_for("admin_login"))

    if "forgot_password_admin_email_final" in session:
        return render_template(
            "forgot-password_final.html",
            user_email=session["forgot_password_admin_email_final"],
        )
    else:
        flash("Email not found, please try again.", "warn")
        return redirect(url_for("admin_login"))


@app.route("/admin/home/pending-applications", methods=["GET", "POST"])
def admin_home():
    if request.method == "GET":
        if "admin_email" in session:
            all_appls = Application.query.filter_by(application_status="Pending").all()
            L = []
            for appl in all_appls:
                dictt = {
                    "application_id": 0,
                    "applicant_name": 0,
                    "applicant_dept": 0,
                    "paper_title": 0,
                    "journal_name": 0,
                    "status": 0,
                }
                dictt["application_id"] = appl.application_id
                dictt["applicant_name"] = appl.applicant_name
                dictt["applicant_dept"] = appl.applicant_dept
                dictt["paper_title"] = appl.paper_title
                dictt["journal_name"] = appl.journal_name
                dictt["status"] = appl.application_status
                L.append(dictt)
            return render_template("admin_home_pending.html", L=L)
        else:
            flash("Login Required!", "warn")
            return redirect(url_for("admin_login"))


@app.route("/admin/processed-applications", methods=["GET", "POST"])
def admin_processed_applications():
    if request.method == "GET":
        if "admin_email" in session:
            all_appls = Application.query.filter_by(
                application_status="Processed"
            ).all()
            L = []
            for appl in all_appls:
                dictt = {
                    "application_id": 0,
                    "applicant_name": 0,
                    "applicant_dept": 0,
                    "paper_title": 0,
                    "journal_name": 0,
                    "status": 0,
                }
                dictt["application_id"] = appl.application_id
                dictt["applicant_name"] = appl.applicant_name
                dictt["applicant_dept"] = appl.applicant_dept
                dictt["paper_title"] = appl.paper_title
                dictt["journal_name"] = appl.journal_name
                dictt["status"] = appl.application_status
                L.append(dictt)
            return render_template("admin_home_processed.html", L=L)
        else:
            flash("Login Required!", "warn")
            return redirect(url_for("admin_login"))


@app.route(
    "/admin/pending-application/details/<application_id>", methods=["GET", "POST"]
)
def admin_pending_application_details(application_id):
    if request.method == "POST":
        appl = Application.query.get(application_id)
        first_author_amount = request.form.get("first_author_amount")
        second_author_amount = request.form.get("second_author_amount")
        third_author_amount = request.form.get("third_author_amount")
        comments = request.form.get("comments", "-")
        if first_author_amount:
            appl.first_author_amount = first_author_amount
        if second_author_amount:
            appl.first_author_amount = second_author_amount
        if third_author_amount:
            appl.first_author_amount = third_author_amount
        appl.processed_at = get_current_time()
        appl.application_status = "Processed"
        appl.comments = comments
        db.session.commit()
        return redirect(url_for("admin_processed_applications"))

    if "admin_email" in session:
        appl = Application.query.filter_by(application_id=application_id).first()
        if appl:
            dictt = {
                "application_id": 0,
                "applicant_name": 0,
                "applicant_dept": 0,
                "paper_title": 0,
                "journal_name": 0,
                "sjr_website_link": 0,
                "publication_month": 0,
                "doi": 0,
                "journal_category": 0,
                "coverage_from": 0,
                "coverage_to": 0,
                "first_author_name": 0,
                "first_author_category": 0,
                "second_author_name": 0,
                "second_author_category": 0,
                "third_author_name": 0,
                "third_author_category": 0,
                "published_paper_pdf_filename": 0,
                "status": 0,
            }
            dictt["application_id"] = appl.application_id
            dictt["submitted_at"] = appl.submitted_at
            dictt["applicant_name"] = appl.applicant_name
            dictt["applicant_dept"] = appl.applicant_dept
            dictt["paper_title"] = appl.paper_title
            dictt["journal_name"] = appl.journal_name
            dictt["sjr_website_link"] = appl.sjr_website_link
            dictt["publication_month"] = appl.publication_month
            dictt["doi"] = appl.doi
            dictt["journal_category"] = appl.journal_category
            dictt["coverage_from"] = appl.coverage_from
            dictt["coverage_to"] = appl.coverage_to
            dictt["first_author_name"] = appl.first_author_name
            dictt["first_author_category"] = appl.first_author_category
            dictt["second_author_name"] = appl.second_author_name
            dictt["second_author_category"] = appl.second_author_category
            dictt["third_author_name"] = appl.third_author_name
            dictt["third_author_category"] = appl.third_author_category
            dictt["published_paper_pdf_filename"] = appl.published_paper_pdf_filename
            dictt["status"] = appl.application_status
            return render_template(
                "admin_pending_application_details.html",
                dictt=dictt,
                filename=appl.published_paper_pdf_filename,
            )
        else:
            return render_template("admin_application_not_found.html")
    else:
        flash("Login Required!", "warn")
        return redirect(url_for("admin_login"))


@app.route(
    "/admin/processed-application/details/<application_id>", methods=["GET", "POST"]
)
def admin_processed_application_details(application_id):
    if request.method == "GET":
        if "admin_email" in session:
            appl = Application.query.filter_by(application_id=application_id).first()
            if appl:
                dictt = {
                    "application_id": 0,
                    "applicant_name": 0,
                    "applicant_dept": 0,
                    "paper_title": 0,
                    "journal_name": 0,
                    "sjr_website_link": 0,
                    "publication_month": 0,
                    "doi": 0,
                    "journal_category": 0,
                    "coverage_from": 0,
                    "coverage_to": 0,
                    "first_author_name": 0,
                    "first_author_category": 0,
                    "second_author_name": 0,
                    "second_author_category": 0,
                    "third_author_name": 0,
                    "third_author_category": 0,
                    "published_paper_pdf_filename": 0,
                    "status": 0,
                }
                dictt["application_id"] = appl.application_id
                dictt["submitted_at"] = appl.submitted_at
                dictt["applicant_name"] = appl.applicant_name
                dictt["applicant_dept"] = appl.applicant_dept
                dictt["paper_title"] = appl.paper_title
                dictt["journal_name"] = appl.journal_name
                dictt["sjr_website_link"] = appl.sjr_website_link
                dictt["publication_month"] = appl.publication_month
                dictt["doi"] = appl.doi
                dictt["journal_category"] = appl.journal_category
                dictt["coverage_from"] = appl.coverage_from
                dictt["coverage_to"] = appl.coverage_to
                dictt["first_author_name"] = appl.first_author_name
                dictt["first_author_category"] = appl.first_author_category
                dictt["second_author_name"] = appl.second_author_name
                dictt["second_author_category"] = appl.second_author_category
                dictt["third_author_name"] = appl.third_author_name
                dictt["third_author_category"] = appl.third_author_category
                dictt[
                    "published_paper_pdf_filename"
                ] = appl.published_paper_pdf_filename
                dictt["first_author_amount"] = appl.first_author_amount
                dictt["second_author_amount"] = appl.second_author_amount
                dictt["third_author_amount"] = appl.third_author_amount
                dictt["processed_at"] = appl.processed_at
                dictt["comments"] = appl.comments
                dictt["status"] = appl.application_status
                return render_template(
                    "admin_processed_application_details.html",
                    dictt=dictt,
                    filename=appl.published_paper_pdf_filename,
                )
            else:
                return render_template("admin_application_not_found.html")
        else:
            flash("Login Required!", "warn")
            return redirect(url_for("admin_login"))


@app.route("/logout", methods=["GET", "POST"])
def logout():
    if "user_email" in session:
        session.pop("user_email", None)
        flash("Logged out Successfully!", "success")
        return redirect(url_for("login"))
    else:
        flash("Login Required!", "warn")
        return redirect(url_for("login"))


@app.route("/admin/logout", methods=["GET", "POST"])
def admin_logout():
    if "admin_email" in session:
        session.pop("admin_email", None)
        flash("Logged out Successfully!", "success")
        return redirect(url_for("admin_login"))
    else:
        flash("Login Required!", "warn")
        return redirect(url_for("admin_login"))


if __name__ == "__main__":
    app.run(host="0.0.0.0")
