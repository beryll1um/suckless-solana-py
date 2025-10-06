# Copyright (c) 2025 The Suckless Solana Python developers
# Distributed under the MIT software license, see the accompanying
# file COPYING or https://opensource.org/license/mit/.

# Import pytest to access the "asyncio" plugin required for async tests.
import pytest

# Custom HTTP wrapper implementation with unified interfaces.
from .http import RpcClient

# Types used for Solana RPC HTTP `getTransaction` arguments.
from . import block, transaction


@pytest.mark.asyncio
async def test_get_transaction_json() -> None:
    """
    Test HTTP Client `getTransaction` with `JSON` encoding.
    """
    # Define the HTTP client connection primitive.
    cli = RpcClient(uri="https://api.devnet.solana.com")
    # Get the example transaction from Solana docs in JSON encoding.
    tx = await cli.get_transaction(
        "5Pj5fCupXLUePYn18JkY8SrRaWFiUctuDTRwvUy2ML9y"
        "vkENLb1QMYbcBGcBXRrSVDjp7RjUwk9a3rLC6gpvtYpZ",
        commitment=block.Commitment.FINALIZED,
        encoding=transaction.Encoding.JSON
    )
    # On success, the response result should be successfully parsed.
    json = transaction.Json.model_validate(tx.result)
    # Also, I already know the expected block time of this transaction.
    assert json.blockTime == 1746479684


@pytest.mark.asyncio
async def test_get_transaction_parsed() -> None:
    """
    Test HTTP Client `getTransaction` with `JSON_PARSED` encoding.
    """
    # Define the HTTP client connection primitive.
    cli = RpcClient(uri="https://api.devnet.solana.com")
    # Get the example transaction from Solana docs in JSON_PARSED encoding.
    tx = await cli.get_transaction(
        "5Pj5fCupXLUePYn18JkY8SrRaWFiUctuDTRwvUy2ML9y"
        "vkENLb1QMYbcBGcBXRrSVDjp7RjUwk9a3rLC6gpvtYpZ",
        commitment=block.Commitment.FINALIZED,
        encoding=transaction.Encoding.JSON_PARSED
    )
    # On success, the response result should be successfully parsed.
    json = transaction.JsonParsed.model_validate(tx.result)
    # Also, I already know the expected block time of this transaction.
    assert json.blockTime == 1746479684


@pytest.mark.asyncio
async def test_get_block_json() -> None:
    """
    Test HTTP Client `getBlock` with `JSON` encoding.
    """
    # Define the HTTP client connection primitive.
    cli = RpcClient(uri="https://api.devnet.solana.com")
    # Get the example block from Solana docs in JSON encoding.
    blk = await cli.get_block(
        378967388,
        commitment=block.Commitment.FINALIZED,
        encoding=transaction.Encoding.JSON
    )
    # On success, the response result should be successfully parsed.
    json = block.Json.model_validate(blk.result)
    # Also, I already know the expected block time of this transaction.
    assert json.blockTime == 1746499354


@pytest.mark.asyncio
async def test_get_block_parsed() -> None:
    """
    Test HTTP Client `getBlock` with `JSON_PARSED` encoding.
    """
    # Define the HTTP client connection primitive.
    cli = RpcClient(uri="https://api.devnet.solana.com")
    # Get the example block from Solana docs in JSON_PARSED encoding.
    blk = await cli.get_block(
        378967388,
        commitment=block.Commitment.FINALIZED,
        encoding=transaction.Encoding.JSON_PARSED
    )
    # On success, the response result should be successfully parsed.
    json = block.JsonParsed.model_validate(blk.result)
    # Also, I already know the expected block time of this transaction.
    assert json.blockTime == 1746499354

# vim: set ts=4 sw=4 expandtab:

