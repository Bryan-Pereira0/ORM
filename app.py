from flask import Flask, request, jsonify
from flask_sqlalchemy import SQLAlchemy
from flask_marshmallow import Marshmallow
from marshmallow import fields, ValidationError
from password import my_password

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = f'mysql+mysqlconnector://root:{my_password}@localhost/fitness_center'
db = SQLAlchemy(app)
ma = Marshmallow(app)

class Members(db.Model):
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    name = db.Column(db.String(255), unique=True)
    age = db.Column(db.Integer)

class Workout_Session(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    member_id = db.Column(db.Integer, nullable=False)
    session_date = db.Column(db.Date, nullable=False)
    session_time = db.Column(db.Time, nullable=False)
    activity = db.Column(db.String(100), nullable=False)

class MemberSchema(ma.Schema):
    id = fields.Integer(required=True)
    name = fields.String(required=True)
    age = fields.Integer(required=True)
    class Meta:
        model = Members
        fields = ('id', 'name', 'age')
        
class WorkoutSessionSchema(ma.Schema):
    id = fields.Int(dump_only=True)
    member_id = fields.Int(required=True)
    session_date = fields.Date(required=True)
    session_time = fields.Time(required=True)
    activity = fields.Str(required=True)
    class Meta:
        model = Workout_Session
        fields = ('session_id', 'member_id', 'session_date', 'session_time', 'activity')

member_schema = MemberSchema()
members_schema = MemberSchema(many=True)
workout_session_schema = WorkoutSessionSchema()
workout_sessions_schema = WorkoutSessionSchema(many=True)

@app.route('/members', methods=['POST'])
def add_member():
    try:
        member_data = member_schema.load(request.json)
    except ValidationError as err:
        return jsonify(err.messages), 400
    new_member = Members(name=member_data['name'], age=member_data['age'])
    db.session.add(new_member)
    db.session.commit()
    return jsonify({'message': 'Customer added successfully.'}), 201

@app.route('/members', methods=['GET'])
def get_members():
    members = Members.query.all()
    return members_schema.jsonify(members)

@app.route('/members/<int:id>', methods=['PUT'])
def update_member(id):
    member = Members.query.get_or_404(id)
    try:
        member_data = member_schema.load(request.json)
    except ValidationError as err:
        return jsonify(err.messages), 400
    member.name = member_data['name']
    member.id = member_data['id']
    member.age = member_data['age']
    db.session.commit()
    return jsonify({'message': 'Member updated successfully.'}), 200

@app.route('/members/<int:id>', methods=['DELETE'])
def delete_member(id):
    member = Members.query.get_or_404(id)
    db.session.delete(member)
    db.session.commit()
    return jsonify({'message': 'Member deleted successfully'})

@app.route('/workouts', methods=['POST'])
def add_workout():
    try:
        workout_data = workout_session_schema.load(request.json)
    except ValidationError as err:
        return jsonify(err.messages), 400
    new_workout = Workout_Session(member_id=workout_data['member_id'], session_date=workout_data['session_date'], session_time=workout_data['session_time'], activity=workout_data['activity'])
    db.session.add(new_workout)
    db.session.commit()
    return jsonify({'message': 'Workout session added successfully'}), 201

@app.route('/workouts', methods=['GET'])
def get_workouts():
    workouts = Workout_Session.query.all()
    return workout_sessions_schema.jsonify(workouts)

@app.route('/workouts/<int:id>', methods=['PUT'])
def update_workout(id):
    workout = Workout_Session.query.get_or_404(id)
    try:
        workout_data = workout_session_schema.load(request.json)
    except ValidationError as err:
        return jsonify(err.messages), 400
    workout.member_id = workout_data['member_id']
    workout.session_date = workout_data['session_date']
    workout.session_time = workout_data['session_time']
    workout.activity = workout_data['activity']
    db.session.commit()
    return jsonify({'message': 'Workout session updated successfully'}), 200

@app.route('/workouts/<int:id>', methods=['DELETE'])
def delete_workout(id):
    workout = Workout_Session.query.get_or_404(id)
    db.session.delete(workout)
    db.session.commit()
    return jsonify({'message': 'Workout session deleted successfully'})

@app.route('/members/<int:member_id>/workouts', methods=['GET'])
def get_member_workouts(member_id):
    workouts = Workout_Session.query.filter_by(member_id=member_id).all()
    return workout_sessions_schema.jsonify(workouts)


if __name__ == '__main__':
    with app.app_context():
        db.create_all()
    app.run(debug=True)
    