class RoutineTracker {
    constructor() {
        this.currentDay = 1;
        this.completedExercises = new Set();
        this.dayCompletedStatus = new Array(8).fill(false); // Index 1-7 for days
        this.totalExercises = 0;
        this.activeTimers = {}; // Store active timers
        this.goalSessionId = document.body.getAttribute('data-goal-session-id') || null;
        this.sessionKey = `routine_progress_${this.goalSessionId || 'default'}`; // Unique key per session

        this.initializeElements();
        this.loadProgress();
        this.displayCurrentDay();
        this.updateProgress();
        this.bindEvents();
        this.loadGoalStatus();
    }

    loadGoalStatus() {
        if (!this.goalSessionId) return;
        
        fetch(`/goal-status/${this.goalSessionId}`)
            .then(res => res.json())
            .then(data => {
                const goalWidget = document.getElementById('goal-status-widget');
                if (goalWidget) {
                    goalWidget.innerHTML = `
                        <div style="background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); padding: 15px; border-radius: 8px; color: white;">
                            <h4 style="margin: 0 0 10px 0;">🎯 Goal: ${data.goal}</h4>
                            <div style="background: rgba(255,255,255,0.2); padding: 8px; border-radius: 4px; margin-bottom: 8px;">
                                <div style="font-size: 12px;">Week ${data.current_week} / 4</div>
                                <div style="height: 6px; background: rgba(255,255,255,0.3); border-radius: 3px; margin-top: 4px;">
                                    <div style="height: 100%; width: ${(data.current_week/4)*100}%; background: #4CAF50; border-radius: 3px;"></div>
                                </div>
                            </div>
                            <p style="margin: 0; font-size: 11px;">⏰ Next review in ${data.time_until_review} days</p>
                        </div>
                    `;
                }
            })
            .catch(err => console.log('Goal tracking unavailable'));
    }

    initializeElements() {
        this.dayTitle = document.getElementById('day-title');
        this.exercisesContainer = document.getElementById('exercises-container');
        this.progressPercentage = document.querySelector('.progress-percentage');
        this.progressFill = document.getElementById('progress-fill');
        this.completedExercisesCount = document.getElementById('completed-exercises');
        this.totalExercisesCount = document.getElementById('total-exercises');
        this.currentDayDisplay = document.getElementById('current-day');
        this.displayDay = document.getElementById('display-day');
        this.dayProgressFill = document.getElementById('day-progress-fill');
        this.dayCompletionText = document.getElementById('day-completion-text');
        this.prevDayBtn = document.getElementById('prev-day');
        this.nextDayBtn = document.getElementById('next-day');
        this.resetDayBtn = document.getElementById('reset-day');
        this.completeDayBtn = document.getElementById('complete-day');
    }

    bindEvents() {
        this.prevDayBtn.addEventListener('click', () => this.navigateDay(-1));
        this.nextDayBtn.addEventListener('click', () => this.navigateDay(1));
        this.resetDayBtn.addEventListener('click', () => this.resetDay());
        this.completeDayBtn.addEventListener('click', () => this.completeDay());

        // Keyboard navigation
        document.addEventListener('keydown', (e) => {
            if (e.key === 'ArrowLeft') this.navigateDay(-1);
            if (e.key === 'ArrowRight') this.navigateDay(1);
        });
    }

    displayCurrentDay() {
        const dayData = weeklyPlan[this.currentDay - 1];
        if (!dayData) return;

        // Update day title
        this.dayTitle.textContent = `Day ${this.currentDay}: ${dayData.name}`;

        // Update navigation
        this.displayDay.textContent = this.currentDay;
        this.prevDayBtn.disabled = this.currentDay === 1;
        this.nextDayBtn.disabled = this.currentDay === 7;

        // Display exercises
        this.displayExercises(dayData);

        // Update day completion status
        this.updateDayCompletionStatus();
    }

    displayExercises(dayData) {
        this.exercisesContainer.innerHTML = '';

        dayData.exercises.forEach((exercise, index) => {
            const exerciseId = `day${this.currentDay}-exercise${index}`;
            const isCompleted = this.completedExercises.has(exerciseId);

            const exerciseElement = document.createElement('div');
            exerciseElement.className = `exercise-item ${isCompleted ? 'completed' : ''}`;
            exerciseElement.innerHTML = `
                <div class="exercise-header">
                    <div class="exercise-info">
                        <div class="exercise-name">${exercise.name}</div>
                        <div class="exercise-details">
                            <span class="sets">${exercise.sets} sets</span>
                            <span class="reps">${exercise.reps}</span>
                            <span class="rest">Rest: ${exercise.rest}</span>
                        </div>
                    </div>
                    <div class="exercise-actions">
                        <label class="checkbox-container">
                            <input type="checkbox" id="${exerciseId}" ${isCompleted ? 'checked' : ''}>
                            <span class="checkmark"></span>
                        </label>
                    </div>
                </div>
                <div class="exercise-notes">
                    <div class="exercise-timer" id="timer-${exerciseId}">
                        <button class="timer-btn" data-exercise-id="${exerciseId}" data-rest="${exercise.rest}">⏱️ Start Rest Timer</button>
                        <span class="timer-display">00:00</span>
                    </div>
                </div>
            `;

            // Add checkbox event listener
            const checkbox = exerciseElement.querySelector(`#${exerciseId}`);
            checkbox.addEventListener('change', (e) => {
                this.toggleExerciseCompletion(exerciseId, e.target.checked);
            });

            // Add timer button event listener
            const timerBtn = exerciseElement.querySelector('.timer-btn');
            timerBtn.addEventListener('click', () => {
                const rest = timerBtn.getAttribute('data-rest');
                this.startRestTimer(exerciseId, rest);
            });

            this.exercisesContainer.appendChild(exerciseElement);
        });

        // Update total exercises count
        this.totalExercises = dayData.exercises.length;
        this.totalExercisesCount.textContent = this.totalExercises;
    }

    startRestTimer(exerciseId, restTime) {
        // Parse rest time (e.g., "60s" -> 60, "90s" -> 90)
        const seconds = parseInt(restTime) || 60;
        
        // Stop any existing timer for this exercise
        if (this.activeTimers[exerciseId]) {
            clearInterval(this.activeTimers[exerciseId]);
        }

        let remaining = seconds;
        const timerDisplay = document.querySelector(`#timer-${exerciseId} .timer-display`);
        const timerBtn = document.querySelector(`#timer-${exerciseId} .timer-btn`);
        
        if (!timerDisplay) return;

        timerBtn.disabled = true;
        timerBtn.style.opacity = '0.5';

        const updateDisplay = () => {
            const mins = Math.floor(remaining / 60);
            const secs = remaining % 60;
            timerDisplay.textContent = `${mins.toString().padStart(2, '0')}:${secs.toString().padStart(2, '0')}`;
            
            // Change color based on remaining time
            if (remaining <= 5) {
                timerDisplay.style.color = '#ff6b6b';
            } else if (remaining <= 10) {
                timerDisplay.style.color = '#ffb800';
            } else {
                timerDisplay.style.color = '#4CAF50';
            }
        };

        updateDisplay();

        this.activeTimers[exerciseId] = setInterval(() => {
            remaining--;
            updateDisplay();

            if (remaining === 0) {
                clearInterval(this.activeTimers[exerciseId]);
                delete this.activeTimers[exerciseId];
                timerDisplay.textContent = '✅ Done!';
                timerDisplay.style.color = '#4CAF50';
                timerBtn.disabled = false;
                timerBtn.style.opacity = '1';
                
                // Play notification sound
                this.playNotification();
            }
        }, 1000);
    }

    playNotification() {
        try {
            const audioContext = new (window.AudioContext || window.webkitAudioContext)();
            const oscillator = audioContext.createOscillator();
            const gainNode = audioContext.createGain();
            
            oscillator.connect(gainNode);
            gainNode.connect(audioContext.destination);
            
            oscillator.frequency.value = 800;
            oscillator.type = 'sine';
            
            gainNode.gain.setValueAtTime(0.3, audioContext.currentTime);
            gainNode.gain.exponentialRampToValueAtTime(0.01, audioContext.currentTime + 0.5);
            
            oscillator.start(audioContext.currentTime);
            oscillator.stop(audioContext.currentTime + 0.5);
        } catch (e) {
            console.log('Audio notification not available');
        }
    }

    toggleExerciseCompletion(exerciseId, isCompleted) {
        if (isCompleted) {
            this.completedExercises.add(exerciseId);
        } else {
            this.completedExercises.delete(exerciseId);
        }

        // Update exercise visual state
        const exerciseElement = document.querySelector(`[id="${exerciseId}"]`).closest('.exercise-item');
        exerciseElement.classList.toggle('completed', isCompleted);

        this.saveProgress();
        this.updateProgress();
        this.updateDayCompletionStatus();
    }

    updateProgress() {
        const totalPossibleExercises = 7 * 4; // Assuming average 4 exercises per day
        const completedCount = this.completedExercises.size;
        const percentage = Math.round((completedCount / totalPossibleExercises) * 100);

        this.progressPercentage.textContent = `${percentage}%`;
        this.progressFill.style.width = `${percentage}%`;
        this.completedExercisesCount.textContent = completedCount;
    }

    updateDayCompletionStatus() {
        const dayExercises = document.querySelectorAll('.exercise-item input[type="checkbox"]');
        const completedInDay = document.querySelectorAll('.exercise-item.completed input[type="checkbox"]:checked').length;
        const totalInDay = dayExercises.length;

        const dayPercentage = totalInDay > 0 ? Math.round((completedInDay / totalInDay) * 100) : 0;
        this.dayProgressFill.style.width = `${dayPercentage}%`;
        this.dayCompletionText.textContent = `${completedInDay} of ${totalInDay} exercises completed`;

        // Update day completion status
        this.dayCompletedStatus[this.currentDay] = completedInDay === totalInDay && totalInDay > 0;

        // Update weekly overview
        this.updateWeeklyOverview();
    }

    updateWeeklyOverview() {
        for (let day = 1; day <= 7; day++) {
            const dayCard = document.querySelector(`.week-day-card[data-day="${day}"]`);
            if (dayCard) {
                const isCompleted = this.dayCompletedStatus[day];
                const isCurrent = day === this.currentDay;

                dayCard.className = `week-day-card ${isCompleted ? 'completed' : ''} ${isCurrent ? 'current' : ''}`;

                const statusElement = dayCard.querySelector('.week-day-status');
                if (statusElement) {
                    if (isCompleted) {
                        statusElement.textContent = '✅';
                    } else if (isCurrent) {
                        statusElement.textContent = '🎯';
                    } else if (day < this.currentDay) {
                        statusElement.textContent = '⏳';
                    } else {
                        statusElement.textContent = '🔒';
                    }
                }
            }
        }
    }

    navigateDay(direction) {
        const newDay = this.currentDay + direction;
        if (newDay >= 1 && newDay <= 7) {
            this.currentDay = newDay;
            this.currentDayDisplay.textContent = this.currentDay;
            this.displayCurrentDay();
        }
    }

    resetDay() {
        if (confirm('Are you sure you want to reset all exercises for this day?')) {
            // Remove all completions for current day
            const dayExercises = document.querySelectorAll('.exercise-item input[type="checkbox"]');
            dayExercises.forEach(checkbox => {
                const exerciseId = checkbox.id;
                this.completedExercises.delete(exerciseId);
                checkbox.checked = false;
                checkbox.closest('.exercise-item').classList.remove('completed');
            });

            this.dayCompletedStatus[this.currentDay] = false;
            this.saveProgress();
            this.updateProgress();
            this.updateDayCompletionStatus();
        }
    }

    completeDay() {
        // Mark all exercises in current day as completed
        const dayExercises = document.querySelectorAll('.exercise-item input[type="checkbox"]:not(:checked)');
        dayExercises.forEach(checkbox => {
            const exerciseId = checkbox.id;
            this.completedExercises.add(exerciseId);
            checkbox.checked = true;
            checkbox.closest('.exercise-item').classList.add('completed');
        });

        this.dayCompletedStatus[this.currentDay] = true;
        this.saveProgress();
        this.updateProgress();
        this.updateDayCompletionStatus();

        // Show success message
        this.showNotification('Day completed! Great work! 🎉');
    }

    startTimer(exerciseId, sets) {
        const timerDisplay = document.querySelector(`#timer-${exerciseId} .timer-display`);
        const timerBtn = document.querySelector(`#timer-${exerciseId} .timer-btn`);

        if (this.currentTimer) {
            clearInterval(this.currentTimer);
        }

        let timeLeft = 90; // 90 seconds rest between sets
        timerBtn.textContent = '⏸️ Pause Timer';
        timerBtn.onclick = () => this.pauseTimer();

        this.currentTimer = setInterval(() => {
            const minutes = Math.floor(timeLeft / 60);
            const seconds = timeLeft % 60;
            timerDisplay.textContent = `${minutes.toString().padStart(2, '0')}:${seconds.toString().padStart(2, '0')}`;

            if (timeLeft <= 0) {
                clearInterval(this.currentTimer);
                timerDisplay.textContent = 'Rest Complete!';
                timerBtn.textContent = '⏱️ Start Next Set';
                timerBtn.onclick = () => this.startTimer(exerciseId, sets);

                // Play notification sound (if supported)
                if ('vibrate' in navigator) {
                    navigator.vibrate(200);
                }
            }
            timeLeft--;
        }, 1000);
    }

    pauseTimer() {
        if (this.currentTimer) {
            clearInterval(this.currentTimer);
            this.currentTimer = null;
            document.querySelector('.timer-btn').textContent = '▶️ Resume Timer';
            document.querySelector('.timer-btn').onclick = () => this.resumeTimer();
        }
    }

    resumeTimer() {
        // This would need to be implemented with saved time
        this.showNotification('Timer resumed');
    }

    showNotification(message) {
        // Create notification element
        const notification = document.createElement('div');
        notification.className = 'notification';
        notification.textContent = message;

        document.body.appendChild(notification);

        // Animate in
        setTimeout(() => notification.classList.add('show'), 100);

        // Remove after 3 seconds
        setTimeout(() => {
            notification.classList.remove('show');
            setTimeout(() => document.body.removeChild(notification), 300);
        }, 3000);
    }

    saveProgress() {
        const progress = {
            completedExercises: Array.from(this.completedExercises),
            dayCompletedStatus: this.dayCompletedStatus,
            currentDay: this.currentDay,
            lastUpdated: new Date().toISOString()
        };

        localStorage.setItem(this.sessionKey, JSON.stringify(progress));
    }

    loadProgress() {
        const saved = localStorage.getItem(this.sessionKey);
        if (saved) {
            const progress = JSON.parse(saved);
            this.completedExercises = new Set(progress.completedExercises || []);
            this.dayCompletedStatus = progress.dayCompletedStatus || new Array(8).fill(false);
            this.currentDay = progress.currentDay || 1;
        }
    }
}

// Initialize the tracker when page loads
let routineTracker;
document.addEventListener('DOMContentLoaded', () => {
    routineTracker = new RoutineTracker();
});