# Wilson Trailer Co. — Inventory AI

Sistema de gestión de inventario con asistente AI, diseñado para una operación tipo Wilson Trailer Co. (fabricante de tráileres ganaderos, graneros y flatbeds, est. 1883 Sioux City IA).

## Problema que resuelve

Una planta de tráileres pierde dinero por:
- No saber el stock real de partes (sobre-compra o paros de línea)
- Falta de trazabilidad de movimientos
- Costos de pintura / aluminio extruido sin control
- Reposición tardía de SKUs críticos

Este sistema centraliza inventario, compras, gastos y movimientos en una sola interfaz con un asistente AI en lenguaje natural.

## Funcionalidades

- **Overview** · KPIs en vivo (valor inventario, compras MTD, gastos MTD, alertas de stock)
- **Inventory** · 80+ SKUs reales (aluminio, ejes Hendrickson, ABS Bendix, lonas Shur-Co, etc.)
- **Purchases** · órdenes multilínea con alta automática al stock
- **Expenses** · categorías operativas (nómina taller, energía, mantenimiento, etc.)
- **Activity Log** · stream cronológico de eventos
- **AI Assistant** · NLP en español sobre tus datos operativos

## Stack

- **Backend**: FastAPI + SQLAlchemy + SQLite
- **Frontend**: HTML + Alpine.js + Chart.js (sin build)
- **AI**: motor local determinístico + fallback opcional a Claude API
- **Hosting**: Vercel serverless

## Run local

```
run.bat
```

Abre **http://localhost:8000**

## Deploy

Push a `main` → Vercel hace deploy automático.

## AI con Claude (opcional)

Setear en Vercel Project Settings → Environment Variables:
```
ANTHROPIC_API_KEY = sk-ant-...
```
