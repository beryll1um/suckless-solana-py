# Copyright (c) 2025 The Suckless Solana Python developers
# Distributed under the MIT software license, see the accompanying
# file COPYING or https://opensource.org/license/mit/.

import pydantic

from . import transaction
from enum import StrEnum


class Encoding(StrEnum):
    """
    Type representing the encoding for a returned block.
    """
    JSON = "json"
    JSON_PARSED = "jsonParsed"
    BASE64 = "base64"
    BASE58 = "base58"


class Commitment(StrEnum):
    """
    Type representing the commitment level of the block.
    """
    FINALIZED = "finalized"
    CONFIRMED = "confirmed"
    PROCESSED = "processed"


class Details(StrEnum):
    """
    Type representing the level of transaction detail to return.
    """
    FULL = "full"
    ACCOUNTS = "accounts"
    SIGNATURES = "signatures"
    NONE = "none"


class Object(pydantic.BaseModel):
    """
    Result object returned by RPC getBlock (full block including transactions).
    """
    # Block height (u64).
    blockHeight: int = pydantic.Field(
        description="Height of the block"
    )

    # Estimated production time (Unix timestamp).
    blockTime: int = pydantic.Field(
        description="Block production time (Unix timestamp)"
    )

    # Hash of this block (base-58).
    blockhash: str = pydantic.Field(
        description="Hash of this block"
    )

    # Parent slot of this block.
    parentSlot: int = pydantic.Field(
        description="Parent slot number"
    )

    # Hash of the previous block.
    previousBlockhash: str = pydantic.Field(
        description="Hash of the previous block"
    )

    # List of transactions with metadata.
    transactions: list[transaction.ObjectWithMeta] = pydantic.Field(
        description="Transactions in this block (with metadata)"
    )

# vim: set ts=4 sw=4 expandtab:

