from flask import Blueprint, render_template, redirect, url_for, request, flash
from flask_login import login_user, logout_user, login_required, current_user
from sqlalchemy import func
from models import db, Admin, Producto, Categoria
from forms import ProductoForm, LoginForm
from utils.image_utils import guardar_imagenes, eliminar_imagenes
from utils.categoria_utils import populate_categoria_choices

admin_bp = Blueprint('admin', __name__, url_prefix='/admin')


@admin_bp.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('admin.dashboard'))

    form = LoginForm()
    if form.validate_on_submit():
        admin = Admin.query.filter_by(username=form.username.data).first()
        if admin and admin.check_password(form.password.data):
            login_user(admin)
            flash(f'Bienvenido {admin.username}', 'success')
            return redirect(url_for('admin.dashboard'))
        flash('Usuario o contraseña incorrectos', 'error')

    return render_template('admin/login.html', form=form)


@admin_bp.route('/logout')
@login_required
def logout():
    logout_user()
    flash('Sesión cerrada correctamente', 'success')
    return redirect(url_for('main.index'))


@admin_bp.route('/dashboard')
@login_required
def dashboard():
    total_productos = Producto.query.count()
    total_categorias = Categoria.query.count()
    ultimos = Producto.query.order_by(Producto.fecha_creacion.desc()).limit(5).all()
    return render_template(
        'admin/dashboard.html',
        total_productos=total_productos,
        total_categorias=total_categorias,
        ultimos=ultimos
    )


@admin_bp.route('/productos')
@login_required
def lista_productos():
    productos = Producto.query.order_by(Producto.fecha_creacion.desc()).all()
    return render_template('admin/productos.html', productos=productos)


@admin_bp.route('/producto/nuevo', methods=['GET', 'POST'])
@login_required
def nuevo_producto():
    form = ProductoForm()
    populate_categoria_choices(form)

    if form.validate_on_submit():
        cat_id = form.categoria_id.data or None
        producto = Producto(
            nombre=form.nombre.data,
            descripcion=form.descripcion.data,
            precio=form.precio.data,
            categoria_id=cat_id,
            destacado=form.destacado.data
        )
        producto.imagenes = guardar_imagenes(form)

        db.session.add(producto)
        db.session.commit()
        flash('Producto creado exitosamente', 'success')
        return redirect(url_for('admin.lista_productos'))

    return render_template('admin/producto_form.html', form=form, titulo='Nuevo Producto')


@admin_bp.route('/producto/<int:id>/editar', methods=['GET', 'POST'])
@login_required
def editar_producto(id):
    producto = Producto.query.get_or_404(id)
    form = ProductoForm(obj=producto)
    populate_categoria_choices(form)

    if form.validate_on_submit():
        producto.nombre = form.nombre.data
        producto.descripcion = form.descripcion.data
        producto.precio = form.precio.data
        producto.categoria_id = form.categoria_id.data or None
        producto.destacado = form.destacado.data

        nuevas = guardar_imagenes(form)
        if nuevas:
            eliminar_imagenes(producto)
            producto.imagenes = nuevas

        db.session.commit()
        flash('Producto actualizado exitosamente', 'success')
        return redirect(url_for('admin.lista_productos'))

    return render_template('admin/producto_form.html', form=form, titulo='Editar Producto')


@admin_bp.route('/producto/<int:id>/eliminar', methods=['POST'])
@login_required
def eliminar_producto(id):
    producto = Producto.query.get_or_404(id)
    eliminar_imagenes(producto)
    db.session.delete(producto)
    db.session.commit()
    flash('Producto eliminado correctamente', 'success')
    return redirect(url_for('admin.lista_productos'))


@admin_bp.route('/categorias')
@login_required
def lista_categorias():
    resultados = db.session.query(
        Categoria,
        func.count(Producto.id).label('total')
    ).outerjoin(Producto, Categoria.id == Producto.categoria_id).group_by(Categoria.id).all()

    categorias = []
    for cat, total in resultados:
        cat.total_productos = total
        categorias.append(cat)

    sin_categoria = Producto.query.filter_by(categoria_id=None).count()
    return render_template('admin/categorias.html', categorias=categorias, sin_categoria=sin_categoria)


@admin_bp.route('/categoria/crear', methods=['POST'])
@login_required
def crear_categoria():
    nombre = request.form.get('nombre', '').strip()
    if not nombre:
        flash('El nombre de la categoría es obligatorio', 'error')
        return redirect(url_for('admin.lista_categorias'))

    existe = Categoria.query.filter_by(nombre=nombre).first()
    if existe:
        flash(f'La categoría "{nombre}" ya existe', 'error')
        return redirect(url_for('admin.lista_categorias'))

    categoria = Categoria(nombre=nombre)
    db.session.add(categoria)
    db.session.commit()
    flash(f'Categoría "{nombre}" creada exitosamente', 'success')
    return redirect(url_for('admin.lista_categorias'))


@admin_bp.route('/categoria/<int:id>/eliminar', methods=['POST'])
@login_required
def eliminar_categoria(id):
    categoria = Categoria.query.get_or_404(id)
    productos_asociados = Producto.query.filter_by(categoria_id=id).count()

    if productos_asociados > 0:
        flash(
            f'No se puede eliminar "{categoria.nombre}": tiene {productos_asociados} producto(s) asociado(s). '
            f'Reasigna o elimina los productos primero.',
            'error'
        )
        return redirect(url_for('admin.lista_categorias'))

    db.session.delete(categoria)
    db.session.commit()
    flash(f'Categoría "{categoria.nombre}" eliminada', 'success')
    return redirect(url_for('admin.lista_categorias'))
