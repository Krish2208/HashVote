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
        try:
            block_json_string= json.dumps(self.__dict__, sort_keys=True)
            return sha256(block_json_string.encode()).hexdigest()
        except(TypeError):
            if(list(self.transactions)):
                x=(list(self.transactions))
                block_json_string= json.dumps([list(x), self.nonce])
                return sha256(block_json_string.encode()).hexdigest()
            block_json_string= json.dumps([list(self.transactions), self.nonce])
            return sha256(block_json_string.encode()).hexdigest()

class Blockchain:
    difficulty= 2
    def __init__(self):
        self.chain= []
        self.unconfirmed_transactions= []

    def create_genesis_block(self):
        genesis_block= Block(0,[],time.time(), "0")
        genesis_block.hash= genesis_block.find_hash()
        self.chain.append(genesis_block)
    
    def create_genesis_block_set(self):
        genesis_block= Block(0,{'start@iiti'},time.time(), "0")
        genesis_block.hash= genesis_block.find_hash()
        self.chain.append(genesis_block)
    

    @property
    def last_block(self):
        return self.chain[-1]
    
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
    def proof_of_work(self, block):
        block.nonce= 0
        curr_hash= block.find_hash()
        while not curr_hash.startswith('0'*Blockchain.difficulty):
            block.nonce+=1
            curr_hash= block.find_hash()
        return curr_hash
    
    def add_new_transaction(self, transaction):
        self.unconfirmed_transactions.append(transaction)
    
    @classmethod
    def is_valid_proof(self, block, block_hash):
        return(block_hash.startswith('0'*Blockchain.difficulty) 
        and block_hash== block.find_hash())

    @classmethod
    def check_chain(self, chain):
        result= True
        previous_hash= chain[0].hash
        for block in chain[1:]:
            print(block.transactions)
            block_hash= block.hash
            print(block_hash)
            delattr(block, "hash")
            block_hash_now= block.find_hash()
            print(block_hash_now)
            if(block_hash_now!=block_hash):
                print("HAA YAHIN SE AAYA")
                return False
            if (not self.is_valid_proof(block, block_hash)) or (previous_hash!= block.previous_hash):
                print('ho gaya')
                return False
            block.hash, previous_hash= block_hash, block_hash
        return result
    
    def mine(self):
        if not self.unconfirmed_transactions:
            return False
        last_block= self.last_block
        for i in range(0, len(self.unconfirmed_transactions)):
            # print(self.unconfirmed_transactions[i])
            new_block= Block(id= last_block.id+1, transactions= self.unconfirmed_transactions[i], 
                            timestamp=time.time(), previous_hash= last_block.hash)
            proof= self.proof_of_work(self, new_block)
            self.add_block(new_block, proof)
        self.unconfirmed_transactions= []
        return True
    
chain= Blockchain()
chain.create_genesis_block_set()
# chain.add_new_transaction(2123)
# result= chain.mine()
# chain.create_genesis_block_set()
# print(chain.last_block().transactions)
new_data= set(chain.last_block.transactions)
new_data.add(32)
# print(new_data)
# k= json.dumps(list(new_data))
# print(sha256(k.encode()).hexdigest())
# new_data.add(2344)
# print(new_data)
# new_data.add(2344)
# print(new_data)
# print(type(new_data))
chain.add_new_transaction(new_data)
# chain.add_new_transaction(234)
# # print(chain.unconfirmed_transactions)
result= chain.mine()
# # print(chain.unconfirmed_transactions)
# # print(chain.last_block().transactions)
new_data= set(chain.last_block.transactions)
new_data.add(32)
chain.add_new_transaction(new_data)
result= chain.mine()
# print((chain.chain[0].hash))
# # print(chain.last_block().transactions)
# # print(result)
# new_data= chain.last_block.transactions[0]
# new_data.add(3142)
# # chain.add_new_transaction(new_data)
# # result= chain.mine()
# # chain.add_new_transaction(new_data)
# # result= chain.mine()
# # print(result)
# # # print(chain.last_block().transactions)
# # print(chain.chain[2].hash)
# print(chain.chain[4].transactions)
chain.chain[1].transactions= {121342}
# # print(chain.chain)
print(chain.check_chain(chain.chain))