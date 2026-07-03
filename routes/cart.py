from flask import Blueprint, render_template, session, request, redirect, url_for
from models import Producto
from utils.cart_utils import obtener_items_carrito, generar_mensaje_whatsapp

cart_bp = Blueprint('cart', __name__)


@cart_bp.route('/carrito')
def ver_carrito():
    items, total = obtener_items_carrito(session)
    mensaje = generar_mensaje_whatsapp(items, total)
    return render_template('carrito.html', items=items, total=total, mensaje_whatsapp=mensaje)


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
