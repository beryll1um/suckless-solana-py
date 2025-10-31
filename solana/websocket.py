# Copyright (c) 2025 The Suckless Solana Python developers
# Distributed under the MIT software license, see the accompanying
# file COPYING or https://opensource.org/license/mit/.

import logging
import asyncio
import websockets

from typing import Any, Callable, Coroutine
from json import JSONDecoder, JSONDecodeError

from . import (
    block, error, jsonrpc20, blocksubscribe, logssubscribe, transaction
)

DEFAULT_CLIENT_LOGGER_NAME = "solana-websocket"


class ClientError(Exception):
    """
    Exception for WebSocket Client-related errors.
    """

    def __init__(self, msg: str, **kwds) -> None:
        """
        Initialize with an error message.
        """
        super().__init__(msg, **kwds)


class Client:
    """
    Implementation of the WebSocket Client.
    """
    __slots__ = ("_conn", "_logger")

    def __init__(self) -> None:
        """
        Initialize all necessary control structures.
        """
        # Connection descriptor used to interact with the WS session.
        self._conn: websockets.ClientConnection | None = None
        # Logger used to notify about the client state.
        self._logger: logging.Logger | None = None

    async def connect(
        self,
        *args,
        logger: logging.Logger | None = None,
        **kwargs
    ) -> None:
        """
        Forward WebSocket connection instance creation arguments
        to the connection initializer.
        """
        if self.is_connected():
            raise ClientError("Unable to connect twice, disconnect first.")
        # Use a custom logger or the default logger if none is provided.
        self._logger = logger or logging.getLogger(DEFAULT_CLIENT_LOGGER_NAME)
        # Invoke connection establishment using the "websockets" library.
        self._conn = await websockets.connect(*args, **kwargs,
                                              logger=self._logger)

    @property
    def logger(self) -> logging.Logger:
        """
        Adapter for the `logging.Logger` object to prevent
        interaction with an uninitialized logger.
        """
        # Throw an exception in case of logger method invocation
        # without an active one.
        if self._logger is None:
            # Its better to raise a custom exception to simplify their
            # extensibility in the future.
            raise ClientError("No initialized logger identified")
        # Return internal logger instance.
        return self._logger

    @property
    def connection(self) -> websockets.ClientConnection:
        """
        Adapter for the `ClientConnection` object to prevent
        interaction with an uninitialized connection.
        """
        # Throw an exception in case of connection method invocation
        # without an active one.
        if self._conn is None:
            # Its better to raise a custom exception to simplify their
            # extensibility in the future.
            raise ClientError("No active connection identified")
        # Return internal client connection.
        return self._conn

    @property
    def disconnected(self) -> asyncio.Future[None]:
        """
        Future that resolves when the connection to the WebSocket Server
        ends, either by user action or in the background.
        """
        return asyncio.shield(self.connection.connection_lost_waiter)

    def is_connected(self) -> bool:
        """
        Return `True` if the client is connected.
        """
        # There may be no connection object, so this means
        # we are not connected ...
        if self._conn is None:
            return False
        # ... otherwise check connection state.
        return self.connection.state in (
            websockets.State.CONNECTING, websockets.State.OPEN)

    async def disconnect(self, *args, **kwargs) -> None:
        """
        Forward the WebSocket connection finalization arguments
        to the connection finalizer.
        """
        # Invoke connection finalization with the RPC WebSocket.
        await self.connection.close(*args, **kwargs)


NotificationHandler = Callable[[jsonrpc20.Notification], None]
"""
Handler for Solana JSON-RPC 2.0 WebSocket notifications.
"""


# Prevents the exponent from being calculated each time
# a sequence identifier is generated.
_ID_MOD = 2**31


class RpcClient(Client):
    """
    Implementation of the Solana RPC WebSocket Client.
    """
    __slots__ = ("_id", "_task", "_id2fut", "_sub2handler")

    def __init__(self, *args, **kwargs) -> None:
        """
        Initialize all necessary control structures.
        """
        # Call the base class initializer to set up its control structures.
        super().__init__(*args, **kwargs)
        # Incremental identifier used to indicate each next request sent.
        self._id = 0
        # Reference to the receiving data task.
        self._task: asyncio.Task | None = None
        # Map that relates request sequence numbers with their futures.
        self._id2fut: dict[int | str, asyncio.Future[jsonrpc20.Response]] = {}
        # Map that relates subscription IDs with their callbacks.
        self._sub2handler: dict[int, NotificationHandler] = {}

    def _process_obj(self, obj: dict[str, Any]) -> None:
        """
        Parse the received object and invoke the corresponding logic.
        """
        # JSON-RPC 2.0 specifies that responses to requests always
        # contain the same IDs provided in those requests.
        # See: https://www.jsonrpc.org/specification
        if "id" in obj:
            # Parse JSON-RPC 2.0 response from the object.
            resp = jsonrpc20.Response.model_validate(obj)
            # Delete it from the dictionary as it has already been utilized.
            fut = self._id2fut.pop(resp.id)
            # If its an error response.
            if resp.is_error():
                # The error is unexpected, so we need to raise an exception.
                fut.set_exception(error.RpcClientError(str(resp.error)))
            else:
                # Set result to the future waiting for the response.
                fut.set_result(resp)
            # We are finished, so exit the function.
            return
        # Otherwise, everything is a notification because, as specified
        # in the spec, a notification is "a Request object without
        # an 'id' member".
        elif "method" in obj:
            # Parse JSON-RPC 2.0 notification from the object and invoke
            # the notification callback.
            # There is no point in parallel processing of notifications here,
            # as this can easily turn into task spam.
            notif = jsonrpc20.Notification.model_validate(obj)
            # As far as I know, a dictionary is always required.
            if not isinstance(notif.params, dict):
                raise error.RpcClientError(
                    "Unexpected JSON-RPC 2.0 notification format: "
                    "'params' isn't a structured type")
            # Also there is should be a subscription ID
            # to identify notification.
            if "subscription" not in notif.params:
                raise error.RpcClientError(
                    "Unexpected JSON-RPC 2.0 notification format: "
                    "'params' doesn't contain the field 'subscription'")
            # If such a handler is still registered, try to execute it.
            if handler := self._sub2handler.get(notif.params["subscription"]):
                handler(notif)
        else:
            # Impossible cases should be logged for sure.
            raise ValueError("Unexpected format of JSON-RPC 2.0 message")

    async def _recv_loop(self) -> None:
        """
        Listen for RPCs and propagate them to independent task handlers.
        """
        # Use a JSON decoder for stream decoding of incoming data.
        decoder = JSONDecoder()
        # Buffer to store data for decoding.
        buffer = ""
        # This try-except block will handle the WebSocket streaming receiver.
        try:
            while True:
                # Read the first chunk from the WebSocket.
                async for chunk in self.connection.recv_streaming(decode=True):
                    # Append received chunks to the buffer for decoding.
                    buffer += chunk  # type: ignore
                    # A chunk may contain more than one complete part
                    # ready for decoding, so continue until an error occurs.
                    while buffer:
                        # This try-except block is the only way
                        # to handle requests for additional data to parse.
                        try:
                            # Try decoding the raw buffer data into JSON.
                            obj, end = decoder.raw_decode(buffer)
                            try:
                                self._process_obj(obj)
                            except Exception as e:
                                self.logger.error(
                                    f"Exception in the receiving loop: {e}")
                            # Shrink the buffer to where the decoder stopped.
                            buffer = buffer[end:]
                        # Decoding failed, but no panic.
                        # We just need to read another chunk of data
                        # to fill the missing part.
                        except JSONDecodeError:
                            # Decoding is not finished successfully;
                            # break to read new data into the buffer.
                            break
        # This is the only exception that may be thrown
        # by the websockets library.
        except websockets.exceptions.ConnectionClosed:
            pass

    async def start(self, *args, **kwargs) -> None:
        """
        Forward WebSocket connection instance creation arguments
        to the connection initializer and create receiving loop task.
        """
        # Its possible that the user may want to connect first and
        # start RPC receiving loop only after.
        if not super().is_connected():
            # Forward startup arguments to the original connection method
            # of the WebSocket client base class.
            await super().connect(*args, **kwargs)
        # However, only one instance of a task should be allowed.
        if self._task is not None and not self._task.done():
            raise error.RpcClientError(
                "Only one instance of the receiving loop is allowed.")
        # If the connection is established and the task does not exist or
        # has completed, a new one can be created.
        self._task = asyncio.create_task(self._recv_loop())

    @property
    def finalized(
        self, loop: asyncio.AbstractEventLoop | None = None
    ) -> asyncio.Future[None]:
        """
        Future that resolves when the receiving loop is completed,
        either by the client or the server.
        """
        if self._task is None:
            raise error.RpcClientError(
                "Unable to wait for unstarted task to finalize.")
        return self._task

    async def _send_request(
        self, req: jsonrpc20.Request
    ) -> jsonrpc20.Response:
        """
        Send an RPC request and wait for the response.
        """
        # Instantiate a future to wait for the subscription response.
        fut = asyncio.Future[jsonrpc20.Response]()
        # Assign this Future to the sequence number for this RPC request.
        self._id2fut[req.id] = fut
        # This connection `send` method may fail due to connectivity issues,
        # so we need to handle it anyway.
        try:
            # Build JSON-RPC 2.0 request with method-specific parameters.
            await self.connection.send(req.model_dump_json())
        except Exception:
            # The future shouldn't expect an answer, so remove it.
            del self._id2fut[req.id]
            raise
        return await fut

    def _next_id(self) -> int:
        """
        Increment the sequence number by one and return it.
        """
        self._id = (self._id % _ID_MOD) + 1
        return self._id

    async def _subscribe(
        self, req: jsonrpc20.Request, handler: NotificationHandler
    ) -> int:
        """
        Send an RPC subscribe request and wait for the response.
        """
        resp = await self._send_request(req)
        # If the response result is not a subscription integer,
        # we need to raise an exception.
        if not isinstance(resp.result, int):
            raise TypeError("JSON-RPC 2.0 subscribe request must be responded "
                            "to with an integer subscription ID.")
        # Bind notification callback for obtained subscription ID.
        self._sub2handler[resp.result] = handler
        return resp.result

    async def _unsubscribe(self, method: str, sub: int) -> None:
        """
        Build and send RPC unsubscribe request, wait for the response and
        delete appropriate notification handler.
        """
        resp = await self._send_request(jsonrpc20.Request(
            method=method, params=[sub], id=self._next_id()
        ))
        # If the response result is not a subscription integer,
        # we need to raise an exception.
        if not isinstance(resp.result, bool):
            raise TypeError("JSON-RPC 2.0 subscribe request must be responded "
                            "to with a boolean success indicator.")
        # I'm not sure is it possible at all, but better to follow spec.
        if not resp.result:
            raise error.RpcClientError(
                f"Failed to unsubscribe from '{sub}' subscription ID "
                "notification.")
        # Unbind notification callback for specific subscription ID.
        del self._sub2handler[sub]

    async def logs_subscribe(
        self,
        handler: NotificationHandler,
        mentions_or_filter: list[logssubscribe.Mention] | logssubscribe.Filter,
        commitment: block.Commitment
    ) -> int:
        """
        Subscribe to transaction logs.
        """
        return await self._subscribe(
            jsonrpc20.Request(
                method="logsSubscribe",
                params=[
                    {"mentions": mentions_or_filter}
                    if isinstance(mentions_or_filter, list)
                    else mentions_or_filter,
                    {"commitment": commitment}
                ],
                id=self._next_id()
            ),
            handler
        )

    async def logs_unsubscribe(self, sub: int) -> None:
        """
        Unsubscribe from transaction logs.
        """
        await self._unsubscribe("logsUnsubscribe", sub)

    async def block_subscribe(
        self,
        handler: NotificationHandler,
        mentions_or_filter:
            list[blocksubscribe.Mention] | blocksubscribe.Filter,
        commitment: block.Commitment = block.Commitment.FINALIZED,
        encoding: block.Encoding = block.Encoding.JSON,
        transaction_details: block.Details = block.Details.FULL,
        rewards: bool = False,
    ) -> int:
        """
        Subscribe to block notifications.
        """
        return await self._subscribe(
            jsonrpc20.Request(
                method="blockSubscribe",
                params=[
                    {"mentionsAccountOrProgram": mentions_or_filter}
                    if isinstance(mentions_or_filter, list)
                    else mentions_or_filter,
                    {
                        # The commitment describes how finalized a block
                        # is at that point in time.
                        "commitment": commitment,
                        "encoding": encoding,
                        "transactionDetails": transaction_details,
                        "showRewards": rewards
                    }
                ],
                id=self._next_id()
            ),
            handler
        )

    async def block_unsubscribe(self, sub: int) -> None:
        """
        Unsubscribe from block notifications.
        """
        await self._unsubscribe("blockUnsubscribe", sub)

    async def slot_subscribe(self, handler: NotificationHandler) -> int:
        """
        Subscribe to slot notifications.
        """
        return await self._subscribe(
            jsonrpc20.Request(
                method="slotSubscribe",
                id=self._next_id()
            ),
            handler
        )

    async def slot_unsubscribe(self, sub: int) -> None:
        """
        Unsubscribe from slot notifications.
        """
        await self._unsubscribe("slotUnsubscribe", sub)

# vim: set ts=4 sw=4 expandtab:

