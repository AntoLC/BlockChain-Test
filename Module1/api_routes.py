#!flask/bin/python
from flask import Flask, jsonify, request
from blockchain import Blockchain
from uuid import uuid4

application = Flask(__name__)
blockchain = Blockchain()
node_address = str(uuid4()).replace("-", "")

def APIApp():
    return application

@application.route('/')
def route_index():
    return "Hello World"

@application.route('/mine_block', methods=['GET'])
def mine_block():
    previous_block = blockchain.get_previous_block()
    proof = blockchain.proof_of_work(previous_block['proof'])
    previous_hash = blockchain.hash(previous_block)
    blockchain.add_transaction(sender=node_address, receiver="Toba Louis", amount=100)
    block = blockchain.create_block(proof, previous_hash)

    response = {
        'message': "Congrat, you mined your first block!",
        'index': block['index'],
        'timestamp': block['timestamp'],
        'proof': block['proof'],
        'previous_hash': block['previous_hash'],
        'transactions': block['transactions'],
    }
    return jsonify(response), 200

@application.route('/get_chain', methods=['GET'])
def get_chain():
    response = {
        'chain': blockchain.chain,
        'length': len(blockchain.chain)
    }
    return jsonify(response), 200

@application.route('/is_chain_valid', methods=['GET'])
def is_chain_valid():
    is_valid = blockchain.is_chain_valid(blockchain.chain)
    response = {
        'is_valid': is_valid,
        'message': "Blockchain Valid!" if is_valid else "Blockchain is not valid!"
    }

    return jsonify(response), 200 if is_valid else 498

@application.route('/add_transaction', methods=['POST'])
def add_transaction():
    json = request.get_json()
    transaction_keys = ['sender', 'receiver', 'amount']
    if not all (key in json for key in transaction_keys):
        return "Some elements are missing in the transaction...", 400

    index = blockchain.add_transaction(sender=json['sender'], receiver=json['receiver'], amount=json['amount'])
    response = { 'message': f'This transaction will be added to block {index}'}
    return jsonify(response), 201
