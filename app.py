from flask import Flask, request, jsonify, make_response
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_marshmallow import Marshmallow
from marshmallow import fields

app = Flask(__name__)

app.config['SECRET_KEY'] = 'thisisasecretkey'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite://///home/mostafa/Desktop/Flask tests/flask-test/todo.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy()
ma: Marshmallow = Marshmallow()

db = SQLAlchemy(app)
migrate = Migrate(app, db)
ma = Marshmallow(app)


class RoleModel(db.Model):
    __tablename__ = "role"
    id = db.Column(db.Integer, primary_key=True)
    role_name = db.Column(db.String(50))

    def save(self):
        db.session.add(self)
        db.session.commit()


class UserModel(db.Model):
    __tablename__ = "user"
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(50))
    roles = db.relationship('RoleModel', secondary='user_role',
                            backref=db.backref('users'))

    def save(self):
        db.session.add(self)
        db.session.commit()


class UserRoleModel(db.Model):
    __tablename__ = "user_role"
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    role_id = db.Column(db.Integer, db.ForeignKey('role.id'))

    def save(self):
        db.session.add(self)
        db.session.commit()


class RoleModelSchema(ma.ModelSchema):
    class Meta:
        model = RoleModel


class UserRoleModelSchema(ma.ModelSchema):
    class Meta:
        model = UserRoleModel


class UserModelSchema(ma.ModelSchema):
    roles = fields.Nested(RoleModelSchema, many=True)

    class Meta:
        model = UserModel


role_schema = RoleModelSchema()
roles_schema = RoleModelSchema(many=True)

user_schema = UserModelSchema()
users_schema = UserModelSchema(many=True)

user_role_schema = UserModelSchema()
users_role_schema = UserModelSchema(many=True)


@app.route('/role/post', methods=['POST'])
def role_post():
    json_data = request.get_json(force=True)
    print(json_data)

    role, errors = role_schema.load(json_data, partial=True)
    role.save()
    data = role_schema.dump(role).data
    return jsonify(data)
    # return {'data': role_json}, 200


@app.route('/role/get', methods=['GET'])
def role_get():
    roles = RoleModel.query.all()
    if roles is None:
        return {"error": "no data found"}, 404
    roles_json = roles_schema.dump(roles).data
    return jsonify(roles_json), 200


@app.route('/user/post', methods=['POST'])
def user_post():
    json_data = request.get_json(force=True)
    user, errors = user_schema.load(json_data, partial=True)
    user.save()

    user_json = user_schema.dump(user).data
    return jsonify(user_json), 200


@app.route('/user/get', methods=['GET'])
def user_get():
    users = UserModel.query.all()
    users_json = users_schema.dump(users).data
    return jsonify(users_json), 200


@app.route('/user-role/post', methods=['POST'])
def user_role_post():
    json_data = request.get_json(force=True)
    user_role, errors = user_role_schema.load(json_data, partial=True)
    user_role.save()

    user_role_json = user_role_schema.dump(user_role).data
    return jsonify(user_role_json), 200


@app.route('/user-role/get', methods=['GET'])
def user_role_get():
    user_roles = UserRoleModel.query.all()
    users_role_json = users_role_schema.dump(user_roles).data
    return jsonify(users_role_json), 200


if __name__ == "__main__":
    app.run(debug=True)
