# Tech Stack — Bubble Tea Shop System

## Overview
This document explains my technology choices for the Bubble Tea Shop MVP and the
reasoning behind each. My guiding principle was to favour tools I already know, or
that are mature and well-documented.

## Summary

| Layer | Choice |
|---|---|
| Backend | Python + FastAPI |
| Database | PostgreSQL |
| Frontend | React |
| UI component library | Ant Design |
| Authentication | Username / password + JWT |

## Choices & Rationale

### Backend — Python + FastAPI
I already know Python, so there's no ramp-up cost. FastAPI is modern, mature, and
well-documented, with built-in request validation and auto-generated API docs,
making it a good fit for a small REST API.

### Database — PostgreSQL
The data model is highly relational — recipes, inventory, orders, and the
dashboards all rely on joins and aggregations, which suits a relational database.
PostgreSQL is mature and strong at the analytical queries the dashboards need； a
relational database is clearly the right fit here.

### Frontend — React
The app is genuinely interactive (cart, live inventory, dashboards), and React
keeps the UI in sync with changing data automatically instead of me writing manual
updates. 

### UI Component Library — Ant Design
The interface is dashboard- and table-heavy, and Ant Design provides polished,
ready-made table, form, and data-display components out of the box — satisfying the
single-component-library requirement with minimal design work. 

### Authentication — Username / password + JWT
This is required by the user stories. JWT is the standard, stateless approach for
authenticating a REST API and pairs naturally with the FastAPI backend.
