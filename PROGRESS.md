# Wilson Trailers — Premium UX Improvements Sprint
**Started:** 2026-05-13 12:11 AM
**Target:** 4:11 AM (4 hours of continuous work)
**Goal:** Transform demo from "works" to "feels expensive"

---

## Round 1 — Micro-interactions (12:11 → 1:11)
- [ ] Number count-up animations on Overview KPIs
- [ ] View transitions (fade + slide) between sidebar sections
- [ ] Button ripple click feedback
- [ ] Loading skeletons replace "Loading…" text
- [ ] Toast notification system (stack, dismiss, success/error variants)
- [ ] Hover lift on panels and KPI cards
- [ ] Custom branded scrollbar (thinner, red on hover)
- [ ] Smooth focus states with red ring
- [ ] Active state indicator slides between sidebar items

## Round 2 — UX Deepening (1:11 → 2:11)
- [ ] SKU detail modal with full movement history (`GET /api/products/{id}/history`)
- [ ] Sortable table columns (click header to sort asc/desc)
- [ ] Command palette (`Cmd+K` / `Ctrl+K`) for instant nav + search
- [ ] Custom confirm dialog replacing browser `confirm()`
- [ ] Empty states with subtle illustrations
- [ ] Inline editing for stock/min_stock fields
- [ ] Multi-select on inventory for bulk withdraw

## Round 3 — Premium Aesthetics (2:11 → 3:11)
- [ ] Three-level typography hierarchy refinement
- [ ] Subtle dot-grid background on panels
- [ ] Animated number counters everywhere stats appear
- [ ] Smooth chart re-render with stagger animation
- [ ] Sidebar active indicator slides between items
- [ ] Critical-item status pulse
- [ ] Custom checkboxes, selects, radio buttons
- [ ] Animated stat dividers on hover

## Round 4 — Advanced UX (3:11 → 4:11)
- [ ] Live polling: dashboard auto-refreshes every 30s with diff highlights
- [ ] Global keyboard shortcuts (G+I = Inventory, P = Production, etc.)
- [ ] Notifications panel with badge counter
- [ ] AI query autocomplete from common questions
- [ ] Saved filters per view
- [ ] Right-click context menus on rows
- [ ] Inline sparkline charts in KPIs (last 7 days mini-trend)

---

## Architecture pointers (so I don't get lost)

**Where things live:**
- Splash & tour: `frontend/index.html` lines 35-100, `app.js` `appRoot()` and `tourController()`
- Dashboard: `app.js` `dashboardApp()`, HTML around line 130
- Inventory: `app.js` `inventoryApp()`, HTML around line 220
- Production: `app.js` `productionApp()`, HTML around line 420
- AI: `app.js` `assistantApp()`, HTML around line 560
- All styles: `styles.css` (~620 lines, organized by component)

**API contract:**
- `/api/dashboard` returns: `{total_skus, total_units, inventory_value, low_stock_count, purchases_mtd, expenses_mtd, monthly_trend[6], top_categories[]}`
- `/api/products` returns: `[{id, sku, name, category, trailer_line, unit_cost, stock, min_stock, location, supplier, ...}]`
- `/api/movements/recent` returns: `[{id, date, sku, item_name, movement_type, quantity, reason}]`

**Deploy flow:**
1. `git add -A && git commit -m "..." && git push`
2. `vercel deploy --prod --yes`
3. Verify with `curl https://wilson-trailers-inventory.vercel.app/api/...`

**Cache buster:** bump `?v=YYYYMMDD<letter>` in `index.html` on every CSS/JS change.

---

## Commits log
