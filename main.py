# import pymongo
from datetime import datetime

from flask import Flask, request, render_template, url_for, session, redirect, flash
from wtforms.csrf import session

from login import login
from admin import admin
from employees import employees
from flask_pymongo import PyMongo
import database_connection
import random_id_generation
import json
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
import numpy as np

import io
import random
from flask import Response
from matplotlib.backends.backend_agg import FigureCanvasAgg as FigureCanvas
from matplotlib.figure import Figure

import string

app = Flask(__name__)

app.config['SECRET_KEY'] = "$%^&U$%^TYURTFY&*GU"

###### BluePrint for differernt pages
app.register_blueprint(login, url_prefix="/login")
app.register_blueprint(admin, url_prefix="/admin")
app.register_blueprint(employees, url_prefix="/employees")

app.config[
    "MONGO_URI"] = "mongodb+srv://Username:Password@cluster0.j1u4m.mongodb.net/EmployeeManagementSystem?retryWrites=true&w=majority"
mongo: PyMongo = PyMongo(app)

fetch_database_connection = database_connection.database_connection()

#### Fetch only certain table
all_roles = database_connection.connect_role_table_name()
login_table_name = database_connection.connect_login_table()
manager_table_name = database_connection.connect_manager_table_name()

gender_array = ['Not Ready to Declare', 'Male', 'Female']


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

@app.route("/", methods=["GET"])
def homepage():
    return render_template('base.html')

# http://127.0.0.1:5001/
@app.route("/login", methods=["GET"])
def redirect_login():
    return redirect(url_for('login.login_info'))


# http://127.0.0.1:5001/hello
@app.route("/employees", methods=["GET"])
def greet():
    return "<h1>Hello World</h1>"


# http://127.0.0.1:5001/name
# This should return your name
@app.route("/name", methods=["GET"])
def name():
    return "<h1>Employee Management System</h1>"


@app.route("/profile")
def profile_pictures():
    return '''
        <form method="POST" action="/create"  enctype="multipart/form-data">
            <input type="text" name="username" />
            <input type="file" name="profile_image" />
            <input type="submit" />
        </form>
    '''


@app.route("/create", methods=['POST'])
def create():
    if "profile_image" in request.files:
        profile_image = request.files["profile_image"]
        mongo.save_file(profile_image.filename.split(".")[1], profile_image)
        return 'DONE!'


@app.route("/file/<filename>")
def file(filename):
    return mongo.send_file(filename)


# @app.route("/profile/<_id>")
# def profile(_id):
#     employees = mongo.db.employees.find_one_or_404({'_id': _id})
#     return f'''
#         <h1>{_id}</h1>
#         <img src="{url_for('file', filename=employees['profile_image_name'])}">
# '''

@app.route("/profiles/<int:id>")
def profile(id):
    # employees = mongo.db.employees.find_one_or_404({'_id': id})
    employees = mongo.db.employees.find_one_or_404({'_id': id})

    return f'''
        <h1>id</h1>
        <img src="{url_for('file', filename=employees['profile_image_name'])}">
    '''


@app.route("/newEmployee")
def createNewEmployeeGET():
    # all_roles = database_connection.connect_role_table_name()
    # all_managers = database_connection.connect_manager_table_name()
    form = InformForm()

    fetch_all_departments = [doc for doc in mongo.db.departments.find()]
    fetch_all_employee_type = [doc for doc in mongo.db.employee_type.find()]
    twenty_yrs_ago = datetime.now() - relativedelta(years=20)

    today = datetime.now()
    set_min_date = today.strftime("%Y-%m-%d")

    strp_today = twenty_yrs_ago.strftime("%Y-%m-%d")

    all_managers = database_connection.connect_manager_table_name()
    return render_template("shared-component/new_employee.html",
                           display_all_roles=database_connection.role_table(all_roles),
                           display_all_managers=database_connection.manager_table(all_managers),
                           display_all_departments=fetch_all_departments,
                           display_all_employee_type=fetch_all_employee_type,
                           form=form,
                           came_from="admin.adminHome",
                           gender_array=gender_array,
                           twenty_yrs_ago=strp_today,
                           min_date=set_min_date)


def createNewFormComparison():
    if "profile_image" in request.files:
        all_employees_table = database_connection.connect_employee_table_name()
        all_emp_record = database_connection.employee_table(all_employees_table)
        salary_hourly_details = {}

        # Fulltime job has some benefits
        if int(request.form.get('employee_type_id')) == 1000:
            my_salary = request.form.get('salary')
            my_bonus = request.form.get('bonus')
            my_basic_allowance = request.form.get('basic_allowance')
            my_medical_allowance = request.form.get('medical_allowance')
            my_provident_fund = request.form.get('provident_fund')
            my_tax = request.form.get('tax')

            salary_hourly_details = {
                "salary_details": {
                    "salary": 0 if not my_salary else float(request.form.get('salary')),
                    "bonus": 0 if not my_bonus else float(request.form.get('bonus')),
                    "allowances": {
                        "basic_allowance": 0 if not my_basic_allowance else float(
                            request.form.get('basic_allowance')),
                        "medical_allowance": 0 if not my_medical_allowance else float(
                            request.form.get('medical_allowance')),
                        "provident_fund": 0 if not my_provident_fund else float(request.form.get('provident_fund')),
                        "tax": 0 if not my_tax else float(request.form.get('tax'))
                    }
                }
            }
        else:
            myhourly_pay = request.form.get('hourly_pay')
            salary_hourly_details = {
                "hourly_pay_details": {
                    "hourly_pay": 0 if not myhourly_pay else float(request.form.get('hourly_pay'))
                }
            }
        if request.files["profile_image"].filename:
            profile_image = request.files["profile_image"]
            picture = random_id_generation.generating_random_id_profile_picture()

            # Mongo save can be done only once, only in POST, in fs.files can have only 1 uploaded file also the length of the uploaded file should be greater than 1
            # fs.files obj.len can never be zero, if it is zero then the file will not load whatsoever
            mongo.save_file(picture + '.' + profile_image.filename.split(".")[1], profile_image)
            profile_image.filename = picture + '.' + profile_image.filename.split(".")[1]
        else:
            profile_image = request.files["profile_image"]

        insert_data = {
            '_id': random_id_generation.generating_random_id_employees(),
            'first_name': request.form.get('first_name'),
            'last_name': request.form.get('last_name'),
            'phone_number': request.form.get('phoneNumber'),
            'email_address': request.form.get('email_address'),
            'user_role_id': int(request.form.get('role_id')),
            'user_manager_id': int(request.form.get('manager_id')),
            'gender': request.form.get('gender'),
            'profile_image_name': profile_image.filename,
            'is_active': True if request.form.get('is_active') else False,
            'employee_type_id': int(request.form.get('employee_type_id')),
            'department_id': int(request.form.get('department_id')),
            'date_of_birth': request.form.get('date_of_birth'),
            'date_of_joining': request.form.get('date_of_joining') + "T08:00",
            'last_date': request.form.get('last_date'),
            'username': request.form.get('first_name') + '.' + request.form.get('last_name'),
            'official_email_address': request.form.get('first_name') + '.' + request.form.get('last_name') + '@ems.com',
            'is_manager': True if request.form.get('is_manager') else False,
            'bank_details': {
                'bank_name': request.form.get('bank_name'),
                'account_number': request.form.get('account_number'),
                'UAN_number': request.form.get('UAN_number'),
            },
            'address': {
                'current_address': request.form.get('current_address'),
                'permanent_address': request.form.get('permanent_address')
            }
        }

        insert_data.update(salary_hourly_details)

        # Insert the employees  data into the employees collection
        mongo.db.employees.insert_one(insert_data)

        # If the is a Manager? then insert the user into the table
        if request.form.get('is_manager'):
            manager_data = {
                "_id": insert_data["_id"],
                "manager_first_name": insert_data["first_name"],
                "manager_last_name": insert_data["last_name"],
                "manager_role_id": insert_data['user_role_id'],
                "manager_department_id": insert_data["department_id"]
            }
            mongo.db.managers.insert_one(manager_data)

        insert_data_Login = {
            "_id": random_id_generation.generating_random_id_login(),
            "username": request.form.get('first_name') + '.' + request.form.get('last_name'),
            "password": "",
            "remember_me": "on",
            "first_name": request.form.get('first_name'),
            "last_name": request.form.get('last_name'),
            "email_address": request.form.get('first_name') + '.' + request.form.get('last_name') + '@ems.com',
            'is_admin': False
        }
        login_table_name.insert_one(insert_data_Login)


@app.route("/createNewEmployee", methods=['POST'])
def createNewEmployee():
    if "profile_image" in request.files:
        profile_image = request.files["profile_image"]
        # mongo.save_file(profile_image.filename, profile_image)
        all_employees_table = database_connection.connect_employee_table_name()
        all_emp_record = database_connection.employee_table(all_employees_table)

        requestForm = {}
        form = InformForm()

        if (not request.form.get("employee_type_id") or not request.form.get("manager_id") or not request.form.get(
                "role_id") or not request.form.get("department_id")):

            error = []

            if not request.form.get("role_id"):
                error.append("Please Select the Job Position")
            elif request.form.get("role_id"):
                requestForm.update({'role_id': int(request.form.get("role_id"))})

            if not request.form.get("manager_id"):
                error.append("Please Select the Reporting Manager")
            elif request.form.get("manager_id"):
                requestForm.update({'manager_id': int(request.form.get("manager_id"))})

            if not request.form.get("employee_type_id"):
                error.append("Please Select the Employment Type")
            elif request.form.get("employee_type_id"):
                requestForm.update({'employee_type_id': int(request.form.get("employee_type_id"))})

            if not request.form.get("department_id"):
                error.append("Please Select the Department")
            elif request.form.get("department_id"):
                requestForm.update({'department_id': int(request.form.get("department_id"))})

            fetch_all_departments = [doc for doc in mongo.db.departments.find()]
            fetch_all_employee_type = [doc for doc in mongo.db.employee_type.find()]

            all_managers = database_connection.connect_manager_table_name()
            return render_template("shared-component/new_employee.html",
                                   display_all_roles=database_connection.role_table(all_roles),
                                   display_all_managers=database_connection.manager_table(all_managers),
                                   display_all_departments=fetch_all_departments,
                                   display_all_employee_type=fetch_all_employee_type,
                                   form=form,
                                   error=error,
                                   came_from="admin.adminHome",
                                   gender_array=gender_array,
                                   requestForm=requestForm)
        elif int(request.form.get("employee_type_id")) != 1000 and request.form.get(
                "is_manager"):  # If manager cannot be in Hourly rate
            error = []
            error.append("Manager Cannot be on an hourly rate")
            requestForm.update({'role_id': int(request.form.get("role_id"))})
            requestForm.update({'manager_id': int(request.form.get("manager_id"))})
            requestForm.update({'employee_type_id': int(request.form.get("employee_type_id"))})
            requestForm.update({'department_id': int(request.form.get("department_id"))})
            fetch_all_departments = [doc for doc in mongo.db.departments.find()]
            fetch_all_employee_type = [doc for doc in mongo.db.employee_type.find()]

            all_managers = database_connection.connect_manager_table_name()
            return render_template("shared-component/new_employee.html",
                                   display_all_roles=database_connection.role_table(all_roles),
                                   display_all_managers=database_connection.manager_table(all_managers),
                                   display_all_departments=fetch_all_departments,
                                   display_all_employee_type=fetch_all_employee_type,
                                   form=form,
                                   error=error,
                                   came_from="admin.adminHome",
                                   gender_array=gender_array,
                                   requestForm=requestForm)
        else:

            manager_dept = mongo.db.managers.find({'manager_department_id': int(request.form.get('department_id'))})
            manager_dept_all = [doc for doc in manager_dept]

            if len(manager_dept_all) == 0 or int(request.form.get('manager_id')) == 0:
                createNewFormComparison()
                return redirect(url_for("admin.adminHome"))
            else:
                result = filter(
                    lambda x: x["manager_department_id"] == int(request.form.get('department_id')) and x['_id'] == int(
                        request.form.get('manager_id')), manager_dept_all)
                list_result = list(result)
                # not_in_list = random_id_generator not in list(result)
                if len(list_result) > 0:
                    createNewFormComparison()
                    return redirect(url_for("admin.adminHome"))
                else:
                    error = []
                    error.append(f"Reporting manager doesn't belong to the department you selected.")
                    requestForm.update({'role_id': int(request.form.get("role_id"))})
                    requestForm.update({'manager_id': int(request.form.get("manager_id"))})
                    requestForm.update({'employee_type_id': int(request.form.get("employee_type_id"))})
                    requestForm.update({'department_id': int(request.form.get("department_id"))})

                    fetch_all_departments = [doc for doc in mongo.db.departments.find()]
                    fetch_all_employee_type = [doc for doc in mongo.db.employee_type.find()]

                    all_managers = database_connection.connect_manager_table_name()
                    return render_template("shared-component/new_employee.html",
                                           display_all_roles=database_connection.role_table(all_roles),
                                           display_all_managers=database_connection.manager_table(all_managers),
                                           display_all_departments=fetch_all_departments,
                                           display_all_employee_type=fetch_all_employee_type,
                                           form=form,
                                           error=error,
                                           came_from="admin.adminHome",
                                           gender_array=gender_array,
                                           requestForm=requestForm)


