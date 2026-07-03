import os
import json
import uuid
from werkzeug.utils import secure_filename
from config import Config

CAMPOS_IMAGEN = ['imagen_1', 'imagen_2', 'imagen_3']


def guardar_imagenes(form):
    nombres = []
    for campo in CAMPOS_IMAGEN:
        file = getattr(form, campo).data
        if not file or file.filename == '':
            continue
        filename = secure_filename(file.filename)
        parts = filename.rsplit('.', 1)
        ext = parts[-1].lower() if len(parts) > 1 and parts[-1] else ''
        if not ext or ext not in Config.ALLOWED_EXTENSIONS:
            continue
        filename = f"{uuid.uuid4().hex}.{ext}"
        path = os.path.join(Config.UPLOAD_FOLDER, filename)
        file.save(path)
        try:
            from PIL import Image
            Image.open(path).verify()
        except Exception:
            os.remove(path)
            continue
        nombres.append(filename)
    return json.dumps(nombres) if nombres else ''


def eliminar_imagenes(producto):
    for nombre in producto.get_imagenes():
        path = os.path.join(Config.UPLOAD_FOLDER, nombre)
        if os.path.exists(path):
            os.remove(path)
