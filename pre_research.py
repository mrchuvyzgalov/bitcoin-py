import json

from constants import Role
from node import Node


def prepare_miner(node: Node, amount_of_blocks: int):
    for i in range(amount_of_blocks):
        new_block = node.blockchain.mine_block(node.address)
        node.verify_and_add_block(new_block)

    with open(f"research_files/blockchain.json", "w") as f:
        json.dump(node.blockchain.to_dict(), f, indent=2)

if __name__ == "__main__":
    role = Role.MINER
    AMOUNT_OF_BLOCKS = 2000

    node = Node("0.0.0.0", 1111, role=role, wallet_file="research_files/miner_wallet.txt")
    prepare_miner(node, AMOUNT_OF_BLOCKS)

