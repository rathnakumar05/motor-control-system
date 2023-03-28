from flask import render_template, request, url_for, redirect, Blueprint, jsonify, session
from datetime import datetime
import sqlite3

from app import app

users = Blueprint('users', __name__)

@users.before_request
def users_middleware():
    if not session.get("auth")=="Y":
        return redirect(url_for("auth.login"))
    if not session.get("role")=="admin":
        return redirect(url_for("dashboard.index"))        

@users.route("/users")
def index():
    users = []
    try:
        conn = sqlite3.connect(app.config["SQL"])
        cursor = conn.cursor()
        sql = f'SELECT * FROM users order by created_date desc'
        cursor.execute(sql)
        users = cursor.fetchall()
    except Exception as err:
        pass
    return render_template("users.html", users=users)

@users.route("/users/add", methods=["POST"])
def add():
    response = {
        "status" : "",
        "message" : "",
    }
    if request.method=="POST":
        username = request.form.get("username")
        password = request.form.get("password")
        message = ""
        error_flag = 0
        if(not (username!="" and len(username) > 2 and len(username) < 60)):
            error_flag = 1
            message = "Username is required and must be between 3 and 60 characters long. "
        if(not (password!="" and len(password) > 2 and len(password) < 60)):
            error_flag = 1
            message = message + "Password is required and must be between 3 and 60 characters long."

        if error_flag==1:
            response["status"] = "error"
            response["message"] = message
            return jsonify(response)
        else:
            try:
                conn = sqlite3.connect(app.config["SQL"])
                cursor = conn.cursor()
                sql = f'SELECT * FROM users WHERE username="{username}"'
                cursor.execute(sql)
                records = cursor.fetchall()
                if(not (len(records) > 0)):
                    sql = ''' INSERT INTO users(username, password, created_date, modified_date)
                             VALUES(?,?,datetime('now'),datetime('now')) '''
                    cursor.execute(sql, (username, password))
                    conn.commit()
                    response["status"] = "success"
                    response["message"] = "User added successfully"
                else:
                    response["status"] = "error"
                    response["message"] = f'user "{username}" already exist'
                conn.close()
            except Exception as err:
                print(err)
                response["status"] = "error"
                response["message"] = "Failed to add user"
    else:
        response["status"] = "error"
        response["message"] = "Failed to add user"
    return jsonify(response)


@users.route("/users/edit", methods=["POST"])
def edit():
    response = {
        "status" : "",
        "message" : "",
    }
    if request.method=="POST":
        username = request.form.get("username")
        password = request.form.get("password")

        message = ""
        error_flag = 0
        if(not (username!="" and len(username) > 2 and len(username) < 60)):
            error_flag = 1
            message = "Username is required and must be between 3 and 60 characters long. "
        if(not (password!="" and len(password) > 2 and len(password) < 60)):
            error_flag = 1
            message = message + "Password is required and must be between 3 and 60 characters long."

        if error_flag==1:
            response["status"] = "error"
            response["message"] = message
            return jsonify(response)
        else:
            try:
                conn = sqlite3.connect(app.config["SQL"])
                cursor = conn.cursor()
                sql = f'SELECT * FROM users WHERE username="{username}"'
                cursor.execute(sql)
                records = cursor.fetchall()
                if(len(records) > 0):
                    sql = '''UPDATE users SET password=?, modified_date=datetime('now') WHERE username=?'''
                    cursor.execute(sql, (password, username))
                    conn.commit()
                    response["status"] = "success"
                    response["message"] = "User updated successfully"
                else:
                    response["status"] = "error"
                    response["message"] = "User not found" 
                conn.close()
            except Exception as err:
                print(err)
                response["status"] = "error"
                response["message"] = "Failed to update user"
    else:
        response["status"] = "error"
        response["message"] = "Failed to update user"
    return jsonify(response)

@users.route("/users/delete/<username>", methods=["GET"])
def delete(username):
    try:
        conn = sqlite3.connect(app.config["SQL"])
        cursor = conn.cursor()
        sql = f'DELETE FROM users WHERE username="{username}"'
        cursor.execute(sql)
        conn.commit()
    except Exception as err:
        print(err)
        pass
    return redirect(url_for("users.index"))

    