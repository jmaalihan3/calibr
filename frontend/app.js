/**
 * Academic Assessment System - Frontend Application Logic
 * 
 * This module handles:
 * - Application state management
 * - UI section switching (home -> exam -> results)
 * - API communication with backend
 * - Question rendering and navigation
 * - Results display
 * 
 * Architecture: Single-page application with client-side state
 */

// Application state
const state = {
    examId: null,               // Current exam ID from backend
    questions: [],              // Array of question objects
    currentQuestionIndex: 0,    // Index of current question (0-based)
    userAnswers: {}             // Map of questionId -> answerIndex
};

// API base URL
const API_BASE = '/api';


/**
 * Initialize application on page load.
 * Sets up event listeners for buttons.
 */
function init() {
    // Home section: Start exam button
    document.getElementById('start-btn').addEventListener('click', startExam);
    
    // Exam section: Navigation buttons
    document.getElementById('next-btn').addEventListener('click', nextQuestion);
    document.getElementById('submit-btn').addEventListener('click', submitExam);
    
    // Results section: New exam button
    document.getElementById('new-exam-btn').addEventListener('click', resetToHome);
    
    console.log('Application initialized');
}


/**
 * Show a specific section and hide others.
 * 
 * @param {string} sectionId - ID of section to show (home-section, exam-section, results-section)
 */
function showSection(sectionId) {
    // Hide all sections
    document.querySelectorAll('.section').forEach(section => {
        section.classList.remove('active');
    });
    
    // Show target section
    document.getElementById(sectionId).classList.add('active');
}


/**
 * Start a new exam by calling the API and loading questions.
 * Transitions from home to exam section.
 */
async function startExam() {
    const startBtn = document.getElementById('start-btn');
    startBtn.disabled = true;
    startBtn.textContent = 'Loading...';
    
    try {
        // Call API to start exam
        const response = await fetch(`${API_BASE}/exams/start`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({ num_questions: 5 })
        });
        
        if (!response.ok) {
            throw new Error(`Failed to start exam: ${response.statusText}`);
        }
        
        const data = await response.json();
        
        // Update state
        state.examId = data.exam_id;
        state.questions = data.questions;
        state.currentQuestionIndex = 0;
        state.userAnswers = {};
        
        // Show first question
        showSection('exam-section');
        renderQuestion();
        
    } catch (error) {
        console.error('Error starting exam:', error);
        alert('Failed to start exam. Please try again.');
        startBtn.disabled = false;
        startBtn.textContent = 'Start Exam';
    }
}


/**
 * Render the current question in the exam section.
 * Updates question text, options, counter, and unit information.
 */
function renderQuestion() {
    const question = state.questions[state.currentQuestionIndex];
    const totalQuestions = state.questions.length;
    const questionNumber = state.currentQuestionIndex + 1;
    
    // Update question counter with unit information
    const unitInfo = question.unit ? ` (Unit ${question.unit})` : '';
    document.getElementById('question-counter').textContent = 
        `Question ${questionNumber} of ${totalQuestions}${unitInfo}`;
    
    // Update question text
    document.getElementById('question-text').textContent = question.question_text;
    
    // Render options
    const optionsContainer = document.getElementById('options-container');
    optionsContainer.innerHTML = '';
    
    question.options.forEach((option, index) => {
        const optionDiv = document.createElement('div');
        optionDiv.className = 'option';
        
        // Check if this option was previously selected
        const isSelected = state.userAnswers[question.id] === index;
        if (isSelected) {
            optionDiv.classList.add('selected');
        }
        
        // Create radio button
        const radio = document.createElement('input');
        radio.type = 'radio';
        radio.name = 'answer';
        radio.value = index;
        radio.id = `option-${index}`;
        radio.checked = isSelected;
        
        // Create label
        const label = document.createElement('label');
        label.htmlFor = `option-${index}`;
        label.textContent = option;
        
        // Add event listener for selection
        optionDiv.addEventListener('click', () => selectOption(index));
        
        optionDiv.appendChild(radio);
        optionDiv.appendChild(label);
        optionsContainer.appendChild(optionDiv);
    });
    
    // Update button visibility
    const nextBtn = document.getElementById('next-btn');
    const submitBtn = document.getElementById('submit-btn');
    
    if (state.currentQuestionIndex === totalQuestions - 1) {
        // Last question: Show submit button
        nextBtn.style.display = 'none';
        submitBtn.style.display = 'inline-block';
    } else {
        // Not last question: Show next button
        nextBtn.style.display = 'inline-block';
        submitBtn.style.display = 'none';
    }
    
    // Hide error message
    document.getElementById('error-message').style.display = 'none';
}


/**
 * Handle option selection.
 * Updates visual state and saves answer.
 * 
 * @param {number} optionIndex - Index of selected option (0-3)
 */
function selectOption(optionIndex) {
    const question = state.questions[state.currentQuestionIndex];
    
    // Save answer to state
    state.userAnswers[question.id] = optionIndex;
    
    // Update visual state
    document.querySelectorAll('.option').forEach((opt, idx) => {
        if (idx === optionIndex) {
            opt.classList.add('selected');
            opt.querySelector('input[type="radio"]').checked = true;
        } else {
            opt.classList.remove('selected');
        }
    });
}


/**
 * Navigate to the next question.
 * Validates that an answer is selected.
 */
