# Copyright (c) 2025 The Suckless Solana Python developers
# Distributed under the MIT software license, see the accompanying
# file COPYING or https://opensource.org/license/mit/.

import pydantic

from typing import Any
from enum import StrEnum

from . import transaction


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


class Base(pydantic.BaseModel):
    """
    The result of a `getBlock` RPC request.
    This shape is a superset that accommodates different `transactionDetails`
    and `encoding` options.
    """
    # Current blockhash.
    blockhash: str = pydantic.Field(
        description="Blockhash of this block"
    )

    # Previous blockhash.
    previousBlockhash: str = pydantic.Field(
        description="Blockhash of the previous block"
    )

    # Slot in which the block was produced.
    parentSlot: int = pydantic.Field(
        description="Parent slot of this block"
    )

    # Optional block height (may be null on some clusters).
    blockHeight: int | None = pydantic.Field(
        default=None,
        description="Block height, if available"
    )

    # Estimated Unix timestamp for the block (or null).
    blockTime: int | None = pydantic.Field(
        default=None,
        description="Estimated Unix timestamp (or null)"
    )

    # Rewards earned in this block.
    rewards: list[transaction.Reward] | None = pydantic.Field(
        default=None,
        description="Validator and fee rewards for this block (or null)"
    )

    # If `transactionDetails="signatures"`, only transaction signatures
    # are returned.
    signatures: list[str] | None = pydantic.Field(
        default=None,
        description="Signatures when transactionDetails='signatures'"
    )


class Json(Base):
    """
    Wrapper combining a `json`-encoded transaction with its execution metadata.
    """
    # If `transactionDetails` is 'none', 'full' or 'accounts', transactions
    # are returned. We provide union slots for either JSON or JSON_PARSED
    # encodings.
    transactions: list[transaction.Json] | None = pydantic.Field(
        default=None,
        description="Transactions in this block, shape depends on `encoding` "
                    "and `transactionDetails`"
    )


class JsonParsed(Base):
    """
    Wrapper combining a `jsonParsed`-encoded transaction with its
    execution metadata.
    """
    # If `transactionDetails` is 'none', 'full' or 'accounts', transactions
    # are returned. We provide union slots for either JSON or JSON_PARSED
    # encodings.
    transactions: list[transaction.JsonParsed] | None = pydantic.Field(
        default=None,
        description="Transactions in this block, shape depends on `encoding` "
                    "and `transactionDetails`"
    )

# vim: set ts=4 sw=4 expandtab:

