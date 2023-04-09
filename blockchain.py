"""
The data format thought of 
{
"mail": "ee210002041@iiti.ac.in",
"votes": "c1000c2000c3000......"
}
"""
from hashlib import sha256
import json
import time
class Block:
    def __init__(self,id, transactions, timestamp, previous_hash):
        self.id= id
        self.transactions= transactions
        self.timesptamp= timestamp
        self.previous_hash= previous_hash
        self.nonce= 0
        self.hash= None
    
    def find_hash(self):
        block_json_string= json.dumps(self.__dict__, sort_keys=True)
        return sha256(block_json_string.encode()).hexdigest()

class Blockchain:
    difficulty= 2
    def __init__(self):
        self.chain= []
        self.create_genesis_block()
        self.unconfirmed_transactions= []

    def create_genesis_block(self):
        genesis_block= Block(0,[],time.time(), "0")
        genesis_block.hash= genesis_block.find_hash()
        self.chain.append(genesis_block)
    
    def create_genesis_block_set(self):
        genesis_block= Block(0,set(),time.time(), "0")
        genesis_block.hash= genesis_block.find_hash()
        self.chain.append(genesis_block)
    

    def last_block(self):
        return self.chain[-1]
    
    def proof_of_work(self, block):
        block.nonce= 0
        curr_hash= block.find_hash()
        while not curr_hash.startswith('0'*Blockchain.difficulty):
            block.nonce+=1
            curr_hash= block.find_hash()
        return curr_hash
    
    def is_valid_proof(self, block, block_hash):
        return(block_hash.startswith('0'*Blockchain.difficulty) and block_hash== block.find_hash())
    
    def add_block(self, block, proof):
        previous_hash= self.last_block.hash 
        if previous_hash!= block.previous_hash:
            return False
        if not Blockchain.is_valid_proof(block, proof):
            return False
        
        block.hash= proof
        self.chain.append(block)
        return True
    
    def add_new_transaction(self, transaction):
        self.unconfirmed_transactions.append(transaction)

    def mine(self):
        if not self.unconfirmed_transactions:
            return False
        last_block= self.last_block
        new_block= Block(id= last_block.id+1, transactions= self.unconfirmed_transactions, 
                        timestamp=time.time(), previous_hash= last_block.hash)
        proof= self.proof_of_work(new_block)
        self.add_block(new_block, proof)
        self.unconfirmed_transactions= []
        return new_block.id
    