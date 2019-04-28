from cli import MultichainCLI
from flask import render_template, request, session
from app import app
import time
from sqlentities import db, Student, students_schema, Diploma, diplomas_schema

"""

This module maps the url's of the third party entity functionalities: create a student, revoke a student, create a 
diploma transfer, create multisignature with student, create multisignature with high authority and create diploma 
revokation transfer.

"""


@app.route('/create_student')
def create_student():
    """
    Method that creates a student. It gives send and receive permissions to a node, creates a multisignature with the
    node and adds the node to the database.

    Args:
        student address (str): the address of the student.
        target_pubkey (str): the public key of the student.
        stud_name (str): the name of the student.
        stud_cnp (str): the id of the student.

    Returns:
         (html): university page
         (dict): response variable that contains all students and diplomas.
    """
    response = dict()

    stud_address = request.args.get("stud_address")
    errors = MultichainCLI.create_stud(stud_address)
    response['create_errors'] = "Could not create student" if errors else ""

    target_pubkey = request.args.get("target_pubkey").replace(" ", "")
    stud_name = request.args.get("stud_name")
    stud_cnp = request.args.get("stud_cnp")

    if len(stud_cnp) != 4:
        response["create_errors"] = "CNP is invalid. It must contain 4 digits"
    else:
        multisig_addr, errors = MultichainCLI.create_multisigaddress(target_pubkey, session["pubkey"])

        if errors:
            response["create_errors"] = "Could not create multisignature address. The provided public key is not valid."
        else:

            MultichainCLI.create_stud(multisig_addr)

            db.session.add(Student(cnp=stud_cnp, name=stud_name, address=stud_address,
                                   pubkey=target_pubkey, multisig=multisig_addr))
            db.session.commit()

    students = Student.query.all()
    response["students"] = students_schema.dump(students).data
    diplomas = Diploma.query.all()
    response["diplomas"] = diplomas_schema.dump(diplomas).data

    return render_template("university.html", response=response)


@app.route('/revoke_student')
def revoke_student():
    """
    Method that revokes a student. It revokes send and receive permissions from a node and deletes the node to the
    database.

    Args:
        student address (str): the address of the student.

    Returns:
         (html): university page.
         (dict): response variable that contains all students and diplomas.
    """
    response = dict()

    stud_address = request.args.get("stud_address")

    errors = MultichainCLI.revoke_stud(stud_address)
    response['revoke_errors'] = "Could not revoke student" if errors else ""

    # !SQL injection possibility - must patch.
    db.session.execute("delete from student where address = '{}'".format(stud_address))
    db.session.commit()

    students = Student.query.all()
    response["students"] = students_schema.dump(students).data
    diplomas = Diploma.query.all()
    response["diplomas"] = diplomas_schema.dump(diplomas).data

    return render_template("university.html", response=response)


@app.route("/create_diploma_transaction")
def create_diploma_transaction():
    """
    Method that gives a diploma to a student. It gets the asset name of the university currency and sends a unit
    of that asset to the multisignature student+university. Then it creates a multisignature transfer from the
    multisignature student+university to university+high authority and signs it. It also adds the cnp(student id)+hash
    as metadata and adds the diploma to the database.

    Args:
        multisig_address (str): the multisignature of student+university.
        stud_cnp (str): the id of the student.
        diploma_hash (str): the hash of the diploma.
        diploma_name (str): the name of the diploma.

    Returns:
        (html): the university page.
        (dict): response variable that contains the students, diplomas and the hexblob of the
        transaction that the student must sign.
    """
    response = dict()

    multisig_address = request.args.get("multisig_address")
    stud_cnp = request.args.get("stud_cnp")
    diploma_hash = request.args.get("diploma_hash")
    diploma_name = request.args.get("diploma_name")

    asset_name = MultichainCLI.get_asset_name()

    error = MultichainCLI.send_asset(multisig_address, asset_name)

    print("Student cnp: {}".format(stud_cnp))

    if not error:
        time.sleep(0.5)

        asset_dest_addr = MultichainCLI.get_destination_addr_asset(asset_name)

        hexblob, errors = MultichainCLI.create_raw_trans(multisig_address, asset_dest_addr, asset_name, stud_cnp + diploma_hash)

        if errors:
            response["create_hexblob"] = "Multisignature with the high authority was not created. Please create the " \
                                         "multisignature before issuing any diploma."
        else:
            response["create_hexblob"] = "Hexblob: {}".format(hexblob["hex"])

            diploma = Diploma(hash=diploma_hash, name=diploma_name, student_cnp=stud_cnp)
            db.session.add(diploma)
            db.session.commit()

    students = Student.query.all()
    response["students"] = students_schema.dump(students).data
    diplomas = Diploma.query.all()
    response["diplomas"] = diplomas_schema.dump(diplomas).data

    return render_template("university.html", response=response)


@app.route("/create_univha_multisig")
def create_univha_multisig():
    response = dict()

    target_pubkey = request.args.get("target_pubkey").replace(" ", "")

    multisig_addr, errors = MultichainCLI.create_multisigaddress(target_pubkey, session["pubkey"])

    if errors:
        response["multisig_errors"] = "Could not create multisignature address. The provided public key is not valid."
    else:
        MultichainCLI.grand_send_recieve(multisig_addr)

    students = Student.query.all()
    response["students"] = students_schema.dump(students).data
    diplomas = Diploma.query.all()
    response["diplomas"] = diplomas_schema.dump(diplomas).data

    return render_template("university.html", response=response)


@app.route('/revoke_diploma_transaction')
def revoke_diploma_transaction():
    """
        Method that revokes a diploma from a student. It creates a multisignature transfer from the multisignature
        between univ+high authority to the burn address.

        Args:
            stud_cnp (str): the id of the student.
            diploma_hash (str): the hash of the diploma.

        Returns:
            (html): the university page.
            (dict): response variable that contains the students, diplomas and the hexblob of the
            transaction that the high authority must sign.
        """

    response = dict()

    stud_cnp = request.args.get("stud_cnp")

    diploma_hash = request.args.get("diploma_hash")

    asset_name = MultichainCLI.get_asset_name()
    asset_dest_addr = MultichainCLI.get_destination_addr_asset(asset_name)

    burn_address = MultichainCLI.get_burn_address()

    hexblob, _ = MultichainCLI.create_raw_trans(asset_dest_addr, burn_address, asset_name, stud_cnp + diploma_hash)

    response["revoke_hexblob"] = "Hexblob: {}".format(hexblob["hex"])

    db.session.execute("delete from diploma where hash = '{}'".format(diploma_hash))
    db.session.commit()

    students = Student.query.all()
    response["students"] = students_schema.dump(students).data
    diplomas = Diploma.query.all()
    response["diplomas"] = diplomas_schema.dump(diplomas).data

    return render_template("university.html", response=response)

