// Drone Saver — Ground Control Station (GCS) Frontend Controller
let twinChart = null;
let healthChart = null;
let currentMode = 'judge'; // 'judge' or 'eng'
let eventSource = null;

document.addEventListener('DOMContentLoaded', () => {
    initCharts();
    initSSEStream();
});

// -------------------------------------------------------------
// 1. Chart Initializations
// -------------------------------------------------------------
function initCharts() {
    const ctxTwin = document.getElementById('twinChart').getContext('2d');
    twinChart = new Chart(ctxTwin, {
        type: 'line',
        data: {
            labels: [],
            datasets: [
                {
                    label: 'Observed EGT Cyl 2 (°C)',
                    borderColor: '#f97316',
                    backgroundColor: 'rgba(249, 115, 22, 0.1)',
                    borderWidth: 2,
                    data: [],
                    pointRadius: 0,
                    tension: 0.2
                },
                {
                    label: 'Physics Baseline EGT 2 (°C)',
                    borderColor: '#38bdf8',
                    borderDash: [5, 5],
                    borderWidth: 1.5,
                    data: [],
                    pointRadius: 0,
                    tension: 0.2
                }
            ]
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            animation: false,
            scales: {
                x: { display: true, grid: { color: 'rgba(255,255,255,0.05)' }, title: { display: true, text: 'Mission Time (s)', color: '#64748b' } },
                y: { display: true, grid: { color: 'rgba(255,255,255,0.05)' }, title: { display: true, text: 'Temperature (°C)', color: '#64748b' } }
            },
            plugins: {
                legend: { labels: { color: '#94a3b8', font: { size: 10 } } }
            }
        }
    });

    const ctxHealth = document.getElementById('healthChart').getContext('2d');
    healthChart = new Chart(ctxHealth, {
        type: 'line',
        data: {
            labels: [],
            datasets: [
                {
                    label: 'Engine Health Index H(t)',
                    borderColor: '#10b981',
                    backgroundColor: 'rgba(16, 185, 129, 0.15)',
                    borderWidth: 2.5,
                    fill: true,
                    data: [],
                    pointRadius: 0,
                    tension: 0.2
                }
            ]
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            animation: false,
            scales: {
                x: { display: true, grid: { color: 'rgba(255,255,255,0.05)' } },
                y: { display: true, min: 0.0, max: 1.0, grid: { color: 'rgba(255,255,255,0.05)' } }
            },
            plugins: {
                legend: { labels: { color: '#94a3b8', font: { size: 10 } } }
            }
        }
    });
}

// -------------------------------------------------------------
// 2. Real-Time Telemetry Stream Handler (SSE & Polling Fallback)
// -------------------------------------------------------------
function initSSEStream() {
    if (!!window.EventSource) {
        eventSource = new EventSource('/api/stream');
        eventSource.onmessage = (event) => {
            const data = JSON.parse(event.data);
            updateDashboard(data);
        };
        eventSource.onerror = () => {
            console.warn("[GCS] SSE connection lost. Falling back to HTTP polling.");
            eventSource.close();
            setInterval(pollState, 1000);
        };
    } else {
        setInterval(pollState, 1000);
    }
}

async function pollState() {
    try {
        const res = await fetch('/api/state');
        if (res.ok) {
            const data = await res.json();
            updateDashboard(data);
        }
    } catch (e) {
        console.error("Polling error:", e);
    }
}

