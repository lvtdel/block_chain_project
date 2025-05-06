import asyncio
import threading
from concurrent.futures import ThreadPoolExecutor
import time
from multiprocessing import cpu_count

from block_chain_core.block import Block
from block_chain_core.block_chain import Blockchain
from block_chain_core.mine import mine_block_multiprocessing
from block_chain_core.transation import Transaction
from exception.transaction_nonce_validation_exceptions import TransactionVerificationFailedException, \
    BlockchainNonceInvalidException, MempoolNonceInvalidException


class Miner:
    def __init__(self, blockchain: Blockchain, max_transaction_per_block, miner_id: str = "fff"):
        self.blockchain = blockchain
        self.miner_id = miner_id
        self.mempool: list[Transaction] = []
        self.mem_temp: list[Transaction] = []
        self.__is_mining = False
        self.mining_thread = None
        self.max_transaction_per_block = max_transaction_per_block
        self.must_stop_mine = False
        self.__lock = threading.Lock()

        self.start_repeat_mine()
        self.ee = self.blockchain.ee

    def start_repeat_mine(self):
        def run_async_in_thread():
            while True:
                # print("Repeat mine")
                self.repeat_mine()
                time.sleep(4)

        threading.Thread(target=run_async_in_thread, daemon=False).start()

    def repeat_mine(self):
        if len(self.mempool) == 0 or self.__is_mining:
            return
        if time.time() - self.blockchain.get_last_block().timestamp < 3:
            return

        self.start_mining()

    def add_transaction(self, transaction, should_emit=True):
        with self.__lock:
            if not transaction.verify():
                raise TransactionVerificationFailedException()
            if not self.is_nonce_valid(transaction.sender, transaction.nonce):
                raise MempoolNonceInvalidException()
            if not self.blockchain.is_nonce_valid(transaction.sender, transaction.nonce):
                raise BlockchainNonceInvalidException()

            self.mempool.append(transaction)
            self.ee.emit('add_new_transaction', transaction)
            if should_emit:
                self.ee.emit('sync:add_new_transaction', transaction)

            if len(self.mempool) >= self.max_transaction_per_block:
                self.start_mining()

            return True

    def start_mining(self):
        if self.__is_mining or self.must_stop_mine:
            # print("Already mining...")
            return

        self.__is_mining = True
        self.mem_temp = self.mempool[:self.max_transaction_per_block]

        # print("Start mining...")
        threading.Thread(target=self.mine_process, daemon=False).start()
        # self.executor.submit(self.mine_process)

        # self.mining_thread = threading.Thread(target=self.mine_process)
        # self.mining_thread.daemon = False
        # self.mining_thread.start()

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
            # print("End mining.")

            if nonce == -1:
                print("No valid nonce found.")
            else:
                new_block.nonce = nonce
                new_block.hash = new_block.compute_hash()
                # print(f"Block mined: {new_block.hash}")

                self.blockchain.add_block(new_block)
                for tx in self.mem_temp:
                    if tx in self.mempool:
                        self.mempool.remove(tx)
                self.mem_temp = []

        finally:
            self.__is_mining = False

    def is_nonce_valid(self, sender: str, nonce: int) -> bool:
        for tx in self.mempool:
            if tx.sender == sender and tx.nonce == nonce:
                return False

        return True

    def clear_tx_list(self, tx_list: list[Transaction]):
        for tx in tx_list:
            if tx in self.mempool:
                self.mempool.remove(tx)
                print(f"Removed tx from mempool: {tx.hash}")