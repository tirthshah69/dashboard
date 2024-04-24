from base import db, app
from flask_migrate import Migrate
migrate = Migrate(app, db)

class LoginVO(db.Model):
    __tablename__ = 'login_table'
    login_id = db.Column('login_id', db.Integer, autoincrement=True, primary_key=True)
    login_username = db.Column('login_username', db.String(255), nullable=False)
    login_password = db.Column('login_password', db.String(255), nullable=False)
    login_role = db.Column('login_role', db.String(255), nullable=False)
    is_deleted = db.Column('is_deleted', db.Boolean, default=False)
    created_on = db.Column('created_on', db.Integer, nullable = False)
    modified_on = db.Column('modified_on', db.Integer, nullable = True)

    def as_dict(self):
        return {
            'login_id':self.login_id,
            'login_username':self.login_username,
            'login_role':self.login_role,
            'is_deleted':self.is_deleted,
            'created_on':self.created_on,
            'modified_on':self.modified_on,
        }
        

class DetectionVO(db.Model):
    __tablename__ = 'detection_table'
    detection_id = db.Column('detection_id', db.Integer, autoincrement=True, primary_key=True)
    input_file_path = db.Column('input_file_path', db.String(255), nullable=False)
    output_file_path = db.Column('output_file_path', db.String(255), nullable=False)
    detection_type = db.Column('detection_type', db.String(255), nullable=False)
    detection_datetime = db.Column('detection_datetime', db.Integer, nullable=False)
    detection_stats = db.Column('detection_stats', db.String(255), nullable=False)
    is_deleted = db.Column('is_deleted', db.Boolean, default=False)
    created_on = db.Column('created_on', db.Integer, nullable=False)
    modified_on = db.Column('modified_on', db.Integer, nullable=False)
    created_by = db.Column('created_by', db.Integer,
                                   db.ForeignKey(LoginVO.login_id,
                                                 ondelete='CASCADE',
                                                 onupdate='CASCADE'),
                                   nullable=False)
    modified_by = db.Column('modified_by', db.Integer,
                                   db.ForeignKey(LoginVO.login_id,
                                                 ondelete='CASCADE',
                                                 onupdate='CASCADE'),
                                   nullable=False)

    def as_dict(self):
        return {
            'detection_id': self.detection_id,
            'detection_login_id': self.detection_login_id,
            'input_file_path': self.input_file_path,
            'output_file_path': self.output_file_path,
            'detection_type': self.detection_type,
            'is_deleted': self.is_deleted,
            'created_on': self.created_on,
            'modified_on': self.modified_on,
            'detection_datetime': self.detection_datetime,
            'detection_stats': self.detection_stats,
        }

with app.app_context():
    db.create_all()