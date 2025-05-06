import os
import threading

from flask.cli import load_dotenv
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

        load_dotenv()
        DIFFICULTY = int(os.getenv('DIFFICULTY', 3))
        MAX_TRANSACTIONS = int(os.getenv('MAX_TRANSACTIONS_PER_BLOCK', 2))
        MY_ADD = os.getenv("MY_ADD")
        REGISTER_ADD = os.getenv("REGISTER_ADD")

        print(f"DIFFICULTY: {DIFFICULTY}")

        self.__ee = EventEmitter()
        self.__block_chain = Blockchain(difficulty=DIFFICULTY, ee=self.__ee)
        self.__miner = Miner(self.__block_chain, MAX_TRANSACTIONS)

        self.__block_chain_sync = BlockChainSync(self.__block_chain, self.__miner, MY_ADD, self.__ee)
        if REGISTER_ADD:
            self.__block_chain_sync.register_node(REGISTER_ADD)
            self.__block_chain_sync.add_node(REGISTER_ADD)

    @property
    def block_chain(self):
        return self.__block_chain

    @property
    def miner(self):
        return self.__miner

    @property
    def ee(self):
        return self.__ee

    @property
    def block_chain_sync(self):
        return self.__block_chain_sync
