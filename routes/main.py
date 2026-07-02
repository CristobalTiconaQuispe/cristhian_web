from flask import Blueprint, render_template, request, flash, redirect, url_for
from models import Producto, Categoria

main_bp = Blueprint('main', __name__)


@main_bp.route('/')
def index():
    destacados = Producto.query.filter_by(destacado=True).order_by(
        Producto.fecha_creacion.desc()
    ).limit(6).all()
    return render_template('inicio.html', destacados=destacados)


@main_bp.route('/catalogo')
def catalogo():
    categoria_id = request.args.get('categoria', type=int)
    if categoria_id:
        productos = Producto.query.filter_by(categoria_id=categoria_id).order_by(
            Producto.fecha_creacion.desc()
        ).all()
    else:
        productos = Producto.query.order_by(Producto.fecha_creacion.desc()).all()

    categorias = Categoria.query.order_by(Categoria.nombre).all()
    return render_template(
        'catalogo.html',
        productos=productos,
        categorias=categorias,
        categoria_seleccionada=categoria_id
    )


@main_bp.route('/producto/<int:id>')
def producto_detalle(id):
    producto = Producto.query.get_or_404(id)
    return render_template('producto_detalle.html', producto=producto)


@main_bp.route('/nosotros')
def nosotros():
    return render_template('nosotros.html')


@main_bp.route('/contacto', methods=['GET', 'POST'])
def contacto():
    if request.method == 'POST':
        nombre = request.form.get('nombre', '').strip()
        email = request.form.get('email', '').strip()
        mensaje = request.form.get('mensaje', '').strip()
        if nombre and mensaje:
            flash('¡Gracias por contactarnos! Te responderemos pronto.', 'success')
        else:
            flash('Por favor completa los campos obligatorios.', 'error')
        return redirect(url_for('main.contacto'))
    return render_template('contacto.html')
