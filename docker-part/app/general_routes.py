from cli import MultichainCLI
from flask import render_template, request, session
import time
from app import app
from sqlentities import University, universities_schema, Student, students_schema, Diploma, diplomas_schema

"""

This module maps the url's of general/common functionalities: return index page, connect and disconnect. It also maps 
the sign and send a multisignature transaction that is common to student and high authority.

"""


@app.route("/")
def index():
    """
    Method that maps the main page (index).
    
    Returns:
         (html): the index page.
    """""

    return render_template("index.html", response=dict())


@app.route("/disconnect")
def disconnect():
    """
     Method that disconnects a user from the application. It stops the blockchain.

    Returns:
         (html): the index page.
    """

    MultichainCLI.disconeect()
    time.sleep(1)

    return render_template("index.html", response=dict())


@app.route("/connect")
def connect():
    """
    Method that connects a user to the application. It stores the address, ip+port, public key and rank(student,
    university, high authority) in the session variable.

    Args:
        scholarium_address (str): the address(ip+port) of the node.

    Returns:
        (html): the page of student, university or high authority, depending on the rank of the node.
        (dict): response variable that contains students and diplomas for university, and universities for high
        authorities.
    """
    response = dict()

    scholarium_address = request.args.get("scholarium_address")

    MultichainCLI.connect(scholarium_address)

    session["address"] = MultichainCLI.get_address()

    session['node_address'] = MultichainCLI.get_node_address()

    session["pubkey"] = MultichainCLI.get_node_public_key()

    session["rank"] = MultichainCLI.get_node_rank(session["address"])

    if session["rank"] == "university":
        students = Student.query.all()
        response["students"] = students_schema.dump(students).data
        diplomas = Diploma.query.all()
        response["diplomas"] = diplomas_schema.dump(diplomas).data

        return render_template("university.html", response=response)
    if session["rank"] == "high_authority":
        universities = University.query.all()
        response["universities"] = universities_schema.dump(universities).data

        return render_template("high_authority.html", response=response)
    if session["rank"] == "student":
        return render_template("student.html", response=response)
    if session["rank"] == "entity":
        return render_template("entity.html", response=response)


@app.route("/sign_transaction")
def sign_transaction():
    """
    Method that sign a multisignature transaction blob and send the transaction to the destination.

    Args:
        transaction_blob (str): the transaction encoded in a hex blob.

    Returns:
         (html): student/high authority page, depending on node ranks.
         (dict): response variable that contains all the universities if the rank of the node is high authority.
    """
    response = dict()
    transaction_blob = request.args.get("transaction_blob")

    _, errors = MultichainCLI.sign_and_send_transaction(transaction_blob)

    if session["rank"] == "student":
        if errors:
            response["sign_errors"] = "Could not sign the diploma transaction. You must create the multisignature with" \
                                      " the university first."

        return render_template("student.html", response=response)
    if session["rank"] == "high_authority":
        universities = University.query.all()
        response["universities"] = universities_schema.dump(universities).data

        return render_template("high_authority.html", response=response)

