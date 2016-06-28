
from datetime import datetime
from flask.ext.login import UserMixin, AnonymousUserMixin
from myapp import db, login_manager

# Association tables for Many-To-Many relationships between various tables
association_table_class_user = db.Table('association_class_user',
                                        db.Column('class_id', db.String(64),
                                                  db.ForeignKey('Class.id')),
                                        db.Column('user_id', db.String(64),
                                                  db.ForeignKey('User.id')))
association_table_class_lab = db.Table('association_class_lab',
                                       db.Column('class_id', db.String(64),
                                                 db.ForeignKey('Class.id')),
                                       db.Column('lab_id', db.String(64),
                                                 db.ForeignKey(
                                                    'Lab.id')))
association_table_user_lab = db.Table('association_user_lab',
                                      db.Column('user_id', db.String(64),
                                                db.ForeignKey('User.id')),
                                      db.Column('lab_id', db.String(64),
                                                db.ForeignKey(
                                                    'Lab.id')))


# set up class to track the date and time information for an object
class DateTimeInfo(object):
    created_on = db.Column(db.DateTime, default=datetime.now)
    updated_on = db.Column(db.DateTime, default=datetime.now,
                           onupdate=datetime.now)


# Store general info of a lab
class Lab(db.Model):
    __tablename__ = 'Lab'
    id = db.Column(db.String(128), nullable=False, unique=True,
                   primary_key=True)
    name = db.Column(db.String(128), nullable=False)
    class_name = db.Column(db.String(128), nullable=False)
    prof_name = db.Column(db.String(128), nullable=False)
    # lab description contained in description variable
    description = db.Column(db.String(4096))
    status = db.Column(db.Enum('Activated', 'Downloadable', 'Unactivated',
                               name='status'))

    # one-to-many: a lab can have multiple experiments
    experiments = db.relationship('Experiment', back_populates='lab',
                                  cascade="all, delete, delete-orphan")
    # Many-to-Many: a class can have multiple labs and a lab can have multiple
    # classes
    classes = db.relationship("Class", secondary=association_table_class_lab,
                              back_populates="labs")
    # Many-to-Many: a user can have multiple labs and a lab can have multiple
    # users
    users = db.relationship("User", secondary=association_table_user_lab,
                            back_populates="labs")

    def __repr__(self):
        # Representation of class object in string format
        tpl = ('Lab<id: {id}, name: {name}'
               ', class_name: {class_name}, prof_name: {prof_name}'
               ', description: {description}, status: {status}'
               ', experiments: {experiments}, classes: {classes}'
               ', users: {users}>')
        formatted = tpl.format(id=self.id, name=self.name,
                               class_name=self.class_name,
                               prof_name=self.prof_name,
                               description=self.description,
                               status=self.status,
                               experiments=[e.name for e in self.experiments],
                               classes=[c.name for c in self.classes],
                               users=[u.name for u in self.users])
        return formatted


# Store experiments' info of a lab
class Experiment(db.Model):
    __tablename__ = 'Experiment'
    id = db.Column(db.String(128), nullable=False, unique=True,
                   primary_key=True)
    name = db.Column(db.String(512), nullable=False)
    description = db.Column(db.String(512))
    order = db.Column(db.Integer, nullable=False)
    # Type of value expected for this experiment
    value_type = db.Column(db.Enum('Number', 'Text', name='value_type'))
    # Value range only applies when the type is a number
    value_range = db.Column(db.String(64))
    # Value candidates only applies when the type is text
    value_candidates = db.Column(db.String(512))

    # Many-to-One: a lab can have multiple experiments
    lab_id = db.Column(db.String(128), db.ForeignKey('Lab.id'))
    lab = db.relationship("Lab", back_populates="experiments")

    # one-to-many: a experiment can have multiple data
    observations = db.relationship('Observation', back_populates='experiment',
                                   cascade="all, delete, delete-orphan")

    def __repr__(self):
        tpl = ('Lab<id: {id}, name: {name}, description: {description}'
               ', order: {order}, value_type: {value_type}'
               ', value_range: {value_range}'
               ', value_candidates: {value_candidates}'
               ', lab_id: {lab_id}, lab:{lab}'
               ', observations: {observations}>')
        formatted = tpl.format(id=self.id, name=self.name,
                               description=self.description,
                               order=self.order,
                               value_type=self.value_type,
                               value_range=self.value_range,
                               value_candidates=self.value_candidates,
                               lab_id=self.lab_id,
                               lab=self.lab.name,
                               observations=[ob.id for ob in self.observations])
        return formatted


# Store data entered by students
class Observation(db.Model, DateTimeInfo):
    __tablename__ = 'Observation'
    id = db.Column(db.String(128), nullable=False, unique=True,
                   primary_key=True)
    student_name = db.Column(db.String(256), nullable=False)
    data = db.Column(db.String(512), nullable=False)

    # Many-to-One: an experiment can have mulitple datasets inputted by
    # different students
    experiment_id = db.Column(db.String(128), db.ForeignKey('Experiment.id'))
    experiment = db.relationship("Experiment", back_populates="observations")

    def __repr__(self):
        tpl = ('Observation<experiment_id: {experiment_id}, id: {id},'
               'data: {data}>')
        formatted = tpl.format(experiment_id=self.experiment_id, id=self.id,
                               data=self.data)
        return formatted


