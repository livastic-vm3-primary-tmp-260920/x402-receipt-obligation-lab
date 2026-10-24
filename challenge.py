"""Synthetic offline training app. No wallets, blockchains, keys, or network calls.

x402-like API receipts are signed by an imaginary payment processor. The
challenge is to detect a trust-boundary error in how the merchant consumes
cryptographically valid receipts across requests. There are no real funds.
"""
from __future__ import annotations

from dataclasses import dataclass
from hashlib import sha256
import hmac
import json

DEMO_KEY = b"secdim-proposal-training-only-not-a-wallet-secret"
CHAINS = {"eip155:8453"}
SINK = "training-shop-usdc-receiver"
OTHER_SINK = "attacker-test-only-receiver"


def body_digest(payload: bytes) -> str:
    return sha256(payload).hexdigest()


@dataclass(frozen=True)
class Receipt:
    order_id: str
    payee: str
    resource: str
    network: str
    amount_micro_usdc: int
    request_digest: str
    expires_at: int
    proof: str


def _receipt_content(order_id: str, payee: str, resource: str,
                     network: str, amount_micro_usdc: int,
                     request_digest: str, expires_at: int) -> bytes:
    obj = {"order_id": order_id, "payee": payee, "resource": resource,
           "network": network, "amount_micro_usdc": amount_micro_usdc,
           "request_digest": request_digest, "expires_at": expires_at}
    return json.dumps(obj, separators=(",", ":"), sort_keys=True).encode()


def processor_issue_receipt(*, order_id: str, payee: str, resource: str,
                            network: str, amount_micro_usdc: int,
                            request_digest: str, expires_at: int) -> Receipt:
    """Simulate an independent payment processor signing a legitimate event.

    This function issues signatures for synthetic events only. It does not
    transfer tokens; never pass an actual wallet secret to this challenge.
    """
    assert amount_micro_usdc >= 0
    msg = _receipt_content(order_id, payee, resource, network,
                           amount_micro_usdc, request_digest, expires_at)
    proof = hmac.digest(DEMO_KEY, msg, "sha256").hex()
    return Receipt(order_id, payee, resource, network, amount_micro_usdc,
                   request_digest, expires_at, proof)


def _processor_signature_valid(receipt: Receipt) -> bool:
    msg = _receipt_content(receipt.order_id, receipt.payee, receipt.resource,
                           receipt.network, receipt.amount_micro_usdc,
                           receipt.request_digest, receipt.expires_at)
    return hmac.compare_digest(receipt.proof, hmac.digest(DEMO_KEY, msg, "sha256").hex())


class PaymentRequired(Exception):
    """Payment not independently proven for this operation."""


class DemoMerchant:
    """One fake merchant with one local paid endpoint. No HTTP or chain calls."""

    def __init__(self) -> None:
        self._consumed_ids: set[str] = set()
        self.delivered: list[str] = []

    def request_report(self, *, resource: str, payload: bytes,
                       receipt: Receipt, time_now: int) -> str:
        required_micro_usdc = 250_000  # 0.25 fake USDC
        if not _processor_signature_valid(receipt):
            raise PaymentRequired("unverifiable synthetic processor proof")
        if receipt.amount_micro_usdc < required_micro_usdc:
            raise PaymentRequired("payment amount too small")
        if receipt.expires_at < time_now:
            raise PaymentRequired("expired")
        # SECURITY CHALLENGE: This validates the processor's signature and
        # amount, but does not ask what obligation that payment settled.
        # Players should derive the missing invariant(s) and make payment
        # proofs single-use without breaking ordinary purchases.
        result = f"report={resource};payload_sha256={body_digest(payload)[:16]}"
        self.delivered.append(result)
        return result
