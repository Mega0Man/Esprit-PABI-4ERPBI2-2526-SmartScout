const API_URL = 'http://localhost:8090';

let state = {
    currentPage: 'home',
    currentRole: null,
    user: null,
    token: null
};

const roleConfigs = {
    group_leader: {
        name: 'Group Leader',
        color: '#2c7fb8',
        gradientFrom: '#1a3a52',
        gradientTo: '#0d2840',
        lightColor: '#5aa0e6',
        icon: '👥',
        modules: ['Scout Forecasting', 'Classification'],
        powerBIUrl: 'https://app.powerbi.com/reportEmbed?reportId=5f0c1758-2012-40a7-a892-56464db8d0be&autoAuth=true&ctid=604f1a96-cbe8-43f8-abbf-f8eaf5d85730&filterPaneEnabled=false&navContentPaneEnabled=false&chrome=false&language=en-US'
    },
    treasurer: {
        name: 'Treasurer',
        color: '#d4af37',
        gradientFrom: '#524a1a',
        gradientTo: '#40350d',
        lightColor: '#f0d78c',
        icon: '💰',
        modules: ['Anomaly Detection'],
        powerBIUrl: 'https://app.powerbi.com/reportEmbed?reportId=7094a587-edf8-4891-8ae1-53ce6871a076&autoAuth=true&ctid=604f1a96-cbe8-43f8-abbf-f8eaf5d85730&filterPaneEnabled=false&navContentPaneEnabled=false&chrome=false&language=en-US'
    },
    unit_leader: {
        name: 'Unit Leader',
        color: '#2d8c59',
        gradientFrom: '#1a523a',
        gradientTo: '#0d4028',
        lightColor: '#5cb885',
        icon: '🎯',
        modules: ['Recommendation System'],
        powerBIUrl: 'https://app.powerbi.com/reportEmbed?reportId=b2aa5284-6c1f-4c5c-8293-17ba828f5148&autoAuth=true&ctid=604f1a96-cbe8-43f8-abbf-f8eaf5d85730&filterPaneEnabled=false&navContentPaneEnabled=false&chrome=false&language=en-US'
    }
};

function init() {
    const savedToken = localStorage.getItem('token');
    const savedUser = localStorage.getItem('user');
    if (savedToken && savedUser) {
        state.token = savedToken;
        state.user = JSON.parse(savedUser);
        state.currentPage = 'dashboard';
        state.currentRole = state.user.role;
    }
    render();
}

function render() {
    const app = document.getElementById('app');
    switch (state.currentPage) {
        case 'home':
            app.innerHTML = renderHomePage();
            break;
        case 'login':
            app.innerHTML = renderLoginPage();
            break;
        case 'dashboard':
            app.innerHTML = renderDashboardPage();
            break;
    }
    attachEventListeners();
}

function renderHomePage() {
    return `
        <div class="home-container">

            <!-- HEADER -->
            <header class="home-header">
                <div class="home-logo">⚜️</div>
                <div>
                    <span class="home-org-name">Grombalia Scout Group</span>
                    <span class="home-org-motto">UNITY &bull; SERVICE &bull; BROTHERHOOD</span>
                </div>
            </header>

            <!-- MAIN AREA -->
            <div class="home-body">

                <!-- LEFT TEXT -->
                <div class="home-left">
                    <h1 class="home-welcome-title">WELCOME!</h1>
                    <span class="home-fleur">⚜</span>
                    <p class="home-choose-title">CHOOSE YOUR DASHBOARD</p>
                    <p class="home-choose-sub">Select your role to access<br>your dashboard</p>
                    <div class="home-quote">
                        <p>To serve, to help,<br>to build a better world.</p>
                    </div>
                </div>

                <!--
                    SVG connector lines from each button center to its fingertip.
                    Coordinates are % of home-body (viewBox 0 0 100 100).
                    Button centers: green(53,35), gold(60,28), blue(67,35)
                    Finger tips:    green(45,53), gold(52,47), blue(59,52)
                -->
                <svg class="home-connector-svg" viewBox="0 0 100 100" preserveAspectRatio="none">
                    <!-- Green line: Unit Leader → middle finger -->
                    <line x1="50" y1="28" x2="52" y2="53"
                          stroke="rgba(111,219,155,0.85)" stroke-width="0.5"
                          stroke-dasharray="1.5 0.8"/>
                    <circle cx="52" cy="53" r="1.2"
                            fill="rgba(111,219,155,0.9)" stroke="#fff" stroke-width="0.3"/>

                    <!-- Gold line: Treasurer → middle finger -->
                    <line x1="56" y1="28" x2="56" y2="52"
                          stroke="rgba(245,224,154,0.85)" stroke-width="0.5"
                          stroke-dasharray="1.5 0.8"/>
                    <circle cx="56" cy="52" r="1.2"
                            fill="rgba(245,224,154,0.9)" stroke="#fff" stroke-width="0.3"/>

                    <!-- Blue line: Group Leader → right fingertip -->
                    <line x1="61" y1="35" x2="60" y2="52"
                          stroke="rgba(106,184,247,0.85)" stroke-width="0.5"
                          stroke-dasharray="1.5 0.8"/>
                    <circle cx="60" cy="52" r="1.2"
                            fill="rgba(106,184,247,0.9)" stroke="#fff" stroke-width="0.3"/>
                </svg>

                <!-- GREEN: left finger -->
                <div class="role-button green" data-role="unit_leader">
                    <div class="role-button-label">
                        <span class="lbl-name">UNIT LEADER</span>
                        <span class="lbl-sub">Dashboard</span>
                    </div>
                    <span class="role-icon">👤</span>
                </div>

                <!-- GOLD: middle finger -->
                <div class="role-button gold" data-role="treasurer">
                    <div class="role-button-label">
                        <span class="lbl-name">TREASURER</span>
                        <span class="lbl-sub">Dashboard</span>
                    </div>
                    <span class="role-icon">💰</span>
                </div>

                <!-- BLUE: right finger -->
                <div class="role-button blue" data-role="group_leader">
                    <div class="role-button-label">
                        <span class="lbl-name">GROUP LEADER</span>
                        <span class="lbl-sub">Dashboard</span>
                    </div>
                    <span class="role-icon">👥</span>
                </div>

            </div>

            <!-- BOTTOM VALUES BAR -->
            <footer class="home-values-bar">
                <div class="value-item"><span class="value-icon">⛺</span><span class="value-label">Adventure</span></div>
                <div class="value-item"><span class="value-icon">🤝</span><span class="value-label">Teamwork</span></div>
                <div class="value-item"><span class="value-icon">🔥</span><span class="value-label">Values</span></div>
                <div class="value-item"><span class="value-icon">🧭</span><span class="value-label">Leadership</span></div>
            </footer>

        </div>
    `;
}

function renderLoginPage() {
    const config = roleConfigs[state.currentRole];
    return `
        <div class="login-container" style="background: linear-gradient(135deg, ${config.gradientFrom} 0%, ${config.gradientTo} 100%)">
            <button class="back-button" id="backBtn">← Back to Home</button>
            <div class="login-box">
                <div class="login-icon">${config.icon}</div>
                <h1>${config.name}</h1>
                <p class="subtitle-login">Sign in to access the dashboard</p>
                <form id="loginForm">
                    <div class="form-group">
                        <label>Username</label>
                        <input type="text" id="username" placeholder="Enter your username" required>
                    </div>
                    <div class="form-group">
                        <label>Password</label>
                        <input type="password" id="password" placeholder="Enter your password" required>
                    </div>
                    <div class="error-message" id="errorMsg" style="display:none;"></div>
                    <button type="submit" style="background: ${config.color}">Sign In</button>
                </form>
                <div class="demo-credentials">
                    <p>Demo credentials (username / password)</p>
                    <code>${state.currentRole} / password</code>
                </div>
            </div>
        </div>
    `;
}