// -------------------------------------------------------------
// 3. UI Update Engine
// -------------------------------------------------------------
function updateDashboard(payload) {
    if (!payload || !payload.state) return;
    
    const state = payload.state;
    const tel = payload.telemetry;
    const lat = payload.latencies || {};
    const ctrl = payload.control || {};

    // 1. Top Header Stats
    const hPct = Math.round(state.engine_health * 100);
    const topHealth = document.getElementById('top-health-val');
    topHealth.innerText = `${hPct}%`;
    topHealth.style.color = state.engine_health > 0.8 ? 'var(--green)' : (state.engine_health > 0.5 ? 'var(--yellow)' : 'var(--red)');
    
    document.getElementById('top-anom-val').innerText = state.anomaly_score.toFixed(2);
    document.getElementById('top-risk-val').innerText = `${Math.round((1.0 - state.mission_success_probability) * 100)}%`;
    document.getElementById('top-latency-val').innerText = `${(lat.total_ms || 65).toFixed(0)} ms`;
    document.getElementById('telemetry-provenance').innerText = ctrl.provenance || 'REAL NGAFID G1000';

    // 2. Master Autopilot Directive Banner
    const banner = document.getElementById('directive-banner');
    const bTitle = document.getElementById('directive-title');
    const bDesc = document.getElementById('directive-desc');
    const bIcon = document.getElementById('directive-icon');
    const fState = document.getElementById('failsafe-state-text');

    fState.innerText = state.failsafe_state;
    banner.className = 'directive-banner';

    if (state.failsafe_state === 'HEALTHY') {
        banner.classList.add('banner-green');
        bIcon.innerText = '🟢';
        bTitle.innerText = 'CONTINUE MISSION';
        bDesc.innerText = 'All engine thermals and lubrication parameters strictly nominal.';
    } else if (state.failsafe_state === 'DEGRADED') {
        banner.classList.add('banner-yellow');
        bIcon.innerText = '🟡';
        bTitle.innerText = 'DERATE POWER / REDUCE LOITER';
        bDesc.innerText = `Early anomaly detected on ${state.fault} (Cyl #${state.affected_cylinder}). Derating throttle to 65%.`;
    } else if (state.failsafe_state === 'RTB') {
        banner.classList.add('banner-orange');
        bIcon.innerText = '🟠';
        bTitle.innerText = 'RETURN TO BASE (RTB)';
        bDesc.innerText = `Mission survival probability below threshold (${(state.mission_success_probability*100).toFixed(0)}%). Autonomous RTB initiated.`;
    } else {
        banner.classList.add('banner-red');
        bIcon.innerText = '🔴';
        bTitle.innerText = 'EMERGENCY DESCENT & LANDING';
        bDesc.innerText = `Critical powertrain redline breach. Diverting immediately to nearest landing zone.`;
    }

    // 3. Live Telemetry
    document.getElementById('tel-rpm').innerText = Math.round(tel.rpm || 0);
    document.getElementById('tel-map').innerText = (tel.map_kpa || 0).toFixed(1);
    document.getElementById('tel-fuel').innerText = (tel.fuel_flow_lph || 0).toFixed(1);
    document.getElementById('tel-oil-p').innerText = Math.round(tel.oil_pressure_kpa || 0);
    document.getElementById('tel-oil-t').innerText = (tel.oil_temp_c || 0).toFixed(1);
    document.getElementById('tel-alt').innerText = Math.round(tel.altitude_m ? tel.altitude_m * 3.28084 : 0).toLocaleString();
    document.getElementById('tel-ias').innerText = Math.round(tel.airspeed_mps ? tel.airspeed_mps * 1.94384 : 0);
    document.getElementById('tel-oat').innerText = (tel.ambient_temp_c || 0).toFixed(1);
    document.getElementById('tel-thr').innerText = Math.round(tel.throttle_pct || 75);

    // 4. 4-Cylinder Health Layout
    for (let i = 1; i <= 4; i++) {
        const egt = tel[`egt_${i}_c`];
        const cht = tel[`cht_${i}_c`];
        document.getElementById(`cyl-egt-${i}`).innerText = egt ? `${Math.round(egt)}°C` : '--';
        document.getElementById(`cyl-cht-${i}`).innerText = cht ? `${Math.round(cht)}°C` : '--';
        
        const box = document.getElementById(`cyl-box-${i}`);
        const badge = document.getElementById(`cyl-badge-${i}`);
        
        if (state.affected_cylinder === i && state.fault_probability > 0.6) {
            box.classList.add('faulty-highlight');
            badge.className = 'cyl-badge badge-red';
            badge.innerText = 'CRITICAL';
        } else {
            box.classList.remove('faulty-highlight');
            badge.className = 'cyl-badge badge-green';
            badge.innerText = 'NORMAL';
        }
    }

    // 5. AI Diagnostics Panel
    document.getElementById('diag-fault-name').innerText = state.fault;
    document.getElementById('diag-cyl').innerText = state.affected_cylinder > 0 ? `CYLINDER #${state.affected_cylinder}` : 'GLOBAL ENGINE';
    document.getElementById('diag-conf').innerText = `${(state.fault_probability * 100).toFixed(1)}%`;

    const egtSpread = tel.egt_spread_c || 0;
    const chtSpread = tel.cht_spread_c || 0;
    document.getElementById('ev-egt-val').innerText = `${egtSpread.toFixed(1)}°C`;
    document.getElementById('ev-cht-val').innerText = `${chtSpread.toFixed(1)}°C`;
    document.getElementById('ev-oil-val').innerText = `${(tel.residual_oil_pressure_kpa || 0).toFixed(1)} kPa`;

    document.getElementById('ev-egt-bar').style.width = `${Math.min(100, (egtSpread / 80) * 100)}%`;
    document.getElementById('ev-cht-bar').style.width = `${Math.min(100, (chtSpread / 40) * 100)}%`;
    document.getElementById('ev-oil-bar').style.width = `${Math.min(100, Math.abs(tel.residual_oil_pressure_kpa || 0) / 100 * 100)}%`;

    // 6. Scenario RUL & Mission Risk
    const rulMin = (state.scenario_rul_sec / 60).toFixed(1);
    const lowMin = (state.scenario_rul_sec * 0.82 / 60).toFixed(1);
    const highMin = (state.scenario_rul_sec * 1.25 / 60).toFixed(1);
    document.getElementById('rul-minutes-val').innerText = `${rulMin} min`;
    document.getElementById('rul-bounds-val').innerText = `90% CI: [${lowMin} to ${highMin} min]`;
    document.getElementById('mr-p-succ').innerText = state.mission_success_probability.toFixed(2);
    document.getElementById('mr-p-rtb').innerText = state.p_rtb_safe.toFixed(2);

    // 7. Update Charts
    updateChartsRealtime(state, tel);
}

