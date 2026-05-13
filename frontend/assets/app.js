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

// Chart.js defaults — dark
if (typeof Chart !== 'undefined') {
  Chart.defaults.color = '#A1A1AA';
  Chart.defaults.borderColor = '#23232B';
  Chart.defaults.font.family = "'Inter', system-ui, sans-serif";
  Chart.defaults.font.size = 11;
}

function dashboardApp() {
  return {
    kpi: null,
    chart: null,
    catChart: null,
    lowStock: [],
    recentPurchases: [],
    recentMovements: [],
    async init() {
      this.kpi = await api('/api/dashboard');
      this.lowStock = await api('/api/products?low_only=true');
      this.recentPurchases = await api('/api/purchases?limit=5');
      this.recentMovements = await api('/api/movements/recent?limit=8');
      this.scheduleRender();
    },
    scheduleRender(tries = 0) {
      // Wait until <template x-if="kpi"> mounted the canvases AND they have dimensions
      const a = document.getElementById('trendChart');
      const b = document.getElementById('catChart');
      if (!a || !b || a.clientWidth === 0 || b.clientWidth === 0) {
        if (tries < 30) return setTimeout(() => this.scheduleRender(tries + 1), 80);
        return;
      }
      this.renderCharts();
    },
    renderCharts() {
      const ctx = document.getElementById('trendChart');
      if (ctx && this.kpi) {
        if (this.chart) this.chart.destroy();
        this.chart = new Chart(ctx, {
          type: 'line',
          data: {
            labels: this.kpi.monthly_trend.map(m => m.label.toLowerCase()),
            datasets: [
              { label: 'purchases', data: this.kpi.monthly_trend.map(m => m.purchases),
                borderColor: '#E30613', backgroundColor: 'rgba(227,6,19,0.10)', tension: .3, fill: true, borderWidth: 1.5, pointRadius: 2, pointBackgroundColor:'#E30613' },
              { label: 'expenses', data: this.kpi.monthly_trend.map(m => m.expenses),
                borderColor: '#A1A1AA', backgroundColor: 'rgba(161,161,170,0.05)', tension: .3, fill: true, borderWidth: 1.5, pointRadius: 2, pointBackgroundColor:'#A1A1AA' },
            ],
          },
          options: {
            responsive: true, maintainAspectRatio: false,
            plugins: {
              legend: { position:'bottom', labels:{boxWidth:8, boxHeight:8, font:{size:11, family:"'JetBrains Mono', monospace"}, color:'#A1A1AA'} },
              tooltip: { backgroundColor:'#131318', borderColor:'#2D2D38', borderWidth:1, titleColor:'#E4E4E7', bodyColor:'#A1A1AA', titleFont:{family:"'JetBrains Mono'", size:11}, bodyFont:{family:"'JetBrains Mono'", size:11}, padding:10, cornerRadius:0 }
            },
            scales: {
              y: { ticks: { callback: v => '$' + (v/1000).toFixed(0) + 'k', font:{family:"'JetBrains Mono', monospace", size:10} }, grid:{color:'#1A1A1F'}, border:{color:'#23232B'} },
              x: { grid: { display: false }, border:{color:'#23232B'}, ticks:{font:{family:"'JetBrains Mono', monospace", size:10}} }
            }
          }
        });
      }
      const cctx = document.getElementById('catChart');
      if (cctx && this.kpi && this.kpi.top_categories.length) {
        if (this.catChart) this.catChart.destroy();
        this.catChart = new Chart(cctx, {
          type: 'doughnut',
          data: {
            labels: this.kpi.top_categories.map(c => c.category),
            datasets: [{
              data: this.kpi.top_categories.map(c => c.value),
              backgroundColor: ['#E30613','#A1A1AA','#F59E0B','#22C55E','#60A5FA','#71717A','#52525B','#7A0309','#3F3F46','#27272A'],
              borderColor: '#0F0F12',
              borderWidth: 2,
            }]
          },
          options: {
            responsive: true, maintainAspectRatio: false, cutout: '65%',
            plugins: {
              legend: { position: 'bottom', labels:{boxWidth:8, boxHeight:8, font:{size:10}, color:'#A1A1AA', padding:8} },
              tooltip: { backgroundColor:'#131318', borderColor:'#2D2D38', borderWidth:1, titleColor:'#E4E4E7', bodyColor:'#A1A1AA', titleFont:{family:"'JetBrains Mono'", size:11}, bodyFont:{family:"'JetBrains Mono'", size:11}, padding:10, cornerRadius:0 }
            }
          }
        });
      }
    }
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

window.dashboardApp = dashboardApp;
window.inventoryApp = inventoryApp;
window.purchasesApp = purchasesApp;
window.expensesApp = expensesApp;
window.productionApp = productionApp;
window.historyApp = historyApp;
window.assistantApp = assistantApp;
