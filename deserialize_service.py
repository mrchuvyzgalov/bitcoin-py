from typing import List

from blockchain import Block
from constants import TxField, BlockField, BlockchainField, DisconnectField
from transaction import Transaction, TxInput, TxOutput


class DeserializeService:
    @staticmethod
    def deserialize_tx(data: dict) -> Transaction:
        inputs = [TxInput(**i) for i in data[TxField.INPUTS]]
        outputs = [TxOutput(**o) for o in data[TxField.OUTPUTS]]
        metadata = data.get(TxField.METADATA, {})
        return Transaction(inputs, outputs, metadata)

    @staticmethod
    def deserialize_block(data: dict):
        txs = [DeserializeService.deserialize_tx(tx) for tx in data[BlockField.TRANSACTIONS]]
        return Block(
            index=data[BlockField.INDEX],
            previous_hash=data[BlockField.PREVIOUS_HASH],
            transactions=txs,
            nonce=data[BlockField.NONCE],
            timestamp=data[BlockField.TIMESTAMP]
        )

    @staticmethod
    def deserialize_chain(data: dict) -> List[Block]:
        blocks = [DeserializeService.deserialize_block(block) for block in data[BlockchainField.BLOCKS]]
        return blocks

    @staticmethod
    def deserialize_disconnect(data: dict) -> (str, int):
        return data[DisconnectField.HOST], data[DisconnectField.PORT]