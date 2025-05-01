import time

from flask import Flask, request, jsonify
from pyee import EventEmitter
from waitress import serve

from block_chain_core.block import Block
from block_chain_core.block_chain import Blockchain
from block_chain_core.miner import Miner
from block_chain_core.transation import Transaction

import os

DIFFICULTY = int(os.getenv('DIFFICULTY'))
PORT = int(os.getenv('PORT'))
MAX_TRANSACTIONS = int(os.getenv('MAX_TRANSACTIONS_PER_BLOCK'))

app = Flask(__name__)

ee = EventEmitter()
blockchain = Blockchain(difficulty=DIFFICULTY, ee=ee)
miner = Miner(blockchain, MAX_TRANSACTIONS)


@ee.on('add_new_block')
def print_new_block(block: Block):
    # for block in blockchain.chain:
    #     print(f"\nBlock {block.index}")
    #     print(f"Hash: {block.hash}")
    #     print(f"Prev: {block.previous_hash}")
    #     print(f"Transactions: {block.transactions}")
    print(f"New block added: {block.hash}, \nTransactions: {block.transactions}")
    print(f"Chain valid: {blockchain.is_chain_valid()}")


@app.route('/transactions/new', methods=['POST'])
def new_transaction():
    data = request.get_json()
    required_fields = ['tx_type', 'payload', 'signature', 'sender', 'nonce']

    if not all(field in data for field in required_fields):
        return jsonify({'message': 'Missing field'}), 400

    # tx = Transaction(data['sender'], data['recipient'], data['amount'])

    tx = Transaction(**data)

    try:
        miner.add_transaction(tx)
    except Exception as e:
        return jsonify({'message': str(e)}), 400

    return jsonify({'message': 'Transaction received', 'tx': tx.__dict__}), 201


# @app.route('/mine', methods=['GET'])
# def mine_block():
#     miner.mine_block()
#     return jsonify({'message': 'Block mined', 'length': len(blockchain.chain)})

@app.route('/chain', methods=['GET'])
def get_chain():
    chain_data = [block.to_dict() for block in blockchain.chain]
    chain_data.reverse()
    return jsonify(chain_data), 200


@app.route('/pending', methods=['GET'])
def get_pending():
    tx_data = [tx.__dict__ for tx in miner.mempool]
    return jsonify(tx_data), 200


@app.route('/transactions/<tx_hash>', methods=['GET'])
def get_transaction_by_hash(tx_hash: str):
    tx = blockchain.find_transaction(tx_hash)
    if tx:
        return jsonify(tx), 200
    else:
        return jsonify({'message': 'Transaction not found'}), 404

@app.route('/block/<block_hash>', methods=['GET'])
def get_block_by_hash(block_hash: str):
    block = blockchain.find_block(block_hash)

    if block:
        return jsonify(block.to_dict()), 200
    else:
        return jsonify({'message': 'Block not found'}), 404

@app.route('/', methods=['GET'])
def hello():
    return 'Hello, World!'


if __name__ == '__main__':
    print("Starting server...")
    # app.run(port=5000)
    # serve(app, host='0.0.0.0', port=PORT,
    #       threads=8,
    #       channel_timeout=120,
    #       asyncore_use_poll=True,
    #       clear_untrusted_proxy_headers=True,
    #       max_request_body_size=1073741824,  # 1GB
    #       ident='Blockchain App'
    #       )
