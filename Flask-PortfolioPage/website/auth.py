import datetime
import os

from flask import (Blueprint, abort, flash, redirect, render_template, request,
                   session, url_for)
from flask_login import current_user, login_required, login_user, logout_user
from flask_mail import Message
from itsdangerous import URLSafeTimedSerializer
from werkzeug.security import check_password_hash, generate_password_hash

from . import db, mail
from .models import User

auth = Blueprint("auth", __name__)
ts_secret_key = os.getenv("TS_SECRET_KEY")
ts = URLSafeTimedSerializer(ts_secret_key)


@auth.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        email = request.form.get("email")
        password = request.form.get("password")
        keep_or_not = request.form.get("keepLoggedIn")

        user = User.query.filter_by(email=email).first()
        if user:
            if user.email_confirmed:
                if (
                    check_password_hash(user.password, password)
                    and user.email_confirmed
                ):
                    session.permanent = True
                    if keep_or_not == "keepLoggedIn":
                        flash("Logged in successfully!", category="success")
                        session.permanent = True
                        login_user(user, remember=True)
                        session.permanent = True
                    else:
                        flash(
                            "Logged in successfully! You will be automatically logged out after 10 minutes of inactivity or when you leave the TI section.",
                            category="success",
                        )
                        session.permanent = True
                        login_user(user)
                        session.permanent = True

                    return redirect(url_for("views.ti_wallet"))
                else:
                    flash("Incorrect password, try again.", category="error")
            else:
                flash(
                    "Your email is not confirmed."
                    " A confirmation link has been sent to the email address you provided during registration. "
                    "Follow the link to complete your account registration.",
                    category="error",
                )
                send_confirmation_email(email)

        else:
            flash("Email does not exist.", category="error")

    return render_template("login.html", user=current_user)


@auth.route("/logout")
@login_required
def logout():
    logout_user()
    return redirect(url_for("auth.login"))


@auth.route("/sign-up", methods=["GET", "POST"])
def sign_up():
    if request.method == "POST":
        email = request.form.get("email")
        first_name = request.form.get("firstName")
        password1 = request.form.get("password1")
        password2 = request.form.get("password2")

        user = User.query.filter_by(email=email).first()
        if user:
            flash("Email already exists.", category="error")
        elif len(email) < 4:
            flash("Email must be greater than 3 characters.", category="error")
        elif len(first_name) < 2:
            flash("First name must be greater than 1 character.", category="error")
        elif password1 != password2:
            flash("Passwords don't match.", category="error")
        elif len(password1) < 7:
            flash("Password must be at least 7 characters.", category="error")
        else:
            try:
                send_confirmation_email(email)
                new_user = User(
                    email=email,
                    first_name=first_name,
                    password=generate_password_hash(password1, method="sha256"),
                )
                db.session.add(new_user)
                db.session.commit()
                flash(
                    "A confirmation link has been sent to the email address you provided during registration. "
                    "Follow the link to complete your account registration.",
                    category="info",
                )
            except:
                flash(
                    "An error occurred while creating your account. Please try again later.",
                    category="error",
                )

            return redirect(url_for("auth.login"))

    return render_template("sign_up.html", user=current_user)


def send_confirmation_email(email):
    token = ts.dumps(email, salt="email-confirm-key")
    msg = Message(
        "TI: Confirm your email",
        sender=("Treasure Island", "ti.treasureisland.mail@gmail.com"),
        recipients=[email],
    )
    msg.body = f"""To confirm your e-mail address, visit the following link:\n
{url_for('auth.confirm_email', token=token, _external=True)}\n
Link is only valid for 24 hours. \n
If you did not make this request then simply ignore this email and no changes will be made.
                """
    mail.send(msg)


def send_change_password_email(email):
    token = ts.dumps(email, salt="email-confirm-key")
    msg = Message(
        "TI: Change password",
        sender=("Treasure Island", "ti.treasureisland.mail@gmail.com"),
        recipients=[email],
    )
    msg.body = f"""To change password to your TI account, visit the following link:\n
{url_for('auth.reset_token', token=token, _external=True)}\n
Link is only valid for 24 hours. \n
If you did not make this request then simply ignore this email and no changes will be made.
                """
    mail.send(msg)


@auth.route("/reset_password", methods=["GET", "POST"])
def reset_request():
    if current_user.is_authenticated:
        try:
            send_change_password_email(email=current_user.email)
            flash(
                "An email has been sent with instructions to reset your password.",
                "info",
            )
        except:
            flash(
                "An error occurred while sending a password change request. Please try again later.",
                "error",
            )
        return redirect(url_for("views.ti_wallet"))
    else:
        if request.method == "POST":
            email = request.form.get("emailResetPass")

            user = User.query.filter_by(email=email).first()
            if not user:
                flash("Email does not exists in TI.", category="error")
            else:
                try:
                    send_change_password_email(user.email)
                    flash(
                        "An email has been sent with instructions to reset your password.",
                        "info",
                    )
                except:
                    flash(
                        "An error occurred while sending a password change request. Please try again later.",
                        "error",
                    )

                return redirect(url_for("auth.login"))

        return render_template(
            "reset_password_request.html", title="Reset Password", user=current_user
        )


@auth.route("/reset_password/<token>", methods=["GET", "POST"])
def reset_token(token):
    session.clear()

    try:
        email = ts.loads(token, salt="email-confirm-key", max_age=86400)
    except:
        abort(404)

    user = User.query.filter_by(email=email).first_or_404()
    if request.method == "POST":
        password1 = request.form.get("newPassword1")
        password2 = request.form.get("newPassword2")

        user = User.query.filter_by(email=email).first()

        if password1 != password2:
            flash("Passwords don't match.", category="error")
        elif len(password1) < 7:
            flash("Password must be at least 7 characters.", category="error")
        else:
            new_password = generate_password_hash(password1, method="sha256")
            user.password = new_password
            db.session.commit()
            flash("Your password has been changed.", category="info")
            return redirect(url_for("auth.login"))

    return render_template(
        "change_password.html", title="Change Password", user=current_user
    )


@auth.route("/confirm/<token>")
def confirm_email(token):
    try:
        email = ts.loads(token, salt="email-confirm-key", max_age=86400)
    except:
        abort(404)

    user = User.query.filter_by(email=email).first_or_404()

    user.email_confirmed = True

    db.session.add(user)
    db.session.commit()
    flash("You confirmed your e-mail, now you can login to TI!")

    return redirect(url_for("auth.login"))


@auth.context_processor
def inject_now():
    return {"now": datetime.datetime.utcnow()}
