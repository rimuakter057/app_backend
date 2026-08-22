class PaymentService:
    """Stub payment gateway integration. Swap with a real provider (Stripe, etc.) as needed."""

    async def charge(self, amount: float, currency: str, customer_reference: str) -> dict:
        return {
            "status": "succeeded",
            "amount": amount,
            "currency": currency,
            "customer_reference": customer_reference,
        }
