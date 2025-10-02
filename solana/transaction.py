# Copyright (c) 2025 The Suckless Solana Python developers
# Distributed under the MIT software license, see the accompanying
# file COPYING or https://opensource.org/license/mit/.

import pydantic

from enum import StrEnum
from typing import Any


class Encoding(StrEnum):
    """
    Type representing the encoding for a returned transaction.
    """
    JSON = "json"
    JSON_PARSED = "jsonParsed"
    BASE64 = "base64"
    BASE58 = "base58"


class UiTokenAmount(pydantic.BaseModel):
    """
    Represents a UI-friendly token amount object in token balances.
    """
    # Raw amount of tokens as a string (ignoring decimals).
    amount: str = pydantic.Field(
        description="Raw token amount as a string (ignoring decimals)"
    )

    # Number of decimals configured for the token’s mint.
    decimals: int = pydantic.Field(
        description="Number of decimals configured for the token mint"
    )

    # Token amount as a float (accounting for decimals).
    # May be null (deprecated).
    uiAmount: float | None = pydantic.Field(
        default=None,
        description="Token amount as a float (accounting for decimals), "
                    "may be null (deprecated)"
    )

    # Token amount as a string (accounting for decimals).
    uiAmountString: str = pydantic.Field(
        description="Token amount as a string (accounting for decimals)"
    )


class TokenBalance(pydantic.BaseModel):
    """
    Represents a token balance entry before or after the transaction.
    """
    # Index of the account in the transaction’s message.accountKeys.
    accountIndex: int = pydantic.Field(
        description="Index of the account in the transaction’s "
                    "accountKeys list"
    )

    # Mint address (token mint pubkey).
    mint: str = pydantic.Field(
        description="Pubkey of the token’s mint"
    )

    # Owner address of the token account (may be undefined in some cases).
    owner: str | None = pydantic.Field(
        default=None,
        description="Owner of the token account (may be undefined)"
    )

    # Program ID of the Token program owning the account (may be undefined).
    programId: str | None = pydantic.Field(
        default=None,
        description="Program ID of token program owning the account "
                    "(may be undefined)"
    )

    # UI-friendly token amount object.
    uiTokenAmount: UiTokenAmount = pydantic.Field(
        description="UI-friendly token amount object"
    )


class ReturnData(pydantic.BaseModel):
    """
    Represents the “returnData” from an instruction, if present.
    """
    # Tuple [data, encoding], where data is usually base64-encoded.
    data: tuple[str, str] = pydantic.Field(
        description="Tuple of [return data string, encoding]"
    )

    # Program that returned the data (pubkey).
    programId: str = pydantic.Field(
        description="Program pubkey that returned the data"
    )


class LoadedAddresses(pydantic.BaseModel):
    """
    Represents addresses loaded from address lookup tables (if used).
    """
    # Ordered list of readonly loaded addresses (pubkeys).
    readonly: list[str] = pydantic.Field(
        description="Ordered list of readonly loaded addresses"
    )

    # Ordered list of writable loaded addresses (pubkeys).
    writable: list[str] = pydantic.Field(
        description="Ordered list of writable loaded addresses"
    )


class Instruction(pydantic.BaseModel):
    """
    Represents a single instruction in a transaction (or inner instruction).
    """
    # Indices of accounts (into message.accountKeys) passed
    # to this instruction.
    accounts: list[int] = pydantic.Field(
        description="Indices of accounts passed to this instruction "
                    "(into accountKeys)"
    )

    # The instruction data, encoded (base58) as a string.
    data: str = pydantic.Field(
        description="Instruction input data (base58-encoded)"
    )

    # Index of the program in message.accountKeys that executes
    # this instruction.
    programIdIndex: int = pydantic.Field(
        description="Index into accountKeys for the program executing "
                    "this instruction"
    )

    # Optional stack height (only present in newer instruction versions).
    stackHeight: int | None = pydantic.Field(
        default=None,
        description="Optional stack height hint (if supported)"
    )


class InnerInstruction(pydantic.BaseModel):
    """
    Represents inner instructions invoked by a top-level instruction.
    """
    # Index of the top-level instruction (whose inner instructions these are).
    index: int = pydantic.Field(
        description="Index of the top-level instruction originating "
                    "these inner instructions"
    )

    # List of inner program instructions invoked.
    instructions: list[Instruction] = pydantic.Field(
        description="List of inner instructions invoked"
    )


class MessageHeader(pydantic.BaseModel):
    """
    Header metadata for the transaction message.
    """
    # Number of required signatures for this transaction.
    numRequiredSignatures: int = pydantic.Field(
        description="Total number of signatures required for the transaction"
    )

    # Number of signed accounts that are read-only.
    numReadonlySignedAccounts: int = pydantic.Field(
        description="Number of signed accounts that are read-only"
    )

    # Number of unsigned accounts that are read-only.
    numReadonlyUnsignedAccounts: int = pydantic.Field(
        description="Number of unsigned accounts that are read-only"
    )


