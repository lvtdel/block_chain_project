import os
import threading

from pyee import EventEmitter
from pyee.asyncio import AsyncIOEventEmitter

from block_chain_core.block_chain import Blockchain
from block_chain_core.miner import Miner
from block_chain_sync.blockchain_sync import BlockChainSync


class Container:
    _instance = None
    _lock = threading.Lock()

    def __new__(cls, *args, **kwargs):
        with cls._lock:
            if not cls._instance:
                cls._instance = super(Container, cls).__new__(cls, *args, **kwargs)
        return cls._instance

    def __init__(self):
        if hasattr(self, "_initialized") and self._initialized:
            return
        self._initialized = True

        DIFFICULTY = os.getenv('DIFFICULTY', 3)
        MAX_TRANSACTIONS = os.getenv('MAX_TRANSACTIONS_PER_BLOCK', 2)

        self.__ee = EventEmitter()
        self.__block_chain = Blockchain(difficulty=DIFFICULTY, ee=self.__ee)
        self.__miner = Miner(self.__block_chain, MAX_TRANSACTIONS)
        self.__block_chain_sync = BlockChainSync(self.__block_chain, self.__miner, self.__ee)

    @property
    def block_chain(self):
        return self.__block_chain

    @property
    def miner(self):
        return self.__miner

    @property
    def ee(self):
        return self.__ee
