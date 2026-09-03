---
name: Supra Enterprise System
colors:
  surface: '#f7f9fb'
  surface-dim: '#d8dadc'
  surface-bright: '#f7f9fb'
  surface-container-lowest: '#ffffff'
  surface-container-low: '#f2f4f6'
  surface-container: '#eceef0'
  surface-container-high: '#e6e8ea'
  surface-container-highest: '#e0e3e5'
  on-surface: '#191c1e'
  on-surface-variant: '#464555'
  inverse-surface: '#2d3133'
  inverse-on-surface: '#eff1f3'
  outline: '#777587'
  outline-variant: '#c7c4d8'
  surface-tint: '#4d44e3'
  primary: '#3525cd'
  on-primary: '#ffffff'
  primary-container: '#4f46e5'
  on-primary-container: '#dad7ff'
  inverse-primary: '#c3c0ff'
  secondary: '#565e74'
  on-secondary: '#ffffff'
  secondary-container: '#dae2fd'
  on-secondary-container: '#5c647a'
  tertiary: '#005338'
  on-tertiary: '#ffffff'
  tertiary-container: '#006e4b'
  on-tertiary-container: '#67f4b7'
  error: '#ba1a1a'
  on-error: '#ffffff'
  error-container: '#ffdad6'
  on-error-container: '#93000a'
  primary-fixed: '#e2dfff'
  primary-fixed-dim: '#c3c0ff'
  on-primary-fixed: '#0f0069'
  on-primary-fixed-variant: '#3323cc'
  secondary-fixed: '#dae2fd'
  secondary-fixed-dim: '#bec6e0'
  on-secondary-fixed: '#131b2e'
  on-secondary-fixed-variant: '#3f465c'
  tertiary-fixed: '#6ffbbe'
  tertiary-fixed-dim: '#4edea3'
  on-tertiary-fixed: '#002113'
  on-tertiary-fixed-variant: '#005236'
  background: '#f7f9fb'
  on-background: '#191c1e'
  surface-variant: '#e0e3e5'
typography:
  headline-lg:
    fontFamily: Plus Jakarta Sans
    fontSize: 30px
    fontWeight: '700'
    lineHeight: 38px
    letterSpacing: -0.02em
  headline-md:
    fontFamily: Plus Jakarta Sans
    fontSize: 24px
    fontWeight: '600'
    lineHeight: 32px
    letterSpacing: -0.01em
  headline-sm:
    fontFamily: Plus Jakarta Sans
    fontSize: 18px
    fontWeight: '600'
    lineHeight: 26px
  body-lg:
    fontFamily: Inter
    fontSize: 16px
    fontWeight: '400'
    lineHeight: 24px
  body-md:
    fontFamily: Inter
    fontSize: 14px
    fontWeight: '400'
    lineHeight: 20px
  body-sm:
    fontFamily: Inter
    fontSize: 12px
    fontWeight: '400'
    lineHeight: 16px
  code-md:
    fontFamily: JetBrains Mono
    fontSize: 13px
    fontWeight: '500'
    lineHeight: 18px
  label-caps:
    fontFamily: Inter
    fontSize: 11px
    fontWeight: '700'
    lineHeight: 16px
    letterSpacing: 0.05em
rounded:
  sm: 0.125rem
  DEFAULT: 0.25rem
  md: 0.375rem
  lg: 0.5rem
  xl: 0.75rem
  full: 9999px
spacing:
  base: 4px
  container-padding-mobile: 16px
  container-padding-desktop: 32px
  gutter: 16px
  stack-sm: 8px
  stack-md: 16px
  stack-lg: 24px
---

## Brand & Style
The design system is built for high-stakes supplier compliance, emphasizing precision, speed, and institutional trust. The aesthetic is **Corporate Modern with high-density utility**, prioritizing data clarity over decorative flourishes. 

The system utilizes a high-contrast foundation to ensure legibility during field audits and high-pressure procurement reviews. It employs a "data-first" philosophy where visual weight is strictly reserved for status indicators and critical action headers. The interface should feel like a sophisticated instrument—reliable, systematic, and structurally rigid.

## Colors
The palette is rooted in a clean Slate and Indigo foundation. 
- **Primary Indigo (#4F46E5)** is reserved for primary actions, active navigation states, and brand reinforcement.
- **Status Colors** (Red, Amber, Emerald) are used with intentionality: solid strokes for icons/text and soft tints for background fills to indicate compliance categories without overwhelming the user.
- **Surface Layering**: The background uses Slate 50 to allow white surface cards to pop, creating clear containment for data sets.

## Typography
This design system uses a tri-font strategy to maximize information hierarchy:
1. **Plus Jakarta Sans**: Used for page titles and section headers to provide a modern, professional terminal feel.
2. **Inter**: The workhorse for all body copy, form labels, and table data, chosen for its exceptional legibility at small sizes.
3. **JetBrains Mono**: Strictly reserved for technical values, including SKUs, chemical CAS numbers, and raw data strings. This monospaced font signals "raw data" to the user, distinguishing it from qualitative descriptions.

Mobile scaling: Headlines should drop by one tier (e.g., `headline-lg` becomes `headline-md`) on screens smaller than 768px.

## Layout & Spacing
The layout follows a **High-Density Fluid Grid**. 
- **Desktop**: 12-column grid with 24px margins. Content is organized in "Card Clusters" that group related compliance metrics.
- **Mobile**: A single-column flow with a persistent bottom tab bar for primary navigation (Dashboard, Audits, Suppliers, Alerts).
- **Rhythm**: Uses a 4px baseline. Components like data tables should utilize "Compact" vertical padding (8px) to maximize the number of visible rows on screen.

## Elevation & Depth
Depth is conveyed through **Low-Contrast Outlines** rather than heavy shadows to maintain a clean, professional "spreadsheet" efficiency.
- **Level 0 (Canvas)**: #F8FAFC.
- **Level 1 (Card/Surface)**: White background with a 1px #E2E8F0 solid border. No shadow.
- **Level 2 (Dropdowns/Modals)**: White background with a 1px #E2E8F0 border and a soft, neutral ambient shadow (Y: 4px, Blur: 12px, Opacity: 0.05) to distinguish overlapping layers.
- **Active State**: Elements being interacted with (like a selected tab) use a 2px Indigo border-bottom or a subtle background shift to #F1F5F9.

## Shapes
The design system uses **Soft (0.25rem)** rounding for standard components like buttons, input fields, and small cards. This retains a serious, structured appearance while feeling contemporary. 
- Large containers and modal windows may use `rounded-lg` (0.5rem) to differentiate them from the internal grid items.
- Status "pills" (tags) should use a fully rounded/pill shape to distinguish them from interactive buttons.

## Components
- **Buttons**: Primary buttons are solid Indigo with white text. Secondary buttons use a white fill with a Slate 200 border. Use 14px Inter Medium for button text.
- **Compliance Chips**: Use a pill shape with 10% opacity background of the status color and 100% opacity text. Example: "Compliant" is Emerald 500 text on Emerald 50 background.
- **Data Tables**: Zero-border on individual cells; use 1px horizontal dividers only. Header row should have a Slate 50 background with `label-caps` typography.
- **Input Fields**: 1px Slate 200 border. On focus, the border transitions to Indigo 600 with a 2px outer glow (Indigo 100).
- **Tabbed Navigation (Mobile)**: Fixed bottom bar with 24px icons and 10px labels. Active state indicated by Indigo 600 color and a 3px top-bar indicator on the tab icon.
- **Audit Cards**: White background, 1px border. Feature a vertical "Status Strip" on the far left edge (4px wide) colored by the compliance state (Red/Amber/Green).