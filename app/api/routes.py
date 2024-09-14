from flask import request, make_response, jsonify
from flask_restx import Resource, fields, Namespace, reqparse, Api
from ..models import db, ShoppingCart, ShoppingCartItem
from ..schemas import ShoppingCartSchema, ShoppingCartItemSchema
import requests
import os

def init_routes(api):
    cart_ns = Namespace('carts', description='Shopping cart operations')
    api.add_namespace(cart_ns, path='/mm-shopping-cart')

    # Define models for serialization
    cart_model = api.model('Cart', {
        'id': fields.Integer(readOnly=True, description="The cart's ID."),
        'customercpf': fields.String(required=True, description="The CPF of the customer owning the cart."),
        'status': fields.Boolean(default=False, description="Status of the cart, True if purchased."),
        'datecreated': fields.DateTime(description="Creation date of the cart."),
        'total': fields.Float(description="Total price of items in the cart.")
    })

    cart_item_model = api.model('CartItem', {
        'id': fields.Integer(readOnly=True, description="The item's ID."),
        'cartid': fields.Integer(required=True, description="The ID of the cart."),
        'productitemid': fields.Integer(required=True, description="The ID of the product item."),
        'quantity': fields.Integer(required=True, description="Quantity of the product item."),
        'subtotal': fields.Float(description="Subtotal price of the item.")  # Calculated on the fly
    })

    # Define the request parser for filtering by customer CPF
    customer_query_parser = reqparse.RequestParser()
    customer_query_parser.add_argument('customercpf', type=str, help='Filter by customer CPF', location='args')

    @cart_ns.route('/')
    class ShoppingCartList(Resource):
        @cart_ns.expect(customer_query_parser)
        @cart_ns.marshal_list_with(cart_model)
        def get(self):
            """List all shopping carts or filter by customer CPF"""
            args = customer_query_parser.parse_args()
            customercpf = args.get('customercpf')

            if customercpf:
                # Fetch customer details from mm-customer
                customer_url = f"{os.getenv('MM_CUSTOMER_URL', 'http://mm-customer:5701')}/customers/{customercpf}"
                response = requests.get(customer_url)
                if response.status_code == 200:
                    customer_data = response.json()
                    customercpf = customer_data.get('cpf')
                    if customercpf:
                        carts = ShoppingCart.query.filter_by(customercpf=customercpf).all()
                        for cart in carts:
                            cart.total = sum(item.quantity * get_price(item.productitemid) for item in cart.items)
                    else:
                        return {'message': 'No customer found with provided CPF'}, 404
                else:
                    return {'message': 'Failed to fetch customer details'}, response.status_code
            else:
                carts = ShoppingCart.query.all()
                for cart in carts:
                    cart.total = sum(item.quantity * get_price(item.productitemid) for item in cart.items)
            return carts

        @cart_ns.expect(cart_model)
        @cart_ns.marshal_with(cart_model, code=201)
        def post(self):
            """Create a new shopping cart"""
            data = request.json
            # Check if the customer CPF exists in the mm-customer service
            customer_url = f"{os.getenv('MM_CUSTOMER_URL', 'http://mm-customer:5701')}/customers/{data['customercpf']}"
            response = requests.get(customer_url)
            if response.status_code == 200:
                customer_data = response.json()
                if customer_data and 'cpf' in customer_data:
                    cart = ShoppingCart(**data)
                    db.session.add(cart)
                    db.session.commit()
                    return cart, 201
                else:
                    return {'message': 'No customer found with provided CPF'}, 404
            else:
                return {'message': 'Failed to validate CPF with customer service'}, response.status_code


    @cart_ns.route('/<int:id>')
    @cart_ns.response(404, 'Shopping cart not found')
    class ShoppingCartDetail(Resource):
        @cart_ns.marshal_with(cart_model)
        def get(self, id):
            """Get a shopping cart by ID including total sum of items"""
            cart = ShoppingCart.query.get_or_404(id)
            cart.total = sum(item.quantity * get_price(item.productitemid) for item in cart.items)
            return cart

        @cart_ns.expect(cart_model)
        @cart_ns.marshal_with(cart_model)
        def put(self, id):
            """Update a shopping cart"""
            cart = ShoppingCart.query.get_or_404(id)
            data = request.json
            # Ensure no updates to the CPF without validation
            if 'customercpf' in data:
                customer_url = f"{os.getenv('MM_CUSTOMER_URL', 'http://mm-customer:5701')}/customers/{data['customercpf']}"
                response = requests.get(customer_url)
                if response.status_code != 200 or not response.json().get('cpf'):
                    return {'message': 'Invalid or non-existent CPF provided'}, 400
            
            for key, value in data.items():
                if hasattr(cart, key):
                    setattr(cart, key, value)

            # Re-calculate the total only if relevant fields that affect total are changed
            if 'items' in data:  # Assuming items can somehow be updated directly, adjust if your model differs
                cart.total = sum(item.quantity * get_price(item.productitemid) for item in cart.items)

            db.session.commit()
            return ShoppingCartSchema().dump(cart)

        @cart_ns.response(204, 'Shopping cart deleted')
        def delete(self, id):
            """Delete a shopping cart"""
            cart = ShoppingCart.query.get_or_404(id)
            db.session.delete(cart)
            db.session.commit()
            return '', 204

    @cart_ns.route('/<int:cartid>/items')
    class CartItemsList(Resource):
        @cart_ns.marshal_list_with(cart_item_model)
        def get(self, cartid):
            """List all items in a shopping cart"""
            items = ShoppingCartItem.query.filter_by(cartid=cartid).all()
            for item in items:
                item.subtotal = item.quantity * get_price(item.productitemid)
            return items
        

        @cart_ns.expect(cart_item_model)
        @cart_ns.marshal_with(cart_item_model, code=201)
        def post(self, cartid):
            """Add a new item to a shopping cart or update the quantity if it already exists"""
            data = request.json
            product_item_id = data['productitemid']
            additional_quantity = data['quantity']

            # Check if the item already exists in the cart
            existing_item = ShoppingCartItem.query.filter_by(cartid=cartid, productitemid=product_item_id).first()

            # If item exists, update the quantity
            if existing_item:
                # Check total required stock
                required_stock = existing_item.quantity + additional_quantity
                
                # Fetch inventory data
                inventory_url = f"{os.getenv('MM_INVENTORY_URL', 'http://MM_INVENTORY_URL:5705')}/mm-inventory/{product_item_id}"
                inventory_response = requests.get(inventory_url)
                if inventory_response.status_code == 200:
                    inventory_data = inventory_response.json()
                    if inventory_data['stock'] >= required_stock:
                        existing_item.quantity = required_stock
                    else:
                        return {'message': 'Insufficient stock available'}, 400
                else:
                    return {'message': 'Failed to check inventory', 'status': inventory_response.status_code}, inventory_response.status_code
            else:
                # If item does not exist, create a new one after checking stock
                inventory_url = f"{os.getenv('MM_INVENTORY_URL', 'http://MM_INVENTORY_URL:5705')}/mm-inventory/{product_item_id}"
                inventory_response = requests.get(inventory_url)
                if inventory_response.status_code == 200:
                    inventory_data = inventory_response.json()
                    if inventory_data['stock'] < additional_quantity:
                        return {'message': 'Insufficient stock available'}, 400
                    # Create new item since it doesn't exist and there's enough stock
                    existing_item = ShoppingCartItem(cartid=cartid, productitemid=product_item_id, quantity=additional_quantity)
                    db.session.add(existing_item)
                else:
                    return {'message': 'Failed to check inventory', 'status': inventory_response.status_code}, inventory_response.status_code

            # Commit the changes to the database
            db.session.commit()
            return ShoppingCartItemSchema().dump(existing_item), 201

    @cart_ns.route('/<int:cartid>/items/<int:productitemid>')
    class CartItemDetail(Resource):
        @cart_ns.marshal_with(cart_item_model)
        def get(self, cartid, productitemid):
            """Get a single item from a provided shopping cart"""
            item = ShoppingCartItem.query.filter_by(cartid=cartid, productitemid=productitemid).first_or_404()
            item.subtotal = item.quantity * get_price(item.productitemid)
            return item

        @cart_ns.expect(cart_item_model)
        @cart_ns.marshal_with(cart_item_model)
        def put(self, cartid, productitemid):
            """Update an item in a shopping cart"""
            item = ShoppingCartItem.query.filter_by(cartid=cartid, productitemid=productitemid).first_or_404()
            data = request.json
            for key, value in data.items():
                if hasattr(item, key):
                    setattr(item, key, value)
            db.session.commit()
            # Recalculate subtotal if quantity or productitemid changes
            item.subtotal = item.quantity * get_price(item.productitemid)
            return item

        @cart_ns.response(204, 'Cart item deleted')
        def delete(self, cartid, productitemid):
            """Delete an item from a shopping cart"""
            item = ShoppingCartItem.query.filter_by(cartid=cartid, productitemid=productitemid).first_or_404()
            db.session.delete(item)
            db.session.commit()
            return '', 204

    @cart_ns.route('/pay/<int:id>')
    class ShoppingCartPay(Resource):
        def post(self, id):
            """Finalize shopping cart payment by updating the stock and status."""
            cart = ShoppingCart.query.get_or_404(id)
            
            if cart.status:
                # If cart is already purchased, return an appropriate error message
                return make_response(jsonify({'message': 'Cart already purchased'}), 400)
            
            # Continue with stock verification and update process
            try:
                items = ShoppingCartItem.query.filter_by(cartid=id).all()
                for item in items:
                    inventory_url = f"{os.getenv('MM_INVENTORY_URL', 'http://mm-inventory:5704')}/mm-inventory/{item.productitemid}"
                    inventory_response = requests.get(inventory_url)
                    if inventory_response.status_code == 200:
                        product_item = inventory_response.json()
                        if product_item['stock'] < item.quantity:
                            return make_response(jsonify({'message': f"Insufficient stock for item ID {item.productitemid}"}), 400)
                        
                        # Update stock if enough is available
                        new_stock = product_item['stock'] - item.quantity
                        update_payload = {
                            "stock": new_stock,
                            "price": product_item['price'],
                            "productid": product_item['productid'],
                            "storeid": product_item['storeid']
                        }
                        inventory_put_url = f"{os.getenv('MM_INVENTORY_URL', 'http://mm-inventory:5704')}/mm-inventory/{item.productitemid}"
                        update_response = requests.put(inventory_put_url, json=update_payload)
                        if update_response.status_code != 200:
                            return make_response(jsonify({'message': 'Failed to update inventory', 'productitemid': item.productitemid}), 400)

                # If all items are successfully verified and stock updated, set the cart status to purchased
                cart.status = True
                db.session.commit()

                # Return the updated cart data
                return make_response(jsonify(ShoppingCartSchema().dump(cart)), 200)
            except Exception as e:
                # General exception handling for any unforeseen errors
                return make_response(jsonify({'message': str(e)}), 500)

def get_price(productitemid):
    """Fetch the price of a product item from mm-inventory service"""
    response = requests.get(f"{os.getenv('MM_INVENTORY_URL', 'http://mm-inventory:5704')}/mm-inventory/{productitemid}")
    if response.status_code == 200:
        product_item = response.json()
        return product_item.get('price', 0) 
    return 0  # If not found or error, assume zero price