def editEmployeeComparison(found_one_from_db_before_json, id):
    if "profile_image" in request.files:
        print("ref: ", request.form)
        found_one_from_db_before_json = mongo.db.employees.find_one({"_id": id})
        if request.files["profile_image"].filename and found_one_from_db_before_json["profile_image_name"] != \
                request.files["profile_image"].filename:
            profile_image = request.files["profile_image"]
            picture = random_id_generation.generating_random_id_profile_picture()

            # Mongo save can be done only once, only in POST, in fs.files can have only 1 uploaded file also the length of the uploaded file should be greater than 1
            # fs.files obj.len can never be zero, if it is zero then the file will not load whatsoever
            mongo.save_file(picture + '.' + profile_image.filename.split(".")[1], profile_image)
            profile_image.filename = picture + '.' + profile_image.filename.split(".")[1]
        else:
            profile_image = request.files["profile_image"]

        requestForm = {}
        form = InformForm()
        converted_json = json.dumps(found_one_from_db_before_json, sort_keys=True)

        one_salary_hourly_pay = {}
        fetched_value_before_json = {
            '_id': id,
            'first_name': request.form.get('first_name'),
            'last_name': request.form.get('last_name'),
            'phone_number': request.form.get('phoneNumber'),
            'email_address': request.form.get('email_address'),
            'user_role_id': int(request.form.get('role_id')),
            'user_manager_id': int(request.form.get('manager_id')) if (found_one_from_db_before_json[
                                                                           "user_manager_id"] == 0 or
                                                                       found_one_from_db_before_json[
                                                                           "user_manager_id"] != 0) else
            found_one_from_db_before_json["user_manager_id"],
            'gender': request.form.get('gender'),
            'profile_image_name': profile_image.filename if profile_image.filename else
            found_one_from_db_before_json[
                "profile_image_name"],
            'is_active': True if request.form.get('is_active') else False,
            'employee_type_id': int(request.form.get('employee_type_id')),
            'department_id': int(request.form.get('department_id')),
            'date_of_birth': request.form.get('date_of_birth'),
            'date_of_joining': request.form.get('date_of_joining') + "T08:00",
            'last_date': request.form.get('last_date'),
            'username': found_one_from_db_before_json['username'],
            'official_email_address': found_one_from_db_before_json['official_email_address'],
            'is_manager': True if request.form.get('is_manager') else False,
            'bank_details': {
                'bank_name': request.form.get('bank_name'),
                'account_number': request.form.get('account_number'),
                'UAN_number': request.form.get('UAN_number'),
            },
            'address': {
                'current_address': request.form.get('current_address'),
                'permanent_address': request.form.get('permanent_address')
            }
        }

        if 'about_me' in found_one_from_db_before_json:
            fetched_value_before_json['about_me'] = request.form.get('about_me') if request.form.get('about_me') else \
            found_one_from_db_before_json['about_me']
        else:
            if request.form.get('about_me'):
                fetched_value_before_json['about_me'] = request.form.get('about_me')
            else:
                fetched_value_before_json['about_me'] = ''

        if int(request.form.get('employee_type_id')) == 1000:
            my_salary = request.form.get('salary')
            my_bonus = request.form.get('bonus')
            my_basic_allowance = request.form.get('basic_allowance')
            my_medical_allowance = request.form.get('medical_allowance')
            my_provident_fund = request.form.get('provident_fund')
            my_tax = request.form.get('tax')

            one_salary_hourly_pay = {
                "salary_details": {
                    "salary": 0 if not my_salary else float(request.form.get('salary')),
                    "bonus": 0 if not my_bonus else float(request.form.get('bonus')),
                    "allowances": {
                        "basic_allowance": 0 if not my_basic_allowance else float(
                            request.form.get('basic_allowance')),
                        "medical_allowance": 0 if not my_medical_allowance else float(
                            request.form.get('medical_allowance')),
                        "provident_fund": 0 if not my_provident_fund else float(request.form.get('provident_fund')),
                        "tax": 0 if not my_tax else float(request.form.get('tax'))
                    }
                }
            }
        else:
            myhourly_pay = request.form.get('hourly_pay')
            one_salary_hourly_pay = {
                "hourly_pay_details": {
                    "hourly_pay": 0 if not myhourly_pay else float(request.form.get('hourly_pay'))
                }
            }
        fetched_value_before_json.update(one_salary_hourly_pay)
        fetched_value_before_json.update(one_salary_hourly_pay)
        fetched_val_json = json.dumps(fetched_value_before_json, sort_keys=True)

        collect_data_to_append = {}
        if converted_json == fetched_val_json:
            print("They are Exactly the same, so don't update the db")
        else:
            if fetched_value_before_json["first_name"] != found_one_from_db_before_json["first_name"]:
                collect_data_to_append["first_name"] = fetched_value_before_json["first_name"]
            if fetched_value_before_json["last_name"] != found_one_from_db_before_json["last_name"]:
                collect_data_to_append["last_name"] = fetched_value_before_json["last_name"]
            if fetched_value_before_json["phone_number"] != found_one_from_db_before_json["phone_number"]:
                collect_data_to_append["phone_number"] = fetched_value_before_json["phone_number"]
            if fetched_value_before_json["email_address"] != found_one_from_db_before_json["email_address"]:
                collect_data_to_append["email_address"] = fetched_value_before_json["email_address"]
            if fetched_value_before_json["user_role_id"] != found_one_from_db_before_json["user_role_id"]:
                collect_data_to_append["user_role_id"] = fetched_value_before_json["user_role_id"]
            if fetched_value_before_json["user_manager_id"] != found_one_from_db_before_json["user_manager_id"]:
                collect_data_to_append["user_manager_id"] = fetched_value_before_json["user_manager_id"]
            if fetched_value_before_json["gender"] != found_one_from_db_before_json["gender"]:
                collect_data_to_append["gender"] = fetched_value_before_json["gender"]
            if (fetched_value_before_json["profile_image_name"] != found_one_from_db_before_json[
                "profile_image_name"]):
                collect_data_to_append["profile_image_name"] = fetched_value_before_json["profile_image_name"]
            if fetched_value_before_json["is_active"] != found_one_from_db_before_json["is_active"]:
                collect_data_to_append["is_active"] = fetched_value_before_json["is_active"]
            if fetched_value_before_json["employee_type_id"] != found_one_from_db_before_json["employee_type_id"]:
                collect_data_to_append["employee_type_id"] = fetched_value_before_json["employee_type_id"]
            if fetched_value_before_json["department_id"] != found_one_from_db_before_json["department_id"]:
                collect_data_to_append["department_id"] = fetched_value_before_json["department_id"]
            if fetched_value_before_json["date_of_birth"] != found_one_from_db_before_json["date_of_birth"]:
                collect_data_to_append["date_of_birth"] = fetched_value_before_json["date_of_birth"]
            if fetched_value_before_json["date_of_joining"] != found_one_from_db_before_json["date_of_joining"]:
                collect_data_to_append["date_of_joining"] = fetched_value_before_json["date_of_joining"]
            if fetched_value_before_json["last_date"] != found_one_from_db_before_json["last_date"]:
                collect_data_to_append["last_date"] = fetched_value_before_json["last_date"]

            # Check if the about me exists
            if 'about_me' in found_one_from_db_before_json:
                if fetched_value_before_json["about_me"] != found_one_from_db_before_json["about_me"]:
                    collect_data_to_append["about_me"] = fetched_value_before_json["about_me"]
            else:
                if request.form.get('about_me'):
                    collect_data_to_append["about_me"] = fetched_value_before_json["about_me"]

            if (fetched_value_before_json["official_email_address"] != found_one_from_db_before_json[
                "official_email_address"]):
                collect_data_to_append["official_email_address"] = fetched_value_before_json[
                    "official_email_address"]
            if fetched_value_before_json["is_manager"] != found_one_from_db_before_json["is_manager"]:
                collect_data_to_append["is_manager"] = fetched_value_before_json["is_manager"]



            address_data = {
                    "address": {
                        "current_address": fetched_value_before_json['address']['current_address'],
                        "permanent_address": fetched_value_before_json['address']['permanent_address']
                    }
                }
            collect_data_to_append.update(address_data)

            bank_details_data = {
                "bank_details": {
                    "bank_name": fetched_value_before_json['bank_details']['bank_name'],
                    "account_number": fetched_value_before_json['bank_details']['account_number'],
                    "UAN_number": fetched_value_before_json['bank_details']['UAN_number']
                }
            }
            collect_data_to_append.update(bank_details_data)

            if ('salary_details' in fetched_value_before_json and 'hourly_pay_details' in found_one_from_db_before_json) or ('salary_details' in found_one_from_db_before_json and 'salary_details' in fetched_value_before_json):
                salary_overall = {
                    "salary_details": {
                        "salary": fetched_value_before_json['salary_details']['salary'],
                        "bonus": fetched_value_before_json['salary_details']['bonus'],
                        "allowances": {
                            "basic_allowance": fetched_value_before_json['salary_details']['allowances'][
                                'basic_allowance'],
                            "medical_allowance": fetched_value_before_json['salary_details']['allowances'][
                                'medical_allowance'],
                            "provident_fund": fetched_value_before_json['salary_details']['allowances'][
                                'provident_fund'],
                            "tax": fetched_value_before_json['salary_details']['allowances']['tax']
                        }
                    }
                }

                collect_data_to_append.update(salary_overall)

                if 'salary_details' in fetched_value_before_json and 'hourly_pay_details' in found_one_from_db_before_json:
                    # Deliberately remove the key called Hourly_pay_details
                    mongo.db.employees.update_one(
                        {'_id': id},
                        {'$unset': {'hourly_pay_details': ""}}
                    )

            elif ('hourly_pay_details' in fetched_value_before_json and 'salary_details' in found_one_from_db_before_json) or ('hourly_pay_details' in found_one_from_db_before_json and 'hourly_pay_details' in fetched_value_before_json):
                hourly_overall = {
                    "hourly_pay_details": {
                        "hourly_pay": fetched_value_before_json['hourly_pay_details']['hourly_pay']
                    }
                }

                collect_data_to_append.update(hourly_overall)

                if 'hourly_pay_details' in fetched_value_before_json and 'salary_details' in found_one_from_db_before_json:
                    # Deliberately remove the key called Hourly_pay_details
                    mongo.db.employees.update_one(
                        {'_id': id},
                        {'$unset': {'salary_details': ""}}
                    )

            # Check whether collect_data_to_append is an empty dict
            res = bool(collect_data_to_append)

            if res:
                if 'is_manager' in collect_data_to_append:
                    if collect_data_to_append["is_manager"]:
                        manager_data = {
                            "_id": id,
                            "manager_first_name": fetched_value_before_json["first_name"],
                            "manager_last_name": fetched_value_before_json["last_name"],
                            "manager_role_id": fetched_value_before_json['user_role_id'],
                            "manager_department_id": fetched_value_before_json["department_id"]
                        }
                        mongo.db.managers.insert_one(manager_data)
                    else:
                        mongo.db.managers.delete_one({'_id': id})

                if request.form.get('is_manager'):
                    manager_update_fetch = {}
                    if 'department_id' in collect_data_to_append:
                        manager_update_fetch['manager_department_id'] = collect_data_to_append['department_id']
                    if 'first_name' in collect_data_to_append:
                        manager_update_fetch['manager_first_name'] = collect_data_to_append['first_name']
                    if 'last_name' in collect_data_to_append:
                        manager_update_fetch['manager_last_name'] = collect_data_to_append['last_name']
                    if 'user_role_id' in collect_data_to_append:
                        manager_update_fetch['manager_role_id'] = collect_data_to_append['user_role_id']

                    if manager_update_fetch:
                        manager_table_name.update_one(
                            {'_id': id},
                            {'$set': manager_update_fetch}
                        )
                if 'first_name' in collect_data_to_append or 'last_name' in collect_data_to_append:
                    # Keep Login page updated as well
                    login_table_name.update_one(
                        {'username': found_one_from_db_before_json['username']},
                        {'$set': {'first_name': request.form.get('first_name'),
                                  'last_name': request.form.get('last_name')}}
                    )

                mongo.db.employees.update_one(
                    {'_id': id},
                    {'$set': collect_data_to_append}
                )


