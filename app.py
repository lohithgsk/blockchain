import hashlib
import json
import time
from urllib.parse import urlparse
from uuid import uuid4
import requests
from flask import Flask, jsonify, request, render_template, redirect, url_for, flash
import sys
import os


class Transaction:
    """Represents a blockchain transaction"""
    
    def __init__(self, sender, recipient, amount, timestamp=None):
        self.sender = sender
        self.recipient = recipient
        self.amount = amount
        self.timestamp = timestamp or time.time()
    
    def to_dict(self):
        """Convert transaction to dictionary"""
        return {
            'sender': self.sender,
            'recipient': self.recipient,
            'amount': self.amount,
            'timestamp': self.timestamp
        }
    
    def __str__(self):
        return f"{self.sender} -> {self.recipient}: {self.amount}"


class Block:
    """Represents a blockchain block"""
    
    def __init__(self, index, transactions, timestamp, previous_hash, nonce=0):
        self.index = index
        self.transactions = transactions
        self.timestamp = timestamp
        self.previous_hash = previous_hash
        self.nonce = nonce
        self._hash = None
    
    def calculate_hash(self):
        """Calculate the hash of the block"""
        block_string = json.dumps({
            'index': self.index,
            'transactions': [tx.to_dict() if isinstance(tx, Transaction) else tx for tx in self.transactions],
            'timestamp': self.timestamp,
            'previous_hash': self.previous_hash,
            'nonce': self.nonce
        }, sort_keys=True)
        return hashlib.sha256(block_string.encode()).hexdigest()
    
    @property
    def hash(self):
        """Get the hash of the block"""
        if self._hash is None:
            self._hash = self.calculate_hash()
        return self._hash
    
    def to_dict(self):
        """Convert block to dictionary"""
        return {
            'index': self.index,
            'transactions': [tx.to_dict() if isinstance(tx, Transaction) else tx for tx in self.transactions],
            'timestamp': self.timestamp,
            'previous_hash': self.previous_hash,
            'nonce': self.nonce,
            'hash': self.hash
        }


class Blockchain:
    """Main blockchain class"""
    
    def __init__(self):
        self.chain = []
        self.current_transactions = []
        self.difficulty = 4  # Mining difficulty
        self.mining_reward = 10
        self.nodes = set()
        
        # Create genesis block
        self.create_genesis_block()
    
    def create_genesis_block(self):
        """Create the first block in the chain"""
        genesis_block = Block(0, [], time.time(), "0")
        genesis_block._hash = genesis_block.calculate_hash()
        self.chain.append(genesis_block)
    
    def get_latest_block(self):
        """Get the last block in the chain"""
        return self.chain[-1]
    
    def add_transaction(self, sender, recipient, amount):
        """Add a new transaction to the pending transactions"""
        transaction = Transaction(sender, recipient, amount)
        self.current_transactions.append(transaction)
        return self.get_latest_block().index + 1
    
    def mine_pending_transactions(self, mining_reward_address):
        """Mine a new block with pending transactions"""
        # Add mining reward transaction
        reward_transaction = Transaction(None, mining_reward_address, self.mining_reward)
        self.current_transactions.append(reward_transaction)
        
        # Create new block
        block = Block(
            index=len(self.chain),
            transactions=self.current_transactions,
            timestamp=time.time(),
            previous_hash=self.get_latest_block().hash
        )
        
        # Mine the block (Proof of Work)
        self.mine_block(block)
        
        # Add block to chain and reset pending transactions
        self.chain.append(block)
        self.current_transactions = []
        
        return block
    
    def mine_block(self, block):
        """Mine a block using Proof of Work"""
        target = "0" * self.difficulty
        
        print(f"Mining block {block.index}...")
        start_time = time.time()
        
        while block.hash[:self.difficulty] != target:
            block.nonce += 1
            block._hash = None  # Reset hash to recalculate
        
        end_time = time.time()
        print(f"Block {block.index} mined in {end_time - start_time:.2f} seconds with nonce {block.nonce}")
        print(f"Block hash: {block.hash}")
    
    def is_chain_valid(self, chain=None):
        """Validate the blockchain"""
        if chain is None:
            chain = self.chain
        
        for i in range(1, len(chain)):
            current_block = chain[i]
            previous_block = chain[i-1]
            
            # Check if current block hash is valid
            if current_block.hash != current_block.calculate_hash():
                return False
            
            # Check if previous hash matches
            if current_block.previous_hash != previous_block.hash:
                return False
            
            # Check proof of work
            if current_block.hash[:self.difficulty] != "0" * self.difficulty:
                return False
        
        return True
    
    def get_balance(self, address):
        """Get balance for a specific address"""
        balance = 0
        
        for block in self.chain:
            for transaction in block.transactions:
                if isinstance(transaction, dict):
                    if transaction['sender'] == address:
                        balance -= transaction['amount']
                    if transaction['recipient'] == address:
                        balance += transaction['amount']
                else:
                    if transaction.sender == address:
                        balance -= transaction.amount
                    if transaction.recipient == address:
                        balance += transaction.amount
        
        return balance
    
    def register_node(self, address):
        """Register a new node in the network"""
        parsed_url = urlparse(address)
        if parsed_url.netloc:
            self.nodes.add(parsed_url.netloc)
        elif parsed_url.path:
            self.nodes.add(parsed_url.path)
        else:
            raise ValueError('Invalid URL')
    
    def resolve_conflicts(self):
        """Consensus algorithm: replace chain with longest valid chain in network"""
        neighbours = self.nodes
        new_chain = None
        max_length = len(self.chain)
        
        for node in neighbours:
            try:
                response = requests.get(f'http://{node}/api/chain', timeout=5)
                
                if response.status_code == 200:
                    data = response.json()
                    length = data['length']
                    chain = data['chain']
                    
                    # Convert chain data back to Block objects for validation
                    chain_objects = []
                    for block_data in chain:
                        block = Block(
                            block_data['index'],
                            block_data['transactions'],
                            block_data['timestamp'],
                            block_data['previous_hash'],
                            block_data['nonce']
                        )
                        block._hash = block_data['hash']
                        chain_objects.append(block)
                    
                    if length > max_length and self.is_chain_valid(chain_objects):
                        max_length = length
                        new_chain = chain_objects
            except requests.RequestException:
                continue
        
        if new_chain:
            self.chain = new_chain
            return True
        
        return False


