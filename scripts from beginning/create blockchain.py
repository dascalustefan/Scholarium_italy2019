import subprocess
import time
import argparse
import json


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("chain_name")

    args = parser.parse_args()
    chain_name = args.chain_name

    subprocess.Popen(["multichain-util create {} -anyone-can-connect=true".format(chain_name)], shell=True)
    proc = subprocess.Popen(["multichaind {} -daemon".format(chain_name)], stdout=subprocess.PIPE, shell=True)
    time.sleep(3)

    proc = subprocess.Popen(["multichain-cli {} getinfo".format(chain_name)], stdout=subprocess.PIPE, shell=True)
    out = proc.communicate()
    burnaddress = json.loads(out[0].decode("ascii"))["burnaddress"]

    subprocess.Popen(["multichain-cli {} grant {} receive".format(chain_name, burnaddress)], shell=True)

    proc = subprocess.Popen(["multichain-cli " + chain_name + " create txfilter destfilter {} 'function filtertransaction() "
                      "{ "
                         "var tx=getfiltertransaction(); "
                         "var asset_name=\"\"; "
                         "var dest_addr=\"\"; "
                         "var src_addr=\"\"; "
                                                              
                         "if (tx.vout[0].hasOwnProperty(\"assets\")) "
                         "{"
                            "if (tx.vout[0].assets[0].type==\"transfer\")"
                            "{"
                                "asset_name = tx.vout[0].assets[0].name; "
                                "var dest_addr=tx.vout[0].scriptPubKey.addresses[0]; "
                                "src_addr=tx.vout[tx.vout.length-1].scriptPubKey.addresses[0];"
                                                              
                                "if (verifypermission(src_addr, \"activate\")) "
                                 "{"
                                    "if (verifypermission(dest_addr, \"activate\"))"
                                    "{"
                                        "return \"University can transfer money only to students\";"
                                    "}"
                                 "}"
                                 "else if(asset_name != \"\")"
                                 "{"
                                    "var asset=getassetinfo(asset_name,true); "
                                    "var dest_addr_asset=asset.details.address; "
                                                                      
                                    "if(dest_addr!=\"" + burnaddress + "\") "
                                    "{"
                                        "if(dest_addr!=dest_addr_asset) "
                                        "{"
                                            "return \"Wrong destination address, must be the multisignature address "
                                            "between High Authority and University\";"
                                        "}"
                                    "}"
                                    "else "
                                    "{ "
                                        "if (src_addr != dest_addr_asset) "
                                        "{"
                                            "return \"Source address must be asset address in order to revoke diploma.\""
                                        "}"
                                    "}"
                                 "} "
                            "}"
                         "}"
                     "}'"],
                     stderr=subprocess.PIPE, shell=True)
    print(proc.communicate())

    proc = subprocess.Popen(["multichain-cli {} getaddresses".format(chain_name)], stdout=subprocess.PIPE, shell=True)
    out = proc.communicate()
    address = json.loads(out[0].decode("ascii"))[0]

    proc = subprocess.Popen(["multichain-cli {} approvefrom {} destfilter true".format(chain_name, address)],
                     stderr=subprocess.PIPE, shell=True)
    print(proc.communicate())