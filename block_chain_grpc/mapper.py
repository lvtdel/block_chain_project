from block_chain_core.block import Block
from block_chain_core.transation import Transaction
from block_chain_grpc import blockchain_pb2


def block_to_grpc(block: Block):
    tx_grpc_list = [tx_to_grpc(tx) for tx in block.transactions]

    return blockchain_pb2.Block(
        index=block.index,
        transactions=tx_grpc_list,
        previous_hash=block.previous_hash,
        timestamp=str(block.timestamp),
        hash=block.hash,
        nonce=block.nonce,
        merkle_root=block.merkle_root
    )


def tx_to_grpc(tx: Transaction):
    return blockchain_pb2.Transaction(
        tx_type=tx.tx_type,
        payload=tx.payload.__str__(),
        sender=tx.sender,
        receiver=tx.receiver,
        signature=tx.signature,
        nonce=tx.nonce,
        timestamp=str(tx.timestamp),
        hash=tx.hash
    )