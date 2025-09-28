# Copyright (c) 2025 The Suckless Solana Python developers
# Distributed under the MIT software license, see the accompanying
# file COPYING or https://opensource.org/license/mit/.

from pydantic import BaseModel, Field, model_validator
from typing import Literal, Any


class Base(BaseModel):
    """
    Represents a JSON-RPC 2.0 base object.
    """
    # Specifies the JSON-RPC protocol version, fixed to "2.0".
    jsonrpc: Literal["2.0"] = Field(
        default="2.0",
        description="Version of the JSON-RPC protocol"
    )


class Request(Base):
    """
    Represents a JSON-RPC 2.0 request object.
    """
    # Identifier used to correlate the request with its response.
    id: int | str = Field(
        description="Unique identifier of the request object"
    )

    # Name of the method to be executed on the server.
    method: str = Field(
        description="Name of the method to be invoked"
    )

    # Optional parameters for the method invocation.
    params: dict[str, Any] | list[Any] | None = Field(
        description="Arguments to be passed to the invoked method"
    )


class Error(BaseModel):
    """
    Represents a JSON-RPC 2.0 error object.
    """
    # Numeric code indicating the type of error.
    code: int = Field(
        description="Code indicating the type of error that occurred"
    )

    # Short description of the error (should not exceed one sentence).
    message: str = Field(
        description="Short description of the error"
    )

    # Additional information about the error, if available.
    data: Any | None = Field(
        description="Additional details about the error"
    )


class Response(Base):
    """
    Represents a JSON-RPC 2.0 response object.
    """
    # Identifier matching the associated request.
    id: int | str = Field(
        description="Unique identifier of the corresponding request"
    )

    # Error details if the method execution failed.
    error: Any | None = Field(
        default=None,
        description="Error information if method execution failed"
    )

    # Result data if the method execution succeeded.
    result: Any | None = Field(
        default=None,
        description="Result of the successfully executed method"
    )

    def is_error(self) -> bool:
        """
        Returns `True` if the response contains an error, otherwise `False`.
        """
        return self.result is None

    @model_validator(mode="after")
    def validate_result_or_error(self) -> "Response":
        """
        Ensures that either `result` or `error` is set,
        but not both or neither.
        """
        # If result and error are in the same state
        # (both present or both absent), raise an exception,
        # since exactly one of them must be set.
        if (self.result is None) == (self.error is None):
            raise ValueError(
                "Exactly one of 'result' or 'error' must be provided")
        return self


class Notification(Base):
    """
    Represents a JSON-RPC 2.0 notification object.
    """
    # Name of the method to be executed without expecting a response.
    method: str = Field(
        description="Name of the method to be invoked"
    )

    # Optional parameters for the notification.
    params: dict[str, Any] | list[Any] | None = Field(
        description="Arguments to be passed to the invoked method"
    )

# vim: set ts=4 sw=4 expandtab:

