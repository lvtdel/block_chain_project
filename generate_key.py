from sign_transation import generate_eth_key_pair, key_infor

if __name__ == '__main__':
    private_key_generate = generate_eth_key_pair()
    print("Key generated:")
    key_infor(private_key_generate)
    print("---------")