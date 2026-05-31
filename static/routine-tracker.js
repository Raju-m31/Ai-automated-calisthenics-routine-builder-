class RoutineTracker {
    constructor() {
        this.currentWeek = 1;
        this.currentDay = 1;
        this.completedExercises = new Set();
        this.dayCompletedStatus = new Array(8).fill(false); // Index 1-7 for days
        this.totalExercises = 0;
        this.activeTimers = {}; // Store active timers
        this.goalSessionId = document.body.getAttribute('data-goal-session-id') || null;
        this.sessionKey = `routine_progress_${this.goalSessionId || 'default'}`; // Unique key per session
        
        // Will be set from global fourWeekPlan
        this.fourWeekPlan = window.fourWeekPlan || [];

        this.initializeElements();
        this.loadProgress();
        this.displayCurrentDay();
        this.updateProgress();
        this.bindEvents();
        this.loadGoalStatus();
        
        // Check if week 4 is complete
        this.checkWeek4Completion();
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
        this.displayWeek = document.getElementById('display-week');
        this.weekInDay = document.getElementById('week-in-day');
        this.dayProgressFill = document.getElementById('day-progress-fill');
        this.dayCompletionText = document.getElementById('day-completion-text');
        this.prevDayBtn = document.getElementById('prev-day');
        this.nextDayBtn = document.getElementById('next-day');
        this.prevWeekBtn = document.getElementById('prev-week');
        this.nextWeekBtn = document.getElementById('next-week');
        this.resetDayBtn = document.getElementById('reset-day');
        this.completeDayBtn = document.getElementById('complete-day');
    }

    bindEvents() {
        this.prevDayBtn.addEventListener('click', () => this.navigateDay(-1));
        this.nextDayBtn.addEventListener('click', () => this.navigateDay(1));
        this.prevWeekBtn?.addEventListener('click', () => this.navigateWeek(-1));
        this.nextWeekBtn?.addEventListener('click', () => this.navigateWeek(1));
        this.resetDayBtn.addEventListener('click', () => this.resetDay());
        this.completeDayBtn.addEventListener('click', () => this.completeDay());

        // Keyboard navigation
        document.addEventListener('keydown', (e) => {
            if (e.key === 'ArrowLeft') this.navigateDay(-1);
            if (e.key === 'ArrowRight') this.navigateDay(1);
        });
    }

    getCurrentWeekPlan() {
        if (!this.fourWeekPlan || !this.fourWeekPlan[this.currentWeek - 1]) {
            // Fallback to weeklyPlan if available
            return window.weeklyPlan || [];
        }
        return this.fourWeekPlan[this.currentWeek - 1];
    }

    displayCurrentDay() {
        const weekPlan = this.getCurrentWeekPlan();
        const dayData = weekPlan[this.currentDay - 1];
        if (!dayData) return;

        // Update day title
        this.dayTitle.textContent = `Week ${this.currentWeek}, Day ${this.currentDay}: ${dayData.name}`;

        // Update navigation
        this.displayDay.textContent = this.currentDay;
        this.displayWeek.textContent = this.currentWeek;
        this.weekInDay.textContent = this.currentWeek;
        this.prevDayBtn.disabled = this.currentDay === 1;
        this.nextDayBtn.disabled = this.currentDay === 7;
        this.prevWeekBtn.disabled = this.currentWeek === 1;
        this.nextWeekBtn.disabled = this.currentWeek === 4;

        // Display exercises
        this.displayExercises(dayData);

        // Update day completion status
        this.updateDayCompletionStatus();
    }

    displayExercises(dayData) {
        this.exercisesContainer.innerHTML = '';

        dayData.exercises.forEach((exercise, index) => {
            const exerciseId = `w${this.currentWeek}d${this.currentDay}-exercise${index}`;
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
        // Calculate progress as percentage of current week
        const weekPlan = this.getCurrentWeekPlan();
        let totalExercisesInWeek = 0;
        weekPlan.forEach(day => {
            totalExercisesInWeek += day.exercises.length;
        });

        // Count completed exercises in this week only
        let completedThisWeek = 0;
        this.completedExercises.forEach(exerciseId => {
            if (exerciseId.startsWith(`w${this.currentWeek}`)) {
                completedThisWeek++;
            }
        });

        const percentage = totalExercisesInWeek > 0 ? Math.round((completedThisWeek / totalExercisesInWeek) * 100) : 0;

        this.progressPercentage.textContent = `${percentage}%`;
        this.progressFill.style.width = `${percentage}%`;
        this.completedExercisesCount.textContent = completedThisWeek;
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
            this.saveProgress();
        }
    }

    navigateWeek(direction) {
        const newWeek = this.currentWeek + direction;
        if (newWeek >= 1 && newWeek <= 4) {
            this.currentWeek = newWeek;
            this.currentDay = 1; // Reset to day 1 when changing weeks
            this.dayCompletedStatus = new Array(8).fill(false); // Reset day completion for new week
            this.displayCurrentDay();
            this.updateProgress();
            this.saveProgress();
        }
    }

    checkWeek4Completion() {
        // Check if all 7 days of week 4 are completed
        const allDaysCompleted = this.dayCompletedStatus.slice(1, 8).every(status => status);
        if (this.currentWeek === 4 && allDaysCompleted && this.completedExercises.size > 0) {
            // Show 4-week review modal after a small delay
            setTimeout(() => this.showWeek4Review(), 1000);
        }
    }

    showWeek4Review() {
        // Check if review hasn't been shown yet
        if (localStorage.getItem(`${this.sessionKey}_review_shown`)) {
            return;
        }

        const goalSessionId = this.goalSessionId;
        const modal = document.createElement('div');
        modal.className = 'modal';
        modal.innerHTML = `
            <div class="modal-content" style="background: white; padding: 30px; border-radius: 10px; max-width: 500px; text-align: center; box-shadow: 0 4px 20px rgba(0,0,0,0.2);">
                <h2 style="margin-top: 0; color: #667eea;">🎉 4-Week Cycle Complete!</h2>
                <p style="font-size: 16px; color: #555;">Congratulations on finishing 4 weeks of training!</p>
                <p style="font-size: 14px; color: #999;">Would you like to continue with the same goal or switch to a new one?</p>
                <div style="display: grid; grid-template-columns: 1fr 1fr; gap: 10px; margin-top: 20px;">
                    <button onclick="window.location.href='/review-goal/${goalSessionId}'" style="padding: 12px; background: #667eea; color: white; border: none; border-radius: 5px; cursor: pointer; font-size: 14px;">
                        ✅ Continue Same Goal
                    </button>
                    <button onclick="window.location.href='/'" style="padding: 12px; background: #ff9500; color: white; border: none; border-radius: 5px; cursor: pointer; font-size: 14px;">
                        🔄 Switch Goal
                    </button>
                </div>
            </div>
        `;
        modal.style.cssText = 'position: fixed; top: 0; left: 0; width: 100%; height: 100%; background: rgba(0,0,0,0.5); display: flex; align-items: center; justify-content: center; z-index: 10000;';
        document.body.appendChild(modal);

        // Mark review as shown
        localStorage.setItem(`${this.sessionKey}_review_shown`, 'true');
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
        
        // Check if week 4 is complete
        this.checkWeek4Completion();
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
            currentWeek: this.currentWeek,
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
            this.currentWeek = progress.currentWeek || 1;
        }
    }
}

// Initialize the tracker when page loads
let routineTracker;
document.addEventListener('DOMContentLoaded', () => {
    routineTracker = new RoutineTracker();
});