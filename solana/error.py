# Copyright (c) 2025 The Suckless Solana Python developers
# Distributed under the MIT software license, see the accompanying
# file COPYING or https://opensource.org/license/mit/.

class RpcClientError(Exception):
    """
    Exception for the Solana RPC Client(s).
    """

    def __init__(self, msg: str, **kwds) -> None:
        """
        Initialize with an error message.
        """
        super().__init__(msg, **kwds)

# vim: set ts=4 sw=4 expandtab:

