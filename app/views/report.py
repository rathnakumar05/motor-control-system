from flask import Blueprint, redirect, render_template, session, url_for, request, jsonify
import sqlite3
from datetime import datetime, timedelta
from time import mktime

from app import app

report = Blueprint('report', __name__)

@report.before_request
def report_middleware():
    if not session.get("auth")=="Y":
        return redirect(url_for("auth.login"))
    if not session.get("role")=="admin":
        return redirect(url_for("dashboard.index"))  
    
@report.route("/report", methods=["GET"])
def index():
    start_date = (datetime.now() - timedelta(days=30)).strftime("%Y-%m-%d")
    end_date = datetime.now().strftime("%Y-%m-%d")

    return render_template("report.html", start_date=start_date, end_date=end_date)

@report.route("/report/data", methods=["GET", "POST"])
def data():
    start_date = request.form.get("start_date")
    end_date = request.form.get("end_date")

    start_date = int(mktime(datetime.strptime(start_date, '%Y-%m-%d').timetuple()))
    end_date = int(mktime((datetime.strptime(end_date, '%Y-%m-%d') + timedelta(days=1)).timetuple()))

    data = {
        "data": []
    }
    try:
        conn = sqlite3.connect(app.config["SQL"])
        cursor = conn.cursor()
        sql = f'''SELECT * FROM report WHERE created_date_int >={start_date} AND created_date_int<={end_date} ORDER BY created_date_int DESC'''
        cursor.execute(sql)
        records = cursor.fetchall()
        for key, value in enumerate(records):
            data["data"].append(
                {
                "id" : key+1,
                "motor": "motor "+str(value[3]),
                "squence": value[2],
                "user": value[1],
                "datetime": value[4]
                }
            )
    except Exception as err:
        pass

    return jsonify(data)