// Wilson Trailers — Inventory AI frontend
const API = '';

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

// ====================== App Root (splash + tour) ======================
function appRoot() {
  return {
    splash: true,
    splashPct: 0,
    splashStatus: 'INITIALIZING',
    tour: tourController(),
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
    async boot() {
      const seen = localStorage.getItem('wt_splash_seen');
      const total = seen ? 2400 : 4800;  // ms total splash duration
      const start = performance.now();

      const tick = () => {
        const elapsed = performance.now() - start;
        const pct = Math.min(100, Math.round((elapsed / total) * 100));
        this.splashPct = pct;
        const step = this._splashSteps.slice().reverse().find(s => pct >= s.at);
        if (step) this.splashStatus = step.label;
        if (pct < 100 && this.splash) {
          this._splashTimer = requestAnimationFrame(tick);
        } else {
          setTimeout(() => this.enterApp(false), 250);
        }
      };
      requestAnimationFrame(tick);
    },
    enterApp(byClick) {
      if (!this.splash) return;
      if (this._splashTimer) cancelAnimationFrame(this._splashTimer);
      // Fade-out class is applied via :class binding when splash flips false
      this.splash = false;
      const seen = localStorage.getItem('wt_splash_seen');
      if (!seen) {
        localStorage.setItem('wt_splash_seen', '1');
        // Wait for splash fade-out (.55s) + small buffer
        setTimeout(() => this.tour.start(), 700);
      }
    },
    resetTour() {
      localStorage.removeItem('wt_splash_seen');
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
    async init() {
      this.kpi = await api('/api/dashboard');
      this.lowStock = await api('/api/products?low_only=true');
      this.recentPurchases = await api('/api/purchases?limit=5');
      this.recentMovements = await api('/api/movements/recent?limit=8');
    },
    trendChartSVG() { return this.kpi ? buildTrendSVG(this.kpi.monthly_trend) : ''; },
    categoryChartSVG() { return this.kpi ? buildDonutSVG(this.kpi.top_categories) : ''; },
    fmtMoney, fmtInt, fmtDate, fmtDateTime,
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
    async init() {
      try {
        this.categories = await api('/api/meta/categories');
      } catch (e) { this.categories = []; }
      await this.load();
      try {
        this.movements = await api('/api/movements/recent?limit=8');
      } catch (e) { this.movements = []; }
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
      if (!confirm('Delete this SKU?')) return;
      await api(`/api/products/${id}`, { method:'DELETE' });
      await this.load();
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
          alert('Failed: ' + (err.detail || JSON.stringify(err)));
          return;
        }
        const data = await r.json();
        this.toast = `${data.operator} pulled ${this.withdrawForm.quantity} x ${data.sku} - ${this.withdrawForm.reason}. New stock: ${data.new_stock}`;
        setTimeout(() => this.toast = null, 5500);
        this.showWithdraw = false;
        await this.load();
        this.movements = await api('/api/movements/recent?limit=8');
      } catch (e) { alert(e.message); }
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
          alert('Production failed: ' + (typeof err.detail === 'string' ? err.detail : JSON.stringify(err.detail)));
          this.producing = false;
          return;
        }
        const wo = await r.json();
        this.toast = `${wo.wo_number} · ${wo.trailer_line} × ${wo.quantity} · material ${fmtMoney(wo.material_cost)}`;
        setTimeout(() => this.toast = null, 5000);
        // Refresh
        this.boms = await api('/api/bom');
        this.workOrders = await api('/api/work-orders?limit=20');
        await this.selectLine(this.selected);
      } catch (e) {
        alert('Error: ' + e.message);
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
    messages: [
      { role:'bot', text: 'Wilson Trailers AI is online.\n\nAsk anything about inventory, purchases, expenses, production capacity, or SKU runout forecasts in plain English.' }
    ],
    input: '',
    loading: false,
    suggestions: [
      'summary',
      'how many trailers can I build',
      'which SKUs run out first',
      'skus below minimum',
      'purchases this month',
      'expenses by category',
      'top SKUs by value',
    ],
    async send(q) {
      const question = (q || this.input || '').trim();
      if (!question || this.loading) return;
      this.messages.push({ role: 'user', text: question });
      this.input = '';
      this.loading = true;
      this.scroll();
      try {
        const res = await api('/api/ai/ask', { method:'POST', body: JSON.stringify({ question }) });
        this.messages.push({ role: 'bot', text: res.answer });
      } catch (e) {
        this.messages.push({ role: 'bot', text: 'Query failed: ' + e.message });
      } finally {
        this.loading = false;
        this.scroll();
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
