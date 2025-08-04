from flask import Flask, render_template, request, redirect, url_for, flash, get_flashed_messages
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
import os

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///fallas.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.secret_key = 'alguna_clave_segura'

db = SQLAlchemy(app)

# Modelos de base de datos
class Falla(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    descripcion = db.Column(db.String(200), nullable=False)
    ubicacion = db.Column(db.String(100), nullable=False)
    fecha_reporte = db.Column(db.DateTime, default=datetime.utcnow)
    reportado_por = db.Column(db.String(100), nullable=False)
    estado = db.Column(db.String(20), default='pendiente')
    acciones = db.relationship('AccionReparacion', backref='falla', lazy=True)

class AccionReparacion(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    falla_id = db.Column(db.Integer, db.ForeignKey('falla.id'), nullable=False)
    responsable = db.Column(db.String(100), nullable=False)
    fecha_planificada = db.Column(db.Date, nullable=False)
    fecha_real = db.Column(db.Date, nullable=True)
    acciones = db.Column(db.Text)
    materiales = db.Column(db.Text)
    historial = db.relationship('HistorialAccion', backref='accion', lazy=True)

class HistorialAccion(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    accion_id = db.Column(db.Integer, db.ForeignKey('accion_reparacion.id'), nullable=False)
    responsable = db.Column(db.String(100))
    fecha_planificada = db.Column(db.Date)
    fecha_real = db.Column(db.Date)
    acciones = db.Column(db.Text)
    materiales = db.Column(db.Text)
    timestamp = db.Column(db.DateTime, default=datetime.utcnow)

# Asegurar carpeta templates existe
if not os.path.exists('templates'):
    os.makedirs('templates')

# Crear templates básicos
with open('templates/index.html', 'w', encoding='utf-8') as f:
    f.write('''<!DOCTYPE html>
<html>
<head>
    <title>Fallas reportadas</title>
    <style>
        body { font-family: Arial, sans-serif; margin: 2em; }
        input, textarea, select, button { margin: 0.5em 0; display: block; width: 100%; max-width: 400px; }
        ul { list-style: none; padding: 0; }
        li { margin-bottom: 1em; background: #f4f4f4; padding: 1em; border-radius: 5px; }
        form { margin-top: 1em; }
    </style>
</head>
<body>
    {% with messages = get_flashed_messages() %}
      {% if messages %}
        <ul style="color: green;">
          {% for message in messages %}
            <li>{{ message }}</li>
          {% endfor %}
        </ul>
      {% endif %}
    {% endwith %}

    <h1>Fallas reportadas</h1>
    <form action="/reportar" method="post">
        <input type="text" name="descripcion" placeholder="Descripción" required>
        <input type="text" name="ubicacion" placeholder="Ubicación" required>
        <input type="text" name="reportado_por" placeholder="Nombre del residente" required>
        <button type="submit">Reportar</button>
    </form>
    <ul>
        {% for falla in fallas %}
        <li>
            <strong>{{ falla.descripcion }}</strong> en {{ falla.ubicacion }}
            [{{ falla.estado }}] - <a href="/gestionar/{{ falla.id }}">Gestionar</a>
            <br><small>Reportado el {{ falla.fecha_reporte.strftime('%Y-%m-%d %H:%M') }} por {{ falla.reportado_por }}</small>
        </li>
        {% endfor %}
    </ul>
</body>
</html>''')

# Resto del código (rutas y lógica) permanece igual, pero debes actualizar la ruta /reportar así:

@app.route('/reportar', methods=['POST'])
def reportar():
    descripcion = request.form['descripcion']
    ubicacion = request.form['ubicacion']
    reportado_por = request.form['reportado_por']
    nueva_falla = Falla(descripcion=descripcion, ubicacion=ubicacion, reportado_por=reportado_por)
    db.session.add(nueva_falla)
    db.session.commit()
    flash("Falla reportada exitosamente.")
    return redirect(url_for('index'))
