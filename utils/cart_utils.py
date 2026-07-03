import urllib.parse
from models import Producto


def obtener_items_carrito(session):
    carrito = session.get('carrito', {})
    items = []
    total = 0

    for producto_id, cantidad in carrito.items():
        producto = Producto.query.get(int(producto_id))
        if producto:
            subtotal = producto.precio * cantidad
            total += subtotal
            items.append({
                'producto': producto,
                'cantidad': cantidad,
                'subtotal': subtotal
            })

    return items, total


def generar_mensaje_whatsapp(items, total):
    lineas = ['¡Hola! Quiero hacer un pedido:']
    for item in items:
        lineas.append(
            f"• {item['producto'].nombre} × {item['cantidad']} - "
            f"Bs. {item['subtotal']:.2f}"
        )
    lineas.append(f"Total del pedido: Bs. {total:.2f}")
    return urllib.parse.quote('\n'.join(lineas))
