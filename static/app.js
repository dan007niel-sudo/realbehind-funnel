/* ═══════════════════════════════════════════════════
   RealBehind Funnel Logic
   Handles step transitions, form submission and Calendly pre-fill.
   ═══════════════════════════════════════════════════ */

const CALENDLY_URL = 'https://calendly.com/dan007niel/30min';

function nextStep(stepNumber) {
    const steps = document.querySelectorAll('.step');
    steps.forEach(s => s.classList.remove('active'));
    
    document.getElementById(`step-${stepNumber}`).classList.add('active');
    
    // Scroller reset
    window.scrollTo({ top: 0, behavior: 'smooth' });
}

// ── Lead Form Handling ────────────────────────────
const leadForm = document.getElementById('lead-form');

if (leadForm) {
    leadForm.addEventListener('submit', async (e) => {
        e.preventDefault();
        
        const leadData = {
            name: document.getElementById('name').value,
            instagram: document.getElementById('instagram').value,
            website: document.getElementById('website').value,
            fokus: document.getElementById('fokus').value
        };
        
        // Step 1: Transition to analysis
        nextStep(3);
        
        // Step 2: Send data to backend (async)
        try {
            const response = await fetch('/api/qualify', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify(leadData)
            });
            const data = await response.json();
            console.log('Lead processed:', data);
        } catch (err) {
            console.error('Backend error:', err);
        }
        
        // Step 3: Wait for "analysis feel" and show Calendly
        setTimeout(() => {
            initCalendly(leadData);
            nextStep(4);
        }, 3000);
    });
}

// ── Calendly Integration ──────────────────────────
function initCalendly(lead) {
    const embedContainer = document.getElementById('calendly-embed');
    
    // Clear previous if any
    embedContainer.innerHTML = '';
    
    // Initialize Calendly with pre-filled data
    // Note: Calendly field names depend on your event settings.
    // Usually: a1 (name), a2 (email), etc. 
    // We try to pass them via URL params for simplicity.
    
    Calendly.initInlineWidget({
        url: CALENDLY_URL,
        parentElement: embedContainer,
        prefill: {
            name: lead.name,
            // email: lead.email, // If we had email
            customAnswers: {
                "a1": lead.instagram + (lead.website ? ` | ${lead.website}` : ''),
                "a2": lead.fokus
            }
        },
        utm: {
            utmSource: 'Instagram',
            utmMedium: 'Funnel',
            utmCampaign: 'BioLink'
        }
    });
}

// ── Background Parallax ───────────────────────────
document.addEventListener('mousemove', (e) => {
    const orbs = document.querySelectorAll('.glow-orb');
    const x = (e.clientX / window.innerWidth) - 0.5;
    const y = (e.clientY / window.innerHeight) - 0.5;
    
    orbs.forEach((orb, index) => {
        const factor = (index + 1) * 20;
        orb.style.transform = `translate(${x * factor}px, ${y * factor}px)`;
    });
});
