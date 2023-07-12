from dataclasses import dataclass
from flask import Flask, jsonify, request
from flask_cors import CORS
from flask_sqlalchemy import SQLAlchemy
from flask_bcrypt import Bcrypt

from sqlalchemy.schema import DropTable
from sqlalchemy.ext.compiler import compiles

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///database.db'
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False


CORS(app)
db = SQLAlchemy(app)

bcrypt = Bcrypt(app)


@dataclass
class Producto(db.Model):
    id: int
    nombre: str
    precio: float
    descripcion: str
    fabricante_nombre: str

    __tablename__ = "producto"
    id = db.Column(db.Integer, primary_key=True)
    nombre = db.Column(db.String(50))
    precio = db.Column(db.Float)
    descripcion = db.Column(db.String(50))
    fabricante_nombre = db.Column(
        db.String(50), db.ForeignKey("fabricante.nombre"))

    def __repr__(self):
        return f"<Producto {self.id}>"


@dataclass
class Cliente(db.Model):
    ruc: str
    email: str
    razon_social: str
    contrasenha: str
    telefono: str

    __tablename__ = "cliente"
    ruc = db.Column(db.String(11), primary_key=True)
    email = db.Column(db.String(50))
    razon_social = db.Column(db.String(50))
    contrasenha = db.Column(db.String(200))
    telefono = db.Column(db.String(50))

    def __repr__(self):
        return f"<Cliente {self.ruc}>"


@dataclass
class Categoria_de(db.Model):
    producto_id: int
    categoria_nombre: str

    __tablename__ = "categoria_de"
    producto_id = db.Column(db.Integer, db.ForeignKey(
        "producto.id"), primary_key=True)
    categoria_nombre = db.Column(
        db.String(50), db.ForeignKey("categoria.nombre"), primary_key=True
    )

    def __repr__(self):
        return f"<Categoria_de {self.producto_id}>"


@dataclass
class Fabricante(db.Model):
    nombre: str
    pais: str
    dominio_correo: str

    __tablename__ = "fabricante"

    nombre = db.Column(db.String(50), primary_key=True)
    pais = db.Column(db.String(50))
    dominio_correo = db.Column(db.String(50))

    def __repr__(self):
        return f"<Fabricante {self.nombre}>"


@dataclass
class Carrito_de_Compras(db.Model):
    cliente_ruc: str
    producto_id: int
    cantidad: int

    __tablename__ = "carrito_de_compras"

    cliente_ruc = db.Column(db.String(11), db.ForeignKey(
        "cliente.ruc"), primary_key=True)
    producto_id = db.Column(db.Integer, db.ForeignKey(
        "producto.id"), primary_key=True)
    cantidad = db.Column(db.Integer)

    def __repr__(self):
        return f"<Carrito_de_Compras {self.id}>"


@dataclass
class Categoria(db.Model):
    nombre: str

    __tablename__ = "categoria"
    nombre = db.Column(db.String(50), primary_key=True)

    def __repr__(self):
        return f"<Categoria {self.nombre}>"


def clear_data(session):
    meta = db.metadata
    for table in reversed(meta.sorted_tables):
        session.execute(table.delete())
    session.commit()


@compiles(DropTable, "postgresql")
def _compile_drop_table(element, compiler, **kwargs):
    return compiler.visit_drop_table(element) + " CASCADE"


with app.app_context():

    db.drop_all()
    db.create_all()

    # aniadir fabricantes
    db.session.add(Fabricante(
        nombre="AMD", pais="USA", dominio_correo="amd.com"))
    db.session.add(Fabricante(nombre="Nvidia", pais="USA",
                   dominio_correo="nvidia.com"))

    # productos
    db.session.add(Producto(id=1, nombre="Ryzen 5",
                   precio=2000, fabricante_nombre="AMD"))
    db.session.add(Producto(id=2, nombre="Ryzen 7",
                   precio=3000, fabricante_nombre="AMD"))
    db.session.add(Producto(id=3, nombre="Ryzen 9",
                   precio=4000, fabricante_nombre="AMD"))
    db.session.add(Producto(id=4, nombre="RTX 2060",
                   precio=3000, fabricante_nombre="Nvidia"))
    db.session.add(Producto(id=5, nombre="RTX 2070",
                   precio=4000, fabricante_nombre="Nvidia"))
    db.session.add(Producto(id=6, nombre="RTX 2080",
                   precio=5000, fabricante_nombre="Nvidia"))
    db.session.add(Producto(id=7, nombre="RTX 2080 Ti",
                   precio=6000, fabricante_nombre="Nvidia"))
    db.session.add(Producto(id=8, nombre="GTX 1660",
                   precio=2000, fabricante_nombre="Nvidia"))
    db.session.add(Producto(id=9, nombre="GTX 1660 Ti",
                   precio=3000, fabricante_nombre="Nvidia"))

    db.session.add(Categoria(nombre="CPU"))
    db.session.add(Categoria(nombre="GPU"))

    db.session.commit()

    db.session.add(Categoria_de(producto_id=1, categoria_nombre="CPU"))
    db.session.add(Categoria_de(producto_id=2, categoria_nombre="CPU"))
    db.session.add(Categoria_de(producto_id=3, categoria_nombre="CPU"))
    db.session.add(Categoria_de(producto_id=4, categoria_nombre="GPU"))
    db.session.add(Categoria_de(producto_id=5, categoria_nombre="GPU"))
    db.session.add(Categoria_de(producto_id=6, categoria_nombre="GPU"))
    db.session.add(Categoria_de(producto_id=7, categoria_nombre="GPU"))
    db.session.add(Categoria_de(producto_id=8, categoria_nombre="GPU"))
    db.session.add(Categoria_de(producto_id=9, categoria_nombre="GPU"))

    # contrasenha
    contra = bcrypt.generate_password_hash("test123").decode("utf-8")

    # clientes
    db.session.add(Cliente(
        ruc='10999999991', email='test1@gmail.com', razon_social='Test1 SAC',
        contrasenha=contra, telefono='999888777'
    ))
    db.session.add(Cliente(
        ruc='10999999992', email='test2@gmail.com', razon_social='Test2 SAC',
        contrasenha=contra, telefono='999888666'
    ))

    db.session.commit()

    # Carrito_de_Compras
    db.session.add(Carrito_de_Compras(
        cliente_ruc='10999999991', producto_id=2, cantidad=10
    ))
    db.session.add(Carrito_de_Compras(
        cliente_ruc='10999999991', producto_id=5, cantidad=6
    ))
    db.session.add(Carrito_de_Compras(
        cliente_ruc='10999999991', producto_id=9, cantidad=3
    ))

    # comitear
    db.session.commit()
