import asyncio
from multiprocessing import Process, Value
import time

from pyee import EventEmitter

from block import Block
from block_chain import Blockchain
from mine import mine_worker
from miner import Miner


# Tạo hàm main() bất đồng bộ
async def main():
    ee = EventEmitter()
    bc = Blockchain(difficulty=4, ee=ee)
    miner = Miner(bc)

    miner.add_transaction({"from": "Alice", "to": "Bob", "amount": 10})
    miner.add_transaction({"from": "Bob", "to": "Charlie", "amount": 5})

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