class Class(db.Model):
    __tablename__ = 'Class'
    id = db.Column(db.String(128), nullable=False, unique=True,
                   primary_key=True)
    name = db.Column(db.String(128), nullable=False)
    time = db.Column(db.String(128), nullable=False)
    # Many-to-Many: A Class can have multiple users(both professors and
    # students)
    users = db.relationship("User", secondary=association_table_class_user,
                            back_populates="classes")
    # Many-to-Many: A Class can have multiple labs
    labs = db.relationship("Lab", secondary=association_table_class_lab,
                           back_populates="classes")

    def __repr__(self):
        tpl = ('Class<id: {id}, time: {time}, name: {name}, users: {users},'
               'labs: {labs}>')
        formatted = tpl.format(id=self.id, time=self.time,
                               name=self.name,
                               users=[u.name for u in self.users],
                               labs=[lab.name for lab in self.labs])
        return formatted


class User(UserMixin, db.Model):
    __tablename__ = 'User'
    id = db.Column(db.String(64), nullable=False, unique=True,
                   primary_key=True)
    username = db.Column(db.String(64), nullable=False, unique=True)
    password = db.Column(db.String(128), nullable=False)
    name = db.Column(db.String(128))
    # Many-to-One: A role can have multiple users
    role_name = db.Column(db.String(64), db.ForeignKey('Role.name'))
    role = db.relationship("Role", back_populates="users")

    # Many-to-Many: A User can have multiple classes
    classes = db.relationship("Class", secondary=association_table_class_user,
                              back_populates="users")
    # Many-to-Many: A User can have multiple labs
    labs = db.relationship("Lab", secondary=association_table_user_lab,
                           back_populates="users")

    def verify_password(self, password):
        return self.password == password

    # can function checks if user is allowed to peform an operation
    def can(self, permissions):
        return self.role is not None and (
            self.role.permissions & permissions) == permissions

    def __repr__(self):
        tpl = ('User<id: {id}, username: {username}, password: {password},'
               ' role: {role_name}, classes: {classes}, labs: {labs}>')
        formatted = tpl.format(id=self.id, username=self.username,
                               password=self.password,
                               role_name=self.role_name,
                               classes=[c.id for c in self.classes],
                               labs=[l.id for l in self.labs])
        return formatted


# Function for use when user is not logged in
class AnonymousUser(AnonymousUserMixin):
    def can(self, permissions):
        return False
# Associate the LoginManager with the anonymous user class
login_manager.anonymous_user = AnonymousUser


# Function accepts a user id and returns the user object of that id
@login_manager.user_loader
def load_user(user_id):
    return User.query.get(user_id)


class Role(db.Model):
    __tablename__ = 'Role'
    name = db.Column(db.String(64), nullable=False, unique=True,
                     primary_key=True)
    # Whether current role object is default of user
    default = db.Column(db.Boolean, default=False)
    # A number representing the power the role has using bit operation
    permissions = db.Column(db.Integer, nullable=False)

    # one-to-many: A Role can have multiple users
    users = db.relationship('User', back_populates='role', lazy='dynamic')

    # For database initialization, no object needed to use this method
    @staticmethod
    def insert_roles():
        roles = {
            'Student': (Permission.DATA_ENTRY, True),
            'Admin': (Permission.DATA_ENTRY |
                      Permission.DATA_EDIT |
                      Permission.LAB_SETUP |
                      Permission.ADMIN, False),
            'SuperAdmin': (Permission.DATA_ENTRY |
                           Permission.DATA_EDIT |
                           Permission.LAB_SETUP |
                           Permission.ADMIN |
                           Permission.LAB_MANAGE |
                           Permission.USER_MANAGE |
                           Permission.SUPERADMIN, False)
        }
        for r in roles:
            role = Role.query.filter_by(name=r).first()
            if role is None:
                role = Role(name=r)
            role.permissions = roles[r][0]
            role.default = roles[r][1]
            db.session.add(role)
        db.session.commit()

    def __repr__(self):
        tpl = ('Role<name: {name}, default: {default},'
               ' permissions: {permissions}>')
        formatted = tpl.format(name=self.name,
                               default=self.default,
                               permissions=self.permissions)
        return formatted


# Bits associated with the role power they represent using hexadecimal format
class Permission:
    DATA_ENTRY = 0x01
    DATA_EDIT = 0x02
    LAB_SETUP = 0x04
    ADMIN = 0x08
    LAB_ACCESS = 0x10
    LAB_MANAGE = 0x20
    USER_MANAGE = 0x40
    SUPERADMIN = 0x200
