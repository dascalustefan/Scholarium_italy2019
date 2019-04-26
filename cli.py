import settings
import subprocess
import time
import json

"""

Module that manages the interaction with the multichain trough commands line (get address, connect etc.). It contains a 
class (MultichainCLI) that contains only class methods (an optimization to not create an instance of the object every 
time you want to call a method)

"""


class MultichainCLI(object):
    mc_cli = "multichain-cli " + settings.scholarium_name
    mcd = "multichaind " + settings.scholarium_name

    @classmethod
    def _multichaincli(cls, params):
        """
        Private method that launches a command on the multichain using a process using the multichain-cli. It opens the
        STDOUT and STDERR pipeline in order to collect the outputs and the errors. It also prints the error(if any).

        Args:
            params (str): a string that contains the parameters.

        Returns:
            (json): the output of the command.
            (str): the errors.

        """

        proc = subprocess.Popen(cls.mc_cli + params,
                                stdout=subprocess.PIPE,
                                stderr=subprocess.PIPE,
                                shell=True)

        out, err = proc.communicate()
        out = out.decode("ascii")
        err = err.decode("ascii")
        print(err)

        try:
            out = json.loads(out)
        except json.decoder.JSONDecodeError:
            pass

        return out, err

    @classmethod
    def disconeect(cls):
        cls._multichaincli(" stop")

    @classmethod
    def connect(cls, scholarium_address):
        """
        Method that launches a command to connect to a multichain. If the connect address is "", it means that this is
        the first node and it launches the multichain wiht the command "multichaind <name> -daemon". Else, it simply
        connects to the given address.

        Args:
            scholarium_address (str): the address to connect to (ip+port)
        """

        if cls._multichaincli(" getaddresses") != ('', "error: couldn't connect to server\n") \
           and scholarium_address == "":
            return

        if scholarium_address != "":
            subprocess.Popen([cls.mcd + "@" + scholarium_address + " -daemon"], shell=True)

        else:
            subprocess.Popen([cls.mcd + " -daemon"], shell=True)

        time.sleep(6)


    @classmethod
    def get_address(cls):
        out, _ = cls._multichaincli(" getaddresses")
        return out[0]

    @classmethod
    def get_node_address(cls):
        out, _ = cls._multichaincli(" getinfo")
        return out['nodeaddress'].split("@")[1]

    @classmethod
    def get_node_public_key(cls):
        out, _ = cls._multichaincli(" getaddresses true")
        return out[0]["pubkey"]

    @classmethod
    def get_node_rank(cls, address):
        """
        Method that launches a listpermission command and verifies the permission of a node.

        Args:
            address (str): the address of the node.

        Returns:
            (str): "high authority", "university", "student" or "entity", depending on the node permissions.
        """
        out, _ = cls._multichaincli(" listpermissions")

        rank = "entity"
        for permission in out:
            if permission["address"] == address and permission["type"] == "admin":
                rank = "high_authority"
                break
            if permission["address"] == address and permission["type"] == "activate" and rank != "admin":
                rank = "university"
            if permission["address"] == address and permission["type"] == "send" and rank != "university":
                rank = "student"

        return rank

    @classmethod
    def create_university(cls, univ_address):
        _, err = cls._multichaincli(" grant " + univ_address + " send,receive,activate")
        return "error" in err

    @classmethod
    def revoke_university(cls, univ_address):
        _, err = cls._multichaincli(" revoke " + univ_address + " send,receive,activate")
        return "error" in err

    @classmethod
    def create_multisigaddress(cls, pubkey1, pubkey2):
        """
        Method that creates a multisignature between two nodes. It also imports the address.

        Args:
            pubkey1 (str): the public key of the first node.
            pubkey2 (str): the public key of the second node.

        Returns:
            (json): the multisignature address between the two nodes.
            (bool): if there are any errors.
        """

        out, err = cls._multichaincli(" addmultisigaddress 2 '[\"" + pubkey1 + "\", \"" + pubkey2 + "\"]'")

        if "error" in err:
            return out, True
        else:
            multisig = out[0:-1]
            cls._multichaincli(" importaddress " + multisig + " '' false")
            return multisig, False

    @classmethod
    def create_stud(cls, stud_address):
        _, err = cls._multichaincli(" grant " + stud_address + " send,receive")
        return "error" in err

    @classmethod
    def revoke_stud(cls, stud_address):
        _, err = cls._multichaincli(" revoke " + stud_address + " send,receive")
        return "error"

    @classmethod
    def issue_asset_univ(cls, univ_address, asset_name, multisig_addr):
        """
        Method that transfer 100000 units of an asset to an address. It's used by the high authority to issue an asset
        to a university. It also adds the multisignature of the high authority+univ to the metadata of the asset.

        Args:
            univ_address (str): the address of the university.
            asset_name (str): the name of the asset.
            multisig_addr (str): the multisignature of the high authority+univ.

        Returns:
            (bool): if there are any errors.
        """

        _, err = cls._multichaincli(" issue  " + univ_address + " " + asset_name + " 100000 1 0 '{\"address\":\"" +
                                 multisig_addr + "\"}'")
        return "Asset or stream with this name already exists" in err

    @classmethod
    def get_multisig_second_address(cls, address):
        """
        Method that returns the other node address in a multisignature.

        Args:
            address (str): the address of the current node.

        Returns:
            (str): the address of the other node.
        """
        out, _ = cls._multichaincli(" getaddresses true")

        for response_address in out[-1]["addresses"]:
            if response_address != address:
                return response_address

    @classmethod
    def get_asset_name(cls):
        out, _ = cls._multichaincli(" gettotalbalances")
        return out[0]["name"]

    @classmethod
    def send_asset(cls, multisig_addr, asset_name):
        _, err = cls._multichaincli(" sendasset " + multisig_addr + " " + asset_name + " 1")
        return "error" in err

    @classmethod
    def grand_send_recieve(cls, address):
        _, err = cls._multichaincli(" grant " + address + " send,receive")
        return "error" in err

    @classmethod
    def get_destination_addr_asset(cls, asset_name):
        """
        Returns the metadata of an asset (the destination address used by the smart filter).

        Args:
            asset_name (str): the name of the asset.

        Returns:
            (str): the destination address.
        """

        out, _ = cls._multichaincli(" getassetinfo " + asset_name + " true")
        return out["details"]["address"]

    @classmethod
    def create_raw_trans(cls, source_address, dest_address, asset_name, data):
        """
        Creates a raw multisignature transaction with data in it.

        Args:
            source_address (str): the source address.
            dest_address (str): the destination address.
            asset_name (str): the name of the asset to transfer units from.
            data (str): the data that will be added in the transfer.

        Returns:
            (str): the encoded hex blob of the transfer.
        """

        out, err = cls._multichaincli(" createrawsendfrom " + source_address
                                    + " '{\"" + dest_address + " \":{\"" + asset_name + "\":1}}' '[\"" +
                                    data + "\"]' sign")

        return out, "error" in err

    @classmethod
    def sign_and_send_transaction(cls, transaction_blob):
        out, _ = cls._multichaincli(" signrawtransaction " + transaction_blob)
        out, err = cls._multichaincli(" sendrawtransaction " + out["hex"])
        return out, "error" in err

    @classmethod
    def get_burn_address(cls):
        out, _ = cls._multichaincli(" getinfo")
        return out["burnaddress"]

    @classmethod
    def decode_transaction(cls, txid):
        out, _ = cls._multichaincli(" getrawtransaction " + txid)
        out, err = cls._multichaincli(" decoderawtransaction " + out)

        return out

    @classmethod
    def list_assets_transactions(cls, asset_name):
        cls._multichaincli(" subscribe " + asset_name)
        out, _ = cls._multichaincli(" listassettransactions " + asset_name)
        return out

    @classmethod
    def list_assets(cls):
        out, _ = cls._multichaincli(" listassets")
        return out

