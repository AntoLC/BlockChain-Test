from flask import Flask, jsonify, request
from Module1.blockchain import Blockchain
from Module1.flaskrun import flaskrun
from uuid import uuid4


app = Flask(__name__)
blockchain = Blockchain()

@app.route('/')
def index():
    return "Hello World"

@app.route('/mine_block', methods=['GET'])
def mine_block():
    previous_block = blockchain.get_previous_block()
    proof = blockchain.proof_of_work(previous_block['proof'])
    previous_hash = blockchain.hash(previous_block)
    block = blockchain.create_block(proof, previous_hash)

    response = {
        'message': "Congrat, you mined your first block!",
        'index': block['index'],
        'timestamp': block['timestamp'],
        'proof': block['proof'],
        'previous_hash': block['previous_hash'],
    }
    return jsonify(response), 200

@app.route('/get_chain', methods=['GET'])
def get_chain():
    response = {
        'chain': blockchain.chain,
        'length': len(blockchain.chain)
    }
    return jsonify(response), 200

@app.route('/is_chain_valid', methods=['GET'])
def is_chain_valid():
    is_valid = blockchain.is_chain_valid(blockchain.chain)
    response = {
        'is_valid': is_valid,
        'message': "Blockchain Valid!" if is_valid else "Blockchain is not valid!"
    }

    return jsonify(response), 200 if is_valid else 498

# if __name__ == '__main__':
#     app.run(debug=True, host='0.0.0.0')
if __name__ == '__main__':
    flaskrun(app)
