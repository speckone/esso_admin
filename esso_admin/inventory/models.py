from esso_admin.database import Column, Model, SurrogatePK, db, reference_col, relationship
from sqlalchemy import Table

order_products = Table('order_items',
                       product_id=reference_col('product'),
                       order_id=reference_col('order'),
                       )


class InventoryItem(SurrogatePK, Model):
    __tablename__ = 'inventory'
    store_quantity = Column(db.Integer)
    storage_quantity = db.Column(db.Integer)
    store_capacity = Column(db.Integer)
    product_id = reference_col('product')
    product = relationship('Product', backref='inventory_items')

    def __repr__(self):
        return self.product.name

    def running_low(self):
        return self.store_capacity <= self.reorder_level

    def get_from_storage(self):
        return self.needed_at_store() <= self.storage_quantity

    def needed_at_store(self):
        return self.store_capacity - self.store_quantity

    def storage_retrieval(self, number_retrieved):
        self.store_quantity += number_retrieved
        self.storage_quantity -= number_retrieved

    def total_quantity(self):
        return self.store_quantity + self.store_quantity

    def cost(self):
        return self.product.unit_price * self.needed_at_store()


class Product(SurrogatePK, Model):
    __tablename__ = 'product'
    name = Column(db.String, unique=True, nullable=False)
    unit_price = Column(db.Float)
    unit_id = reference_col('unit')
    unit = relationship('Unit', backref='products')
    vendor_id = reference_col('vendor')
    vendor = relationship('Vendor', backref='products')
    reorder_level = Column(db.Integer)

    def __repr__(self):
        return self.name


class Unit(SurrogatePK, Model):
    __tablename__ = 'unit'
    name = Column(db.String, unique=True, nullable=False)


class Vendor(SurrogatePK, Model):
    __tablename__ = 'vendor'
    name = Column(db.String, unique=True, nullable=False)


class Order(SurrogatePK, Model):
    __tablename__ = 'order'
    order_date = Column(db.DateTime)
    products = relationship('Product', secondary=order_products)
