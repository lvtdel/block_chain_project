import asyncio
import json
import threading
from multiprocessing import cpu_count

from pyee import EventEmitter
from pyee.asyncio import AsyncIOEventEmitter

import time

from block_chain_core.block import Block
from block_chain_core.mine import run_async_in_thread
from block_chain_core.transation import Transaction


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
        first_tx = Transaction("payment", "{\"amount\": 100, \"currency\": \"USD\"}", "0", "0", "", "0xd206080A25862e79C74B804273936A0e843DAa03")
        genesis_block = Block(0, [first_tx], 0, "0")
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

    def get_all_transactions(self):
        transactions = []
        for block in self.chain:
            for tx in block.transactions:
                tx_dict = tx.__dict__.copy()
                tx_dict['block_hash'] = block.hash
                tx_dict['block_index'] = block.index
                tx_dict['block_timestamp'] = block.timestamp
                transactions.append(tx_dict)
        return transactions

    def get_address_balance(self, address: str) -> dict:
        """
        Kiểm tra số dư của một địa chỉ trong blockchain

        Args:
            address (str): Địa chỉ cần kiểm tra số dư

        Returns:
            dict: Dictionary chứa thông tin số dư theo từng loại tiền tệ
        """
        balances = {}  # Dict lưu số dư theo từng loại tiền

        # Duyệt qua tất cả các block trong blockchain
        for block in self.chain:
            for tx in block.transactions:
                # Kiểm tra giao dịch có phải loại payment không
                if tx.tx_type.lower() != 'payment':
                    continue

                try:
                    # Parse payload để lấy thông tin amount và currency
                    payload = json.loads(tx.payload)
                    amount = float(payload.get('amount', 0))
                    currency = payload.get('currency', '').upper()

                    # Nếu currency chưa có trong balances thì khởi tạo
                    if currency not in balances:
                        balances[currency] = 0

                    # Nếu địa chỉ là người nhận, cộng số tiền
                    if tx.receiver == address:
                        balances[currency] += amount

                    # Nếu địa chỉ là người gửi, trừ số tiền
                    if tx.sender == address:
                        balances[currency] -= amount

                except (json.JSONDecodeError, KeyError, ValueError):
                    # Bỏ qua nếu payload không hợp lệ
                    continue

        return {
            'address': address,
            'balances': balances,
            'total_transactions': sum(
                1 for block in self.chain
                for tx in block.transactions
                if tx.sender == address or tx.receiver == address
            ),
            'last_updated': int(time.time())  # Thời gian cập nhật cuối
        }