# Copyright (c) 2025 The Suckless Solana Python developers
# Distributed under the MIT software license, see the accompanying
# file COPYING or https://opensource.org/license/mit/.

from pydantic import BaseModel as PydanticBaseModel, Field


class Context(PydanticBaseModel):
    """
    Represents the context of the `logSubscribe` RPC method result.
    """
    # Slot number from the "logsNotification" result context.
    slot: int | None = Field(
        default=None,
        description="Optional slot number in the context"
    )


class Value(PydanticBaseModel):
    """
    Represents the value of the `logSubscribe` RPC method result.
    """
    # Transaction signature from the "logsNotification" result value.
    signature: str = Field(
        description="Transaction signature as a string"
    )

    # Optional error details from the "logsNotification" result value.
    err: dict | None = Field(
        default=None,
        description="Optional error details if present"
    )

    # Log messages from the "logsNotification" result value.
    logs: tuple[str, ...] | None = Field(
        default=None,
        description="Optional tuple of log message strings"
    )


class Result(PydanticBaseModel):
    """
    Represents the result of the `logSubscribe` RPC method.
    """
    # Context of the "logsNotification" result.
    context: Context = Field(
        description="Context object of the log subscription"
    )

    # Value of the "logsNotification" result.
    value: Value = Field(
        description="Value object of the log subscription"
    )


class Params(PydanticBaseModel):
    """
    Represents the parameters of the `logSubscribe` RPC method.
    """
    # Result object of the "logsNotification" parameters.
    result: Result = Field(
        description="Result object of the 'logsNotification' parameters"
    )

    # Identifier used to track messages or unsubscribe.
    subscription: int = Field(
        description="Subscription identifier used for tracking "
                    "and unsubscribing"
    )

# vim: set ts=4 sw=4 expandtab:

