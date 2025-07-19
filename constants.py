from enum import Enum


class MessageType:
    TX = "tx"
    BLOCK = "block"
    REQUEST_CHAIN = "request_chain"
    CHAIN = "chain"
    MINING = "mining"
    REBROADCAST = "rebroadcast"
    FINALISE_BLOCK = "finalize_block"
    DISCONNECT = "disconnect"

class MessageField:
    TYPE = "type"
    DATA = "data"

class TxInputField:
    TX_ID = "tx_id"
    INDEX = "index"
    SIGNATURE = "signature"
    PUBKEY = "pubkey"

class TxOutputField:
    AMOUNT = "amount"
    ADDRESS = "address"

class TxField:
    INPUTS = "inputs"
    OUTPUTS = "outputs"
    METADATA = "metadata"

class MetadataType:
    HEIGHT = "height"

class BlockField:
    INDEX = "index"
    PREVIOUS_HASH = "previous_hash"
    TRANSACTIONS = "transactions"
    NONCE = "nonce"
    TIMESTAMP = "timestamp"

class BlockchainField:
    BLOCKS = "blocks"

class DisconnectField:
    HOST = "host"
    PORT = "port"

class Role(Enum):
    MINER = "miner"
    USER = "user"

class Stage(Enum):
    TX = "tx"
    MINING = "mining"

class Constants:
    TIME_TO_SLEEP = 60
    MINER_REWARD = 50
    DIFFICULTY = 3

class RebroadcastField:
    HOST = "host"
    PORT = "port"
    BLOCK = "block"