@app.route("/editEmployee/<int:id>")
def editEmployee(id):
    # Fetch only the particular employee whose Id matches in the database
    find_one = database_connection.fetch_only_one_employee(id)
    form = InformForm()
    twenty_yrs_ago = datetime.now() - relativedelta(years=20)
    strp_today = twenty_yrs_ago.strftime("%Y-%m-%d")

    one_salary_hourly_pay = {}
    if 'hourly_pay_details' in find_one:
        one_salary_hourly_pay = {
            'hourly_pay': find_one['hourly_pay_details']['hourly_pay']
        }
    else:
        one_salary_hourly_pay = {
            'salary': find_one['salary_details']['salary'],
            "bonus": find_one['salary_details']['bonus'],
            "basic_allowance": find_one['salary_details']['allowances']['basic_allowance'],
            "medical_allowance": find_one['salary_details']['allowances']['medical_allowance'],
            "provident_fund": find_one['salary_details']['allowances']['provident_fund'],
            "tax": find_one['salary_details']['allowances']['tax']
        }
    find_one.update(one_salary_hourly_pay)
    fetch_all_departments = [doc for doc in mongo.db.departments.find()]
    fetch_all_employee_type = [doc for doc in mongo.db.employee_type.find()]

    all_managers = database_connection.connect_manager_table_name()
    return render_template("shared-component/edit_employee.html",
                           form=form,
                           one_employee=find_one,
                           display_all_roles=database_connection.role_table(all_roles),
                           display_all_managers=database_connection.manager_table(all_managers),
                           display_all_departments=fetch_all_departments,
                           display_all_employee_type=fetch_all_employee_type,
                           came_from="admin.adminHome",
                           gender_array=gender_array,
                           twenty_yrs_ago=strp_today)


@app.route("/editAnEmployee/<int:id>", methods=['POST'])
def editAnEmployee(id):
    if "profile_image" in request.files:
        found_one_from_db_before_json = mongo.db.employees.find_one({"_id": id})
        profile_image = request.files["profile_image"]
        requestForm = {}
        form = InformForm()

        if ((not request.form.get("employee_type_id") or not request.form.get("manager_id") or not request.form.get(
                "role_id") or not request.form.get("department_id")) and id != 0):

            error = []

            if not request.form.get("role_id"):
                error.append("Please Select the Job Position")
            elif request.form.get("role_id"):
                requestForm.update({'role_id': int(request.form.get("role_id"))})

            if not request.form.get("manager_id") and id != 0:
                error.append("Please Select the Reporting Manager")
            elif request.form.get("manager_id"):
                requestForm.update({'manager_id': int(request.form.get("manager_id"))})

            if not request.form.get("employee_type_id"):
                error.append("Please Select the Employment Type")
            elif request.form.get("employee_type_id"):
                requestForm.update({'employee_type_id': int(request.form.get("employee_type_id"))})

            if not request.form.get("department_id"):
                error.append("Please Select the Department")
            elif request.form.get("department_id"):
                requestForm.update({'department_id': int(request.form.get("department_id"))})

            fetch_all_departments = [doc for doc in mongo.db.departments.find()]
            fetch_all_employee_type = [doc for doc in mongo.db.employee_type.find()]

            all_managers = database_connection.connect_manager_table_name()
            return render_template("shared-component/edit_employee.html",
                                   display_all_roles=database_connection.role_table(all_roles),
                                   display_all_managers=database_connection.manager_table(all_managers),
                                   display_all_departments=fetch_all_departments,
                                   display_all_employee_type=fetch_all_employee_type,
                                   form=form,
                                   error=error,
                                   came_from="admin.adminHome",
                                   gender_array=gender_array,
                                   requestForm=requestForm,
                                   one_employee=found_one_from_db_before_json)
        elif int(request.form.get("employee_type_id")) != 1000 and request.form.get(
                "is_manager"):  # If manager cannot be in Hourly rate
            error = []
            error.append("Manager Cannot be on an hourly rate")
            requestForm.update({'role_id': int(request.form.get("role_id"))})
            requestForm.update({'manager_id': int(request.form.get("manager_id"))})
            requestForm.update({'employee_type_id': int(request.form.get("employee_type_id"))})
            requestForm.update({'department_id': int(request.form.get("department_id"))})
            fetch_all_departments = [doc for doc in mongo.db.departments.find()]
            fetch_all_employee_type = [doc for doc in mongo.db.employee_type.find()]

            all_managers = database_connection.connect_manager_table_name()
            return render_template("shared-component/edit_employee.html",
                                   display_all_roles=database_connection.role_table(all_roles),
                                   display_all_managers=database_connection.manager_table(all_managers),
                                   display_all_departments=fetch_all_departments,
                                   display_all_employee_type=fetch_all_employee_type,
                                   form=form,
                                   error=error,
                                   came_from="admin.adminHome",
                                   gender_array=gender_array,
                                   requestForm=requestForm,
                                   one_employee=found_one_from_db_before_json)
        else:
            # editEmployeeComparison(found_one_from_db_before_json)


            manager_dept = mongo.db.managers.find({'manager_department_id': int(request.form.get('department_id'))})
            manager_dept_all = [doc for doc in manager_dept]

            if id != 0:
                if len(manager_dept_all) == 0 or int(request.form.get('manager_id')) == 0:
                    editEmployeeComparison(found_one_from_db_before_json, id)
                    return redirect(url_for("admin.adminHome"))
                else:
                    result = filter(
                        lambda x: x["manager_department_id"] == int(request.form.get('department_id')) and x[
                            '_id'] == int(
                            request.form.get('manager_id')), manager_dept_all)
                    list_result = list(result)
                    # not_in_list = random_id_generator not in list(result)
                    if len(list_result) > 0:
                        editEmployeeComparison(found_one_from_db_before_json, id)
                        return redirect(url_for("admin.adminHome"))
                    else:
                        error = []
                        error.append(f"Reporting manager doesn't belong to the department you selected.")
                        requestForm.update({'role_id': int(request.form.get("role_id"))})
                        requestForm.update({'manager_id': int(request.form.get("manager_id"))})
                        requestForm.update({'employee_type_id': int(request.form.get("employee_type_id"))})
                        requestForm.update({'department_id': int(request.form.get("department_id"))})
                        fetch_all_departments = [doc for doc in mongo.db.departments.find()]
                        fetch_all_employee_type = [doc for doc in mongo.db.employee_type.find()]

                        all_managers = database_connection.connect_manager_table_name()
                        return render_template("shared-component/edit_employee.html",
                                               display_all_roles=database_connection.role_table(all_roles),
                                               display_all_managers=database_connection.manager_table(all_managers),
                                               display_all_departments=fetch_all_departments,
                                               display_all_employee_type=fetch_all_employee_type,
                                               form=form,
                                               error=error,
                                               came_from="admin.adminHome",
                                               gender_array=gender_array,
                                               requestForm=requestForm,
                                               one_employee=found_one_from_db_before_json)
            else:  # if its a CEO Just return
                editEmployeeComparison(found_one_from_db_before_json, id)
                return redirect(url_for("admin.adminHome"))


