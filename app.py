from flask import Flask, render_template, request, redirect, url_for, session
from flask_sqlalchemy import SQLAlchemy
import os

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///modix.db'
app.config['SECRET_KEY'] = 'modix_secret_key_2026'
db = SQLAlchemy(app)

class Category(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    products = db.relationship('Product', backref='category_rel', lazy=True)

class Product(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    price = db.Column(db.String(50), nullable=False)
    car_model = db.Column(db.String(100), nullable=False)
    image_url = db.Column(db.String(200), nullable=False)
    category_id = db.Column(db.Integer, db.ForeignKey('category.id'), nullable=False)
    has_variant = db.Column(db.Boolean, default=False)

with app.app_context():
    db.create_all()

@app.route('/')
def index():
    search_query = request.args.get('q', '')
    category_id = request.args.get('category_id', type=int)
    
    query = Product.query
    if search_query:
        query = query.filter((Product.name.contains(search_query)) | (Product.car_model.contains(search_query)))
    if category_id:
        query = query.filter_by(category_id=category_id)
        
    products = query.all()
    categories = Category.query.all()
    return render_template('index.html', products=products, categories=categories, search_query=search_query, active_category=category_id)

@app.route('/admin', methods=['GET', 'POST'])
def admin():
    if session.get('logged_in'):
        categories = Category.query.all()
        products = Product.query.all()
        return render_template('admin.html', categories=categories, products=products)
    
    if request.method == 'POST':
        password = request.form.get('password')
        if password == 'toto1102005':
            session['logged_in'] = True
            return redirect(url_for('admin'))
        else:
            return render_template('admin_login.html', error='كلمة المرور غير صحيحة')
    
    return render_template('admin_login.html')

@app.route('/admin/logout')
def logout():
    session.pop('logged_in', None)
    return redirect(url_for('index'))

@app.route('/admin/add_category', methods=['POST'])
def add_category():
    if not session.get('logged_in'):
        return redirect(url_for('admin'))
    name = request.form.get('name')
    if name:
        db.session.add(Category(name=name))
        db.session.commit()
    return redirect(url_for('admin'))

@app.route('/admin/add_product', methods=['POST'])
def add_product():
    if not session.get('logged_in'):
        return redirect(url_for('admin'))
    name = request.form.get('name')
    price = request.form.get('price')
    car_model = request.form.get('car_model')
    category_id = request.form.get('category_id', type=int)
    has_variant = True if request.form.get('has_variant') else False
    
    image_file = request.files.get('image')
    image_url = ""
    if image_file and image_file.filename != '':
        os.makedirs('static', exist_ok=True)
        image_path = os.path.join('static', image_file.filename)
        image_file.save(image_path)
        image_url = image_file.filename
    else:
        image_url = request.form.get('image_url', '')

    if name and price and category_id:
        product = Product(
            name=name,
            price=price,
            car_model=car_model,
            image_url=image_url,
            category_id=category_id,
            has_variant=has_variant
        )
        db.session.add(product)
        db.session.commit()
    return redirect(url_for('admin'))

@app.route('/admin/delete_product/<int:id>')
def delete_product(id):
    if not session.get('logged_in'):
        return redirect(url_for('admin'))
    product = Product.query.get_or_404(id)
    db.session.delete(product)
    db.session.commit()
    return redirect(url_for('admin'))

@app.route('/admin/delete_category/<int:id>')
def delete_category(id):
    if not session.get('logged_in'):
        return redirect(url_for('admin'))
    category = Category.query.get_or_404(id)
    db.session.delete(category)
    db.session.commit()
    return redirect(url_for('admin'))

if __name__ == '__main__':
    app.run(debug=True)