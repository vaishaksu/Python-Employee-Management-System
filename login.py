from flask import Blueprint, render_template, request, session, redirect, url_for, app
from datetime import datetime
from flask import Flask, request, render_template, url_for, session, redirect, flash
from flask_pymongo import PyMongo
import database_connection
import random_id_generation
import json
from flask_wtf import FlaskForm
from wtforms import Form, BooleanField, StringField, PasswordField, validators
from wtforms.fields.html5 import DateTimeLocalField, EmailField
import logging
from random import randrange

login = Blueprint("login", __name__, static_folder="static", template_folder="templates")

# Login table name
login_table_name = database_connection.connect_login_table()
employee_table_name = database_connection.connect_employee_table_name()


class LoginForm(FlaskForm):
    username = StringField('Username', [validators.DataRequired()])
    email_address = EmailField('Email Address', validators=(validators.DataRequired(), validators.Email()))
    first_name = StringField('First Name', [validators.DataRequired()])
    last_name = StringField('Last Name', [validators.DataRequired()])
    password = PasswordField('New Password', [
        validators.DataRequired(),
        validators.EqualTo('confirm', message='Passwords must match')
    ])
    confirm = PasswordField('Repeat Password')
    accept_tos = BooleanField('I accept the TOS', [validators.DataRequired()])


@login.route("/")
def login_info():
    if 'username' in session:
        session.clear()  # Clear the session
    form = LoginForm()
    return render_template("shared-component/login.html",
                           form=form)


@login.route("/register")
def register():
    if 'username' in session:
        session.clear()  # Clear the session
    form = LoginForm()
    return render_template("shared-component/RegistrationForm.html",
                           form1=form)


@login.route("/signupPOST", methods=["GET", "POST"])
def signupPostData():
    error = []
    if request.form.get('password') != request.form.get('confirm'):
        form = LoginForm()
        error.append("Password doesn't match")
        logging.critical("Password doesn't match")
        return render_template("shared-component/RegistrationForm.html",
                               error=error,
                               form1=form)
    else:
        insert_data = {
            "_id": random_id_generation.generating_random_id_login(),
            "username": request.form.get('username'),
            "password": request.form.get('password'),
            "remember_me": request.form.get('remember'),
            "first_name": request.form.get('first_name'),
            "last_name": request.form.get('last_name'),
            "email_address": request.form.get('email_address')
        }

        login_table_name.insert_one(insert_data)
        logging.warning("Successfully Inserted")
        print(request.form)
        return redirect(url_for('login.login_info'))


def loginComparison(all_login_info, username, password):
    count = 1
    index = 0
    boolValue = False
    print(request.form)
    while count > 0:
        if index < len(all_login_info):
            if all_login_info[index][username] == request.form.get(username) and all_login_info[index][
                password] == request.form.get(password):
                count = 0
                boolValue = True
                data = {
                    'booleanValue': boolValue,
                    'one_data': all_login_info[index]
                }
                return data
            else:  # SUCCESS
                count += 1
                boolValue = False
            index += 1
        else:
            count = 0


@login.route("/login_validation", methods=["POST"])
def login_validationPost():
    # Fetch all the data from the Login Collection
    all_login_info = database_connection.login_table(login_table_name)
    login_check = loginComparison(all_login_info, 'username', 'password')

    error = []
    print("user12: ", login_check)
    if login_check:
        session['username'] = login_check['one_data']['username']
        session['first_name'] = login_check['one_data']['first_name']
        session['last_name'] = login_check['one_data']['last_name']
        session['is_admin'] = login_check['one_data']['is_admin']
        # session['_id'] = login_check['one_data']['_id']
        # session['email_address'] = login_check['one_data']['email_address']

        if login_check['one_data']['is_admin']:
            print("Reditct him to Sdmin oage: ", session)
            return redirect(url_for("admin.adminHome"))
        else:
            print("to notmal emp page")
            query = {
                'username': request.form.get('username')
            }
            fetch_employee_one = employee_table_name.find_one(query)
            session['employee_id'] = fetch_employee_one['_id']
            print("1233 ***-+595* : ", fetch_employee_one)

            # TODO: Redirect to Employee page
            return redirect(url_for('employees.home'))
    else:
        error.append("Username and password doesn't match")
        form = LoginForm()
        return render_template("shared-component/login.html",
                               form=form,
                               error=error)


@login.route("/forgotPassword")
def forgotPasswordGET():
    form = LoginForm()
    return render_template("shared-component/forgot-password.html",
                           form=form)


@login.route("/resetPassword", methods=["GET", "POST"])
def resetPassword():
    all_login_info = database_connection.login_table(login_table_name)
    login_check = loginComparison(all_login_info, 'username', 'email_address')

    form = LoginForm()

    if login_check:
        if request.form.get('password') and request.form.get('confirm'):
            if request.form.get('password') == request.form.get('confirm'):
                login_table_name.update_one(
                    {'_id': login_check['one_data']['_id']},
                    {'$set': {'password': request.form.get('password')}}
                )
                return redirect(url_for('login.login_info'))
            else:
                error = ["Looks like password and confirm password doesn't match"]
                return render_template("shared-component/forgot-password.html",
                                       form=form,
                                       show_password=True,
                                       error=error)

        return render_template("shared-component/forgot-password.html",
                               form=form,
                               show_password=True)
    else:
        error = ["Username and Email address doesn't match our record. Please try again! or contact your admin"]

        return render_template("shared-component/forgot-password.html",
                               form=form,
                               error=error)
