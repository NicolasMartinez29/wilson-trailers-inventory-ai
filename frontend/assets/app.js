// Wilson Trailers — Inventory AI frontend
const API = '';

/** Access the body-level appRoot() data from anywhere. */
window.app = () => document.body._x_dataStack?.[0];

// ====================== Global utilities ======================

/** Count-up animation: animates element textContent from current to target. */
function countUp(el, to, opts = {}) {
  if (!el) return;
  const duration = opts.duration || 1100;
  const prefix = opts.prefix || '';
  const suffix = opts.suffix || '';
  const decimals = opts.decimals || 0;
  const from = opts.from !== undefined ? opts.from : 0;
  const start = performance.now();
  const ease = t => 1 - Math.pow(1 - t, 3); // easeOutCubic
  const tick = now => {
    const t = Math.min(1, (now - start) / duration);
    const v = from + (to - from) * ease(t);
    el.textContent = prefix + v.toLocaleString('en-US', {
      minimumFractionDigits: decimals,
      maximumFractionDigits: decimals,
    }) + suffix;
    if (t < 1) requestAnimationFrame(tick);
    else el.textContent = prefix + to.toLocaleString('en-US', {
      minimumFractionDigits: decimals,
      maximumFractionDigits: decimals,
    }) + suffix;
  };
  requestAnimationFrame(tick);
}

/** Ripple click effect — attach to any element. */
function addRipple(ev) {
  const el = ev.currentTarget;
  const rect = el.getBoundingClientRect();
  const size = Math.max(rect.width, rect.height);
  const ripple = document.createElement('span');
  ripple.className = 'ripple';
  ripple.style.width = ripple.style.height = size + 'px';
  ripple.style.left = (ev.clientX - rect.left - size/2) + 'px';
  ripple.style.top  = (ev.clientY - rect.top  - size/2) + 'px';
  el.appendChild(ripple);
  setTimeout(() => ripple.remove(), 600);
}

/** Auto-attach ripple to all .btn, sidebar a, .pill. */
document.addEventListener('click', (ev) => {
  const target = ev.target.closest('.btn, .sidebar a, .pill, .splash-continue');
  if (target) addRipple({ currentTarget: target, clientX: ev.clientX, clientY: ev.clientY });
}, true);

/** Global toast store via Alpine. */
document.addEventListener('alpine:init', () => {
  if (window.Alpine) {
    Alpine.store('toasts', {
      items: [],
      _id: 1,
      push(opts) {
        const id = this._id++;
        const toast = {
          id,
          type: opts.type || 'info',
          title: opts.title || '',
          msg: opts.msg || '',
          life: opts.life || 4000,
        };
        this.items.push(toast);
        setTimeout(() => this.dismiss(id), toast.life);
      },
      dismiss(id) {
        const idx = this.items.findIndex(t => t.id === id);
        if (idx === -1) return;
        // Mark leaving so CSS transition runs
        this.items[idx]._leaving = true;
        setTimeout(() => {
          const i = this.items.findIndex(t => t.id === id);
          if (i !== -1) this.items.splice(i, 1);
        }, 250);
      },
      success(title, msg) { this.push({type:'success', title, msg}); },
      error(title, msg)   { this.push({type:'error',   title, msg, life: 6000}); },
      info(title, msg)    { this.push({type:'info',    title, msg}); },
      warn(title, msg)    { this.push({type:'warn',    title, msg, life: 5000}); },
    });
  }
});

/** Helper to access toast store from anywhere. */
function toast(opts) {
  if (window.Alpine && Alpine.store('toasts')) Alpine.store('toasts').push(opts);
}
function toastSuccess(title, msg) { toast({ type:'success', title, msg }); }
function toastError(title, msg)   { toast({ type:'error',   title, msg, life: 6000 }); }
function toastInfo(title, msg)    { toast({ type:'info',    title, msg }); }
function toastWarn(title, msg)    { toast({ type:'warn',    title, msg, life: 5000 }); }

const fmtMoney = (n) => '$' + (Number(n)||0).toLocaleString('en-US', {minimumFractionDigits:2, maximumFractionDigits:2});
const fmtInt = (n) => (Number(n)||0).toLocaleString('en-US');
const fmtDate = (iso) => {
  if (!iso) return '';
  const d = new Date(iso);
  return d.toISOString().slice(0,10);
};
const fmtDateTime = (iso) => {
  if (!iso) return '';
  const d = new Date(iso);
  const pad = (x) => String(x).padStart(2,'0');
  return `${d.getFullYear()}-${pad(d.getMonth()+1)}-${pad(d.getDate())} ${pad(d.getHours())}:${pad(d.getMinutes())}`;
};