function renderDashboardPage() {
    const config = roleConfigs[state.user.role];

    let mlButtons = '';
    if (state.user.role === 'group_leader') {
        mlButtons = `
            <button class="ml-nav-btn" onclick="openModel('forecast')">📊 Scout Forecast</button>
            <button class="ml-nav-btn" onclick="openModel('classification')">🏷️ Classification</button>
        `;
    } else if (state.user.role === 'treasurer') {
        mlButtons = `
            <button class="ml-nav-btn" onclick="openModel('anomaly')">⚠️ Anomaly Detection</button>
        `;
    } else if (state.user.role === 'unit_leader') {
        mlButtons = `
            <button class="ml-nav-btn" onclick="openModel('recommendation')">🎯 Recommendation</button>
        `;
    }

    let powerBIContent = '';
    if (config.powerBIUrl) {
        powerBIContent = `<iframe src="${config.powerBIUrl}" class="powerbi-iframe" frameborder="0" allowfullscreen="true"></iframe>`;
    } else {
        powerBIContent = `
            <div class="powerbi-placeholder">
                <div class="placeholder-icon">📈</div>
                <h4>${config.name} Dashboard</h4>
                <p>Power BI report coming soon! Share your embed URL when you have it.</p>
            </div>
        `;
    }

    return `
        <div class="dashboard-container" style="background: linear-gradient(135deg, ${config.gradientFrom} 0%, ${config.gradientTo} 100%)">
            <nav class="navbar">
                <div class="nav-left">
                    <div class="nav-logo">🌿</div>
                    <div class="nav-title">
                        <h2>GROMBALIA SCOUT GROUP</h2>
                        <p>${config.name} Dashboard</p>
                    </div>
                </div>
                <div class="nav-right">
                    <div class="ml-buttons">
                        ${mlButtons}
                    </div>
                    <span class="user-info">Welcome, ${state.user.username}</span>
                    <button class="logout-btn" id="logoutBtn">Logout</button>
                </div>
            </nav>
            <main class="dashboard-content">
                <section class="dashboard-section">
                    <div class="section-header">
                        <h3>📊 Power BI Reports</h3>
                    </div>
                    <div class="card powerbi-card">
                        ${powerBIContent}
                    </div>
                </section>
            </main>
        </div>
    `;
}

function renderForecastingCard() {
    return `
        <div class="card ml-card">
            <div class="card-header">
                <h4>📊 Scout Forecasting</h4>
            </div>
            <form id="forecastingForm">
                <div class="form-row">
                    <label>Months to Forecast</label>
                    <input type="number" id="forecastMonths" min="1" max="24" value="12">
                </div>
                <button type="submit">Run Forecast</button>
            </form>
            <div id="forecastingResult"></div>
        </div>
    `;
}

function renderClassificationCard() {
    return `
        <div class="card ml-card">
            <div class="card-header">
                <h4>🏷️ Classification</h4>
            </div>
            <form id="classificationForm">
                <div class="form-row">
                    <label>Age</label>
                    <input type="number" id="classAge" value="14">
                </div>
                <div class="form-row">
                    <label>Gender</label>
                    <select id="classGender">
                        <option value="male">Male</option>
                        <option value="female">Female</option>
                    </select>
                </div>
                <div class="form-row">
                    <label>Unit</label>
                    <select id="classUnit">
                        <option value="cubs">Cubs</option>
                        <option value="scouts">Scouts</option>
                        <option value="ventures">Ventures</option>
                        <option value="rovers">Rovers</option>
                    </select>
                </div>
                <div class="form-row">
                    <label>Membership Years</label>
                    <input type="number" id="classMembership" value="2">
                </div>
                <button type="submit">Classify</button>
            </form>
            <div id="classificationResult"></div>
        </div>
    `;
}

function renderAnomalyCard() {
    return `
        <div class="card ml-card">
            <div class="card-header">
                <h4>⚠️ Anomaly Detection</h4>
            </div>
            <form id="anomalyForm">
                <div class="form-row">
                    <label>Amount</label>
                    <input type="number" id="anomalyAmount" step="0.01" value="100">
                </div>
                <div class="form-row">
                    <label>Transaction Type</label>
                    <select id="anomalyType">
                        <option value="income">Income</option>
                        <option value="expense">Expense</option>
                    </select>
                </div>
                <div class="form-row">
                    <label>Category</label>
                    <select id="anomalyCategory">
                        <option value="supplies">Supplies</option>
                        <option value="events">Events</option>
                        <option value="membership">Membership</option>
                        <option value="donations">Donations</option>
                    </select>
                </div>
                <button type="submit">Detect Anomaly</button>
            </form>
            <div id="anomalyResult"></div>
        </div>
    `;
}

function renderRecommendationCard() {
    return `
        <div class="card ml-card">
            <div class="card-header">
                <h4>🎯 Recommendation System</h4>
            </div>
            <form id="recommendationForm">
                <div class="form-row">
                    <label>Scout ID</label>
                    <input type="number" id="recScoutId" value="1">
                </div>
                <div class="form-row">
                    <label>Activity Preferences (comma separated)</label>
                    <input type="text" id="recPreferences" placeholder="e.g., camping, hiking, first aid">
                </div>
                <button type="submit">Get Recommendations</button>
            </form>
            <div id="recommendationResult"></div>
        </div>
    `;
}

function attachEventListeners() {
    // Home page role buttons
    document.querySelectorAll('.role-button').forEach(card => {
        card.addEventListener('click', () => {
            state.currentRole = card.dataset.role;
            state.currentPage = 'login';
            render();
        });
    });

    // Back button
    const backBtn = document.getElementById('backBtn');
    if (backBtn) {
        backBtn.addEventListener('click', () => {
            state.currentPage = 'home';
            render();
        });
    }

    // Login form
    const loginForm = document.getElementById('loginForm');
    if (loginForm) {
        loginForm.addEventListener('submit', async (e) => {
            e.preventDefault();
            await handleLogin();
        });
    }

    // Logout button
    const logoutBtn = document.getElementById('logoutBtn');
    if (logoutBtn) {
        logoutBtn.addEventListener('click', () => {
            handleLogout();
        });
    }

    // ML forms
    const forecastingForm = document.getElementById('forecastingForm');
    if (forecastingForm) {
        forecastingForm.addEventListener('submit', async (e) => {
            e.preventDefault();
            await handleForecasting();
        });
    }

    const classificationForm = document.getElementById('classificationForm');
    if (classificationForm) {
        classificationForm.addEventListener('submit', async (e) => {
            e.preventDefault();
            await handleClassification();
        });
    }

    const anomalyForm = document.getElementById('anomalyForm');
    if (anomalyForm) {
        anomalyForm.addEventListener('submit', async (e) => {
            e.preventDefault();
            await handleAnomaly();
        });
    }

    const recommendationForm = document.getElementById('recommendationForm');
    if (recommendationForm) {
        recommendationForm.addEventListener('submit', async (e) => {
            e.preventDefault();
            await handleRecommendation();
        });
    }
}

async function handleLogin() {
    const username = document.getElementById('username').value;
    const password = document.getElementById('password').value;
    const errorMsg = document.getElementById('errorMsg');

    const formData = new FormData();
    formData.append('username', username);
    formData.append('password', password);

    try {
        const response = await fetch(`${API_URL}/token`, {
            method: 'POST',
            body: formData
        });

        if (!response.ok) {
            throw new Error('Invalid credentials');
        }

        const data = await response.json();
        state.token = data.access_token;
        state.user = data.user;
        localStorage.setItem('token', state.token);
        localStorage.setItem('user', JSON.stringify(state.user));

        if (data.user.role === state.currentRole) {
            state.currentPage = 'dashboard';
            render();
        } else {
            errorMsg.textContent = 'Invalid role for this login page';
            errorMsg.style.display = 'block';
        }
    } catch (error) {
        errorMsg.textContent = 'Invalid username or password';
        errorMsg.style.display = 'block';
    }
}

function openModel(modelType) {
    const paths = {
        forecast: 'http://localhost:5000',
        classification: 'http://localhost:5002',
        anomaly: 'http://localhost:5004',
        recommendation: 'http://localhost:5003'
    };
    window.open(paths[modelType], '_blank');
}

function handleLogout() {
    state.token = null;
    state.user = null;
    state.currentPage = 'home';
    localStorage.removeItem('token');
    localStorage.removeItem('user');
    render();
}

