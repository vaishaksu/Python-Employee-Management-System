import pymongo

# ***************************Database Connection ********************************* #
from bson import ObjectId


def database_connection():
    connection_string = "mongodb+srv://Username:Password@cluster0.j1u4m.mongodb.net/EmployeeManagementSystem?retryWrites=true&w=majority"
    my_client = pymongo.MongoClient(connection_string)
    database_name = my_client["EmployeeManagementSystem"]
    return database_name


# Connect the table only to login
def connect_login_table():
    database_name = database_connection()
    login_table_name = database_name["login"]
    return login_table_name


# Connect the table only to employees
def connect_employee_table_name():
    database_name = database_connection()
    employee_table_name = database_name["employees"]
    return employee_table_name


# Connect the table only to employees
def connect_employee_type_table_name():
    database_name = database_connection()
    employee_type_table_name = database_name["employee_type "]
    return employee_type_table_name


# Connect the table only to role
def connect_role_table_name():
    database_name = database_connection()
    role_table_name = database_name["role"]
    return role_table_name


# Connect to work_schedule
def connect_workSchedule_table_name():
    database_name = database_connection()
    workSchedule_table_name = database_name["workSchedule"]
    return workSchedule_table_name


# Connect the table only to Manager
def connect_manager_table_name():
    database_name = database_connection()
    managers_table_name = database_name["managers"]
    return managers_table_name


# Connect the table only to role
def connect_department_table_name():
    database_name = database_connection()
    department_table_name = database_name["departments"]
    return department_table_name


def connect_employees_role_table_department():
    database_name = database_connection()
    employee_table_name = database_name["employees"]
    role_table_name = database_name["role"]
    department_table_name = database_name["departments"]
    return {"employee": employee_table_name, "role": role_table_name, "department": department_table_name}

def connect_role_dept_mgr_table():
    database_name = database_connection()
    role_table_name = database_name["role"]
    department_table_name = database_name["departments"]
    manager_table_name = database_name["managers"]
    return {"role": role_table_name, "department": department_table_name, "manager": manager_table_name}


# Fetching all the table names to make life easier
def fetch_all_tables():
    database_name = database_connection()
    login_table_name = database_name["login"]
    employee_table_name = database_name["employees"]
    role_table_name = database_name["role"]
    manager_table_name = database_name["managers "]

    return {"login": login_table_name, "employee": employee_table_name, "role": role_table_name,
            'manager': manager_table_name}


def merge_employee_role(status):
    emp_role = connect_employees_role_table_department()
    if status == 'home':
        emp = employee_table(emp_role["employee"])
    else:
        emp = status
    role = role_table(emp_role["role"])
    dept = department_table(emp_role["department"])

    merged_array = []
    for employee in emp:
        for rol in role:
            if employee["user_role_id"] == rol["_id"]:
                employee["role"] = rol["role_name"]

                for department in dept:
                    if employee["department_id"] == department["_id"]:
                        employee["department_name"] = department["department_name"]
                        merged_array.append(employee)
    return merged_array


def login_table(login):
    fetch_values = login.find()
    login_user = [record for record in fetch_values]
    return login_user


def employee_table(employee):
    fetch_values = employee.find()
    employee_user = [record for record in fetch_values]
    return employee_user


def department_table(department):
    fetch_values = department.find()
    department_user = [record for record in fetch_values]
    return department_user


def role_table(role):
    fetch_values = role.find()
    role_user = [record for record in fetch_values]
    return role_user


def workSchedule_table(schedule):
    fetch_values = schedule.find()
    schedule_user = [record for record in fetch_values]
    return schedule_user


def manager_table(manager):
    fetch_values = manager.find()
    manager_user = [record for record in fetch_values]
    return manager_user


def fetch_only_one_manager(id):
    fetch_one = connect_manager_table_name()
    query = {'_id': id}
    find_one_mgr = fetch_one.find_one(query)
    return find_one_mgr


def fetch_only_one_employee(id):
    fetch_one = connect_employee_table_name()
    query = {'_id': id}
    find_one_employee = fetch_one.find_one(query)
    return find_one_employee


def fetch_only_one_work_schedule(id):
    fetch_one = connect_workSchedule_table_name()
    query = {'_id': ObjectId(id)}
    find_one_employee = fetch_one.find_one(query)
    return find_one_employee


def fetch_work_schedule_particular_emp(empId):
    fetch_one = connect_workSchedule_table_name()
    query = {'employee_id': empId}
    find_work_schedule_emp = [doc for doc in fetch_one.find(query)]
    return find_work_schedule_emp


def fetch_employee_search_name(values):
    connected_employees = connect_employee_table_name()

    # the below query will fetch all case insensitive characters
    fetch_me = connected_employees.find({"$or": [{"first_name": {"$regex": f".*{values}.*", "$options": 'i'}},
                                                 {"last_name": {"$regex": f".*{values}.*", "$options": 'i'}}]})

    overall_fetch = [doc for doc in fetch_me]
    return overall_fetch


def fetch_active_inactive_employee(status):
    fetch_one = connect_employee_table_name()
    if status == 'all':
        find_staus_employee = fetch_one.find()
    else:
        find_staus_employee = fetch_one.find({'is_active': status})
    fetch_status_employee = [doc for doc in find_staus_employee]

    return fetch_status_employee


# Connect to Employee_type
def connect_fs_files():
    database_name = database_connection()
    fs_files_table_name = database_name["fs.files"]
    return fs_files_table_name


# Connect to Employee_type
def connect_employee_type_table_name():
    database_name = database_connection()
    employee_type_table_name = database_name["employee_type"]
    return employee_type_table_name


def employee_type_table(emp_type):
    fetch_values = emp_type.find()
    emp_type_user = [record for record in fetch_values]
    return emp_type_user

def merge_employee_one_role(id):
    emp_role = connect_employees_role_table_department()
    emp = fetch_only_one_employee(id)

    role = role_table(emp_role["role"])
    dept = department_table(emp_role["department"])

    merged_array = []
    for rol in role:
        if emp["user_role_id"] == rol["_id"]:
            emp["role"] = rol["role_name"]

            for department in dept:
                if (emp["department_id"] == department["_id"]):
                    emp["department_name"] = department["department_name"]
                    merged_array.append(emp)
    return merged_array
