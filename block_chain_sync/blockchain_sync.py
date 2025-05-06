import threading
import time
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
from block_chain_grpc.mapper import tx_to_grpc, block_to_grpc

T = TypeVar('T')  # Định nghĩa generic type


class BlockChainSyncAbstract(ABC):
    def __init__(self, my_add: str):
        self.my_add = my_add
        self.nodes: set[str] = {my_add}

    def register_node(self, node: str):
        pass

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
    def __init__(self, blockchain: Blockchain, miner: Miner, my_add: str, ee=EventEmitter()):
        super().__init__(my_add)

        self.blockchain = blockchain
        self.miner = miner
        self.ee = ee

        self.register_listener()
        self.start_repeat_sync()

    def start_repeat_sync(self):
        def run_async_in_thread():
            while True:
                # print("Repeat mine")
                self.sync()
                time.sleep(5)

        threading.Thread(target=run_async_in_thread, daemon=False).start()

    def register_listener(self):
        self.ee.on('sync:add_new_transaction', self.broadcast_transaction)
        self.ee.on('sync:add_new_block', self.broadcast_block)

    def register_node(self, node_address_register: str):
        try:
            with grpc.insecure_channel(node_address_register) as channel:
                stub = blockchain_pb2_grpc.BlockchainServiceStub(channel)
                node_add_proto = blockchain_pb2.NodeAddress()
                node_add_proto.ip = self.my_add

                response = stub.AddNode(node_add_proto)
                node_add_list = [node.ip for node in response.ips]

                self.nodes.update(node_add_list)
        except grpc.RpcError as e:
            print(f"Không thể đăng ký node {node_address_register}: {e}")
        except Exception as e:
            print(f"Lỗi khi đăng ký node {node_address_register}: {e}")

    def add_node(self, node: str):
        self.nodes.add(node)
        print(f"Node set: {self.nodes}")

    def remove_node(self, node: str):
        self.nodes.remove(node)

    def sync(self):
        node_longest = self.get_node_longest_chain()
        if not node_longest: return

        if node_longest['length'] > len(self.blockchain.chain):
            print(f"Node longest chain is longer than local chain. Syncing with node {node_longest['node']}")
            self.sync_with_node(node_longest)
        # else:
        #     print("Local chain is longer than node longest chain. Do nothing.")

        # chain_longest = self.get_chain_from_node(node_longest)

    def sync_with_node(self, node_infor):
        try:
            chain_longest = self.get_chain_from_node(node_infor)
            self.miner.must_stop_mine = True
            self.blockchain.chain = chain_longest.chain

            with grpc.insecure_channel(node_infor['node']) as channel:
                stub = blockchain_pb2_grpc.BlockchainServiceStub(channel)
                mempool_grpc = stub.GetMempool(blockchain_pb2.Empty())
                mempool = [Transaction.from_proto(tx_grpc) for tx_grpc in mempool_grpc.transactions]

                self.miner.mempool = mempool
                self.miner.must_stop_mine = False

            self.miner.must_stop_sync = False
        except grpc.RpcError as e:
            print(f"Đồng bộ thất bại: {e}")
        except Exception as e:
            print(f"Lỗi khi đồng bộ: {e}")

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
        add_to_send = self.get_different_node()
        for node in add_to_send:
            thread = threading.Thread(target=send_transaction_to_node, args=(node,))
            thread.start()
            thread_list.append(thread)

    def broadcast_block(self, block: Block):
        def send_block_to_node(node: str):
            try:
                with grpc.insecure_channel(node) as chanel:
                    stub = blockchain_pb2_grpc.BlockchainServiceStub(chanel)
                    block_proto = block_to_grpc(block)
                    stub.AddBlock(block_proto)
            except grpc.RpcError as e:
                print(f"Không thể gửi block tới node {node}: {e}")
            except Exception as e:
                print(f"Lỗi khi gửi block tới node {node}: {e}")

        thread_list: list[threading.Thread] = []
        add_to_send = self.get_different_node()
        for node in add_to_send:
            thread = threading.Thread(target=send_block_to_node, args=(node,))
            thread.start()
            thread_list.append(thread)

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

        node_diff = self.get_different_node()
        for node in node_diff:
            thr = threading.Thread(target=add_infor_node, args=(node,))
            thr.start()
            thread_list.append(thr)

        for thread in thread_list:
            thread.join()

        if not infor_nodes:
            print("Chưa có node nào khác trong mạng")
            return None

        chain_longest = max(infor_nodes, key=lambda x: x["length"])

        # print(f"longest chain: {chain_longest}")
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

    def get_different_node(self):
        return self.nodes.difference({self.my_add})
