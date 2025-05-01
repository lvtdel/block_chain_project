import asyncio
import json
from multiprocessing import Process, Value
import time
from os import cpu_count

from pyee import EventEmitter

from block_chain_core.block import Block
from block_chain_core.block_chain import Blockchain
from block_chain_core.miner import Miner
from block_chain_core.transation import Transaction


# Tạo hàm main() bất đồng bộ
async def main():
    ee = EventEmitter()
    bc = Blockchain(difficulty=4, ee=ee)
    miner = Miner(bc, 3)

    tx1 = Transaction("payment", "Bob", "Alice", "Bob", "")
    tx2 = Transaction("payment", "Bob", "Alice", "Bob","")
    miner.add_transaction(tx1)
    miner.add_transaction(tx2)

    # print(json.dumps({"from": "Alice", "to": "Bob", "amount": 10}, sort_keys=True).encode())

    # Đợi cho quá trình đào hoàn tất
    # await bc.mine_pending_transactions()

    # In kết quả
    @ee.on('add_new_block')
    def print_new_block(block: Block):
        for block in bc.chain:
            print(f"\nBlock {block.index}")
            print(f"Hash: {block.hash}")
            print(f"Prev: {block.previous_hash}")
            print(f"Transactions: {block.transactions}")
        print(bc.is_chain_valid())




if __name__ == '__main__':
    # Chạy hàm main() trong event loop
    asyncio.run(main())
