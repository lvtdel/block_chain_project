class TransactionVerificationFailedException(Exception):
    """Raised when transaction verification fails."""
    def __init__(self, message="Transaction verification failed."):
        super().__init__(message)


class BlockchainNonceInvalidException(Exception):
    """Raised when nonce is not valid in the blockchain."""
    def __init__(self, message="Nonce validation failed in Blockchain."):
        super().__init__(message)


class MempoolNonceInvalidException(Exception):
    """Raised when nonce is not valid in the mempool."""
    def __init__(self, message="Nonce validation failed in Mempool."):
        super().__init__(message)