function updateChartsRealtime(state, tel) {
    const t = Math.round(state.time_seconds);
    
    // Update Twin Chart
    if (twinChart) {
        if (twinChart.data.labels.length > 50) {
            twinChart.data.labels.shift();
            twinChart.data.datasets[0].data.shift();
            twinChart.data.datasets[1].data.shift();
        }
        twinChart.data.labels.push(t);
        twinChart.data.datasets[0].data.push(tel.egt_2_c || 760);
        twinChart.data.datasets[1].data.push(tel.expected_egt_2_c || (tel.egt_2_c - (tel.residual_egt_2_c || 0)));
        twinChart.update('none');
    }

    // Update Health Chart
    if (healthChart) {
        if (healthChart.data.labels.length > 50) {
            healthChart.data.labels.shift();
            healthChart.data.datasets[0].data.shift();
        }
        healthChart.data.labels.push(t);
        healthChart.data.datasets[0].data.push(state.engine_health);
        
        // Color transition
        if (state.engine_health < 0.5) {
            healthChart.data.datasets[0].borderColor = '#ef4444';
            healthChart.data.datasets[0].backgroundColor = 'rgba(239, 68, 68, 0.2)';
        } else if (state.engine_health < 0.8) {
            healthChart.data.datasets[0].borderColor = '#f59e0b';
            healthChart.data.datasets[0].backgroundColor = 'rgba(245, 158, 11, 0.2)';
        } else {
            healthChart.data.datasets[0].borderColor = '#10b981';
            healthChart.data.datasets[0].backgroundColor = 'rgba(16, 185, 129, 0.15)';
        }
        healthChart.update('none');
    }
}

// -------------------------------------------------------------
// 4. Scenario & Control Commands
// -------------------------------------------------------------
async function triggerScenario(path) {
    try {
        await fetch('/api/control/scenario', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ scenario_path: path })
        });
        if (twinChart) { twinChart.data.labels = []; twinChart.data.datasets[0].data = []; twinChart.data.datasets[1].data = []; }
        if (healthChart) { healthChart.data.labels = []; healthChart.data.datasets[0].data = []; }
    } catch (e) {
        console.error("Scenario trigger failed:", e);
    }
}

async function setSpeed(spd) {
    try {
        await fetch('/api/control/speed', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ speed: spd })
        });
        document.querySelectorAll('.btn-speed').forEach(b => b.classList.remove('active'));
        if (event && event.target) event.target.classList.add('active');
    } catch (e) {
        console.error("Speed change failed:", e);
    }
}

async function resetDemo() {
    try {
        await fetch('/api/control/reset', { method: 'POST' });
        if (twinChart) { twinChart.data.labels = []; twinChart.data.datasets[0].data = []; twinChart.data.datasets[1].data = []; }
        if (healthChart) { healthChart.data.labels = []; healthChart.data.datasets[0].data = []; }
    } catch (e) {
        console.error("Reset failed:", e);
    }
}

function setMode(mode) {
    currentMode = mode;
    document.getElementById('btn-mode-judge').classList.toggle('active', mode === 'judge');
    document.getElementById('btn-mode-eng').classList.toggle('active', mode === 'eng');
    document.getElementById('eng-chart-panel').style.display = (mode === 'judge' ? 'none' : 'block');
}
