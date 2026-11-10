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
    userAnswers: {},            // Map of questionId -> answerIndex
    userConfidence: {},         // Map of questionId -> confidence (0-100 percentage)
    pendingConfidence: false,   // Whether waiting for confidence input
    // Authentication state
    user: null,                 // Current user object (null if not authenticated)
    csrfToken: null            // CSRF token for authenticated requests
};

// API base URL
const API_BASE = '/api';


/**
 * Initialize application on page load.
 * Sets up event listeners for buttons and checks authentication status.
 */
function init() {
    // Authentication: Login form
    document.getElementById('login-form').addEventListener('submit', handleLogin);
    document.getElementById('show-register').addEventListener('click', (e) => {
        e.preventDefault();
        showSection('register-section');
    });
    
    // Authentication: Register form
    document.getElementById('register-form').addEventListener('submit', handleRegister);
    document.getElementById('show-login').addEventListener('click', (e) => {
        e.preventDefault();
        showSection('login-section');
    });
    
    // Home section: Start exam button
    document.getElementById('start-btn').addEventListener('click', startExam);
    
    // Exam section: Navigation buttons
    document.getElementById('next-btn').addEventListener('click', nextQuestion);
    document.getElementById('submit-btn').addEventListener('click', submitExam);
    
    // Results section: New exam button and view history button
    document.getElementById('new-exam-btn').addEventListener('click', resetToHome);
    document.getElementById('view-history-from-results-btn').addEventListener('click', () => {
        showHistory();
    });
    
    // History section: View history and back buttons
    document.getElementById('view-history-link').addEventListener('click', (e) => {
        e.preventDefault();
        showHistory();
    });
    document.getElementById('back-to-home-btn').addEventListener('click', () => {
        showSection('home-section');
    });
    
    // Confidence modal: Slider and confirm button
    const slider = document.getElementById('confidence-slider');
    const valueDisplay = document.getElementById('confidence-value-display');
    
    slider.addEventListener('input', (e) => {
        valueDisplay.textContent = `${e.target.value}%`;
    });
    
    document.getElementById('confirm-confidence-btn').addEventListener('click', () => {
        const confidenceValue = parseInt(slider.value);
        handleConfidence(confidenceValue);
    });
    
    // Keyboard shortcut: Enter to confirm confidence
    document.addEventListener('keydown', handleKeyboardShortcut);
    
    // Check authentication status on page load
    checkAuthStatus();
    
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
    
    // Get selected number of questions
    const numQuestions = parseInt(document.getElementById('num-questions').value);
    
    try {
        // Call API to start exam
        const response = await fetch(`${API_BASE}/exams/start`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            credentials: 'include',  // Include cookies for authentication
            body: JSON.stringify({ num_questions: numQuestions })
        });
        
        if (!response.ok) {
            // Try to get detailed error message from response
            let errorDetail = response.statusText;
            try {
                const errorData = await response.json();
                errorDetail = errorData.detail || errorData.message || response.statusText;
            } catch (e) {
                // If response is not JSON, use status text
            }
            throw new Error(`Failed to start exam: ${errorDetail}`);
        }
        
        const data = await response.json();
        
        // Update state
        state.examId = data.exam_id;
        state.questions = data.questions;
        state.currentQuestionIndex = 0;
        state.userAnswers = {};
        state.userConfidence = {};
        state.pendingConfidence = false;
        
        // Show first question
        showSection('exam-section');
        renderQuestion();
        
    } catch (error) {
        console.error('Error starting exam:', error);
        alert(`Failed to start exam: ${error.message}\n\nCheck browser console (F12) for details.`);
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
    document.getElementById('question-text').innerHTML = question.question_text;
    
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
        label.innerHTML = option;
        
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
    
    // Render math with MathJax
    if (window.MathJax) {
        MathJax.typesetPromise([document.getElementById('question-text'), optionsContainer])
            .catch((err) => console.error('MathJax rendering error:', err));
    }
}


/**
 * Handle option selection.
 * Updates visual state and saves answer.
 * If confidence not yet recorded, shows confidence modal.
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
    
    // Show confidence modal if not already answered
    if (state.userConfidence[question.id] === undefined) {
        showConfidenceModal(optionIndex);
    }
}


/**
 * Navigate to the next question.
 * Validates that an answer and confidence are selected.
 */
