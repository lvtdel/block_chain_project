import time

from eth_keys import keys
from eth_utils import keccak
import json


class Transaction:
    def __init__(self, tx_type, payload: str, sender, signature, nonce, receiver=None, ):
        self.tx_type = tx_type  # e.g. 'payment', 'document', 'vote', etc.
        self.payload = payload  # Dữ liệu cụ thể (dict, text...)
        self.sender = sender
        self.receiver = receiver
        self.signature = signature
        self.nonce = nonce
        self.timestamp = time.time()
        self.hash = self.compute_hash_msg().hex()

    @staticmethod
    def from_proto(proto_tx):
        new_tx = Transaction(
            tx_type=proto_tx.tx_type,
            payload=proto_tx.payload,
            sender=proto_tx.sender,
            receiver=proto_tx.receiver,
            signature=proto_tx.signature,
            nonce=proto_tx.nonce,
        )
        new_tx.timestamp = proto_tx.timestamp
        new_tx.hash = proto_tx.hash
        return new_tx

    def to_dict(self):
        return {
            "tx_type": self.tx_type,
            "payload": self.payload,
            "sender": self.sender,
            "receiver": self.receiver,
            "nonce": self.nonce
        }

    def compute_hash_msg(self):
        message = json.dumps(self.to_dict(), sort_keys=True).encode('utf-8')
        return keccak(message)

    # Hàm: xác minh chữ ký từ giao dịch + chữ ký
    def verify(self) -> bool:
        tx_hash = self.compute_hash_msg()
        signature_hex = self.signature

        signature = keys.Signature(
            bytes.fromhex(signature_hex[2:] if signature_hex.startswith("0x") else signature_hex))
        pub_key = signature.recover_public_key_from_msg_hash(tx_hash)
        recovered_address = pub_key.to_checksum_address()

        return recovered_address.lower() == self.sender.lower()

    def __str__(self):
        # dct = self.__dict__
        # dct['tx_hash'] = self.compute_hash_msg().hex()
        return self.__dict__.__str__()

    def __repr__(self):
        return self.__str__()

    def to_json(self):
        return json.dumps(self.__dict__, indent=4)

    def __eq__(self, other):
        if not isinstance(other, Transaction):
            return False
        return self.hash == other.hash

    def __hash__(self):
        return hash(self.hash)
