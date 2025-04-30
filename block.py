import json
import hashlib


class Block:
    def __init__(self, index, transactions, timestamp, previous_hash, nonce=0):
        self.index = index
        self.transactions = transactions  # list of dict
        self.timestamp = timestamp
        self.previous_hash = previous_hash
        self.nonce = nonce
        self.merkle_root = self.compute_merkle_root()
        self.hash = self.compute_hash()

    def compute_merkle_root(self):
        def hash_pair(a, b):
            return hashlib.sha256((a + b).encode()).hexdigest()

        tx_hashes = [hashlib.sha256(json.dumps(tx, sort_keys=True).encode()).hexdigest()
                     for tx in self.transactions]

        while len(tx_hashes) > 1:
            if len(tx_hashes) % 2 == 1:  # make even
                tx_hashes.append(tx_hashes[-1])
            tx_hashes = [hash_pair(tx_hashes[i], tx_hashes[i + 1])
                         for i in range(0, len(tx_hashes), 2)]

        return tx_hashes[0] if tx_hashes else ''

    def compute_hash(self):
        block_string = json.dumps({
            "index": self.index,
            "transactions": self.transactions,
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
