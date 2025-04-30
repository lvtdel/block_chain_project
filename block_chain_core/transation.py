import hashlib
import json


class Transaction:
    def __init__(self, tx_type, payload, sender=None, receiver=None):
        self.tx_type = tx_type  # e.g. 'payment', 'document', 'vote', etc.
        self.payload = payload  # Dữ liệu cụ thể (dict, text...)
        self.sender = sender
        self.receiver = receiver

    def to_dict(self):
        return {
            "type": self.tx_type,
            "payload": self.payload,
            "sender": self.sender,
            "receiver": self.receiver
        }

    def compute_hash(self):
        return hashlib.sha256(json.dumps(self.to_dict(), sort_keys=True).encode()).hexdigest()

    def __str__(self):
        return f"{{type: {self.tx_type}, payload: {self.payload}, sender: {self.sender}, receiver: {self.receiver}}}"

    def __repr__(self):
        return self.__str__()