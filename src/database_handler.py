"""Petition interactions with the database."""

import math
import send_email
import sqlite3

def get_petitions(email):
    """Connects to database and gets list of petitions associated with the
    department of the input email."""
    conn = sqlite3.connect("petitiondb.sqlite3")  # connect to the database

    petition_results = []

    # Get department based on inputted email:
    department_query = "SELECT department FROM User_Table WHERE email = \"{A}\"".format(A = email)
    dept_query_obj = conn.execute(department_query)
    dept_tuple = dept_query_obj.fetchone()  # store results of query - in a tuple
    try:
        dept_result = dept_tuple[0]  # if query returns a result, store it as a string
    except:
        dept_result = ""  # if query returns no results/an error, set value as empty string

    # Find petitions for that department:
    petition_query = "SELECT name, email, department, petitionID FROM Student_Petition WHERE department = \"{A}\"".format(A = dept_result)
    petition_query_obj = conn.execute(petition_query)
    petition_list = petition_query_obj.fetchall()  # store results of query - in a tuple
    try:
        petition_results = petition_list # if query returns a result, store it as a string
    except:
        petition_results = ""  # if query returns no results/an error, set value as empty string

    return(petition_results)
    conn.close()


def get_petition_info(id):
    """Connects to the database and gets info about a specific petition."""
    conn = sqlite3.connect("petitiondb.sqlite3")  # connect to the database

    petition_query = "SELECT * FROM Student_Petition WHERE petitionID = \"{A}\"".format(A = id)
    petition_query_obj = conn.execute(petition_query)
    petition_tuple = petition_query_obj.fetchall()
    try:
        petition_info = petition_tuple[0]
    except:
        petition_info = ""

    return petition_info
    conn.close()


def change_password(email, new_password):
    """Changes the password based on the given email."""
    conn = sqlite3.connect("petitiondb.sqlite3")  # connect to the database

    change_pass_query = "UPDATE User_Table SET password = \"{A}\" WHERE email = \"{B}\"".format(A = new_password, B = email)
    cur = conn.cursor()
    cur.execute(change_pass_query)
    conn.commit()
    conn.close()


id = 0  # set started ID value for users in User_Table
def create_account(email, password, role, department):
    """Creates a user account."""
    conn = sqlite3.connect("petitiondb.sqlite3")  # connect to the database

    max_id_query = "SELECT max(id) FROM User_Table"  # get the most recently created acocunts id
    max_id_obj = conn.execute(max_id_query)
    max_id_tuple = max_id_obj.fetchall()
    try:
        max_id = max_id_tuple[0][0]  # store most recent id
    except:
        max_id = 0

    id = max_id + 1  # create newest id

    # get department for user entered name:
    get_dept_id_query = "SELECT ID FROM Department WHERE name = \"{A}\"".format(A = department)
    get_dept_id_obj = conn.execute(get_dept_id_query)
    dept_id_tuple = get_dept_id_obj.fetchone()
    try:
        dept_id = dept_id_tuple[0]
    except:
        dept_id = ""

    create_user_insert = "INSERT INTO User_Table(id, email, password, role, department) VALUES({A}, \"{B}\", \"{C}\", \"{D}\", {E})".format(A = id, B = email, C = password, D = role, E = dept_id)

    cur = conn.cursor()
    cur.execute(create_user_insert)  # execute the creation
    conn.commit()  # commit changes to the database
    conn.close()  # close database connection


