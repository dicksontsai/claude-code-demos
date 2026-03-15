# Marketplace — Project Context

## What This Is

A classifieds marketplace web app where users can browse, search, and post listings across categories (Electronics, Furniture, Vehicles, Clothing, Services). This is the demo project for the "Claude Code + Chrome" tutorial.

## Tech Stack

- **Server:** Node.js with Express
- **Frontend:** Vanilla HTML, CSS, and JavaScript (no frameworks)
- **Data:** In-memory array (no database)

## How to Run

```bash
npm install
npm start
```

The server runs at http://localhost:3000.

## API Endpoints

- `GET /api/listings` — Returns all listings
- `GET /api/listings/:id` — Returns a single listing by ID
- `POST /api/listings` — Creates a new listing (expects JSON with title, description, price, category)

## Project Structure

- `server.js` — Express server, API routes, and seed data
- `public/index.html` — Homepage with listing grid, search, category filters, and new-listing modal
- `public/listing.html` — Detail page for a single listing

## Guidelines

This is a tutorial project. Keep changes simple and focused. Avoid adding external dependencies unless absolutely necessary. All CSS is inline in the HTML files — no external stylesheets or CSS frameworks.