@app.route("/editAnIndividualEmployee/<int:id>", methods=['POST'])
def editAnIndividualEmployee(id):
    if "profile_image" in request.files:
        found_one_from_db_before_json = mongo.db.employees.find_one({"_id": id})
        profile_image = request.files["profile_image"]
        requestForm = {}
        form = InformForm()

        if ((not request.form.get("employee_type_id") or not request.form.get("manager_id") or not request.form.get(
                "role_id") or not request.form.get("department_id")) and id != 0):

            error = []

            if not request.form.get("role_id"):
                error.append("Please Select the Job Position")
            elif request.form.get("role_id"):
                requestForm.update({'role_id': int(request.form.get("role_id"))})

            if not request.form.get("manager_id") and id != 0:
                error.append("Please Select the Reporting Manager")
            elif request.form.get("manager_id"):
                requestForm.update({'manager_id': int(request.form.get("manager_id"))})

            if not request.form.get("employee_type_id"):
                error.append("Please Select the Employment Type")
            elif request.form.get("employee_type_id"):
                requestForm.update({'employee_type_id': int(request.form.get("employee_type_id"))})

            if not request.form.get("department_id"):
                error.append("Please Select the Department")
            elif request.form.get("department_id"):
                requestForm.update({'department_id': int(request.form.get("department_id"))})

            fetch_all_departments = [doc for doc in mongo.db.departments.find()]
            fetch_all_employee_type = [doc for doc in mongo.db.employee_type.find()]

            all_managers = database_connection.connect_manager_table_name()
            return render_template("employees/employee.html",
                                   display_all_roles=database_connection.role_table(all_roles),
                                   display_all_managers=database_connection.manager_table(all_managers),
                                   display_all_departments=fetch_all_departments,
                                   display_all_employee_type=fetch_all_employee_type,
                                   form=form,
                                   error=error,
                                   came_from="employees.home",
                                   gender_array=gender_array,
                                   requestForm=requestForm,
                                   one_employee=found_one_from_db_before_json)
        elif int(request.form.get("employee_type_id")) != 1000 and request.form.get(
                "is_manager"):  # If manager cannot be in Hourly rate
            error = []
            error.append("Manager Cannot be on an hourly rate")
            requestForm.update({'role_id': int(request.form.get("role_id"))})
            requestForm.update({'manager_id': int(request.form.get("manager_id"))})
            requestForm.update({'employee_type_id': int(request.form.get("employee_type_id"))})
            requestForm.update({'department_id': int(request.form.get("department_id"))})
            fetch_all_departments = [doc for doc in mongo.db.departments.find()]
            fetch_all_employee_type = [doc for doc in mongo.db.employee_type.find()]

            all_managers = database_connection.connect_manager_table_name()
            return render_template("employees/employee.html",
                                   display_all_roles=database_connection.role_table(all_roles),
                                   display_all_managers=database_connection.manager_table(all_managers),
                                   display_all_departments=fetch_all_departments,
                                   display_all_employee_type=fetch_all_employee_type,
                                   form=form,
                                   error=error,
                                   came_from="employees.home",
                                   gender_array=gender_array,
                                   requestForm=requestForm,
                                   one_employee=found_one_from_db_before_json)
        else:
            # editEmployeeComparison(found_one_from_db_before_json)


            manager_dept = mongo.db.managers.find({'manager_department_id': int(request.form.get('department_id'))})
            manager_dept_all = [doc for doc in manager_dept]

            if id != 0:
                if len(manager_dept_all) == 0 or int(request.form.get('manager_id')) == 0:
                    editEmployeeComparison(found_one_from_db_before_json, id)
                    return redirect(url_for("employees.home"))
                else:
                    result = filter(
                        lambda x: x["manager_department_id"] == int(request.form.get('department_id')) and x[
                            '_id'] == int(
                            request.form.get('manager_id')), manager_dept_all)
                    list_result = list(result)
                    # not_in_list = random_id_generator not in list(result)
                    if len(list_result) > 0:
                        editEmployeeComparison(found_one_from_db_before_json, id)
                        return redirect(url_for("employees.home"))
                    else:
                        error = []
                        error.append(f"Reporting manager doesn't belong to the department you selected.")
                        requestForm.update({'role_id': int(request.form.get("role_id"))})
                        requestForm.update({'manager_id': int(request.form.get("manager_id"))})
                        requestForm.update({'employee_type_id': int(request.form.get("employee_type_id"))})
                        requestForm.update({'department_id': int(request.form.get("department_id"))})
                        fetch_all_departments = [doc for doc in mongo.db.departments.find()]
                        fetch_all_employee_type = [doc for doc in mongo.db.employee_type.find()]

                        all_managers = database_connection.connect_manager_table_name()
                        return render_template("employees/employee.html",
                                               display_all_roles=database_connection.role_table(all_roles),
                                               display_all_managers=database_connection.manager_table(all_managers),
                                               display_all_departments=fetch_all_departments,
                                               display_all_employee_type=fetch_all_employee_type,
                                               form=form,
                                               error=error,
                                               came_from="employees.home",
                                               gender_array=gender_array,
                                               requestForm=requestForm,
                                               one_employee=found_one_from_db_before_json)
            else:  # if its a CEO Just return
                editEmployeeComparison(found_one_from_db_before_json, id)
                return redirect(url_for("employees.home"))


# Delete an Event
@app.route("/deleteExistingEmployee/<int:id>")
def deleteExistingEmployee(id):
    fetch_one_employee = mongo.db.employees.find_one({'_id': id})
    if fetch_one_employee['is_manager']:
        mongo.db.managers.delete_one({'_id': id})

    # Delete the login who has the same username
    mongo.db.login.delete_one({'username': fetch_one_employee['username']})

    mongo.db.employees.delete_one({'_id': id})
    return redirect(url_for('admin.adminHome'))


# ********************************** CREATEING A NEW DEPARTMENT ************************** #
@app.route("/createNewDepartment", methods=['GET', 'POST'])
def createNewDepartmentGET():
    form = InformForm()
    return render_template("admin/new_department.html",
                           form=form,
                           came_from="admin.adminHome")


@app.route("/createNewDepartmentPOST", methods=['GET', 'POST'])
def createNewDepartmentPOST():
    # Insert the employees  data into the employees collection
    mongo.db.departments.insert_one({
        '_id': random_id_generation.generating_random_id_departments(),
        'department_name': request.form.get('department_name')
    })
    return redirect(url_for("admin.adminHome"))


@app.route("/editDepartment/<int:id>", methods=['GET', 'POST'])
def editingDepartmentGET(id):
    # Insert the employees  data into the employees collection
    form = InformForm()
    one_department = mongo.db.departments.find_one({"_id": id})
    employees_dept = mongo.db.employees.find({'department_id': id})
    manager_dept = mongo.db.managers.find({'manager_department_id': id})
    all_mgrs = [doc for doc in manager_dept]
    all_emp = [doc for doc in employees_dept]
    no_of_employees = list(filter(lambda x: x["_id"] != 0, all_emp))

    if len(all_mgrs):
        for emp in all_emp:
            for mgr in all_mgrs:
                if emp["_id"] == mgr["_id"]:
                    mgr["email_address"] = emp["email_address"]
                    mgr["phone_number"] = emp["phone_number"]
                    mgr["profile_image_name"] = emp["profile_image_name"]
                    mgr["is_active"] = emp["is_active"]
                    mgr["official_email_address"] = emp["official_email_address"]


        mgr_count = 0
        emp_count = 0
        for mgr in all_mgrs:
            mgr_count += 1
            mgr['children'] = []
            for emp in all_emp:
                if mgr["_id"] == emp["user_manager_id"]:
                    mgr['children'].append(emp)
                    emp_count += 1

        take_separately = []
        for mgr_children in all_mgrs:
            if len(mgr_children['children']):
                take_separately.append(mgr_children)

        # Find the grandchildren
        for mgr_children in all_mgrs:
            for segregate in take_separately:

                if len(mgr_children['children']) > 0:
                    for mgr_grand_children in mgr_children['children']:

                        if segregate["_id"] == mgr_grand_children["_id"]:
                            mgr_grand_children["children"] = []
                            for seg in segregate["children"]:
                                mgr_grand_children["children"].append(seg)

        # Delete the repeated ones in the manager
        map_add_level = []
        for mgr in all_mgrs:
            for mgr_1 in all_mgrs:
                for mgr_children1 in mgr_1["children"]:
                    if mgr_children1["_id"] == mgr["_id"]:
                        map_add_level.append(mgr["_id"])

        all_emp_in_mgrs_table = list(filter(lambda d: d['_id'] not in map_add_level, all_mgrs))
        all_roles = mongo.db.role.find()
        all_roles1 = [doc for doc in all_roles]

        for mgr_emp in all_emp_in_mgrs_table:
            for role in all_roles1:
                if role["_id"] == mgr_emp["manager_role_id"]:
                    mgr_emp["manager_role_description"] = role["role_name"]

                for mgr_children in mgr_emp["children"]:
                    for role1 in all_roles1:
                        if 'user_manager_id' in mgr_children:
                            if role1["_id"] == mgr_children["user_role_id"]:
                                mgr_children["manager_role_description"] = role1["role_name"]

                                if 'children' in mgr_children:
                                    for mgr_grand_children in mgr_children["children"]:
                                        for role2 in all_roles1:
                                            if role2["_id"] == mgr_grand_children["user_role_id"]:
                                                mgr_grand_children["manager_role_description"] = role2["role_name"]

        # Is there any other employees (other than the one in the manager's table) reporting directly to CEO
        # map_all_mgr = list(map(lambda x: x['_id'], all_mgrs))
        # all_emp_not_in_mgr_table = list(filter(lambda d: d['_id'] not in map_all_mgr, all_emp)) #All emp not in mgr table
        # arr1 = np.array(all_emp_in_mgrs_table)
        #
        # arr2 = np.array(all_emp_not_in_mgr_table)
        #
        # all_emp_in_mgrs_table = np.concatenate((arr1, arr2))

    else:
        all_emp_in_mgrs_table = []
        all_emp_in_mgrs_table = no_of_employees

    return render_template("admin/edit_department.html",
                           form=form,
                           one_department=one_department,
                           came_from="admin.adminHome",
                           all_emp_in_mgrs_table=all_emp_in_mgrs_table,
                           no_of_employees=len(no_of_employees))


@app.route("/editDepartmentPOST/<int:id>", methods=['GET', 'POST'])
def editingDepartmentPOST(id):
    # Insert the employees  data into the employees collection
    form = InformForm()

    # Update the employees  data into the employees collection
    mongo.db.departments.update_one(
        {'_id': id},
        {'$set': {'department_name': request.form.get('department_name')}})
    return redirect(url_for("admin.adminHome"))


# ********************************** CREATEING A NEW EMPLOYEE TYPE ************************** #
@app.route("/createNewEmployeeType", methods=['GET', 'POST'])
def createNewEmployeeTypeGET():
    form = InformForm()
    return render_template("admin/new_employee_type.html",
                           form=form,
                           came_from="admin.adminHome")


@app.route("/createNewEmployeeTypePOST", methods=['GET', 'POST'])
def createNewEmployeeTypePOST():
    # Insert the employees  data into the employees collection
    mongo.db.employee_type.insert_one({
        '_id': random_id_generation.generating_random_id_employee_type(),
        'employee_type_description': request.form.get('employee_type_description')
    })
    return redirect(url_for("admin.adminHome"))


@app.route("/editEmployeeType/<int:id>", methods=['GET', 'POST'])
def editingEmployeeTypeGET(id):
    # Insert the employees  data into the employees collection
    form = InformForm()
    one_employee_type = mongo.db.employee_type.find_one({"_id": id})
    return render_template("admin/edit_employee_type.html",
                           form=form,
                           one_employee_type=one_employee_type,
                           came_from="admin.adminHome")


@app.route("/editingEmployeeTypePOST/<int:id>", methods=['GET', 'POST'])
def editingEmployeeTypePOST(id):
    # Insert the employees  data into the employees collection
    form = InformForm()

    # Update the employees  data into the employees collection
    mongo.db.employee_type.update_one(
        {'_id': id},
        {'$set': {'employee_type_description': request.form.get('employee_type_description')}})
    return redirect(url_for("admin.adminHome"))


# ********************************** CREATING A NEW ROLE ************************** #
@app.route("/createNewRole", methods=['GET', 'POST'])
def createNewRoleGET():
    form = InformForm()
    fetch_all_departments = [doc for doc in mongo.db.departments.find()]

    return render_template("admin/new_role.html",
                           form=form,
                           display_all_departments=fetch_all_departments,
                           came_from="admin.adminHome")


@app.route("/createNewRolePOST", methods=['GET', 'POST'])
def createNewRolePOST():
    form = InformForm()
    # Insert the employees  data into the employees collection
    mongo.db.role.insert_one({
        '_id': random_id_generation.generating_random_id_role(),
        'role_name': request.form.get('role_name'),
    })
    return redirect(url_for("admin.adminHome"))


@app.route("/editRole/<int:id>", methods=['GET', 'POST'])
def editingRoleGET(id):
    # Insert the employees  data into the employees collection
    form = InformForm()
    one_role = mongo.db.role.find_one({"_id": id})

    fetch_all_departments = [doc for doc in mongo.db.departments.find()]
    return render_template("admin/edit_role.html",
                           form=form,
                           display_all_departments=fetch_all_departments,
                           one_role=one_role,
                           came_from="admin.adminHome")


