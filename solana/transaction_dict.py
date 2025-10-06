# Copyright (c) 2025 The Suckless Solana Python developers
# Distributed under the MIT software license, see the accompanying
# file COPYING or https://opensource.org/license/mit/.

from typing import Any, Literal, NotRequired, TypedDict


class ReturnData(TypedDict, total=True):
    """
    Represents the “returnData” from an instruction, if present.
    """
    # Tuple [data, encoding], where data is base64-encoded.
    data: tuple[str, str] | list[str]

    # Program that returned the data (pubkey).
    programId: str


class TokenAmount(TypedDict, total=True):
    """
    UI-friendly token amount object used in token balances.
    Mirrors Anza's `TokenAmount`
    (StringifiedBigInt/Number in TS become strings here).
    """
    # Raw amount of tokens as a string (ignoring decimals).
    amount: str

    # Number of decimals configured for the token's mint.
    decimals: int

    # Token amount as a string (accounting for decimals).
    uiAmountString: str

    # Deprecated: Token amount as a float (may be null).
    uiAmount: float | None


class TokenBalance(TypedDict, total=True):
    """
    Represents a token balance entry before or after the transaction.
    Mirrors Anza's `TokenBalance`.
    """
    # Index of the account in the transaction's message.accountKeys.
    accountIndex: int

    # Mint address (token mint pubkey).
    mint: str

    # Owner address of the token account (may be undefined in some cases).
    owner: NotRequired[str]

    # Program ID of the Token program owning the account (may be undefined).
    programId: NotRequired[str]

    # UI-friendly token amount object.
    uiTokenAmount: TokenAmount


class Reward(TypedDict, total=True):
    """
    Transaction-level reward (fee, rent, voting, staking).
    """
    # Account that received the reward (base58 pubkey).
    pubkey: str

    # Lamports credited/debited as a signed i64.
    lamports: int

    # Account balance in lamports after applying the reward.
    postBalance: int

    # Type of reward: 'fee' | 'rent' | 'voting' | 'staking'
    rewardType: NotRequired[Literal['fee', 'rent', 'voting', 'staking']]

    # Vote account commission when credited (if applicable).
    commission: NotRequired[int]


class LoadedAddresses(TypedDict, total=True):
    """
    Represents addresses loaded from address lookup tables (if used).
    """
    # Ordered list of readonly loaded addresses (pubkeys).
    readonly: list[str]

    # Ordered list of writable loaded addresses (pubkeys).
    writable: list[str]


class MessageHeader(TypedDict, total=True):
    """
    Header metadata for the transaction message.
    (Present for `encoding='json'` messages.)
    """
    # Number of required signatures for this transaction.
    numRequiredSignatures: int

    # Number of signed accounts that are read-only.
    numReadonlySignedAccounts: int

    # Number of unsigned accounts that are read-only.
    numReadonlyUnsignedAccounts: int


class AddressTableLookup(TypedDict, total=True):
    """
    str lookup from on-chain account lookup tables (optional).
    Mirrors Anza's `AddressTableLookup`.
    """
    # Pubkey of the address lookup table account.
    accountKey: str

    # Indices loaded as readonly from table.
    readonlyIndexes: list[int]

    # Indices loaded as writable from table.
    writableIndexes: list[int]


class Instruction(TypedDict, total=True):
    """
    Represents a single (unparsed) instruction in a transaction
    (or inner instruction). Mirrors Anza `TransactionInstruction` shape
    when `encoding="json"`.
    """
    # Indices of accounts passed to this instruction (into accountKeys).
    accounts: list[int]

    # Instruction input data (base58-encoded).
    data: str

    # Index into accountKeys for the program executing this instruction.
    programIdIndex: int

    # Optional stack height hint (if supported).
    stackHeight: int | None


class RawInstruction(TypedDict, total=True):
    """
    Raw (partially decoded) instruction entry when using `jsonParsed` encoding.
    Mirrors Anza's `PartiallyDecodedTransactionInstruction`.
    """
    # Account pubkeys referenced by this instruction.
    accounts: list[str]

    # Instruction input data (base58-encoded).
    data: str

    # Program ID (pubkey).
    programId: str

    # Optional stack height hint (if supported).
    stackHeight: int | None


class ProgramParsed(TypedDict, total=True):
    """
    Program-specific parsed instruction payload.
    Mirrors Anza's `ParsedTransactionInstruction.parsed` object.
    """
    # Instruction type (e.g., 'transfer').
    type: str

    # Program-specific parsed fields.
    info: NotRequired[dict[str, Any]]


class ParsedProgramInstruction(TypedDict, total=True):
    """
    Parsed program instruction entry for `encoding="jsonParsed"`.
    Mirrors Anza's `ParsedTransactionInstruction`.
    """
    # Program name (e.g., 'system', 'spl-token').
    program: str

    # Program ID (pubkey).
    programId: str

    # Program-specific parsed data (object or primitive).
    parsed: ProgramParsed | str | int | None

    # Optional stack height hint (if supported).
    stackHeight: int | None


class InnerInstruction(TypedDict, total=True):
    """
    Represents inner instructions invoked by a top-level instruction
    for `encoding="json"` responses.
    Mirrors Anza's unparsed inner instructions entry.
    """
    # Index of the top-level instruction originating these inner instructions.
    index: int

    # List of inner instructions invoked.
    instructions: list[Instruction]


