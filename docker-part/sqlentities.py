from main import db, ma


"""

   This module contains the tables of the databases represented as python classes. They are used by the SQLAlchemy 
   library to query the database. It also contains a metadata class of the classes, used by the Marshmallow library to
   create a Rest api. The metadata classes contain the fields that will be contained in the json response. More 
   information about these two libraries, and also some examples, can be found at:
   - SQLAlchemy: http://flask-sqlalchemy.pocoo.org/2.3/quickstart/
   - Marshmallow: https://medium.com/python-pandemonium/build-simple-restful-api-with-python-and-flask-part-2-724ebf04d12

"""


class University(db.Model):
   id = db.Column(db.Integer, primary_key=True)
   name = db.Column(db.String(255), unique=True, nullable=False)
   pubkey = db.Column(db.String(255), unique=True, nullable=False)
   address = db.Column(db.String(255), unique=True, nullable=False)


class UniversitySchema(ma.Schema):
   class Meta:
      fields = ('name', 'pubkey', 'address')


class Student(db.Model):
   __tablename__ = "student"

   cnp = db.Column(db.String(25), primary_key=True)
   name = db.Column(db.String(255), unique=True, nullable=False)
   pubkey = db.Column(db.String(255), unique=True, nullable=False)
   address = db.Column(db.String(255), unique=True, nullable=False)
   multisig = db.Column(db.String(255), unique=True, nullable=False)
   diploma = db.relationship("Diploma", backref='student', passive_deletes=True)


class StudentSchema(ma.Schema):
   class Meta:
      fields = ('cnp', 'name', 'pubkey', 'address', 'multisig')


class Diploma(db.Model):
   __tablename__ = "diploma"

   hash = db.Column(db.String(512), primary_key=True)
   student_cnp = db.Column(db.String(25), db.ForeignKey(Student.cnp, ondelete='CASCADE'), unique=True, nullable=False)
   name = db.Column(db.String(255), unique=True, nullable=False)


class DiplomaSchema(ma.Schema):
   class Meta:
      fields = ('hash', 'student_cnp', 'name')


students_schema = StudentSchema(many=True)
universities_schema = UniversitySchema(many=True)
diplomas_schema = DiplomaSchema(many=True)