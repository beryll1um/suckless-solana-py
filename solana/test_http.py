# Copyright (c) 2025 The Suckless Solana Python developers
# Distributed under the MIT software license, see the accompanying
# file COPYING or https://opensource.org/license/mit/.

# Import pytest to access the "asyncio" plugin required for async tests.
import pytest

# Custom HTTP wrapper implementation with unified interfaces.
from .http import RpcClient

# Types used for Solana RPC HTTP `getTransaction` arguments.
from . import transaction


@pytest.mark.asyncio
async def test_get_transaction() -> None:
    """
    Test WebSocket Client `start` and `disconnect` methods.
    """
    # Define the HTTP client connection primitive.
    cli = RpcClient(uri="https://api.devnet.solana.com")
    # Get the example transaction from Solana docs.
    tx = await cli.get_transaction(
        "5Pj5fCupXLUePYn18JkY8SrRaWFiUctuDTRwvUy2ML9y"
        "vkENLb1QMYbcBGcBXRrSVDjp7RjUwk9a3rLC6gpvtYpZ",
        commitment=transaction.Finalized
    )
    # On success, the response should contain dict in result field.
    assert isinstance(tx.result, dict)
    # Also, I already know the expected block time of this transaction.
    assert tx.result.get("blockTime") == 1746479684

# vim: set ts=4 sw=4 expandtab:

