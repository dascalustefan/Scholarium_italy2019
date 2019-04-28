from cli import MultichainCLI
from flask import render_template, request, session
from app import app
from sqlentities import db, University, universities_schema

"""

This module maps the url's of the high authority functionalities: create university and revoke university.

"""


@app.route('/create_university')
def create_university():
    """
    Method that creates a university. It gives a node activate, send and receive permissions, creates the multisignature
    and adds the university to the database.

    Args:
        univ_address (str): the address of the university.
        target_pubkey (str): the public key of the university.
        univ_name (str): the name of the university.
        asset_name (str): the asset name of the university.

    Returns:
         (html): the high authority page
         (dict): response variable that contains all the universities and whether there were errors at creation.
    """
    response = dict()

    univ_address = request.args.get("univ_address")

    errors = MultichainCLI.create_university(univ_address)
    response['create_errors'] = "Could not create university" if errors else ""

    target_pubkey = request.args.get("target_pubkey").replace(" ", "")
    univ_name = request.args.get("univ_name")

    multisig_addr, errors = MultichainCLI.create_multisigaddress(session["pubkey"], target_pubkey)

    print(multisig_addr)

    if errors:
        response["create_errors"] = "Could not create multisignature address. The provided public key is not valid."
    else:
        asset_name = request.args.get("asset_name")
        univ_address = MultichainCLI.get_multisig_second_address(session["address"])
        errors = MultichainCLI.issue_asset_univ(univ_address, asset_name, multisig_addr)

        if errors:
             response["create_errors"] = "Multisig was already created"
        else:
            db.session.add(University(name=univ_name, address=univ_address, pubkey=target_pubkey))
            db.session.commit()
            universities = University.query.all()
            response["universities"] = universities_schema.dump(universities).data

    return render_template("high_authority.html", response=response)


@app.route('/revoke_university')
def revoke_university():
    """
        Method that revokes a university. It revokes a node activate, send and receive permissions and deletes it from
        the database.

        Args:
            univ_address (str): the address of the university.

        Returns:
            (html): the high authority page
            (dict): response variable that contains all the universities and whether there were errors.
    """

    response = dict()

    univ_address = request.args.get("univ_address")

    errors = MultichainCLI.revoke_university(univ_address)
    response['revoke_errors'] = "Could not revoke university" if errors else ""

    # carefull here! SQL injection possibility - must patch.
    db.session.execute("delete from university where address = '{}'".format(univ_address))
    db.session.commit()
    universities = University.query.all()
    response["universities"] = universities_schema.dump(universities).data

    return render_template("high_authority.html", response=response)


