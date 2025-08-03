from flask import Flask, render_template, request, redirect, url_for
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///fallas.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)

class Falla(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    descripcion = db.Column(db.String(500), nullable=False)
    ubicacion = db.Column(db.String(100), nullable=False)
    fecha_reporte = db.Column(db.DateTime, default=datetime.utcnow)
    estado = db.Column(db.String(20), default='pendiente')
    acciones = db.relationship('AccionReparacion', backref='falla', lazy=True)

class AccionReparacion(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    falla_id = db.Column(db.Integer, db.ForeignKey('falla.id'), nullable=False)
    responsable = db.Column(db.String(100), nullable=False)
    fecha_planificada = db.Column(db.Date)
    fecha_real = db.Column(db.Date)
    acciones = db.Column(db.Text)
    materiales = db.Column(db.Text)

@app.route('/')
def index():
    fallas = Falla.query.order_by(Falla.fecha_reporte.desc()).all()
    return render_template('index.html', fallas=fallas)

@app.route('/reportar', methods=['POST'])
def reportar():
    descripcion = request.form['descripcion']
    ubicacion = request.form['ubicacion']
    nueva_falla = Falla(descripcion=descripcion, ubicacion=ubicacion)
    db.session.add(nueva_falla)
    db.session.commit()
    return redirect(url_for('index'))

@app.route('/gestionar/<int:id>', methods=['GET', 'POST'])
def gestionar(id):
    falla = Falla.query.get_or_404(id)
    if request.method == 'POST':
        accion = AccionReparacion(
            falla_id=id,
            responsable=request.form['responsable'],
            fecha_planificada=request.form['fecha_planificada'],
            fecha_real=request.form['fecha_real'],
            acciones=request.form['acciones'],
            materiales=request.form['materiales']
        )
        falla.estado = request.form['estado']
        db.session.add(accion)
        db.session.commit()
        return redirect(url_for('index'))
    return render_template('gestionar.html', falla=falla)

if __name__ == '__main__':
    with app.app_context():
        db.create_all()
    app.run(debug=True)
