from flask import render_template, request, url_for, redirect, Blueprint, session
import sqlite3

from app import app

auth = Blueprint('auth', __name__)

@auth.before_request
def auth_middleware():
    if request.path==url_for("auth.logout"):
        return
    if "username" in session:
        return redirect(url_for("dashboard.index"))

@auth.route("/admin/login", methods=['GET', 'POST'])
def login():
    admin_credentials = app.config["ADMIN"]
    error = {
        "message" : ""
    }
    if request.method=="POST":
        username = request.form.get("username")
        password = request.form.get("password")

        if(admin_credentials["username"]==username and admin_credentials["password"]==password):
            session['username'] = username
            session['auth'] = "Y"
            session['role'] = "admin"
            return redirect(url_for("dashboard.index"))
        else:
            error["message"] = "Invalid credentials"
    return render_template("login.html", error=error)

@auth.route("/logout", methods=['GET', 'POST'])
def logout():
    session.clear()
    return redirect(url_for("auth.user_login"))

@auth.route("/login", methods=['GET', 'POST'])
def user_login():
    error = {
        "message" : ""
    }
    if request.method=="POST":
        username = request.form.get("username")
        password = request.form.get("password")
        try:
            conn = sqlite3.connect(app.config["SQL"])
            cursor = conn.cursor()
            sql = f'SELECT * FROM users WHERE username="{username}"'
            cursor.execute(sql)
            users = cursor.fetchall()
            if(len(users) > 0):
                if(users[0][2]==password):
                    session['username'] = username
                    session['auth'] = "Y"
                    session['role'] = "user"
                    return redirect(url_for("dashboard.index"))
                else:
                    error["message"] = "Invalid credentials"
            else:
                error["message"] = "User not found"
        except Exception as err:
            error["message"] = "Something went wrong"
    return render_template("login.html", error=error)