class JsonParsedInnerInstruction(TypedDict, total=True):
    """
    Inner instruction wrapper (jsonParsed) holding mixed parsed/raw entries.
    Mirrors Anza's parsed inner instructions entry.
    """
    # Index of the top-level instruction originating these inner instructions.
    index: int

    # List of inner instructions (parsed or raw).
    instructions: list[ParsedProgramInstruction | RawInstruction]


class Message(TypedDict, total=True):
    """
    The message part of a Solana transaction (defines accounts, etc)
    for `encoding="json"` responses.
    """
    # List of public keys (base58) used by this transaction.
    accountKeys: list[str]

    # Header that describes signature & account properties.
    header: MessageHeader

    # List of program instructions to execute.
    instructions: list[Instruction]

    # Recent blockhash used by this transaction.
    recentBlockhash: str

    # Optional address lookup table entries (if used).
    addressTableLookups: NotRequired[list[AddressTableLookup]]


class InnerTransaction(TypedDict, total=True):
    """
    A Solana transaction wrapper including message & signatures
    for `encoding="json"` responses.
    """
    # Message object containing accounts and instructions.
    message: Message

    # List of signatures (base58), length = numRequiredSignatures.
    signatures: list[str]


class ParsedAccountKey(TypedDict, total=True):
    """
    Account key entry with signer/writable flags for `encoding="jsonParsed"`.
    """
    # Account pubkey (base58).
    pubkey: str

    # Whether the account is a signer.
    signer: bool

    # Whether the account is writable.
    writable: bool

    # Source of the account: 'transaction' or 'lookupTable'
    source: Literal["transaction", "lookupTable"]


class JsonParsedMessage(TypedDict, total=True):
    """
    The message part of a Solana transaction for `encoding="jsonParsed"`.
    """
    # Account entries with signer/writable/source flags.
    accountKeys: list[ParsedAccountKey]

    # List of program instructions (parsed or raw).
    instructions: list[ParsedProgramInstruction | RawInstruction]

    # Recent blockhash used by this transaction.
    recentBlockhash: str

    # Optional address lookup table entries (if used).
    addressTableLookups: NotRequired[list[AddressTableLookup]]


class JsonParsedInnerTransaction(TypedDict, total=True):
    """
    A Solana transaction wrapper including message & signatures
    for `encoding="jsonParsed"` responses.
    """
    # Parsed message object containing accounts and instructions.
    message: JsonParsedMessage

    # List of signatures (base58).
    signatures: list[str]


class MetaBase(TypedDict, total=True):
    """
    Common fields for transaction execution metadata.
    """
    # Error object if failed, null if succeeded.
    err: Any | None

    # Fee the transaction was charged, in lamports.
    fee: int

    # Account balances before execution.
    preBalances: list[int]

    # Account balances after execution.
    postBalances: list[int]

    # Token balances before execution (if enabled).
    preTokenBalances: NotRequired[list[TokenBalance]]

    # Token balances after execution (if enabled).
    postTokenBalances: NotRequired[list[TokenBalance]]

    # Logs emitted during execution (null if not recorded).
    logMessages: list[str] | None

    # Transaction-level rewards (or null).
    rewards: list[Reward] | None

    # Return data from instruction (if any).
    returnData: NotRequired[ReturnData]

    # Compute units consumed during execution (if supported).
    computeUnitsConsumed: NotRequired[int]


class Meta(MetaBase):
    """
    Metadata for `encoding="json"` responses.
    Includes loaded addresses and unparsed inner instructions.
    """
    # Inner instructions invoked (null if not recorded).
    innerInstructions: list[InnerInstruction] | None

    # Addresses loaded from lookup tables (if used).
    loadedAddresses: NotRequired[LoadedAddresses]

    # Signatures corresponding to transaction order in the block.
    signatures: NotRequired[list[str]]


class JsonParsedMeta(MetaBase):
    """
    Metadata for `encoding="jsonParsed"` responses.
    Does NOT include `loadedAddresses` (per RPC behavior).
    """
    # Inner instructions invoked (null if not recorded).
    innerInstructions: list[JsonParsedInnerInstruction] | None


class Base(TypedDict, total=True):
    """
    The result of a `getTransaction` and/or `getBlock` RPC requests.
    This shape is a superset that accommodates different `transactionDetails`
    and `encoding` options.
    """
    # Transaction version: 'legacy' or integer (if supported).
    version: NotRequired[str | int]

    # Estimated Unix timestamp (or null).
    blockTime: int | None

    # Slot in which this transaction was processed.
    slot: NotRequired[int]


class Json(Base):
    """
    Wrapper combining a `json`-encoded transaction with its execution metadata.
    """
    # Transaction object (message + signatures).
    transaction: InnerTransaction

    # Metadata about execution (or null if unavailable).
    meta: Meta | None


class JsonParsed(Base):
    """
    Wrapper combining a `jsonParsed`-encoded transaction with its
    execution metadata.
    """
    # Transaction object (message + signatures).
    transaction: JsonParsedInnerTransaction

    # Metadata about execution (or null if unavailable).
    meta: JsonParsedMeta | None

# vim: set ts=4 sw=4 expandtab:

