import asyncio
import threading
from concurrent.futures import ThreadPoolExecutor
import time
from multiprocessing import cpu_count

from block import Block
from block_chain import Blockchain, mine_block_multiprocessing

# executor = ThreadPoolExecutor()

class Miner:
    def __init__(self, blockchain: Blockchain, miner_id: str = "fff"):
        self.blockchain = blockchain
        self.miner_id = miner_id
        self.mempool = []
        self.mem_temp = []
        self.__is_mining = False
        self.mining_thread = None
        self.start_repeat_mining()

    def start_repeat_mining(self):
        def schedule_next():
            self.repeat_mine()
            # Lập lịch cho lần chạy tiếp theo
            threading.Timer(4, schedule_next).start()

        schedule_next()

    def repeat_mine(self):
        if len(self.mempool) == 0 or self.__is_mining:
            return
        if time.time() - self.blockchain.get_last_block().timestamp < 3:
            return

        self.start_mining()

    def add_transaction(self, transaction):
        self.mempool.append(transaction)
        self.start_mining()

    def start_mining(self):
        if self.__is_mining:
            return

        self.__is_mining = True
        self.mem_temp = self.mempool[:5]

        self.mining_thread = threading.Thread(target=self.mine_process)
        self.mining_thread.daemon = False
        self.mining_thread.start()

    def mine_process(self):
        try:
            new_block = Block(
                index=len(self.blockchain.chain),
                transactions=self.mem_temp,
                timestamp=time.time(),
                previous_hash=self.blockchain.get_last_block().hash
            )

            print("Mining block...")

            nonce = mine_block_multiprocessing(new_block, 
                                            difficulty=self.blockchain.difficulty, 
                                            processes=cpu_count())
            
            if nonce == -1:
                print("No valid nonce found.")
            else:
                new_block.nonce = nonce
                new_block.hash = new_block.compute_hash()
                print(f"Block mined: {new_block.hash}")
                
                self.blockchain.add_block(new_block)
                for tx in self.mem_temp:
                    if tx in self.mempool:
                        self.mempool.remove(tx)
                self.mem_temp = []

        finally:
            self.__is_mining = False