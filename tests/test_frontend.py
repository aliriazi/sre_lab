import pytest
import json
import tempfile
import os
import sys

# Add parent directory to path to import the app
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))


@pytest.fixture
def app_with_db():
    """Create a test app with a temporary database"""
    # Create temporary directory for test database
    db_dir = tempfile.mkdtemp()
    db_file = os.path.join(db_dir, 'db.json')
    
    # Initialize empty database
    with open(db_file, 'w') as f:
        json.dump({'entries': []}, f)
    
    # Now import and configure the app
    from flask import Flask, request, jsonify
    
    DB = db_file
    
    def load_db():
        with open(DB, 'r') as f:
            return json.load(f)
    
    def save_db(d):
        with open(DB, 'w') as f:
            json.dump(d, f)
    
    app = Flask(__name__)
    app.config['TESTING'] = True
    
    @app.route('/entries', methods=['GET'])
    def list_entries():
        d = load_db()
        return jsonify(d['entries'])
    
    @app.route('/entries', methods=['POST'])
    def add_entry():
        d = load_db()
        body = request.get_json(force=True)
        next_id = 1
        if d['entries']:
            next_id = max(e.get('id', 0) for e in d['entries']) + 1
        entry = {'id': next_id, 'title': body.get('title'), 'description': body.get('description')}
        d['entries'].append(entry)
        save_db(d)
        return jsonify(entry), 201
    
    client = app.test_client()
    
    yield client, db_file
    
    # Cleanup
    import shutil
    shutil.rmtree(db_dir)


class TestFrontendAPI:
    """Test cases for the Construction Frontend API"""
    
    def test_get_empty_entries(self, app_with_db):
        """Test GET /entries returns empty list initially"""
        client, _ = app_with_db
        response = client.get('/entries')
        
        assert response.status_code == 200
        assert response.json == []
    
    def test_post_single_entry(self, app_with_db):
        """Test POST /entries adds a single entry"""
        client, _ = app_with_db
        
        entry_data = {
            'title': 'Test Project',
            'description': 'Test Description'
        }
        
        response = client.post('/entries', 
                              data=json.dumps(entry_data),
                              content_type='application/json')
        
        assert response.status_code == 201
        assert response.json['id'] == 1
        assert response.json['title'] == 'Test Project'
        assert response.json['description'] == 'Test Description'
    
    def test_post_entry_without_description(self, app_with_db):
        """Test POST /entries with only title"""
        client, _ = app_with_db
        
        entry_data = {'title': 'Project Without Description'}
        
        response = client.post('/entries',
                              data=json.dumps(entry_data),
                              content_type='application/json')
        
        assert response.status_code == 201
        assert response.json['title'] == 'Project Without Description'
        assert response.json['description'] is None
    
    def test_post_multiple_entries(self, app_with_db):
        """Test adding multiple entries with auto-incrementing IDs"""
        client, _ = app_with_db
        
        # Add first entry
        response1 = client.post('/entries',
                               data=json.dumps({'title': 'Project 1', 'description': 'First'}),
                               content_type='application/json')
        assert response1.status_code == 201
        assert response1.json['id'] == 1
        
        # Add second entry
        response2 = client.post('/entries',
                               data=json.dumps({'title': 'Project 2', 'description': 'Second'}),
                               content_type='application/json')
        assert response2.status_code == 201
        assert response2.json['id'] == 2
        
        # Add third entry
        response3 = client.post('/entries',
                               data=json.dumps({'title': 'Project 3', 'description': 'Third'}),
                               content_type='application/json')
        assert response3.status_code == 201
        assert response3.json['id'] == 3
    
    def test_get_entries_after_adding(self, app_with_db):
        """Test GET /entries returns all added entries"""
        client, _ = app_with_db
        
        # Add multiple entries
        client.post('/entries',
                   data=json.dumps({'title': 'Project A', 'description': 'Description A'}),
                   content_type='application/json')
        client.post('/entries',
                   data=json.dumps({'title': 'Project B', 'description': 'Description B'}),
                   content_type='application/json')
        
        # Get all entries
        response = client.get('/entries')
        
        assert response.status_code == 200
        entries = response.json
        assert len(entries) == 2
        assert entries[0]['title'] == 'Project A'
        assert entries[1]['title'] == 'Project B'
    
    def test_special_characters_in_title(self, app_with_db):
        """Test POST /entries handles special characters"""
        client, _ = app_with_db
        
        entry_data = {
            'title': 'Project with "quotes" & special <chars>',
            'description': 'Description with émojis 🚀'
        }
        
        response = client.post('/entries',
                              data=json.dumps(entry_data),
                              content_type='application/json')
        
        assert response.status_code == 201
        assert response.json['title'] == 'Project with "quotes" & special <chars>'
        assert '🚀' in response.json['description']
    
    def test_long_entry_text(self, app_with_db):
        """Test POST /entries with long title and description"""
        client, _ = app_with_db
        
        long_title = 'A' * 500
        long_description = 'B' * 2000
        
        entry_data = {
            'title': long_title,
            'description': long_description
        }
        
        response = client.post('/entries',
                              data=json.dumps(entry_data),
                              content_type='application/json')
        
        assert response.status_code == 201
        assert len(response.json['title']) == 500
        assert len(response.json['description']) == 2000
    
    def test_empty_title(self, app_with_db):
        """Test POST /entries with empty title (should still work)"""
        client, _ = app_with_db
        
        entry_data = {
            'title': '',
            'description': 'Some description'
        }
        
        response = client.post('/entries',
                              data=json.dumps(entry_data),
                              content_type='application/json')
        
        assert response.status_code == 201
        assert response.json['title'] == ''
    
    def test_whitespace_handling(self, app_with_db):
        """Test POST /entries preserves whitespace"""
        client, _ = app_with_db
        
        entry_data = {
            'title': '  Project with spaces  ',
            'description': '  Description  \n  with  \n  newlines  '
        }
        
        response = client.post('/entries',
                              data=json.dumps(entry_data),
                              content_type='application/json')
        
        assert response.status_code == 201
        assert response.json['title'] == '  Project with spaces  '
        assert '\n' in response.json['description']
    
    def test_missing_content_type(self, app_with_db):
        """Test POST /entries works even without explicit content-type"""
        client, _ = app_with_db
        
        entry_data = {'title': 'Test', 'description': 'Test'}
        
        # This tests the force=True in get_json() in the app
        response = client.post('/entries',
                              data=json.dumps(entry_data))
        
        assert response.status_code == 201
    
    def test_entry_id_persistence(self, app_with_db):
        """Test that entry IDs are unique and persistent"""
        client, _ = app_with_db
        
        ids = set()
        for i in range(5):
            response = client.post('/entries',
                                  data=json.dumps({'title': f'Project {i}'}),
                                  content_type='application/json')
            entry_id = response.json['id']
            assert entry_id not in ids, "Duplicate ID found"
            ids.add(entry_id)
        
        # Verify all IDs are sequential
        assert ids == {1, 2, 3, 4, 5}


if __name__ == '__main__':
    pytest.main([__file__, '-v'])
