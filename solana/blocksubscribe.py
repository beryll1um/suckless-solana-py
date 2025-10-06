# Copyright (c) 2025 The Suckless Solana Python developers
# Distributed under the MIT software license, see the accompanying
# file COPYING or https://opensource.org/license/mit/.

from typing import NewType
from enum import StrEnum


class Filter(StrEnum):
    """
    Type representing criteria for the logs to receive results.
    """
    ALL = "all"


Mention = NewType("Mention", str)
"""
Type representing an account public key (Base58-encoded string).
"""

# vim: set ts=4 sw=4 expandtab:

