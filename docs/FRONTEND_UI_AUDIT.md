# Company Brain — Frontend UI/UX Professional Audit & Refinement Plan

**Date:** 2026-10-15  
**Role:** Senior Frontend Engineer & UI/UX Design Systems Architect  
**Target:** Production-grade Polish, WCAG AA Compliance, Responsive Enterprise Aesthetics  

---

## 1. Executive Summary

An in-depth audit of the **Company Brain** frontend was conducted across HTML structure, CSS stylesheets, client-side ES6 JavaScript, responsive viewports, and visual references provided in project screenshots.

The application possesses a solid foundation: a warm ivory background (`#FFF9F5`), coral/orange accent palette (`#FA7B38`), pure white surface cards, and a multi-tab workflow (`Workspace & Chat`, `Documents`, `Graph Explorer`). However, several key architectural, visual, and interaction defects were identified that prevent it from looking like a top-tier enterprise platform.

---

## 2. Identified Frontend Defects & Pain Points

### A. Architectural & Code Quality Issues
1. **Duplicate & Conflicting Styles**: `index.html` contains an inline `<style>` block (over 400 lines) duplicating and conflicting with `frontend/style.css` (specifically headers, footers, workspace chips, and responsive breakpoints).
2. **Redundant Web Font Calls**: Google Fonts are loaded via both `<link>` tags in HTML and `@import` in `style.css`, causing redundant network roundtrips and font rendering layout shifts (FOUT).
3. **Scroll Position Desynchronization**: Switching tabs does not reset page scroll (`window.scrollTo(0, 0)`), causing tabs to open scrolled halfway down.

### B. Color System & Contrast Deficiencies (WCAG AA)
1. **Sub-optimal Text Contrast**: Muted metadata (`--text-dim: #9CA3AF`, contrast 2.8:1) and placeholder text fail WCAG AA 4.5:1 ratio on light surfaces (`#FFFFFF` and `#FFFDFB`).
2. **Inactive Tab Affordance**: Navigation tabs lack sufficient contrast and state distinction when inactive (`#6B7280` on light orange track).
3. **Status Indicators**: Health latency text and node/edge counters lack cohesive, high-contrast borders and readable typographic hierarchy.

### C. Typography & Visual Hierarchy
1. **Inconsistent Line Heights & Letter Spacing**: Long headings, suggested question pills, and message bubbles exhibit awkward wrapping on narrower viewports.
2. **Technical Metadata Styling**: Document IDs, SHA-256 hashes, and Cypher relationship paths require standardized monospace treatment (`JetBrains Mono`) with high legibility.

### D. Container Layouts & Viewport Sizing
1. **Rigid Viewport Heights**: `.workspace-grid` uses `height: calc(100vh - 160px); min-height: 640px;` causing double-scrollbars on standard 13" laptops (1366x768 and 1440x900) when combined with the 300px footer.
2. **Empty State Alignment**: The right sidebar ("Verified Evidence & Graph Context") empty state icon and typography feel unanchored when no query is active.
3. **Canvas HiDPI Blurriness**: The HTML5 canvas renders at fixed 960x400 without adjusting for retina/devicePixelRatio (`window.devicePixelRatio`), resulting in slightly blurry text on modern 4K/Retina displays.

### E. Interactive Elements & Accessibility
1. **Missing Focus Indicators**: Buttons, tabs, and query pills lack visible `:focus-visible` rings for keyboard navigation.
2. **Clickable Cards Accessibility**: `.citation-card` and `.conn-card` lack keyboard focus, `tabindex="0"`, and `Enter`/`Space` listeners.
3. **Form Feedback**: No real-time search/filter for the Documents table, making it difficult to find files in large repositories.

---

## 3. Implementation Plan

```
┌────────────────────────────────────────────────────────────────────────┐
│                        REFINEMENT ROADMAP                              │
├──────────────────────────┬─────────────────────────────────────────────┤
│ Step 1: Design Tokens    │ Centralize WCAG AA color variables, radii, │
│                          │ shadows, and typography scale in style.css. │
├──────────────────────────┼─────────────────────────────────────────────┤
│ Step 2: Clean index.html │ Remove 400 lines of conflicting inline CSS; │
│                          │ clean up semantic tags, ARIA labels, fonts. │
├──────────────────────────┼─────────────────────────────────────────────┤
│ Step 3: Header & Nav     │ Pixel-perfect brand logo, status pills, and │
│                          │ distinct active/inactive tab buttons.       │
├──────────────────────────┼─────────────────────────────────────────────┤
│ Step 4: Workspace & Chat │ Fluid chat container, suggested query pills │
│                          │ with hover lift, crisp message bubbles, and │
│                          │ sticky full-width input bar with send icon. │
├──────────────────────────┼─────────────────────────────────────────────┤
│ Step 5: Evidence Drawer  │ Polished citation cards, authentic passage  │
│                          │ quotation styling, and Cypher rel badges.   │
├──────────────────────────┼─────────────────────────────────────────────┤
│ Step 6: Documents Panel  │ Live search filter, interactive chunk modal,│
│                          │ refined dropzone with drag-and-drop feedback│
├──────────────────────────┼─────────────────────────────────────────────┤
│ Step 7: Graph Explorer   │ HiDPI sharp canvas rendering, hover pointer │
│                          │ cursor over nodes, 360° incoming/outgoing.  │
├──────────────────────────┼─────────────────────────────────────────────┤
│ Step 8: Responsive & QA  │ Breakpoints for Desktop, Laptop, Tablet,    │
│                          │ Mobile. Automated browser visual testing.   │
└──────────────────────────┴─────────────────────────────────────────────┘
```
