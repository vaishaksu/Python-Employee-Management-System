import database_connection
from random import randrange

login_table_name = database_connection.connect_login_table()
employee_table_name = database_connection.connect_employee_table_name()
department_table_name = database_connection.connect_department_table_name()
employee_type_name = database_connection.connect_employee_type_table_name()
role_table_name = database_connection.connect_role_table_name()
fs_files_table_name = database_connection.connect_fs_files()


# Generating a new random id for Login
def generating_random_id_login():
    i = 1
    all_login_info = database_connection.login_table(login_table_name)
    while i > 0:
        random_id_generator = randrange(1, 1000000)

        # Fetch only the Id only for comparing
        result = map(lambda x: x["_id"], all_login_info)
        not_in_list = random_id_generator not in list(result)
        if not_in_list:
            i = 0
            return random_id_generator
        else:
            i = 1

# Generating a new random id for employees
def generating_random_id_employees():
    i = 1
    while (i > 0):
        random_id_generator = randrange(1, 1000000)
        all_employees_find = employee_table_name.find()

        # Fetch only the Id only for comparing
        result = map(lambda x: x["_id"], all_employees_find)
        not_in_list = random_id_generator not in list(result)
        if (not_in_list):
            i = 0
            return random_id_generator
        else:
            i = 1

# Generating a new random id for Department
def generating_random_id_departments():
    i = 1
    while (i > 0):
        random_id_generator = randrange(1, 1000000)
        all_departments_find = department_table_name.find()

        # Fetch only the Id only for comparing
        result = map(lambda x: x["_id"], all_departments_find)
        not_in_list = random_id_generator not in list(result)
        if (not_in_list):
            i = 0
            return random_id_generator
        else:
            i = 1

# Generating a new random id for employees_type
def generating_random_id_employee_type():
    i = 1
    while (i > 0):
        random_id_generator = randrange(1, 1000000)
        all_employee_type_find = employee_type_name.find()

        # Fetch only the Id only for comparing
        result = map(lambda x: x["_id"], all_employee_type_find)
        not_in_list = random_id_generator not in list(result)
        if (not_in_list):
            i = 0
            return random_id_generator
        else:
            i = 1

# Generating a new random id for role
def generating_random_id_role():
    i = 1
    while i > 0:
        random_id_generator = randrange(1, 1000000)
        all_role_find = role_table_name.find()

        # Fetch only the Id only for comparing
        result = map(lambda x: x["_id"], all_role_find)
        not_in_list = random_id_generator not in list(result)
        if not_in_list:
            i = 0
            return random_id_generator
        else:
            i = 1

def generating_random_id_profile_picture():
    # Generating a new random id for employees
    i = 1

    while (i > 0):
        random_id_generator = randrange(1, 1000000000000000000000000000000000)
        print("uniq: ", fs_files_table_name.find())
        all_employee_type_find = [docss for docss in fs_files_table_name.find()]

        # Fetch only the Id only for comparing
        result = map(lambda x: x["filename"], all_employee_type_find)
        not_in_list = str(random_id_generator) not in list(result)
        if (not_in_list):
            i = 0
            return str(random_id_generator)
        else:
            i = 1