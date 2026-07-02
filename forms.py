from flask_wtf import FlaskForm
from flask_wtf.file import FileAllowed
from wtforms import StringField, TextAreaField, FloatField, FileField, SubmitField, PasswordField, BooleanField, SelectField
from wtforms.validators import DataRequired, Length, NumberRange

ALLOWED = ['jpg', 'jpeg', 'png', 'gif', 'webp']
IMG_VALIDATORS = [FileAllowed(ALLOWED, 'Solo imágenes (jpg, png, gif, webp)')]


class ProductoForm(FlaskForm):
    nombre = StringField('Nombre del producto', validators=[
        DataRequired(message='El nombre es obligatorio'),
        Length(max=200)
    ])
    descripcion = TextAreaField('Descripción')
    precio = FloatField('Precio (Bs)', validators=[
        DataRequired(message='El precio es obligatorio'),
        NumberRange(min=0.01, message='El precio debe ser mayor a 0')
    ])
    imagen_1 = FileField('Foto principal', validators=IMG_VALIDATORS)
    imagen_2 = FileField('Foto 2 (opcional)', validators=IMG_VALIDATORS)
    imagen_3 = FileField('Foto 3 (opcional)', validators=IMG_VALIDATORS)
    categoria_id = SelectField('Categoría', coerce=int, validators=[])
    destacado = BooleanField('Producto destacado (aparece en la página de inicio)')
    submit = SubmitField('Guardar producto')


class LoginForm(FlaskForm):
    username = StringField('Usuario', validators=[DataRequired(message='El usuario es obligatorio')])
    password = PasswordField('Contraseña', validators=[DataRequired(message='La contraseña es obligatoria')])
    submit = SubmitField('Ingresar')
