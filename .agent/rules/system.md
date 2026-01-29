---
trigger: always_on
---

HARVEST SYNC: SYSTEM ARCHITECTURE & DESIGN RULES1. MANDATORY MODULARITY RULEThe AI must never combine CSS, JS, and HTML into a single file.Every page must link to global.css and its specific module.css.Every script must be an ES6 module.Action: If a request is made for a new feature, create a new specific file if it doesn't fit the existing architecture.2. STRICT COLOR THEME ENFORCEMENTThe following hex codes are immutable. Do not use "close" colors or CSS named colors (like 'orange'). Use these exact variables:ModuleCSS VariableHex CodeUsageGlobal--bg-glassrgba(255, 255, 255, 0.15)Background of all cardsGlobal--border-glassrgba(255, 255, 255, 0.2)All card/button bordersFarmer--brand-farmer#F59E0BButtons, icons, and accentsConsumer--brand-user#0EA5E9Marketplace highlightsWorker--brand-worker#475569Logistics/Map elementsGovt--brand-govt#6366F1Admin dashboard accentsDanger--brand-alert#EF4444Disaster warnings / Error states3. UI STYLE GUIDELINES (ANTIGRAVITY RULES)Roundness: All border-radius must be 24px or higher.Glassmorphism: Every card MUST have backdrop-filter: blur(12px) and background: var(--bg-glass).Shadows: Use only box-shadow: 0 10px 25px rgba(0,0,0,0.1).No Frameworks: Use only Vanilla JS and pure CSS3 (Flex/Grid).4. ROLE-BASED LOGIC (JS)The chatbot.js and ui.js must check the data-role attribute of the <body> tag before executing logic.Farmer Role: AI persona must act as an Agronomist.User Role: AI persona must act as a Shopping Assistant.5. FILE HEADER TEMPLATEEvery new file generated must start with a comment identifying its role:/* CSS Module: [Name] - Part of Harvest Sync *//* JS Module: [Name] - Handles [Function] */

Use MVC architecture
tech stack html,css,js and django


the applicattion should be be billingual(english and malayalam)there will be a option in settings to adjust it
