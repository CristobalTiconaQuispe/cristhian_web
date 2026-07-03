import urllib.parse
from flask import Blueprint, render_template, session, request, redirect, url_for
from models import Producto

cart_bp = Blueprint('cart', __name__)


@cart_bp.route('/carrito')
def ver_carrito():
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

    mensaje = _generar_mensaje_whatsapp(items, total)

    return render_template('carrito.html', items=items, total=total, mensaje_whatsapp=mensaje)


def _generar_mensaje_whatsapp(items, total):
    lineas = ['¡Hola! Quiero hacer un pedido:']
    for item in items:
        lineas.append(
            f"• {item['producto'].nombre} × {item['cantidad']} - "
            f"Bs. {item['subtotal']:.2f}"
        )
    lineas.append(f"Total del pedido: Bs. {total:.2f}")
    return urllib.parse.quote('\n'.join(lineas))


@cart_bp.route('/carrito/agregar/<int:producto_id>', methods=['POST'])
def agregar(producto_id):
    Producto.query.get_or_404(producto_id)
    carrito = session.get('carrito', {})

    str_id = str(producto_id)
    if str_id in carrito:
        carrito[str_id] += 1
    else:
        carrito[str_id] = 1

    session['carrito'] = carrito
    return redirect(request.referrer or url_for('main.catalogo'))


@cart_bp.route('/carrito/actualizar/<int:producto_id>', methods=['POST'])
def actualizar(producto_id):
    try:
        cantidad = int(request.form.get('cantidad', 1))
    except (ValueError, TypeError):
        cantidad = 1
    cantidad = max(0, min(cantidad, 100))
    carrito = session.get('carrito', {})

    if cantidad > 0:
        carrito[str(producto_id)] = cantidad
    else:
        carrito.pop(str(producto_id), None)

    session['carrito'] = carrito
    return redirect(url_for('cart.ver_carrito'))


@cart_bp.route('/carrito/eliminar/<int:producto_id>', methods=['POST'])
def eliminar(producto_id):
    carrito = session.get('carrito', {})
    carrito.pop(str(producto_id), None)
    session['carrito'] = carrito
    return redirect(url_for('cart.ver_carrito'))