def submit_decision(petitionID, approval_decision, email):
    """Checks if faculty has submitted a vote, submits a vote, determines if petition is approved."""
    conn = sqlite3.connect("petitiondb.sqlite3")  # connect to the database
    cur = conn.cursor()

    # find the faculty member's id:
    id_query = "SELECT id FROM User_Table WHERE email = \"{A}\"".format(A = email)
    id_query_obj = conn.execute(id_query)
    id_tuple = id_query_obj.fetchone()  # store results of query - in a tuple
    try:
        id_result = id_tuple[0]  # if query returns a result, store it in object
    except:
        id_result = ""  # if query returns no results/an error, set value as empty string

    # find the given petition:
    find_petition_query = "SELECT * FROM Approval_Responses WHERE petitionID = {A}".format(A = petitionID)
    find_petition_query_obj = conn.execute(find_petition_query)
    petition_tuple = find_petition_query_obj.fetchall()
    try:
        approval_info = petition_tuple[0]
    except:
        # if the petition does not exist in the approval table, add it:
        create_approval = "INSERT INTO Approval_Responses(petitionID, numOfResponses, numOfApprovals) VALUES({A}, {B}, {C})".format(A = petitionID, B = 0, C = 0)
        cur.execute(create_approval)  # execute the creation
        conn.commit()  # commit changes to the database

    # get the number of responses and number of approvals for petition:
    num_query = "SELECT numOfResponses, numOfApprovals FROM Approval_Responses WHERE petitionID = {A}".format(A = petitionID)
    num_query_obj = conn.execute(num_query)
    num_tuple = num_query_obj.fetchall()
    try:
        numOfResponses = num_tuple[0][0]  # store the number of responses
        numOfApprovals = num_tuple[0][1]  # store the number of approvals
    except:
        numOfResponses = 0
        numOfApprovals = 0

    # get the id's of faculty who have voted in the petition:
    get_petition_voters_query = "SELECT ID FROM Petition_Voters WHERE petitionID = {A}".format(A = petitionID)
    petition_voters_obj = conn.execute(get_petition_voters_query)
    petition_voters_list = petition_voters_obj.fetchall()

    not_voted = False  # declare non_voted

    if find(id_result,petition_voters_list) != -1:
        not_voted = False
        print(find(id_result,petition_voters_list))
        print("You have already voted.")
    else:
        not_voted = True
        print("You have not voted.")

    if not_voted is True:  # check if the faculty member has not voted
        print("Adding your vote.")
        add_vote(approval_decision, petitionID, id_result, numOfResponses, numOfApprovals)  # submit new vote
        # get the updated number of approvals and responses:
        num_query = "SELECT numOfResponses, numOfApprovals FROM Approval_Responses WHERE petitionID = {A}".format(A = petitionID)
        num_query_obj = conn.execute(num_query)
        num_tuple = num_query_obj.fetchall()
        try:
            numOfResponses = num_tuple[0][0]  # store the number of responses
            numOfApprovals = num_tuple[0][1]  # store the number of approvals
        except:
            numOfResponses = 0
            numOfApprovals = 0

        count_votes(numOfApprovals, numOfResponses, petitionID)  # count current votes
    else:
        print("No vote will be added.")

    conn.close()

def count_votes(numOfApprovals, numOfResponses, petitionID):
    """Counts the votes for given petition."""
    conn = sqlite3.connect("petitiondb.sqlite3")  # connect to the database
    cur = conn.cursor()
    # get the student email for the petition:
    get_student_email_query = "SELECT email FROM Student_Petition WHERE petitionID = {A}".format(A = petitionID)
    get_student_email_obj = conn.execute(get_student_email_query)
    student_email_tuple = get_student_email_obj.fetchone()
    try:
        student_email = student_email_tuple[0]
    except:
        student_email = ""

    # get the department for the petition:
    get_petition_department = "SELECT department FROM Student_Petition WHERE petitionID = {A}".format(A = petitionID)
    get_department_obj = conn.execute(get_petition_department)
    department_tuple = get_department_obj.fetchone()
    try:
        petition_department = department_tuple[0]
    except:
        petition_department = ""

    # get the faculty members of the petition department:
    get_faculty_emails_query = "SELECT email FROM User_Table WHERE department = {A}".format(A = petition_department)
    faculty_emails_obj = conn.execute(get_faculty_emails_query)
    faculty_email_list = faculty_emails_obj.fetchall()

    print(len(faculty_email_list))
    if numOfResponses >= len(faculty_email_list):  # check if all faculty for department have responded:
        necessaryApprovals = math.ceil(len(faculty_email_list) / 2)  # calculate majority vote needed for approval
        if numOfApprovals >= necessaryApprovals:  # check if student has the necessary amount of approvals
            # set email messages for a passing result:
            student_message = "After votes by the department faculty, it was determined that your petition has been approved."
            faculty_message = "This email is to let you know that the reviewed petition by", student_email, "passed."
        else:  # student does not have necessary amount of approvals
            # set email messages for a failing result:
            student_message = "After votes by department faculty, it was determined that your petition has been denied."
            faculty_message = "This email is to let you know that the reviewed petition by", student_email, "did not pass."

        student_subject = "Information About Your Petition" # set subject of student email
        faculty_subject = "Information About Student Petition" # set subject of faculty email

        send_email.send_email(student_subject, student_message, student_email)  # send email to the student

        for i in range(len(faculty_email_list)):
            current_email = faculty_email_list[i][0]
            print(current_email)
            send_email.send_email(faculty_subject, faculty_message, current_email)  # send email to faculty member

        delete_petition(petitionID)  # the petition was reviewed; remove it from database.

    conn.close()  # close database connection


def add_vote(approval_decision, petitionID, user_id, numOfResponses, numOfApprovals):
    """Adds faculty vote for a given petition."""
    conn = sqlite3.connect("petitiondb.sqlite3")  # connect to the database
    cur = conn.cursor()  # create cursor

    # adds id of voting faculty into Petition_Voters table for given petition:
    add_voted_id = "INSERT INTO Petition_Voters(petitionID, ID) VALUES({A}, {B})".format(A = petitionID, B = user_id)
    cur.execute(add_voted_id)
    conn.commit()

    # updates number of responses for given petition:
    numOfResponses += 1
    add_review = "UPDATE Approval_Responses SET numOfResponses = {A} WHERE petitionID = {B}".format(A = numOfResponses, B = petitionID)
    cur.execute(add_review)
    conn.commit()

    if approval_decision is True:
        # if the approval decision is true, update number of approvals in database:
        numOfApprovals += 1
        add_approval = "UPDATE Approval_Responses SET numOfApprovals = {A} WHERE petitionID = {B}".format(A = numOfApprovals, B = petitionID)
        cur.execute(add_approval)
        conn.commit()
    else:
        pass  # pass if the faculty does not approve the petition

    conn.close()


def find(value, matrix):
    """Finds a item in a list of tuples."""
    for list in matrix:
        if value in list:
            return [matrix.index(list),list.index(value)]
    return -1


def add_petition(name, student_email, description, department):
    """Adds student petitions to the database."""
    conn = sqlite3.connect("petitiondb.sqlite3")  # connect to the database
    cur = conn.cursor()  # create cursor

    # get department for user entered name:
    get_dept_id_query = "SELECT ID FROM Department WHERE name = \"{A}\"".format(A = department)
    get_dept_id_obj = conn.execute(get_dept_id_query)
    dept_id_tuple = get_dept_id_obj.fetchone()
    try:
        dept_id = dept_id_tuple[0]
    except:
        dept_id = ""

    # find the most recently added (largest) petitionID in the database:
    max_id_query = "SELECT max(petitionID) FROM Student_Petition"  # get the most recently created acocunts id
    max_id_obj = conn.execute(max_id_query)
    max_id_tuple = max_id_obj.fetchall()
    try:
        max_id = max_id_tuple[0][0]  # store most recent id
    except:
        max_id = 0

    petitionID = max_id + 1  # create newest id for use in new petition

    # add new petition to database with user-entered information:
    add_petition = "INSERT INTO Student_Petition(name, email, petition, department, petitionID) VALUES(\"{A}\", \"{B}\", \"{C}\", {D}, {E})".format(A = name, B = student_email, C = description, D = dept_id, E = petitionID)
    cur.execute(add_petition)
    conn.commit()

    conn.close()


def delete_petition(petitionID):
    """Removes student petitions from the database."""
    conn = sqlite3.connect("petitiondb.sqlite3")  # connect to the database
    cur = conn.cursor()  # create cursor

    # deletes the petition for the specified petitionID
    delete_petition = "DELETE FROM Student_Petition WHERE petitionID = {A}".format(A = petitionID)
    cur.execute(delete_petition)
    conn.commit()