function nextQuestion() {
    const question = state.questions[state.currentQuestionIndex];
    
    // Validate that an answer is selected
    if (state.userAnswers[question.id] === undefined) {
        showError('Please select an answer before continuing.');
        return;
    }
    
    // Validate that confidence is recorded
    if (state.userConfidence[question.id] === undefined) {
        showError('Please indicate your confidence level before continuing.');
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
    
    // Validate that confidence is recorded
    if (state.userConfidence[question.id] === undefined) {
        showError('Please indicate your confidence level before submitting.');
        return;
    }
    
    const submitBtn = document.getElementById('submit-btn');
    submitBtn.disabled = true;
    submitBtn.textContent = 'Submitting...';
    
    try {
        // Convert numeric keys to strings for JSON
        const answersForAPI = {};
        const confidenceForAPI = {};
        for (const [qId, answerIdx] of Object.entries(state.userAnswers)) {
            answersForAPI[qId.toString()] = answerIdx;
        }
        for (const [qId, conf] of Object.entries(state.userConfidence)) {
            confidenceForAPI[qId.toString()] = conf;
        }
        
        // Call API to submit exam
        const response = await fetch(`${API_BASE}/exams/${state.examId}/submit`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({ 
                answers: answersForAPI,
                confidence: confidenceForAPI 
            })
        });
        
        if (!response.ok) {
            throw new Error(`Failed to submit exam: ${response.statusText}`);
        }
        
        const results = await response.json();
        
        // Show results
        showSection('results-section');
        renderResults(results);
        
        // Update auth status to show/hide history button
        updateAuthStatus();
        
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
 * Displays Brier Score, Bias Score, and calibration indicators.
 * 
 * @param {Object} data - Results data from API
 * @param {number} data.score - Number of correct answers
 * @param {number} data.total - Total number of questions
 * @param {number} data.percentage - Score percentage
 * @param {number} data.brier_score - Calibration metric (0=perfect, 1=worst)
 * @param {number} data.bias_score - Bias metric (-1 to 1, negative=underconfident, positive=overconfident)
 * @param {Array} data.results - Array of result objects
 */
function renderResults(data) {
    // Render score summary with Brier Score
    const scoreSummary = document.getElementById('score-summary');
    
    // Build confidence vs performance comparison section HTML
    let comparisonSectionHTML = '';
    if (data.average_confidence !== null && data.average_confidence !== undefined && 
        data.percentage !== null && data.percentage !== undefined) {
        
        const avgConfidence = parseFloat(data.average_confidence);
        const accuracy = parseFloat(data.percentage);
        const difference = avgConfidence - accuracy;
        
        // Determine calibration state
        let differenceClass = '';
        let differenceLabel = '';
        let differenceIcon = '';
        
        if (Math.abs(difference) <= 5) {
            differenceClass = 'well-calibrated';
            differenceLabel = 'Well-calibrated on average ✓';
            differenceIcon = '⚖️';
        } else if (difference > 5) {
            differenceClass = 'overconfident';
            differenceLabel = 'Overconfidence';
            differenceIcon = '📈';
        } else {
            differenceClass = 'underconfident';
            differenceLabel = 'Underconfidence';
            differenceIcon = '📉';
        }
        
        comparisonSectionHTML = `
            <div class="calibration-comparison">
                <h3>Confidence vs. Performance</h3>
                
                <div class="comparison-bar-container">
                    <div class="comparison-label">
                        <span class="comparison-label-text">Average Confidence</span>
                        <span class="comparison-label-value" style="color: #4a9eff;">${avgConfidence.toFixed(1)}%</span>
                    </div>
                    <div class="comparison-bar-background">
                        <div class="comparison-bar-fill comparison-bar-confidence" style="width: ${avgConfidence}%;"></div>
                    </div>
                </div>
                
                <div class="comparison-bar-container">
                    <div class="comparison-label">
                        <span class="comparison-label-text">Actual Accuracy</span>
                        <span class="comparison-label-value" style="color: #28a745;">${accuracy.toFixed(1)}%</span>
                    </div>
                    <div class="comparison-bar-background">
                        <div class="comparison-bar-fill comparison-bar-accuracy" style="width: ${accuracy}%;"></div>
                    </div>
                </div>
                
                <div class="comparison-difference ${differenceClass}">
                    <div class="comparison-difference-label">Difference</div>
                    <div class="comparison-difference-value">
                        ${difference >= 0 ? '+' : ''}${difference.toFixed(1)} percentage points
                    </div>
                    <div class="comparison-difference-interpretation">
                        ${differenceIcon} ${differenceLabel}
                    </div>
                </div>
            </div>
        `;
    }
    
    // Build calibration section HTML
    let calibrationSectionHTML = '';
    
    // Average Confidence
    let averageConfidenceHTML = '';
    if (data.average_confidence !== null && data.average_confidence !== undefined) {
        averageConfidenceHTML = `
            <div style="margin-bottom: 20px;">
                <div style="font-size: 0.9rem; color: #888; margin-bottom: 5px;">Average Confidence</div>
                <div style="font-size: 2rem; font-weight: bold; color: #4a9eff;">${data.average_confidence.toFixed(1)}%</div>
            </div>
        `;
    }
    
    // Brier Score
    let brierScoreHTML = '';
    if (data.brier_score !== null && data.brier_score !== undefined) {
        // Determine calibration quality
        let calibrationLabel = '';
        let calibrationColor = '';
        if (data.brier_score <= 0.20) {
            calibrationLabel = 'Excellent calibration ✓';
            calibrationColor = '#28a745';
        } else if (data.brier_score <= 0.40) {
            calibrationLabel = 'Good calibration ✓';
            calibrationColor = '#4a9eff';
        } else if (data.brier_score <= 0.60) {
            calibrationLabel = 'Poor calibration';
            calibrationColor = '#ff9800';
        } else {
            calibrationLabel = 'Very poor calibration';
            calibrationColor = '#ff4444';
        }
        
        brierScoreHTML = `
            <div style="margin-bottom: 20px;">
                <div style="font-size: 0.9rem; color: #888; margin-bottom: 5px;">Brier Score</div>
                <div style="font-size: 2rem; font-weight: bold; color: #4a9eff;">${data.brier_score.toFixed(3)}</div>
                <div style="font-size: 1rem; color: ${calibrationColor}; margin-top: 5px;">${calibrationLabel}</div>
            </div>
        `;
    }
    
    // Bias Score
    let biasScoreHTML = '';
    if (data.bias_score !== null && data.bias_score !== undefined) {
        // Determine bias interpretation
        let biasLabel = '';
        let biasColor = '';
        let biasIcon = '';
        let biasExplanation = '';
        
        if (Math.abs(data.bias_score) <= 0.10) {
            biasLabel = 'Well-calibrated ✓';
            biasColor = '#28a745';
            biasIcon = '⚖️';
            biasExplanation = 'Your confidence matches your performance';
        } else if (data.bias_score > 0.10) {
            if (data.bias_score <= 0.30) {
                biasLabel = 'Slightly overconfident';
                biasColor = '#ff9800';
            } else {
                biasLabel = 'Overconfident';
                biasColor = '#ff4444';
            }
            biasIcon = '📈';
            biasExplanation = 'You tend to be confident even when incorrect';
        } else {  // bias_score < -0.10
            if (data.bias_score >= -0.30) {
                biasLabel = 'Slightly underconfident';
                biasColor = '#4a9eff';
            } else {
                biasLabel = 'Underconfident';
                biasColor = '#888';
            }
            biasIcon = '📉';
            biasExplanation = 'You tend to lack confidence even when correct';
        }
        
        biasScoreHTML = `
            <div>
                <div style="font-size: 0.9rem; color: #888; margin-bottom: 5px;">
                    ${biasIcon} Bias Score
                </div>
                <div style="font-size: 2rem; font-weight: bold; color: #4a9eff;">
                    ${data.bias_score >= 0 ? '+' : ''}${data.bias_score.toFixed(3)}
                </div>
                <div style="font-size: 1rem; color: ${biasColor}; margin-top: 5px;">
                    ${biasLabel}
                </div>
                <div style="font-size: 0.85rem; color: #666; margin-top: 10px;">
                    ${biasExplanation}
                </div>
            </div>
        `;
    }
    
    // Combine all under Calibration header if any exist
    if (averageConfidenceHTML || brierScoreHTML || biasScoreHTML) {
        calibrationSectionHTML = `
            <div style="margin-top: 20px; padding-top: 20px; border-top: 1px solid #3a3a3a;">
                <h3 style="font-size: 1.2rem; color: #e0e0e0; margin-bottom: 15px;">Calibration</h3>
                ${averageConfidenceHTML}
                ${brierScoreHTML}
                ${biasScoreHTML}
            </div>
        `;
    }
    
    scoreSummary.innerHTML = `
        <div>
            <h3 style="font-size: 1.2rem; color: #e0e0e0; margin-bottom: 15px;">Accuracy</h3>
            <div class="score">${data.score} / ${data.total}</div>
            <div class="percentage">${data.percentage}%</div>
        </div>
        ${comparisonSectionHTML}
        ${calibrationSectionHTML}
    `;
    
    // Group results by unit
    const resultsByUnit = {};
    data.results.forEach((result, index) => {
        const question = state.questions.find(q => q.id === result.question_id);
        const unit = result.unit || (question && question.unit) || 0;
        const unitName = result.unit_name || (question && question.unit_name) || 'Uncategorized';
        
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
        
        // Calculate unit-specific confidence vs performance
        let unitComparisonHTML = '';
        const resultsWithConfidence = unitResults.filter(r => r.confidence !== null && r.confidence !== undefined);
        
        if (resultsWithConfidence.length > 0) {
            // Calculate unit average confidence
            const unitConfidenceSum = resultsWithConfidence.reduce((sum, r) => sum + r.confidence, 0);
            const unitAvgConfidence = unitConfidenceSum / resultsWithConfidence.length;
            
            // Calculate unit accuracy
            const unitAccuracy = (unitCorrect / unitTotal) * 100;
            
            // Calculate difference
            const unitDifference = unitAvgConfidence - unitAccuracy;
            
            // Determine calibration state
            let unitDiffClass = '';
            let unitDiffLabel = '';
            let unitDiffIcon = '';
            
            if (Math.abs(unitDifference) <= 5) {
                unitDiffClass = 'well-calibrated';
                unitDiffLabel = 'Well-calibrated ✓';
                unitDiffIcon = '⚖️';
            } else if (unitDifference > 5) {
                unitDiffClass = 'overconfident';
                unitDiffLabel = 'Overconfidence';
                unitDiffIcon = '📈';
            } else {
                unitDiffClass = 'underconfident';
                unitDiffLabel = 'Underconfidence';
                unitDiffIcon = '📉';
            }
            
            unitComparisonHTML = `
                <div class="calibration-comparison" style="margin: 0; border-radius: 0; border-bottom: 1px solid #444;">
                    <h4 style="font-size: 1rem; color: #e0e0e0; margin-bottom: 15px; font-weight: 600;">Confidence vs. Performance</h4>
                    
                    <div class="comparison-bar-container">
                        <div class="comparison-label">
                            <span class="comparison-label-text">Average Confidence</span>
                            <span class="comparison-label-value" style="color: #4a9eff;">${unitAvgConfidence.toFixed(1)}%</span>
                        </div>
                        <div class="comparison-bar-background">
                            <div class="comparison-bar-fill comparison-bar-confidence" style="width: ${unitAvgConfidence}%;"></div>
                        </div>
                    </div>
                    
                    <div class="comparison-bar-container">
                        <div class="comparison-label">
                            <span class="comparison-label-text">Actual Accuracy</span>
                            <span class="comparison-label-value" style="color: #28a745;">${unitAccuracy.toFixed(1)}%</span>
                        </div>
                        <div class="comparison-bar-background">
                            <div class="comparison-bar-fill comparison-bar-accuracy" style="width: ${unitAccuracy}%;"></div>
                        </div>
                    </div>
                    
                    <div class="comparison-difference ${unitDiffClass}">
                        <div class="comparison-difference-label">Difference</div>
                        <div class="comparison-difference-value" style="font-size: 1.3rem;">
                            ${unitDifference >= 0 ? '+' : ''}${unitDifference.toFixed(1)} percentage points
                        </div>
                        <div class="comparison-difference-interpretation" style="font-size: 0.9rem;">
                            ${unitDiffIcon} ${unitDiffLabel}
                        </div>
                    </div>
                </div>
            `;
        }
        
        htmlContent += `
            <div class="unit-section">
                <div class="unit-header">
                    <h3>Unit ${unit}: ${unitData.unitName}</h3>
                    <span class="unit-score">${unitCorrect} / ${unitTotal} correct</span>
                </div>
                ${unitComparisonHTML}
                
                <div class="questions-container">
        `;
        
        unitResults.forEach((result) => {
            const questionNum = result.originalIndex + 1;
            const resultClass = result.is_correct ? 'result-correct' : 'result-incorrect';
            const resultIcon = result.is_correct ? '✓' : '✗';
            const resultText = result.is_correct ? 'Correct' : 'Incorrect';
            
            // Determine header text (use review.title if available, otherwise a default)
            let headerText = `Question ${questionNum}`;
            if (result.review && result.review.title) {
                headerText = `Q${questionNum}: ${result.review.title}`;
            }
            
            // Confidence display
            let confidenceText = 'N/A';
            let confidenceColor = '#888';
            if (result.confidence !== null && result.confidence !== undefined) {
                confidenceText = `${result.confidence}%`;
                if (result.confidence >= 70) {
                    confidenceColor = '#28a745';
                } else if (result.confidence >= 40) {
                    confidenceColor = '#4a9eff';
                } else {
                    confidenceColor = '#ff9800';
                }
            }
            
            // Build the question feedback content
            let feedbackHTML = '';
            
            // Check if we have the new format (choices with explanations)
            if (result.choices && Array.isArray(result.choices)) {
                // New format with rich explanations
                
                // Find user's selected choice and correct choice
                const userChoice = result.user_answer !== null 
                    ? result.choices[result.user_answer] 
                    : null;
                const correctChoice = result.choices[result.correct_answer];
                
                feedbackHTML = `
                    <div class="question-feedback-content">
                        <div class="feedback-section">
                            <h4>Question</h4>
                            <p>${result.question_text}</p>
                        </div>
                        
                        <div class="feedback-section">
                            <h4>Your Answer</h4>
                            <div class="answer-box ${result.is_correct ? 'correct-answer-box' : 'incorrect-answer-box'}">
                                <div class="answer-text">
                                    ${userChoice ? userChoice.text : 'Not answered'}
                                </div>
                                <div class="answer-meta">
                                    <span class="result-badge ${resultClass}">
                                        ${resultIcon} ${resultText}
                                    </span>
                                    <span class="confidence-badge" style="color: ${confidenceColor};">
                                        Confidence: ${confidenceText}
                                    </span>
                                </div>
                            </div>
                        </div>
                        
                        <div class="feedback-section">
                            <h4>Correct Answer</h4>
                            <div class="answer-box correct-answer-box">
                                <div class="answer-text">
                                    ${correctChoice.text}
                                </div>
                            </div>
                            <div class="explanation-box">
                                <strong>Explanation:</strong> ${correctChoice.explanation}
                            </div>
                        </div>
                `;
                
                // Show misconception feedback only if answered incorrectly
                if (!result.is_correct && userChoice && userChoice.misconception_id) {
                    feedbackHTML += `
                        <div class="feedback-section misconception-section">
                            <h4>Misconception Associated with Your Answer</h4>
                            <div class="misconception-box">
                                ${userChoice.explanation}
                            </div>
                            <p class="misconception-note">
                                Note: This describes a common misunderstanding associated with this answer choice,
                                not necessarily a statement of your beliefs.
                            </p>
                        </div>
                    `;
                }
                
                // Show learning objective and related concepts if available
                if (result.review) {
                    if (result.review.learning_objective) {
                        feedbackHTML += `
                            <div class="feedback-section">
                                <h4>Learning Objective</h4>
                                <p>${result.review.learning_objective}</p>
                            </div>
                        `;
                    }
                    
                    if (result.review.related_concepts && result.review.related_concepts.length > 0) {
                        const conceptsHTML = result.review.related_concepts
                            .map(concept => `<span class="concept-tag">${concept}</span>`)
                            .join('');
                        feedbackHTML += `
                            <div class="feedback-section">
                                <h4>Related Concepts</h4>
                                <div class="concepts-container">
                                    ${conceptsHTML}
                                </div>
                            </div>
                        `;
                    }
                }
                
                feedbackHTML += `</div>`;
                
            } else {
                // Fallback to old format (for backwards compatibility)
                const userAnswer = result.user_answer !== null 
                    ? result.options[result.user_answer] 
                    : 'Not answered';
                const correctAnswer = result.options[result.correct_answer];
                
                feedbackHTML = `
                    <div class="question-feedback-content">
                        <div class="feedback-section">
                            <h4>Question</h4>
                            <p>${result.question_text}</p>
                        </div>
                        
                        <div class="feedback-section">
                            <h4>Your Answer</h4>
                            <div class="answer-box ${result.is_correct ? 'correct-answer-box' : 'incorrect-answer-box'}">
                                ${userAnswer}
                            </div>
                            <div class="answer-meta">
                                <span class="result-badge ${resultClass}">
                                    ${resultIcon} ${resultText}
                                </span>
                                <span class="confidence-badge" style="color: ${confidenceColor};">
                                    Confidence: ${confidenceText}
                                </span>
                            </div>
                        </div>
                        
                        <div class="feedback-section">
                            <h4>Correct Answer</h4>
                            <div class="answer-box correct-answer-box">
                                ${correctAnswer}
                            </div>
                        </div>
                    </div>
                `;
            }
            
            // Generate unique ID for accordion
            const accordionId = `question-${questionNum}`;
            
            htmlContent += `
                <div class="question-card">
                    <div class="question-header ${resultClass}" onclick="toggleQuestion('${accordionId}')">
                        <div class="question-header-content">
                            <span class="result-icon">${resultIcon}</span>
                            <span class="question-title">${headerText}</span>
                        </div>
                        <span class="expand-icon" id="${accordionId}-icon">▼</span>
                    </div>
                    <div class="question-content" id="${accordionId}" style="display: none;">
                        ${feedbackHTML}
                    </div>
                </div>
            `;
        });
        
        htmlContent += `
                </div>
            </div>
        `;
    });
    
    resultsDetails.innerHTML = htmlContent;
    
    // Render math with MathJax in results
    if (window.MathJax) {
        MathJax.typesetPromise([resultsDetails])
            .catch((err) => console.error('MathJax rendering error:', err));
    }
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
    state.userConfidence = {};
    state.pendingConfidence = false;
    
    // Reset start button
    const startBtn = document.getElementById('start-btn');
    startBtn.disabled = false;
    startBtn.textContent = 'Start Exam';
    
    // Show home section
    showSection('home-section');
}


/**
 * Show confidence modal after user selects an answer.
 * 
 * @param {number} selectedOptionIndex - Index of the selected answer
 */
function showConfidenceModal(selectedOptionIndex) {
    const question = state.questions[state.currentQuestionIndex];
    const selectedAnswer = question.options[selectedOptionIndex];
    const questionNumber = state.currentQuestionIndex + 1;
    const totalQuestions = state.questions.length;
    const unitInfo = question.unit ? ` (Unit ${question.unit})` : '';
    
    // Update modal content
    document.querySelector('#confidence-selected-answer strong').textContent = selectedAnswer;
    document.getElementById('confidence-progress').textContent = 
        `Question ${questionNumber} of ${totalQuestions}${unitInfo}`;
    
    // Reset slider to 50%
    const slider = document.getElementById('confidence-slider');
    slider.value = 50;
    document.getElementById('confidence-value-display').textContent = '50%';
    
    // Show modal
    document.getElementById('confidence-modal').style.display = 'block';
    state.pendingConfidence = true;
}


/**
 * Hide confidence modal.
 */
function hideConfidenceModal() {
    document.getElementById('confidence-modal').style.display = 'none';
    state.pendingConfidence = false;
}


/**
 * Handle confidence selection from slider.
 * 
 * @param {number} confidence - Confidence percentage (0-100)
 */
function handleConfidence(confidence) {
    const question = state.questions[state.currentQuestionIndex];
    
    // Save confidence to state
    state.userConfidence[question.id] = confidence;
    
    // Hide modal
    hideConfidenceModal();
    
    console.log(`Confidence recorded: ${confidence}%`);
}


/**
 * Handle keyboard shortcuts.
 * Enter = Confirm confidence (only when modal is open)
 * 
 * @param {KeyboardEvent} event - Keyboard event
 */
function handleKeyboardShortcut(event) {
    // Only handle shortcuts when confidence modal is open
    if (!state.pendingConfidence) {
        return;
    }
    
    if (event.key === 'Enter') {
        event.preventDefault();
        const slider = document.getElementById('confidence-slider');
        const confidenceValue = parseInt(slider.value);
        handleConfidence(confidenceValue);
    }
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


/**
 * Toggle the visibility of a question's feedback content.
 * 
 * @param {string} questionId - ID of the question element to toggle
 */
function toggleQuestion(questionId) {
    const content = document.getElementById(questionId);
    const icon = document.getElementById(`${questionId}-icon`);
    
    if (content.style.display === 'none') {
        content.style.display = 'block';
        icon.textContent = '▲';
    } else {
        content.style.display = 'none';
        icon.textContent = '▼';
    }
}

// Make toggleQuestion globally accessible
window.toggleQuestion = toggleQuestion;


/**
 * Check authentication status on page load.
 * If authenticated, shows home section. Otherwise shows login.
 */
async function checkAuthStatus() {
    try {
        const response = await fetch(`${API_BASE}/auth/me`, {
            credentials: 'include'
        });
        
        if (response.ok) {
            const user = await response.json();
            state.user = user;
            
            // Get CSRF token
            const csrfResponse = await fetch(`${API_BASE}/auth/csrf-token`, {
                credentials: 'include'
            });
            if (csrfResponse.ok) {
                const csrfData = await csrfResponse.json();
                state.csrfToken = csrfData.csrf_token;
            }
            
            // Update UI
            updateAuthStatus();
            showSection('home-section');
        } else {
            // Not authenticated - show login
            showSection('login-section');
        }
    } catch (error) {
        console.error('Error checking auth status:', error);
        showSection('login-section');
    }
}


/**
 * Update authentication status display in header.
 */
function updateAuthStatus() {
    const authStatus = document.getElementById('auth-status');
    const historyLinkContainer = document.getElementById('history-link-container');
    const viewHistoryFromResultsBtn = document.getElementById('view-history-from-results-btn');
    
    if (state.user) {
        authStatus.innerHTML = `
            <span class="user-email">${state.user.email}</span>
            <span class="logout-link" onclick="handleLogout()">Logout</span>
        `;
        // Show history link on home page
        if (historyLinkContainer) {
            historyLinkContainer.style.display = 'block';
        }
        // Show history button on results page
        if (viewHistoryFromResultsBtn) {
            viewHistoryFromResultsBtn.style.display = 'inline-block';
        }
    } else {
        authStatus.innerHTML = '';
        // Hide history link on home page
        if (historyLinkContainer) {
            historyLinkContainer.style.display = 'none';
        }
        // Hide history button on results page
        if (viewHistoryFromResultsBtn) {
            viewHistoryFromResultsBtn.style.display = 'none';
        }
    }
}


/**
 * Handle login form submission.
 */
async function handleLogin(e) {
    e.preventDefault();
    
    const email = document.getElementById('login-email').value;
    const password = document.getElementById('login-password').value;
    const errorDiv = document.getElementById('login-error');
    const submitBtn = e.target.querySelector('button[type="submit"]');
    
    // Disable button
    submitBtn.disabled = true;
    submitBtn.textContent = 'Logging in...';
    errorDiv.style.display = 'none';
    
    try {
        const response = await fetch(`${API_BASE}/auth/login`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            credentials: 'include',
            body: JSON.stringify({ email, password })
        });
        
        if (response.ok) {
            const data = await response.json();
            state.user = data.user;
            state.csrfToken = data.csrf_token;
            
            // Update UI
            updateAuthStatus();
            showSection('home-section');
            
            // Clear form
            document.getElementById('login-form').reset();
        } else {
            const error = await response.json();
            errorDiv.textContent = error.detail || 'Login failed';
            errorDiv.style.display = 'block';
        }
    } catch (error) {
        console.error('Login error:', error);
        errorDiv.textContent = 'Network error. Please try again.';
        errorDiv.style.display = 'block';
    } finally {
        submitBtn.disabled = false;
        submitBtn.textContent = 'Login';
    }
}


/**
 * Handle register form submission.
 */
async function handleRegister(e) {
    e.preventDefault();
    
    const email = document.getElementById('register-email').value;
    const password = document.getElementById('register-password').value;
    const passwordConfirm = document.getElementById('register-password-confirm').value;
    const errorDiv = document.getElementById('register-error');
    const submitBtn = e.target.querySelector('button[type="submit"]');
    
    // Validate passwords match
    if (password !== passwordConfirm) {
        errorDiv.textContent = 'Passwords do not match';
        errorDiv.style.display = 'block';
        return;
    }
    
    // Disable button
    submitBtn.disabled = true;
    submitBtn.textContent = 'Registering...';
    errorDiv.style.display = 'none';
    
    try {
        const response = await fetch(`${API_BASE}/auth/register`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({ email, password })
        });
        
        if (response.ok) {
            // Registration successful - show login form
            alert('Registration successful! Please log in.');
            showSection('login-section');
            
            // Pre-fill email in login form
            document.getElementById('login-email').value = email;
            
            // Clear register form
            document.getElementById('register-form').reset();
        } else {
            const error = await response.json();
            
            // Parse validation errors
            if (error.detail && Array.isArray(error.detail)) {
                const errors = error.detail.map(err => err.msg).join(', ');
                errorDiv.textContent = errors;
            } else {
                errorDiv.textContent = error.detail || 'Registration failed';
            }
            errorDiv.style.display = 'block';
        }
    } catch (error) {
        console.error('Registration error:', error);
        errorDiv.textContent = 'Network error. Please try again.';
        errorDiv.style.display = 'block';
    } finally {
        submitBtn.disabled = false;
        submitBtn.textContent = 'Register';
    }
}


/**
 * Handle logout.
 */
async function handleLogout() {
    if (!state.csrfToken) {
        // No CSRF token - just clear state and show login
        state.user = null;
        state.csrfToken = null;
        updateAuthStatus();
        showSection('login-section');
        return;
    }
    
    try {
        const response = await fetch(`${API_BASE}/auth/logout`, {
            method: 'POST',
            headers: {
                'X-CSRF-Token': state.csrfToken
            },
            credentials: 'include'
        });
        
        if (response.ok) {
            state.user = null;
            state.csrfToken = null;
            updateAuthStatus();
            showSection('login-section');
        }
    } catch (error) {
        console.error('Logout error:', error);
        // Even if logout fails, clear local state
        state.user = null;
        state.csrfToken = null;
        updateAuthStatus();
        showSection('login-section');
    }
}


/**
 * Show exam history section and load data.
 */
async function showHistory() {
    showSection('history-section');
    
    // Load statistics
    await loadStatistics();
    
    // Load exam history
    await loadExamHistory();
    
    // Load performance history charts
    await loadPerformanceCharts();
}


/**
 * Load and display user statistics.
 */
async function loadStatistics() {
    const summaryDiv = document.getElementById('statistics-summary');
    
    try {
        const response = await fetch(`${API_BASE}/exams/statistics`, {
            credentials: 'include'
        });
        
        if (response.ok) {
            const stats = await response.json();
            
            if (stats.total_exams === 0) {
                summaryDiv.innerHTML = `
                    <div style="grid-column: 1 / -1; text-align: center; color: #888;">
                        No completed exams yet. Take an exam to see your statistics!
                    </div>
                `;
            } else {
                summaryDiv.innerHTML = `
                    <div class="stat-item">
                        <div class="stat-label">Total Exams</div>
                        <div class="stat-value">${stats.total_exams}</div>
                    </div>
                    <div class="stat-item">
                        <div class="stat-label">Accuracy</div>
                        <div class="stat-value">${stats.accuracy ? stats.accuracy.toFixed(1) : 'N/A'}<span class="stat-unit">%</span></div>
                    </div>
                    <div class="stat-item">
                        <div class="stat-label">Avg Confidence</div>
                        <div class="stat-value">${stats.average_confidence ? stats.average_confidence.toFixed(1) : 'N/A'}<span class="stat-unit">%</span></div>
                    </div>
                    <div class="stat-item">
                        <div class="stat-label">Brier Score</div>
                        <div class="stat-value">${stats.average_brier_score ? stats.average_brier_score.toFixed(3) : 'N/A'}</div>
                    </div>
                `;
            }
        } else {
            summaryDiv.innerHTML = '<div style="color: #ff4444;">Failed to load statistics</div>';
        }
    } catch (error) {
        console.error('Error loading statistics:', error);
        summaryDiv.innerHTML = '<div style="color: #ff4444;">Error loading statistics</div>';
    }
}


/**
 * Load and display exam history.
 */
async function loadExamHistory() {
    const historyList = document.getElementById('history-list');
    
    try {
        const response = await fetch(`${API_BASE}/exams/history?limit=50`, {
            credentials: 'include'
        });
        
        if (response.ok) {
            const data = await response.json();
            
            if (data.exams.length === 0) {
                historyList.innerHTML = `
                    <div class="history-empty">
                        <p>No exam history yet.</p>
                        <p>Take your first exam to start tracking your progress!</p>
                    </div>
                `;
            } else {
                historyList.innerHTML = data.exams.map(exam => renderHistoryItem(exam)).join('');
            }
        } else {
            historyList.innerHTML = '<div style="color: #ff4444;">Failed to load exam history</div>';
        }
    } catch (error) {
        console.error('Error loading exam history:', error);
        historyList.innerHTML = '<div style="color: #ff4444;">Error loading exam history</div>';
    }
}


/**
 * Render a single history item.
 */
function renderHistoryItem(exam) {
    const date = new Date(exam.created_at);
    const dateStr = date.toLocaleDateString() + ' ' + date.toLocaleTimeString([], {hour: '2-digit', minute: '2-digit'});
    
    // Determine score color
    let scoreClass = 'poor';
    if (exam.percentage >= 80) scoreClass = 'good';
    else if (exam.percentage >= 60) scoreClass = 'medium';
    
    // Status
    const status = exam.completed_at ? 'Completed' : 'In Progress';
    const scoreDisplay = exam.score !== null 
        ? `${exam.score}/${exam.total_questions} (${exam.percentage.toFixed(0)}%)`
        : 'Not completed';
    
    return `
        <div class="history-item" onclick="viewExamResults(${exam.id})">
            <div class="history-item-header">
                <div class="history-item-date">${dateStr}</div>
                <div class="history-item-score ${scoreClass}">${scoreDisplay}</div>
            </div>
            <div class="history-item-details">
                <span>${exam.total_questions} questions</span>
                <span>•</span>
                <span>${status}</span>
            </div>
        </div>
    `;
}


/**
 * View results for a specific exam from history.
 */
async function viewExamResults(examId) {
    try {
        const response = await fetch(`${API_BASE}/exams/${examId}/results`, {
            credentials: 'include'
        });
        
        if (response.ok) {
            const results = await response.json();
            
            // Show results section
            showSection('results-section');
            renderResults(results);
            
            // Update auth status to show/hide history button
            updateAuthStatus();
        } else {
            alert('Failed to load exam results');
        }
    } catch (error) {
        console.error('Error loading exam results:', error);
        alert('Error loading exam results');
    }
}


/**
 * Load and display performance history charts.
 */
let performanceChart = null;
let calibrationChart = null;

async function loadPerformanceCharts() {
    const chartSection = document.getElementById('performance-history');
    
    try {
        const response = await fetch(`${API_BASE}/exams/trends`, {
            credentials: 'include'
        });
        
        if (response.ok) {
            const data = await response.json();
            const trends = data.trends;
            
            if (trends && trends.length >= 2) {
                // Show chart section
                chartSection.style.display = 'block';
                
                // Set up chart toggle buttons
                setupChartToggle();
                
                // Render both charts
                renderPerformanceChart(trends);
                renderCalibrationChart(trends);
            } else {
                // Hide chart section if not enough data
                chartSection.style.display = 'none';
            }
        }
    } catch (error) {
        console.error('Error loading performance charts:', error);
        chartSection.style.display = 'none';
    }
}


/**
 * Set up chart toggle button handlers.
 */
function setupChartToggle() {
    const performanceBtn = document.getElementById('show-performance-chart');
    const calibrationBtn = document.getElementById('show-calibration-chart');
    const performanceContainer = document.getElementById('performance-chart-container');
    const calibrationContainer = document.getElementById('calibration-chart-container');
    const performanceExplanation = document.getElementById('performance-explanation');
    const calibrationExplanation = document.getElementById('calibration-explanation');
    
    performanceBtn.addEventListener('click', () => {
        performanceBtn.classList.add('active');
        calibrationBtn.classList.remove('active');
        performanceContainer.style.display = 'block';
        calibrationContainer.style.display = 'none';
        performanceExplanation.style.display = 'block';
        calibrationExplanation.style.display = 'none';
    });
    
    calibrationBtn.addEventListener('click', () => {
        calibrationBtn.classList.add('active');
        performanceBtn.classList.remove('active');
        calibrationContainer.style.display = 'block';
        performanceContainer.style.display = 'none';
        calibrationExplanation.style.display = 'block';
        performanceExplanation.style.display = 'none';
    });
}


/**
 * Render performance chart (accuracy and confidence).
 */
function renderPerformanceChart(trends) {
    const canvas = document.getElementById('performance-chart');
    const ctx = canvas.getContext('2d');
    
    // Destroy existing chart if it exists
    if (performanceChart) {
        performanceChart.destroy();
    }
    
    // Prepare data
    const labels = trends.map(t => `Exam ${t.exam_number}`);
    const accuracy = trends.map(t => t.accuracy);
    const confidence = trends.map(t => t.average_confidence);
    
    // Create chart
    performanceChart = new Chart(ctx, {
        type: 'line',
        data: {
            labels: labels,
            datasets: [
                {
                    label: 'Answer Accuracy (%)',
                    data: accuracy,
                    borderColor: '#28a745',
                    backgroundColor: 'rgba(40, 167, 69, 0.1)',
                    borderWidth: 2,
                    tension: 0.3,
                    fill: true
                },
                {
                    label: 'Average Confidence (%)',
                    data: confidence,
                    borderColor: '#4a9eff',
                    backgroundColor: 'rgba(74, 158, 255, 0.1)',
                    borderWidth: 2,
                    tension: 0.3,
                    fill: true
                }
            ]
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            plugins: {
                legend: {
                    display: true,
                    position: 'top',
                    labels: {
                        color: '#e0e0e0',
                        padding: 15,
                        font: {
                            size: 12
                        }
                    }
                },
                title: {
                    display: true,
                    text: 'Performance Over Time',
                    color: '#e0e0e0',
                    font: {
                        size: 16,
                        weight: 'bold'
                    },
                    padding: {
                        bottom: 20
                    }
                },
                tooltip: {
                    backgroundColor: 'rgba(0, 0, 0, 0.8)',
                    titleColor: '#fff',
                    bodyColor: '#fff',
                    borderColor: '#3a3a3a',
                    borderWidth: 1,
                    padding: 12,
                    displayColors: true
                }
            },
            scales: {
                x: {
                    grid: {
                        color: '#3a3a3a'
                    },
                    ticks: {
                        color: '#b0b0b0'
                    }
                },
                y: {
                    min: 0,
                    max: 100,
                    grid: {
                        color: '#3a3a3a'
                    },
                    ticks: {
                        color: '#b0b0b0',
                        callback: function(value) {
                            return value + '%';
                        }
                    },
                    title: {
                        display: true,
                        text: 'Percentage (%)',
                        color: '#b0b0b0'
                    }
                }
            }
        }
    });
}


/**
 * Render calibration chart (Brier score and bias).
 */
function renderCalibrationChart(trends) {
    const canvas = document.getElementById('calibration-chart');
    const ctx = canvas.getContext('2d');
    
    // Destroy existing chart if it exists
    if (calibrationChart) {
        calibrationChart.destroy();
    }
    
    // Prepare data
    const labels = trends.map(t => `Exam ${t.exam_number}`);
    const brierScores = trends.map(t => t.brier_score);
    const biasScores = trends.map(t => t.bias_score);
    
    // Create chart with dual y-axes
    calibrationChart = new Chart(ctx, {
        type: 'line',
        data: {
            labels: labels,
            datasets: [
                {
                    label: 'Brier Score',
                    data: brierScores,
                    borderColor: '#ff9800',
                    backgroundColor: 'rgba(255, 152, 0, 0.1)',
                    borderWidth: 2,
                    tension: 0.3,
                    fill: true,
                    yAxisID: 'y-brier'
                },
                {
                    label: 'Calibration Bias',
                    data: biasScores,
                    borderColor: '#9c27b0',
                    backgroundColor: 'rgba(156, 39, 176, 0.1)',
                    borderWidth: 2,
                    tension: 0.3,
                    fill: true,
                    yAxisID: 'y-bias'
                }
            ]
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            interaction: {
                mode: 'index',
                intersect: false
            },
            plugins: {
                legend: {
                    display: true,
                    position: 'top',
                    labels: {
                        color: '#e0e0e0',
                        padding: 15,
                        font: {
                            size: 12
                        }
                    }
                },
                title: {
                    display: true,
                    text: 'Calibration Over Time',
                    color: '#e0e0e0',
                    font: {
                        size: 16,
                        weight: 'bold'
                    },
                    padding: {
                        bottom: 20
                    }
                },
                tooltip: {
                    backgroundColor: 'rgba(0, 0, 0, 0.8)',
                    titleColor: '#fff',
                    bodyColor: '#fff',
                    borderColor: '#3a3a3a',
                    borderWidth: 1,
                    padding: 12,
                    displayColors: true,
                    callbacks: {
                        label: function(context) {
                            let label = context.dataset.label || '';
                            if (label) {
                                label += ': ';
                            }
                            if (context.parsed.y !== null) {
                                label += context.parsed.y.toFixed(3);
                            }
                            return label;
                        }
                    }
                }
            },
            scales: {
                x: {
                    grid: {
                        color: '#3a3a3a'
                    },
                    ticks: {
                        color: '#b0b0b0'
                    }
                },
                'y-brier': {
                    type: 'linear',
                    position: 'left',
                    min: 0,
                    max: 0.5,
                    grid: {
                        color: '#3a3a3a'
                    },
                    ticks: {
                        color: '#ff9800',
                        callback: function(value) {
                            return value.toFixed(2);
                        }
                    },
                    title: {
                        display: true,
                        text: 'Brier Score',
                        color: '#ff9800'
                    }
                },
                'y-bias': {
                    type: 'linear',
                    position: 'right',
                    min: -0.5,
                    max: 0.5,
                    grid: {
                        drawOnChartArea: false
                    },
                    ticks: {
                        color: '#9c27b0',
                        callback: function(value) {
                            return value.toFixed(2);
                        }
                    },
                    title: {
                        display: true,
                        text: 'Calibration Bias',
                        color: '#9c27b0'
                    }
                }
            }
        }
    });
}


// Initialize app when DOM is ready
if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', init);
} else {
    init();
}
