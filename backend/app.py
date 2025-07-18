from flask import Flask, request, jsonify
from flask_jwt_extended import create_access_token, JWTManager, jwt_required, get_jwt_identity
from models import db, User, Product, Sale

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///pos.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['JWT_SECRET_KEY'] = 'super-secret'  # Change this in your application!
jwt = JWTManager(app)
db.init_app(app)

@app.route('/login', methods=['POST'])
def login():
    username = request.json.get('username', None)
    password = request.json.get('password', None)
    user = User.query.filter_by(username=username, password=password).first()
    if user:
        access_token = create_access_token(identity={'username': username, 'role': user.role})
        return jsonify(access_token=access_token)
    return jsonify({"msg": "Bad username or password"}), 401

@app.route('/products', methods=['GET'])
def get_products():
    products = Product.query.all()
    return jsonify([{'id': p.id, 'name': p.name, 'price': p.price, 'quantity': p.quantity} for p in products])

@app.route('/products', methods=['POST'])
@jwt_required()
def add_product():
    current_user = get_jwt_identity()
    if current_user['role'] != 'admin':
        return jsonify({"msg": "Admins only!"}), 403
    data = request.get_json()
    new_product = Product(name=data['name'], price=data['price'], quantity=data['quantity'])
    db.session.add(new_product)
    db.session.commit()
    return jsonify({'id': new_product.id, 'name': new_product.name, 'price': new_product.price, 'quantity': new_product.quantity})

@app.route('/products/<int:product_id>', methods=['PUT'])
@jwt_required()
def update_product(product_id):
    current_user = get_jwt_identity()
    if current_user['role'] != 'admin':
        return jsonify({"msg": "Admins only!"}), 403
    product = Product.query.get_or_404(product_id)
    data = request.get_json()
    product.name = data['name']
    product.price = data['price']
    product.quantity = data['quantity']
    db.session.commit()
    return jsonify({'id': product.id, 'name': product.name, 'price': product.price, 'quantity': product.quantity})

@app.route('/products/<int:product_id>', methods=['DELETE'])
@jwt_required()
def delete_product(product_id):
    current_user = get_jwt_identity()
    if current_user['role'] != 'admin':
        return jsonify({"msg": "Admins only!"}), 403
    product = Product.query.get_or_404(product_id)
    db.session.delete(product)
    db.session.commit()
    return jsonify({'message': 'Product deleted'})

@app.route('/sales', methods=['POST'])
def create_sale():
    data = request.get_json()
    product_id = data['product_id']
    quantity = data['quantity']
    product = Product.query.get_or_404(product_id)
    if product.quantity < quantity:
        return jsonify({'message': 'Not enough stock'}), 400
    total_price = product.price * quantity
    sale = Sale(product_id=product_id, quantity=quantity, total_price=total_price)
    product.quantity -= quantity
    db.session.add(sale)
    db.session.commit()
    return jsonify({'id': sale.id, 'product_id': sale.product_id, 'quantity': sale.quantity, 'total_price': sale.total_price})

@app.route('/sales', methods=['GET'])
@jwt_required()
def get_sales():
    current_user = get_jwt_identity()
    if current_user['role'] != 'admin':
        return jsonify({"msg": "Admins only!"}), 403
    sales = Sale.query.all()
    return jsonify([{'id': s.id, 'product_id': s.product_id, 'quantity': s.quantity, 'total_price': s.total_price} for s in sales])

if __name__ == '__main__':
    with app.app_context():
        db.create_all()
        if not User.query.filter_by(username='admin').first():
            admin_user = User(username='admin', password='admin', role='admin')
            db.session.add(admin_user)
            db.session.commit()
    app.run(debug=True)