@app.route("/editingRolePOST/<int:id>", methods=['GET', 'POST'])
def editingRolePOST(id):
    # Insert the employees  data into the employees collection
    form = InformForm()
    found_one_from_db_before_json = mongo.db.role.find_one({"_id": id})
    fetched_one_value_before_json = {
        '_id': id,
        "role_name": found_one_from_db_before_json['role_name'],
    }

    converted_json = json.dumps(fetched_one_value_before_json, sort_keys=True)
    fetched_value_before_json = {
        '_id': id,
        "role_name": request.form.get('role_name'),
    }

    fetched_val_json = json.dumps(fetched_value_before_json, sort_keys=True)

    collect_data_to_append = {}
    if converted_json == fetched_val_json:
        print("They are Exactly the same, so don't update the db")
    else:
        if fetched_value_before_json["role_name"] != fetched_one_value_before_json["role_name"]:
            collect_data_to_append["role_name"] = fetched_value_before_json["role_name"]

        # Update the employees  data into the employees collection
        mongo.db.role.update_one(
            {'_id': id},
            {'$set': collect_data_to_append}
        )

    return redirect(url_for("admin.adminHome"))


# Function to convert the date format
def convert24(str1):
    # Checking if last two elements of time
    # is AM and first two elements are 12
    if str1[-2:] == "AM" and str1[:2] == "12":
        return "00" + str1[2:-2]

    # remove the AM
    elif str1[-2:] == "AM":
        return str1[:-2]

    # Checking if last two elements of time
    # is PM and first two elements are 12
    elif str1[-2:] == "PM" and str1[:2] == "12":
        return str1[:-2]

    else:

        # add 12 to hours and remove PM
        return str(int(str1[:2]) + 12) + str1[2:8]


# ********************************** CREATING CALENDAR EVENT ***************************** #
@app.route("/createNewEventPost", methods=['GET', 'POST'])
def createNewEventPost():
    form = InformForm()
    # TODO we may need to show all the employees list

    # TODO remove this
    today = datetime.now()
    set_min_date = today.strftime("%Y-%m-%d")
    strp_today = today.strftime("%Y-%m-%d %H:%M")
    curr_date_time = datetime.strptime(strp_today, "%Y-%m-%d %H:%M")
    timestamp_current_date_time = datetime.timestamp(curr_date_time)

    if (form.validate_on_submit()):
        return redirect(url_for("date"))

    all_employees = database_connection.connect_employee_table_name()
    all_managers = database_connection.connect_manager_table_name()
    display_all_managers = database_connection.manager_table(all_managers)

    return render_template('admin/new_event_creation.html',
                           form=form,
                           display_all_employees=database_connection.employee_table(all_employees),
                           display_all_managers=display_all_managers,
                           str_display_all_mgr=json.dumps(display_all_managers),
                           min_date=set_min_date)


@app.route("/admin/calendar", methods=['POST'])
def date():
    form = InformForm()

    # TODO Need to validate and some logics
    # https://www.dataquest.io/blog/python-datetime-tutorial/
    start_date_split = request.form.get('startdate').split("-")
    start_at_split = request.form.get('start_at').split(":")

    end_date_split = request.form.get('enddate').split("-")
    end_at_split = request.form.get('end_at').split(":")

    # date1 = datetime(int(start_date_split[0]), int(start_date_split[1]), int(start_date_split[2]), int(start_at_split[0]), int(start_at_split[1]), 00)
    # date2 = datetime(int(end_date_split[0]), int(end_date_split[1]), int(end_date_split[2]), int(end_at_split[0]), int(end_at_split[1]), 00)
    #
    # diff = date2 - date1


    form = InformForm()

    if not request.form.get("employee_id") or not request.form.get("manager_id"):
        requestForm = {}
        error = []

        if not request.form.get("employee_id"):
            error.append("Please Select the Employee Name")
        elif request.form.get("employee_id"):
            requestForm.update({'employee_id': int(request.form.get("employee_id"))})

        if not request.form.get("manager_id"):
            error.append("Please Select the Reporting Manager")
        elif request.form.get("manager_id"):
            requestForm.update({'manager_id': int(request.form.get("manager_id"))})

        all_employees = database_connection.connect_employee_table_name()
        all_managers = database_connection.connect_manager_table_name()
        return render_template('admin/new_event_creation.html',
                               form=form,
                               error=error,
                               requestForm=requestForm,
                               display_all_employees=database_connection.employee_table(all_employees),
                               display_all_managers=database_connection.manager_table(all_managers))
    elif int(request.form.get('employee_id')) == int(request.form.get('manager_id')):
        error = []
        error.append("Employee and Manager cannot be the same")
        requestForm = {
            'employee_id': int(request.form.get('employee_id')),
            'manager_id': int(request.form.get('manager_id'))
        }
        all_employees = database_connection.connect_employee_table_name()
        all_managers = database_connection.connect_manager_table_name()
        return render_template('admin/new_event_creation.html',
                               form=form,
                               error=error,
                               requestForm=requestForm,
                               display_all_employees=database_connection.employee_table(all_employees),
                               display_all_managers=database_connection.manager_table(all_managers))
    else:
        requestForm = {
            "employee_id": int(request.form.get("employee_id")),
            "manager_id": int(request.form.get("manager_id"))
        }

        dt_object1 = datetime.strptime(request.form.get('startdate') + ' ' + request.form.get('start_at'),
                                       "%Y-%m-%d %H:%M")
        dt_object2 = datetime.strptime(request.form.get('enddate') + ' ' + request.form.get('end_at'), "%Y-%m-%d %H:%M")
        timestamp = datetime.timestamp(dt_object2)
        timestamp2 = datetime.timestamp(dt_object1)

        # split_start_date = request.form.get('startdate').split('-')
        # split_end_date = request.form.get('enddate').split('-')
        # split_start_at = str(converted_start_date).split(':')
        # split_end_at = str(converted_end_date).split(':')
        #
        # d1 = datetime(int(split_start_date[0]), int(split_start_date[1]), int(split_start_date[2]), int(split_start_at[0]),
        #               int(split_start_at[1]))
        # d2 = datetime(int(split_end_date[0]), int(split_end_date[1]), int(split_end_date[2]), int(split_end_at[0]), int(split_end_at[1]))
        #

        # Today's timestamp
        today = datetime.now()
        strp_today = today.strftime("%Y-%m-%d %H:%M")
        curr_date_time = datetime.strptime(strp_today, "%Y-%m-%d %H:%M")
        timestamp_current_date_time = datetime.timestamp(curr_date_time)

        today = datetime.now()

        error = []
        if (timestamp == timestamp2):
            # flash("Start date and End date are same, please try to enter the start date to be less than the end date")
            error.append(
                'Start date and End date are same, please try to enter the start date to be less than the end date')
            all_employees = database_connection.connect_employee_table_name()
            all_managers = database_connection.connect_manager_table_name()
            return render_template('admin/new_event_creation.html',
                                   form=form,
                                   display_all_employees=database_connection.employee_table(all_employees),
                                   display_all_managers=database_connection.manager_table(all_managers), error=error,
                                   requestForm=requestForm)

        elif (float(timestamp) < float(timestamp2)):
            error.append('Looks like the start date is greater than end date')

            all_employees = database_connection.connect_employee_table_name()
            all_managers = database_connection.connect_manager_table_name()
            return render_template('admin/new_event_creation.html',
                                   form=form,
                                   display_all_employees=database_connection.employee_table(all_employees),
                                   display_all_managers=database_connection.manager_table(all_managers), error=error,
                                   requestForm=requestForm)
        else:
            mongo.db.workSchedule.insert_one({
                'employee_id': int(request.form.get('employee_id')),
                'title': request.form.get('title'),
                'start': request.form.get('startdate') + 'T' + request.form.get('start_at'),
                'end': request.form.get('enddate') + 'T' + request.form.get('end_at'),
                'manager_id': int(request.form.get('manager_id'))})
            return redirect(url_for("admin.getFullCalendar"))