# Initialize Flask app
app = Flask(__name__)
app.secret_key = 'blockchain_secret_key_change_in_production'

# Generate a globally unique address for this node
node_identifier = str(uuid4()).replace('-', '')

# Instantiate the Blockchain
blockchain = Blockchain()


# =============================================================================
# WEB ROUTES (Frontend Pages)
# =============================================================================

@app.route('/')
def index():
    """Main dashboard page"""
    return render_template('index.html',
                         node_id=node_identifier[:8],
                         chain_length=len(blockchain.chain),
                         peer_count=len(blockchain.nodes),
                         pending_count=len(blockchain.current_transactions),
                         balance=blockchain.get_balance(node_identifier),
                         mining_reward=blockchain.mining_reward,
                         difficulty=blockchain.difficulty)

@app.route('/transactions')
def transactions_page():
    """Transactions management page"""
    return render_template('transactions.html',
                         pending_transactions=blockchain.current_transactions,
                         node_id=node_identifier[:8])

@app.route('/mining')
def mining_page():
    """Mining center page"""
    return render_template('mining.html',
                         node_id=node_identifier[:8],
                         mining_reward=blockchain.mining_reward,
                         difficulty=blockchain.difficulty,
                         pending_count=len(blockchain.current_transactions))

@app.route('/network')
def network_page():
    """Network management page"""
    return render_template('network.html',
                         node_id=node_identifier[:8],
                         peers=list(blockchain.nodes),
                         peer_count=len(blockchain.nodes))

@app.route('/explorer')
def explorer_page():
    """Blockchain explorer page"""
    return render_template('explorer.html',
                         chain=list(reversed(blockchain.chain)),
                         chain_length=len(blockchain.chain),
                         node_id=node_identifier[:8])

@app.route('/balance')
def balance_page():
    """Balance checker page"""
    return render_template('balance.html',
                         node_id=node_identifier[:8],
                         node_balance=blockchain.get_balance(node_identifier))


# =============================================================================
# API ROUTES (Backend Endpoints)
# =============================================================================

@app.route('/api/stats')
def api_stats():
    """Get blockchain statistics"""
    return jsonify({
        'chain_length': len(blockchain.chain),
        'pending_count': len(blockchain.current_transactions),
        'peer_count': len(blockchain.nodes),
        'balance': blockchain.get_balance(node_identifier),
        'difficulty': blockchain.difficulty,
        'mining_reward': blockchain.mining_reward,
        'node_id': node_identifier,
        'is_valid': blockchain.is_chain_valid()
    })

@app.route('/api/chain')
def api_chain():
    """Get the full blockchain"""
    response = {
        'chain': [block.to_dict() for block in blockchain.chain],
        'length': len(blockchain.chain),
    }
    return jsonify(response)

@app.route('/api/transactions', methods=['GET', 'POST'])
def api_transactions():
    """Handle transactions"""
    if request.method == 'GET':
        return jsonify({
            'pending_transactions': [tx.to_dict() for tx in blockchain.current_transactions],
            'count': len(blockchain.current_transactions)
        })
    
    elif request.method == 'POST':
        values = request.get_json()
        
        # Check required fields
        required = ['sender', 'recipient', 'amount']
        if not all(k in values for k in required):
            return jsonify({'error': 'Missing required fields'}), 400
        
        sender = values['sender']
        recipient = values['recipient']
        amount = float(values['amount'])
        
        # Validate transaction
        if amount <= 0:
            return jsonify({'error': 'Amount must be positive'}), 400
        
        if sender == recipient:
            return jsonify({'error': 'Sender and recipient cannot be the same'}), 400
        
        if sender != 'Mining Reward' and blockchain.get_balance(sender) < amount:
            return jsonify({'error': f'Insufficient balance. Available: {blockchain.get_balance(sender)}'}), 400
        
        # Create transaction
        index = blockchain.add_transaction(sender, recipient, amount)
        
        response = {
            'message': f'Transaction will be added to Block {index}',
            'transaction': {
                'sender': sender,
                'recipient': recipient,
                'amount': amount
            }
        }
        return jsonify(response), 201

@app.route('/api/mine', methods=['POST'])
def api_mine():
    """Mine a new block"""
    if not blockchain.current_transactions:
        return jsonify({'error': 'No transactions to mine'}), 400
    
    # Mine the block
    start_time = time.time()
    block = blockchain.mine_pending_transactions(node_identifier)
    end_time = time.time()
    
    response = {
        'message': 'New Block Forged',
        'index': block.index,
        'transactions': [tx.to_dict() for tx in block.transactions],
        'nonce': block.nonce,
        'previous_hash': block.previous_hash,
        'hash': block.hash,
        'mining_time': round(end_time - start_time, 2)
    }
    return jsonify(response), 200

@app.route('/api/nodes', methods=['GET', 'POST'])
def api_nodes():
    """Handle node management"""
    if request.method == 'GET':
        return jsonify({
            'nodes': list(blockchain.nodes),
            'count': len(blockchain.nodes)
        })
    
    elif request.method == 'POST':
        values = request.get_json()
        nodes = values.get('nodes')
        
        if nodes is None:
            return jsonify({'error': 'Please supply a valid list of nodes'}), 400
        
        successful_nodes = []
        failed_nodes = []
        
        for node in nodes:
            try:
                # Test connection to the node
                test_response = requests.get(f"{node}/api/chain", timeout=5)
                if test_response.status_code == 200:
                    blockchain.register_node(node)
                    successful_nodes.append(node)
                else:
                    failed_nodes.append(node)
            except requests.RequestException:
                failed_nodes.append(node)
        
        response = {
            'message': 'Registration complete',
            'successful_nodes': successful_nodes,
            'failed_nodes': failed_nodes,
            'total_nodes': list(blockchain.nodes),
        }
        return jsonify(response), 201

@app.route('/api/consensus', methods=['POST'])
def api_consensus():
    """Resolve conflicts using consensus algorithm"""
    initial_length = len(blockchain.chain)
    replaced = blockchain.resolve_conflicts()
    final_length = len(blockchain.chain)
    
    if replaced:
        response = {
            'message': f'Chain was replaced! Length changed from {initial_length} to {final_length}',
            'replaced': True,
            'new_length': final_length,
            'blocks_added': final_length - initial_length
        }
    else:
        response = {
            'message': 'Our chain is authoritative',
            'replaced': False,
            'current_length': final_length,
            'peers_checked': len(blockchain.nodes)
        }
    
    return jsonify(response), 200

@app.route('/api/balance/<address>')
def api_balance(address):
    """Get balance for a specific address"""
    balance = blockchain.get_balance(address)
    return jsonify({
        'address': address,
        'balance': balance
    })

@app.route('/api/health')
def api_health():
    """Get node health information"""
    health_info = {
        'node_id': node_identifier,
        'status': 'online',
        'chain_length': len(blockchain.chain),
        'pending_transactions': len(blockchain.current_transactions),
        'connected_peers': len(blockchain.nodes),
        'last_block_hash': blockchain.get_latest_block().hash,
        'difficulty': blockchain.difficulty,
        'is_chain_valid': blockchain.is_chain_valid()
    }
    
    # Test peer connectivity
    peer_status = {}
    for peer in blockchain.nodes:
        try:
            response = requests.get(f"http://{peer}/api/chain", timeout=2)
            peer_status[peer] = 'online' if response.status_code == 200 else 'error'
        except requests.RequestException:
            peer_status[peer] = 'offline'
    
    health_info['peer_status'] = peer_status
    return jsonify(health_info)


# =============================================================================
# FORM HANDLING ROUTES (Bridge between frontend forms and API)
# =============================================================================

@app.route('/create_transaction', methods=['POST'])
def create_transaction():
    """Handle transaction creation from form"""
    sender = request.form.get('sender')
    recipient = request.form.get('recipient')
    amount = request.form.get('amount')
    
    try:
        amount = float(amount)
        
        # Validate
        if amount <= 0:
            flash('Amount must be positive', 'error')
            return redirect(url_for('transactions_page'))
        
        if sender == recipient:
            flash('Sender and recipient cannot be the same', 'error')
            return redirect(url_for('transactions_page'))
        
        if sender != 'Mining Reward' and blockchain.get_balance(sender) < amount:
            flash(f'Insufficient balance. Available: {blockchain.get_balance(sender)}', 'error')
            return redirect(url_for('transactions_page'))
        
        # Create transaction
        blockchain.add_transaction(sender, recipient, amount)
        flash(f'Transaction created: {sender} → {recipient} ({amount} coins)', 'success')
        
    except ValueError:
        flash('Invalid amount', 'error')
    
    return redirect(url_for('transactions_page'))

@app.route('/mine_block', methods=['POST'])
def mine_block():
    """Handle block mining from form"""
    if not blockchain.current_transactions:
        flash('No transactions to mine', 'error')
        return redirect(url_for('mining_page'))
    
    try:
        block = blockchain.mine_pending_transactions(node_identifier)
        flash(f'Block #{block.index} mined successfully! Nonce: {block.nonce}', 'success')
    except Exception as e:
        flash(f'Mining failed: {str(e)}', 'error')
    
    return redirect(url_for('mining_page'))

@app.route('/add_peer', methods=['POST'])
def add_peer():
    """Handle peer addition from form"""
    peer_url = request.form.get('peer_url')
    
    if not peer_url:
        flash('Please provide a peer URL', 'error')
        return redirect(url_for('network_page'))
    
    try:
        # Test connection
        test_response = requests.get(f"{peer_url}/api/chain", timeout=5)
        if test_response.status_code == 200:
            blockchain.register_node(peer_url)
            flash(f'Peer added successfully: {peer_url}', 'success')
        else:
            flash(f'Failed to connect to peer: {peer_url}', 'error')
    except requests.RequestException:
        flash(f'Cannot reach peer: {peer_url}', 'error')
    
    return redirect(url_for('network_page'))

@app.route('/sync_network', methods=['POST'])
def sync_network():
    """Handle network synchronization from form"""
    try:
        initial_length = len(blockchain.chain)
        replaced = blockchain.resolve_conflicts()
        final_length = len(blockchain.chain)
        
        if replaced:
            flash(f'Chain synchronized! Length: {initial_length} → {final_length}', 'success')
        else:
            flash('Network is already synchronized', 'info')
    except Exception as e:
        flash(f'Synchronization failed: {str(e)}', 'error')
    
    return redirect(url_for('network_page'))

@app.route('/check_balance', methods=['POST'])
def check_balance():
    """Handle balance check from form"""
    address = request.form.get('address')
    
    if not address:
        flash('Please provide an address', 'error')
        return redirect(url_for('balance_page'))
    
    balance = blockchain.get_balance(address)
    flash(f'Balance for {address}: {balance} coins', 'info')
    
    return redirect(url_for('balance_page'))


if __name__ == '__main__':
    from argparse import ArgumentParser
    
    parser = ArgumentParser()
    parser.add_argument('-p', '--port', default=5000, type=int, help='port to listen on')
    parser.add_argument('--host', default='0.0.0.0', help='host to bind to')
    parser.add_argument('--debug', action='store_true', help='enable debug mode')
    args = parser.parse_args()
    
    port = args.port
    host = args.host
    debug = args.debug
    
    print("🔗" * 30)
    print(f"🚀 P2P Blockchain Network Starting")
    print(f"📡 Node ID: {node_identifier}")
    print(f"🌐 Server: http://{host}:{port}/")
    print(f"📊 API Base: http://{host}:{port}/api/")
    print(f"🔧 Debug Mode: {'ON' if debug else 'OFF'}")
    print("🔗" * 30)
    
    try:
        app.run(host=host, port=port, debug=debug)
    except KeyboardInterrupt:
        print("\n\n👋 Blockchain node shutting down gracefully...")
    except Exception as e:
        print(f"\n❌ Error starting blockchain node: {e}")
        sys.exit(1)
