import grpc
from concurrent import futures
import time

from block_chain_core.block import Block
from block_chain_core.block_chain import Blockchain
from block_chain_core.miner import Miner
from block_chain_core.transation import Transaction
from block_chain_grpc import blockchain_pb2_grpc, blockchain_pb2
from block_chain_grpc.mapper import block_to_grpc, tx_to_grpc
from block_chain_sync.blockchain_sync import BlockChainSyncAbstract
from container import Container


class BlockchainServicer(blockchain_pb2_grpc.BlockchainServiceServicer):
    def __init__(self, blockchain: Blockchain, miner: Miner, blockchain_sync: BlockChainSyncAbstract):
        self.blockchain = blockchain
        self.miner = miner
        self.blockchain_sync = blockchain_sync

    def StreamChain(self, request, context):
        for block in self.blockchain.chain:
            block_grpc = block_to_grpc(block)

            # for tx in block.transactions:
            #     tx_grpc = tx_to_grpc(tx)
            #     block_grpc.transactions.append(tx_grpc)

            yield block_grpc

    def GetChainInfor(self, request, context):
        return blockchain_pb2.ChainInfor(
            difficulty=self.blockchain.difficulty,
            length=len(self.blockchain.chain),
            last_block_hash=self.blockchain.get_last_block().hash,
            last_merkle_root=self.blockchain.get_last_block().merkle_root,
        )

    def GetMempool(self, request, context):
        return blockchain_pb2.Mempool(transactions=[tx_to_grpc(tx) for tx in self.miner.mempool])

    def AddTransaction(self, request, context):
        try:
            tx = Transaction.from_proto(request)
            self.miner.add_transaction(tx, should_emit=False)
        except Exception as e:
            print(f"Failed to process transaction: {str(e)}")
            context.abort(grpc.StatusCode.INVALID_ARGUMENT, f"Failed to process transaction: {str(e)}")

        return blockchain_pb2.Empty()

    def AddBlock(self, request, context):
        print(f"Received block: Block hash: {request.hash}")
        try:
            block = Block.from_proto(request)
            self.blockchain.add_block(block, should_emit=False)
            # self.blockchain_sync.broadcast_block(block)
            self.miner.clear_tx_list(block.transactions)
        except Exception as e:
            print(f"Failed to process block: {str(e)}")
            context.abort(grpc.StatusCode.INVALID_ARGUMENT, f"Failed to process block: {str(e)}")

        return blockchain_pb2.Empty()

    def AddNode(self, request, context):
        try:
            self.blockchain_sync.add_node(request.ip)

            response = blockchain_pb2.NodeAddressList()

            for node_ip in self.blockchain_sync.nodes:
                node = response.ips.add()
                node.ip = node_ip

            return response
        except Exception as e:
            print(f"Failed to add node: {str(e)}")
            context.abort(grpc.StatusCode.INVALID_ARGUMENT, f"Failed to add node: {str(e)}")
            return None


def serve_grpc(port: int = 50051):
    container = Container()
    blockchain = container.block_chain
    miner = container.miner
    blockchain_sync = container.block_chain_sync

    blockchain_service = BlockchainServicer(blockchain, miner, blockchain_sync)

    server = grpc.server(futures.ThreadPoolExecutor(max_workers=10))
    blockchain_pb2_grpc.add_BlockchainServiceServicer_to_server(blockchain_service, server)
    server.add_insecure_port(f'[::]:{port}')
    server.start()
    print(f"Blockchain node gRPC server started at port {port}.")
    server.wait_for_termination()

# if __name__ == "__main__":
#     serve()
