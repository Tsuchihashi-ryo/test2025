import pytest
import app as app_module  # To access module-level variables like tasks and next_task_id
from app import app as flask_app # The Flask app instance for the test client

# Helper function to reset tasks before each test
# This function is called by pytest if it's named setup_function or teardown_function
# and is defined in the global scope of the test file.
# However, for clarity and explicit control, we'll call it manually at the start of each test.
def reset_app_state():
    app_module.tasks.clear()
    app_module.next_task_id = 1


@pytest.fixture
def client():
    flask_app.config['TESTING'] = True
    flask_app.config['WTF_CSRF_ENABLED'] = False
    with flask_app.test_client() as client:
        # Before yielding the client, ensure the app state is clean
        # This is an alternative to calling reset_app_state() in each test,
        # making the tests themselves cleaner.
        reset_app_state()
        yield client

def test_homepage_loads(client):
    """Test that the homepage loads correctly."""
    # reset_app_state() # No longer needed here if done in fixture
    response = client.get('/')
    assert response.status_code == 200
    assert b"Task Management Tool" in response.data
    assert b"Current Tasks" in response.data

def test_add_task(client):
    """Test adding a new task."""
    # reset_app_state()
    response_add = client.post('/add', data={
        'title': 'Test Task 1',
        'description': 'This is a test description for task 1.'
    }, follow_redirects=True) # follow_redirects=True means response.status_code will be 200 if redirect target is OK
    
    assert response_add.status_code == 200 
    assert b"Test Task 1" in response_add.data
    assert b"This is a test description for task 1." in response_add.data
    
    assert len(app_module.tasks) == 1
    assert app_module.tasks[0]['title'] == 'Test Task 1'
    assert app_module.tasks[0]['id'] == 1 # next_task_id starts at 1

def test_view_task_on_edit_page(client):
    """Test viewing task details on the edit page."""
    # reset_app_state()
    client.post('/add', data={'title': 'View Me', 'description': 'Details here'}, follow_redirects=True)
    
    task_id = app_module.tasks[0]['id']
    response_edit_page = client.get(f'/edit/{task_id}')
    assert response_edit_page.status_code == 200
    # Check for values in form inputs
    assert b'value="View Me"' in response_edit_page.data 
    assert b'>Details here</textarea>' in response_edit_page.data

def test_update_task_details(client):
    """Test updating a task's title and description."""
    # reset_app_state()
    client.post('/add', data={'title': 'Original Title', 'description': 'Original Desc'}, follow_redirects=True)
    task_id = app_module.tasks[0]['id']

    response_edit = client.post(f'/edit/{task_id}', data={
        'title': 'Updated Title',
        'description': 'Updated Desc',
        'status': 'todo' 
    }, follow_redirects=True)
    assert response_edit.status_code == 200
    assert b"Updated Title" in response_edit.data
    assert b"Updated Desc" in response_edit.data
    
    assert len(app_module.tasks) == 1
    assert app_module.tasks[0]['title'] == 'Updated Title'
    assert app_module.tasks[0]['description'] == 'Updated Desc'

def test_update_task_status(client):
    """Test updating a task's status."""
    # reset_app_state()
    client.post('/add', data={'title': 'Status Test', 'description': 'Desc'}, follow_redirects=True)
    task_id = app_module.tasks[0]['id']
    
    assert app_module.tasks[0]['status'] == 'todo'

    response_update = client.get(f'/update_status/{task_id}/inprogress', follow_redirects=True)
    assert response_update.status_code == 200
    # The text displayed on the page for status is capitalized by the template filter
    assert b"Inprogress" in response_update.data 
    
    assert len(app_module.tasks) == 1
    assert app_module.tasks[0]['status'] == 'inprogress'

    response_update_done = client.get(f'/update_status/{task_id}/done', follow_redirects=True)
    assert response_update_done.status_code == 200
    assert b"Done" in response_update_done.data
    assert app_module.tasks[0]['status'] == 'done'

def test_delete_task(client):
    """Test deleting a task."""
    # reset_app_state()
    add_response = client.post('/add', data={'title': 'Delete Me', 'description': 'Desc'}, follow_redirects=True)
    assert b'Delete Me' in add_response.data 
    task_id = app_module.tasks[0]['id']
    assert len(app_module.tasks) == 1

    response_delete = client.get(f'/delete/{task_id}', follow_redirects=True)
    assert response_delete.status_code == 200
    assert b'Delete Me' not in response_delete.data 
    
    assert len(app_module.tasks) == 0

# Instructions to run tests:
# 1. Make sure Flask and pytest are installed:
#    pip install Flask pytest
# 2. Navigate to the root directory of the project in your terminal (where app.py and test_app.py are).
# 3. Run the command:
#    pytest
#
# The `reset_app_state()` function is now called within the `client` fixture,
# ensuring a clean state for each test that uses the client.