// Strip emojis from any string
const stripEmoji = (s) => (s || '').replace(/[\u{1F300}-\u{1FAFF}\u{2600}-\u{27BF}\u{1F000}-\u{1F02F}\u{2300}-\u{23FF}]/gu, '').trim();

const mdLite = (text) => {
  if (!text) return '';
  return stripEmoji(text)
    .replace(/&/g,'&amp;').replace(/</g,'&lt;').replace(/>/g,'&gt;')
    .replace(/\*\*(.+?)\*\*/g, '<strong>$1</strong>')
    .replace(/`([^`]+)`/g, '<code>$1</code>')
    .replace(/\n/g, '<br>');
};

async function api(path, opts={}) {
  const r = await fetch(API + path, {
    headers: {'Content-Type':'application/json'},
    ...opts,
  });
  if (!r.ok) throw new Error(`API ${path} → ${r.status}`);
  return r.json();
}

// ====================== App Root (splash + tour + cmd palette + confirm) ======================
function appRoot() {
  return {
    splash: true,
    splashPct: 0,
    splashStatus: 'INITIALIZING',
    tour: tourController(),
    skuDetail: skuDetailController(this),
    cmd: cmdPalette(this),
    confirmDialog: confirmController(),
    _splashTimer: null,
    _splashSteps: [
      { at: 0,    label: 'INITIALIZING SYSTEM' },
      { at: 12,   label: 'CONNECTING TO PLANT' },
      { at: 28,   label: 'LOADING SKU REGISTRY' },
      { at: 45,   label: 'SYNCING BILL OF MATERIALS' },
      { at: 62,   label: 'INDEXING STOCK MOVEMENTS' },
      { at: 78,   label: 'CALIBRATING AI MODULE' },
      { at: 92,   label: 'READY' },
    ],
    setView(v) {
      const appEl = document.querySelector('.app');
      if (appEl && appEl._x_dataStack) {
        appEl._x_dataStack[0].view = v;
      }
    },
    // Notifications panel state
    notifs: {
      open: false,
      items: [],
      unread: 0,
    },
    async loadNotifs() {
      try {
        const low = await api('/api/products?low_only=true');
        const items = low.map(p => ({
          kind: 'alert',
          title: `${p.sku} below minimum`,
          subtitle: `${p.name}`,
          value: `${p.stock}u / min ${p.min_stock}`,
          productId: p.id,
        }));
        // Most recent purchases
        const purchases = await api('/api/purchases?limit=3');
        for (const p of purchases) {
          items.push({
            kind: 'po',
            title: `${p.po_number}`,
            subtitle: `${p.vendor}`,
            value: fmtMoney(p.total),
            date: p.date,
          });
        }
        this.notifs.items = items;
        this.notifs.unread = low.length;
      } catch (e) {}
    },
    toggleNotifs() {
      this.notifs.open = !this.notifs.open;
      if (this.notifs.open) this.notifs.unread = 0;
    },
    async boot() {
      // Initial notifications load + poll every 45s
      this.loadNotifs();
      setInterval(() => this.loadNotifs(), 45000);
      // Lock body scroll while splash is up
      document.body.classList.add('splash-locked');

      // Global keyboard shortcuts
      window.addEventListener('keydown', (e) => {
        // Cmd+K / Ctrl+K -> command palette
        if ((e.metaKey || e.ctrlKey) && e.key.toLowerCase() === 'k') {
          e.preventDefault();
          if (!this.splash) this.cmd.toggle();
          return;
        }
        // Ignore if typing in an input
        if (['INPUT','TEXTAREA','SELECT'].includes(e.target.tagName)) return;
        if (this.splash || this.cmd.open) return;

        const key = e.key.toLowerCase();
        // Single-key shortcuts (no modifiers)
        if (!e.metaKey && !e.ctrlKey && !e.altKey) {
          const map = { 'o': 'dashboard', 'i': 'inventory', 'c': 'purchases',
                        'x': 'expenses', 'p': 'production', 'h': 'history', 'a': 'assistant' };
          if (map[key]) {
            e.preventDefault();
            this.setView(map[key]);
          }
        }
      });

      const total = 5200;
      const start = performance.now();

      const tick = () => {
        const elapsed = performance.now() - start;
        const pct = Math.min(100, Math.round((elapsed / total) * 100));
        this.splashPct = pct;
        const step = this._splashSteps.slice().reverse().find(s => pct >= s.at);
        if (step) this.splashStatus = step.label;
        if (pct < 100) {
          this._splashTimer = requestAnimationFrame(tick);
        }
        // When pct === 100 we STOP the loop. The user must click ENTER SYSTEM.
      };
      requestAnimationFrame(tick);
    },
    endSplash() {
      if (!this.splash) return;
      this.splash = false;
      // Unlock scroll once fade-out animation completes
      setTimeout(() => document.body.classList.remove('splash-locked'), 600);
      const seen = localStorage.getItem('wt_tour_seen');
      if (!seen) {
        localStorage.setItem('wt_tour_seen', '1');
        setTimeout(() => this.tour.start(), 800);
      }
    },
    resetTour() {
      localStorage.removeItem('wt_tour_seen');
      location.reload();
    },
  };
}

// ====================== Tour ======================
function tourController() {
  return {
    active: false,
    idx: 0,
    steps: [
      { target: '#tour-kpis', title: 'Real-time KPIs', body: 'Your plant at a glance: inventory value, MTD purchases, expenses, and active stock alerts. Numbers update automatically as movements happen.', placement: 'bottom' },
      { target: '#tour-charts', title: 'Cashflow & inventory mix', body: 'Six months of purchases vs expenses, plus how your $12M of inventory is distributed across categories.', placement: 'top' },
      { target: '#tour-nav-inv', title: 'Inventory', body: 'All 94 part SKUs with stock, cost, value, and location. Hit "withdraw" on any row to log who pulled what for which work order.', placement: 'right' },
      { target: '#tour-nav-prod', title: 'Production — the magic', body: 'Pick a trailer model and hit Produce. The system decrements all 30-48 BoM parts automatically and creates a work order with material cost.', placement: 'right' },
      { target: '#tour-nav-ai', title: 'AI Assistant', body: 'Ask in plain English: "how many trailers can I build?", "which SKUs run out first?", "expenses by category". Answers come from live data.', placement: 'right' },
    ],
    start() { this.idx = 0; this.active = true; this.highlight(); },
    advance() {
      this.unhighlight();
      this.idx++;
      if (this.idx >= this.steps.length) { this.active = false; return; }
      this.highlight();
    },
    skip() { this.unhighlight(); this.active = false; },
    highlight() {
      const el = document.querySelector(this.steps[this.idx].target);
      if (el) el.classList.add('tour-target');
    },
    unhighlight() {
      document.querySelectorAll('.tour-target').forEach(el => el.classList.remove('tour-target'));
    },
    cardStyle() {
      const step = this.steps[this.idx];
      const el = document.querySelector(step.target);
      if (!el) return 'top:40%;left:50%;transform:translate(-50%,-50%);';
      const r = el.getBoundingClientRect();
      const pad = 16, cardW = 360, cardH = 220;
      let top, left;
      if (step.placement === 'right') {
        top = Math.max(20, Math.min(window.innerHeight - cardH - 20, r.top + r.height/2 - cardH/2));
        left = Math.min(window.innerWidth - cardW - 20, r.right + pad);
      } else if (step.placement === 'top') {
        top = Math.max(20, r.top - cardH - pad);
        left = Math.max(20, Math.min(window.innerWidth - cardW - 20, r.left + r.width/2 - cardW/2));
      } else {
        top = Math.min(window.innerHeight - cardH - 20, r.bottom + pad);
        left = Math.max(20, Math.min(window.innerWidth - cardW - 20, r.left + r.width/2 - cardW/2));
      }
      return `top:${top}px;left:${left}px;`;
    },
  };
}

// ====================== Sparkline (mini SVG line) ======================
function sparkSVG(values, opts = {}) {
  if (!values || values.length < 2) return '';
  const W = 100, H = 22;
  const max = Math.max(...values, 1);
  const min = Math.min(...values, 0);
  const range = max - min || 1;
  const stepX = W / (values.length - 1);
  const points = values.map((v, i) => `${(i * stepX).toFixed(1)},${(H - ((v - min) / range) * H).toFixed(1)}`);
  const line = 'M ' + points.join(' L ');
  const area = `M 0,${H} L ` + points.join(' L ') + ` L ${W},${H} Z`;
  const color = opts.color || '#E30613';
  const fillColor = opts.fillColor || 'rgba(227,6,19,.12)';
  const lastPt = points[points.length-1].split(',');
  return `<svg class="sparkline" viewBox="0 0 ${W} ${H}" preserveAspectRatio="none">
    <path d="${area}" fill="${fillColor}" stroke="none"/>
    <path d="${line}" fill="none" stroke="${color}" stroke-width="1.3"/>
    <circle cx="${lastPt[0]}" cy="${lastPt[1]}" r="1.8" fill="${color}"/>
  </svg>`;
}

// ====================== SKU Detail Modal ======================
function skuDetailController() {
  return {
    open: false,
    data: null,
    async show(productId) {
      this.open = true;
      this.data = null;
      try {
        this.data = await api(`/api/products/${productId}/history`);
      } catch (e) {
        toastError('Failed to load SKU details', e.message);
        this.open = false;
      }
    },
    close() { this.open = false; this.data = null; },
    daysLeftText() {
      const d = this.data?.stats?.days_left;
      if (d === null || d === undefined) return '—';
      if (d > 999) return '∞';
      return Math.round(d) + 'd';
    },
    daysSubText() {
      const d = this.data?.stats?.days_left;
      if (!d) return 'no consumption';
      if (d < 14) return 'CRITICAL';
      if (d < 30) return 'reorder soon';
      return 'healthy';
    },
    daysFlagClass() {
      const d = this.data?.stats?.days_left;
      if (!d) return '';
      if (d < 14) return 'danger';
      if (d < 30) return 'warn';
      return 'good';
    },
  };
}

// ====================== Command Palette ======================
function cmdPalette(rootRef) {
  return {
    open: false,
    query: '',
    idx: 0,
    results: [],
    _allProducts: [],
    _staticCommands: [
      { kind:'nav', badge:'NAV', label:'Overview', view:'dashboard', sub:'press O' },
      { kind:'nav', badge:'NAV', label:'Inventory', view:'inventory', sub:'press I' },
      { kind:'nav', badge:'NAV', label:'Purchases', view:'purchases', sub:'press C' },
      { kind:'nav', badge:'NAV', label:'Expenses', view:'expenses', sub:'press X' },
      { kind:'nav', badge:'NAV', label:'Production', view:'production', sub:'press P' },
      { kind:'nav', badge:'NAV', label:'Activity Log', view:'history', sub:'press H' },
      { kind:'nav', badge:'NAV', label:'AI Assistant', view:'assistant', sub:'press A' },
      { kind:'ai',  badge:'AI',  label:'Ask: how many trailers can I build?', query:'how many trailers can I build' },
      { kind:'ai',  badge:'AI',  label:'Ask: which SKUs run out first?', query:'which SKUs run out first' },
      { kind:'ai',  badge:'AI',  label:'Ask: summary of operations', query:'summary' },
      { kind:'ai',  badge:'AI',  label:'Ask: expenses by category', query:'expenses by category' },
    ],
    async toggle() {
      this.open = !this.open;
      if (this.open) {
        this.query = ''; this.idx = 0;
        if (!this._allProducts.length) {
          try { this._allProducts = await api('/api/products'); } catch (e) {}
        }
        this.filter();
        this.$nextTick(() => { try { document.querySelector('.cmd-input')?.focus(); } catch(e){} });
      }
    },
    close() { this.open = false; this.idx = 0; },
    filter() {
      const q = this.query.toLowerCase().trim();
      let res = [];
      if (!q) {
        res = this._staticCommands.slice();
      } else {
        res = this._staticCommands.filter(c => c.label.toLowerCase().includes(q));
        const skus = this._allProducts.filter(p =>
          p.sku.toLowerCase().includes(q) || p.name.toLowerCase().includes(q)
        ).slice(0, 10);
        for (const p of skus) {
          res.push({ kind:'sku', badge:'SKU', label: p.sku + ' · ' + p.name, sub: `stock ${p.stock} · $${p.unit_cost}`, productId: p.id });
        }
      }
      this.results = res;
      this.idx = 0;
    },
    move(delta) {
      if (!this.results.length) return;
      this.idx = (this.idx + delta + this.results.length) % this.results.length;
      this.$nextTick(() => {
        const el = document.querySelectorAll('.cmd-result')[this.idx];
        el?.scrollIntoView({ block: 'nearest' });
      });
    },
    execute() {
      const r = this.results[this.idx];
      if (!r) return;
      this.close();
      if (r.kind === 'nav') {
        rootRef.setView ? rootRef.setView(r.view) : (document.querySelector('.app')._x_dataStack[0].view = r.view);
      } else if (r.kind === 'sku') {
        rootRef.skuDetail.show(r.productId);
      } else if (r.kind === 'ai') {
        const root = document.querySelector('.app')._x_dataStack[0];
        if (root) root.view = 'assistant';
        setTimeout(() => {
          const section = document.querySelector('[x-data^="assistantApp"]');
          if (section && section._x_dataStack) {
            section._x_dataStack[0].input = r.query;
            section._x_dataStack[0].send();
          }
        }, 200);
      }
    },
  };
}

// ====================== Custom Confirm Dialog ======================
function confirmController() {
  return {
    open: false,
    title: '',
    message: '',
    confirmLabel: 'Confirm',
    cancelLabel: 'Cancel',
    _resolve: null,
    ask(opts) {
      this.title = opts.title || 'Confirm';
      this.message = opts.message || 'Are you sure?';
      this.confirmLabel = opts.confirmLabel || 'Confirm';
      this.cancelLabel = opts.cancelLabel || 'Cancel';
      this.open = true;
      return new Promise(res => { this._resolve = res; });
    },
    confirm() {
      this.open = false;
      if (this._resolve) this._resolve(true);
      this._resolve = null;
    },
    cancel() {
      this.open = false;
      if (this._resolve) this._resolve(false);
      this._resolve = null;
    },
  };
}

// Global helper
function askConfirm(opts) {
  const body = document.body._x_dataStack?.[0];
  if (!body || !body.confirmDialog) return Promise.resolve(window.confirm(opts.message));
  return body.confirmDialog.ask(opts);
}

// ====================== SVG Chart Renderers ======================
function buildTrendSVG(trend) {
  if (!trend || !trend.length) return '<div class="empty">No data</div>';
  const W = 720, H = 220, padL = 56, padR = 16, padT = 16, padB = 30;
  const innerW = W - padL - padR, innerH = H - padT - padB;
  const maxV = Math.max(...trend.flatMap(m => [m.purchases, m.expenses]), 1);

  const xAt = (i) => padL + (i / (trend.length - 1 || 1)) * innerW;
  const yAt = (v) => padT + innerH - (v / maxV) * innerH;

  const buildPath = (key, kind) => {
    const pts = trend.map((m, i) => `${xAt(i)},${yAt(m[key])}`);
    const line = 'M ' + pts.join(' L ');
    const area = `M ${xAt(0)},${padT + innerH} L ` + pts.join(' L ') + ` L ${xAt(trend.length-1)},${padT + innerH} Z`;
    return `<path class="area-${kind}" d="${area}" />
            <path class="line-${kind}" d="${line}" />`;
  };

  const points = (key, kind) => trend.map((m, i) =>
    `<circle class="pt-${kind}" cx="${xAt(i)}" cy="${yAt(m[key])}" r="4"><title>${m.label}: $${m[key].toLocaleString()}</title></circle>`
  ).join('');

  // Y axis ticks (5 ticks)
  let yTicks = '';
  for (let i = 0; i <= 4; i++) {
    const v = (maxV * i / 4);
    const y = yAt(v);
    yTicks += `<line x1="${padL}" y1="${y}" x2="${W-padR}" y2="${y}" stroke="#1A1A1F" stroke-width="1"/>
               <text class="axis-num" x="${padL - 8}" y="${y + 3}">$${(v/1000).toFixed(0)}k</text>`;
  }

  // X axis labels
  const xLabels = trend.map((m, i) =>
    `<text class="axis-label" x="${xAt(i)}" y="${H - padB + 18}" text-anchor="middle">${m.label.toLowerCase()}</text>`
  ).join('');

  return `<svg class="chart-svg" viewBox="0 0 ${W} ${H}" preserveAspectRatio="xMidYMid meet">
    <g class="grid">${yTicks}</g>
    ${buildPath('expenses','expenses')}
    ${buildPath('purchases','purchases')}
    ${points('expenses','expenses')}
    ${points('purchases','purchases')}
    ${xLabels}
  </svg>`;
}

function buildDonutSVG(categories) {
  if (!categories || !categories.length) return '<div class="empty">No data</div>';
  const top = categories.slice(0, 8);
  const total = top.reduce((s, c) => s + c.value, 0);
  const palette = ['#E30613','#F59E0B','#22C55E','#60A5FA','#A78BFA','#F472B6','#FB923C','#94A3B8'];
  const r = 70, c = 100, circ = 2 * Math.PI * r;
  let offset = 0;
  const segs = top.map((cat, i) => {
    const portion = total > 0 ? cat.value / total : 0;
    const dash = portion * circ;
    const el = `<circle cx="${c}" cy="${c}" r="${r}"
                  stroke="${palette[i]}"
                  stroke-dasharray="${dash} ${circ}"
                  stroke-dashoffset="${-offset}"
                  transform="rotate(-90 ${c} ${c})">
                <title>${cat.category}: $${cat.value.toLocaleString()}</title>
              </circle>`;
    offset += dash;
    return el;
  }).join('');

  const legend = top.map((cat, i) =>
    `<div class="it">
      <span class="sw" style="background:${palette[i]};"></span>
      <span class="lbl">${cat.category}</span>
      <span class="val">$${(cat.value/1000).toFixed(0)}k</span>
    </div>`
  ).join('');

  return `<div class="donut-wrap">
    <svg class="donut-svg" viewBox="0 0 200 200">
      <circle cx="${c}" cy="${c}" r="${r}" stroke="#18181E" stroke-width="18" fill="none"/>
      ${segs}
      <text x="${c}" y="${c-4}" text-anchor="middle" font-family="JetBrains Mono, monospace" font-size="9" fill="#71717A" letter-spacing=".15em">TOTAL VALUE</text>
      <text x="${c}" y="${c+14}" text-anchor="middle" font-family="JetBrains Mono, monospace" font-size="14" fill="#E4E4E7" font-weight="600">$${(total/1000000).toFixed(2)}M</text>
    </svg>
    <div class="donut-legend">${legend}</div>
  </div>`;
}

function dashboardApp() {
  return {
    kpi: null,
    lowStock: [],
    recentPurchases: [],
    recentMovements: [],
    _poll: null,
    _lastMovementId: 0,
    pollMs: 30000,
    async init() {
      await this.refresh(true);
      this._poll = setInterval(() => this.refresh(false), this.pollMs);
    },
    destroy() { if (this._poll) clearInterval(this._poll); },
    async refresh(initial) {
      try {
        const [kpi, lowStock, recentPurchases, recentMovements] = await Promise.all([
          api('/api/dashboard'),
          api('/api/products?low_only=true'),
          api('/api/purchases?limit=5'),
          api('/api/movements/recent?limit=8'),
        ]);
        // Diff detection on subsequent refreshes
        if (!initial && recentMovements.length && this._lastMovementId) {
          const newest = recentMovements[0];
          if (newest.id > this._lastMovementId) {
            toastInfo('New movement detected', `${newest.sku} · ${newest.movement_type} · ${newest.quantity}u`);
          }
        }
        if (recentMovements.length) this._lastMovementId = Math.max(this._lastMovementId, recentMovements[0].id);
        this.kpi = kpi;
        this.lowStock = lowStock;
        this.recentPurchases = recentPurchases;
        this.recentMovements = recentMovements;
      } catch (e) {
        if (initial) toastError('Failed to load dashboard', e.message);
      }
    },
    trendChartSVG() { return this.kpi ? buildTrendSVG(this.kpi.monthly_trend) : ''; },
    categoryChartSVG() { return this.kpi ? buildDonutSVG(this.kpi.top_categories) : ''; },
    sparkSVG, fmtMoney, fmtInt, fmtDate, fmtDateTime,
  };
}

function inventoryApp() {
  const blank = () => ({ sku:'', name:'', category:'', trailer_line:'', unit_cost:0, stock:0, min_stock:5, location:'', supplier:'' });
  return {
    items: [],
    movements: [],
    q: '',
    category: '',
    categories: [],
    lowOnly: false,
    showModal: false,
    showWithdraw: false,
    editing: null,
    form: blank(),
    withdrawTarget: null,
    withdrawForm: { quantity: 1, operator: '', reason: '', notes: '' },
    operatorPresets: ['Tom Henderson','Mike Schultz','Carlos Reyes','Dave Anderson','Sarah Klein','Jeremy Cole'],
    toast: null,
    sortKey: '',
    sortDir: 1,
    async init() {
      try {
        this.categories = await api('/api/meta/categories');
      } catch (e) { this.categories = []; }
      await this.load();
      try {
        this.movements = await api('/api/movements/recent?limit=8');
      } catch (e) { this.movements = []; }
    },
    sortBy(key) {
      if (this.sortKey === key) this.sortDir *= -1;
      else { this.sortKey = key; this.sortDir = 1; }
      const dir = this.sortDir;
      this.items.sort((a, b) => {
        let va = a[key], vb = b[key];
        if (key === 'value') { va = a.stock * a.unit_cost; vb = b.stock * b.unit_cost; }
        if (va == null) va = '';
        if (vb == null) vb = '';
        if (typeof va === 'number' && typeof vb === 'number') return (va - vb) * dir;
        return String(va).localeCompare(String(vb)) * dir;
      });
    },
    sortIcon(key) {
      if (this.sortKey !== key) return '↕';
      return this.sortDir > 0 ? '↑' : '↓';
    },
    sortClass(key) {
      if (this.sortKey !== key) return '';
      return this.sortDir > 0 ? 'sort-asc' : 'sort-desc';
    },
    emptyForm() { return blank(); },
    async load() {
      const params = new URLSearchParams();
      if (this.q) params.set('q', this.q);
      if (this.category) params.set('category', this.category);
      if (this.lowOnly) params.set('low_only', 'true');
      this.items = await api('/api/products?' + params.toString());
    },
    open(item) {
      if (item) { this.editing = item.id; this.form = { ...item }; }
      else { this.editing = null; this.form = blank(); }
      this.showModal = true;
    },
    async save() {
      try {
        if (this.editing) await api(`/api/products/${this.editing}`, { method:'PUT', body: JSON.stringify(this.form) });
        else await api('/api/products', { method:'POST', body: JSON.stringify(this.form) });
        this.showModal = false;
        await this.load();
      } catch (e) { alert(e.message); }
    },
    async remove(id) {
      const ok = await askConfirm({
        title: 'Delete SKU',
        message: 'This will permanently remove the SKU from the registry. This action cannot be undone.',
        confirmLabel: 'Delete', cancelLabel: 'Cancel',
      });
      if (!ok) return;
      await api(`/api/products/${id}`, { method:'DELETE' });
      toastSuccess('SKU deleted', 'Removed from registry');
      await this.load();
    },
    showDetail(id) {
      const root = document.body._x_dataStack?.[0];
      if (root && root.skuDetail) root.skuDetail.show(id);
    },
    openWithdraw(p) {
      this.withdrawTarget = p;
      this.withdrawForm = { quantity: 1, operator: this.operatorPresets[0], reason: '', notes: '' };
      this.showWithdraw = true;
    },
    async doWithdraw() {
      if (!this.withdrawTarget) return;
      try {
        const r = await fetch(`/api/products/${this.withdrawTarget.id}/withdraw`, {
          method: 'POST',
          headers: {'Content-Type':'application/json'},
          body: JSON.stringify({
            product_id: this.withdrawTarget.id,
            quantity: Number(this.withdrawForm.quantity),
            operator: this.withdrawForm.operator,
            reason: this.withdrawForm.reason || 'manual',
            notes: this.withdrawForm.notes,
          }),
        });
        if (!r.ok) {
          const err = await r.json();
          toastError('Withdraw failed', err.detail || 'Could not decrement stock');
          return;
        }
        const data = await r.json();
        toastSuccess(
          `${data.sku} - ${this.withdrawForm.quantity} units withdrawn`,
          `${data.operator} · ${this.withdrawForm.reason} · new stock: ${data.new_stock}`
        );
        this.showWithdraw = false;
        await this.load();
        this.movements = await api('/api/movements/recent?limit=8');
      } catch (e) { toastError('Network error', e.message); }
    },
    isLow(p) { return p.stock <= p.min_stock; },
    value(p) { return p.stock * p.unit_cost; },
    fmtMoney, fmtInt, fmtDateTime,
  };
}

function purchasesApp() {
  return {
    items: [],
    products: [],
    vendors: [],
    showModal: false,
    form: { po_number:'', vendor:'', notes:'', items: [] },
    async init() {
      this.items = await api('/api/purchases');
      this.products = await api('/api/products');
      this.vendors = await api('/api/meta/vendors');
    },
    nextPO() {
      const next = Math.floor(1000 + Math.random()*9000);
      this.form.po_number = `PO-2026-${next}`;
    },
    open() {
      this.form = { po_number:'', vendor:'', notes:'', items: [{ product_id: this.products[0]?.id, quantity:1, unit_cost: this.products[0]?.unit_cost || 0 }] };
      this.nextPO();
      this.showModal = true;
    },
    addLine() {
      this.form.items.push({ product_id: this.products[0]?.id, quantity:1, unit_cost: this.products[0]?.unit_cost || 0 });
    },
    rmLine(i) { this.form.items.splice(i, 1); },
    onProdChange(line) {
      const p = this.products.find(x => x.id == line.product_id);
      if (p) line.unit_cost = p.unit_cost;
    },
    total() {
      return this.form.items.reduce((s, it) => s + (Number(it.quantity)||0) * (Number(it.unit_cost)||0), 0);
    },
    async save() {
      try {
        const payload = { ...this.form, items: this.form.items.map(it => ({...it, product_id: Number(it.product_id), quantity: Number(it.quantity), unit_cost: Number(it.unit_cost)})) };
        await api('/api/purchases', { method:'POST', body: JSON.stringify(payload) });
        this.showModal = false;
        this.items = await api('/api/purchases');
      } catch (e) { alert(e.message); }
    },
    fmtMoney, fmtDate, fmtDateTime,
  };
}

function expensesApp() {
  return {
    items: [],
    categories: [],
    filter: '',
    showModal: false,
    form: { category:'', description:'', amount:0, paid_to:'', notes:'' },
    presetCats: ['Nómina taller','Energía eléctrica','Mantenimiento maquinaria','Combustible','Transporte','Suministros oficina','Internet y telefonía','Seguros','Capacitación','Marketing','Otros'],
    async init() {
      await this.load();
      this.categories = await api('/api/meta/expense_categories');
    },
    async load() {
      const params = new URLSearchParams();
      if (this.filter) params.set('category', this.filter);
      this.items = await api('/api/expenses?' + params.toString());
    },
    open() {
      this.form = { category: this.presetCats[0], description:'', amount:0, paid_to:'', notes:'' };
      this.showModal = true;
    },
    async save() {
      try {
        await api('/api/expenses', { method:'POST', body: JSON.stringify({...this.form, amount: Number(this.form.amount)}) });
        this.showModal = false;
        await this.load();
      } catch (e) { alert(e.message); }
    },
    monthTotal() {
      const now = new Date();
      return this.items.filter(e => {
        const d = new Date(e.date);
        return d.getFullYear() === now.getFullYear() && d.getMonth() === now.getMonth();
      }).reduce((s, e) => s + e.amount, 0);
    },
    todayTotal() {
      const today = new Date().toDateString();
      return this.items.filter(e => new Date(e.date).toDateString() === today)
        .reduce((s, e) => s + e.amount, 0);
    },
    fmtMoney, fmtDate, fmtDateTime,
  };
}

function productionApp() {
  return {
    boms: [],
    bom: null,
    selected: null,
    workOrders: [],
    produceQty: 1,
    producing: false,
    toast: null,
    async init() {
      this.boms = await api('/api/bom');
      this.workOrders = await api('/api/work-orders?limit=20');
      if (this.boms.length) await this.selectLine(this.boms[0].trailer_line);
    },
    async selectLine(line) {
      this.selected = line;
      this.bom = await api(`/api/bom/${encodeURIComponent(line)}`);
    },
    async produce() {
      if (!this.bom || this.producing) return;
      this.producing = true;
      try {
        const r = await fetch('/api/produce', {
          method: 'POST',
          headers: {'Content-Type':'application/json'},
          body: JSON.stringify({ trailer_line: this.selected, quantity: this.produceQty }),
        });
        if (!r.ok) {
          const err = await r.json();
          const msg = typeof err.detail === 'string' ? err.detail : (err.detail?.error || 'Production failed');
          toastError('Production failed', msg);
          this.producing = false;
          return;
        }
        const wo = await r.json();
        toastSuccess(
          `${wo.wo_number} registered`,
          `${wo.trailer_line} × ${wo.quantity} · material ${fmtMoney(wo.material_cost)}`
        );
        // Refresh
        this.boms = await api('/api/bom');
        this.workOrders = await api('/api/work-orders?limit=20');
        await this.selectLine(this.selected);
      } catch (e) {
        toastError('Network error', e.message);
      } finally {
        this.producing = false;
      }
    },
    fmtMoney, fmtDateTime,
  };
}

function historyApp() {
  return {
    events: [],
    filter: 'all',
    async init() { this.events = await api('/api/history?limit=200'); },
    get visible() {
      if (this.filter === 'all') return this.events;
      return this.events.filter(e => e.type === this.filter);
    },
    typeLabel(t) {
      return { movement: 'STK', purchase: 'PO', expense: 'EXP' }[t] || t.toUpperCase();
    },
    cleanTitle(t) { return stripEmoji(t).replace(/^[·•]\s*/,''); },
    fmtDateTime,
  };
}

function assistantApp() {
  return {
    messages: JSON.parse(localStorage.getItem('wt_chat') || 'null') || [
      { role:'bot', text: 'Wilson Trailers AI is online.\n\nAsk anything about inventory, purchases, expenses, production capacity, or SKU runout forecasts in plain English.' }
    ],
    input: '',
    loading: false,
    showSuggestions: false,
    suggestions: [
      'summary',
      'how many trailers can I build',
      'which SKUs run out first',
      'skus below minimum',
      'purchases this month',
      'expenses by category',
      'top SKUs by value',
    ],
    filteredSuggestions() {
      const q = this.input.toLowerCase().trim();
      if (!q) return this.suggestions;
      return this.suggestions.filter(s => s.toLowerCase().includes(q));
    },
    clearHistory() {
      this.messages = [{ role:'bot', text: 'Conversation cleared. How can I help?' }];
      localStorage.removeItem('wt_chat');
    },
    _save() {
      try { localStorage.setItem('wt_chat', JSON.stringify(this.messages.slice(-30))); } catch(e){}
    },
    async send(q) {
      const question = (q || this.input || '').trim();
      if (!question || this.loading) return;
      this.messages.push({ role: 'user', text: question });
      this.input = '';
      this.showSuggestions = false;
      this.loading = true;
      this.scroll();
      this._save();
      try {
        const res = await api('/api/ai/ask', { method:'POST', body: JSON.stringify({ question }) });
        this.messages.push({ role: 'bot', text: res.answer });
      } catch (e) {
        this.messages.push({ role: 'bot', text: 'Query failed: ' + e.message });
      } finally {
        this.loading = false;
        this.scroll();
        this._save();
      }
    },
    scroll() {
      this.$nextTick(() => {
        const el = document.querySelector('.chat-msgs');
        if (el) el.scrollTop = el.scrollHeight;
      });
    },
    mdLite,
  };
}

window.appRoot = appRoot;
window.tourController = tourController;
window.dashboardApp = dashboardApp;
window.inventoryApp = inventoryApp;
window.purchasesApp = purchasesApp;
window.expensesApp = expensesApp;
window.productionApp = productionApp;
window.historyApp = historyApp;
window.assistantApp = assistantApp;
