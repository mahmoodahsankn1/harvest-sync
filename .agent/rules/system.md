---
trigger: always_on
---

# HARVEST SYNC: SYSTEM ARCHITECTURE & DESIGN RULES
## 1. MANDATORY MODULARITY RULE
- **Separation of Concerns**: The AI must never combine CSS, JS, and HTML into a single file.
- **Linking**: Every page must link to [global.css](cci:7://file:///c:/Users/mahmo/hackathon/Harvest%20sync/static/css/global.css:0:0-0:0) and its specific `module.css`.
- **Scripts**: Every script must be an ES6 module (`type="module"`).
- **Architecture**: Use MVC architecture (Django).
- **New Features**: If a request is made for a new feature, create a new specific file if it doesn't fit the existing architecture.
- **Navigation**: Every page within a module (Farmer, Consumer, Worker, Govt) must include its own specific navigation bar, styled according to the module's brand color.
## 2. STRICT COLOR THEME ENFORCEMENT
The following hex codes are immutable. Do not use "close" colors.
| Context | CSS Variable | Hex Code | Usage |
| :--- | :--- | :--- | :--- |
| **Global** | `--bg-glass` | `rgba(255, 255, 255, 0.25)` | Glass cards background |
| **Global** | `--border-glass` | `rgba(255, 255, 255, 0.3)` | All borders |
| **Farmer** | `--brand-farmer` | `#F59E0B` | Primary accent, buttons, icons |
| **Consumer** | `--brand-user` | `#0EA5E9` | Marketplace highlights |
| **Worker** | `--brand-worker` | `#475569` | Logistics/Map elements |
| **Govt** | `--brand-govt` | `#6366F1` | Admin dashboard accents |
| **Danger** | `--brand-alert` | `#EF4444` | Warnings / Error states |
### Dark Theme Extension
For **ALL Farmer Module Pages** (Dashboard, Add Product, My Orders, etc.), strictly adhere to these additional backgrounds while keeping the strict variables above:
- **Body Background**: `linear-gradient(135deg, #0f172a 0%, #1e293b 100%)` (Slate Dark)
- **Text Color**: White (`#FFFFFF`) or Light Gray (`rgba(255,255,255,0.8)`)
## 3. UI STYLE GUIDELINES (ANTIGRAVITY RULES)
- **Roundness**: All border-radius must be **24px** or higher.
- **Glassmorphism**: Every card MUST have `backdrop-filter: blur(12px)` and `background: var(--bg-glass)`.
- **Shadows**: Use only `box-shadow: 0 10px 25px rgba(0,0,0,0.1)`.
- **Tech Stack**: HTML, CSS, JS (Vanilla), Django. **No Frontend Frameworks** (React/Vue/Tailwind).
## 4. ROLE-BASED LOGIC & BILINGUAL SUPPORT
- **Role Detection**: JS files (`chatbot.js`, `ui.js`) must check `data-role` on `<body>` tag.
- **Farmer Persona**: AI acts as an **Agronomist**.
- **User Persona**: AI acts as a **Shopping Assistant**.
- **Bilingual Support**: Application must support **English** and **Malayalam**.
  - **Toggle**: Global language toggle must be present and functional on ALL pages.
  - **Persistence**: User language preference must be saved in `localStorage` and applied on page load.
  - **Implementation**: changing the language must update ALL text content dynamically.
  - **HTML Structure**: All translatable text MUST be wrapped in an element with a `data-i18n="KEY"` attribute.
  - **Missing Translations**: Fallback to English if a translation key is missing.
## 5. FILE HEADER TEMPLATE
Every new file generated must start with:
```css
/* CSS Module: [Name] - Part of Harvest Sync */
or

/* JS Module: [Name] - Handles [Function] */