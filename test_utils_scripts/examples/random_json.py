import json
import random
import os
from datetime import datetime
from faker import Faker

fake = Faker("es_ES") 

VALID_OPERATION_TYPES = ["invoice", "credit", "debit", "note"]
PAYMENT_METHODS = [
    ("01", "Efectivo"),
    ("02", "Tarjeta de Crédito"),
    ("03", "Tarjeta de Débito"),
    ("04", "Transferencia"),
    ("05", "Depósito"),
    ("06", "Cheque"),
    ("07", "Criptomoneda"),
    ("08", "Pago Móvil"),
    ("09", "Crédito Directo"),
    ("10", "Bizum"),
    ("11", "PayPal"),
    ("12", "Dólares Electrónicos"),
    ("13", "Pago Contra Entrega"),
    ("14", "Cuenta Corriente"),
    ("15", "Vale de Compra"),
    ("16", "Pago en Especies"),
    ("17", "Otro"),
    ("18", "Bitcoin"),
    ("19", "Binance Pay"),
    ("20", "Pago QR"),
]


def generate_random_json():
    operation_type = random.choice(VALID_OPERATION_TYPES)

    affected_document = {
        "document_number": fake.bothify("#####-###-####"),
        "document_date": fake.date_this_year().isoformat(),
        "document_serial": fake.bothify("Z0A#######"),
    }

    customer = {
        "customer_vat": fake.bothify("V#########"),
        "customer_name": fake.name(),
        "customer_address": fake.address().replace("\n", ", "),
        "customer_phone": fake.phone_number(),
        "customer_email": fake.email(),
    }

    items = []
    for _ in range(random.randint(1, 5)):
        item = {
            "item_ref": fake.bothify("##-####"),
            "item_name": fake.word().capitalize() + " " + fake.word().capitalize(),
            "item_quantity": random.randint(1, 10),
            "item_price": round(random.uniform(5, 100), 2),
            "item_tax": random.choice([0, 8, 12, 22]),
            "item_discount": round(random.uniform(0, 20), 2),
            "item_discount_type": random.choice(
                ["discount_percentage", "surcharge_percentage", "discount_amount", "surcharge_amount"]
            ),
            "item_comment": fake.sentence(),
        }
        items.append(item)

    total = 0
    for item in items:
        subtotal = item["item_price"] * item["item_quantity"]

        if item["item_discount_type"] == "discount_percentage":
            subtotal *= 1 - item["item_discount"] / 100
        elif item["item_discount_type"] == "surcharge_percentage":
            subtotal *= 1 + item["item_discount"] / 100
        elif item["item_discount_type"] == "discount_amount":
            subtotal -= item["item_discount"]
        else:  # surcharge_amount
            subtotal += item["item_discount"]

        total += subtotal * (1 + item["item_tax"] / 100)

    payments = []
    remaining = round(total, 2)
    num_payments = random.randint(1, 3)

    for i in range(num_payments):
        payment_method = random.choice(PAYMENT_METHODS)
        amount = round(remaining / (num_payments - i), 2) if i != num_payments - 1 else remaining
        payments.append(
            {"payment_method": payment_method[0], "payment_name": payment_method[1], "payment_amount": amount}
        )
        remaining -= amount

    json_data = {
        "operation_type": operation_type,
        "operation_metadata": {
            "terminal_id": fake.bothify("T###"),
            "branch_code": fake.bothify("SUC###"),
            "operator_id": fake.bothify("OP###"),
        },
        "affected_document": affected_document,
        "customer": customer,
        "document": {
            "document_number": fake.bothify("#####-###-####"),
            "document_date": datetime.now().strftime("%Y-%m-%d"),
            "document_name": f"Shop/{fake.bothify('####')}",
            "document_cashier": fake.first_name(),
        },
        "items": items,
        "payments": payments,
        "delivery": {
            "delivery_comments": [fake.sentence() for _ in range(random.randint(0, 3))],
            "delivery_barcode": fake.bothify("150025-####"),
        },
    }

    return json_data


def save_json_to_file(json_data, output_dir="documents"):
    os.makedirs(output_dir, exist_ok=True)
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    filename = f"document_{timestamp}_{json_data['document']['document_number']}.json"

    with open(os.path.join(output_dir, filename), "w", encoding="utf-8") as f:
        json.dump(json_data, f, ensure_ascii=False, indent=4)


for _ in range(5):
    doc = generate_random_json()
    save_json_to_file(doc)
