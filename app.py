import asyncio
import threading
import time
from multiprocessing import Process

from flask import Flask, request, jsonify
from pyee import EventEmitter
from waitress import serve

from block_chain_core.block import Block
from block_chain_core.block_chain import Blockchain
from block_chain_core.miner import Miner
from block_chain_core.transation import Transaction

import os

from block_chain_grpc.blockchain_service import serve_grpc
from container import Container


def crate_app():
    container = Container()

    ee = container.ee
    blockchain = container.block_chain
    miner = container.miner

    app = Flask(__name__)

    @ee.on('add_new_block')
    def print_new_block(block: Block):
        def print_inf():
            time.sleep(5)
            print(f"New block added: {block.hash}, \nTransactions: {block.transactions}")
            print(f"Chain valid: {blockchain.is_chain_valid()}")
            # raise Exception("stop")

        threading.Thread(target=print_inf, daemon=False).start()

        # raise Exception("stop")

    @app.route('/transactions/new', methods=['POST'])
    def new_transaction():
        data = request.get_json()
        required_fields = ['tx_type', 'payload', 'signature', 'sender', 'nonce']
        data.pop('timestamp')
        data.pop('hash')

        if not all(field in data for field in required_fields):
            return jsonify({'message': 'Missing field'}), 400

        # tx = Transaction(data['sender'], data['recipient'], data['amount'])

        tx = Transaction(**data)

        try:
            miner.add_transaction(tx)
        except Exception as e:
            return jsonify({'message': str(e)}), 400

        return jsonify({'message': 'Transaction received', 'tx': tx.__dict__}), 201

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

    return app


def run_grpc_server(port: int):
    try:
        serve_grpc(port)
    except Exception as e:
        print(f"gRPC server error: {e}")


def run_http_server(app: Flask, port: int):
    try:
        serve(app, host='0.0.0.0', port=port,
              threads=8,
              channel_timeout=120,
              asyncore_use_poll=True,
              clear_untrusted_proxy_headers=True,
              max_request_body_size=1073741824,
              ident='Blockchain App')
    except Exception as e:
        print(f"HTTP server error: {e}")


if __name__ == '__main__':
    HTTP_PORT = int(os.getenv('HTTP_PORT', 5000))
    GRPC_PORT = int(os.getenv('GRPC_PORT', 50051))

    print(f"Starting servers...")
    print(f"HTTP server will run on port {HTTP_PORT}")
    print(f"gRPC server will run on port {GRPC_PORT}")
    app = crate_app()
    container = Container()

    grpc_thread = threading.Thread(
        target=run_grpc_server,
        args=(GRPC_PORT,),
        daemon=True
    )
    grpc_thread.start()

    run_http_server(app, HTTP_PORT)
