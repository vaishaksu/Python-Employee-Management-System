from flask import Blueprint, render_template, request, url_for, redirect, jsonify, session
import database_connection
import json
import datetime
from datetime import datetime

from flask_wtf import FlaskForm
from wtforms import BooleanField, TextAreaField, IntegerField
from wtforms.fields.html5 import DateField, TimeField
from wtforms.validators import DataRequired, required, NumberRange, Optional, url
from wtforms import validators, SubmitField, StringField, form
from wtforms.fields.html5 import DateTimeLocalField, EmailField
from wtforms_components import DateRange
from bson import ObjectId
from random import randrange
from wtforms.fields import html5 as h5fields
from wtforms.widgets import html5 as h5widgets
from dateutil.relativedelta import relativedelta

import gridfs

admin = Blueprint("admin", __name__, static_folder="static", template_folder="templates")
# Employee Table
fetch_all_employees_table = database_connection.connect_employee_table_name()
data_conn = database_connection.database_connection()
work_schedle_db = database_connection.connect_workSchedule_table_name()


class InformForm(FlaskForm):
    title = StringField('Title', validators=[DataRequired()])
    startdate = DateField('Start Date', format="%Y-%m-%d", validators=(validators.DataRequired(),))
    enddate = DateField('End Date', format="%Y-%m-%d", validators=(validators.DataRequired(),))
    start_at = TimeField('Start at', format="'%h-%m'",
                         validators=[DateRange(min=datetime.now()), validators.DataRequired()])
    end_at = TimeField('End at', format="'%h-%m'",
                       validators=[DateRange(min=datetime.now()), validators.DataRequired()])
    date_of_joining = DateField('Date of Joining', format="%Y-%m-%d", validators=(validators.DataRequired(),))
    date_of_birth = DateField('Date Of Birth', format="%Y-%m-%d", validators=(validators.DataRequired(),))
    last_date = DateField('Last Date', format="%Y-%m-%d", )
    official_email_address = EmailField('Official Email address')
    email_address = EmailField('Email address', validators=(validators.DataRequired(), validators.Email()))
    phoneNumber = StringField('Phone Number')
    salary = h5fields.IntegerField(
        "Salary", widget=h5widgets.NumberInput(min=0)
    )
    bonus = h5fields.IntegerField(
        "Bonus", widget=h5widgets.NumberInput(min=0)
    )
    bank_name = StringField('Bank Name')
    account_number = StringField('Account Number')
    UAN_number = StringField('UAN Number')
    basic_allowance = h5fields.IntegerField(
        "Basic Allowance", widget=h5widgets.NumberInput(min=0)
    )
    medical_allowance = h5fields.IntegerField(
        "Medical Allowance", widget=h5widgets.NumberInput(min=0)
    )
    provident_fund = h5fields.IntegerField(
        "Provident Fund", widget=h5widgets.NumberInput(min=0)
    )
    tax = h5fields.IntegerField(
        "Tax", widget=h5widgets.NumberInput(min=0)
    )
    current_address = StringField('Current Address')
    permanent_address = StringField('Permanent Address')
    is_active = BooleanField('Active')
    is_manager = BooleanField('Is a Manager?')
    first_name = StringField('First Name', validators=[DataRequired()])
    last_name = StringField('Last Name', validators=[DataRequired()])
    hourly_pay = IntegerField('Hourly Pay')
    submit = SubmitField('Submit')

    department_name = StringField('Department Name', validators=[DataRequired()])
    employee_type_description = StringField('Employee Type Description', validators=[DataRequired()])

    role_name = StringField('Role Name', validators=[DataRequired()])
    role_have_full_power = BooleanField('Assign Full Power?')
    role_upload_documents_profile_pictures = BooleanField('Ablity to Upload Document?')


@admin.route("/")
@admin.route("/home")
def adminHome():
    employees = database_connection.merge_employee_role('home')
    print("session123123 Admin: ", session)
    session['username'] = session['username']
    for employee in employees:
        employee["date_of_joining"] = datetime.strptime(employee["date_of_joining"],
                                                        '%Y-%m-%dT%H:%M%S').strftime("%B %d, %Y")

    return render_template("admin/admin.html", display_all_employees=employees, came_from="admin.adminHome",
                           search_result="")


