from flask import Flask, render_template, request
import requests
import json
from web3 import Web3

ESP32_IP = "http://192.168.1.150"  # Replace with your ESP32 IP

PRIVATE_KEY = "8a44846c051dd62acfed47f03c429f24e1ffa93dc062eb16553035ecccf37d1e"
WALLET_ADDRESS = "0x95d8CaEB09DecE9504F449aB63607D0985B69665"
CONTRACT_ADDRESS = "0x795F9CC8f4555C36e2272c916BFF042a392ac5E7"
RPC_URL = "https://rpc.testnet.monad.xyz"

ABI = [
    {
        "inputs": [
            {"internalType": "address", "name": "to", "type": "address"},
            {"internalType": "string", "name": "uri", "type": "string"}
        ],
        "name": "mintCertificateNFT",
        "outputs": [],
        "stateMutability": "nonpayable",
        "type": "function"
    }
]

app = Flask(__name__)
web3 = Web3(Web3.HTTPProvider(RPC_URL))
contract = web3.eth.contract(address=Web3.to_checksum_address(CONTRACT_ADDRESS), abi=ABI)

def mint_nft(runtime, device_id):
    uri = f"data:application/json,{{\\\"name\\\":\\\"Certificate\\\",\\\"description\\\":\\\"{device_id} runtime: {runtime}s\\\"}}"
    nonce = web3.eth.get_transaction_count(WALLET_ADDRESS)
    txn = contract.functions.mintCertificateNFT(WALLET_ADDRESS, uri).build_transaction({
        'from': WALLET_ADDRESS,
        'nonce': nonce,
        'gas': 200000,
        'gasPrice': web3.to_wei('10', 'gwei')
    })
    signed_txn = web3.eth.account.sign_transaction(txn, PRIVATE_KEY)
    tx_hash = web3.eth.send_raw_transaction(signed_txn.rawTransaction)
    return web3.to_hex(tx_hash)

@app.route("/")
def index():
    return render_template("index.html", status=None)

@app.route("/relay/<relay>/<action>")
def control_relay(relay, action):
    if relay in ["relay1", "relay2"] and action in ["on", "off"]:
        url = f"{ESP32_IP}/{relay}/{action}"
        try:
            r = requests.get(url)
            status = r.text
            if "Runtime" in status and action == "off":
                runtime = int(status.split(": ")[-1].replace("s", "").strip())
                if runtime <= 120:
                    tx = mint_nft(runtime, relay)
                    return render_template("index.html", status=f"{status} | NFT Minted: {tx}")
                else:
                    return render_template("index.html", status=f"{status} | Not compliant, no NFT")
            return render_template("index.html", status=status)
        except Exception as e:
            return render_template("index.html", status=f"ESP32 not reachable: {str(e)}")
    return "Invalid request"

if __name__ == "__main__":
    app.run(debug=True)
