# Copyright (c) 2025 The Suckless Solana Python developers
# Distributed under the MIT software license, see the accompanying
# file COPYING or https://opensource.org/license/mit/.

# Import pytest to access the "asyncio" plugin required for async tests.
import pytest

# Custom WebSocket wrapper implementation with unified interfaces.
from .websocket import Client, RpcClient, RpcDispatcher

# Utilities required to simulate async behavior.
from asyncio import Event, sleep

# Types used for Solana RPC WebSocket `logsSubscribe` arguments.
from . import block, logssubscribe


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
    Test RPC Client `logs_subscribe` and `logs_unsubscribe` methods.
    """
    # Define the Solana RPC WebSocket client connection primitive.
    rpc = RpcClient()
    # Connect to the Solana Devnet RPC WebSocket.
    await rpc.start(uri="wss://api.devnet.solana.com")
    # Subscribe to account logs and await the response.
    resp = await rpc.logs_subscribe(
        [logssubscribe.Mention("11111111111111111111111111111111")],
        block.Commitment.PROCESSED
    )
    # On success, the response should contain a subscription ID (int).
    assert isinstance(resp.result, int)
    # Unsubscribe from the subscription and await the response.
    resp = await rpc.logs_unsubscribe(resp.result)
    # On success, the response should be a bool and equal to True.
    assert isinstance(resp.result, bool) and resp.result is True
    # Disconnect from the RPC.
    await rpc.disconnect()
    # Verify that the client is successfully disconnected from the RPC.
    assert not rpc.is_connected()


@pytest.mark.asyncio
async def test_set_unset_notification_handler() -> None:
    """
    Test the Dispatcher’s ability to register and
    remove 'logsNotification' handlers.
    """
    # Define the WebSocket client connection primitive.
    disp = RpcDispatcher()
    # Connect to the Solana Devnet RPC WebSocket.
    await disp.start(uri="wss://api.devnet.solana.com")

    # Create an Event to coordinate between the handler and the test task.
    ev = Event()
    # Register a "logsNotification" handler in the Dispatcher.
    disp.set_notification_handler(
        "logsNotification",
        lambda _: sleep(0.0, result=ev.set())  # type: ignore
    )

    # Subscribe to account logs and await the response.
    resp = await disp.logs_subscribe(
        [logssubscribe.Mention("11111111111111111111111111111111")],
        block.Commitment.PROCESSED
    )
    # On success, the response should contain a subscription ID (int).
    assert isinstance(resp.result, int)

    # Wait up to two seconds for the "logsNotification" event to be received.
    await sleep(2.0)
    # Fail the test if no event was received within two seconds.
    assert ev.is_set()

    # Remove the "logsNotification" handler from the Dispatcher.
    disp.unset_notification_handler("logsNotification")
    # Clear the event so it doesn’t overlap with the previous result.
    ev.clear()
    # Wait for two seconds to confirm no event is received.
    await sleep(2.0)
    # If no event was received, the removal was successful.
    assert not ev.is_set()

    # Unsubscribe from the subscription and await the response.
    resp = await disp.logs_unsubscribe(resp.result)
    # On success, the response should be a bool and equal to True.
    assert isinstance(resp.result, bool) and resp.result is True
    # Disconnect from the RPC.
    await disp.disconnect()
    # Verify that the dispatcher is successfully disconnected from the RPC.
    assert not disp.is_connected()

# vim: set ts=4 sw=4 expandtab:

