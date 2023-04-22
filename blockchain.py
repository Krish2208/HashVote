"""
The data format thought of 
{
"mail": "ee210002041@iiti.ac.in",
"votes": "c1000,c2000,c3000......,"
}
"""
from hashlib import sha256
import json
import time

class Block:
    #Initialise block
    def __init__(self,id, transactions, timestamp, previous_hash):
        self.id= id
        self.transactions= transactions #data of the block
        self.timesptamp= timestamp
        self.previous_hash= previous_hash
        self.nonce= 0 #facilitates POW
        self.hash= None
    
    #Function to find hash of the block
    def find_hash(self):
        try:
            block_json_string= json.dumps(self.__dict__, sort_keys=True)
            return sha256(block_json_string.encode()).hexdigest()
        except(TypeError): #For handling the set
            if(list(self.transactions)):
                x=(list(self.transactions))
                block_json_string= json.dumps([list(x), self.nonce])
                return sha256(block_json_string.encode()).hexdigest()
            block_json_string= json.dumps([list(self.transactions), self.nonce])
            return sha256(block_json_string.encode()).hexdigest()

class Blockchain:

    difficulty= 2 #Difficulty for POW. As it increases, POW takes more time
    
    #Initialise chain
    def __init__(self):
        self.chain= []
        self.unconfirmed_transactions= []

    #Create the first block of the chain with "0" as previous hash and block id 0
    def create_genesis_block(self):
        genesis_block= Block(0,[],time.time(), "0")
        genesis_block.hash= genesis_block.find_hash()
        self.chain.append(genesis_block)
    
    #If we want the data type for transaction to be set, use this function too create the genesis block
    def create_genesis_block_set(self):
        genesis_block= Block(0,{'start@iiti'},time.time(), "0")
        genesis_block.hash= genesis_block.find_hash()
        self.chain.append(genesis_block)
    

    @property
    #Access the last block of the chain
    def last_block(self):
        return self.chain[-1]
    
    #Add block to the chain after verfying it has valid hash and no fiddling
    def add_block(self, block, proof):
        previous_hash= self.last_block.hash 
        if previous_hash!= block.previous_hash:
            return False
        if not Blockchain.is_valid_proof(block, proof):
            return False
        block.hash= proof
        self.chain.append(block)
        return True
    
    @staticmethod
    #Method to secure the chain further and reduce concurrency problems
    def proof_of_work(self, block):
        block.nonce= 0 #Used to get the required hash. It is changed to satisfy the condition of hash
        curr_hash= block.find_hash()
        while not curr_hash.startswith('0'*Blockchain.difficulty):
            block.nonce+=1
            curr_hash= block.find_hash()
        return curr_hash
    
    #A new transaction is added here before mining it further
    def add_new_transaction(self, transaction):
        self.unconfirmed_transactions.append(transaction)
    
    @classmethod
    #Check if hash has satisfied the proof of work or not
    def is_valid_proof(self, block, block_hash):
        return(block_hash.startswith('0'*Blockchain.difficulty) 
        and block_hash== block.find_hash())

    #Check the validity of the data in the chain to catch any malpractices
    def check_chain(self):
        result= True
        previous_hash = self.chain[0].hash
        for block in self.chain[1:]:
            block_hash= block.hash
            delattr(block, "hash")
            block_hash_now= block.find_hash()
            print(block_hash_now)
            if(block_hash_now!=block_hash):
                return False
            if (not self.is_valid_proof(block, block_hash)) or (previous_hash!= block.previous_hash):
                return False
            block.hash, previous_hash= block_hash, block_hash
        return result
    
    #Add new block to the chain
    def mine(self):
        if not self.unconfirmed_transactions:
            return False
        last_block= self.last_block
        for i in range(0, len(self.unconfirmed_transactions)):
            new_block= Block(id= last_block.id+1, transactions= self.unconfirmed_transactions[i], 
                            timestamp=time.time(), previous_hash= last_block.hash)
            proof= self.proof_of_work(self, new_block)
            self.add_block(new_block, proof)
        self.unconfirmed_transactions= []
        return True
    
    #Function to check the results of the election. Unrelated for basic functioning of blockchain
    def chk_result(self, result):
        for block in self.chain[1:]:
            x= block.transactions
            votes= x["votes"].split(",")[:-1]
            for i in range(0, len(votes)):
                result[votes[i]]= result[votes[i]]+1
        return result
    

    """
#Code for decentralisation and peer to peer. Use in main.py to implement
peers= set()
@app.route('/register_node', methods=['POST'])
def register_new_peers():
    node_address = request.get_json()["node_address"]
    if not node_address:
        return "Invalid data", 400
    # Add the node to the peer list
    peers.add(node_address)
    # Return the blockchain to the newly registered node so that it can sync
    return get_chain()

  
@app.route('/register_with', methods=['POST'])
def register_with_existing_node():
    
    node_address = request.get_json()["node_address"]
    if not node_address:
        return "Invalid data", 400

    data = {"node_address": request.host_url}
    headers = {'Content-Type': "application/json"}

    # Make a request to register with remote node and obtain information
    response = requests.post(node_address + "/register_node",
                             data=json.dumps(data), headers=headers)

    if response.status_code == 200:
        global blockchain
        global peers
        # update chain and the peers
        chain_dump = response.json()['chain']
        blockchain = create_chain_from_dump(chain_dump)
        peers.update(response.json()['peers'])
        return "Registration successful", 200
    else:
        # if something goes wrong, pass it on to the API response
        return response.content, response.status_code
 

def create_chain_from_dump(chain_dump):
    blockchain = Blockchain()
    for idx, block_data in enumerate(chain_dump):
        block = Block(block_data["index"],
                      block_data["transactions"],
                      block_data["timestamp"],
                      block_data["previous_hash"])
        proof = block_data['hash']
        if idx > 0:
            added = blockchain.add_block(block, proof)
            if not added:
                raise Exception("The chain dump is tampered!!")
        else:  # the block is a genesis block, no verification needed
            blockchain.chain.append(block)
    return blockchain

    def consensus(peers):
        global blockchain
        longest_chain = None
        current_len = len(blockchain.chain)

        for node in peers:
            response = requests.get('{}/chain'.format(node))
            length = response.json()['length']
            chain = response.json()['chain']
            if length > current_len and blockchain.check_chain_validity(chain):
                # Longer valid chain found!
                current_len = length
                longest_chain = chain

        if longest_chain:
            blockchain = longest_chain
            return True

        return False

    def announce_new_block(block):
    for peer in peers:
        url = "{}add_block".format(peer)
        requests.post(url, data=json.dumps(block.__dict__, sort_keys=True)) 
"""