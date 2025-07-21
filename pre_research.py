import json

from constants import Role, Constants, MetadataType
from node import Node
from transaction import Transaction, TxOutput


def prepare_miner(node: Node, amount_of_blocks: int, amount_of_tx_in_block: int):
    for i in range(amount_of_blocks):
        height = len(node.blockchain.chain)
        for j in range(amount_of_tx_in_block):
            tx = Transaction([],
                             [TxOutput(Constants.MINER_REWARD, node.address)],
                             {
                                 MetadataType.HEIGHT: height,
                                 "number_of_block": i + 1,
                                 "number_of_tx": j + 1,
                               })
            node.blockchain.pending_txs.append(tx)
        new_block = node.blockchain.mine_block(node.address)
        node.verify_and_add_block(new_block)
        print(f"Block #{i} added")

    with open(f"research_files/blockchain.json", "w") as f:
        json.dump(node.blockchain.to_dict(), f, indent=2)

if __name__ == "__main__":
    role = Role.MINER
    AMOUNT_OF_BLOCKS = 30
    AMOUNT_OF_TX_IN_BLOCK = 1000

    node = Node("0.0.0.0", 1111, role=role, wallet_file="research_files/miner_wallet.txt")
    prepare_miner(node, AMOUNT_OF_BLOCKS, AMOUNT_OF_TX_IN_BLOCK)

