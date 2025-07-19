import queue
import socket
import threading
import json
import time

from blockchain import Blockchain, Block
from constants import MessageType, MessageField, DisconnectField, Role, Stage, Constants, RebroadcastField
from deserialize_service import DeserializeService
from transaction import Transaction
from wallet import load_wallet, pubkey_to_address


def _get_local_ip():
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    try:
        s.connect(("8.8.8.8", 80))
        ip = s.getsockname()[0]
    except:
        ip = "127.0.0.1"
    finally:
        s.close()
    return ip


class Node:
    def __init__(self, host: str, port: int, role: Role, wallet_file="my_wallet.txt"):
        self._host = host
        self._port = port
        self.peers = set()
        self.blockchain = Blockchain()
        self.wallet = load_wallet(wallet_file)
        self.address = pubkey_to_address(self.wallet)
        self._discovery_port = 9000
        self._external_ip = _get_local_ip()
        self.role = role

        self._pending_blocks: dict[str, list] = {}
        self._block_lock = threading.Lock()

        self.stage: Stage = Stage.TX
        self._stage_lock = threading.Lock()

        self.message_queue = queue.Queue()

        self._mining_thread = None

        print(f"🟢 Node launched at {self._external_ip}:{self._port}")
        print(f"🏠 Wallet address: {self.address[:8]}...")

    def _set_stage(self, stage: Stage):
        with self._stage_lock:
            self.stage = stage

    def get_stage(self) -> Stage:
        with self._stage_lock:
            return self.stage

    def start(self):
        threading.Thread(target=self._listen_tcp, daemon=True).start()
        threading.Thread(target=self._listen_discovery, daemon=True).start()
        threading.Thread(target=self._broadcast_presence, daemon=True).start()
        threading.Thread(target=self._process_message_queue, daemon=True).start()

        self._mining_thread = threading.Thread(target=self._broadcast_mining, daemon=True)
        self._mining_thread.start()

    def _process_message_queue(self):
        while True:
            time.sleep(3)
            message = self.message_queue.get()
            try:
                self._handle_message(message)
            except Exception as e:
                print(f"❌ Error handling message: {e}")

    def disconnect(self):
        self._broadcast_disconnect()

    def verify_and_add_block(self, block):
        if block.previous_hash == self.blockchain.chain[-1].hash():
            if self.blockchain.validate_block(block):
                self._clear_pending_blocks()
                self.blockchain.chain.append(block)
                for tx in block.transactions:
                    self.blockchain.update_utxo_set(tx)
                return True
            else:
                print("❌ The block did not pass validation")
        return False

    def _listen_tcp(self):
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.bind((self._host, self._port))
        sock.listen()
        print("📥 Waiting for TCP connections...")
        while True:
            conn, _ = sock.accept()
            threading.Thread(target=self._handle_tcp_connection, args=(conn,), daemon=True).start()

    def _handle_tcp_connection(self, conn):
        try:
            buffer = b""
            while True:
                chunk = conn.recv(4096)
                if not chunk:
                    break
                buffer += chunk
            data = buffer.decode()
            message = json.loads(data)
            self.message_queue.put(message)
        except Exception as e:
            print("❌ TCP error:", e)
        finally:
            conn.close()

    def _register_pending_block(self, block):
        block_hash = block.hash()
        with self._block_lock:
            if block_hash not in self._pending_blocks:
                self._pending_blocks[block_hash] = [block, 1]
            else:
                self._pending_blocks[block_hash][1] += 1

    def _get_best_pending_block(self):
        with self._block_lock:
            if not self._pending_blocks:
                return None
            block, votes = max(self._pending_blocks.values(), key=lambda x: x[1])
            return block, votes

    def _clear_pending_blocks(self):
        with self._block_lock:
            self._pending_blocks.clear()

    def _try_to_add_block(self):
        if len(self._pending_blocks) > 0:
            best_block, best_votes = self._get_best_pending_block()
            if 2 * best_votes >= len(self.peers):
                if self._is_leader():
                    self._finalize_block(block=best_block)
                    self.message_queue.put(
                        {
                            MessageField.TYPE: MessageType.FINALISE_BLOCK,
                            MessageField.DATA: best_block.to_dict()
                        }
                    )

    def _handle_message(self, message: dict):
        msg_type = message.get(MessageField.TYPE)
        data = message.get(MessageField.DATA)

        if msg_type == MessageType.TX:
            tx = DeserializeService.deserialize_tx(data)
            self.blockchain.add_transaction(tx)

        elif msg_type == MessageType.FINALISE_BLOCK:
            block = DeserializeService.deserialize_block(data)
            self.verify_and_add_block(block)
            self._set_stage(Stage.TX)

            self._mining_thread = threading.Thread(target=self._broadcast_mining, daemon=True)
            self._mining_thread.start()

        elif msg_type == MessageType.REBROADCAST:
            self._set_stage(Stage.MINING)
            host, port, block = DeserializeService.deserialize_rebroadcast(data)

            if block.previous_hash == self.blockchain.chain[-1].hash():
                if self.blockchain.validate_block(block):
                    self._register_pending_block(block)

            self._try_to_add_block()

        elif msg_type == MessageType.BLOCK:
            self._set_stage(Stage.MINING)
            block = DeserializeService.deserialize_block(data)

            if block.previous_hash == self.blockchain.chain[-1].hash():
                self._register_pending_block(block)

                self._rebroadcast_block(block)
                self.message_queue.put(
                    {
                        MessageField.TYPE: MessageType.REBROADCAST,
                        MessageField.DATA: {
                            RebroadcastField.HOST: self._external_ip,
                            RebroadcastField.PORT: self._port,
                            RebroadcastField.BLOCK: block.to_dict()
                        }
                    }
                )

        elif msg_type == MessageType.REQUEST_CHAIN:
            self._broadcast_chain()

        elif msg_type == MessageType.CHAIN:
            blocks = DeserializeService.deserialize_chain(data)
            self.blockchain.try_to_update_chain(blocks)

        elif msg_type == MessageType.MINING:
            self._set_stage(Stage.MINING)
            if self.role == Role.MINER:
                block = self.blockchain.mine_block(self.address)

                self._broadcast_block(block)
                self.message_queue.put({
                    MessageField.TYPE: MessageType.BLOCK,
                    MessageField.DATA: block.to_dict()
                })

        elif msg_type == MessageType.DISCONNECT:
            peer_to_remove = DeserializeService.deserialize_disconnect(data)
            self.peers.remove(peer_to_remove)

        else:
            print("⚠️ Unknown message type:", msg_type)

    def _finalize_block(self, block: Block):
        self._broadcast({
            MessageField.TYPE: MessageType.FINALISE_BLOCK,
            MessageField.DATA: block.to_dict()
        })

    def _rebroadcast_block(self, block: Block):
        self._broadcast({
            MessageField.TYPE: MessageType.REBROADCAST,
            MessageField.DATA: {
                RebroadcastField.HOST: self._external_ip,
                RebroadcastField.PORT: self._port,
                RebroadcastField.BLOCK: block.to_dict()
            },
        })

    def _broadcast_request_chain(self):
        self._broadcast({
            MessageField.TYPE: MessageType.REQUEST_CHAIN
        })

    def _broadcast_disconnect(self):
        self._broadcast({
            MessageField.TYPE: MessageType.DISCONNECT,
            MessageField.DATA: {
                DisconnectField.HOST: self._external_ip,
                DisconnectField.PORT: self._port
            }
        })

    def _broadcast(self, message: dict):
        raw = json.dumps(message).encode()
        for peer in self.peers.copy():
            try:
                with socket.socket() as s:
                    s.connect(peer)
                    s.send(raw)
            except Exception as e:
                print(f"❌ Failed to send {message['type']} → {peer}: {e}")

    def _broadcast_chain(self):
        self._broadcast({
            MessageField.TYPE: MessageType.CHAIN,
            MessageField.DATA: self.blockchain.to_dict()})

    def broadcast_transaction(self, tx: Transaction):
        self._broadcast({
            MessageField.TYPE: MessageType.TX,
            MessageField.DATA: tx.to_dict()
        })

    def _broadcast_block(self, block):
        self._broadcast({
            MessageField.TYPE: MessageType.BLOCK,
            MessageField.DATA: block.to_dict()
        })

    def add_and_broadcast_tx(self, tx: Transaction) -> bool:
        if self.blockchain.add_transaction(tx):
            self.broadcast_transaction(tx)
            return True
        return False

    def _listen_discovery(self):
        sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        sock.bind(('', self._discovery_port))
        while True:
            data, addr = sock.recvfrom(1024)
            if data == b"DISCOVER":
                response = f"{self._external_ip}:{self._port}"
                sock.sendto(response.encode(), addr)

    def _broadcast_mining(self):
        time.sleep(Constants.TIME_TO_SLEEP)
        if self._is_leader():
            message = {MessageField.TYPE: MessageType.MINING}
            self._broadcast(message)
            if self.role == Role.MINER:
                self.message_queue.put(message)

    def _broadcast_presence(self):
        sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        sock.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)
        while True:
            try:
                sock.sendto(b"DISCOVER", ('<broadcast>', self._discovery_port))
                sock.settimeout(1.0)
                while True:
                    try:
                        data, addr = sock.recvfrom(1024)
                        peer_host, peer_port = data.decode().split(":")
                        if peer_host == self._external_ip and int(peer_port) == self._port:
                            continue
                        peer = (peer_host, int(peer_port))
                        self.peers.add(peer)

                        if len(self.blockchain.chain) == 1:
                            self._broadcast_request_chain()
                    except socket.timeout:
                        break
            except Exception as e:
                print("Error during UDP discovery:", e)
            time.sleep(5)

    def _is_leader(self) -> bool:
        my_id = f"{self._external_ip}:{self._port}"
        peer_ids = [f"{host}:{port}" for (host, port) in self.peers]
        return my_id == min([my_id] + peer_ids)