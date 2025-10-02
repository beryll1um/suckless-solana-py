# Copyright (c) 2025 The Suckless Solana Python developers
# Distributed under the MIT software license, see the accompanying
# file COPYING or https://opensource.org/license/mit/.

import pydantic
from typing import Any


class Value(pydantic.BaseModel):
    """
    Represents the value of the `blockSubscribe` RPC method result.
    """
    # Slot number at which this block was produced.
    slot: int = pydantic.Field(
        description="Slot number at which this block was produced"
    )

    # Block object containing transactions and metadata, but I'm not sure
    # about type as it floating currently.
    block: dict[str, Any] | None = pydantic.Field(
        default=None,
        description="Block object containing transactions and metadata"
    )

    # Optional error details if the block is invalid.
    err: dict | None = pydantic.Field(
        default=None,
        description="Optional error details if the block is invalid"
    )


class Context(pydantic.BaseModel):
    """
    Represents the context of the `blockSubscribe` RPC method result.
    """
    # Slot number from the "blockNotification" result context.
    slot: int | None = pydantic.Field(
        default=None,
        description="Optional slot number in the context"
    )


class Result(pydantic.BaseModel):
    """
    Represents the result of the `blockSubscribe` RPC method.
    """
    # Context of the "blockNotification" result.
    context: Context = pydantic.Field(
        description="Context object of the block subscription"
    )

    # Value of the "blockNotification" result.
    value: Value = pydantic.Field(
        description="Value object of the block subscription"
    )


class Params(pydantic.BaseModel):
    """
    Represents the parameters of the `blockSubscribe` RPC method.
    """
    # Result object of the "blockNotification" parameters.
    result: Result = pydantic.Field(
        description="Result object of the 'blockNotification' parameters"
    )

    # Identifier used to track messages or unsubscribe.
    subscription: int = pydantic.Field(
        description="Subscription identifier used for tracking "
                    "and unsubscribing"
    )

# vim: set ts=4 sw=4 expandtab:

