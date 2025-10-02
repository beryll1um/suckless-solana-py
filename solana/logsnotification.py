# Copyright (c) 2025 The Suckless Solana Python developers
# Distributed under the MIT software license, see the accompanying
# file COPYING or https://opensource.org/license/mit/.

import pydantic


class Context(pydantic.BaseModel):
    """
    Represents the context of the `logSubscribe` RPC method result.
    """
    # Slot number from the "logsNotification" result context.
    slot: int | None = pydantic.Field(
        default=None,
        description="Optional slot number in the context"
    )


class Value(pydantic.BaseModel):
    """
    Represents the value of the `logSubscribe` RPC method result.
    """
    # Transaction signature from the "logsNotification" result value.
    signature: str = pydantic.Field(
        description="Transaction signature as a string"
    )

    # Optional error details from the "logsNotification" result value.
    err: dict | None = pydantic.Field(
        default=None,
        description="Optional error details if present"
    )

    # Log messages from the "logsNotification" result value.
    logs: tuple[str, ...] | None = pydantic.Field(
        default=None,
        description="Optional tuple of log message strings"
    )


class Result(pydantic.BaseModel):
    """
    Represents the result of the `logSubscribe` RPC method.
    """
    # Context of the "logsNotification" result.
    context: Context = pydantic.Field(
        description="Context object of the log subscription"
    )

    # Value of the "logsNotification" result.
    value: Value = pydantic.Field(
        description="Value object of the log subscription"
    )


class Params(pydantic.BaseModel):
    """
    Represents the parameters of the `logSubscribe` RPC method.
    """
    # Result object of the "logsNotification" parameters.
    result: Result = pydantic.Field(
        description="Result object of the 'logsNotification' parameters"
    )

    # Identifier used to track messages or unsubscribe.
    subscription: int = pydantic.Field(
        description="Subscription identifier used for tracking "
                    "and unsubscribing"
    )

# vim: set ts=4 sw=4 expandtab:

