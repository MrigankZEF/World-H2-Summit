/* ════════════════════════════════════════════════════════════════
   ZEF Poll · state machine + reveal renderer
   Reads question config from server-injected JSON blocks.
   ════════════════════════════════════════════════════════════════ */

const QUESTIONS = JSON.parse(document.getElementById('cfg-questions').textContent);
const HOOKS     = JSON.parse(document.getElementById('cfg-hooks').textContent);
const BENCHMARK = JSON.parse(document.getElementById('cfg-benchmark').textContent);
let AGGREGATE   = JSON.parse(document.getElementById('cfg-aggregate').textContent);

const Q_IDS = QUESTIONS.map(q => q.id);
const Q_BY_ID = Object.fromEntries(QUESTIONS.map(q => [q.id, q]));
const SHORT = Object.fromEntries(QUESTIONS.map(q => [q.id, q.short_labels || {}]));
const VALUES = Object.fromEntries(QUESTIONS.map(q => [q.id, q.options.map(o => o.value)]));
const IS_MULTI = qid => !!(Q_BY_ID[qid] && Q_BY_ID[qid].multi);

function defaultAnswer(qid) {
  return IS_MULTI(qid) ? [] : null;
}

const state = {
  current: 'hook',
  answers: Object.fromEntries(Q_IDS.map(id => [id, defaultAnswer(id)])),
  sessionId: (crypto && crypto.randomUUID) ? crypto.randomUUID() : 'sess-' + Date.now() + '-' + Math.random().toString(36).slice(2,8),
  pollPosted: false,
};

// Holds the auto-advance setTimeout id so back-clicks can cancel it.
let pendingAdvance = null;

/* ── Hook headlines ──────────────────────────────────── */
function renderHook(key) {
  const words = HOOKS[key] || Object.values(HOOKS)[0];
  const el = document.getElementById('hook-headline');
  if (!el || !words) return;
  el.innerHTML = '';
  words.forEach((w, i) => {
    const span = document.createElement('span');
    const isNum = typeof w === 'object';
    span.className = 'word' + (isNum ? ' num' : '');
    span.textContent = isNum ? w.num : w;
    span.style.transitionDelay = (i * 30) + 'ms';
    el.appendChild(span);
  });
  document.body.setAttribute('data-hook', key);
}
renderHook(document.body.getAttribute('data-hook') || 'C');

/* ── Scene navigation ────────────────────────────────── */
function goto(id, opts = {}) {
  // Fix A: cancel any pending auto-advance so it can't fire after the user navigates.
  if (pendingAdvance) {
    clearTimeout(pendingAdvance);
    pendingAdvance = null;
  }

  // Fix B: never land on reveal with missing answers — redirect to first unanswered question.
  if (id === 'reveal' && !allAnswered()) {
    const missing = Q_IDS.find(qid => {
      const v = state.answers[qid];
      return IS_MULTI(qid) ? (!Array.isArray(v) || v.length === 0) : !v;
    });
    if (missing) id = missing;
  }

  if (opts.reset) {
    Q_IDS.forEach(qid => state.answers[qid] = defaultAnswer(qid));
    state.pollPosted = false;
    document.querySelectorAll('.opt').forEach(o => {
      o.classList.remove('is-locked');
      o.classList.remove('is-disabled');
    });
    document.querySelectorAll('.continue-btn').forEach(btn => {
      btn.disabled = true;
      const c = btn.querySelector('.count');
      if (c) c.textContent = '0';
    });
    document.querySelectorAll('#role-chips .chip').forEach(c => c.classList.remove('is-on'));
    selectedRole = null;
    document.getElementById('lead-form').style.display = '';
    document.getElementById('lead-success').classList.remove('is-on');
    const errEl = document.getElementById('lead-error');
    if (errEl) errEl.hidden = true;
    document.getElementById('lead-email').value = '';
  }
  const cur = document.querySelector('.scene.is-active');
  const next = document.getElementById('scene-' + id);
  if (!next || next === cur) return;

  if (cur) {
    cur.classList.remove('is-active');
    cur.classList.add('is-exit-left');
    setTimeout(() => cur.classList.remove('is-exit-left'), 340);
  }
  // Activate next scene synchronously so pointer-events flip immediately
  // (no 60ms gap where every scene is pointer-events:none and clicks land on nothing).
  next.classList.add('is-active');
  next.scrollTop = 0;
  state.current = id;
  if (id === 'reveal') renderReveal();
  if (id === 'hook') renderHook(document.body.getAttribute('data-hook') || 'C');
  syncSelections();
}

/* ── data-goto wiring (delegated; survives any per-element binding race) ─── */
document.addEventListener('click', (e) => {
  const goEl = e.target.closest('[data-goto]');
  if (!goEl) return;
  const target = goEl.getAttribute('data-goto');
  const reset = goEl.getAttribute('data-reset') === '1';
  console.log('[nav]', target, 'from', state.current);
  goto(target, { reset });
});

/* ── Option tap → lock-in (single) or toggle (multi) ─── */
document.querySelectorAll('.options').forEach(group => {
  const qid = group.dataset.question;
  const isMulti = group.dataset.multi === '1';
  const maxSelect = parseInt(group.dataset.maxSelect || '1', 10);

  group.querySelectorAll('.opt').forEach(opt => {
    opt.addEventListener('click', () => {
      if (isMulti) {
        const v = opt.dataset.value;
        const arr = Array.isArray(state.answers[qid]) ? [...state.answers[qid]] : [];
        const idx = arr.indexOf(v);
        if (idx >= 0) {
          arr.splice(idx, 1);
          opt.classList.remove('is-locked');
        } else {
          if (arr.length >= maxSelect) return; // cap reached, ignore
          arr.push(v);
          opt.classList.add('is-locked');
        }
        state.answers[qid] = arr;
        updateMultiState(group);
      } else {
        group.querySelectorAll('.opt').forEach(o => o.classList.remove('is-locked'));
        opt.classList.add('is-locked');
        state.answers[qid] = opt.dataset.value;

        const i = Q_IDS.indexOf(qid);
        const isLast = i === Q_IDS.length - 1;
        const nextId = isLast ? 'reveal' : Q_IDS[i + 1];
        pendingAdvance = setTimeout(() => {
          pendingAdvance = null;
          goto(nextId);
        }, 280);
        if (isLast) postPoll();
      }
    });
  });
});

function updateMultiState(group) {
  const qid = group.dataset.question;
  const maxSelect = parseInt(group.dataset.maxSelect || '1', 10);
  const arr = Array.isArray(state.answers[qid]) ? state.answers[qid] : [];
  const atCap = arr.length >= maxSelect;
  group.querySelectorAll('.opt').forEach(opt => {
    const picked = arr.includes(opt.dataset.value);
    opt.classList.toggle('is-disabled', atCap && !picked);
  });
  // Continue button below this scene
  const scene = group.closest('.scene');
  const btn = scene && scene.querySelector('.continue-btn[data-question="' + qid + '"]');
  if (btn) {
    btn.disabled = arr.length === 0;
    const c = btn.querySelector('.count');
    if (c) c.textContent = String(arr.length);
  }
}

/* ── Continue buttons (multi-select scenes) ────────── */
document.querySelectorAll('.continue-btn').forEach(btn => {
  btn.addEventListener('click', () => {
    const qid = btn.dataset.question;
    if (btn.disabled) return;
    const i = Q_IDS.indexOf(qid);
    const isLast = i === Q_IDS.length - 1;
    const nextId = isLast ? 'reveal' : Q_IDS[i + 1];
    goto(nextId);
    if (isLast) postPoll();
  });
});

/* ── Restore selections when revisiting ──────────────── */
function syncSelections() {
  document.querySelectorAll('.options').forEach(group => {
    const qid = group.dataset.question;
    const v = state.answers[qid];
    const isMulti = group.dataset.multi === '1';
    if (isMulti) {
      const arr = Array.isArray(v) ? v : [];
      group.querySelectorAll('.opt').forEach(o => o.classList.toggle('is-locked', arr.includes(o.dataset.value)));
      updateMultiState(group);
    } else {
      group.querySelectorAll('.opt').forEach(o => o.classList.toggle('is-locked', !!v && o.dataset.value === v));
    }
  });
}

/* ════════════════════════════════════════════════════════════════
   API calls
   ════════════════════════════════════════════════════════════════ */
function allAnswered() {
  return Q_IDS.every(id => {
    const v = state.answers[id];
    if (IS_MULTI(id)) return Array.isArray(v) && v.length > 0;
    return !!v;
  });
}

async function postPoll() {
  if (state.pollPosted) return;
  if (!allAnswered()) return;
  state.pollPosted = true;
  try {
    const r = await fetch('/api/poll', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        sessionId: state.sessionId,
        submittedAt: new Date().toISOString(),
        source: 'whs2026',
        answers: { ...state.answers },
      }),
    });
    if (!r.ok) throw new Error('poll failed');
    fetchAggregate();
  } catch (err) {
    console.warn('[poll]', err);
    state.pollPosted = false;
  }
}

async function fetchAggregate() {
  try {
    const r = await fetch('/api/results', { cache: 'no-store' });
    if (!r.ok) return;
    const data = await r.json();
    AGGREGATE = data;
    if (state.current === 'reveal') renderReveal();
  } catch (err) {
    console.warn('[results]', err);
  }
}

async function postLead(payload) {
  const r = await fetch('/api/lead', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(payload),
  });
  if (!r.ok) {
    const detail = await r.json().catch(() => ({}));
    throw new Error(detail.detail || 'lead submission failed');
  }
  return r.json();
}

/* ════════════════════════════════════════════════════════════════
   REVEAL
   ════════════════════════════════════════════════════════════════ */

const PRICE_ORDER = ['lt2', '2to3', '3to5', '5to8', 'gt8'];

function computeInsight() {
  const primary = QUESTIONS[0];
  const g = state.answers[primary.id];
  const data = AGGREGATE[primary.id] || {};
  if (!g) return `Here's how the room answered <b>${primary.chart_title}</b>.`;

  const isPriceQ = primary.options.every(o => PRICE_ORDER.includes(o.value));
  if (isPriceQ) {
    const idx = PRICE_ORDER.indexOf(g);
    let higher = 0, lower = 0;
    PRICE_ORDER.slice(idx + 1).forEach(k => higher += (data[k] || 0));
    PRICE_ORDER.slice(0, idx).forEach(k => lower += (data[k] || 0));
    const same = data[g] || 0;
    if (g === 'lt2' || g === '2to3') {
      return `You're more optimistic than <span class="pct">${Math.round(higher * 100)}%</span> of the room.`;
    }
    if (g === 'gt8' || g === '5to8') {
      return `<span class="pct">${Math.round(lower * 100)}%</span> of the room is more optimistic than you.`;
    }
    return `You're with <span class="pct">${Math.round(same * 100)}%</span> of the room.`;
  }
  const pct = Math.round((data[g] || 0) * 100);
  return `You're with <span class="pct">${pct}%</span> of the room.`;
}

function escapeHtml(s) {
  return String(s)
    .replaceAll('&', '&amp;')
    .replaceAll('<', '&lt;')
    .replaceAll('>', '&gt;')
    .replaceAll('"', '&quot;')
    .replaceAll("'", '&#39;');
}

function buildBarChart(container, qid, userAnswer) {
  const bars = container.querySelector('.bars');
  if (!bars) return;
  bars.innerHTML = '';

  const data = AGGREGATE[qid] || {};
  const shortLabels = SHORT[qid] || {};
  const keys = VALUES[qid] || Object.keys(data);
  const max = Math.max(...keys.map(k => data[k] || 0), 0.0001);

  const userSet = new Set(Array.isArray(userAnswer) ? userAnswer : (userAnswer ? [userAnswer] : []));

  keys.forEach((k, i) => {
    const pct = data[k] || 0;
    const scaled = (pct / max) * 100;
    const isUser = userSet.has(k);
    const row = document.createElement('div');
    row.className = 'bar-row' + (isUser ? ' is-user' : '');
    const delay = (i * 80) + (isUser ? 120 : 0);
    row.innerHTML = `
      <div class="bar-label">${escapeHtml(shortLabels[k] || k)}</div>
      <div class="bar-track"><div class="bar-fill" style="--d:${delay}ms"></div></div>
      <div class="bar-pct" style="--d:${delay}ms">${Math.round(pct * 100)}%</div>
    `;
    bars.appendChild(row);
    requestAnimationFrame(() => {
      setTimeout(() => {
        row.querySelector('.bar-fill').style.width = scaled + '%';
      }, 40);
    });
  });

  if (BENCHMARK && BENCHMARK.question_id === qid) {
    const marker = container.querySelector('.zef-marker');
    if (marker) {
      marker.hidden = false;
      marker.querySelector('.kicker').textContent = BENCHMARK.kicker || '';
      const valueEl = marker.querySelector('.value');
      valueEl.innerHTML = `${escapeHtml(BENCHMARK.value || '')}<span class="unit">${escapeHtml(BENCHMARK.unit || '')}</span>`;
      marker.querySelector('.red-pill').textContent = BENCHMARK.pill || '';

      const bucketIdx = keys.indexOf(BENCHMARK.bucket);
      if (bucketIdx >= 0) {
        const offset = Math.min(Math.max(BENCHMARK.bucket_offset || 0, 0), 1);
        const leftPct = (bucketIdx / keys.length + (offset / keys.length)) * 100;
        const tickLine = marker.querySelector('.tick-line');
        if (tickLine) tickLine.style.left = `calc(${leftPct.toFixed(1)}% + 12px)`;
      }
    }
  }
}

