# Marketplace — Claude Code + Chrome Tutorial Demo

A classifieds marketplace web app built as the starter project for the **Claude Code + Chrome** YouTube tutorial. Follow along to build, iterate, and test this app using Claude Code with Chrome as your browser.

## What You'll Build

A local classifieds marketplace where users can browse and post listings across categories like Electronics, Furniture, Vehicles, and more. The app features a clean, modern UI with category filtering, search, and a detail view for each listing.

## Prerequisites

- **Node.js** (v18 or later recommended)
- A modern web browser (Chrome recommended for this tutorial)

## Getting Started

1. Install dependencies:

   ```bash
   npm install
   ```

2. Start the server:

   ```bash
   npm start
   ```

3. Open [http://localhost:3000](http://localhost:3000) in Chrome.

## Project Structure

```
chrome-extension/
├── server.js              # Express server with REST API
├── package.json
├── CLAUDE.md              # Project context for Claude Code
├── public/
│   ├── index.html         # Marketplace homepage
│   └── listing.html       # Individual listing detail page
└── README.md
```

## API Endpoints

| Method | Endpoint             | Description              |
|--------|----------------------|--------------------------|
| GET    | `/api/listings`      | Get all listings         |
| POST   | `/api/listings`      | Create a new listing     |
| GET    | `/api/listings/:id`  | Get a single listing     |

## Tutorial

This project is the starting point for the Claude Code + Chrome tutorial. The tutorial walks through using Claude Code to iteratively enhance this app — adding features, fixing bugs, and refining the UI — all while testing in Chrome.
