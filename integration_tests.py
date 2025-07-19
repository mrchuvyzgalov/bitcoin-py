import copy

import pytest
import time
import tempfile

from main import create_transaction
from node import Node
from constants import Role, Constants
from wallet import generate_keypair

Constants.TIME_TO_SLEEP = 60

@pytest.fixture
def temp_wallet_file1():
    privkey, _ = generate_keypair()
    path = tempfile.mktemp()
    with open(path, "w") as f:
        f.write(privkey)
    return path

@pytest.fixture
def temp_wallet_file2():
    privkey, _ = generate_keypair()
    path = tempfile.mktemp()
    with open(path, "w") as f:
        f.write(privkey)
    return path

def test_miner_node_creates_block_and_updates_balance(temp_wallet_file1):
    host = "127.0.0.1"
    port = 1111

    node = Node(host=host, port=port, role=Role.MINER, wallet_file=temp_wallet_file1)
    node.start()

    time.sleep(Constants.TIME_TO_SLEEP * 1.5)

    chain = node.blockchain.chain
    assert len(chain) == 2, "Expected 2 blocks (including genesis)"

    last_block = chain[-1]
    assert len(last_block.transactions) == 1, "The last block must contain 1 transaction"

    coinbase = last_block.transactions[0]
    assert coinbase.is_coinbase(), "The transaction must be coinbase"

    balance = node.blockchain.get_balance(node.address)
    assert balance == Constants.MINER_REWARD, f"The balance should be {Constants.MINER_REWARD}, but it is {balance}"

def test_node_can_synchronize_chain(temp_wallet_file1, temp_wallet_file2):
    host = "127.0.0.1"
    miner_port = 1111
    user_port = 2222

    miner_node = Node(host=host, port=miner_port, role=Role.MINER, wallet_file=temp_wallet_file1)
    user_node = Node(host=host, port=user_port, role=Role.USER, wallet_file=temp_wallet_file2)

    # mocks
    miner_node._external_ip = host
    user_node._external_ip = host

    miner_node._listen_tcp = None
    user_node._listen_tcp = None

    miner_node._handle_tcp_connection = None
    user_node._handle_tcp_connection = None

    miner_node._listen_discovery = None
    user_node._listen_discovery = None

    miner_node._broadcast_presence = None
    user_node._broadcast_presence = None

    def broadcast_to_user(message: dict):
        if len(miner_node.peers) > 0:
            user_node.message_queue.put(message)

    def broadcast_to_miner(message: dict):
        if len(user_node.peers) > 0:
            miner_node.message_queue.put(message)

    miner_node._broadcast = broadcast_to_user
    user_node._broadcast = broadcast_to_miner

    # start miner node
    miner_node.start()

    time.sleep(Constants.TIME_TO_SLEEP * 1.5)

    # start user node
    user_node.start()

    miner_node.peers.add((host, user_port))
    user_node.peers.add((host, miner_port))

    user_node._broadcast_request_chain()

    time.sleep(5)

    miner_chain = copy.deepcopy(miner_node.blockchain.chain)
    user_chain = copy.deepcopy(user_node.blockchain.chain)

    miner_balance = miner_node.blockchain.get_balance(miner_node.address)
    user_balance = user_node.blockchain.get_balance(user_node.address)

    assert len(miner_chain) == 2, "Expected 2 miner blocks (including genesis)"
    assert len(user_chain) == 2, "Expected 2 user blocks (including genesis)"

    assert [b.to_dict() for b in miner_chain] == [b.to_dict() for b in user_chain], "Expected that the chains are identical"

    assert miner_balance == Constants.MINER_REWARD, f"The miner balance should be {Constants.MINER_REWARD}, but it is {user_balance}"
    assert user_balance == 0, f"The user balance should be 0, but it is {user_balance}"

def test_transaction_propagates_between_nodes(temp_wallet_file1, temp_wallet_file2):
    host = "127.0.0.1"
    miner_port = 1111
    user_port = 2222

    miner_node = Node(host=host, port=miner_port, role=Role.MINER, wallet_file=temp_wallet_file1)
    user_node = Node(host=host, port=user_port, role=Role.USER, wallet_file=temp_wallet_file2)

    # mocks
    miner_node._external_ip = host
    user_node._external_ip = host

    miner_node._listen_tcp = None
    user_node._listen_tcp = None

    miner_node._handle_tcp_connection = None
    user_node._handle_tcp_connection = None

    miner_node._listen_discovery = None
    user_node._listen_discovery = None

    miner_node._broadcast_presence = None
    user_node._broadcast_presence = None

    def broadcast_to_user(message: dict):
        if len(miner_node.peers) > 0:
            user_node.message_queue.put(message)

    def broadcast_to_miner(message: dict):
        if len(user_node.peers) > 0:
            miner_node.message_queue.put(message)

    miner_node._broadcast = broadcast_to_user
    user_node._broadcast = broadcast_to_miner

    # start miner node
    miner_node.start()

    time.sleep(Constants.TIME_TO_SLEEP * 1.5)

    # start user node
    user_node.start()

    miner_node.peers.add((host, user_port))
    user_node.peers.add((host, miner_port))

    user_node._broadcast_request_chain()

    time.sleep(5)

    coins_to_send = 3
    tx = create_transaction(miner_node, to_address=user_node.address, amount=coins_to_send)
    miner_node.add_and_broadcast_tx(tx)

    time.sleep(Constants.TIME_TO_SLEEP)

    miner_chain = copy.deepcopy(miner_node.blockchain.chain)
    user_chain = copy.deepcopy(user_node.blockchain.chain)

    miner_balance = miner_node.blockchain.get_balance(miner_node.address)
    user_balance = user_node.blockchain.get_balance(user_node.address)

    expected_miner_balance = Constants.MINER_REWARD * 2 - coins_to_send
    expected_user_balance = coins_to_send

    assert len(miner_chain) == 3, "Expected 3 miner blocks (including genesis)"
    assert len(user_chain) == 3, "Expected 3 user blocks (including genesis)"

    assert miner_balance == expected_miner_balance, \
        f"The miner balance should be {expected_miner_balance}, but it is {miner_balance}"
    assert user_balance == expected_user_balance, \
        f"The user balance should be {expected_user_balance}, but it is {user_balance}"
