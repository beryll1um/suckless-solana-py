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

    async def start(
        self,
        *args,
        logger: logging.Logger | None = None,
        **kwargs
    ) -> None:
        """
        Forward WebSocket connection instance creation arguments
        to the connection initializer.
        """
        # Use a custom logger or the default logger if none is provided.
        self._logger = logger or logging.getLogger(DEFAULT_CLIENT_LOGGER_NAME)
        try:
            # Invoke connection establishment using the "websockets" library.
            self._conn = await websockets.connect(*args, **kwargs,
                                                  logger=self._logger)
        except Exception as e:
            # Its better to raise a custom exception to simplify their
            # extensibility in the future.
            raise ClientError("Error connecting to server.") from e

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
            raise ClientError("No initialized logger identified.")
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
            raise ClientError("No active connection identified.")
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
        return self.connection.state in (
            websockets.State.CONNECTING, websockets.State.OPEN)

    async def disconnect(self, *args, **kwargs) -> None:
        """
        Forward the WebSocket connection finalization arguments
        to the connection finalizer.
        """
        try:
            # Invoke connection finalization with the RPC WebSocket.
            await self.connection.close(*args, **kwargs)
        except Exception as e:
            # Raise custom client exception to simplify future extensibility.
            raise ClientError("Failed to finalize connection.") from e


class RpcClient(Client):
    """
    Implementation of the Solana RPC WebSocket Client.
    """
    __slots__ = ("_seq", "_seq2fut", "_tasks")

    def __init__(self, *args, **kwargs) -> None:
        """
        Initialize all necessary control structures.
        """
        # Call the base class initializer to set up its control structures.
        super().__init__(*args, **kwargs)
        # Incremental identifier used to indicate each next request sent.
        self._seq = 0
        # Map that relates request sequence numbers with their futures.
        self._seq2fut: dict[int | str, asyncio.Future[jsonrpc20.Response]] = {}
        # Initialize O(1) accesss storage for active tasks.
        self._tasks: set[asyncio.Task] = set()

    def _notification_cb(self, notif: jsonrpc20.Notification) -> None:
        """
        Abstract method that defines the JSON-RPC 2.0 notification callback.
        """
        pass

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
            fut = self._seq2fut.pop(resp.id)
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
            self._notification_cb(jsonrpc20.Notification.model_validate(obj))
        # If something unexpected happened, this should be impossible.
        else:
            # Impossible cases should be logged for sure.
            raise ValueError("Unexpected format of JSON-RPC 2.0 message.")

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
            # Lets start reading the WebSocket incoming data chunk by chunk.
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
                                # If an exception occurs, log it
                                # instead of stopping the loop.
                                # I expect it to handle validator exceptions.
                                self.logger.error(
                                    f"Exception in the receiving loop: {e}")
                            # Shrink the buffer to where the decoder stopped.
                            buffer = buffer[end:]
                        # Decoding failed, but without panic.
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
        to the connection initializer.
        """
        # Forward startup arguments to the original startup method
        # of the WebSocket client base class.
        await super().start(*args, **kwargs)
        # If the connection is successful, create a listener
        # to read WebSocket messages.
        task = asyncio.create_task(self._recv_loop())
        # Dangling tasks is prohibited by docs.
        self._tasks.add(task)
        task.add_done_callback(self._tasks.discard)

    async def _send_request(
        self,
        req: jsonrpc20.Request
    ) -> jsonrpc20.Response:
        """
        Send an RPC request and wait for the response.
        """
        # Instantiate a future to wait for the subscription response.
        fut = asyncio.Future[jsonrpc20.Response]()
        # Assign this Future to the sequence number for this RPC request.
        self._seq2fut[req.id] = fut
        # This connection `send` method may fail due to connectivity issues,
        # so we need to handle it anyway.
        try:
            # Build JSON-RPC 2.0 request with method-specific parameters.
            await self.connection.send(req.model_dump_json())
        except Exception as e:
            # The future shouldn't expect an answer, so remove it.
            del self._seq2fut[req.id]
            # Raise custom client exception to simplify future extensibility.
            raise error.RpcClientError(
                "Failed to send Solana RPC request.") from e
        # Await the response from the receiving task.
        return await fut

    def _next_seq(self) -> int:
        """
        Increment the sequence number by one and return it.
        """
        self._seq += 1
        return self._seq

    async def logs_subscribe(
        self,
        mentions_or_filter: list[logssubscribe.Mention] | logssubscribe.Filter,
        commitment: block.Commitment
    ) -> jsonrpc20.Response:
        """
        Subscribe to transaction logs.
        """
        return await self._send_request(jsonrpc20.Request(
            method="logsSubscribe",
            params=[
                {"mentions": mentions_or_filter}
                if isinstance(mentions_or_filter, list)
                else mentions_or_filter,
                {"commitment": commitment}
            ],
            id=self._next_seq()
        ))

    async def logs_unsubscribe(self, subscription: int) -> jsonrpc20.Response:
        """
        Unsubscribe from transaction logs.
        """
        return await self._send_request(jsonrpc20.Request(
            method="logsUnsubscribe",
            params=[subscription],
            id=self._next_seq()
        ))

    async def block_subscribe(
        self,
        mentions_or_filter:
            list[blocksubscribe.Mention] | blocksubscribe.Filter,
        commitment: block.Commitment,
        encoding: block.Encoding = block.Encoding.JSON,
        transaction_details: block.Details = block.Details.FULL,
        rewards: bool = False
    ) -> jsonrpc20.Response:
        """
        Subscribe to block logs.
        """
        return await self._send_request(jsonrpc20.Request(
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
            id=self._next_seq()
        ))

    async def block_unsubscribe(self, subscription: int) -> jsonrpc20.Response:
        """
        Unsubscribe from block notifications.
        """
        return await self._send_request(jsonrpc20.Request(
            method="blockUnsubscribe",
            params=[subscription],
            id=self._next_seq()
        ))

    async def slot_subscribe(self) -> jsonrpc20.Response:
        """
        Subscribe to receive notification anytime a slot is processed
        by the validator.
        """
        return await self._send_request(jsonrpc20.Request(
            method="slotSubscribe",
            id=self._next_seq()
        ))

    async def slot_unsubscribe(self, subscription: int) -> jsonrpc20.Response:
        """
        Subscribe to receive notification anytime a slot is processed
        by the validator.
        """
        return await self._send_request(jsonrpc20.Request(
            method="slotUnsubscribe",
            params=[subscription],
            id=self._next_seq()
        ))


NotificationCallback = Callable[
    [jsonrpc20.Notification], Coroutine[None, None, None]]
"""
Handler for Solana JSON-RPC 2.0 WebSocket notifications.
"""


class RpcDispatcherError(Exception):
    """
    Exception for the dispatcher of the Solana RPC WebSocket Client.
    """

    def __init__(self, msg: str, **kwds) -> None:
        """
        Initialize with an error message.
        """
        super().__init__(msg, **kwds)


class RpcDispatcher(RpcClient):
    """
    Implementation of a dispatcher for the Solana RPC WebSocket Client.
    """
    __slots__ = ("_method2cb", "_tasks")

    def __init__(self, *args, **kwargs) -> None:
        """
        Initialize all necessary control structures.
        """
        # Call the base class initializer to set up its control structures.
        super().__init__(*args, **kwargs)
        # Dictionary containing all notification handlers to be executed.
        self._method2cb: dict[str, NotificationCallback] = {}
        # Initialize O(1) accesss storage for active tasks.
        self._tasks: set[asyncio.Task] = set()

    def _notification_cb(self, notif: jsonrpc20.Notification) -> None:
        """
        Callback for the Solana JSON-RPC 2.0 notifications.
        """
        try:
            # If the callback is not registered, skip execution.
            cb = self._method2cb[notif.method]
            # Create an independent task for the method handler.
            task = asyncio.create_task(cb(notif))
            # Dangling tasks is prohibited by docs.
            self._tasks.add(task)
            task.add_done_callback(self._tasks.discard)
        except KeyError as e:
            # Its better to raise a custom exception to simplify their
            # extensibility in the future.
            raise RpcDispatcherError(
                f"The '{notif.method}' notification remains unhandled.") from e

    def set_notification_handler(
        self,
        method: str,
        cb: NotificationCallback
    ) -> None:
        """
        Add a handler for a specific notification callback.
        """
        # Add the handler to the set if its not already present.
        self._method2cb[method] = cb

    def unset_notification_handler(self, method: str) -> None:
        """
        Remove a handler for a specific notification callback.
        """
        try:
            # Try to remove the handler from the "logsNotification" set.
            del self._method2cb[method]
        except KeyError as e:
            # Its better to raise a custom exception to simplify their
            # extensibility in the future.
            raise RpcDispatcherError(
                "This method isn't registered yet.") from e

# vim: set ts=4 sw=4 expandtab:

