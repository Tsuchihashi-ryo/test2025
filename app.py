from flask import Flask, render_template, request, redirect, url_for

app = Flask(__name__)

tasks = []
next_task_id = 1

@app.route('/')
def index():
    return render_template('index.html', tasks=tasks)

@app.route('/add', methods=['GET', 'POST'])
def add_task():
    global next_task_id
    if request.method == 'POST':
        title = request.form['title']
        description = request.form['description']
        new_task = {
            'id': next_task_id,
            'title': title,
            'description': description,
            'status': 'todo'
        }
        tasks.append(new_task)
        next_task_id += 1
        return redirect(url_for('index'))
    return render_template('add_task.html')

@app.route('/edit/<int:task_id>', methods=['GET', 'POST'])
def edit_task(task_id):
    task = next((task for task in tasks if task['id'] == task_id), None)
    if not task:
        return "Task not found", 404
    
    if request.method == 'POST':
        task['title'] = request.form['title']
        task['description'] = request.form['description']
        task['status'] = request.form['status']
        return redirect(url_for('index'))
    
    return render_template('edit_task.html', task=task)

@app.route('/update_status/<int:task_id>/<string:new_status>', methods=['GET']) # Changed to GET for simplicity for now
def update_status(task_id, new_status):
    task = next((task for task in tasks if task['id'] == task_id), None)
    if not task:
        return "Task not found", 404
    
    task['status'] = new_status
    return redirect(url_for('index'))

@app.route('/delete/<int:task_id>', methods=['GET']) # Using GET for simplicity
def delete_task(task_id):
    global tasks
    task_to_delete = next((task for task in tasks if task['id'] == task_id), None)
    if task_to_delete:
        tasks.remove(task_to_delete)
    # If task not found, it will just redirect to index without error, which is acceptable for now.
    return redirect(url_for('index'))

if __name__ == '__main__':
    app.run(debug=True)
