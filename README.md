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
- **unit_tests.py** — Unit tests for blockchain logic
- **integration_tests.py** — Integration tests for node communication logic
- **pre_research.py** — preparation for research
- **research.py** — master thesis research
- **Dockerfile** — docker build for single node  
- **docker-compose.yml** — multi-node configuration (nodes + miners)  
- **README.md** — project documentation (this file)  


---

## 🧩 Dependencies

Python modules:

```bash
pip install ecdsa
pip install pytest
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

- **6 nodes:** cli_node1, cli_node2, cli_node3, cli_node4, cli_node5, cli_node6

**3. Go into the containers:**

```bash
docker exec -it {container_name} bash
```

For example:

```bash
docker exec -it cli_node1 bash
```

**4. Launch the program:**

Run the program as shown in **Run Modes** section


---

## 🧪 Test Execution 

To launch Unit tests, execute the following command:


```bash
pytest unit_tests.py
```

To launch Integration tests, execute the following command:


```bash
pytest integration_tests.py
```


---

## 📊 Running TPS Research

The research on transactions per second (TPS) is a crucial part of my Master’s Thesis, aimed at comparing two different Bitcoin architectures. This module is designed to measure the TPS of the system.  

The experiment involves 1 miner node and 3 non-miner nodes. First, the miner is initialized and mines 30 blocks with 1001 transactions in each block to prepare the blockchain. After this preparation phase, the 3 non-miner nodes join the network.  

During the experiment, the miner sends 1 BTC to a randomly selected non-miner every 0.01 seconds, continuing this process until 3 new blocks are mined. This setup enables the estimation of the approximate TPS achieved under these conditions.  

In order to launch miner, execute the following command:

```bash
python research.py miner
```

In order to launch non-miner, execute the following command:

```bash
python research.py user {number of user (0/1/2)}
```

For example:

```bash
python research.py user 2
```

To start the research, you need to follow these steps:  

1. Launch preparation research file:
   ```bash
    python pre_research.py
    ```
2. Launch miner node (you should use docker containers)  
3. Launch 3 non-miner nodes (you should use docker containers)  
5. Launch researching in the miner node and wait the results  
6. When the research is complete, you will see the following results: amount of added transactions, time spent and tps


---

## 📄 License

Licensed under MIT. See [LICENSE](./LICENSE) file for full terms.


---

## 🤝 Author

Kirill Chuvyzgalov — Developed as a Master's research project in Constructor University Bremen.
