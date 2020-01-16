import hashlib
import json
from time import time
from uuid import uuid4

from flask import Flask, jsonify, request


class Blockchain(object):
    def __init__(self):
        self.chain = []
        self.current_transactions = []

        # create the genesis block
        self.new_block(previous_hash=1, proof=100)

    def new_block(self, proof, previous_hash=None):
        """
        Create a new Block in the Blockchain

        A block should have:
        * Index
        * Timestamp
        * List of current transactions
        * The proof used to mine this block
        * The hash of the previous block

        :param proof: <int> The proof given by the Proof of Work algorithm
        :param previous_hash: (Optional) <str> Hash of previous Block
        :return: <dict> New Block
        """

        block = {
            'index': len(self.chain) + 1,
            'timestamp': time(),
            'tranactions': self.current_transactions,
            'proof': proof,
            'previous_hash': previous_hash
        }

        # reset the current list of transactions
        self.current_transactions = []
        # append the chain to the block
        self.chain.append(block)
        # return the new block
        return block

    def hash(self, block):
        """
        Creates a SHA-256 hash of a Block

        :param block": <dict> Block
        "return": <str>
        """

        # Use json.dumps to convert json into a string
        # Use hashlib.sha256 to create a hash
        # It requires a `bytes-like` object, which is what
        # .encode() does.
        # It convertes the string to bytes.
        # We must make sure that the Dictionary is Ordered,
        # or we'll have inconsistent hashes

        # prior to python 3.7, you were not guaranteed to get a consistent order of keys when you refernce a python dictionary
        # this sorts the keys alphabetically and then created a string version of it
        # => json.dumps(block, sort_keys=True)
        # encode turns it into a 'bytes-like' object

        string_object = json.dumps(block, sort_keys=True).encode()

        raw_hash = hashlib.sha256(string_object)

        hex_hash = raw_hash.hexdigest()

        # By itself, the sha256 function returns the hash in a raw string
        # that will likely include escaped characters.
        # This can be hard to read, but .hexdigest() converts the
        # hash to a string of hexadecimal characters, which is
        # easier to work with and understand

        return hex_hash

    @property
    def last_block(self):
        return self.chain[-1]

    @staticmethod
    def valid_proof(block_string, proof):
        """
        Validates the Proof:  Does hash(block_string, proof) contain 3
        leading zeroes?  Return true if the proof is valid
        :param block_string: <string> The stringified block to use to
        check in combination with `proof`
        :param proof: <int?> The value that when combined with the
        stringified previous block results in a hash that has the
        correct number of leading zeroes.
        :return: True if the resulting hash is a valid proof, False otherwise
        """
        
        guess = block_string + str(proof)
        guess = guess.encode()
        guess_hash = hashlib.sha256(guess).hexdigest()
        # return True or False
        # return guess_hash[:6] == "000000"
        if guess_hash[:3] == "000":
            print("********** true")
            print(guess_hash)
        return guess_hash[:3] == "000"



# instantiate our Node
app = Flask(__name__)

# generate a globally unique address for this node
node_identifier = str(uuid4()).replace('-', '')

# instantiate the Blockchain
blockchain = Blockchain()


@app.route('/mine', methods=['POST'])
def mine():
    
    data = request.get_json()

    if data['id'] and data['proof']:
        # checking last_hash in real time
        last_hash = blockchain.last_block['previous_hash']
        block_string = blockchain.hash(blockchain.last_block)
        print("!!!!!!!!!!", data['proof'])
        print("******", blockchain.valid_proof(block_string, data['proof']))
        # run the proof against the proof of work algorithm
        if blockchain.valid_proof(block_string, data['proof']):
            # forge the new Block by adding it to the chain with the proof
            block = blockchain.new_block(data['proof'], last_hash)
            response = {
                'message': 'New Block Forged'
            }
            status_code = 201
        else:
            response = {
                'message': 'Incorrect proof. Try again!'
            }
            status_code = 200
    else:
        response = {
            'message': 'Bad request'
        }
        status_code = 400

    return jsonify(response), status_code


@app.route('/chain', methods=['GET'])
def full_chain():
    response = {
        'length': len(blockchain.chain),
        'chain': blockchain.chain
    }
    return jsonify(response), 200


@app.route('/last_block', methods=['GET'])
def last_block():
    response = {
        'last_block': blockchain.last_block
    }
    return jsonify(response), 200


# Run the program on port 5000
if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)
