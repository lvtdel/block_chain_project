import asyncio
import threading
from copy import deepcopy
from multiprocessing import Process, Value, cpu_count

from block_chain_core.block import Block


def mine_worker(start_nonce, step, block: Block, difficulty: int, result_nonce: Value, found_flag: Value):
    prefix = '0' * difficulty
    nonce = start_nonce

    while (not found_flag.value) or (nonce < start_nonce + 10000):
        block.nonce = nonce
        current_hash = block.compute_hash()
        if current_hash.startswith(prefix):
            with result_nonce.get_lock(), found_flag.get_lock():
                if not found_flag.value:
                    # print(f"Found result nonce: {nonce}")
                    result_nonce.value = nonce
                    found_flag.value = 1
            return
        nonce += step
        # print(f"Current nonce: {nonce} ", flush=True)


def mine_block_multiprocessing(block: Block, difficulty: int, processes: int = 4):
    result_nonce = Value('i', 0)
    found_flag = Value('i', 0)

    workers = []
    for i in range(processes):
        block_copy = deepcopy(block)

        p = Process(target=mine_worker, args=(i * 1000, 1, block_copy, difficulty, result_nonce, found_flag))
        p.start()
        workers.append(p)

    for p in workers:
        p.join()

    # block.nonce = result_nonce.value
    # block.hash = block.compute_hash()

    # print(f"Nonce found: {result_nonce.value}")
    # block.nonce = result_nonce.value
    # print(f"Hash : {block.compute_hash()}")
    return result_nonce.value if found_flag.value else -1

def run_async_in_thread(coro):
    threading.Thread(target=lambda: asyncio.run(coro)).start()