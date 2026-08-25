import uuid


def create_payment(total, payment_method):

    payment_id = "PAY-" + uuid.uuid4().hex[:10].upper()

    return {
        "payment_id": payment_id,
        "amount": total,
        "payment_method": payment_method,
        "status": "SUCCESS"
    }