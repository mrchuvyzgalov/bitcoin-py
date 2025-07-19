import pytest
from blockchain import Blockchain, Block
from transaction import Transaction, TxInput, TxOutput


@pytest.fixture
def blockchain():
    return Blockchain()


def test_create_genesis_block(blockchain):
    genesis = blockchain.chain[0]
    assert genesis.index == 0
    assert genesis.previous_hash == "0" * 64
    assert genesis.transactions == []


def test_mine_block_contains_coinbase(blockchain):
    block = blockchain.mine_block("miner1")
    coinbase_tx = block.transactions[0]
    assert coinbase_tx.outputs[0].amount == 50
    assert coinbase_tx.outputs[0].address == "miner1"


def test_add_valid_transaction(blockchain):
    cb = Transaction([], [TxOutput(100, "alice")])
    blockchain.chain.append(Block(1, blockchain.chain[-1].hash(), [cb]))
    blockchain.rebuild_utxo_set()

    tx = Transaction([TxInput(cb.hash(), 0, "", "")], [TxOutput(60, "bob"), TxOutput(40, "alice")])
    assert blockchain.add_transaction(tx) is True
    assert tx in blockchain.pending_txs


def test_duplicate_transaction_fails(blockchain):
    cb = Transaction([], [TxOutput(100, "alice")])
    blockchain.chain.append(Block(1, blockchain.chain[-1].hash(), [cb]))
    blockchain.rebuild_utxo_set()

    tx = Transaction([TxInput(cb.hash(), 0, "", "")], [TxOutput(100, "bob")])
    blockchain.add_transaction(tx)
    assert blockchain.add_transaction(tx) is False


def test_transaction_with_invalid_input_fails(blockchain):
    tx = Transaction([TxInput("bad_id", 0, "", "")], [TxOutput(10, "bob")])
    assert blockchain.validate_transaction(tx) is False


def test_transaction_with_overspend_fails(blockchain):
    cb = Transaction([], [TxOutput(30, "alice")])
    blockchain.chain.append(Block(1, blockchain.chain[-1].hash(), [cb]))
    blockchain.rebuild_utxo_set()

    tx = Transaction([TxInput(cb.hash(), 0, "", "")], [TxOutput(40, "bob")])
    assert blockchain.validate_transaction(tx) is False


def test_get_balance(blockchain):
    cb = Transaction([], [TxOutput(80, "alice")])
    blockchain.chain.append(Block(1, blockchain.chain[-1].hash(), [cb]))
    blockchain.rebuild_utxo_set()

    assert blockchain.get_balance("alice") == 80.0
    assert blockchain.get_balance("bob") == 0.0


def test_valid_block_passes_validation(blockchain):
    cb = Transaction([], [TxOutput(100, "alice")])
    blockchain.chain.append(Block(1, blockchain.chain[-1].hash(), [cb]))
    blockchain.rebuild_utxo_set()

    tx = Transaction([TxInput(cb.hash(), 0, "", "")], [TxOutput(70, "bob"), TxOutput(30, "alice")])
    block = Block(2, blockchain.chain[-1].hash(), [tx])
    assert blockchain.validate_block(block) is True


def test_add_block_invalid_prev_hash(blockchain):
    bad_block = Block(1, "bad_prev_hash", [])
    assert blockchain.add_block(bad_block) is False


def test_try_to_update_chain(blockchain):
    new_chain = [blockchain.chain[0]]
    cb = Transaction([], [TxOutput(100, "alice")])
    new_block = Block(1, blockchain.chain[0].hash(), [cb])
    new_chain.append(new_block)

    blockchain.try_to_update_chain(new_chain)
    assert len(blockchain.chain) == 2
    assert blockchain.get_balance("alice") == 100
