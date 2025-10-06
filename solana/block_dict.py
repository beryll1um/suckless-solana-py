# Copyright (c) 2025 The Suckless Solana Python developers
# Distributed under the MIT software license, see the accompanying
# file COPYING or https://opensource.org/license/mit/.

from typing import NotRequired, TypedDict

from . import transaction_dict


class Base(TypedDict, total=True):
    """
    The result of a `getBlock` RPC request.
    This shape is a superset that accommodates different `transactionDetails`
    and `encoding` options.
    """
    # Current blockhash.
    blockhash: str

    # Previous blockhash.
    previousBlockhash: str

    # Slot in which the block was produced.
    parentSlot: int

    # Optional block height (may be null on some clusters).
    blockHeight: int | None

    # Estimated Unix timestamp for the block (or null).
    blockTime: int | None

    # Rewards earned in this block.
    rewards: NotRequired[list[transaction_dict.Reward] | None]

    # If `transactionDetails="signatures"`, only transaction signatures
    # are returned.
    signatures: NotRequired[list[str]]


class Json(Base):
    """
    Wrapper combining a `json`-encoded transaction with its execution metadata.
    """
    # If `transactionDetails` is 'none', 'full' or 'accounts', transactions
    # are returned. We provide union slots for either JSON or JSON_PARSED
    # encodings.
    transactions: list[transaction_dict.Json]


class JsonParsed(Base):
    """
    Wrapper combining a `jsonParsed`-encoded transaction with its
    execution metadata.
    """
    # If `transactionDetails` is 'none', 'full' or 'accounts', transactions
    # are returned. We provide union slots for either JSON or JSON_PARSED
    # encodings.
    transactions: list[transaction_dict.JsonParsed]

# vim: set ts=4 sw=4 expandtab:

