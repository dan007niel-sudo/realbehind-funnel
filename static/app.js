/* ═══════════════════════════════════════════════════
   RealBehind — Funnel Logic v2
   Step transitions, form handling, Calendly pre-fill.
   ═══════════════════════════════════════════════════ */

const CALENDLY_URL = 'https://calendly.com/dan007niel/30min';

// ── Step Navigation ───────────────────────────────
function nextStep(stepNumber) {
    const steps = document.querySelectorAll('.step');
    steps.forEach(s => s.classList.remove('active'));
    document.getElementById(`step-${stepNumber}`).classList.add('active');
    window.scrollTo({ top: 0, behavior: 'smooth' });
}

// ── Lead Form Handling ────────────────────────────
const leadForm = document.getElementById('lead-form');

if (leadForm) {
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
            console.log('Lead processed:', data);
        } catch (err) {
            console.error('Backend error (non-critical):', err);
        }

        // Show Calendly after brief "processing" feel
        setTimeout(() => {
            initCalendly(leadData);
            nextStep(4);
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
