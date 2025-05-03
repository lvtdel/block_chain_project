import threading
from abc import ABC

import grpc
from pyee import EventEmitter

from block_chain_core.block import Block
from block_chain_core.block_chain import Blockchain
from block_chain_core.miner import Miner

import grpc
from concurrent import futures
from typing import Any, Callable, TypeVar

from block_chain_core.transation import Transaction
from block_chain_grpc import blockchain_pb2_grpc, blockchain_pb2
from block_chain_grpc.mapper import tx_to_grpc

T = TypeVar('T')  # Định nghĩa generic type


class BlockChainSyncAbstract(ABC):
    def add_node(self, node: str):
        pass

    def remove_node(self, node: str):
        pass

    def broadcast_block(self, block: Block):
        pass

    def broadcast_transaction(self, transaction: Transaction):
        pass

    def get_node_longest_chain(self):
        pass

    def sync_with_node(self, node: str):
        pass


class BlockChainSync(BlockChainSyncAbstract):
    def __init__(self, blockchain: Blockchain, miner: Miner, ee=EventEmitter()):
        self.blockchain = blockchain
        self.miner = miner
        self.ee = ee

        self.nodes: list[str] = ["localhost:5001", "localhost:6001", "localhost:5002", "localhost:5003",
                                 "localhost:5004", ]

        self.ee.on('add_new_block', self.broadcast_block)
        self.ee.on('add_new_transaction', self.broadcast_transaction)

    def register_listener(self):
        self.ee.on('add_new_transaction', self.broadcast_transaction)

    def add_node(self, node: str):
        self.nodes.append(node)

    def remove_node(self, node: str):
        self.nodes.remove(node)

    def sync(self):
        for node in self.nodes:
            self.sync_with_node(node)

    def broadcast_transaction(self, transaction: Transaction):
        def send_transaction_to_node(node: str):
            try:
                with grpc.insecure_channel(node) as channel:
                    stub = blockchain_pb2_grpc.BlockchainServiceStub(channel)
                    transaction_proto = tx_to_grpc(transaction)
                    stub.AddTransaction(transaction_proto)
            except grpc.RpcError as e:
                print(f"Không thể gửi transaction tới node {node}: {e}")
            except Exception as e:
                print(f"Lỗi khi gửi transaction tới node {node}: {e}")

        thread_list: list[threading.Thread] = []
        for node in self.nodes:
            thread = threading.Thread(target=send_transaction_to_node, args=(node,))
            thread.start()
            thread_list.append(thread)

        # Đợi tất cả các thread hoàn thành
        # for thread in thread_list:
        #     thread.join()

    def sync_with_node(self, node: str):
        pass

    def get_node_longest_chain(self):
        infor_nodes = []

        def infor_grpc_to_dict(infor_grpc, node):
            return {"node": node, "difficulty": infor_grpc.difficulty, "length": infor_grpc.length,
                    "last_block_hash": infor_grpc.last_block_hash, }

        def add_infor_node(node):
            response = self.get_chain_info(node)
            if response:
                infor_nodes.append(infor_grpc_to_dict(response, node))
            else:
                print(f"Failed to get chain info from node {node}")

        thread_list: list[threading.Thread] = []
        for node in self.nodes:
            thr = threading.Thread(target=add_infor_node, args=(node,))
            thr.start()
            thread_list.append(thr)

        for thread in thread_list:
            thread.join()

        chain_longest = max(infor_nodes, key=lambda x: x["length"])

        print(f"longest chain: {chain_longest}")
        return chain_longest

    def get_chain_info(self, node: str):
        try:
            with grpc.insecure_channel(node) as channel:
                stub = blockchain_pb2_grpc.BlockchainServiceStub(channel)
                block_chain_infor = stub.GetChainInfor(blockchain_pb2.Empty())
                return block_chain_infor
        except grpc.RpcError as e:
            print(f"An RPC error occurred: {e}")
            return None
        except Exception as e:
            print(f"An error occurred: {e}")
            return None

    def get_chain_from_node(self, node_infor: dict[str, Any]):
        with grpc.insecure_channel(node_infor['node']) as channel:
            stub = blockchain_pb2_grpc.BlockchainServiceStub(channel)
            ## Get dif,
            difficulty = node_infor['difficulty']

            block_chain = Blockchain(difficulty=difficulty, ee=EventEmitter())
            block_chain.chain.clear()

            try:
                response = stub.StreamChain(blockchain_pb2.Empty())
                for block_grpc in response:
                    block = Block.from_proto(block_grpc)
                    # print(block)
                    block_chain.add_block(block, validate=False)

                print(block_chain.is_chain_valid())

            except grpc.RpcError as e:
                # Xử lý lỗi gRPC (nếu có xảy ra)
                print(f"An RPC error occurred: {e}")
                return None

        return block_chain