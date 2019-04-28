from cli import MultichainCLI
from flask import render_template, request, session
from app import app

"""

This module maps the url's of the student functionalities: create multisignature with the university.

"""

@app.route("/create_studuniv_multisig")
def create_studuniv_multisig():
    """
    Method that creates the multisignature with the university.

    Args:
       target_pubkey (str): the public key of the university.

    Returns:
         (html): student page.
         (dict): response variable that contains whether there was an error of creation of the multisignature.
    """
    response = dict()

    target_pubkey = request.args.get("target_pubkey").replace(" ", "")

    _, errors = MultichainCLI.create_multisigaddress(session["pubkey"], target_pubkey)
    response["multisig_errors"] = "Could not create multisignature address. The provided public key is not valid." \
                                  if errors else ""

    return render_template("student.html", response=response)