class AddressTableLookup(pydantic.BaseModel):
    """
    Address lookup from on-chain account lookup tables (optional).
    """
    # Pubkey of the address lookup table.
    accountKey: str = pydantic.Field(
        description="Pubkey of the address lookup table account"
    )

    # Indices of writable accounts loaded from the table.
    writableIndexes: list[int] = pydantic.Field(
        description="Indices loaded as writable from table"
    )

    # Indices of readonly accounts loaded from the table.
    readonlyIndexes: list[int] = pydantic.Field(
        description="Indices loaded as readonly from table"
    )


class Message(pydantic.BaseModel):
    """
    The message part of a Solana transaction (defines accounts, etc).
    """
    # List of base-58 public keys (accounts involved + signers).
    accountKeys: list[str] = pydantic.Field(
        description="List of public keys (base58) used by this transaction"
    )

    # Header describing number of signatures, and read-only accounts.
    header: MessageHeader = pydantic.Field(
        description="Header that describes signature & account properties"
    )

    # List of instructions in the transaction.
    instructions: list[Instruction] = pydantic.Field(
        description="List of program instructions to execute"
    )

    # A recent blockhash used to prevent transaction replay.
    recentBlockhash: str = pydantic.Field(
        description="Recent blockhash used by this transaction"
    )

    # Optional address table lookups
    # (if versioned transactions use lookup tables).
    addressTableLookups: list[AddressTableLookup] | None = pydantic.Field(
        default=None,
        description="Optional address lookup table entries (if used)"
    )


class Object(pydantic.BaseModel):
    """
    A Solana transaction wrapper including message & signatures.
    """
    # The message object (accounts + instructions, etc).
    message: Message = pydantic.Field(
        description="Message object containing accounts and instructions"
    )

    # Signatures applied to the transaction
    # (must match first numRequiredSignatures).
    signatures: list[str] = pydantic.Field(
        description="List of signatures (base58), "
                    "length = numRequiredSignatures"
    )


class Meta(pydantic.BaseModel):
    """
    Metadata about a transaction execution in a block.
    """
    # Error object if transaction failed, or null if succeeded.
    err: Any | None = pydantic.Field(
        default=None,
        description="Error object if failed, null if succeeded"
    )

    # Transaction fee paid in lamports (u64).
    fee: int = pydantic.Field(
        description="Fee the transaction was charged, in lamports"
    )

    # List of balances before execution.
    preBalances: list[int] = pydantic.Field(
        description="Account balances before execution"
    )

    # List of balances after execution.
    postBalances: list[int] = pydantic.Field(
        description="Account balances after execution"
    )

    # Optional list of inner instructions (or null if not recorded).
    innerInstructions: list[InnerInstruction] | None = pydantic.Field(
        default=None,
        description="Inner instructions invoked (null if not recorded)"
    )

    # Optional token balances before execution (omitted if not enabled).
    preTokenBalances: list[TokenBalance] | None = pydantic.Field(
        default=None,
        description="Token balances before execution (if enabled)"
    )

    # Optional token balances after execution (omitted if not enabled).
    postTokenBalances: list[TokenBalance] | None = pydantic.Field(
        default=None,
        description="Token balances after execution (if enabled)"
    )

    # Optional log messages (or null if not recorded).
    logMessages: list[str] | None = pydantic.Field(
        default=None,
        description="Logs emitted during execution (null if not recorded)"
    )

    # Optional rewards from the transaction (or null).
    rewards: list[Any] | None = pydantic.Field(
        default=None,
        description="Transaction-level rewards (or null if none)"
    )

    # Optional loaded addresses from address lookup tables (if used).
    loadedAddresses: LoadedAddresses | None = pydantic.Field(
        default=None,
        description="Addresses loaded from lookup tables (if used)"
    )

    # Optional return data from an instruction (if any).
    returnData: ReturnData | None = pydantic.Field(
        default=None,
        description="Return data from instruction (if any)"
    )

    # Optional compute units consumed by the transaction.
    computeUnitsConsumed: int | None = pydantic.Field(
        default=None,
        description="Compute units consumed during execution (if supported)"
    )

    # Version of the transaction ("legacy" or numeric).
    # May be undefined if not set.
    version: str | int | None = pydantic.Field(
        default=None,
        description="Transaction version: 'legacy' or integer (if supported)"
    )


class ObjectWithMeta(pydantic.BaseModel):
    """
    Wrapper combining a transaction with its execution metadata.
    """
    # The transaction object.
    transaction: Object = pydantic.Field(
        description="Transaction object (message + signatures)"
    )

    # Associated execution metadata.
    meta: Meta = pydantic.Field(
        description="Metadata about execution"
    )

# vim: set ts=4 sw=4 expandtab:

