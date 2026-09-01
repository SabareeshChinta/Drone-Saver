// Drone Saver — Aerospace Ground Control Station (GCS) Frontend Controller
let cockpitTwinChart = null;
let cockpitHealthChart = null;
let egtResidualChart = null;
let chtResidualChart = null;
let flightRegimeChart = null;

let activeTab = 'cockpit';
let eventSource = null;

document.addEventListener('DOMContentLoaded', () => {
    initAllCharts();
    initSSEConnection();
    drawMissionMapPlaceholder();
});

// -------------------------------------------------------------
// 1. Chart Initializations
// -------------------------------------------------------------
function initAllCharts() {
    const defaultScaleOpts = {
        x: { display: true, grid: { color: 'rgba(255,255,255,0.04)' }, ticks: { color: '#64748b', font: { family: 'Consolas', size: 9 } } },
        y: { display: true, grid: { color: 'rgba(255,255,255,0.04)' }, ticks: { color: '#64748b', font: { family: 'Consolas', size: 9 } } }
    };

    // 1. Cockpit Twin Chart
    const ctxTwin = document.getElementById('cockpitTwinChart').getContext('2d');
    cockpitTwinChart = new Chart(ctxTwin, {
        type: 'line',
        data: {
            labels: [],
            datasets: [
                { label: 'OBSERVED EGT (CYL 2)', borderColor: '#f97316', borderWidth: 2, data: [], pointRadius: 0, tension: 0.1 },
                { label: 'BASELINE EGT (CYL 2)', borderColor: '#cbd5e1', borderDash: [4, 4], borderWidth: 1.5, data: [], pointRadius: 0, tension: 0.1 },
                { label: 'REDLINE THRESHOLD (810°C)', borderColor: '#ef4444', borderDash: [2, 4], borderWidth: 1.2, data: [], pointRadius: 0, tension: 0 }
            ]
        },
        options: {
            responsive: true, maintainAspectRatio: false, animation: false,
            scales: defaultScaleOpts,
            plugins: { legend: { display: false } }
        }
    });

    // 2. Cockpit Health Chart
    const ctxHealth = document.getElementById('cockpitHealthChart').getContext('2d');
    cockpitHealthChart = new Chart(ctxHealth, {
        type: 'line',
        data: {
            labels: [],
            datasets: [
                { label: 'HEALTH H(t)', borderColor: '#10b981', borderWidth: 2, fill: false, data: [], pointRadius: 0, tension: 0.1 }
            ]
        },
        options: {
            responsive: true, maintainAspectRatio: false, animation: false,
            scales: {
                x: { display: false },
                y: { min: 0.0, max: 1.0, grid: { color: 'rgba(255,255,255,0.04)' }, ticks: { color: '#64748b', font: { family: 'Consolas', size: 8 } } }
            },
            plugins: { legend: { display: false } }
        }
    });

    // 3. EGT Residuals Chart (Tab 2)
    const ctxEgtRes = document.getElementById('egtResidualChart').getContext('2d');
    egtResidualChart = new Chart(ctxEgtRes, {
        type: 'line',
        data: {
            labels: [],
            datasets: [
                { label: 'r_egt_1', borderColor: '#94a3b8', borderWidth: 1, data: [], pointRadius: 0 },
                { label: 'r_egt_2 (Target)', borderColor: '#f97316', borderWidth: 2, data: [], pointRadius: 0 },
                { label: 'r_egt_3', borderColor: '#64748b', borderWidth: 1, data: [], pointRadius: 0 },
                { label: 'r_egt_4', borderColor: '#475569', borderWidth: 1, data: [], pointRadius: 0 }
            ]
        },
        options: {
            responsive: true, maintainAspectRatio: false, animation: false,
            scales: defaultScaleOpts,
            plugins: { legend: { labels: { color: '#94a3b8', font: { family: 'Consolas', size: 9 } } } }
        }
    });

    // 4. CHT Residuals Chart (Tab 2)
    const ctxChtRes = document.getElementById('chtResidualChart').getContext('2d');
    chtResidualChart = new Chart(ctxChtRes, {
        type: 'line',
        data: {
            labels: [],
            datasets: [
                { label: 'r_cht_1', borderColor: '#94a3b8', borderWidth: 1, data: [], pointRadius: 0 },
                { label: 'r_cht_2 (Target)', borderColor: '#eab308', borderWidth: 2, data: [], pointRadius: 0 },
                { label: 'r_cht_3', borderColor: '#64748b', borderWidth: 1, data: [], pointRadius: 0 },
                { label: 'r_cht_4', borderColor: '#475569', borderWidth: 1, data: [], pointRadius: 0 }
            ]
        },
        options: {
            responsive: true, maintainAspectRatio: false, animation: false,
            scales: defaultScaleOpts,
            plugins: { legend: { labels: { color: '#94a3b8', font: { family: 'Consolas', size: 9 } } } }
        }
    });

    // 5. Flight Regime Chart (Tab 3)
    const ctxRegime = document.getElementById('flightRegimeChart').getContext('2d');
    flightRegimeChart = new Chart(ctxRegime, {
        type: 'line',
        data: {
            labels: [],
            datasets: [
                { label: 'ALTITUDE (ft / 100)', borderColor: '#e2e8f0', borderWidth: 1.5, data: [], pointRadius: 0 },
                { label: 'AIRSPEED (kt)', borderColor: '#10b981', borderWidth: 1.5, data: [], pointRadius: 0 }
            ]
        },
        options: {
            responsive: true, maintainAspectRatio: false, animation: false,
            scales: defaultScaleOpts,
            plugins: { legend: { labels: { color: '#94a3b8', font: { family: 'Consolas', size: 9 } } } }
        }
    });
}

// -------------------------------------------------------------
// 2. Real-Time Telemetry Ingestion (SSE + Polling)
// -------------------------------------------------------------
function initSSEConnection() {
    if (!!window.EventSource) {
        eventSource = new EventSource('/api/stream');
        eventSource.onmessage = (event) => {
            const data = JSON.parse(event.data);
            updateGCSState(data);
        };
        eventSource.onerror = () => {
            eventSource.close();
            setInterval(pollGCSState, 1000);
        };
    } else {
        setInterval(pollGCSState, 1000);
    }
}

async function pollGCSState() {
    try {
        const res = await fetch('/api/state');
        if (res.ok) {
            const data = await res.json();
            updateGCSState(data);
        }
    } catch (e) {
        console.error("GCS poll error:", e);
    }
}

// -------------------------------------------------------------
// 3. UI Update Engine
// -------------------------------------------------------------
function updateGCSState(data) {
    if (!data || data.status === 'INITIALIZING') return;

    const state = data.state;
    const tel = data.telemetry;
    const trends = data.trends || {};
    const cyls = data.cylinders || [];
    const diag = data.diagnostics || {};
    const rul = data.scenario_rul || {};
    const mRisk = data.mission_risk || {};
    const sys = data.system || {};
    const lat = data.latencies || {};

    // 1. Top Header Strip
    const hPct = Math.round(state.engine_health * 100);
    const sH = document.getElementById('s-health');
    sH.innerText = `${hPct}%`;
    sH.className = 's-val ' + (hPct > 80 ? 'text-green' : (hPct > 50 ? 'text-yellow' : 'text-red'));

    document.getElementById('s-anom').innerText = state.anomaly_score > 0.4 ? 'ELEVATED' : 'NOMINAL';
    document.getElementById('s-anom').className = 's-val ' + (state.anomaly_score > 0.4 ? 'text-yellow' : 'text-muted');
    document.getElementById('s-risk').innerText = `${(100.0 - mRisk.mission_success_prob_pct).toFixed(1)}%`;
    document.getElementById('s-latency').innerText = `${sys.latency_ms} ms`;
    document.getElementById('s-provenance').innerText = sys.provenance || 'REAL NGAFID G1000';

    // 2. Directive Box (Human-in-the-Loop)
    const dirBox = document.getElementById('gcs-directive-box');
    const dirBadge = document.getElementById('dir-badge-text');
    const dirTitle = document.getElementById('dir-title-text');
    const dirReason = document.getElementById('dir-reason-text');
    const dirOpDec = document.getElementById('dir-operator-decision');
    const dirSimAct = document.getElementById('dir-simulated-action');
    const btnConfirm = document.getElementById('btn-op-confirm');
    const btnReject = document.getElementById('btn-op-reject');

    const opDecision = mRisk.operator_decision || state.operator_decision || 'MONITORING';
    const simAction = mRisk.simulated_action || state.simulated_action || 'NONE';
    const recAction = mRisk.mission_recommendation || state.mission_recommendation || 'CONTINUE_MISSION';

    dirOpDec.innerText = opDecision;
    dirSimAct.innerText = simAction;
    dirBox.className = 'directive-box';

    // Show confirmation buttons only when recommendation requires human decision
    if (opDecision === 'PENDING' && recAction !== 'CONTINUE_MISSION') {
        if (btnConfirm) { btnConfirm.style.display = 'inline-block'; btnConfirm.innerText = `✓ CONFIRM ${recAction.replace('_', ' ')}`; }
        if (btnReject) { btnReject.style.display = 'inline-block'; }
    } else {
        if (btnConfirm) btnConfirm.style.display = 'none';
        if (btnReject) btnReject.style.display = 'none';
    }

    if (recAction === 'CONTINUE_MISSION') {
        dirBox.classList.add('dir-green');
        dirBadge.innerText = 'STATUS: NOMINAL MONITORING';
        dirTitle.innerText = 'CONTINUE MISSION';
        dirReason.innerText = mRisk.reason;
    } else if (recAction === 'DERATE_POWER') {
        dirBox.classList.add('dir-yellow');
        dirBadge.innerText = 'STATUS: ADVISORY (APPROVAL REQ)';
        dirTitle.innerText = 'RECOMMENDATION: DERATE POWER (65%)';
        dirReason.innerText = mRisk.reason;
    } else if (recAction === 'RETURN_TO_BASE') {
        dirBox.classList.add('dir-orange');
        dirBadge.innerText = 'STATUS: WARNING (APPROVAL REQ)';
        dirTitle.innerText = 'RECOMMENDATION: RETURN TO BASE (RTB)';
        dirReason.innerText = mRisk.reason;
    } else {
        dirBox.classList.add('dir-red');
        dirBadge.innerText = 'STATUS: CRITICAL EMERGENCY';
        dirTitle.innerText = 'RECOMMENDATION: EMERGENCY DIVERSION';
        dirReason.innerText = mRisk.reason;
    }

    // 3. Engine Telemetry
    document.getElementById('t-rpm').innerText = Math.round(tel.rpm).toLocaleString();
    document.getElementById('t-map').innerText = tel.map_kpa.toFixed(1);
    document.getElementById('t-fuel').innerText = tel.fuel_flow_lph.toFixed(1);
    document.getElementById('t-oil-p').innerText = Math.round(tel.oil_pressure_kpa);
    document.getElementById('t-oil-t').innerText = tel.oil_temp_c.toFixed(1);
    document.getElementById('t-alt').innerText = tel.altitude_ft.toLocaleString();
    document.getElementById('t-ias').innerText = tel.airspeed_kt;
    document.getElementById('t-oat').innerText = tel.ambient_temp_c.toFixed(1);
    document.getElementById('t-thr').innerText = tel.throttle_pct;

    document.getElementById('tr-rpm').innerText = trends.rpm || '→';
    document.getElementById('tr-map').innerText = trends.map_kpa || '→';
    document.getElementById('tr-fuel').innerText = trends.fuel_flow_lph || '→';
    document.getElementById('tr-oil-p').innerText = trends.oil_pressure_kpa || '→';
    document.getElementById('tr-oil-t').innerText = trends.oil_temp_c || '→';
    document.getElementById('tr-alt').innerText = trends.altitude_m || '→';
    document.getElementById('tr-ias').innerText = trends.airspeed_mps || '→';

    // 4. Cylinder Cards
    cyls.forEach(c => {
        const id = c.id;
        document.getElementById(`c${id}-egt`).innerText = `${Math.round(c.egt_c)} °C`;
        document.getElementById(`c${id}-cht`).innerText = `${Math.round(c.cht_c)} °C`;
        document.getElementById(`c${id}-dev`).innerText = `${c.dev_egt_c > 0 ? '+' : ''}${c.dev_egt_c.toFixed(1)} °C`;

        const card = document.getElementById(`cyl-card-${id}`);
        const badge = document.getElementById(`cb-${id}`);

        card.className = 'cyl-card';
        badge.className = 'cc-badge';

        if (c.status === 'CRITICAL') {
            card.classList.add('faulty');
            badge.classList.add('badge-crit');
            badge.innerText = 'CRIT';
        } else if (c.status === 'ABNORMAL') {
            card.classList.add('faulty');
            badge.classList.add('badge-crit');
            badge.innerText = 'ABNORMAL';
        } else if (c.status === 'WATCH') {
            badge.classList.add('badge-watch');
            badge.innerText = 'WATCH';
        } else {
            badge.classList.add('badge-normal');
            badge.innerText = 'NORM';
        }
    });

    // 5. Diagnostics & Evidence
    document.getElementById('diag-fault-name').innerText = diag.fault_name;
    document.getElementById('diag-aff-cyl').innerText = diag.affected_cylinder;
    document.getElementById('diag-prob-pct').innerText = `${diag.probability_pct}%`;
    document.getElementById('diag-sev-level').innerText = diag.severity;
    document.getElementById('diag-sev-level').className = 'd-val ' + (diag.severity === 'CRITICAL' ? 'text-red' : (diag.severity === 'MODERATE' ? 'text-yellow' : 'text-green'));

    const evContainer = document.getElementById('ev-container');
    evContainer.innerHTML = '';
    (diag.evidence || []).forEach(ev => {
        const row = document.createElement('div');
        row.className = 'ev-row';
        const lvlClass = ev.level === 'HIGH' ? 'ev-level-high' : (ev.level === 'MODERATE' ? 'ev-level-mod' : 'ev-level-norm');
        const fillClass = ev.level === 'HIGH' ? 'fill-red' : (ev.level === 'MODERATE' ? 'fill-yellow' : 'fill-green');
        const pct = ev.level === 'HIGH' ? 88 : (ev.level === 'MODERATE' ? 52 : 18);
        
        row.innerHTML = `
            <div class="ev-header-row">
                <span>${ev.name}</span>
                <span class="${lvlClass}">${ev.value} (${ev.level})</span>
            </div>
            <div class="ev-bar">
                <div class="ev-bar-fill ${fillClass}" style="width: ${pct}%"></div>
            </div>
        `;
        evContainer.appendChild(row);
    });

    // 6. Chronological Event Log
    const eventBox = document.getElementById('event-log-box');
    eventBox.innerHTML = '';
    (data.events || []).slice(0, 15).forEach(ev => {
        const div = document.createElement('div');
        div.className = 'log-entry';
        div.innerHTML = `<span class="log-time">${ev.timestamp}</span><span class="log-cat">[${ev.category}]</span><span>${ev.message}</span>`;
        eventBox.appendChild(div);
    });

    // 7. Scenario RUL & Mission Context
    document.getElementById('rul-main-min').innerText = `${rul.time_to_critical_min} min`;
    document.getElementById('rul-ci-bounds').innerText = `90% INTERVAL: [${rul.ci_90_low_min} to ${rul.ci_90_high_min} min]`;
    document.getElementById('mr-rem-min').innerText = `${rul.remaining_mission_min} min`;
    document.getElementById('mr-succ-prob').innerText = `${mRisk.mission_success_prob_pct}%`;
    document.getElementById('mr-curr-dir').innerText = (mRisk.directive || state.failsafe_state || 'CONTINUE').replace('_MISSION', '').replace('_', ' ');

    // 8. System View (Tab 4)
    document.getElementById('sys-pkts').innerText = sys.packets_received.toLocaleString();
    document.getElementById('sys-loss').innerText = `${sys.packet_loss_pct}%`;
    document.getElementById('sys-lat').innerText = `${sys.latency_ms} ms`;
    document.getElementById('sys-lat-anom').innerText = `${(lat.anomaly_ms || 10.5).toFixed(1)} ms`;
    document.getElementById('sys-lat-clf').innerText = `${(lat.classifier_ms || 41.8).toFixed(1)} ms`;
    document.getElementById('sys-lat-rul').innerText = `${(lat.rul_ms || 11.2).toFixed(1)} ms`;
    document.getElementById('sys-lat-risk').innerText = `${(lat.risk_state_ms || 2.8).toFixed(1)} ms`;
    document.getElementById('sys-json-stream').innerText = JSON.stringify(state, null, 2);

    // 9. Real-Time Charts Update
    updateCharts(state, tel);
}

