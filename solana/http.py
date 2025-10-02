# Copyright (c) 2025 The Suckless Solana Python developers
# Distributed under the MIT software license, see the accompanying
# file COPYING or https://opensource.org/license/mit/.

import httpx

from functools import cached_property

from . import error, transaction, logssubscribe, jsonrpc20


class Client[T]:
    """
    Implementation of the HTTP Client.
    """
    __slots__ = ("_uri", "_user_agent", "_timeout")

    def __init__(
        self,
        uri: str,
        *,
        user_agent: str = "suckless-solana-py",
        timeout: float = 30.0
    ) -> None:
        self._uri = uri
        self._user_agent = user_agent
        self._timeout = timeout

    @cached_property
    def _client(self) -> httpx.AsyncClient:
        """
        Creates a reusable HTTP(S) client.
        """
        return httpx.AsyncClient(headers={"User-Agent": self._user_agent},
                                 timeout=httpx.Timeout(self._timeout))

    async def close(self) -> None:
        """
        Destroys a reusable HTTP(S) client session.
        """
        # Close asynchronous client and release all resources.
        await self._client.aclose()

    # There is not better way to explain mypy something about the return type
    # than just don't touch it.
    async def __aenter__(self) -> "Client":
        """
        Enters the context for the `async with` statement.
        """
        return self  # type: ignore

    async def __aexit__(self, exc_type, exc_value, traceback) -> None:
        """
        Exits the context for the `async with` statement.
        """
        await self.close()


class RpcClient(Client["RpcClient"]):
    """
    Implementation of the Solana RPC HTTP Client.
    """
    def __init__(self, *args, **kwargs) -> None:
        """
        Initialize all necessary control structures.
        """
        # Call the base class initializer to set up its control structures.
        super().__init__(*args, **kwargs)

    async def _send_request(
        self,
        req: jsonrpc20.Request
    ) -> jsonrpc20.Response:
        """
        Send an RPC request and wait for the response.
        """
        # As far as I know, all Solana RPC HTTP methods expect POST requests.
        resp = await self._client.post(
            self._uri,
            headers={"Content-Type": "application/json"},
            content=req.model_dump_json()
        )
        # In case the request fails, we need to raise an exception.
        if resp.status_code != 200:
            # This exception should store the content that RPC responded to.
            raise error.RpcClientError(resp.text)
        try:
            return jsonrpc20.Response.model_validate_json(resp.text)
        except Exception as exc:
            raise error.RpcClientError(
                "Unexpected format of JSON-RPC 2.0 response.")

    async def get_transaction(
        self,
        signature: str,
        commitment: transaction.Commitment,
        encoding: transaction.Encoding = transaction.JSON
    ) -> jsonrpc20.Response:
        """
        Returns transaction details for a confirmed transaction
        """
        return await self._send_request(jsonrpc20.Request(
            method="getTransaction",
            params=[signature, {
                # The commitment describes how finalized a block
                # is at that point in time.
                "commitment": commitment,
                # Currently, the only valid value for this parameter is 0.
                "maxSupportedTransactionVersion": 0,
                "encoding": encoding
            }],
            # Because only one request at a time can be constant.
            id="1"
        ))

# vim: set ts=4 sw=4 expandtab:

