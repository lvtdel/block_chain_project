import grpc
from pyee import EventEmitter

from block_chain_core.block import Block
from block_chain_core.block_chain import Blockchain
from block_chain_grpc import blockchain_pb2
from block_chain_grpc import blockchain_pb2_grpc


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

# get_chain_from_node()
if __name__ == '__main__':
    block_chain = get_chain_from_node()
    print(f"Blockchain: {block_chain.chain}")