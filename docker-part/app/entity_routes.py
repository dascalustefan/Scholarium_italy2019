from app import app
from cli import MultichainCLI
from flask import render_template, request, session


"""

This module maps the url's of the third party entity functionalities: verification of diploma validation and searching
for diplomas in blockchain.

"""


@app.route('/verify_diploma')
def verify_diploma():
    """
    Method that verifies if a diploma is valid. It lists all the transaction of the given asset and checks whether the
    cnp+diploma hash is found in the university+high authority multisignature address. It also checks if the
    diploma was revoked, the cnp+diploma was transferred to burn address.

    Args:
        diploma_hash (str): the hash of the diploma.
        asset_name (str): the name of the asset of the university.
        stud_cnp (str): the student id.

    Returns:
         (html): the entity page.
         (dict): response variable that contains a message that says whether the diploma is valid.
    """
    response = dict()

    diploma_hash = request.args.get("diploma_hash")
    asset_name = request.args.get("asset_name")
    stud_cnp = request.args.get("stud_cnp")

    asset_transactions = MultichainCLI.list_assets_transactions(asset_name)
    burn_address = MultichainCLI.get_burn_address()

    diploma_hash_exists = False
    diploma_revoked = False
    for transaction in asset_transactions:
        if len(transaction["data"]) > 0:
            if stud_cnp + diploma_hash == transaction["data"][0]:
                if burn_address not in transaction["addresses"]:
                    diploma_hash_exists = True
                else:
                    diploma_revoked = True

    if diploma_hash_exists and not diploma_revoked:
        response["valid"] = "Diploma is valid"
    else:
        response["valid"] = "Diploma is not valid"

    return render_template("entity.html", response=response)


@app.route('/search_diplomas')
def search_diplomas():
    """Method that search for diplomas of a student, given its cnp(student id). Firstly, it lists all the assets found
    in the blockchain, then it lists all the transactions of every asset. If the student cnp is found in any transaction
    and it was not revoked, the diploma is added to the response variable

    Args:
        stud_cnp (str): the id of the student.

    Returns:
         (html): the entity page
         (dict): response variable that contains all the valid diplomas with the corresponding asset name of the
         university that issued it.
    """
    response = dict()
    response["diplomas"] = dict()

    stud_cnp = request.args.get("stud_cnp")

    assets = MultichainCLI.list_assets()
    burn_address = MultichainCLI.get_burn_address()

    for asset in assets:
        asset_transaction = MultichainCLI.list_assets_transactions(asset["name"])

        for transaction in asset_transaction:
            if len(transaction["data"]) > 0:
                if stud_cnp == transaction["data"][0][0:4]:
                    if burn_address not in transaction["addresses"]:
                        response["diplomas"][transaction["data"][0][4:]] = asset["name"]
                    else:
                        response["diplomas"].pop(transaction["data"][0][4:])

    return render_template("entity.html", response=response)
