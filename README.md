# 🧱 Bitcoin‑Py (Python Bitcoin Simulator)

Simulation of a simplified Bitcoin-like network implemented in Python using UTXO model, P2P messaging, mining, and consensus mechanisms.

---

## 🚀 Features

- **Decentralized P2P network** — no central server; peer discovery via UDP
- **UTXO model** — transaction inputs/outputs with double-spend prevention
- **Mining mode** — proof-of-work mining
- **Block voting consensus** — majority selection on forks
- **Wallet & key generation** — ECDSA-based address creation
- **CLI interface** — balance query, transaction sending, blockchain viewing
- **Dockerized multi-node setup** — launching several nodes and miners

---

## 📋 Repository Structure

- **blockchain.py** — blockchain and UTXO set logic  
- **constants.py** — constants for describing messages between nodes  
- **deserialize_service.py** — functions for deserialization  
- **transaction.py** — transactions, inputs/outputs, and signatures 
- **wallet.py** — key generation and address handling  
- **node.py** — P2P networking, message handling, synchronization  
- **main.py** — CLI entry point (node or miner mode)  
- **Dockerfile** — docker build for single node  
- **docker-compose.yml** — multi-node configuration (nodes + miners)  
- **README.md** — project documentation (this file)  


---

## 🧩 Dependencies

Python modules:

```bash
pip install ecdsa
```


---

## 🚀 Run Modes

**1. Node mode (non-miner):**

```bash
python main.py
```

**2. Miner mode:**

```bash
python main.py miner
```


---

## 🐳 Docker Setup

If you want to test the program in Docker, follow these instructions:  

**1. Build images:**

```bash
docker-compose build
```

**2. Launch containers:**

```bash
docker-compose up
```

By default, this starts:

- **2 regular nodes:** cli_node1, cli_node2  
- **2 miner:** cli_miner1, cli_miner2  

**3. Go into the containers:**

```bash
docker exec -it {container_name} bash
```

For example:

```bash
docker exec -it cli_miner1 bash
```

**4. Launch the program:**

Run the program as shown in **Run Modes** section


---

## 📄 License

Licensed under MIT. See [LICENSE](./LICENSE) file for full terms.


---

## 🤝 Author

Kirill Chuvyzgalov — Developed as a Master's research project in Constructor University Bremen.
