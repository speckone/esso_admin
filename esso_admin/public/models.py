from esso_admin.database import Column, Model, SurrogatePK, db, reference_col, relationship


class PgFile(SurrogatePK, Model):
    __tablename__ = 'pgfiles'
    name = Column(db.String, unique=True, nullable=False)
    file = Column(db.String, unique=True, nullable=False)

    def __repr__(self):
        return self.name

