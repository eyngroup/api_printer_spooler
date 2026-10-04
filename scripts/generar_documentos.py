import json
import random
import string
from datetime import datetime

def random_string(length, chars=string.ascii_uppercase + string.digits):
    return ''.join(random.choice(chars) for _ in range(length))

def random_phone():
    return f"+58 4{random.choice(['14', '24', '12', '16'])}-{random.randint(1000000, 9999999)}"

def random_address():
    # Calles y referencias comunes
    streets = ["Av. Bolivar", "Calle 23", "Av. Principal", "Calle Los Proceres", "Av. Miranda", 
               "Calle 85", "Av. Universidad", "Calle Comercio", "Av. Libertador", "Calle 52"]
    references = ["frente al parque", "al lado del supermercado", "cerca de la plaza", 
                  "detrás del banco", "junto al centro comercial", "frente a la escuela",
                  "al lado de la farmacia", "cerca del hospital", "detrás de la iglesia"]
    cities = ["Caracas", "Maracaibo", "Valencia", "Barquisimeto", "Maracay", 
              "Ciudad Guayana", "San Cristobal", "Maturin", "Barcelona", "Merida"]
    
    # Generar componentes aleatorios
    street = random.choice(streets)
    number = random.randint(100, 9999)
    reference = random.choice(references)
    city = random.choice(cities)
    zip_code = f"{random.randint(1000, 9999)}"
    
    # Variar la longitud de la dirección
    address_type = random.choice(["short", "medium", "long"])
    
    if address_type == "short":
        # Dirección corta (~30-40 chars)
        address = f"DIRECCION: {street} #{number}, {city}"
    elif address_type == "medium":
        # Dirección media (~60-80 chars)
        address = f"DIRECCION: {street} #{number}, {reference}, {city}"
    else:
        # Dirección larga (~100-120 chars)
        urbanization = random_string(8, string.ascii_uppercase)
        address = f"DIRECCION: Urb. {urbanization}, {street} #{number}, {reference}, {city}, {zip_code}"
    
    return address

def random_customer_name():
    # Nombres de personas comunes
    first_names = ["MARIA", "JOSE", "JUAN", "ANA", "CARLOS", "LUIS", "CARMEN", "PEDRO", 
                   "ROSA", "MANUEL", "BEATRIZ", "MIGUEL", "TERESA", "RAFAEL", "SOFIA"]
    last_names = ["GONZALEZ", "RODRIGUEZ", "PEREZ", "MARTINEZ", "GARCIA", "LOPEZ", 
                  "DIAZ", "SANCHEZ", "RAMIREZ", "TORRES", "FERNANDEZ", "JIMENEZ"]
    
    # Nombres de empresas
    companies = ["SERVICIOS TECNICOS C.A.", "COMERCIALIZADORA INTERNACIONAL", 
                 "INDUSTRIAS METALURGICAS S.A.", "DISTRIBUIDORA NACIONAL C.A.",
                 "CONSTRUCTORA DEL CARIBE", "ALIMENTOS PROCESADOS INDUSTRIAL",
                 "TECNOLOGIA Y SOLUCIONES INTEGRAL", "IMPORTADORA Y EXPORTADORA VENEZOLANA"]
    
    # Elegir entre persona o empresa
    if random.random() < 0.6:  # 60% personas, 40% empresas
        # Persona física
        name = f"CLIENTE: {random.choice(first_names)} {random.choice(last_names)}"
    else:
        # Empresa
        name = f"CLIENTE: {random.choice(companies)}"
    
    return name

def random_doc_reference():
    # Tipos de referencias con formatos realistas
    ref_types = [
        # Pedidos (PED-00001 a PED-99999)
        lambda: f"PED-{random.randint(1, 99999):05d}",
        # Órdenes de compra (OC-000001 a OC-999999)
        lambda: f"OC-{random.randint(1, 999999):06d}",
        # Cotizaciones (COT-0001 a COT-9999)
        lambda: f"COT-{random.randint(1, 9999):04d}",
        # Referencias alfanuméricas (REF + 3 letras + 4 números)
        lambda: f"REF{random_string(3, string.ascii_uppercase)}{random.randint(1000, 9999)}",
        # Facturas anteriores (FAC-000001 a FAC-999999)
        lambda: f"FAC-{random.randint(1, 999999):06d}",
        # Notas de entrega (NE-0001 a NE-9999)
        lambda: f"NE-{random.randint(1, 9999):04d}"
    ]
    return random.choice(ref_types)()