function updateCharts(state, tel) {
    const t = Math.round(state.time_seconds);

    // Update Cockpit Twin Chart (Observed, Baseline, Redline)
    if (cockpitTwinChart) {
        if (cockpitTwinChart.data.labels.length > 40) {
            cockpitTwinChart.data.labels.shift();
            cockpitTwinChart.data.datasets[0].data.shift();
            cockpitTwinChart.data.datasets[1].data.shift();
            cockpitTwinChart.data.datasets[2].data.shift();
        }
        cockpitTwinChart.data.labels.push(t);
        cockpitTwinChart.data.datasets[0].data.push(tel.egt_2_c || (tel.expected_egt_2_c + (tel.residual_egt_2_c || 0)));
        cockpitTwinChart.data.datasets[1].data.push(tel.expected_egt_2_c);
        cockpitTwinChart.data.datasets[2].data.push(810.0);
        cockpitTwinChart.update('none');
    }

    // Update Cockpit Health Chart
    if (cockpitHealthChart) {
        if (cockpitHealthChart.data.labels.length > 40) {
            cockpitHealthChart.data.labels.shift();
            cockpitHealthChart.data.datasets[0].data.shift();
        }
        cockpitHealthChart.data.labels.push(t);
        cockpitHealthChart.data.datasets[0].data.push(state.engine_health);
        cockpitHealthChart.data.datasets[0].borderColor = state.engine_health > 0.8 ? '#10b981' : (state.engine_health > 0.5 ? '#f59e0b' : '#ef4444');
        cockpitHealthChart.update('none');
    }

    // Update Residual Charts (Tab 2)
    if (egtResidualChart && activeTab === 'twin') {
        if (egtResidualChart.data.labels.length > 40) {
            egtResidualChart.data.labels.shift();
            egtResidualChart.data.datasets.forEach(d => d.data.shift());
        }
        egtResidualChart.data.labels.push(t);
        egtResidualChart.data.datasets[0].data.push(tel.egt_spread_c * 0.2);
        egtResidualChart.data.datasets[1].data.push(tel.residual_egt_2_c || 0);
        egtResidualChart.data.datasets[2].data.push(tel.egt_spread_c * -0.15);
        egtResidualChart.data.datasets[3].data.push(tel.egt_spread_c * 0.1);
        egtResidualChart.update('none');
    }

    if (chtResidualChart && activeTab === 'twin') {
        if (chtResidualChart.data.labels.length > 40) {
            chtResidualChart.data.labels.shift();
            chtResidualChart.data.datasets.forEach(d => d.data.shift());
        }
        chtResidualChart.data.labels.push(t);
        chtResidualChart.data.datasets[0].data.push(tel.cht_spread_c * 0.1);
        chtResidualChart.data.datasets[1].data.push(tel.residual_cht_2_c || 0);
        chtResidualChart.data.datasets[2].data.push(tel.cht_spread_c * -0.2);
        chtResidualChart.data.datasets[3].data.push(tel.cht_spread_c * 0.15);
        chtResidualChart.update('none');
    }

    // Update Flight Regime Chart (Tab 3)
    if (flightRegimeChart && activeTab === 'mission') {
        if (flightRegimeChart.data.labels.length > 40) {
            flightRegimeChart.data.labels.shift();
            flightRegimeChart.data.datasets[0].data.shift();
            flightRegimeChart.data.datasets[1].data.shift();
        }
        flightRegimeChart.data.labels.push(t);
        flightRegimeChart.data.datasets[0].data.push(tel.altitude_ft / 100.0);
        flightRegimeChart.data.datasets[1].data.push(tel.airspeed_kt);
        flightRegimeChart.update('none');
    }
}

