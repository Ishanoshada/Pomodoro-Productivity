# Productivity Application - Cosmic Theam


## Table of Contents
- [Overview](#overview)
- [Project Structure](#project-structure)
- [Features](#features)
    - [Task Management](#task-management)
    - [Pomodoro Timer](#pomodoro-timer)
    - [Analytics Dashboard](#analytics-dashboard)
    - [Responsive & Cosmic UI](#responsive--cosmic-ui)
- [Technology Stack](#technology-stack)
    - [Backend](#backend)
    - [Frontend](#frontend)
    - [Database](#database)
- [Setup & Installation](#setup--installation)
- [Demo](#demo)
- [Code Structure](#code-structure)
- [Routes Overview](#routes-overview)
- [Usage Guidelines](#usage-guidelines)
- [Contributing & License](#contributing--license)

## Overview
The Cosmic Productivity Application is a Flask-based web app designed to help users manage tasks, track productivity with a space-themed Pomodoro timer, and view detailed analytics of task performance and work sessions. This system integrates task management, customizable Pomodoro sessions, and dynamic analytics visualizations using Chart.js.


![diagram](/diagram.svg)


## Project Structure
```
project/
├── api/
│   ├── static/
│   │   ├── css/
│   │   │   ├── style.css
│   │   │   └── pomodoro.css
│   │   ├── js/
│   │   │   ├── main.js
│   │   │   └── pomodoro.js
│   │   └── img/
│   ├── templates/
│   │   ├── base.html
│   │   ├── dashboard.html 
│   │   ├── pomodoro.html
│   │   ├── analytics.html
│   │   ├── index.html
│   │   ├── login.html
│   │   └── register.html
│   ├── app.py
├── .env.example ( rename to .env )
├── .gitignore
└── requirements.txt
```
## Features

### Task Management
- Create, update, complete, and delete tasks.
- Include details such as title, description, priority, date ranges, and tags.
- Visual indicators like completion labels and priority borders improve usability.

### Pomodoro Timer
- Customize durations for work sessions, short breaks, and long breaks.
- Real-time countdown and interactive controls (start, pause, reset).
- Display current task info and log session history.
- Engaging animations (pulsating effects and break prompts) signal session completions.

### Analytics Dashboard
- View productivity metrics, including total completed tasks, session counts, and work/break durations.
- Dynamic charts for task completion trends, daily session distribution, and time allocation per tag.
- Aggregates data from MongoDB to present up-to-date statistics.

### Responsive & Cosmic UI
- Custom CSS with space-inspired color schemes and animations.
- Mobile-friendly layouts with smooth UI interactions and hover effects.
- Cosmic visual elements such as rotating planets, shooting stars, and immersive backgrounds.

## Technology Stack

### Backend
- Python with Flask framework
- MongoDB connectivity via flask-pymongo
- Security and session management provided by Werkzeug

### Frontend
- HTML templating with Jinja2
- Custom CSS for a cosmic aesthetic, including keyframe animations
- JavaScript for timer control, DOM manipulation, and Chart.js integration

### Database
- MongoDB serves as the primary data store for tasks and work sessions


## Setup & Installation
1. **Clone the repository** from GitHub:
    ```bash
    git clone https://github.com/ishanoshada/Pomodoro-Productivity.git
    cd Pomodoro-Productivity
    ```
2. **Set up your environment**:
     - Create a virtual environment.
     - Install dependencies using:
         ```
         pip install -r requirements.txt
         ```
3. **Configure Environment Variables**:
     - Create a `.env` file and set your `SECRET_KEY` and `MONGO_URI` as provided.
4. **Run the Application**:
     - Start the Flask development server:
         ```
         python api/app.py
         ```
5. **Access the App**:
     - Open your browser and navigate to `http://localhost:5000`.

## Demo

Experience the Cosmic Productivity Application in action:

![ss1](/ss1.png)
![ss2](/ss2.png)
![ss3](/ss3.png)
![ss4](/ss4.png)

Check out the live demo [here](https://pomodoro-productivity-time.vercel.app/).

Explore the intuitive dashboard, task management features, and the space-themed Pomodoro timer in real time.


## Code Structure
 
- **/api/app.py**:  
    Contains route handlers for the dashboard, analytics, Pomodoro timer, and user registration. Also includes business logic for tracking productivity metrics.

- **Templates (t/api/emplates/)**:  
    HTML files (e.g., dashboard.html, analytics.html, pomodoro.html, register.html) built with Jinja templating to structure the UI and integrate dynamic data.

- **Static Assets (/api/static/)**:
    - **CSS (/api/static/css/)**:  
        - Global stylesheet (style.css) and component-specific styles (pomodoro.css) utilizing CSS variables and animations.
    - **JavaScript (/api/static/js/)**:  
        - Handles application behavior (e.g., timer operations via pomodoro.js) and user interactions (e.g., background animations, modal control, and chart rendering).
    - Additional assets include images and audio files for notifications and UI enhancements.

- **Environment & Dependencies**:
    - A `.env` file stores sensitive credentials (SECRET_KEY, MONGO_URI).
    - `requirements.txt` lists dependencies such as Flask, flask-pymongo, and Werkzeug.

## Routes Overview

The Cosmic Productivity Application offers several Flask routes to handle both core functionality and supporting tasks:

- **/**  
        Landing page that redirects authenticated users to the dashboard.
- **/register**  
        Provides registration functionality for new users.

- **/login**  
        Authenticates users and creates sessions.

- **/logout**  
        Clears the session and logs out the user.

- **/dashboard**  
        Displays the user’s tasks, productivity stats, and current streak, along with detailed analytics.
- **/add_task**  
        Handles task creation, including title, description, priority, dates, and tags.

- **/complete_task/&lt;task_id&gt;**  
        Marks a specified task as complete.

- **/edit_task**  
        Allows modifications to task details such as date ranges and tags.

- **/delete_task/&lt;task_id&gt;**  
        Deletes a specified task.

- **/pomodoro**  
        Provides the Pomodoro timer interface where users can start, pause, and reset sessions.

- **/analytics**  
        Displays detailed analytics, including task trends, session distribution, and average session duration.

- **/get_task/&lt;task_id&gt;**  
        Returns task details in JSON format for asynchronous retrieval.

- **/record_session**  
        Receives and logs Pomodoro session data (work, short break, long break) via AJAX.

- **/get_task_times/&lt;task_id&gt;**  
        Retrieves time allocation statistics (work and break durations) for a task.

- **/get_task_sessions/&lt;task_id&gt;**  
        Fetches the session history for a task, providing details like duration and completion time.

- **/populate_dummy_data**  
        Creates sample tasks and sessions for testing purposes.

Many of these routes enforce authentication and use session data to ensure the correct user environment. The endpoints support both full-page renders using Jinja templates and dynamic JSON responses for client-side interactions.


## Usage Guidelines

- Register or log in to begin managing tasks.
- Use the dashboard to add and organize tasks with attributes like tags, priorities, and date ranges.
- Launch the Pomodoro timer to stay focused while the app tracks work sessions.
- Refer to the analytics dashboard for detailed insights into your productivity trends.
- Enjoy the immersive cosmic-themed experience enhanced by custom animations and responsive design.

## Contributing & License

- Contributions are welcome. Please review the repository’s contribution guidelines for coding conventions and pull request protocols.
- Report issues and submit feature requests via the GitHub issue tracker.
- Developed by Ishan Oshada © 2025. All rights reserved – see the LICENSE file for complete license information.


**Repository Views** ![Views](https://profile-counter.glitch.me/pomodoro-pro/count.svg)
