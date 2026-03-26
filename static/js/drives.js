// drives.js
// Handles view button, branch tooltip accessibility, and modal population.

document.addEventListener('DOMContentLoaded', function () {
    // Delegate view button clicks
    const table = document.getElementById('drivesTable');
    if (table) {
        table.addEventListener('click', function (e) {
            const btn = e.target.closest('.action-icon.view');
            if (btn) {
                const id = btn.dataset.driveId;
                if (id) showDriveDetails(id);
            }
        });
    }

    // Make branches chips keyboard accessible and toggle tooltip
    document.querySelectorAll('.branches-chip').forEach(chip => {
        chip.setAttribute('tabindex', '0');
        chip.setAttribute('role', 'button');
        chip.addEventListener('click', toggleBranchesTooltip);
        chip.addEventListener('keydown', function (e) {
            if (e.key === 'Enter' || e.key === ' ') {
                e.preventDefault();
                toggleBranchesTooltip.call(this, e);
            } else if (e.key === 'Escape') {
                hideTooltipForChip(this);
            }
        });
    });

    // Close tooltip when clicking outside
    document.addEventListener('click', function (e) {
        if (!e.target.closest('.branches-dropdown')) {
            document.querySelectorAll('.branches-tooltip.show').forEach(t => t.classList.remove('show'));
        }
    });
});

function toggleBranchesTooltip(e) {
    const dropdown = this.closest('.branches-dropdown');
    if (!dropdown) return;
    const tooltip = dropdown.querySelector('.branches-tooltip');
    if (!tooltip) return;
    const isShown = tooltip.classList.toggle('show');
    this.setAttribute('aria-expanded', isShown ? 'true' : 'false');
}

function hideTooltipForChip(chip) {
    const dropdown = chip.closest('.branches-dropdown');
    if (!dropdown) return;
    const tooltip = dropdown.querySelector('.branches-tooltip');
    if (tooltip) {
        tooltip.classList.remove('show');
        chip.setAttribute('aria-expanded', 'false');
    }
}

function showDriveDetails(id) {
    // Minimal modal population. Replace fetch logic with your API if available.
    const modalEl = document.getElementById('driveModal');
    const titleEl = document.getElementById('modalTitle');
    const bodyEl = document.getElementById('modalBody');
    if (!modalEl || !titleEl || !bodyEl) return;

    titleEl.textContent = `Drive #${id}`;
    bodyEl.innerHTML = '<p>Loading details…</p>';

    // If you have an endpoint that returns drive details as HTML or JSON, fetch it here.
    // Example (uncomment and adapt if you have an endpoint):
    // fetch(`/admin/drive/${id}/details`)
    //   .then(r => r.text())
    //   .then(html => { bodyEl.innerHTML = html; })
    //   .catch(() => { bodyEl.innerHTML = '<p>Unable to load details.</p>'; });

    // Show Bootstrap modal if available
    if (window.bootstrap && bootstrap.Modal) {
        const modal = new bootstrap.Modal(modalEl);
        modal.show();
    } else {
        // Fallback: make modal visible (if your CSS supports it)
        modalEl.style.display = 'block';
    }
}
