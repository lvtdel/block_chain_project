class VerificationException(Exception):
    """Base class for all exceptions raised by this module."""
    def __init__(self, message="Verification failed."):
        super().__init__(message)

class TransactionVerificationFailedException(VerificationException):
    """Raised when transaction verification fails."""
    def __init__(self, message="Transaction verification failed."):
        super().__init__(message)


class BlockchainNonceInvalidException(VerificationException):
    """Raised when nonce is not valid in the blockchain."""
    def __init__(self, message="Nonce validation failed in Blockchain."):
        super().__init__(message)


class MempoolNonceInvalidException(VerificationException):
    """Raised when nonce is not valid in the mempool."""
    def __init__(self, message="Nonce validation failed in Mempool."):
        super().__init__(message)