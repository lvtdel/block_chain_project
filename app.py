from flask import Flask, request, jsonify
from pyee import EventEmitter
from waitress import serve

from block_chain_core.block import Block
from block_chain_core.block_chain import Blockchain
from block_chain_core.miner import Miner
from block_chain_core.transation import Transaction

app = Flask(__name__)

# Khởi tạo blockchain và miner
ee = EventEmitter()
blockchain = Blockchain(difficulty=4, ee=ee)
miner = Miner(blockchain)


@ee.on('add_new_block')
def print_new_block(block: Block):
    for block in blockchain.chain:
        print(f"\nBlock {block.index}")
        print(f"Hash: {block.hash}")
        print(f"Prev: {block.previous_hash}")
        print(f"Transactions: {block.transactions}")
    print(blockchain.is_chain_valid())


@app.route('/transactions/new', methods=['POST'])
def new_transaction():
    data = request.get_json()
    required_fields = ['tx_type', 'payload']

    if not all(field in data for field in required_fields):
        return 'Missing fields', 400

    # tx = Transaction(data['sender'], data['recipient'], data['amount'])
    tx = Transaction(**data)
    miner.add_transaction(tx)
    return jsonify({'message': 'Transaction received'}), 201


# @app.route('/mine', methods=['GET'])
# def mine_block():
#     miner.mine_block()
#     return jsonify({'message': 'Block mined', 'length': len(blockchain.chain)})

@app.route('/chain', methods=['GET'])
def get_chain():
    chain_data = [block.to_dict() for block in blockchain.chain]
    return jsonify(chain_data), 200


@app.route('/pending', methods=['GET'])
def get_pending():
    tx_data = [tx.__dict__ for tx in miner.mempool]
    return jsonify(tx_data), 200


@app.route('/', methods=['GET'])
def hello():
    return 'Hello, World!'


if __name__ == '__main__':
    # app.run(port=5000)
    serve(app, host='0.0.0.0', port=5000,
          threads=8,
          channel_timeout=120,
          asyncore_use_poll=True,
          clear_untrusted_proxy_headers=True,
          max_request_body_size=1073741824,  # 1GB
          ident='Blockchain App'
          )
