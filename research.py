import random
import sys
import time

from constants import Role, Stage
from main import ensure_wallet, choose_port, create_transaction
from node import Node

def start_research(node: Node, addresses: list[str]) -> (int, float): # (amount of added txs, time)
    coins_to_send = 1

    amount_of_blocks_before = len(node.blockchain.chain)
    amount_of_generated_blocks = 3

    amount_of_added_txs = 0
    start = time.time()

    delay = 0.12

    while len(node.blockchain.chain) - amount_of_blocks_before != amount_of_generated_blocks:
        if node.get_stage() != Stage.TX:
            time.sleep(delay)
            continue

        tx = create_transaction(node, random.choice(addresses), coins_to_send)
        if node.add_and_broadcast_tx(tx):
            amount_of_added_txs += 1

        time.sleep(delay)

    return amount_of_added_txs, time.time() - start

def prepare_miner(node: Node, amount_of_blocks: int):
    for i in range(amount_of_blocks):
        new_block = node.blockchain.mine_block(node.address)
        node.verify_and_add_block(new_block)

def show_menu(node: Node):
    addresses: list[str] = []

    while True:
        print("\n===== Menu =====")
        print("1. Show address")
        print("2. Add address")
        print("3. Start research")
        print("0. Exit")

        choice = input("Choice: ").strip()
        if choice == "1":
            print("🏠 Address:", node.address)
        elif choice == "2":
            address = input("New address: ")
            addresses.append(address)
            print("New address was added")
        elif choice == "3":
            print("Research started")
            tx_amount, sec = start_research(node, addresses)
            print("Amount of transactions: ", tx_amount)
            print("Time spent: ", sec / 60.0, " minutes")
            print("TPS: ", tx_amount / sec)
        elif choice == "0":
            node.disconnect()
            print("👋 Goodbye!")
            break
        else:
            print("⚠️ Incorrect input")

if __name__ == "__main__":
    role = Role.USER

    if len(sys.argv) > 1:
        command = sys.argv[1]
        if command == "miner":
            role = Role.MINER

    ensure_wallet()
    port = choose_port()
    node = Node("0.0.0.0", port, role)

    if role == Role.MINER:
        print("Started preparing miner")
        prepare_miner(node, 2000)
        print("Finished preparing miner")

    node.start()

    show_menu(node)