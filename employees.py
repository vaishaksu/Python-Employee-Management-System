from flask import Flask, request, render_template, url_for, session, redirect, flash
from datetime import datetime
from flask import Blueprint, render_template
import database_connection
import json
from flask_wtf import FlaskForm
from wtforms import BooleanField, TextAreaField, IntegerField
from wtforms.fields.html5 import DateField, TimeField
from wtforms.validators import DataRequired, required, NumberRange, Optional
from wtforms import validators, SubmitField, StringField
from wtforms.fields.html5 import DateTimeLocalField, EmailField
from wtforms_components import DateRange
from bson import ObjectId
from random import randrange
from wtforms.fields import html5 as h5fields
from wtforms.widgets import html5 as h5widgets
from dateutil.relativedelta import relativedelta

department_db = database_connection.connect_department_table_name()
employee_type_db = database_connection.connect_employee_type_table_name()
employee_table_name_db = database_connection.connect_employee_table_name()
manager_table_name_db = database_connection.connect_manager_table_name()
all_roles = database_connection.connect_role_table_name()

gender_array = ['Not Ready to Declare', 'Male', 'Female']

employees = Blueprint("employees", __name__, static_folder="static", template_folder="templates")


class InformForm(FlaskForm):
    title = StringField('Title', validators=[DataRequired()])
    startdate = DateField('Start Date', format="%Y-%m-%d", validators=(validators.DataRequired(),))
    enddate = DateField('End Date', format="%Y-%m-%d", validators=(validators.DataRequired(),))
    start_at = TimeField('Start at', format="'%h-%m'", validators=[DateRange(min=datetime.now())])
    end_at = TimeField('End at', format="'%h-%m'", validators=[DateRange(min=datetime.now())])
    date_of_joining = DateField('Date of Joining', format="%Y-%m-%d", validators=(validators.DataRequired(),))
    date_of_birth = DateField('Date Of Birth', format="%Y-%m-%d", validators=(validators.DataRequired(),))
    last_date = DateField('Last Date', format="%Y-%m-%d", )
    official_email_address = EmailField('Official Email address',
                                        validators=(validators.DataRequired(), validators.Email()))
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


@employees.route("/")
# @employees.route("/<int:id>")
def home():
    if 'employee_id' in session:
        employees_one = database_connection.merge_employee_one_role(session['employee_id'])
        session['employee_id'] = session['employee_id']
        print("-----: ", session)
        for employee in employees_one:
            employee["date_of_joining"] = datetime.strptime(employee["date_of_joining"],
                                                            '%Y-%m-%dT%H:%M%S').strftime("%B %d, %Y")

        return render_template("employees/employee-info.html", display_all_employees=employees_one,
                               came_from="employees.home",
                               search_result="")
    else:
        return redirect(url_for('login.login_info'))


@employees.route("/editEmployee/<int:id>")
def editEmployee(id):
    # Fetch only the particular employee whose Id matches in the database
    dbdepartment = database_connection.department_table(department_db)
    db_employee_type = database_connection.employee_type_table(employee_type_db)
    find_one = database_connection.fetch_only_one_employee(id)
    form = InformForm()
    twenty_yrs_ago = datetime.now() - relativedelta(years=20)
    strp_today = twenty_yrs_ago.strftime("%Y-%m-%d")

    print("***************** ", find_one)
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
    print(dbdepartment)
    fetch_all_departments = [doc for doc in dbdepartment]
    fetch_all_employee_type = [doc for doc in db_employee_type]

    all_managers = database_connection.connect_manager_table_name()
    session['first_name'] = find_one['first_name']
    session['last_name'] = find_one['last_name']

    return render_template("employees/employee.html",
                           form=form,
                           one_employee=find_one,
                           display_all_roles=database_connection.role_table(all_roles),
                           display_all_managers=database_connection.manager_table(all_managers),
                           display_all_departments=fetch_all_departments,
                           display_all_employee_type=fetch_all_employee_type,
                           came_from="admin.adminHome",
                           gender_array=gender_array,
                           twenty_yrs_ago=strp_today)


@employees.route("/EditEmployee/event/<int:empId>")
def getEditEmployeeEventCalendar(empId):
    events = database_connection.fetch_work_schedule_particular_emp(empId)
    return render_template("shared-component/employee_calendar.html", employee_id=empId, events=events,
                           login_employee_only=True)


@employees.route("/yourProfile")
def yourProfileInfo():
    if 'employee_id' in session:
        query = {
            "_id": session['employee_id']
        }
        fetch_empl_one = employee_table_name_db.find_one(query)

        fetch_empl_one["date_of_joining"] = datetime.strptime(fetch_empl_one["date_of_joining"],
                                                              '%Y-%m-%dT%H:%M%S').strftime("%B %d, %Y")
        fetch_empl_one["date_of_birth"] = datetime.strptime(fetch_empl_one["date_of_birth"],
                                                            '%Y-%m-%d').strftime("%B %d, %Y")

        # ROle find one Query
        role_find_one = all_roles.find_one({"_id": fetch_empl_one["user_role_id"]})

        # Department find one Query
        dept_find_one = department_db.find_one({"_id": fetch_empl_one["department_id"]})

        # Manager findOne Query
        mgr_find_one = manager_table_name_db.find_one({"_id": fetch_empl_one["user_manager_id"]})

        # Employee Type Query
        emp_type_one = employee_type_db.find_one({'_id': fetch_empl_one["employee_type_id"]})

        fetch_empl_one["role_name"] = role_find_one["role_name"]
        fetch_empl_one["department_name"] = dept_find_one["department_name"]
        fetch_empl_one["employee_type_description"] = emp_type_one["employee_type_description"]

        fetch_empl_one["manager_fullname"] = mgr_find_one["manager_first_name"] + " " + mgr_find_one[
            "manager_last_name"]

        # Again find the Managers role id
        fetch_role_mgr = all_roles.find_one({"_id": mgr_find_one["manager_role_id"]})
        fetch_empl_one["mgr_role_name"] = fetch_role_mgr["role_name"]

    return render_template("shared-component/yourProfileInfo.html",
                           employee=fetch_empl_one)


@employees.route("/getExistingEvent/<id>/<int:toggle>/empId/<int:employee_id>", methods=['GET', 'POST'])
def editExitEvent(id, toggle, employee_id):
    one_element = database_connection.fetch_only_one_work_schedule(ObjectId(id))
    print("DATE: ", one_element, toggle, employee_id)
    print("Session: ", session)

    form = InformForm()

    # TODO we may need to show all the employees list
    print("Session: ", session, 'employee_id' not in session)
    all_employees = database_connection.connect_employee_table_name()
    all_managers = database_connection.connect_manager_table_name()
    return render_template('admin/edit_event_creation.html',
                           form=form,
                           display_all_employees=database_connection.employee_table(all_employees),
                           display_all_managers=database_connection.manager_table(all_managers),
                           fetched_data=one_element,
                           show_all_btns=True if 'employee_id' not in session else None,
                           toggle=toggle,
                           coming_from_emp_edit_screen=employee_id)
