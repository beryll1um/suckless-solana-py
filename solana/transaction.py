# Copyright (c) 2025 The Suckless Solana Python developers
# Distributed under the MIT software license, see the accompanying
# file COPYING or https://opensource.org/license/mit/.

import pydantic

from enum import StrEnum
from typing import Any, Literal


class Encoding(StrEnum):
    """
    Type representing the encoding for a returned transaction.
    """
    JSON = "json"
    JSON_PARSED = "jsonParsed"
    BASE64 = "base64"
    BASE58 = "base58"


class ReturnData(pydantic.BaseModel):
    """
    Represents the “returnData” from an instruction, if present.
    """
    # Tuple [data, encoding], where data is base64-encoded.
    data: tuple[str, str] | list[str] = pydantic.Field(
        description="Tuple/array of [return data string, encoding]"
    )

    # Program that returned the data (pubkey).
    programId: str = pydantic.Field(
        description="Program pubkey that returned the data"
    )


class TokenAmount(pydantic.BaseModel):
    """
    UI-friendly token amount object used in token balances.
    Mirrors Anza's `TokenAmount`
    (StringifiedBigInt/Number in TS become strings here).
    """
    # Raw amount of tokens as a string (ignoring decimals).
    amount: str = pydantic.Field(
        description="Raw token amount as a string (ignoring decimals)"
    )

    # Number of decimals configured for the token's mint.
    decimals: int = pydantic.Field(
        description="Number of decimals configured for the token mint"
    )

    # Token amount as a string (accounting for decimals).
    uiAmountString: str = pydantic.Field(
        description="Token amount as a string (accounting for decimals)"
    )

    # Deprecated: Token amount as a float (may be null).
    uiAmount: float | None = pydantic.Field(
        default=None,
        description="(Deprecated) Token amount as a float; may be null"
    )


