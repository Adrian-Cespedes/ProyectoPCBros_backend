from dataclasses import dataclass
from flask import Flask, jsonify, request
from flask_cors import CORS
from flask_sqlalchemy import SQLAlchemy
from flask_bcrypt import Bcrypt

app = Flask(__name__)
app.config[
    "SQLALCHEMY_DATABASE_URI"
] = "postgresql://postgres:vBu1iSunMNScmB1L8cE1@containers-us-west-67.railway.app:5571/railway"
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False


CORS(app)
db = SQLAlchemy(app)

bcrypt = Bcrypt(app)


@dataclass
class Cliente(db.Model):
    ruc: str
    email: str
    razon_social: str
    contrasenha: str
    telefono: str

    __tablename__ = "cliente"
    ruc = db.Column(db.String(11), primary_key=True)
    email = db.Column(db.String(50), unique=True)
    razon_social = db.Column(db.String(50))
    contrasenha = db.Column(db.String(200))
    telefono = db.Column(db.String(50))

    def __repr__(self):
        return f"<Cliente {self.ruc}>"

    def check_password(self, password):
        return self.contrasenha == password


@dataclass
class Venta(db.Model):
    id: int
    cliente_ruc: str
    recogedor_asignado_dni: int
    f_creacion: db.DateTime
    f_limite: db.DateTime
    estado: str
    monto_total: float

    __tablename__ = "venta"
    id = db.Column(db.Integer, primary_key=True)
    cliente_ruc = db.Column(db.String(11), db.ForeignKey("cliente.ruc"))
    recogedor_asignado_dni = db.Column(
        db.Integer, db.ForeignKey("recogedor.dni"))
    f_creacion = db.Column(db.DateTime)
    f_limite = db.Column(db.DateTime)
    estado = db.Column(db.String(50))
    monto_total = db.Column(db.Float)

    def __repr__(self):
        return f"<Venta {self.id}>"


@dataclass
class Pago(db.Model):
    id: int
    venta_id: int
    fecha: db.DateTime
    monto: float
    metodo: str

    __tablename__ = "pago"
    id = db.Column(db.Integer, primary_key=True)
    venta_id = db.Column(db.Integer, db.ForeignKey("venta.id"))
    fecha = db.Column(db.DateTime)
    monto = db.Column(db.Float)
    metodo = db.Column(db.String(50))

    def __repr__(self):
        return f"<Pago {self.id}>"


@dataclass
class Reembolso(db.Model):
    id: int
    pago_id: int
    fecha: db.DateTime

    __tablename__ = "reembolso"
    id = db.Column(db.Integer, primary_key=True)
    pago_id = db.Column(db.Integer, db.ForeignKey("pago.id"))
    fecha = db.Column(db.DateTime)

    def __repr__(self):
        return f"<Reembolso {self.id}>"


@dataclass
class Contiene_pr_venta(db.Model):
    venta_id: int
    producto_id: int
    cantidad: int

    __tablename__ = "contiene_pr_venta"
    venta_id = db.Column(db.Integer, db.ForeignKey(
        "venta.id"), primary_key=True)
    producto_id = db.Column(db.Integer, db.ForeignKey(
        "producto.id"), primary_key=True)
    cantidad = db.Column(db.Integer)

    def __repr__(self):
        return f"<Contiene_pr_venta {self.venta_id}>"


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
class Categoria(db.Model):
    nombre: str

    __tablename__ = "categoria"
    nombre = db.Column(db.String(50), primary_key=True)

    def __repr__(self):
        return f"<Categoria {self.nombre}>"


@dataclass
class Stock(db.Model):
    producto_id: int
    almacen_numero: int
    cantidad: int

    __tablename__ = "stock"
    producto_id = db.Column(db.Integer, db.ForeignKey(
        "producto.id"), primary_key=True)
    almacen_numero = db.Column(
        db.Integer, db.ForeignKey("almacen.numero"), primary_key=True
    )
    cantidad = db.Column(db.Integer)

    def __repr__(self):
        return f"<Stock del producto con id : {self.producto_id}>"


@dataclass
class Almacen(db.Model):
    numero: int
    direccion: str

    __tablename__ = "almacen"
    numero = db.Column(db.Integer, primary_key=True)
    direccion = db.Column(db.String(50))

    def __repr__(self):
        return f"<Almacen {self.numero}>"


@dataclass
class Persona(db.Model):
    dni: int
    nombre: str
    apellido: str
    telefono: str

    __tablename__ = "persona"
    dni = db.Column(db.Integer, primary_key=True)
    nombre = db.Column(db.String(50))
    apellido = db.Column(db.String(50))
    telefono = db.Column(db.String(12))

    def __repr__(self):
        return f"<Persona {self.dni}>"


@dataclass
class Recogedor(Persona):
    dni: int
    cliente_ruc: str

    __tablename__ = "recogedor"

    dni = db.Column(db.Integer, db.ForeignKey("persona.dni"), primary_key=True)
    cliente_ruc = db.Column(db.String(11), db.ForeignKey("cliente.ruc"))

    def __repr__(self):
        return f"<Recogedor {self.dni}>"


