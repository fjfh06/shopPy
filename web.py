
from werkzeug.security import generate_password_hash
from sqlalchemy.sql.functions import session_user
from werkzeug.security import check_password_hash
import pymysql
from flask.templating import render_template
from flask import Flask, render_template, request, redirect, url_for,session
from werkzeug.utils import secure_filename
import os

from clases import Product, app, db, User, Purchase, PurchaseLine

@app.route('/')
def index():
    q = request.args.get('q', '')  # Obtener término de búsqueda
    if q:
        productos = Product.query.filter(Product.name.ilike(f'%{q}%')).all()
    else:
        productos = Product.query.all()
    usuario = None
    if 'user' in session:
        usuario = User.query.get(session['user'])
    return render_template('shop/main.html', productos=productos, usuario=usuario)



@app.route('/producto/<int:id>')
def detalle_producto(id):
    # Buscar el producto en la base de datos por id
    p = Product.query.get(id)  # devuelve None si no existe

    if p:
        return render_template('shop/product/detalle.html', producto=p)
    else:
        return "Producto no encontrado", 404

@app.route('/eliminar/<int:id>', methods=['POST'])
def eliminar_producto(id):
    producto = Product.query.get(id)
    if producto:
        db.session.delete(producto)
        db.session.commit()
        productos = Product.query.all()  # Consultar de nuevo para actualizar la lista
        return render_template('shop/main.html', productos=productos)
    else:
        return "Producto no encontrado", 404

@app.route('/editar/<int:id>')
def editar_producto(id):
    producto = Product.query.get(id)
    if producto:
        # Aquí puedes agregar la lógica para editar el producto
        # Por ejemplo, podrías redirigir a un formulario de edición
        return render_template('shop/product/formEdit.html', producto=producto)
    else:
        return "Producto no encontrado", 404

@app.route('/productos/editar/<int:id>', methods=['POST'])
def actualizar_producto(id):
    producto = Product.query.get(id)
    if producto:
        # Actualizar los campos del producto con los datos del formulario
        producto.name = request.form['nombre']
        producto.price = float(request.form['precio'])
        producto.stock = request.form['stock']
        archivo = request.files['imagen']
        if archivo and archivo.filename != '':
            filename = secure_filename(archivo.filename)
            archivo.save(os.path.join('static/uploads', filename))
            producto.img = filename  # Actualizar la imagen solo si se subió una nueva
        
        db.session.commit()  # Guardar los cambios en la base de datos
        return render_template('shop/product/detalle.html', producto=producto)
    else:
        return "Producto no encontrado", 404

@app.route('/productos/nuevo')
def nuevo_producto():
    # Renderiza el formulario para añadir un producto
    return render_template('shop/product/formAdd.html')


@app.route('/productos/agregar', methods=['POST'])
def agregar_producto():
    archivo = request.files['imagen']
    filename = None

    if archivo and archivo.filename != '':
        filename = secure_filename(archivo.filename)
        archivo.save(os.path.join('static/uploads', filename))
    nuevo = Product(
        name=request.form['nombre'],
        price=request.form['precio'],
        stock=request.form['stock'],
        img=filename

    )
    db.session.add(nuevo)
    db.session.commit()
    return redirect(url_for('index'))

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        user = User.query.filter_by(username=username).first()
        # print(user.contrasena)
        # print(password)
        # print(generate_password_hash(password))
        if user and check_password_hash(user.password ,password):
            session['user'] = user.id
            session['roles'] = user.roles.split()
            # 🆕 Crear carrito si no existe
            if 'carrito' not in session:
                session['carrito'] = {}  # {product_id: cantidad}
            return redirect(url_for('index'))
        else:
            return "Credenciales inválidas", 401
    else:
        return render_template('sesion/login.html')

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']

        hashed_password = generate_password_hash(password)
        new_user = User(username=username, password=hashed_password)
        db.session.add(new_user)
        db.session.commit() 
        return redirect(url_for('login'))
    else:
        return render_template('sesion/register.html')

@app.route('/logout')
def logout():
    session.pop('user', None)
    return redirect(url_for('index'))


@app.route('/carrito')
def carrito():
    if 'carrito' not in session or not isinstance(session['carrito'], dict):
        session['carrito'] = {}

    carrito_ids = [int(pid) for pid in session['carrito'].keys()]  # convertir a int
    productos_carrito = Product.query.filter(Product.id.in_(carrito_ids)).all()

    for p in productos_carrito:
        p.cantidad = session['carrito'][str(p.id)]  # clave string

    return render_template('shop/cart.html', carrito=productos_carrito)



@app.route('/carrito/<int:producto_id>', methods=['POST'])
def agregar_al_carrito(producto_id):
    if 'carrito' not in session or not isinstance(session['carrito'], dict):
        session['carrito'] = {}
    
    carrito = session['carrito']
    pid = str(producto_id)  # ✅ usar string como clave

    if pid in carrito:
        carrito[pid] += 1
    else:
        carrito[pid] = 1

    session['carrito'] = carrito
    session.modified = True
    return redirect(url_for('carrito'))


@app.route('/eliminar_del_carrito/<int:producto_id>', methods=['POST'])
def eliminar_del_carrito(producto_id):
    if 'carrito' not in session or not isinstance(session['carrito'], dict):
        session['carrito'] = {}

    carrito = session['carrito']
    pid = str(producto_id)  # clave string

    if pid in carrito:
        carrito[pid] -= 1
        if carrito[pid] <= 0:
            del carrito[pid]

    session['carrito'] = carrito
    session.modified = True
    return redirect(url_for('carrito'))


@app.route('/pedido', methods=['POST'])
def realizar_pedido():
    if 'carrito' not in session or not session['carrito']:
        return redirect(url_for('carrito'))

    purchase = Purchase(user_id=session['user'], status='OPEN')
    db.session.add(purchase)
    db.session.commit()  # Necesario para obtener purchase.id

    for product_id, cantidad in session['carrito'].items():
        detalle = PurchaseLine(
            purchase_id=purchase.id,
            product_id=product_id,
            cantidad=cantidad,
            precio_unidad=Product.query.get(product_id).price
        )
        db.session.add(detalle)
    db.session.commit()

    session['carrito'] = {}  # ❌ ahora como diccionario
    session.modified = True
    return redirect(url_for('index'))


if __name__ == '__main__':
    with app.app_context():
        db.create_all()
        app.run(host="0.0.0.0", port=5000, debug=True)