function nextQuestion() {
    const question = state.questions[state.currentQuestionIndex];
    
    // Validate that an answer is selected
    if (state.userAnswers[question.id] === undefined) {
        showError('Please select an answer before continuing.');
        return;
    }
    
    // Move to next question
    state.currentQuestionIndex++;
    renderQuestion();
}


/**
 * Submit exam answers to the API and show results.
 */
async function submitExam() {
    const question = state.questions[state.currentQuestionIndex];
    
    // Validate that last answer is selected
    if (state.userAnswers[question.id] === undefined) {
        showError('Please select an answer before submitting.');
        return;
    }
    
    const submitBtn = document.getElementById('submit-btn');
    submitBtn.disabled = true;
    submitBtn.textContent = 'Submitting...';
    
    try {
        // Convert numeric keys to strings for JSON
        const answersForAPI = {};
        for (const [qId, answerIdx] of Object.entries(state.userAnswers)) {
            answersForAPI[qId.toString()] = answerIdx;
        }
        
        // Call API to submit exam
        const response = await fetch(`${API_BASE}/exams/${state.examId}/submit`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({ answers: answersForAPI })
        });
        
        if (!response.ok) {
            throw new Error(`Failed to submit exam: ${response.statusText}`);
        }
        
        const results = await response.json();
        
        // Show results
        showSection('results-section');
        renderResults(results);
        
    } catch (error) {
        console.error('Error submitting exam:', error);
        showError('Failed to submit exam. Please try again.');
        submitBtn.disabled = false;
        submitBtn.textContent = 'Submit Exam';
    }
}


/**
 * Render exam results in the results section.
 * Groups questions by unit for better organization.
 * 
 * @param {Object} data - Results data from API
 * @param {number} data.score - Number of correct answers
 * @param {number} data.total - Total number of questions
 * @param {number} data.percentage - Score percentage
 * @param {Array} data.results - Array of result objects
 */
function renderResults(data) {
    // Render score summary
    const scoreSummary = document.getElementById('score-summary');
    scoreSummary.innerHTML = `
        <div class="score">${data.score} / ${data.total}</div>
        <div class="percentage">${data.percentage}%</div>
    `;
    
    // Group results by unit
    const resultsByUnit = {};
    data.results.forEach((result, index) => {
        const question = state.questions.find(q => q.id === result.question_id);
        const unit = question && question.unit ? question.unit : 0;
        const unitName = question && question.unit_name ? question.unit_name : 'Uncategorized';
        
        if (!resultsByUnit[unit]) {
            resultsByUnit[unit] = {
                unitName: unitName,
                results: []
            };
        }
        
        resultsByUnit[unit].results.push({
            ...result,
            originalIndex: index,
            unit: unit,
            unitName: unitName
        });
    });
    
    // Sort units by number
    const sortedUnits = Object.keys(resultsByUnit).sort((a, b) => parseInt(a) - parseInt(b));
    
    // Render results grouped by unit
    const resultsDetails = document.getElementById('results-details');
    let htmlContent = '';
    
    sortedUnits.forEach(unit => {
        const unitData = resultsByUnit[unit];
        const unitResults = unitData.results;
        const unitCorrect = unitResults.filter(r => r.is_correct).length;
        const unitTotal = unitResults.length;
        
        htmlContent += `
            <div class="unit-section">
                <div class="unit-header">
                    <h3>Unit ${unit}: ${unitData.unitName}</h3>
                    <span class="unit-score">${unitCorrect} / ${unitTotal} correct</span>
                </div>
                
                <table class="results-table">
                    <thead>
                        <tr>
                            <th>#</th>
                            <th>Question</th>
                            <th>Your Answer</th>
                            <th>Correct Answer</th>
                            <th>Result</th>
                        </tr>
                    </thead>
                    <tbody>
        `;
        
        unitResults.forEach((result) => {
            const questionNum = result.originalIndex + 1;
            const userAnswer = result.user_answer !== null 
                ? result.options[result.user_answer] 
                : 'Not answered';
            const correctAnswer = result.options[result.correct_answer];
            const resultClass = result.is_correct ? 'result-correct' : 'result-incorrect';
            const resultIcon = result.is_correct ? '✓' : '✗';
            
            htmlContent += `
                <tr>
                    <td>${questionNum}</td>
                    <td>${result.question_text}</td>
                    <td>${userAnswer}</td>
                    <td>${correctAnswer}</td>
                    <td class="${resultClass}">
                        <span class="result-icon">${resultIcon}</span>
                        ${result.is_correct ? 'Correct' : 'Incorrect'}
                    </td>
                </tr>
            `;
        });
        
        htmlContent += `
                    </tbody>
                </table>
            </div>
        `;
    });
    
    resultsDetails.innerHTML = htmlContent;
}


/**
 * Reset application to home screen for a new exam.
 */
function resetToHome() {
    // Clear state
    state.examId = null;
    state.questions = [];
    state.currentQuestionIndex = 0;
    state.userAnswers = {};
    
    // Reset start button
    const startBtn = document.getElementById('start-btn');
    startBtn.disabled = false;
    startBtn.textContent = 'Start Exam';
    
    // Show home section
    showSection('home-section');
}


/**
 * Show error message in exam section.
 * 
 * @param {string} message - Error message to display
 */
function showError(message) {
    const errorDiv = document.getElementById('error-message');
    errorDiv.textContent = message;
    errorDiv.style.display = 'block';
}


// Initialize app when DOM is ready
if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', init);
} else {
    init();
}