@dataclass
class Empleado(Persona):
    dni: int
    correo_institucional: str

    __tablename__ = "empleado"

    dni = db.Column(db.Integer, db.ForeignKey("persona.dni"), primary_key=True)
    correo_institucional = db.Column(db.String(50))

    def __repr__(self):
        return f"<Empleado {self.dni}>"


@dataclass
class Atencion_al_cliente(Empleado):
    dni: int

    __tablename__ = "atencion_al_cliente"

    dni = db.Column(db.Integer, db.ForeignKey(
        "empleado.dni"), primary_key=True)

    def __repr__(self):
        return f"<Atencion_al_cliente {self.dni}>"


@dataclass
class Almacenero(Empleado):
    dni: int
    almacen_numero: int

    __tablename__ = "almacenero"

    dni = db.Column(db.Integer, db.ForeignKey(
        "empleado.dni"), primary_key=True)
    almacen_numero = db.Column(db.Integer, db.ForeignKey("almacen.numero"))

    def __repr__(self):
        return f"<Almacenero {self.dni}>"


@dataclass
class Despacho(db.Model):
    numero: int
    fecha: db.DateTime
    venta_id: int
    atencion_al_cliente_dni: int
    recogedor_asignado_dni: int

    __tablename__ = "despacho"

    numero = db.Column(db.Integer, primary_key=True)
    fecha = db.Column(db.DateTime)
    venta_id = db.Column(db.Integer, db.ForeignKey("venta.id"))
    atencion_al_cliente_dni = db.Column(
        db.Integer, db.ForeignKey("atencion_al_cliente.dni")
    )
    recogedor_asignado_dni = db.Column(
        db.Integer, db.ForeignKey("recogedor.dni"))

    def __repr__(self):
        return f"<Despacho {self.numero}>"


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


@app.route("/api/clientes", methods=["GET", "POST"])
def route_clientes():
    if request.method == "GET":
        clientes = Cliente.query.all()
        return jsonify(clientes)
    elif request.method == "POST":
        cliente = Cliente(**request.json)
        db.session.add(cliente)
        db.session.commit()
        return "SUCCESS"


@app.route("/api/clientes/<ruc>", methods=["GET", "PUT", "DELETE"])
def route_cliente(ruc):
    if request.method == "GET":
        cliente = Cliente.query.get(ruc)
        return jsonify(cliente)
    elif request.method == "PUT":
        cliente = Cliente.query.get(ruc)
        cliente.nombre = request.json["nombre"]
        cliente.apellido = request.json["apellido"]
        cliente.correo = request.json["correo"]
        cliente.telefono = request.json["telefono"]
        db.session.commit()
        return "SUCCESS"
    elif request.method == "DELETE":
        cliente = Cliente.query.get(ruc)
        db.session.delete(cliente)
        db.session.commit()
        return "SUCCESS"


# Obtener carrito de cliente
@app.route("/api/clientes/carrito/<ruc>", methods=["GET", "POST"])
def route_carrito(ruc):
    if request.method == "GET":
        carrito = Carrito_de_Compras.query.filter_by(cliente_ruc=ruc).all()
        productos_carrito = []
        for item in carrito:
            producto = Producto.query.get(item.producto_id)
            if producto:
                producto_info = {
                    "id": producto.id,
                    "nombre": producto.nombre,
                    "precio": producto.precio,
                    "cantidad": item.cantidad
                }
                productos_carrito.append(producto_info)
        return jsonify(productos_carrito)
    elif request.method == "POST":
        carrito = Carrito_de_Compras(
            cliente_ruc=ruc,
            producto_id=request.json["producto_id"],
            cantidad=request.json["cantidad"],
        )
        db.session.add(carrito)
        db.session.commit()
        return "SUCCESS"


# ruta de productos
@app.route("/api/productos", methods=["GET", "POST"])
def route_productos():
    if request.method == "GET":
        productos = Producto.query.all()
        return jsonify(productos)
    elif request.method == "POST":
        producto = Producto(**request.json)
        db.session.add(producto)
        db.session.commit()
        return "SUCCESS"


# ruta para obtener productos por categoria
@app.route("/api/productos/<categoria>", methods=["GET"])
def route_productos_categoria(categoria):
    if request.method == "GET":
        prod = Producto.query.all()
        cat = Categoria_de.query.filter_by(categoria_nombre = categoria.upper()).all()
        productos_cat = []

        for pr in prod:
            for c in cat:
                if pr.id == c.producto_id:
                    productos_cat.append(pr)


        return jsonify(productos_cat)


# ruta para verificar contrasenha
@app.route('/api/login', methods=['POST'])
def login():
    data = request.json
    ruc = data.get('ruc')
    contrasenha = data.get('contrasenha')

    cliente = Cliente.query.get(ruc)
    check = cliente is not None and bcrypt.check_password_hash(
        cliente.contrasenha, contrasenha)
    return jsonify({"check": check})


with app.app_context():
    db.create_all()


if __name__ == "__main__":
    app.run(port=8080, debug=True, host='0.0.0.0')
