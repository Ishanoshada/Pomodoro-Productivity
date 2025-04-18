import os
import atexit
from flask import Flask, render_template, request, redirect, url_for, session, flash, jsonify
from pymongo import MongoClient
from datetime import datetime, timedelta
from werkzeug.security import generate_password_hash, check_password_hash
from bson.objectid import ObjectId
from dotenv import load_dotenv
import random
from flask import request
from flask_minify import Minify

# Load environment variables from .env file
load_dotenv()

# Initialize Flask app

app = Flask(__name__)

Minify(app=app, html=True, js=True, cssless=True)

app.config['TEMPLATES_AUTO_RELOAD'] = True


secret_key = os.getenv('SECRET_KEY')
if not secret_key:
    print("Error: SECRET_KEY environment variable is missing. Please set it in your environment or in your .env file.")
    exit(1)
app.secret_key = secret_key

# Validate environment variables
if not app.secret_key:
    raise ValueError("No SECRET_KEY set in environment variables or .env file")

MONGO_URI = os.getenv('MONGO_URI')
if not MONGO_URI:
    raise ValueError("No MONGO_URI set in environment variables or .env file")

# Initialize MongoDB connection
try:
    client = MongoClient(MONGO_URI, serverSelectionTimeoutMS=5000)
    client.admin.command('ping')
    print("MongoDB connection successful!")
except Exception as e:
    raise Exception(f"MongoDB connection failed: {e}")

# Define database and collections
db = client.pomodoro_universe
users_collection = db.users
tasks_collection = db.tasks
sessions_collection = db.sessions



# Routes
@app.route('/')
def index():
    if 'user_id' in session:
        return redirect(url_for('dashboard'))
    return render_template('index.html')

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        existing_user = users_collection.find_one({'username': request.form['username']})
        if existing_user is None:
            hashed_password = generate_password_hash(request.form['password'])
            user_id = users_collection.insert_one({
                'username': request.form['username'],
                'password': hashed_password,
                'email': request.form['email'],
                'created_at': datetime.now(),
                   'best_streak': 0  
            }).inserted_id
            session['user_id'] = str(user_id)
            session['username'] = request.form['username']
            flash('Registration successful!', 'success')
            return redirect(url_for('dashboard'))
        flash('Username already exists!', 'error')
    return render_template('register.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        login_user = users_collection.find_one({'username': request.form['username']})
        if login_user and check_password_hash(login_user['password'], request.form['password']):
            session['user_id'] = str(login_user['_id'])
            session['username'] = login_user['username']
            flash('Login successful!', 'success')
            return redirect(url_for('dashboard'))
        flash('Invalid username/password combination', 'error')
    return render_template('login.html')

@app.route('/logout')
def logout():
    session.clear()
    flash('You have been logged out', 'info')
    return redirect(url_for('index'))

@app.route('/dashboard')
def dashboard():
    if 'user_id' not in session:
        flash('Please login first', 'error')
        return redirect(url_for('login'))
    
    today = datetime.now().strftime('%Y-%m-%d')
    
    # Get today's tasks
    tasks_cursor = tasks_collection.find({
        'user_id': session['user_id'],
        'date': today
    })
    tasks = list(tasks_cursor)
    
    # Calculate completed tasks for today
    completed_tasks = tasks_collection.count_documents({
        'user_id': session['user_id'],
        'date': today,
        'completed': True
    })
    
    # Calculate completion rate for today
    total_tasks = len(tasks)
    completion_rate = f"{(completed_tasks / total_tasks * 100) if total_tasks > 0 else 0:.1f}%"
    
    # Calculate streak
    streak = 0
    current_date = datetime.now()
    
    while True:
        check_date = (current_date - timedelta(days=streak)).strftime('%Y-%m-%d')
        completed_count = tasks_collection.count_documents({
            'user_id': session['user_id'],
            'date': check_date,
            'completed': True
        })
        total_count = tasks_collection.count_documents({
            'user_id': session['user_id'],
            'date': check_date
        })
        
        if total_count == 0 or completed_count == 0:
            break
            
        streak += 1
    
    # Calculate time spent per task for today
    time_spent = sessions_collection.aggregate([
        {
            '$match': {
                'user_id': session['user_id'],
                'completed_at': {
                    '$gte': datetime.strptime(today, '%Y-%m-%d'),
                    '$lt': datetime.strptime(today, '%Y-%m-%d') + timedelta(days=1)
                },
                'task_id': {'$ne': None}
            }
        },
        {
            '$group': {
                '_id': '$task_id',
                'work_time': {
                    '$sum': {
                        '$cond': [{'$eq': ['$mode', 'work']}, '$duration', 0]
                    }
                },
                'break_time': {
                    '$sum': {
                        '$cond': [{'$in': ['$mode', ['short-break', 'long-break']]}, '$duration', 0]
                    }
                }
            }
        }
    ])
    
    time_spent_dict = {str(item['_id']): {
        'work_time': item['work_time'],
        'break_time': item['break_time']
    } for item in time_spent}
    
    # Add time spent to tasks
    for task in tasks:
        task_id = str(task['_id'])
        task['work_time'] = time_spent_dict.get(task_id, {}).get('work_time', 0)
        task['break_time'] = time_spent_dict.get(task_id, {}).get('break_time', 0)
    

     # Calculate current streak
    current_streak = 0
    current_date = datetime.now()
    
    while True:
        check_date = (current_date - timedelta(days=current_streak)).strftime('%Y-%m-%d')
        completed_count = tasks_collection.count_documents({
            'user_id': session['user_id'],
            'date': check_date,
            'completed': True
        })
        total_count = tasks_collection.count_documents({
            'user_id': session['user_id'],
            'date': check_date
        })
        
        if total_count == 0 or completed_count == 0:
            break
            
        current_streak += 1
    
    # Update best streak if current streak is higher
    user = users_collection.find_one({'_id': ObjectId(session['user_id'])})
    best_streak = user.get('best_streak', 0)
    
    if current_streak > best_streak:
        users_collection.update_one(
            {'_id': ObjectId(session['user_id'])},
            {'$set': {'best_streak': current_streak}}
        )
        best_streak = current_streak
    
      # Calculate total work time today
    today_start = datetime.strptime(today, '%Y-%m-%d')
    today_end = today_start + timedelta(days=1)
    
    total_time = sessions_collection.aggregate([
        {
            '$match': {
                'user_id': session['user_id'],
                'completed_at': {
                    '$gte': today_start,
                    '$lt': today_end
                },
                'mode': 'work'  # Only count work sessions
            }
        },
        {
            '$group': {
                '_id': None,
                'total_minutes': {
                    '$sum': '$duration'
                }
            }
        }
    ])
    
    total_minutes = next(total_time, {}).get('total_minutes', 0)
    hours = total_minutes // 60
    minutes = total_minutes % 60
    total_time_display = f"{hours}h {minutes}m"


    return render_template(
        'dashboard.html',
        tasks=tasks,
        username=session['username'],
        completed_tasks=completed_tasks,
        completion_rate=completion_rate,
        streak=streak,
        best_streak=best_streak,
        total_time=total_time_display,
    )


# Modify the add_task route
@app.route('/add_task', methods=['POST'])
def add_task():
    if 'user_id' not in session:
        flash('Please login first', 'error')
        return redirect(url_for('login'))
    
    tags = request.form['tags'].split(',')
    tags = [tag.strip() for tag in tags if tag.strip()]
    
    start_date = request.form['start_date']
    end_date = request.form['end_date']
    
    # Create tasks for each day in the date range
    current_date = datetime.strptime(start_date, '%Y-%m-%d')
    end_date = datetime.strptime(end_date, '%Y-%m-%d')
    
    while current_date <= end_date:
        tasks_collection.insert_one({
            'user_id': session['user_id'],
            'title': request.form['title'],
            'description': request.form['description'],
            'tags': tags,
            'completed': False,
            'date': current_date.strftime('%Y-%m-%d'),
            'created_at': datetime.now(),
            'priority': request.form['priority'],
            'start_date': start_date,
            'end_date': end_date
        })
        current_date += timedelta(days=1)
    
    flash('Tasks added successfully for the date range!', 'success')
    return redirect(url_for('dashboard'))

@app.route('/complete_task/<task_id>')
def complete_task(task_id):
    if 'user_id' not in session:
        flash('Please login first', 'error')
        return redirect(url_for('login'))
    
    tasks_collection.update_one(
        {'_id': ObjectId(task_id), 'user_id': session['user_id']},
        {'$set': {'completed': True}}
    )
    
    flash('Task marked as complete!', 'success')
    return redirect(url_for('dashboard'))

@app.route('/edit_task', methods=['POST'])
def edit_task():
    if 'user_id' not in session:
        flash('Please login first', 'error')
        return redirect(url_for('login'))

    task_id = request.form['task_id']
    tags = request.form['tags'].split(',')
    tags = [tag.strip() for tag in tags if tag.strip()]

    # Retrieve the original task to get its start_date and end_date
    original_task = tasks_collection.find_one({'_id': ObjectId(task_id), 'user_id': session['user_id']})
    if not original_task:
        flash('Task not found', 'error')
        return redirect(url_for('dashboard'))

    # Get new start and end dates from the form
    new_start_date = request.form['start_date']
    new_end_date = request.form['end_date']

    # Delete all tasks from the previous recurring group (using the original start_date and end_date)
    tasks_collection.delete_many({
        'user_id': session['user_id'],
        'start_date': original_task['start_date'],
        'end_date': original_task['end_date']
    })

    # Insert new tasks for the new date range
    start_dt = datetime.strptime(new_start_date, '%Y-%m-%d')
    end_dt = datetime.strptime(new_end_date, '%Y-%m-%d')
    while start_dt <= end_dt:
        tasks_collection.insert_one({
            'user_id': session['user_id'],
            'title': request.form['title'],
            'description': request.form['description'],
            'tags': tags,
            'completed': False,
            'date': start_dt.strftime('%Y-%m-%d'),
            'created_at': datetime.now(),
            'priority': request.form['priority'],
            'start_date': new_start_date,
            'end_date': new_end_date
        })
        start_dt += timedelta(days=1)

    flash('Task updated successfully!', 'success')
    return redirect(url_for('dashboard'))

@app.route('/delete_task/<task_id>')
def delete_task(task_id):
    if 'user_id' not in session:
        flash('Please login first', 'error')
        return redirect(url_for('login'))
    
    tasks_collection.delete_one({'_id': ObjectId(task_id), 'user_id': session['user_id']})
    flash('Task deleted successfully!', 'success')
    return redirect(url_for('dashboard'))


@app.route('/pomodoro')
def pomodoro():
    if 'user_id' not in session:
        flash('Please login first', 'error')
        return redirect(url_for('login'))
    
    today = datetime.now().strftime('%Y-%m-%d')
    tasks_cursor = tasks_collection.find({
        'user_id': session['user_id'],
        'date': today,
        'completed': False
    })
    tasks = list(tasks_cursor)
    
    # Calculate time spent per task for today
    time_spent = sessions_collection.aggregate([
        {
            '$match': {
                'user_id': session['user_id'],
                'completed_at': {
                    '$gte': datetime.strptime(today, '%Y-%m-%d'),
                    '$lt': datetime.strptime(today, '%Y-%m-%d') + timedelta(days=1)
                },
                'task_id': {'$ne': None}
            }
        },
        {
            '$group': {
                '_id': '$task_id',
                'work_time': {
                    '$sum': {
                        '$cond': [{'$eq': ['$mode', 'work']}, '$duration', 0]
                    }
                },
                'break_time': {
                    '$sum': {
                        '$cond': [{'$in': ['$mode', ['short-break', 'long-break']]}, '$duration', 0]
                    }
                }
            }
        }
    ])
    
    time_spent_dict = {str(item['_id']): {
        'work_time': item['work_time'],
        'break_time': item['break_time']
    } for item in time_spent}
    
    # Add time spent to tasks
    for task in tasks:
        task_id = str(task['_id'])
        task['work_time'] = time_spent_dict.get(task_id, {}).get('work_time', 0)
        task['break_time'] = time_spent_dict.get(task_id, {}).get('break_time', 0)
    
    return render_template('pomodoro.html', tasks=tasks)

@app.route('/get_task/<task_id>')
def get_task(task_id):
    if 'user_id' not in session:
        return jsonify({'error': 'Unauthorized'}), 401
    
    task = tasks_collection.find_one({
        '_id': ObjectId(task_id),
        'user_id': session['user_id']
    })
    
    if not task:
        return jsonify({'error': 'Task not found'}), 404
    
    return jsonify({
        'title': task['title'],
        'description': task.get('description', ''),
        'tags': task.get('tags', [])
    })



@app.route('/analytics')
def analytics():
    if 'user_id' not in session:
        return redirect(url_for('login'))
    
    username = session.get('username', 'User')
    
    # Calculate basic stats
    stats = {
        'total_tasks': tasks_collection.count_documents({
            'user_id': session['user_id'],
            'completed': True
        }),
        'total_sessions': sessions_collection.count_documents({
            'user_id': session['user_id']
        }),
        'work_sessions': sessions_collection.count_documents({
            'user_id': session['user_id'],
            'mode': 'work'
        }),
        'break_sessions': sessions_collection.count_documents({
            'user_id': session['user_id'],
            'mode': {'$in': ['short-break', 'long-break']}
        })
    }
    
    # Total work and break times (last 30 days)
    thirty_days_ago = datetime.now() - timedelta(days=30)
    time_aggregate = sessions_collection.aggregate([
        {
            '$match': {
                'user_id': session['user_id'],
                'completed_at': {'$gte': thirty_days_ago}
            }
        },
        {
            '$group': {
                '_id': None,
                'total_work_time': {
                    '$sum': {
                        '$cond': [{'$eq': ['$mode', 'work']}, '$duration', 0]
                    }
                },
                'total_break_time': {
                    '$sum': {
                        '$cond': [{'$in': ['$mode', ['short-break', 'long-break']]}, '$duration', 0]
                    }
                }
            }
        }
    ])
    time_result = next(time_aggregate, {})
    stats['total_work_time'] = time_result.get('total_work_time', 0)  # In minutes
    stats['total_break_time'] = time_result.get('total_break_time', 0)  # In minutes
    
    # Task completion trend (last 7 days)
    trend_data = []
    for i in range(6, -1, -1):
        date = (datetime.now() - timedelta(days=i)).strftime('%Y-%m-%d')
        total = tasks_collection.count_documents({
            'user_id': session['user_id'],
            'created_at': {
                '$gte': datetime.strptime(date, '%Y-%m-%d'),
                '$lt': datetime.strptime(date, '%Y-%m-%d') + timedelta(days=1)
            }
        })
        completed = tasks_collection.count_documents({
            'user_id': session['user_id'],
            'completed': True,
            'completed_at': {
                '$gte': datetime.strptime(date, '%Y-%m-%d'),
                '$lt': datetime.strptime(date, '%Y-%m-%d') + timedelta(days=1)
            }
        })
        trend_data.append({
            'date': date,
            'total': total,
            'completed': completed
        })
    
    # Session trend (last 7 days)
    session_trend_data = []
    for i in range(6, -1, -1):
        date = (datetime.now() - timedelta(days=i)).strftime('%Y-%m-%d')
        work_sessions = sessions_collection.count_documents({
            'user_id': session['user_id'],
            'mode': 'work',
            'completed_at': {
                '$gte': datetime.strptime(date, '%Y-%m-%d'),
                '$lt': datetime.strptime(date, '%Y-%m-%d') + timedelta(days=1)
            }
        })
        break_sessions = sessions_collection.count_documents({
            'user_id': session['user_id'],
            'mode': {'$in': ['short-break', 'long-break']},
            'completed_at': {
                '$gte': datetime.strptime(date, '%Y-%m-%d'),
                '$lt': datetime.strptime(date, '%Y-%m-%d') + timedelta(days=1)
            }
        })
        session_trend_data.append({
            'date': date,
            'work_sessions': work_sessions,
            'break_sessions': break_sessions
        })
    
    # Time spent per task (last 30 days)
    task_times = sessions_collection.aggregate([
        {
            '$match': {
                'user_id': session['user_id'],
                'task_id': {'$ne': None},
                'completed_at': {'$gte': thirty_days_ago}
            }
        },
        {
            '$addFields': {
                'task_id_obj': {'$toObjectId': '$task_id'}  # Convert string task_id to ObjectId
            }
        },
        {
            '$group': {
                '_id': '$task_id_obj',
                'work_time': {
                    '$sum': {
                        '$cond': [{'$eq': ['$mode', 'work']}, '$duration', 0]
                    }
                },
                'break_time': {
                    '$sum': {
                        '$cond': [{'$in': ['$mode', ['short-break', 'long-break']]}, '$duration', 0]
                    }
                }
            }
        },
        {
            '$lookup': {
                'from': 'tasks',
                'localField': '_id',
                'foreignField': '_id',
                'as': 'task'
            }
        },
        {
            '$unwind': {
                'path': '$task',
                'preserveNullAndEmptyArrays': True
            }
        },
        {
            '$project': {
                'task_title': {'$ifNull': ['$task.title', 'Unknown Task']},
                'work_time': 1,
                'break_time': 1
            }
        },
        {
            '$sort': {'work_time': -1}
        }
    ])
    
    # Format time spent data
    time_spent_data = list(task_times)
   # print("Time spent data:", time_spent_data)
    if not time_spent_data:
        print("No time spent data found for tasks in last 30 days")
    
    # Time spent by tag (last 30 days)
    tag_time = sessions_collection.aggregate([
        {
            '$match': {
                'user_id': session['user_id'],
                'task_id': {'$ne': None},
                'completed_at': {'$gte': thirty_days_ago}
            }
        },
        {
            '$addFields': {
                'task_id_obj': {'$toObjectId': '$task_id'}  # Convert string task_id to ObjectId
            }
        },
        {
            '$lookup': {
                'from': 'tasks',
                'localField': 'task_id_obj',
                'foreignField': '_id',
                'as': 'task'
            }
        },
        {
            '$unwind': {
                'path': '$task',
                'preserveNullAndEmptyArrays': True
            }
        },
        {
            '$unwind': {
                'path': '$task.tags',
                'preserveNullAndEmptyArrays': True
            }
        },
        {
            '$group': {
                '_id': {
                    '$ifNull': ['$task.tags', 'Untagged']
                },
                'work_time': {
                    '$sum': {
                        '$cond': [{'$eq': ['$mode', 'work']}, '$duration', 0]
                    }
                },
                'break_time': {
                    '$sum': {
                        '$cond': [{'$in': ['$mode', ['short-break', 'long-break']]}, '$duration', 0]
                    }
                }
            }
        },
        {
            '$project': {
                'tag': '$_id',
                'work_time': 1,
                'break_time': 1,
                '_id': 0
            }
        },
        {
            '$sort': {'work_time': -1}
        }
    ])
    
    # Format tag time data
    tag_time_data = list(tag_time)
   # print("Tag time data:", tag_time_data)
    if not tag_time_data:
        print("No tag time data found for tasks in last 30 days")
    
    # Additional metrics
    avg_duration = sessions_collection.aggregate([
        {
            '$match': {
                'user_id': session['user_id'],
                'completed_at': {'$gte': thirty_days_ago}
            }
        },
        {
            '$group': {
                '_id': None,
                'avg_duration': {'$avg': '$duration'}
            }
        }
    ])
    avg_result = next(avg_duration, {})
    stats['avg_session_duration'] = avg_result.get('avg_duration', 0)  # In minutes
    
    day_counts = sessions_collection.aggregate([
        {
            '$match': {
                'user_id': session['user_id'],
                'mode': 'work',
                'completed_at': {'$gte': thirty_days_ago}
            }
        },
        {
            '$group': {
                '_id': {'$dayOfWeek': '$completed_at'},
                'count': {'$sum': 1}
            }
        },
        {
            '$sort': {'count': -1}
        },
        {
            '$limit': 1
        }
    ])
    day_map = {
        1: 'Sunday', 2: 'Monday', 3: 'Tuesday', 4: 'Wednesday',
        5: 'Thursday', 6: 'Friday', 7: 'Saturday'
    }
    day_result = next(day_counts, {})
    stats['most_productive_day'] = day_map.get(day_result.get('_id', 1), 'N/A')
    
    total_tasks = tasks_collection.count_documents({
        'user_id': session['user_id'],
        'created_at': {'$gte': thirty_days_ago}
    })
    completed_tasks = tasks_collection.count_documents({
        'user_id': session['user_id'],
        'completed': True,
        'created_at': {'$gte': thirty_days_ago}
    })
    stats['completion_rate'] = (completed_tasks / total_tasks * 100) if total_tasks > 0 else 0
    
    # Debug tasks
    sample_tasks = list(tasks_collection.find({
        'user_id': session['user_id'],
        '_id': {'$in': [ObjectId(task_id) for task_id in ['6801653c70d73aa057dd99ca', '680170bf951630c22a409690']]}
    }))
   # print("Sample tasks:", sample_tasks)
    
    return render_template('analytics.html',
                         username=username,
                         stats=stats,
                         trend_data=trend_data,
                         session_trend_data=session_trend_data,
                         time_spent_data=time_spent_data,
                         tag_time_data=tag_time_data)

@app.route('/record_session', methods=['POST'])
def record_session():
    if 'user_id' not in session:
        return jsonify({'error': 'Unauthorized'}), 401
    
    data = request.get_json()
    mode = data.get('mode')
    task_id = data.get('task_id')
    duration = data.get('duration')
    
    if not mode or mode not in ['work', 'short-break', 'long-break']:
        return jsonify({'error': 'Invalid mode'}), 400
    
    if not duration or not isinstance(duration, (int, float)) or duration <= 0:
        return jsonify({'error': 'Invalid duration'}), 400
    
    sessions_collection.insert_one({
        'user_id': session['user_id'],
        'mode': mode,
        'task_id': task_id if task_id else None,
        'duration': duration,
        'completed_at': datetime.now()
    })
    
    return jsonify({'status': 'success'})


@app.route('/get_task_times/<task_id>')
def get_task_times(task_id):
    if 'user_id' not in session:
        return jsonify({'error': 'Unauthorized'}), 401
    today = datetime.now().strftime('%Y-%m-%d')
    time_spent = sessions_collection.aggregate([
        {
            '$match': {
                'user_id': session['user_id'],
                'task_id': task_id,
                'completed_at': {
                    '$gte': datetime.strptime(today, '%Y-%m-%d'),
                    '$lt': datetime.strptime(today, '%Y-%m-%d') + timedelta(days=1)
                }
            }
        },
        {
            '$group': {
                '_id': '$task_id',
                'work_time': {
                    '$sum': {
                        '$cond': [{'$eq': ['$mode', 'work']}, '$duration', 0]
                    }
                },
                'break_time': {
                    '$sum': {
                        '$cond': [{'$in': ['$mode', ['short-break', 'long-break']]}, '$duration', 0]
                    }
                }
            }
        }
    ])
    result = next(time_spent, {})
    return jsonify({
        'work_time': result.get('work_time', 0),
        'break_time': result.get('break_time', 0)
    })

@app.route('/get_task_sessions/<task_id>')
def get_task_sessions(task_id):
    if 'user_id' not in session:
        return jsonify({'error': 'Unauthorized'}), 401
    
    sessions = sessions_collection.find({
        'user_id': session['user_id'],
        'task_id': task_id,
        'completed_at': {'$exists': True}
    }).sort('completed_at', -1)
    
    session_list = []
    for s in sessions:
        session_list.append({
            'mode': s['mode'],
            'duration': s['duration'],
            'completed_at': s['completed_at'].strftime('%Y-%m-%d %H:%M:%S')
        })
    
    return jsonify(session_list)


@app.before_request
def auth_middleware():
        public_endpoints = {'index', 'login', 'register', 'static'}
        if request.endpoint not in public_endpoints and 'user_id' not in session:
            flash("Please login first", "error")
            return redirect(url_for("login"))






@app.route('/populate_dummy_data')
def populate_dummy_data():
    if 'user_id' not in session:
        return redirect(url_for('login'))
    
    # Sample data pools
    titles = ["Python Study", "JavaScript Project", "Database Design", "API Development", 
             "UI/UX Research", "Code Review", "Bug Fixing", "Feature Implementation",
             "Documentation", "Testing"]
    
    descriptions = ["Learning scapy and network programming", 
                   "Building REST APIs with Flask",
                   "Implementing authentication system",
                   "Working on frontend components",
                   "Database optimization tasks"]
    
    tags_pool = ["work", "study", "coding", "design", "testing", "documentation"]
    priorities = ["low", "medium", "high"]
    
    # Generate 20 dummy tasks
    base_date = datetime(2025, 4, 18)
    user_id = session['user_id']
    
    for i in range(20):
        # Randomize dates
        start_date = base_date + timedelta(days=random.randint(0, 30))
        end_date = start_date + timedelta(days=random.randint(1, 7))
        
        # Random tags (1-3 tags per task)
        task_tags = random.sample(tags_pool, random.randint(1, 3))
        
        task = {
            '_id': ObjectId(),
            'user_id': user_id,
            'title': random.choice(titles),
            'description': random.choice(descriptions),
            'tags': task_tags,
            'completed': random.choice([True, False]),
            'date': "2025-04-18",
            'created_at': datetime.now(),
            'priority': random.choice(priorities),
            'start_date': start_date.strftime('%Y-%m-%d'),
            'end_date': end_date.strftime('%Y-%m-%d')
        }
        
        tasks_collection.insert_one(task)
    
    flash('20 dummy tasks have been created!', 'success')
    return redirect(url_for('dashboard'))













if __name__ == '__main__':
    app.run(debug=True)
















