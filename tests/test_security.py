"""Defense assertions: SHOULD FAIL on the supplied vulnerable baseline.

After a correct patch, all five checks must pass while usability still passes.
No tokens move, and neither test depends on any remote service.
"""
import unittest
from challenge import (SINK, OTHER_SINK, DemoMerchant, PaymentRequired,
                       body_digest, processor_issue_receipt)


def proof(*, resource="/reports/demo", body=b"sample", order_id="order-A",
          payee=SINK, network="eip155:8453"):
    return processor_issue_receipt(
        order_id=order_id, payee=payee, resource=resource,
        network=network, amount_micro_usdc=250_000,
        request_digest=body_digest(body), expires_at=200
    )


class Security(unittest.TestCase):
    def test_one_invoice_must_not_buy_two_deliveries(self):
        merchant = DemoMerchant()
        receipt = proof()
        merchant.request_report(resource="/reports/demo", payload=b"sample",
                                receipt=receipt, time_now=100)
        with self.assertRaises(PaymentRequired):
            merchant.request_report(resource="/reports/demo", payload=b"sample",
                                    receipt=receipt, time_now=100)

    def test_payment_for_another_payee_is_not_payment_to_this_merchant(self):
        receipt = proof(payee=OTHER_SINK)
        with self.assertRaises(PaymentRequired):
            DemoMerchant().request_report(resource="/reports/demo", payload=b"sample",
                                          receipt=receipt, time_now=100)

    def test_wrong_service_path_cannot_share_proof(self):
        receipt = proof(resource="/reports/demo")
        with self.assertRaises(PaymentRequired):
            DemoMerchant().request_report(resource="/reports/another-team",
                                          payload=b"sample", receipt=receipt, time_now=100)

    def test_wrong_request_body_cannot_share_proof(self):
        receipt = proof(body=b"sample")
        with self.assertRaises(PaymentRequired):
            DemoMerchant().request_report(resource="/reports/demo", payload=b"other",
                                          receipt=receipt, time_now=100)

    def test_wrong_payment_network_is_not_acceptable(self):
        receipt = proof(network="eip155:1")
        with self.assertRaises(PaymentRequired):
            DemoMerchant().request_report(resource="/reports/demo", payload=b"sample",
                                          receipt=receipt, time_now=100)


if __name__ == "__main__":
    unittest.main()
