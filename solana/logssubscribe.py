# Copyright (c) 2025 The Suckless Solana Python developers
# Distributed under the MIT software license, see the accompanying
# file COPYING or https://opensource.org/license/mit/.

from typing import NewType

Mention = NewType("Mention", str)
"""
Type representing an account public key (Base58-encoded string).
"""

Commitment = NewType("Commitment", str)
"""
Type representing the commitment level of a transaction.
"""

Processed = Commitment("processed")
"""
Constant representing the most recent node block (which may be incomplete).
"""

# vim: set ts=4 sw=4 expandtab:

