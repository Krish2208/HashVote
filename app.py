from flask import Flask, request
import time
import blockchain
import json
app= Flask(__name__)
Blockchain= blockchain.Blockchain()
Blockchain_voter= blockchain.Blockchain()
Blockchain.create_genesis_block()
Blockchain_voter.create_genesis_block_set()
@app.route('/')
def home():
    return "Hello, Flask!"

@app.route('/login', methods=['POST'])
def chk_double():
    prev= Blockchain_voter.last_block.transactions
    trans_data= request.get_json()
    if trans_data["mail"] in prev:
        return "Chtya samjha hai kya?", 404
    prev.add(trans_data["mail"])
    trans_data["timestamp"]= time.time()
    trans_data["mail"]= prev
    Blockchain_voter.add_new_transaction(trans_data)
    return "Sahi hai", 201



@app.route('/new_transaction', methods=['POST'])
def new_transaction():
    trans_data= request.get_json()
    required_fields= ["mail","votes"]
    for field in required_fields:
        if not trans_data.get(field):
            return "Chtya hai kya", 404
    trans_data["timestamp"]= time.time()
    Blockchain.add_new_transaction(trans_data)
    return "Sahi hai", 201

@app.route('/chain', methods=['GET'])
def get_chain():
    chain_data= []
    for block in Blockchain.chain:
        chain_data.append(block.__dict__)
    return json.dumps({"length": len(chain_data), "chain": chain_data})

@app.route('/mine', methods=['GET'])
def mine_unconfirmed_transaction():
    result= Blockchain.mine()
    if not result:
        return "Khali hai"
    return "Block #{} is mined".format(result)

@app.route('/pending_trans')
def get_pending_trans():
    return json.dumps(Blockchain.unconfirmed_transactions)

if __name__ == "__main__":
    app.run()