function renderReveal() {
  const primary = QUESTIONS[0];
  document.getElementById('reveal-headline').innerHTML = computeInsight();
  const total = AGGREGATE.total || 0;
  const isPreview = AGGREGATE.source !== 'sheet';
  const totalLabel = total > 0 ? `${total} ${total === 1 ? 'person has' : 'people have'} answered` : 'no one has answered yet';
  document.getElementById('reveal-sub').innerHTML = isPreview
    ? `${totalLabel} so far. Seed distribution shown until the threshold is reached.`
    : `Here's how ${total} people answered <b>${primary.chart_title}</b>.` +
      (state.answers[primary.id] ? ` Yours is in red.` : '');

  document.querySelectorAll('.chart .rev-n').forEach(el => el.textContent = total);
  document.getElementById('rev-live').textContent = isPreview
    ? `PREVIEW · ${total} / ${AGGREGATE.threshold || 5}`
    : `${total} ANSWERED`;

  // Toggle the seed-distribution note on the Q1 chart
  const seedNote = document.querySelector('#chart-' + primary.id + ' .seed-note');
  if (seedNote) {
    seedNote.hidden = !isPreview;
    const thr = seedNote.querySelector('.threshold-n');
    if (thr) thr.textContent = AGGREGATE.threshold || 5;
  }

  // Render the Q1 chart
  const chart = document.getElementById('chart-' + primary.id);
  if (chart) {
    buildBarChart(chart, primary.id, state.answers[primary.id]);
    setTimeout(() => chart.classList.add('is-revealed'), 150);
  }
}

/* ════════════════════════════════════════════════════════════════
   LEAD
   ════════════════════════════════════════════════════════════════ */

let selectedRole = null;
document.querySelectorAll('#role-chips .chip').forEach(chip => {
  chip.addEventListener('click', () => {
    const r = chip.dataset.role;
    if (selectedRole === r) {
      chip.classList.remove('is-on');
      selectedRole = null;
    } else {
      document.querySelectorAll('#role-chips .chip').forEach(c => c.classList.remove('is-on'));
      chip.classList.add('is-on');
      selectedRole = r;
    }
  });
});

document.getElementById('lead-form').addEventListener('submit', async e => {
  e.preventDefault();
  const email = document.getElementById('lead-email');
  const errEl = document.getElementById('lead-error');
  const btn = e.target.querySelector('.lead-submit');
  const v = email.value.trim();
  errEl.hidden = true;

  if (!/^\S+@\S+\.\S+$/.test(v)) {
    email.classList.add('is-invalid');
    setTimeout(() => email.classList.remove('is-invalid'), 1800);
    return;
  }
  btn.disabled = true;
  try {
    await postLead({
      sessionId: state.sessionId,
      email: v,
      role: selectedRole,
      consent: true,
      submittedAt: new Date().toISOString(),
    });
    document.getElementById('lead-form').style.display = 'none';
    document.getElementById('lead-success').classList.add('is-on');
  } catch (err) {
    errEl.textContent = "Couldn't send that — please try again.";
    errEl.hidden = false;
  } finally {
    btn.disabled = false;
  }
});

/* ════════════════════════════════════════════════════════════════
   Demo hotkeys
   ════════════════════════════════════════════════════════════════ */
document.addEventListener('keydown', e => {
  if (e.target && (e.target.tagName === 'INPUT' || e.target.tagName === 'TEXTAREA')) return;
  if (e.key === 'd' || e.key === 'D') {
    QUESTIONS.forEach(q => {
      const second = q.options[Math.min(1, q.options.length - 1)].value;
      state.answers[q.id] = q.multi ? [q.options[0].value, second] : second;
    });
    syncSelections();
    goto('reveal');
  }
  if (e.key === 'h' || e.key === 'H') goto('hook', { reset: true });
  const order = ['hook', ...Q_IDS, 'reveal', 'lead'];
  if (e.key === 'ArrowRight') {
    const i = order.indexOf(state.current);
    if (i >= 0 && i < order.length - 1) goto(order[i + 1]);
  }
  if (e.key === 'ArrowLeft') {
    const i = order.indexOf(state.current);
    if (i > 0) goto(order[i - 1]);
  }
});

/* Refresh aggregate on load */
fetchAggregate();
