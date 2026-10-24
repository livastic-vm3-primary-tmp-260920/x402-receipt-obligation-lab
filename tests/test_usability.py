import unittest

from challenge import (
    DEMO_KEY, OTHER_SINK, SINK, DemoMerchant, PaymentRequired,
    body_digest, processor_issue_receipt, Receipt,
)


def valid_receipt(resource="/reports/demo", body=b"{\"team\":\"example\"}",
                  order_id="test-order-A", payee=SINK,
                  network="eip155:8453", amount=250_000, expiration=200):
    return processor_issue_receipt(
        order_id=order_id, payee=payee, resource=resource, network=network,
        amount_micro_usdc=amount, request_digest=body_digest(body),
        expires_at=expiration,
    )


class Usability(unittest.TestCase):
    def test_valid_paid_operation(self):
        m = DemoMerchant()
        body = b'{"team":"example"}'
        s = m.request_report(resource="/reports/demo", payload=body,
                             receipt=valid_receipt(body=body), time_now=100)
        self.assertEqual(s, "report=/reports/demo;payload_sha256=" + body_digest(body)[:16])

    def test_two_independent_purchases_still_work(self):
        m = DemoMerchant()
        body = b"{}"
        for n in (1, 2):
            receipt = valid_receipt(order_id=f"new-order-{n}", body=body)
            self.assertIn("report=/reports/demo", m.request_report(
                resource="/reports/demo", payload=body, receipt=receipt, time_now=100))
        self.assertEqual(len(m.delivered), 2)

    def test_unsigned_receipt_rejected(self):
        r = valid_receipt()
        tampered = Receipt(r.order_id, r.payee, r.resource, r.network,
                           r.amount_micro_usdc, r.request_digest, r.expires_at, "00"*32)
        with self.assertRaises(PaymentRequired):
            DemoMerchant().request_report(resource="/reports/demo", payload=b'{"team":"example"}',
                                          receipt=tampered, time_now=100)

    def test_underpayment_and_expired_receipt_rejected(self):
        m = DemoMerchant()
        with self.assertRaises(PaymentRequired):
            m.request_report(resource="/reports/demo", payload=b"{}",
                             receipt=valid_receipt(body=b"{}", amount=249_999), time_now=100)
        with self.assertRaises(PaymentRequired):
            m.request_report(resource="/reports/demo", payload=b"{}",
                             receipt=valid_receipt(body=b"{}", expiration=90), time_now=100)


if __name__ == "__main__":
    unittest.main()
