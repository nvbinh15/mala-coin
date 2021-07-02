from django.db import models

import json
import hashlib
from time import time
from datetime import datetime
from Crypto.PublicKey import RSA
from Crypto.Signature import *
from urllib.parse import urlparse
import requests
import jsonpickle

# Create your models here.
class Blockchain(object):
    def __init__(self):
        self.chain = [] #initialize an empty list of Blocks
        self.pending_transactions = []
        self.difficulty = 4
        self.miner_rewards = 50
        self.block_size = 10
        self.nodes = set()
    
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

    def generate_keys(self):
        key = RSA.generate(2048)

        private_key = key.export_key()
        file_out = open('private.pem', 'wb')
        file_out.write(private_key)
        file_out.close()

        public_key = key.publickey().export_key()
        file_out = open('receiver.pem', 'wb')
        file_out.write(public_key)

        file_out.close()

        return key.publickey().export_key().decode('ASCII')

    def get_last_block(self):
        return self.chain[-1]

    def add_block(self, block):
        if len(self.chain) > 0:
            block.prev = self.get_last_block().hash
        else:
            block.prev = "none"
        self.chain.append(block)

    def register_node(self, address):
        parsed_url = urlparse(address)
        self.node.add(parsed_url.netloc)
    
    def resolve_conflicts(self):
        neighbors = self.nodes
        new_chain = None

        max_length = len(self.chain)

        for node in neighbors:
            response = requests.get(f"http://{node}/chain")

            if response.status_code == 200:
                length = response.json()['length']
                chain = response.json()['chain']

                if length > max_length and self.is_valid_chain():
                    max_length = length
                    new_chain = chain

        if new_chain:
            self.chain = self.chain_json_decode(new_chain)
            print(self.chain)
            return True
        
        return False
            
    def mine_pending_transactions(self, miner):
        len_pending_trans = len(self.pending_transactions)
        
        if (len_pending_trans <= 1):
            print("Not enough transactions to mine!")
            return False

        else:
            for i in range(0, len_pending_trans, self.block_size):
                end = i + self.block_size
                if i >= len_pending_trans:
                    end = len_pending_trans
                
                transaction_slice = self.pending_transactions[i: end]
                
                new_block = Block(transaction_slice, datetime.now().strftime("%m/%d/%Y, %H:%M:%S"), len(self.chain))

                hash_val = self.get_last_block().hash
                new_block.prev = hash_val
                new_block.mine_block(self.difficulty)
                self.chain.append(new_block)
            print("Mining Transactions Successfully!")
            
            pay_miner = Transaction("Miner Rewards", miner, self.miner_rewards)
            self.pending_transactions = [pay_miner]    
        return True
    
    def is_valid_chain(self):
        for i in range(1, len(self.chain)):
            prev_block = self.chain[i - 1]
            curr_block = self.chain[i]

            if not curr_block.has_valid_transactions():
                print("Error")
                return False
            
            if curr_block.hash != curr_block.calculate_hash():
                print("Error")
                return False
            
            if curr_block.prev != prev_block.hash:
                print("Error")
            
        return True
    
    def chain_json_encode(self):
        block_list_json = []

        for block in self.chain:
            block_json = {}
            block_json['hash'] = block.hash
            block_json['index'] = block.index
            block_json['prev'] = block.prev
            block_json['time'] = block.time
            block_json['nonce'] = block.nonce

            transactions_list_json = []
            transactions_json = {}
            for transaction in block.transactions:
                transactions_json['time'] = transaction.time
                transactions_json['sender'] = transaction.sender
                transactions_json['receiver'] = transaction.receiver
                transactions_json['amount'] = transaction.amount
                transactions_json['hash'] = transaction.hash
                transactions_list_json.append(transactions_json)

            block_json['transactions'] = transactions_list_json

            block_list_json.append(block_json)

        return block_list_json

    def chain_json_decode(self, chain_json):
        chain = []
        
        for block_json in chain_json:

            trans_list = []

            for trans_json in block_json['transactions']:
                transaction = Transaction(
                    trans_json['sender'],
                    trans_json['receiver'],
                    trans_json['amount']
                )

                transaction.time = trans_json['time']
                transaction.hash = trans_json['hash']
                trans_list.append(transaction)
            
            block = Block(trans_list, block_json['time'], block_json['index'])
            block.hash = block_json['hash']
            block.prev= block_json['prev']
            block.nonce = block_json['nonce']

            chain.append(block)
        
        return chain

    def get_balance(self, person):
        balance = 0

        for i in range(1, len(self.chain)):

            block = self.chain[i]

            try:
                for transaction in block.transactions:
                    if (transaction.sender == person):
                        balance -= transaction.amount
                    elif (transaction.receiver == person):
                        balance += transaction.amount

            except AttributeError:
                print("No transaction")
        
        # Why +100??
        return balance + 100



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

    def has_valid_transactions(self):
        for transaction in self.transactions:
            if not transaction.is_valid_transaction():
                return False
        
        return True
    
    def json_endcode(self):
        return jsonpickle.endcode(self)



    def __str__(self):
        result = '--------------------\n\n'
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

    def sign_transaction(self, key, sender_key):
        if (self.hash != self.calculate_hash()):
            print('Transaction error')
            return False
        
        if str(key.publickey().export_key()) != str(sender_key.publickey().export_key()):
            print('Transaction attempt to be signed from another wallet')
            return False

        pkcs1_15.new(key)

        self.signature = 'made'
        print('Made signature!')
        return True
    
    def is_valid_transaction(self):
        if self.hash != self.calculate_hash():
            return False
        if self.sender == self.receiver:
            return False
        if self.sender == "Miner Rewards":
            return False
        if (not self.signature) or (len(self.signature) == 0):
            return False
        return True


    def __str__(self):
        return str(self.sender + ' ---> ' + self.receiver + ': ' + str(self.amount) + ' MAL at ' + str(self.time))

    