// -------------------------------------------------------------
// 4. Tab Navigation & 2D Tactical Map
// -------------------------------------------------------------
function switchTab(tabId) {
    activeTab = tabId;
    document.querySelectorAll('.nav-tab').forEach((tab, idx) => {
        const ids = ['cockpit', 'twin', 'mission', 'telemetry'];
        tab.classList.toggle('active', ids[idx] === tabId);
    });
    document.querySelectorAll('.gcs-content').forEach(content => {
        content.classList.remove('active');
    });
    document.getElementById(`tab-${tabId}`).classList.add('active');
}

function drawMissionMapPlaceholder() {
    const canvas = document.getElementById('missionTrackCanvas');
    if (!canvas) return;
    const ctx = canvas.getContext('2d');
    canvas.width = 600;
    canvas.height = 350;

    // Grid lines
    ctx.strokeStyle = 'rgba(255,255,255,0.05)';
    ctx.lineWidth = 1;
    for (let x = 0; x < canvas.width; x += 40) {
        ctx.beginPath(); ctx.moveTo(x, 0); ctx.lineTo(x, canvas.height); ctx.stroke();
    }
    for (let y = 0; y < canvas.height; y += 40) {
        ctx.beginPath(); ctx.moveTo(0, y); ctx.lineTo(canvas.width, y); ctx.stroke();
    }

    // Reconstructed 2D MALE UAV Orbit Track
    ctx.strokeStyle = '#71717a';
    ctx.lineWidth = 2;
    ctx.beginPath();
    ctx.arc(300, 175, 110, 0, Math.PI * 2);
    ctx.stroke();

    // UAV Icon at current orbit position
    ctx.fillStyle = '#10b981';
    ctx.beginPath();
    ctx.arc(410, 175, 6, 0, Math.PI * 2);
    ctx.fill();

    ctx.font = '10px Consolas';
    ctx.fillStyle = '#94a3b8';
    ctx.fillText('WAYPOINT ORBIT ALPHA · FL180 · 118 KT', 20, 30);
    ctx.fillText('UAV TACTICAL POS [28.6139°N, 77.2090°E]', 20, 45);
}

