# Copyright (c) 2025 The Suckless Solana Python developers
# Distributed under the MIT software license, see the accompanying
# file COPYING or https://opensource.org/license/mit/.

from typing import NewType

Encoding = NewType("Encoding", str)
"""
Type representing the encoding for a returned transaction.
"""

JSON = Encoding("json")
"""
Constant representing default parse mode for the transaction request.
"""

Commitment = NewType("Commitment", str)
"""
Type representing the commitment level of the transaction.
"""

Finalized = Commitment("finalized")
"""
Constant representing the most recent block confirmed
by supermajority of the cluster as having reached maximum lockout,
meaning the cluster has recognized this block as finalized.
"""

Confirmed = Commitment("confirmed")
"""
Constant representing the most recent block that has been voted on
by supermajority of the cluster.
"""

Processed = Commitment("processed")
"""
Constant representing the most recent block (which may be incomplete).
"""
# vim: set ts=4 sw=4 expandtab:

