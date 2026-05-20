/* ═══════════════════════════════════════════════════
   RealBehind — Funnel Logic v2
   Step transitions, form handling, Calendly pre-fill.
   ═══════════════════════════════════════════════════ */

const CALENDLY_URL = 'https://calendly.com/dan007niel/30min';
const sessionId = (window.crypto && window.crypto.randomUUID)
    ? window.crypto.randomUUID()
    : `${Date.now()}-${Math.random()}`;
let currentLeadId = null;
let formStarted = false;

function trackEvent(event, metadata = {}) {
    fetch('/api/events', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
            event,
            session_id: sessionId,
            lead_id: currentLeadId,
            metadata
        }),
        keepalive: true
    }).catch((err) => {
        console.warn('Tracking event failed:', err);
    });
}

// ── Step Navigation ───────────────────────────────
function nextStep(stepNumber) {
    const steps = document.querySelectorAll('.step');
    steps.forEach(s => s.classList.remove('active'));
    document.getElementById(`step-${stepNumber}`).classList.add('active');
    window.scrollTo({ top: 0, behavior: 'smooth' });
}

function startFunnel() {
    trackEvent('cta_clicked', { step: 1, label: 'Jetzt Kennenlernen anfragen' });
    nextStep(2);
}

// ── Lead Form Handling ────────────────────────────
const leadForm = document.getElementById('lead-form');

if (leadForm) {
    leadForm.addEventListener('input', () => {
        if (!formStarted) {
            formStarted = true;
            trackEvent('form_started', { step: 2 });
        }
    });

    leadForm.addEventListener('submit', async (e) => {
        e.preventDefault();

        if (!leadForm.checkValidity()) {
            leadForm.reportValidity();
            return;
        }

        const leadData = {
            name:                document.getElementById('name').value.trim(),
            instagram:           document.getElementById('instagram').value.trim(),
            website:             document.getElementById('website').value.trim(),
            fokus:               document.getElementById('fokus').value,
            datum:               document.getElementById('datum').value.trim(),
            momente:             document.getElementById('momente').value.trim(),
            investitionsrahmen:  document.getElementById('investitionsrahmen').value
        };

        trackEvent('form_submitted', { fokus: leadData.fokus, investitionsrahmen: leadData.investitionsrahmen });

        // Transition to loading screen
        nextStep(3);

        // Fire lead to backend (non-blocking)
        try {
            const response = await fetch('/api/qualify', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify(leadData)
            });
            const data = await response.json();
            currentLeadId = data.lead_id || null;
            console.log('Lead processed:', data);
        } catch (err) {
            console.error('Backend error (non-critical):', err);
        }

        // Show Calendly after brief "processing" feel
        setTimeout(() => {
            initCalendly(leadData);
            nextStep(4);
            trackEvent('calendly_loaded', { step: 4 });
        }, 2800);
    });
}

// ── Calendly Integration ──────────────────────────
function initCalendly(lead) {
    const embedContainer = document.getElementById('calendly-embed');
    embedContainer.innerHTML = '';

    Calendly.initInlineWidget({
        url: CALENDLY_URL,
        parentElement: embedContainer,
        prefill: {
            name: lead.name,
            customAnswers: {
                a1: lead.instagram + (lead.website ? ` | ${lead.website}` : ''),
                a2: `${lead.fokus} | ${lead.datum} | ${lead.investitionsrahmen} | ${lead.momente}`
            }
        },
        utm: {
            utmSource:   'Instagram',
            utmMedium:   'Funnel',
            utmCampaign: 'BioLink'
        }
    });
}

window.addEventListener('message', (event) => {
    if (event.data && event.data.event === 'calendly.event_scheduled') {
        trackEvent('calendly_event_scheduled', { calendlyEvent: event.data.event });
    }
});

// ── Subtle Parallax on Orbs ───────────────────────
document.addEventListener('mousemove', (e) => {
    const orbs = document.querySelectorAll('.orb');
    const x = (e.clientX / window.innerWidth)  - 0.5;
    const y = (e.clientY / window.innerHeight) - 0.5;

    orbs.forEach((orb, i) => {
        const depth = (i + 1) * 14;
        orb.style.transform = `translate(${x * depth}px, ${y * depth}px)`;
    });
});

// ── Image Protection ──────────────────────────────
// Casual-download protection. Cannot block DevTools/Screenshot.
// Scope: protected images only (hero portrait + studio thumbs). Leaves
// devtools, form, and rest of the page fully functional.
(function protectImages() {
    const protectedSelector = '.hero-portrait img, .portrait-studios .thumb img, .hero-portrait, .portrait-studios .thumb';

    // Block right-click "Save Image As" on protected images
    document.addEventListener('contextmenu', (e) => {
        if (e.target.closest('.hero-portrait, .portrait-studios')) {
            e.preventDefault();
        }
    });

    // Block drag-to-desktop
    document.addEventListener('dragstart', (e) => {
        if (e.target.tagName === 'IMG' || e.target.closest('.hero-portrait, .portrait-studios')) {
            e.preventDefault();
        }
    });

    // Block Cmd+S / Ctrl+S "Save Page"
    document.addEventListener('keydown', (e) => {
        if ((e.ctrlKey || e.metaKey) && e.key === 's') {
            e.preventDefault();
        }
    });

    // Set draggable=false on all protected images programmatically
    document.querySelectorAll(protectedSelector).forEach((el) => {
        if (el.tagName === 'IMG') el.setAttribute('draggable', 'false');
    });
})();