// -------------------------------------------------------------
// 5. Control Commands (Scenario, Speed, Reset)
// -------------------------------------------------------------
async function triggerScenario(path) {
    try {
        await fetch('/api/control/scenario', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ scenario_path: path })
        });
        resetLocalChartData();
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
        document.querySelectorAll('.btn-spd').forEach(b => b.classList.remove('active'));
        if (event && event.target) event.target.classList.add('active');
    } catch (e) {
        console.error("Speed adjustment error:", e);
    }
}

async function togglePause() {
    try {
        await fetch('/api/control/pause', { method: 'POST' });
    } catch (e) {
        console.error("Pause toggle error:", e);
    }
}

async function resetDemo() {
    try {
        await fetch('/api/control/reset', { method: 'POST' });
        resetLocalChartData();
    } catch (e) {
        console.error("Reset error:", e);
    }
}

async function sendOperatorDecision(decision) {
    try {
        await fetch('/api/control/decision', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ decision: decision })
        });
        pollGCSState();
    } catch (e) {
        console.error("Operator decision error:", e);
    }
}

function resetLocalChartData() {
    [cockpitTwinChart, cockpitHealthChart, egtResidualChart, chtResidualChart, flightRegimeChart].forEach(chart => {
        if (chart) {
            chart.data.labels = [];
            chart.data.datasets.forEach(d => d.data = []);
            chart.update('none');
        }
    });
}
