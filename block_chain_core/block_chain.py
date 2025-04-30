from multiprocessing import cpu_count

from pyee import EventEmitter
from pyee.asyncio import AsyncIOEventEmitter

import time

from block_chain_core.block import Block


class Blockchain:
    def __init__(self, difficulty=2, ee = EventEmitter):
        self.chain: list[Block] = []
        self.difficulty = difficulty
        self.pending_transactions = []
        self.create_genesis_block()
        self.__ee = ee

        # self.ee = AsyncIOEventEmitter()
        # self.ee.on('add_transaction', self.on_add_transaction)

    def create_genesis_block(self):
        genesis_block = Block(0, [], time.time(), "0")
        self.chain.append(genesis_block)

    def add_block(self, block: Block):
        if not self.is_new_block_valid(block):
            print("Invalid block, block discarded.")

        self.chain.append(block)
        self.__ee.emit('add_new_block', block)

    def is_new_block_valid(self, block: Block):
        if block.previous_hash != self.get_last_block().hash:
            return False
        if not block.hash.startswith('0' * self.difficulty):
            return False
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
            if not curr.hash.startswith('0' * self.difficulty):
                return False

        return True
