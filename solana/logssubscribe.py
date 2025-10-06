# Copyright (c) 2025 The Suckless Solana Python developers
# Distributed under the MIT software license, see the accompanying
# file COPYING or https://opensource.org/license/mit/.

from enum import StrEnum
from typing import NewType


class Filter(StrEnum):
    """
    Type representing criteria for the logs to receive results.
    """
    ALL = "all"
    ALL_WITH_VOTES = "allWithVotes"


Mention = NewType("Mention", str)
"""
Type representing an account public key (Base58-encoded string).
"""

# vim: set ts=4 sw=4 expandtab:

