from django.db import models
import json
import hashlib
from time import time
from datetime import datetime

# Create your models here.
class Blockchain(object):
    def __init__(self):
        self.chain = [] #initialize an empty list of Blocks
        self.pending_transactions = []
        self.difficulty = 4
        self.miner_rewards = 50
        self.block_size = 10
    
    def add_transaction(self, sender, receiver, amount, key_string, sender_key):
        key_byte = key_string.encode('ASCII')
        sender_key_byte = sender_key.encode('ASCII')

        key = RSA.import_key(key_byte)
        sender_key = RSA.import_key(sender_key_byte)
        if not sender or not receiver or not amount:
            print('Transaction error')
            return False
        
        transaction = Transaction(sender, receiver, amount)

        transaction.sign_transaction(key, sender_key)

        if not transaction.is_valid_transaction():
            print('Transaction error')
            return False
        
        self.pending_transactions.append(transaction)
        return len(self.chain) + 1


    def get_last_block(self):
        return self.chain[-1]

    def add_block(self, block):
        if len(self.chain) > 0:
            block.prev = self.get_last_block().hash
        else:
            block.prev = "none"
        self.chain.append(block)


class Block(object):
    def __init__(self, transactions, time, index):
        self.index = index # block number
        self.transactions = transactions # transactions data
        self.time = time # the time at which block is created
        self.prev = "" # hash of the previous block
        self.nonce = 0
        self.hash = self.calculate_hash() # hash of block
        

    def calculate_hash(self):
        hash_transactions = ""
        for transaction in self.transactions:
            hash_transactions += transaction.hash

        hash_string = str(self.time) + hash_transactions + self.prev + str(self.index) + str(self.nonce)
        hash_encoded = json.dumps(hash_string, sort_keys=True).encode()
        return hashlib.sha256(hash_encoded).hexdigest()

    def mine_block(self, difficulty=4):
        head = '0' * difficulty
        
        # compute until the beginning of the hash is head
        while self.hash[0:difficulty] != head:
            self.nonce += 1
            self.hash = self.calculate_hash()

        print("Block mined")
        return True


    def __str__(self):
        result = '----------\n\n'
        result += f"Block: {self.index}\n" + f"Hash: {self.hash}\n"
        result += f"Transactions:\n"
        for transaction in self.transactions:
            result += '    ' + str(transaction) + '\n'
        result += f"Time created: {self.time}\n" + f"Previous hash: {self.prev}\n" + f"Nonce: {self.nonce}\n"
        return result

class Transaction(object):
    def __init__(self, sender, receiver, amount):
        self.sender = sender
        self.receiver = receiver
        self.amount = amount
        self.time = datetime.now().strftime("%m/%d/%Y, %H:%M:%S")
        self.hash = self.calculate_hash()

    def calculate_hash(self):
        hash_string = self.sender + self.receiver + str(self.amount) + str(self.time)
        hash_encode = json.dumps(hash_string, sort_keys=True).encode()
        return hashlib.sha256(hash_encode).hexdigest()

    def __str__(self):
        return str(self.sender + ' ---> ' + self.receiver + ': ' + str(self.amount) + ' MAL at ' + str(self.time))

    
