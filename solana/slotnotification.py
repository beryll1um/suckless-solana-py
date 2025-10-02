# Copyright (c) 2025 The Suckless Solana Python developers
# Distributed under the MIT software license, see the accompanying
# file COPYING or https://opensource.org/license/mit/.

import pydantic


class Result(pydantic.BaseModel):
    """
    Represents the result of the `logSubscribe` RPC method.
    """
    # Parent slot of the current slot.
    parent: int = pydantic.Field(
        description="Parent slot of the current slot"
    )

    # Root slot observed by the node.
    root: int = pydantic.Field(
        description="Root slot observed by the node"
    )

    # Current slot number.
    slot: int = pydantic.Field(
        description="Current slot number"
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

