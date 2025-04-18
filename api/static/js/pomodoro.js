document.addEventListener('DOMContentLoaded', () => {
    // Timer elements
    const timerDisplay = document.querySelector('.timer-display');
    const startBtn = document.querySelector('#start-btn');
    const pauseBtn = document.querySelector('#pause-btn');
    const resetBtn = document.querySelector('#reset-btn');
    const modeButtons = document.querySelectorAll('.mode-btn');
    const taskSelect = document.querySelector('#task-select');
    const taskDetails = document.querySelector('.selected-task-details');
    const sessionsCount = document.querySelector('.sessions-count');
    const sessionsList = document.querySelector('#sessions-list');
    const pomodoroUniverse = document.querySelector('.pomodoro-universe');
    const workTimeInput = document.querySelector('#work-time');
    const shortBreakTimeInput = document.querySelector('#short-break-time');
    const longBreakTimeInput = document.querySelector('#long-break-time');
    const breakModal = document.querySelector('#break-modal');
    const breakPrompt = document.querySelector('#break-prompt');
    const startBreakBtn = document.querySelector('#start-break-btn');
    const newSessionBtn = document.querySelector('#new-session-btn');
    const skipBreakBtn = document.querySelector('#skip-break-btn');
    const newWorkTimeInput = document.querySelector('#new-work-time');

    // Verify elements
    if (!timerDisplay) console.error('Timer display element not found');
    if (!startBtn) console.error('Start button not found');
    if (!pauseBtn) console.error('Pause button not found');
    if (!resetBtn) console.error('Reset button not found');
    if (!taskSelect) console.error('Task select element not found');
    if (!taskDetails) console.error('Task details element not found');
    if (!sessionsCount) console.error('Sessions count element not found');
    if (!sessionsList) console.error('Sessions list element not found');
    if (!pomodoroUniverse) console.error('Pomodoro universe element not found');
    if (!workTimeInput) console.error('Work time input not found');
    if (!shortBreakTimeInput) console.error('Short break time input not found');
    if (!longBreakTimeInput) console.error('Long break time input not found');
    if (!breakModal) console.error('Break modal not found');
    if (!breakPrompt) console.error('Break prompt not found');
    if (!startBreakBtn) console.error('Start break button not found');
    if (!newSessionBtn) console.error('New session button not found');
    if (!skipBreakBtn) console.error('Skip break button not found');
    if (!newWorkTimeInput) console.error('New work time input not found');

    // Timer state
    let timer;
    let isRunning = false;
    let secondsLeft = 25 * 60; // Default to 25 minutes
    let mode = 'work'; // Default mode
    let completedSessions = 0;
    let customDurations = {
        work: 25 * 60,
        'short-break': 5 * 60,
        'long-break': 15 * 60
    };

    // Default mode durations (in seconds)
    const defaultModes = {
        work: 25 * 60,
        'short-break': 5 * 60,
        'long-break': 15 * 60
    };

    // Audio for timer completion
    const audio = new Audio('/static/audio/timer-complete.mp3');

    // Reset task selector on page load
    function resetTaskSelector() {
        if (taskSelect) {
            taskSelect.value = ''; // Reset to "Select a task"
        }
        if (taskDetails) {
            taskDetails.innerHTML = `<p>Select a task to start focusing.</p>`;
        }
        // Reset durations to defaults
        if (workTimeInput) workTimeInput.value = 25;
        if (shortBreakTimeInput) shortBreakTimeInput.value = 5;
        if (longBreakTimeInput) longBreakTimeInput.value = 15;
        customDurations = { ...defaultModes };
        secondsLeft = customDurations[mode];
        updateTimerDisplay();
    }

    // Update custom durations based on input fields
    function updateCustomDurations() {
        if (!workTimeInput || !shortBreakTimeInput || !longBreakTimeInput) return;
        const workMinutes = parseInt(workTimeInput.value) || 25;
        const shortBreakMinutes = parseInt(shortBreakTimeInput.value) || 5;
        const longBreakMinutes = parseInt(longBreakTimeInput.value) || 15;

        customDurations = {
            work: Math.max(1, workMinutes) * 60,
            'short-break': Math.max(1, shortBreakMinutes) * 60,
            'long-break': Math.max(1, longBreakMinutes) * 60
        };

        // Update secondsLeft if not running
        if (!isRunning) {
            secondsLeft = customDurations[mode] || defaultModes[mode];
            updateTimerDisplay();
        }
    }

    // Update timer display
    function updateTimerDisplay() {
        if (!timerDisplay) return;
        const minutes = Math.floor(secondsLeft / 60);
        const seconds = secondsLeft % 60;
        timerDisplay.textContent = `${minutes.toString().padStart(2, '0')}:${seconds.toString().padStart(2, '0')}`;
    }

    // Update task times display for task cards and current task
    function updateTaskTimes(taskId, workTime, breakTime) {
        // Update task card
        const taskCard = document.querySelector(`.task-card[data-task-id="${taskId}"]`);
        if (taskCard) {
            const workTimeElement = taskCard.querySelector('.task-time .work-time');
            const breakTimeElement = taskCard.querySelector('.task-time .break-time');
            if (workTimeElement) {
                workTimeElement.textContent = `Work Time: ${(workTime / 60).toFixed(1)} hours`;
                workTimeElement.dataset.time = workTime;
            }
            if (breakTimeElement) {
                breakTimeElement.textContent = `Break Time: ${(breakTime / 60).toFixed(1)} hours`;
                breakTimeElement.dataset.time = breakTime;
            }
        }
        // Update current task if it matches
        if (taskSelect && taskSelect.value === taskId) {
            const currentWorkTimeElement = taskDetails.querySelector('.task-time .work-time');
            const currentBreakTimeElement = taskDetails.querySelector('.task-time .break-time');
            if (currentWorkTimeElement) {
                currentWorkTimeElement.textContent = `Work Time: ${(workTime / 60).toFixed(1)} hours`;
            }
            if (currentBreakTimeElement) {
                currentBreakTimeElement.textContent = `Break Time: ${(breakTime / 60).toFixed(1)} hours`;
            }
        }
    }

    // Record a completed session
    function recordSession() {
        const taskId = taskSelect ? taskSelect.value : null;
        // Calculate duration in minutes
        const duration = (customDurations[mode] || defaultModes[mode]) / 60;
        
        fetch('/record_session', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({
                mode: mode,
                task_id: taskId || null,
                duration: duration
            })
        })
        .then(response => response.json())
        .then(data => {
            if (data.error) {
                console.error('Failed to record session:', data.error);
            } else {
                console.log('Session recorded:', data);
                // Update task times if taskId exists
                if (taskId) {
                    // Fetch updated time spent via new endpoint
                    fetch(`/get_task_times/${taskId}`)
                        .then(response => response.json())
                        .then(timeData => {
                            if (!timeData.error) {
                                updateTaskTimes(taskId, timeData.work_time, timeData.break_time);
                            } else {
                                console.error('Error fetching task times:', timeData.error);
                            }
                        })
                        .catch(err => console.error('Error fetching task times:', err));
                }
            }
        })
        .catch(err => console.error('Error recording session:', err));
    }

    // Show break prompt modal
    function showBreakPrompt(nextMode, breakDuration) {
        return new Promise(resolve => {
            breakPrompt.textContent = `Would you like to take a ${nextMode.replace('-', ' ')} (${breakDuration} minutes) or start a new work session?`;
            breakModal.style.display = 'flex';
            startBreakBtn.onclick = () => {
                breakModal.style.display = 'none';
                resolve('break');
            };
            newSessionBtn.onclick = () => {
                const newDuration = parseInt(newWorkTimeInput.value);
                breakModal.style.display = 'none';
                if (newDuration && newDuration > 0) {
                    workTimeInput.value = newDuration;
                    updateCustomDurations();
                    resolve('new-session');
                } else {
                    resolve('skip');
                }
            };
            skipBreakBtn.onclick = () => {
                breakModal.style.display = 'none';
                resolve('skip');
            };
        });
    }

    // Start timer (now async)
    async function startTimer() {
        if (isRunning) return;
        if (mode === 'work' && (!taskSelect || !taskSelect.value)) {
            alert('Please select a task before starting a work session.');
            return;
        }
        isRunning = true;
        if (startBtn) startBtn.classList.add('active');
        if (pomodoroUniverse) pomodoroUniverse.classList.add('focus-mode');
        timer = setInterval(async () => {
            if (secondsLeft <= 0) {
                clearInterval(timer);
                isRunning = false;
                if (startBtn) startBtn.classList.remove('active');
                if (pomodoroUniverse) pomodoroUniverse.classList.remove('focus-mode');
                
                // Play audio
                audio.play().catch(err => console.warn('Audio playback failed:', err));
                
                // Increment sessions
                completedSessions++;
                if (sessionsCount) sessionsCount.textContent = completedSessions;

                // Add session to history
                if (sessionsList) {
                    const sessionItem = document.createElement('li');
                    sessionItem.innerHTML = `<span>${mode.charAt(0).toUpperCase() + mode.slice(1)} completed</span> <span class="session-time">${new Date().toLocaleTimeString()}</span>`;
                    sessionItem.classList.add('session-complete');
                    sessionsList.prepend(sessionItem);
                }

                // Record session in MongoDB
                recordSession();

                // Notify user
                if (Notification.permission === 'granted') {
                    new Notification(`${mode.charAt(0).toUpperCase() + mode.slice(1)} session completed!`, {
                        icon: '/static/img/logo.png'
                    });
                }

                // Prompt for break or new session if work session
                if (mode === 'work') {
                    const nextMode = completedSessions % 4 === 0 ? 'long-break' : 'short-break';
                    const breakDuration = customDurations[nextMode] / 60;
                    const userAction = await showBreakPrompt(nextMode, breakDuration);
                    if (userAction === 'break') {
                        switchMode(nextMode);
                        startTimer();
                    } else if (userAction === 'new-session') {
                        switchMode('work');
                        startTimer();
                    } else {
                        switchMode('work');
                        updateTimerDisplay();
                    }
                    return;
                }

                // Default to work mode if no action taken
                switchMode('work');
                updateTimerDisplay();
            } else {
                secondsLeft--;
                updateTimerDisplay();
            }
        }, 1000);
    }

    // Pause timer
    function pauseTimer() {
        if (!isRunning) return;
        clearInterval(timer);
        isRunning = false;
        if (startBtn) startBtn.classList.remove('active');
        if (pomodoroUniverse) pomodoroUniverse.classList.remove('focus-mode');
    }

    // Reset timer
    function resetTimer() {
        clearInterval(timer);
        isRunning = false;
        secondsLeft = customDurations[mode] || defaultModes[mode];
        if (startBtn) startBtn.classList.remove('active');
        if (pomodoroUniverse) pomodoroUniverse.classList.remove('focus-mode');
        updateTimerDisplay();
    }

    // Switch timer mode
    function switchMode(newMode) {
        mode = newMode;
        secondsLeft = customDurations[newMode] || defaultModes[newMode];
        modeButtons.forEach(btn => {
            btn.classList.toggle('active', btn.dataset.mode === newMode);
        });
        resetTimer();
    }

    // Initialize timer and reset task selector
    resetTaskSelector(); // Call reset on page load
    updateCustomDurations();
    updateTimerDisplay();

    // Event listeners for timer controls
    if (startBtn) startBtn.addEventListener('click', startTimer);
    if (pauseBtn) pauseBtn.addEventListener('click', pauseTimer);
    if (resetBtn) resetBtn.addEventListener('click', resetTimer);

    // Mode button listeners
    modeButtons.forEach(btn => {
        btn.addEventListener('click', () => {
            if (btn.dataset.mode !== mode) {
                switchMode(btn.dataset.mode);
            }
        });
    });

    // Task selection and custom time updates
    if (taskSelect) {
        taskSelect.addEventListener('change', () => {
            const taskId = taskSelect.value;
            if (taskId) {
                fetch(`/get_task/${taskId}`)
                    .then(response => response.json())
                    .then(data => {
                        if (data.error) {
                            taskDetails.innerHTML = `<p>Error: ${data.error}</p>`;
                        } else {
                            // Get work and break times from select option
                            const selectedOption = taskSelect.querySelector(`option[value="${taskId}"]`);
                            const workTime = parseFloat(selectedOption.dataset.workTime) || 0;
                            const breakTime = parseFloat(selectedOption.dataset.breakTime) || 0;
                            taskDetails.innerHTML = `
                                <h3>${data.title}</h3>
                                <p>${data.description || 'No description'}</p>
                                <div class="tags">${data.tags.map(tag => `<span class="tag">${tag}</span>`).join('')}</div>
                                <div class="task-time">
                                    <p class="work-time">Work Time: ${(workTime / 60).toFixed(1)} hours</p>
                                    <p class="break-time">Break Time: ${(breakTime / 60).toFixed(1)} hours</p>
                                </div>
                            `;
                        }
                    })
                    .catch(err => {
                        console.error('Fetch error:', err);
                        taskDetails.innerHTML = `<p>Error loading task</p>`;
                    });
                updateCustomDurations();
            } else {
                taskDetails.innerHTML = `<p>Select a task to start focusing.</p>`;
                // Reset to default durations
                customDurations = { ...defaultModes };
                workTimeInput.value = 25;
                shortBreakTimeInput.value = 5;
                longBreakTimeInput.value = 15;
                secondsLeft = customDurations[mode];
                updateTimerDisplay();
            }
        });
    }

    // Update custom durations on input change
    if (workTimeInput) workTimeInput.addEventListener('input', updateCustomDurations);
    if (shortBreakTimeInput) shortBreakTimeInput.addEventListener('input', updateCustomDurations);
    if (longBreakTimeInput) longBreakTimeInput.addEventListener('input', updateCustomDurations);

    // Request notification permission
    if (Notification.permission !== 'granted' && Notification.permission !== 'denied') {
        Notification.requestPermission();
    }
});


function updateSessionsList(taskId) {
    const sessionsList = document.getElementById('sessions-list');
    const sessionsCount = document.getElementById('sessions-count');
    
    if (!taskId) {
        sessionsList.innerHTML = '<p>No sessions completed yet.</p>';
        sessionsCount.textContent = '0 sessions';
        return;
    }

    fetch(`/get_task_sessions/${taskId}`)
        .then(response => response.json())
        .then(sessions => {
            if (sessions.length === 0) {
                sessionsList.innerHTML = '<p>No sessions completed yet.</p>';
                sessionsCount.textContent = '0 sessions';
                return;
            }

            sessionsCount.textContent = `${sessions.length} session${sessions.length === 1 ? '' : 's'}`;

            const sessionsHtml = sessions.map(session => `
                <div class="session-item ${session.mode.includes('break') ? 'break' : ''}">
                    <strong>${session.mode.charAt(0).toUpperCase() + session.mode.slice(1)}</strong>
                    <br>
                    Duration: ${session.duration} minutes
                    <br>
                    <small>Completed: ${new Date(session.completed_at).toLocaleString()}</small>
                </div>
            `).join('');

            sessionsList.innerHTML = sessionsHtml;
        })
        .catch(error => {
            console.error('Error fetching sessions:', error);
            sessionsList.innerHTML = '<p>Error loading sessions.</p>';
            sessionsCount.textContent = '0 sessions';
        });
}

document.getElementById('task-select').addEventListener('change', function() {
    const taskId = this.value;
    if (taskId) {
        fetch(`/get_task_sessions/${taskId}`)
            .then(response => response.json())
            .then(sessions => {
                const sessionsList = document.getElementById('sessions-list');
                if (sessions.length === 0) {
                    sessionsList.innerHTML = '<p>No sessions completed yet.</p>';
                    return;
                }
                
                updateSessionsList(taskId);
            })
            .catch(error => console.error('Error:', error));
    } else {
        document.getElementById('sessions-list').innerHTML = '<p>No sessions completed yet.</p>';
    }
});