class TokenBalance(pydantic.BaseModel):
    """
    Represents a token balance entry before or after the transaction.
    Mirrors Anza's `TokenBalance`.
    """
    # Index of the account in the transaction's message.accountKeys.
    accountIndex: int = pydantic.Field(
        description="Index of the account in the transaction's "
                    "accountKeys list"
    )

    # Mint address (token mint pubkey).
    mint: str = pydantic.Field(
        description="Pubkey of the token's mint"
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
    uiTokenAmount: TokenAmount = pydantic.Field(
        description="UI-friendly token amount object"
    )


class Reward(pydantic.BaseModel):
    """
    Transaction-level reward (fee, rent, voting, staking).
    """
    pubkey: str = pydantic.Field(
        description="Account that received the reward (base58 pubkey)"
    )
    lamports: int = pydantic.Field(
        description="Lamports credited/debited as a signed i64"
    )
    postBalance: int = pydantic.Field(
        description="Account balance in lamports after applying the reward"
    )
    rewardType: Literal['fee', 'rent', 'voting', 'staking'] | None = \
        pydantic.Field(
            default=None,
            description="Type of reward: 'fee' | 'rent' | 'voting' "
                        "| 'staking'")
    commission: int | None = pydantic.Field(
        default=None,
        description="Vote account commission when credited (if applicable)"
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


class MessageHeader(pydantic.BaseModel):
    """
    Header metadata for the transaction message.
    (Present for `encoding='json'` messages.)
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
    str lookup from on-chain account lookup tables (optional).
    Mirrors Anza's `AddressTableLookup`.
    """
    # Pubkey of the address lookup table.
    accountKey: str = pydantic.Field(
        description="Pubkey of the address lookup table account"
    )

    # Indices of readonly accounts loaded from the table.
    readonlyIndexes: list[int] = pydantic.Field(
        description="Indices loaded as readonly from table"
    )

    # Indices of writable accounts loaded from the table.
    writableIndexes: list[int] = pydantic.Field(
        description="Indices loaded as writable from table"
    )


class Instruction(pydantic.BaseModel):
    """
    Represents a single (unparsed) instruction in a transaction
    (or inner instruction). Mirrors Anza `TransactionInstruction` shape
    when `encoding="json"`.
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


class RawInstruction(pydantic.BaseModel):
    """
    Raw (partially decoded) instruction entry when using `jsonParsed` encoding.
    Mirrors Anza's `PartiallyDecodedTransactionInstruction`.
    """
    # Account pubkeys referenced by this instruction.
    accounts: list[str] = pydantic.Field(
        description="Account pubkeys referenced by this instruction"
    )

    # The instruction data, encoded (base58) as a string.
    data: str = pydantic.Field(
        description="Instruction input data (base58-encoded)"
    )

    # Program ID (pubkey) that executes this instruction.
    programId: str = pydantic.Field(
        description="Program ID (pubkey)"
    )

    # Optional stack height (only present in newer instruction versions).
    stackHeight: int | None = pydantic.Field(
        default=None,
        description="Optional stack height hint (if supported)"
    )


class ProgramParsed(pydantic.BaseModel):
    """
    Program-specific parsed instruction payload.
    Mirrors Anza's `ParsedTransactionInstruction.parsed` object.
    """
    # Parsed instruction type, e.g. "transfer".
    type: str = pydantic.Field(
        description="Instruction type (e.g., 'transfer')"
    )

    # Program-specific key-value fields for this instruction.
    info: dict[str, Any] | None = pydantic.Field(
        default=None,
        description="Program-specific parsed fields"
    )


class ParsedProgramInstruction(pydantic.BaseModel):
    """
    Parsed program instruction entry for `encoding="jsonParsed"`.
    Mirrors Anza's `ParsedTransactionInstruction`.
    """
    # Program name (e.g., "system", "spl-token").
    program: str = pydantic.Field(
        description="Program name (e.g., 'system', 'spl-token')"
    )

    # Program ID (pubkey).
    programId: str = pydantic.Field(
        description="Program ID (pubkey)"
    )

    # Parsed program data: usually an object {"type": ..., "info": {...}}.
    parsed: ProgramParsed | str | int | None = pydantic.Field(
        description="Program-specific parsed data (object or primitive)"
    )

    # Optional stack height (only present in newer instruction versions).
    stackHeight: int | None = pydantic.Field(
        default=None,
        description="Optional stack height hint (if supported)"
    )


class InnerInstruction(pydantic.BaseModel):
    """
    Represents inner instructions invoked by a top-level instruction
    for `encoding="json"` responses.
    Mirrors Anza's unparsed inner instructions entry.
    """
    # Index of the top-level instruction (whose inner instructions these are).
    index: int = pydantic.Field(
        description="Index of the top-level instruction originating these "
                    "inner instructions"
    )

    # List of inner program instructions invoked.
    instructions: list[Instruction] = pydantic.Field(
        description="List of inner instructions invoked"
    )


class JsonParsedInnerInstruction(pydantic.BaseModel):
    """
    Inner instruction wrapper (jsonParsed) holding mixed parsed/raw entries.
    Mirrors Anza's parsed inner instructions entry.
    """
    # Index of the top-level instruction (whose inner instructions these are).
    index: int = pydantic.Field(
        description="Index of the top-level instruction originating these "
                    "inner instructions"
    )

    # List of inner program instructions: parsed or raw.
    instructions: list[ParsedProgramInstruction | RawInstruction] = \
        pydantic.Field(
            description="List of inner instructions (parsed or raw)")


class Message(pydantic.BaseModel):
    """
    The message part of a Solana transaction (defines accounts, etc)
    for `encoding="json"` responses.
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


class InnerTransaction(pydantic.BaseModel):
    """
    A Solana transaction wrapper including message & signatures
    for `encoding="json"` responses.
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


class ParsedAccountKey(pydantic.BaseModel):
    """
    Account key entry with signer/writable flags for `encoding="jsonParsed"`.
    """
    # Account pubkey (base58).
    pubkey: str = pydantic.Field(
        description="Account pubkey (base58)"
    )

    # Whether the account is a required signer.
    signer: bool = pydantic.Field(
        description="Whether the account is a signer"
    )

    # Whether the account is writable.
    writable: bool = pydantic.Field(
        description="Whether the account is writable"
    )

    # Source of the account (transaction or lookupTable); may be omitted.
    source: Literal["transaction", "lookupTable"] = pydantic.Field(
        description="Source of the account: 'transaction' or 'lookupTable'"
    )


class JsonParsedMessage(pydantic.BaseModel):
    """
    The message part of a Solana transaction for `encoding="jsonParsed"`.
    """
    # List of account entries with signer/writable/source flags.
    accountKeys: list[ParsedAccountKey] = pydantic.Field(
        description="Account entries with signer/writable/source flags"
    )

    # List of instructions (parsed or raw) in the transaction.
    instructions: list[ParsedProgramInstruction | RawInstruction] = \
        pydantic.Field(
            description="List of program instructions (parsed or raw)")

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


class JsonParsedInnerTransaction(pydantic.BaseModel):
    """
    A Solana transaction wrapper including message & signatures
    for `encoding="jsonParsed"` responses.
    """
    # The parsed message object.
    message: JsonParsedMessage = pydantic.Field(
        description="Parsed message object containing accounts "
                    "and instructions")

    # Signatures applied to the transaction.
    signatures: list[str] = pydantic.Field(
        description="List of signatures (base58)"
    )


class MetaBase(pydantic.BaseModel):
    """
    Common fields for transaction execution metadata.
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
    rewards: list[Reward] | None = pydantic.Field(
        default=None,
        description="Transaction-level rewards (or null)"
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


class Meta(MetaBase):
    """
    Metadata for `encoding="json"` responses.
    Includes loaded addresses and unparsed inner instructions.
    """
    # Optional list of inner instructions (or null if not recorded).
    innerInstructions: list[InnerInstruction] | None = pydantic.Field(
        default=None,
        description="Inner instructions invoked (null if not recorded)"
    )

    # Optional loaded addresses from address lookup tables (if used).
    loadedAddresses: LoadedAddresses | None = pydantic.Field(
        default=None,
        description="Addresses loaded from lookup tables (if used)"
    )

    # Signatures corresponding to transaction order in the block.
    signatures: list[str] | None = pydantic.Field(
        default=None,
        description="Signatures corresponding to transaction order "
                    "in the block"
    )


class JsonParsedMeta(MetaBase):
    """
    Metadata for `encoding="jsonParsed"` responses.
    Does NOT include `loadedAddresses` (per RPC behavior).
    """
    # Optional list of inner instructions (or null if not recorded).
    innerInstructions: list[JsonParsedInnerInstruction] | None = \
        pydantic.Field(
            default=None,
            description="Inner instructions invoked (null if not recorded)")


class Base(pydantic.BaseModel):
    """
    The result of a `getTransaction` and/or `getBlock` RPC requests.
    This shape is a superset that accommodates different `transactionDetails`
    and `encoding` options.
    """
    # Transaction version: 'legacy' or integer (if supported).
    version: str | int | None = pydantic.Field(
        default=None,
        description="Transaction version: 'legacy' or integer (if supported)"
    )

    # Estimated Unix timestamp (or null).
    blockTime: int | None = pydantic.Field(
        default=None,
        description="Estimated Unix timestamp (or null)"
    )

    # Slot in which this transaction was processed.
    slot: int | None = pydantic.Field(
        default=None,
        description="Slot in which this transaction was processed"
    )


class Json(Base):
    """
    Wrapper combining a `json`-encoded transaction with its execution metadata.
    """
    # Transaction object (message + signatures).
    transaction: InnerTransaction = pydantic.Field(
        description="Transaction object (message + signatures)"
    )

    # Metadata about execution (or null if unavailable).
    meta: Meta | None = pydantic.Field(
        description="Metadata about execution (or null if unavailable)"
    )


class JsonParsed(Base):
    """
    Wrapper combining a `jsonParsed`-encoded transaction with its
    execution metadata.
    """
    # Transaction object (message + signatures).
    transaction: JsonParsedInnerTransaction = pydantic.Field(
        description="Transaction object (message + signatures)"
    )

    # Metadata about execution (or null if unavailable).
    meta: JsonParsedMeta | None = pydantic.Field(
        description="Metadata about execution (or null if unavailable)"
    )

# vim: set ts=4 sw=4 expandtab:

