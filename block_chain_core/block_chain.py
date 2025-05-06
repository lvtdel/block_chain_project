import asyncio
import threading
from multiprocessing import cpu_count

from pyee import EventEmitter
from pyee.asyncio import AsyncIOEventEmitter

import time

from block_chain_core.block import Block
from block_chain_core.mine import run_async_in_thread


class Blockchain:
    def __init__(self, difficulty=2, ee=EventEmitter()):
        self.chain: list[Block] = []
        self.difficulty = difficulty
        # self.pending_transactions = []
        self.create_genesis_block()
        self.__ee = ee
        self._lock = threading.Lock()

        # self.ee = AsyncIOEventEmitter()
        # self.ee.on('add_transaction', self.on_add_transaction)

    @property
    def ee(self):
        return self.__ee

    def create_genesis_block(self):
        genesis_block = Block(0, [], 0, "0")
        self.chain.append(genesis_block)

    def add_block(self, block: Block, validate=True, should_emit=True):
        with self._lock:
            if validate:
                if not self.is_new_block_valid(block):
                    print(f"Invalid block, block discarded: Block hash {block.hash}")
                    return

            self.chain.append(block)
            self.__ee.emit('add_new_block', block)
            if should_emit: self.__ee.emit('sync:add_new_block', block)

    def is_new_block_valid(self, block: Block):
        if not block.is_valid(self.difficulty): return False
        if block.previous_hash != self.get_last_block().hash:
            return False

        for tx in block.transactions:
            if not tx.verify(): return False

        return True

    def get_last_block(self):
        return self.chain[-1]

    def is_chain_valid(self):
        for i in range(1, len(self.chain)):
            curr = self.chain[i]
            prev = self.chain[i - 1]

            if curr.hash != curr.compute_hash():
                return False
            if curr.previous_hash != prev.hash:
                return False
            if not curr.is_valid(self.difficulty):
                return False

        return True

    def find_transaction(self, tx_hash: str):
        for block in self.chain:
            for tx in block.transactions:
                if tx.hash == tx_hash:
                    block_dict = block.to_dict()
                    block_dict.pop('transactions')
                    return {"block": block_dict, "tx": tx.__dict__}

        return False

    def find_block(self, block_hash: str):
        for block in self.chain:
            if block.hash == block_hash:
                return block

        return False

    def is_nonce_valid(self, sender: str, nonce: int) -> bool:
        for block in self.chain:
            for tx in block.transactions:
                if tx.sender == sender and tx.nonce == nonce:
                    return False

        return True