def random_item_name():
    # Nombres de productos realistas
    products = [
        "Laptop HP Pavilion 15.6\"",
        "Monitor Samsung 24\" LED",
        "Mouse Logitech USB",
        "Teclado Mecánico RGB",
        "Impresora Epson L3150",
        "Disco Duro Externo 1TB",
        "Memoria RAM 8GB DDR4",
        "Router WiFi TP-Link",
        "USB 32GB SanDisk",
        "Auriculares Bluetooth",
        "Webcam HD 1080p",
        "Silla de Oficina Ergonómica",
        "Escritorio 120x60cm",
        "Toner HP LaserJet",
        "Cable HDMI 2m",
        "Batería Portátil 10000mAh",
        "Parlante Bluetooth JBL",
        "Tablet 10\" WiFi",
        "Smartphone Android",
        "Diskette 3.5\""
    ]
    return random.choice(products)

def random_business_email():
    # Correos electrónicos de negocios realistas
    companies = ["empresa", "negocio", "corporacion", "industria", "servicios", 
                 "comercial", "importadora", "exportadora", "distribuidora", "tecnologia"]
    domains = ["gmail.com", "yahoo.com", "outlook.com", "hotmail.com", 
               "empresa.com", "corporacion.net", "servicios.org", "tecnologia.io"]
    
    if random.random() < 0.7:  # 70% con formato nombre@empresa
        return f"{random.choice(['contacto', 'info', 'ventas', 'admin', 'soporte'])}@{random.choice(companies)}{random.choice(['.com', '.net', '.org', '.ve'])}"
    else:  # 30% con formato personal
        return f"{random_string(6, string.ascii_lowercase)}@{random.choice(domains)}"

def generar_documentos():
    doc_date = datetime.now().strftime("%Y-%m-%d")

    # Valores aleatorios
    customer_name = random_customer_name()
    customer_address = random_address()
    customer_phone = random_phone()
    customer_email = random_business_email()
    document_number = ''.join(random.choice(string.digits) for _ in range(10))
    doc_refs = ["OC-" + random_string(5), "PED-" + random_string(5), "COT-" + random_string(5)]
    doc_reference = random_doc_reference()
    document_cashier = "Cajero " + random.choice(["Juan", "Pedro", "Maria", "Ana", "Luis"])
    item_ref = random_string(3, string.ascii_uppercase) + "-" + random_string(4, string.digits)
    item_name = random_item_name()
    delivery_barcode = "CODE128-" + random_string(10)
    terminal_id = random_string(12, string.ascii_lowercase + string.digits)
    branch_code = random_string(5, string.ascii_uppercase)
    operator_id = random_business_email()

    # Valores fijos o controlados para evitar líos con la memoria fiscal
    item_quantity = 1
    item_price = round(random.uniform(0.1, 10.0), 2)
    tax_rate = 16
    total_with_tax = round(item_price * item_quantity * (1 + tax_rate / 100), 2)

    # Plantilla base sacada de factura.json
    data = {
      "operation_type": "invoice",
      "affected_document": {
        "affected_number": "00000000",
        "affected_date": "2026-03-24",
        "affected_serial": "Z7C1234567"
      },
      "customer": {
        "customer_vat": "J-1234567-0",
        "customer_name": customer_name,
        "customer_address": customer_address,
        "customer_phone": customer_phone,
        "customer_email": customer_email
      },
      "document": {
        "document_number": document_number,
        "document_date": doc_date,
        "document_name": "FACTURA DE PRUEBA",
        "doc_reference": doc_reference,
        "document_cashier": document_cashier
      },
      "items": [
        {
          "item_ref": item_ref,
          "item_name": item_name,
          "item_quantity": item_quantity,
          "item_price": item_price,
          "item_tax": tax_rate,
          "item_discount": 0,
          "item_discount_type": "discount_percentage",
          "item_comment": ""
        }
      ],
      "payments": [
        {
          "payment_method": f"{random.randint(1, 19):02d}",
          "payment_name": "CONTADO",
          "payment_amount": total_with_tax
        }
      ],
      "delivery": {
        "delivery_comments": [],
        "delivery_barcode": delivery_barcode
      },
      "operation_metadata": {
        "terminal_id": terminal_id,
        "branch_code": branch_code,
        "operator_id": operator_id,
        "currency_code": "VEF",
        "exchange_rate": 1,
        "inverse_rate": 1
      }
    }

    # 1. Generar Factura
    with open('factura.json', 'w') as f:
        json.dump(data, f, indent=2)

    # 2. Generar Crédito y Débito
    data["affected_document"]["affected_date"] = doc_date
    
    # - Crédito
    data["operation_type"] = "credit"
    data["document"]["document_name"] = "NOTA DE CREDITO DE PRUEBA"
    with open('credito.json', 'w') as f:
        json.dump(data, f, indent=2)

    # - Débito
    data["operation_type"] = "debit"
    data["document"]["document_name"] = "NOTA DE DEBITO DE PRUEBA"
    with open('debito.json', 'w') as f:
        json.dump(data, f, indent=2)

    print(f"Archivos generados correctamente: factura.json, credito.json, debito.json (Total: {total_with_tax})")

if __name__ == '__main__':
    generar_documentos()
