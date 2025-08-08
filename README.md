# P2P Blockchain Network

*Peer-to-Peer Blockchain Network Implementation*

## Overview

## Features

<table>
<tr>
<td width="50%">

### Core Blockchain Features
- **Complete Blockchain Implementation**
  - Transaction validation and processing
  - Block creation and linking
  - Hash integrity verification
  
- **Proof-of-Work Mining**
  - Configurable difficulty levels
  - Nonce-based hash puzzles
  - Mining reward system
  
- **Peer-to-Peer Network**
  - Node discovery and registration
  - Automatic synchronization
  - Consensus algorithm (longest chain)

</td>
<td width="50%">

### Web Interface Features
- **Interactive Dashboard**
  - Real-time statistics and monitoring
  - Network status indicators
  - Quick action buttons
  
- **Transaction Management**
  - Easy transaction creation
  - Pending transaction pool
  - Balance validation
  
- **Blockchain Explorer**
  - Search by block, hash, or address
  - Detailed transaction history
  - Visual block representation

</td>
</tr>
</table>

---

## Output Screenshots

![HomePage](https://github.com/lohithgsk/blockchain/blob/main/images/Image%200.png)

<br>

![HomePage+1](https://github.com/lohithgsk/blockchain/blob/main/images/quick.png)

<br>

![Mining](https://github.com/lohithgsk/blockchain/blob/main/images/Image%202.png)

<br>

![Network](https://github.com/lohithgsk/blockchain/blob/main/images/Image%203.png)

<br>

![Network](https://github.com/lohithgsk/blockchain/blob/main/images/Image%204.png)

<br>

## Quick Start

### Installation

```bash
# 1. Clone or create the project
mkdir blockchain_app && cd blockchain_app

# 2. Create directory structure
mkdir -p static/css static/js templates

# 3. Install dependencies
pip install flask requests

# 4. Add all project files (provided separately)
# - Copy app.py to root directory
# - Copy templates/*.html to templates/
# - Copy static/css/style.css to static/css/
# - Copy static/js/main.js to static/js/
```

### Launch Your Blockchain Network

<table>
<tr>
<td width="50%">

**Single Node Setup**
```bash
python app.py
```
Access at: http://localhost:5000

</td>
<td width="50%">

**Multi-Node Network**
```bash
# Terminal 1
python app.py -p 5000

# Terminal 2
python app.py -p 5001

# Terminal 3
python app.py -p 5002
```

</td>
</tr>
</table>

### Connect Your Network

1. **Open multiple browser tabs** for each node
2. **Navigate to Network page** on each node
3. **Add peer URLs** (e.g., `http://localhost:5001`)
4. **Watch the magic happen** as nodes synchronize!

---

## Project Architecture

```
blockchain_app/
├── app.py                 
├── requirements.txt       
├── README.md             
├── tatic/
│   ├── css/
│   │   └── style.css        
│   └── js/
│       └── main.js          
└── templates/
    ├── base.html         
    ├── index.html        
    ├── transactions.html 
    ├── mining.html        
    ├── network.html      
    ├── explorer.html     
    └── balance.html      
```

---

## User Interface Tour

### Dashboard - Your Command Center
<details>
<summary>Click to explore the Dashboard features</summary>

- **Real-time Statistics Cards**
  - Current chain length and network status
  - Pending transactions counter
  - Connected peers monitoring
  - Node balance tracking

- **Quick Action Center**
  - One-click transaction creation
  - Instant mining activation
  - Network management shortcuts
  - Blockchain exploration links

- **Network Activity Feed**
  - Live transaction updates
  - Recent block notifications
  - Mining event tracking
  - Peer connection status

</details>

### Transaction 
<details>
<summary>Transaction management capabilities</summary>

- **Smart Transaction Creator**
  - Intuitive form with validation
  - Balance checking before sending
  - Quick-fill templates for testing
  - Real-time error prevention

- **Pending Transaction Pool**
  - Live updates of waiting transactions
  - Visual transaction cards
  - Amount and address display
  - Time stamps and status

- **Transaction Statistics**
  - Total volume calculations
  - Transaction type breakdown
  - Historical data visualization
  - Network throughput metrics

</details>

### Mining Center
<details>
<summary>The mining interface</summary>

- **Interactive Mining Console**
  - One-click mining activation
  - Real-time progress tracking
  - Visual difficulty indicators
  - Reward calculations

- **Mining Statistics Dashboard**
  - Blocks mined counter
  - Total earnings tracker
  - Hash rate estimation
  - Mining history log

- **Advanced Mining Controls**
  - Difficulty visualization
  - Nonce progression display
  - Energy consumption estimates
  - Performance optimization tips

</details>

### Network Manager - Connect & Synchronize
<details>
<summary>Master network management</summary>

- **Peer Connection Interface**
  - Easy peer addition with URL input
  - Auto-discovery for local networks
  - Connection status monitoring
  - Quick-connect templates

- **Synchronization Center**
  - One-click network sync
  - Consensus algorithm execution
  - Conflict resolution tracking
  - Sync performance metrics

- **Network Topology View**
  - Visual network representation
  - Connection quality indicators
  - Peer response time tracking
  - Network health monitoring

</details>

### Blockchain Explorer - Dive Deep
<details>
<summary>Explore the blockchain in detail</summary>

- **Advanced Search Engine**
  - Search by block number, hash, or address
  - Real-time search suggestions
  - Instant result highlighting
  - Search history tracking

- **Detailed Block Viewer**
  - Complete block information display
  - Transaction breakdown and analysis
  - Hash verification tools
  - Timestamp and nonce details

- **Chain Analytics**
  - Total supply calculations
  - Transaction volume metrics
  - Average block time analysis
  - Network growth statistics

</details>

### Balance Checker - Track Wealth
<details>
<summary>Monitor account balances</summary>

- **Comprehensive Balance Display**
  - Current balance with animations
  - Transaction history breakdown
  - Received vs sent analysis
  - Mining rewards tracking

- **Address Analytics**
  - Top addresses leaderboard
  - Wealth distribution charts
  - Address activity tracking
  - Balance change notifications

- **🔧 Balance Tools**
  - Address generator for testing
  - Quick balance lookups
  - Historical balance tracking
  - Export capabilities

</details>

---


## Customization

### Blockchain Parameters
```python
# In app.py - Blockchain class
class Blockchain:
    def __init__(self):
        self.difficulty = 4        # Mining difficulty (leading zeros)
        self.mining_reward = 10    # Coins per block reward
        self.max_transactions = 100 # Max transactions per block
```

---

## API Reference

### Statistics & Health
| Endpoint | Method | Description | Response |
|----------|--------|-------------|----------|
| `/api/stats` | GET | Node statistics | Chain length, peers, balance |
| `/api/health` | GET | Node health check | Status, chain validity, peer info |

### Blockchain Data
| Endpoint | Method | Description | Response |
|----------|--------|-------------|----------|
| `/api/chain` | GET | Full blockchain | Complete chain with all blocks |
| `/api/balance/<address>` | GET | Address balance | Current balance for address |

### Transaction Management
| Endpoint | Method | Description | Body |
|----------|--------|-------------|------|
| `/api/transactions` | GET | Pending transactions | - |
| `/api/transactions` | POST | Create transaction | `{sender, recipient, amount}` |

### Mining Operations
| Endpoint | Method | Description | Response |
|----------|--------|-------------|----------|
| `/api/mine` | POST | Mine new block | Block details with nonce |

### Network Management
| Endpoint | Method | Description | Body |
|----------|--------|-------------|------|
| `/api/nodes` | GET | Connected peers | List of registered nodes |
| `/api/nodes` | POST | Register peers | `{nodes: [urls]}` |
| `/api/consensus` | POST | Sync network | Consensus result |

---


---