@app.route("/postAnExistingEvent/<int:toggle>/<id>", methods=['POST'])
def postAnExistingEventData(id, toggle):
    requestForm = {
        "employee_id": int(request.form.get("employee_id")),
        "manager_id": int(request.form.get("manager_id"))
    }
    form = InformForm()
    #
    value_date1 = request.form.get('startdate') + ' ' + request.form.get('start_at')

    # converted_start_at = convert24(request.form.get('start_at'))
    # converted_end_at = convert24(request.form.get('end_at'))
    if (request.form.get('startdate') and request.form.get('start_at')) and (
            request.form.get('enddate') and request.form.get('end_at')):
        ############# START AT ###############
        if len(request.form.get('start_at')) >= 8:
            dt_object1 = datetime.strptime(request.form.get('startdate') + ' ' + request.form.get('start_at'),
                                           "%Y-%m-%d %H:%M:%S")
        else:
            dt_object1 = datetime.strptime(request.form.get('startdate') + ' ' + request.form.get('start_at'),
                                           "%Y-%m-%d %H:%M")

        ############# END AT ###############
        if len(request.form.get('end_at')) >= 8:
            dt_object2 = datetime.strptime(request.form.get('enddate') + ' ' + request.form.get('end_at'),
                                           "%Y-%m-%d %H:%M:%S")
        else:
            dt_object2 = datetime.strptime(request.form.get('enddate') + ' ' + request.form.get('end_at'),
                                           "%Y-%m-%d %H:%M")

    else:
        error = 'Please check the entry for Start date and time or end date and time'
        all_employees = database_connection.connect_employee_table_name()
        all_managers = database_connection.connect_manager_table_name()
        one_element = {
            "_id": ObjectId(id),
            "employee_id": int(request.form.get("employee_id")),
            "manager_id": int(request.form.get("manager_id")),
            "title": request.form.get("title"),
            'start': request.form.get('startdate') + 'T' + request.form.get('start_at'),
            'end': request.form.get('enddate') + 'T' + request.form.get('end_at'),
        }
        return render_template('admin/edit_event_creation.html',
                               form=form,
                               display_all_employees=database_connection.employee_table(all_employees),
                               display_all_managers=database_connection.manager_table(all_managers),
                               error=error,
                               toggle=toggle,
                               requestForm=requestForm,
                               fetched_data=one_element)

    timestamp = datetime.timestamp(dt_object2)
    timestamp2 = datetime.timestamp(dt_object1)
    error = None


    if (timestamp == timestamp2):

        one_element = {
            "_id": ObjectId(id),
            "employee_id": int(request.form.get("employee_id")),
            "manager_id": int(request.form.get("manager_id")),
            "title": request.form.get("title"),
            'start': request.form.get('startdate') + 'T' + request.form.get('start_at'),
            'end': request.form.get('enddate') + 'T' + request.form.get('end_at'),
        }

        # flash("Start date and End date are same, please try to enter the start date to be less than the end date")
        error = 'Start date and End date are same, please try to enter the start date to be less than the end date'
        all_employees = database_connection.connect_employee_table_name()
        all_managers = database_connection.connect_manager_table_name()
        return render_template('admin/edit_event_creation.html',
                               form=form,
                               display_all_employees=database_connection.employee_table(all_employees),
                               display_all_managers=database_connection.manager_table(all_managers),
                               error=error,
                               toggle=toggle,
                               requestForm=requestForm,
                               fetched_data=one_element)
    elif (float(timestamp) < float(timestamp2)):
        one_element = {
            "_id": ObjectId(id),
            "employee_id": int(request.form.get("employee_id")),
            "manager_id": int(request.form.get("manager_id")),
            "title": request.form.get("title"),
            'start': request.form.get('startdate') + 'T' + request.form.get('start_at'),
            'end': request.form.get('enddate') + 'T' + request.form.get('end_at'),
        }
        error = 'Looks like the start date is greater than end date'
        all_employees = database_connection.connect_employee_table_name()
        all_managers = database_connection.connect_manager_table_name()
        return render_template('admin/edit_event_creation.html',
                               form=form,
                               display_all_employees=database_connection.employee_table(all_employees),
                               display_all_managers=database_connection.manager_table(all_managers),
                               error=error,
                               toggle=toggle,
                               requestForm=requestForm,
                               fetched_data=one_element)

    else:
        found_one_from_db_before_json = database_connection.fetch_only_one_work_schedule(ObjectId(id))

        del found_one_from_db_before_json["_id"]
        converted_json = json.dumps(found_one_from_db_before_json, sort_keys=True)
        fetched_value_before_json = {
            'employee_id': int(request.form.get('employee_id')),
            'title': request.form.get('title'),
            'manager_id': int(request.form.get('manager_id')),
            'start': request.form.get('startdate') + 'T' + request.form.get('start_at'),
            'end': request.form.get('enddate') + 'T' + request.form.get('end_at'),
        }
        fetched_val_json = json.dumps(fetched_value_before_json, sort_keys=True)

        collect_data_to_append = {}
        if converted_json == fetched_val_json:
            print("They are Exactly the same, so don't update the db")
        else:
            if fetched_value_before_json["employee_id"] != found_one_from_db_before_json["employee_id"]:
                collect_data_to_append["employee_id"] = fetched_value_before_json["employee_id"]
            if fetched_value_before_json["title"] != found_one_from_db_before_json["title"]:
                collect_data_to_append["title"] = fetched_value_before_json["title"]
            if fetched_value_before_json["manager_id"] != found_one_from_db_before_json["manager_id"]:
                collect_data_to_append["manager_id"] = fetched_value_before_json["manager_id"]
            if fetched_value_before_json["start"] != found_one_from_db_before_json["start"]:
                collect_data_to_append["start"] = fetched_value_before_json["start"]
            if fetched_value_before_json["end"] != found_one_from_db_before_json["end"]:
                collect_data_to_append["end"] = fetched_value_before_json["end"]

            mongo.db.workSchedule.update_one(
                {'_id': ObjectId(id)},
                {'$set': collect_data_to_append}
            )
        if toggle == 1:
            return redirect(url_for('admin.getFullCalendar'))
        else:
            return redirect(url_for('admin.getEditEmployeeEventCalendar', empId=requestForm['employee_id']))
            # return redirect(url_for('admin.getFullCalendar'))


# Delete an Event
@app.route("/deleteEvent/<id>/<int:toggle>/empId/<int:coming_from_emp_edit_screen>")
def deleteEvent(id, toggle, coming_from_emp_edit_screen):
    mongo.db.workSchedule.delete_one({'_id': ObjectId(id)})

    # Toggle says from where it is coming from and where u want to go
    if toggle == 1:
        return redirect(url_for('admin.getFullCalendar'))
    else:
        return redirect(url_for('admin.getEditEmployeeEventCalendar', empId=coming_from_emp_edit_screen))


@app.route("/help")
def help():
    return render_template("shared-component/help.html")


@app.route('/plot.png')
def plot_png():
    fig = create_figure()
    output = io.BytesIO()
    FigureCanvas(fig).print_png(output)
    return Response(output.getvalue(), mimetype='image/png')


def create_figure():
    fig = Figure()
    axis = fig.add_subplot(1, 1, 1)
    xs = range(100)
    ys = [random.randint(1, 50) for x in xs]
    axis.plot(xs, ys)
    return fig


if __name__ == '__main__':
    app.run(port=5001, debug=True)
