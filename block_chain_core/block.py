import json
import hashlib

from block_chain_core.transation import Transaction


class Block:
    def __init__(self, index, transactions, timestamp, previous_hash, nonce=0):
        self.index = index
        self.transactions: list[Transaction] = transactions
        self.timestamp = timestamp
        self.previous_hash = previous_hash
        self.nonce = nonce
        self.merkle_root = self.compute_merkle_root()
        self.hash = self.compute_hash()

    @staticmethod
    def from_proto(proto_block):
        transactions = [Transaction.from_proto(tx) for tx in proto_block.transactions]
        new_block = Block(
            index=proto_block.index,
            previous_hash=proto_block.previous_hash,
            timestamp=float(proto_block.timestamp),  # nếu cần
            nonce=proto_block.nonce,
            transactions=transactions
        )
        new_block.hash = proto_block.hash
        new_block.merkle_root = proto_block.merkle_root
        return new_block

    def compute_merkle_root(self):
        def hash_pair(a, b):
            return hashlib.sha256((a + b).encode()).hexdigest()

        tx_hashes = [tx.compute_hash_msg().hex() for tx in self.transactions]

        while len(tx_hashes) > 1:
            if len(tx_hashes) % 2 == 1:  # make even
                tx_hashes.append(tx_hashes[-1])
            tx_hashes = [hash_pair(tx_hashes[i], tx_hashes[i + 1])
                         for i in range(0, len(tx_hashes), 2)]

        return tx_hashes[0] if tx_hashes else ''

    def compute_hash(self):
        block_string = json.dumps({
            "index": self.index,
            # "transactions": self.transactions,
            "timestamp": self.timestamp,
            "previous_hash": self.previous_hash,
            "nonce": self.nonce,
            "merkle_root": self.merkle_root
        }, sort_keys=True)
        return hashlib.sha256(block_string.encode()).hexdigest()

    def is_valid(self, difficulty):
        return self.hash.startswith('0' * difficulty)

    def __str__(self):
        return (
            f"index: {self.index}, transactions: {len(self.transactions)}, nonce: {self.nonce}, timestamp: {self.timestamp}\n"
            f"merkle_root: {self.merkle_root}\n"
            f"previous_hash: {self.previous_hash}\n"
            f"hash: {self.hash}")

    def to_dict(self):
        return {
            'index': self.index,
            'timestamp': self.timestamp,
            'transactions': [tx.__dict__ for tx in self.transactions],
            'previous_hash': self.previous_hash,
            'hash': self.hash,
            'nonce': self.nonce
        }
    def __repr__(self):
        return self.__str__()