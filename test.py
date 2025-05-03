import json

import grpc
from pyee import EventEmitter

from block_chain_core.block import Block
from block_chain_core.block_chain import Blockchain
from block_chain_core.miner import Miner
from block_chain_core.transation import Transaction
from block_chain_grpc import blockchain_pb2
from block_chain_grpc import blockchain_pb2_grpc
from block_chain_sync.blockchain_sync import BlockChainSync


def get_chain_from_node(host="localhost", port=50051):
    # Kết nối với node qua gRPC
    with grpc.insecure_channel(f"{host}:{port}") as channel:
        stub = blockchain_pb2_grpc.BlockchainServiceStub(channel)
        ## Get dif,
        difficulty = 3

        block_chain = Blockchain(difficulty=difficulty, ee=EventEmitter())
        block_chain.chain.clear()

        try:
            response = stub.StreamChain(blockchain_pb2.Empty())
            for block_grpc in response:
                block = Block.from_proto(block_grpc)
                print(block)
                block_chain.add_block(block, validate=False)

            print(block_chain.is_chain_valid())

        except grpc.RpcError as e:
            # Xử lý lỗi gRPC (nếu có xảy ra)
            print(f"An RPC error occurred: {e}")
            return None

    return block_chain


def test_get_chain():
    block_chain_sync = BlockChainSync(blockchain=None, miner=None, ee=EventEmitter())
    node_longest = block_chain_sync.get_node_longest_chain()
    chain_longest = block_chain_sync.get_chain_from_node(node_longest)
    print(f"chain longest: {chain_longest.get_last_block().__dict__}")


# get_chain_from_node()
if __name__ == '__main__':
    # block_chain = get_chain_from_node()
    # print(f"Blockchain: {block_chain.chain}")

    # test_get_chain()

    # tx_sample = Transaction("payment", '{"amount": 100, "currency": "USD"}',
    #                         "0xd206080A25862e79C74B804273936A0e843DAa03",
    #                         "0x5adead24b25fb8a36139abda4445df64e091cf34238a6395404b6e75ee9863f4460dcd19c680768f29c2b181f41bee2217a0766eebc63fa3f7be395ed60e83bb00",
    #                         nonce=1,
    #                         receiver="0xf0faC6cc7eB427268C405A462bF304a2ac84A425")
    # tx_sample2 = Transaction("payment", '{"amount": 100, "currency": "USD"}',
    #                         "0xd206080A25862e79C74B804273936A0e843DAa03",
    #                         "0x42868f4a930ce991eb99ef1d1bcc97658b5539607db607d64196cb0a5bd438ba4aad85ba0c5169c59431bbf66e0d714220241f243246ba53d09e8833a1e8f33200",
    #                         nonce=2,
    #                         receiver="0xf0faC6cc7eB427268C405A462bF304a2ac84A425")
    #
    # print(tx_sample2.verify())
    # block_chain_sync = BlockChainSync(blockchain=None, miner=None, ee=EventEmitter())
    # block_chain_sync.broadcast_transaction(tx_sample2)

    test_get_chain()