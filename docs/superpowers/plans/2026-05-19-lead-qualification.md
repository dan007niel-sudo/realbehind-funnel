# Lead Qualification Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Extend the RealBehind funnel with low-friction lead qualification fields and a 799 EUR budget anchor.

**Architecture:** Keep the existing FastAPI + static HTML/CSS/JS structure. Extend `LeadData` and frontend payload fields, then update Gemini prompt/email context so Pamela receives timing, emotional motivation, and budget-readiness guidance.

**Tech Stack:** FastAPI, Pydantic, vanilla HTML/CSS/JS, Python unittest.

---

### Task 1: Qualification Contract Tests

**Files:**
- Create: `test_lead_qualification_contract.py`

- [ ] Add unittest coverage that requires the HTML to include `datum`, `momente`, `investitionsrahmen`, and the approved budget options.
- [ ] Add API contract coverage that posts the extended lead payload to `/api/qualify` and expects success.
- [ ] Run `python3 -m unittest test_lead_qualification_contract.py -v`; expected initial failure before implementation.

### Task 2: Backend Lead Model and Briefing

**Files:**
- Modify: `main.py`

- [ ] Add `datum`, `momente`, and `investitionsrahmen` to `LeadData`.
- [ ] Include the new fields in `user_input` and email lead details.
- [ ] Update the Gemini system prompt to produce budget-readiness and call recommendation.

### Task 3: Frontend Form and Payload

**Files:**
- Modify: `static/index.html`
- Modify: `static/app.js`
- Modify: `static/style.css` if spacing needs polish.

- [ ] Add fields for date/timeframe, emotional moment motivation, and investment range.
- [ ] Use budget options: `Ich brauche erst ein Gefühl für die Pakete`, `ab 799 €`, `1.000-1.500 €`, `1.500 €+`.
- [ ] Submit the new fields to `/api/qualify`.
- [ ] Pass the relevant context into Calendly custom answers.

### Task 4: Verification

- [ ] Run unittest and Python compile checks.
- [ ] Start local uvicorn.
- [ ] Use browser validation: load page, click CTA, fill/select new fields enough to verify state, submit until loader/Calendly transition.
- [ ] Do not deploy until Daniel confirms push/deploy.
