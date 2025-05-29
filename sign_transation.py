import os
import secrets
from copy import deepcopy

from eth_keys import keys
from eth_utils import keccak
import json

from block_chain_core.transation import Transaction


def generate_eth_key_pair():
    # Tạo private key ngẫu nhiên 32 bytes
    private_key_bytes = secrets.token_bytes(32)
    private_key = keys.PrivateKey(private_key_bytes)

    return private_key


def read_private_key_from_file(file_path: str) -> keys.PrivateKey:
    with open(file_path, 'r') as file:
        private_key_hex = file.readline().strip()

    if private_key_hex.startswith("0x"):
        private_key_hex = private_key_hex[2:]

    private_key = keys.PrivateKey(bytes.fromhex(private_key_hex))
    return private_key


def sign_transaction(tx_hash_msg, private_key_hex: str) -> str:
    private_key_bytes = bytes.fromhex(private_key_hex[2:] if private_key_hex.startswith("0x") else private_key_hex)
    private_key = keys.PrivateKey(private_key_bytes)

    signature = private_key.sign_msg_hash(tx_hash_msg)
    return signature.to_hex()


def key_infor(private_key: keys.PrivateKey):
    private_key_hex = private_key.to_hex()

    public_key = private_key.public_key
    sender_address = public_key.to_checksum_address()

    print(f"Private key: {private_key_hex}")
    print(f"Public key: {public_key.to_hex()}")
    print(f"Sender address: {sender_address}")


if __name__ == '__main__':
    # private_key_generate = generate_eth_key_pair()
    # print("Key generated:")
    # key_infor(private_key_generate)
    # print("---------")


    private_key = read_private_key_from_file(os.path.join(os.getcwd(), "private_key_1"))
    print("Key read from file:")
    key_infor(private_key)

    sender_address = private_key.public_key.to_checksum_address()

    ## Tạo transaction và ký
    nonce = 1
    payload = '{"amount": 100, "currency": "USD"}'
    # payload = 'Trong bối cảnh công nghệ hiện đại phát triển vượt bậc, việc ứng dụng các giải pháp công nghệ vào quản lý và giảng dạy trong môi trường giáo dục là một xu hướng tất yếu. Đề tài "Hệ thống điểm danh bằng điện thoại sinh viên tích hợp nhận diện khuôn mặt" được thực hiện nhằm mục đích nâng cao hiệu quả và tính chính xác trong quá trình điểm danh, đồng thời tạo điều kiện thuận lợi cho cả giảng viên và sinh viên.'
    type = "payment"
    tx = Transaction(type, payload, sender_address, "", nonce=nonce,
                     receiver="0xf0faC6cc7eB427268C405A462bF304a2ac84A425")
    tx.signature = sign_transaction(tx.compute_hash_msg(), private_key.to_hex())

    # tx_sample = Transaction("payment", '{"amount": 100, "currency": "USD"}', sender_address,
    #                         "0x42868f4a930ce991eb99ef1d1bcc97658b5539607db607d64196cb0a5bd438ba4aad85ba0c5169c59431bbf66e0d714220241f243246ba53d09e8833a1e8f33200",
    #                         nonce=nonce,
    #                         receiver="0xf0faC6cc7eB427268C405A462bF304a2ac84A425")
    print(tx.to_json())
    # print(f"'{tx.signature}'")
    print(tx.verify())