async function handleForecasting() {
    const months = document.getElementById('forecastMonths').value;
    const resultDiv = document.getElementById('forecastingResult');

    try {
        const response = await fetch(`${API_URL}/ml/forecasting`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                'Authorization': `Bearer ${state.token}`
            },
            body: JSON.stringify({ months: parseInt(months) })
        });

        const data = await response.json();
        resultDiv.innerHTML = `
            <div class="result-box">
                <div class="result-header">Prediction Result</div>
                <div class="result-content">
                    <div class="forecast-list">
                        ${data.prediction.map(item => `
                            <div class="forecast-item">
                                <span class="month">${item.month}</span>
                                <span class="value">${item.predicted_scouts} scouts</span>
                            </div>
                        `).join('')}
                    </div>
                </div>
                <div class="result-footer">Inference time: ${data.inference_time_ms.toFixed(2)}ms</div>
            </div>
        `;
    } catch (error) {
        resultDiv.innerHTML = `<div class="error-message">Error: ${error.message}</div>`;
    }
}

async function handleClassification() {
    const age = document.getElementById('classAge').value;
    const gender = document.getElementById('classGender').value;
    const unit = document.getElementById('classUnit').value;
    const membership = document.getElementById('classMembership').value;
    const resultDiv = document.getElementById('classificationResult');

    try {
        const response = await fetch(`${API_URL}/ml/classification`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                'Authorization': `Bearer ${state.token}`
            },
            body: JSON.stringify({
                age: parseInt(age),
                gender,
                unit,
                membership_years: parseInt(membership)
            })
        });

        const data = await response.json();
        resultDiv.innerHTML = `
            <div class="result-box">
                <div class="result-header">Prediction Result</div>
                <div class="result-content">
                    <div class="classification-result">
                        <span class="class-label">${data.prediction.toUpperCase()}</span>
                        <span class="confidence">Confidence: ${(data.confidence * 100).toFixed(1)}%</span>
                    </div>
                </div>
                <div class="result-footer">Inference time: ${data.inference_time_ms.toFixed(2)}ms</div>
            </div>
        `;
    } catch (error) {
        resultDiv.innerHTML = `<div class="error-message">Error: ${error.message}</div>`;
    }
}

async function handleAnomaly() {
    const amount = document.getElementById('anomalyAmount').value;
    const type = document.getElementById('anomalyType').value;
    const category = document.getElementById('anomalyCategory').value;
    const resultDiv = document.getElementById('anomalyResult');

    try {
        const response = await fetch(`${API_URL}/ml/anomaly`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                'Authorization': `Bearer ${state.token}`
            },
            body: JSON.stringify({
                amount: parseFloat(amount),
                transaction_type: type,
                category
            })
        });

        const data = await response.json();
        resultDiv.innerHTML = `
            <div class="result-box">
                <div class="result-header">Prediction Result</div>
                <div class="result-content">
                    <div class="anomaly-result">
                        <span class="anomaly-badge ${data.prediction.is_anomaly ? 'anomaly' : ''}">
                            ${data.prediction.is_anomaly ? '⚠️ ANOMALY DETECTED' : '✓ NORMAL'}
                        </span>
                        <span class="score">Score: ${data.prediction.score.toFixed(3)}</span>
                    </div>
                </div>
                <div class="result-footer">Inference time: ${data.inference_time_ms.toFixed(2)}ms</div>
            </div>
        `;
    } catch (error) {
        resultDiv.innerHTML = `<div class="error-message">Error: ${error.message}</div>`;
    }
}

async function handleRecommendation() {
    const scoutId = document.getElementById('recScoutId').value;
    const preferences = document.getElementById('recPreferences').value.split(',').map(s => s.trim());
    const resultDiv = document.getElementById('recommendationResult');

    try {
        const response = await fetch(`${API_URL}/ml/recommendation`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                'Authorization': `Bearer ${state.token}`
            },
            body: JSON.stringify({
                scout_id: parseInt(scoutId),
                activity_preferences: preferences
            })
        });

        const data = await response.json();
        resultDiv.innerHTML = `
            <div class="result-box">
                <div class="result-header">Prediction Result</div>
                <div class="result-content">
                    <ul class="recommendation-list">
                        ${data.prediction.map(activity => `<li>${activity}</li>`).join('')}
                    </ul>
                </div>
                <div class="result-footer">Inference time: ${data.inference_time_ms.toFixed(2)}ms</div>
            </div>
        `;
    } catch (error) {
        resultDiv.innerHTML = `<div class="error-message">Error: ${error.message}</div>`;
    }
}

init();
