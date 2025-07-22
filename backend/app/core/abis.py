ERC20_ABI = [
    # balanceOf(address account)
    {
        "name": "balanceOf",
        "type": "function",
        "stateMutability": "view",
        "inputs": [
            {"name": "account", "type": "address"}
        ],
        "outputs": [
            {"name": "", "type": "uint256"}
        ]
    },

    # transfer(address to, uint256 amount)
    {
        "name": "transfer",
        "type": "function",
        "stateMutability": "nonpayable",
        "inputs": [
            {"name": "to", "type": "address"},
            {"name": "amount", "type": "uint256"}
        ],
        "outputs": [
            {"name": "", "type": "bool"}
        ]
    },

    # Transfer event
    {
        "anonymous": False,
        "type": "event",
        "name": "Transfer",
        "inputs": [
            {"indexed": True, "name": "from", "type": "address"},
            {"indexed": True, "name": "to", "type": "address"},
            {"indexed": False, "name": "value", "type": "uint256"}
        ]
    }
]