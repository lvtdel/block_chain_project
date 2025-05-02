import grpc
from concurrent import futures
import time

from block_chain_core.block import Block
from block_chain_core.block_chain import Blockchain
from block_chain_core.transation import Transaction
from block_chain_grpc import blockchain_pb2_grpc, blockchain_pb2
from block_chain_grpc.mapper import block_to_grpc, tx_to_grpc


class BlockchainServicer(blockchain_pb2_grpc.BlockchainServiceServicer):
    def __init__(self, blockchain: Blockchain):
        self.blockchain = blockchain

    def StreamChain(self, request, context):
        for block in self.blockchain.chain:
            block_grpc = block_to_grpc(block)

            for tx in block.transactions:
                tx_grpc = tx_to_grpc(tx)
                block_grpc.transactions.append(tx_grpc)

            yield block_grpc

    def GetChainInfor(self, request, context):
        return blockchain_pb2.ChainInfor(
            difficulty=self.blockchain.difficulty,
            length=len(self.blockchain.chain),
            last_block_hash=self.blockchain.get_last_block().hash,
            last_merkle_root=self.blockchain.get_last_block().merkle_root,
        )


def serve_grpc(blockchain: Blockchain, port: int = 50051):
    server = grpc.server(futures.ThreadPoolExecutor(max_workers=10))
    blockchain_pb2_grpc.add_BlockchainServiceServicer_to_server(BlockchainServicer(blockchain), server)
    server.add_insecure_port(f'[::]:{port}')
    server.start()
    print(f"Blockchain node gRPC server started at port {port}.")
    server.wait_for_termination()

# if __name__ == "__main__":
#     serve()
