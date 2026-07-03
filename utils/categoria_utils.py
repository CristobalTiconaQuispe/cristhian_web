from models import Categoria


def populate_categoria_choices(form):
    categorias = Categoria.query.order_by(Categoria.nombre).all()
    form.categoria_id.choices = [(0, 'Sin categoría')] + [(c.id, c.nombre) for c in categorias]