@admin.route("/search", methods=["POST"])
def searchAnEmployee():
    fetch_search_result = request.form.get('search_value')
    fetch_names = database_connection.fetch_employee_search_name(fetch_search_result)
    if (fetch_search_result):
        return render_template("admin/admin.html", display_all_employees=fetch_names, search_result=fetch_search_result,
                               value_search=request.form.get('search_value'))
    else:
        return redirect(url_for("admin.adminHome"))  # If the search field is empty then navigate to the home page


@admin.route("/calendar")
def getFullCalendar():
    work_scheule = database_connection.workSchedule_table(work_schedle_db)
    events = work_scheule

    return render_template("admin/calendar.html", events=events)


# Drag the event from one date to the other date
@admin.route("/postData", methods=['GET', 'POST'])
def return_data():
    req_json_obj = request.json
    fetchedData = req_json_obj["eventData"]
    one_element = database_connection.fetch_only_one_work_schedule(fetchedData["_id"])

    new_start_date = str(fetchedData["start"])
    old_end_date = fetchedData["end"]

    if len(old_end_date) >= 19:
        end_date_string = datetime.strptime(old_end_date, "%Y-%m-%dT%H:%M:%S")
    else:
        end_date_string = datetime.strptime(old_end_date, "%Y-%m-%dT%H:%M")

    start_date_string = datetime.strptime(new_start_date, "%Y-%m-%dT%H:%M:%S.%fZ")

    new_format_end_time = "%H:%M:%S"
    new_format_start_time = "%Y-%m-%d"
    new_end_date = start_date_string.strftime(new_format_start_time) + 'T' + end_date_string.strftime(
        new_format_end_time)
    start_date_format = "%Y-%m-%dT%H:%M:%S"
    new_value_start = start_date_string.strftime(start_date_format)
    work_schedle_db.update_one(
        {'_id': one_element["_id"]},
        {'$set': {'start': new_value_start, 'end': new_end_date}}
    )
    return jsonify(req_json_obj)


@admin.route("/EmployeeActive/<status>", methods=['GET'])
def employee_active_data(status):
    if status == 'Inactive':
        is_active = False
    elif status == 'active':
        is_active = True
    else:
        return redirect(url_for('admin.adminHome'))
    is_active_status = database_connection.fetch_active_inactive_employee(is_active)
    employees = database_connection.merge_employee_role(is_active_status)  # Merging 3 tables
    for employee in employees:
        employee["date_of_joining"] = datetime.strptime(employee["date_of_joining"],
                                                        '%Y-%m-%dT%H:%M%S').strftime("%B %d, %Y")
    return render_template("admin/admin.html", display_all_employees=employees, came_from="admin.adminHome",
                           search_result="", status=status)


@admin.route("/EditEmployee/event/<int:empId>")
def getEditEmployeeEventCalendar(empId):
    events = database_connection.fetch_work_schedule_particular_emp(empId)
    return render_template("shared-component/employee_calendar.html", employee_id=empId, events=events,
                           drag_drop_enable=True if 'employee_id' not in session else None)


@admin.route("/getExistingEvent/<id>/<int:toggle>/empId/<int:employee_id>", methods=['GET', 'POST'])
def editExitEvent(id, toggle, employee_id):
    one_element = database_connection.fetch_only_one_work_schedule(ObjectId(id))
    form = InformForm()

    all_employees = database_connection.connect_employee_table_name()
    all_managers = database_connection.connect_manager_table_name()
    return render_template('admin/edit_event_creation.html',
                           form=form,
                           display_all_employees=database_connection.employee_table(all_employees),
                           display_all_managers=database_connection.manager_table(all_managers),
                           fetched_data=one_element,
                           toggle=toggle,
                           show_all_btns=True,
                           coming_from_emp_edit_screen=employee_id)