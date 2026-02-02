from flask import Flask, request, jsonify
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
import os
import time

app = Flask(__name__)

# Database configuration
db_host = os.getenv('DB_HOST', 'postgres.observability.svc.cluster.local')
db_port = os.getenv('DB_PORT', '5432')
db_user = os.getenv('DB_USER', 'postgres')
db_password = os.getenv('DB_PASSWORD', 'postgrespassword')
db_name = os.getenv('DB_NAME', 'construction')

# Wait for database to be ready
max_retries = 30
retry_count = 0
while retry_count < max_retries:
    try:
        import psycopg2
        conn = psycopg2.connect(
            host=db_host,
            user=db_user,
            password=db_password,
            port=db_port
        )
        conn.close()
        break
    except:
        retry_count += 1
        if retry_count >= max_retries:
            print("Failed to connect to PostgreSQL after retries")
        else:
            time.sleep(1)

app.config['SQLALCHEMY_DATABASE_URI'] = f'postgresql://{db_user}:{db_password}@{db_host}:{db_port}/{db_name}'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)

class Project(db.Model):
    __tablename__ = 'projects'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(255), nullable=False)
    description = db.Column(db.Text)
    location = db.Column(db.String(255))
    manager = db.Column(db.String(255))
    status = db.Column(db.String(50), default='Planning')
    start_date = db.Column(db.Date)
    end_date = db.Column(db.Date)
    budget = db.Column(db.Float, default=0)
    spent = db.Column(db.Float, default=0)
    progress = db.Column(db.Integer, default=0)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    def to_dict(self):
        return {
            'id': self.id,
            'name': self.name,
            'description': self.description,
            'location': self.location,
            'manager': self.manager,
            'status': self.status,
            'start_date': self.start_date.isoformat() if self.start_date else None,
            'end_date': self.end_date.isoformat() if self.end_date else None,
            'budget': self.budget,
            'spent': self.spent,
            'progress': self.progress,
            'created_at': self.created_at.isoformat(),
            'updated_at': self.updated_at.isoformat()
        }

class ProjectLog(db.Model):
    __tablename__ = 'project_logs'
    id = db.Column(db.Integer, primary_key=True)
    project_id = db.Column(db.Integer, db.ForeignKey('projects.id'), nullable=False)
    action = db.Column(db.String(255))
    details = db.Column(db.Text)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

# Create tables
with app.app_context():
    db.create_all()

# Routes
@app.route('/')
def index():
    with open('/config/index.html', 'r') as f:
        return f.read()

@app.route('/api/projects', methods=['GET'])
def get_projects():
    projects = Project.query.all()
    return jsonify([p.to_dict() for p in projects])

@app.route('/api/projects', methods=['POST'])
def create_project():
    data = request.json
    project = Project(
        name=data.get('name'),
        description=data.get('description'),
        location=data.get('location'),
        manager=data.get('manager'),
        status=data.get('status', 'Planning'),
        start_date=data.get('start_date'),
        end_date=data.get('end_date'),
        budget=data.get('budget', 0),
        spent=data.get('spent', 0),
        progress=data.get('progress', 0)
    )
    db.session.add(project)
    db.session.commit()
    return jsonify(project.to_dict()), 201

@app.route('/api/projects/<int:id>', methods=['GET'])
def get_project(id):
    project = Project.query.get(id)
    if not project:
        return jsonify({'error': 'Not found'}), 404
    return jsonify(project.to_dict())

@app.route('/api/projects/<int:id>', methods=['PUT'])
def update_project(id):
    project = Project.query.get(id)
    if not project:
        return jsonify({'error': 'Not found'}), 404
    
    data = request.json
    project.name = data.get('name', project.name)
    project.description = data.get('description', project.description)
    project.location = data.get('location', project.location)
    project.manager = data.get('manager', project.manager)
    project.status = data.get('status', project.status)
    project.start_date = data.get('start_date', project.start_date)
    project.end_date = data.get('end_date', project.end_date)
    project.budget = data.get('budget', project.budget)
    project.spent = data.get('spent', project.spent)
    project.progress = data.get('progress', project.progress)
    project.updated_at = datetime.utcnow()
    
    db.session.commit()
    return jsonify(project.to_dict())

@app.route('/api/projects/<int:id>', methods=['DELETE'])
def delete_project(id):
    project = Project.query.get(id)
    if not project:
        return jsonify({'error': 'Not found'}), 404
    
    db.session.delete(project)
    db.session.commit()
    return '', 204

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=9898, debug=False)
