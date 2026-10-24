# Quote ≠ Paid Authorization: synthetic x402 receipt-context challenge (proposal)

**Status: PROPOSAL, not SecDim-approved, not an official SecDim challenge.** This
educational Python 3.12 sandbox is original, all-fake and deliberately vulnerable.
It does not connect to a chain, use a private wallet key, sign user transactions,
run a remote API, or touch real token balances. No paid or free actual purchase occurs.

## Security concept

A valid third-party payment processor signature authenticates **the payment
event**, but it is not automatically authorization to supply any requested
merchant resource. A merchant should independently match the receipt to the
correct merchant payee, chain and asset, HTTP resource and request body, quoted
price, and a one-time obligation. A signature is necessary but not sufficient.

The challenge includes a minimal service and processor to reproduce a multi-hop
**confused-deputy / payment-context binding** failure.

## Reproduction (no pip install)

Requirements: Python 3.10+ with standard library only.

```sh
python3 -m unittest -v tests.test_usability
python3 -m unittest -v tests.test_security
```

Expected for deliberately vulnerable `main`:

- Usability tests: **4 PASS**.
- Security tests: **5 FAIL**. Each failed defense assertion exposes a
  genuinely distinct operation admitted with an otherwise authentic payment
  processor receipt that is not valid for that requested obligation.
- After a correct defense, usability **4 PASS** + security **5 PASS**.

## Rules for the solver

Patch `DemoMerchant.request_report` without weakening the synthetic processor
signature check. Preserve ordinary new independent purchases, reject repeat
obligations, and ensure receipt context actually matches the requested
resource, payload and merchant. Enforce network. Do not add dependencies.

## Trust & originality boundaries

No claim that this demonstrates an exploit on any deployed x402 vendor, wallet,
real payment processor or SecDim deployment. Inputs, receipts, signers, payees,
balances and API responses are synthetic. AI-assisted preparation and tests
must be disclosed to any paying publisher; a real human remains the sole
beneficial operator. Acceptance and cash reward are subject to SecDim's written
preapproval and review. No income is booked on a draft proposal.
