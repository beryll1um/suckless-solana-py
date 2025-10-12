# Copyright (c) 2025 The Suckless Solana Python developers
# Distributed under the MIT software license, see the accompanying
# file COPYING or https://opensource.org/license/mit/.

# Import pytest to access the "asyncio" plugin required for async tests.
import pytest
import asyncio

# Custom WebSocket wrapper implementation with unified interfaces.
from .websocket import Client, RpcClient

# Types used for Solana RPC WebSocket `logsSubscribe` arguments.
from . import jsonrpc20, block, logssubscribe


@pytest.mark.asyncio
async def test_start_disconnect() -> None:
    """
    Test WebSocket Client `start` and `disconnect` methods.
    """
    # Define the WebSocket client connection primitive.
    ws = Client()
    # Connect to the Solana Devnet RPC WebSocket.
    await ws.connect(uri="wss://api.devnet.solana.com")
    # Verify that the client is successfully connected.
    assert ws.is_connected()
    # Disconnect from the WebSocket.
    await ws.disconnect()
    # Verify that the client is successfully disconnected from the RPC.
    assert not ws.is_connected()


@pytest.mark.asyncio
async def test_logs_subscribe_unsubscribe() -> None:
    """
    Test RPC Client `logs_subscribe` and `logs_unsubscribe` methods
    ability to register and remove 'logsNotification' handlers.
    """
    # Define the Solana RPC WebSocket client connection primitive.
    rpc = RpcClient()
    # Connect to the Solana Devnet RPC WebSocket.
    await rpc.start(uri="wss://api.devnet.solana.com")

    # Create an Event to coordinate between the handler and the test task.
    ev = asyncio.Event()
    # Subscribe to account logs and await the response.
    sub = await rpc.logs_subscribe(
        lambda _: asyncio.sleep(0.0, result=ev.set()),  # type: ignore
        [logssubscribe.Mention("11111111111111111111111111111111")],
        block.Commitment.PROCESSED
    )

    # Wait up to two seconds for the "logsNotification" event to be received.
    await asyncio.sleep(2.0)
    # Fail the test if no event was received within two seconds.
    assert ev.is_set()

    # Unsubscribe from the subscription and await the response.
    await rpc.logs_unsubscribe(sub)
    # Disconnect from the RPC.
    await rpc.disconnect()
    # Wait for the RPC to complete (process the rest of the received payload).
    await rpc.finalized
    # Verify that the client is successfully disconnected from the RPC.
    assert not rpc.is_connected()

# vim: set ts=4 sw=4 expandtab:

