# Copyright (c) 2025 The Suckless Solana Python developers
# Distributed under the MIT software license, see the accompanying
# file COPYING or https://opensource.org/license/mit/.

from typing import NewType

Filter = NewType("Filter", str)
"""
Type representing criteria for the logs to receive results.
"""

All = Filter("all")
"""
Constant representing subscription to all transactions in block.
"""

Mention = NewType("Mention", str)
"""
Type representing an account public key (Base58-encoded string).
"""

# vim: set ts=4 sw=4 expandtab:

