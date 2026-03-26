// view_candidate.js
// Handles AOS init, contact modal, schedule interview modal and status updates.

document.addEventListener('DOMContentLoaded', () => {
    // AOS initialization
    if (typeof AOS !== 'undefined') {
        AOS.init({ duration: 1000, once: true });
    }

    initializeContactModal();
});

function getStudentData() {
    const root = document.getElementById('viewCandidate');
    return {
        email: root?.dataset.studentEmail || '',
        name: root?.dataset.studentName || ''
    };
}

function contactCandidate() {
    const { email, name } = getStudentData();
    showContactModal(email, name);
}

function showContactModal(email, name) {
    let modal = document.getElementById('contactCandidateModal');
    if (!modal) {
        modal = document.createElement('div');
        modal.id = 'contactCandidateModal';
        modal.className = 'modal fade';
        modal.setAttribute('tabindex', '-1');
        modal.setAttribute('aria-hidden', 'true');
        modal.innerHTML = `
            <div class="modal-dialog modal-dialog-centered">
                <div class="modal-content futuristic-modal">
                    <div class="modal-header">
                        <h5 class="modal-title">Contact Candidate</h5>
                        <button type="button" class="btn-close" data-bs-dismiss="modal" aria-label="Close"></button>
                    </div>
                    <div class="modal-body">
                        <div class="contact-info mb-3">
                            <p><strong id="modalCandidateName"></strong></p>
                            <p id="modalCandidateEmail" class="text-muted small"></p>
                        </div>
                        <form id="contactForm">
                            <div class="form-group-futuristic mb-2">
                                <label class="form-label">Method</label>
                                <select id="contactMethod" class="form-control">
                                    <option value="email">Default Mail</option>
                                    <option value="gmail">Gmail</option>
                                    <option value="outlook">Outlook</option>
                                    <option value="copy">Copy to clipboard</option>
                                </select>
                            </div>
                            <div class="form-group-futuristic mb-2">
                                <label class="form-label">Subject</label>
                                <input id="emailSubject" class="form-control" placeholder="Subject">
                            </div>
                            <div class="form-group-futuristic mb-2">
                                <label class="form-label">Message</label>
                                <textarea id="emailMessage" class="form-control" rows="4" placeholder="Message..."></textarea>
                            </div>
                        </form>
                    </div>
                    <div class="modal-footer">
                        <button type="button" class="btn-modal-secondary" data-bs-dismiss="modal">Cancel</button>
                        <button type="button" class="btn-modal-primary" id="sendContactBtn"><i class="fas fa-paper-plane me-2" aria-hidden="true"></i>Send Message</button>
                    </div>
                </div>
            </div>
        `;
        document.body.appendChild(modal);
        document.getElementById('sendContactBtn').addEventListener('click', sendEmail);
    }

    document.getElementById('modalCandidateName').textContent = name;
    document.getElementById('modalCandidateEmail').textContent = email;

    const bsModal = new bootstrap.Modal(modal);
    bsModal.show();
}

function sendEmail(event) {
    if (event) event.preventDefault();
    const { email } = getStudentData();
    const subject = document.getElementById('emailSubject')?.value || 'Interview Opportunity';
    const message = document.getElementById('emailMessage')?.value || 'I would like to discuss an opportunity with you.';
    const method = document.getElementById('contactMethod')?.value || 'email';

    if (!email) return;

    switch (method) {
        case 'email':
            window.location.href = `mailto:${email}?subject=${encodeURIComponent(subject)}&body=${encodeURIComponent(message)}`;
            break;
        case 'gmail':
            window.open(`https://mail.google.com/mail/?view=cm&fs=1&to=${email}&su=${encodeURIComponent(subject)}&body=${encodeURIComponent(message)}`, '_blank');
            break;
        case 'outlook':
            window.open(`https://outlook.live.com/mail/0/deeplink/compose?to=${email}&subject=${encodeURIComponent(subject)}&body=${encodeURIComponent(message)}`, '_blank');
            break;
        case 'copy':
            const fullMessage = `To: ${email}\nSubject: ${subject}\n\n${message}`;
            navigator.clipboard.writeText(fullMessage).then(() => alert('Message copied to clipboard!')).catch(() => alert('Failed to copy to clipboard'));
            break;
    }

    const modal = document.getElementById('contactCandidateModal');
    const bsModal = bootstrap.Modal.getInstance(modal);
    if (bsModal) bsModal.hide();
}

function scheduleInterview() {
    const { email: studentEmail, name: studentName } = getStudentData();
    let modal = document.getElementById('scheduleInterviewModal');
    if (!modal) {
        modal = document.createElement('div');
        modal.id = 'scheduleInterviewModal';
        modal.className = 'modal fade';
        modal.setAttribute('tabindex', '-1');
        modal.setAttribute('aria-hidden', 'true');
        modal.innerHTML = `
            <div class="modal-dialog modal-dialog-centered">
                <div class="modal-content futuristic-modal">
                    <div class="modal-header">
                        <h5 class="modal-title"><i class="fas fa-calendar-check me-2" aria-hidden="true"></i>Schedule Interview</h5>
                        <button type="button" class="btn-close" data-bs-dismiss="modal" aria-label="Close"></button>
                    </div>
                    <div class="modal-body">
                        <form id="interviewForm">
                            <div class="form-group-futuristic mb-3">
                                <label class="form-label">Date</label>
                                <input type="date" id="interviewDate" class="form-control">
                            </div>
                            <div class="form-group-futuristic mb-3">
                                <label class="form-label">Time</label>
                                <input type="time" id="interviewTime" class="form-control">
                            </div>
                            <div class="form-group-futuristic mb-3">
                                <label class="form-label">Mode</label>
                                <select id="interviewMode" class="form-control">
                                    <option value="online">Online</option>
                                    <option value="offline">Offline</option>
                                    <option value="unspecified">Unspecified</option>
                                </select>
                            </div>
                            <div class="form-group-futuristic mb-3" id="onlineLinkGroup" style="display:none;">
                                <label class="form-label">Meeting Link</label>
                                <input type="url" class="form-control" id="meetingLink" placeholder="https://meet.google.com/...">
                            </div>
                            <div class="form-group-futuristic mb-3" id="offlineLocationGroup" style="display:none;">
                                <label class="form-label">Location</label>
                                <input type="text" class="form-control" id="location" placeholder="Office address...">
                            </div>
                            <div class="form-group-futuristic mb-3">
                                <label class="form-label">Additional Notes</label>
                                <textarea class="form-control" id="interviewNotes" rows="3"></textarea>
                            </div>
                        </form>
                    </div>
                    <div class="modal-footer">
                        <button type="button" class="btn-modal-secondary" data-bs-dismiss="modal">Cancel</button>
                        <button type="button" class="btn-modal-primary" id="sendInterviewBtn"><i class="fas fa-paper-plane me-2" aria-hidden="true"></i>Send Invitation</button>
                    </div>
                </div>
            </div>
        `;
        document.body.appendChild(modal);

        modal.querySelector('#interviewMode').addEventListener('change', function() {
            const onlineGroup = document.getElementById('onlineLinkGroup');
            const offlineGroup = document.getElementById('offlineLocationGroup');
            if (this.value === 'online') { onlineGroup.style.display = 'block'; offlineGroup.style.display = 'none'; }
            else if (this.value === 'offline') { onlineGroup.style.display = 'none'; offlineGroup.style.display = 'block'; }
            else { onlineGroup.style.display = 'none'; offlineGroup.style.display = 'none'; }
        });

        document.getElementById('sendInterviewBtn').addEventListener('click', sendInterviewInvite);
    }

    const bsModal = new bootstrap.Modal(modal);
    bsModal.show();
}

function sendInterviewInvite() {
    const date = document.getElementById('interviewDate')?.value;
    const time = document.getElementById('interviewTime')?.value;
    const mode = document.getElementById('interviewMode')?.value;
    const notes = document.getElementById('interviewNotes')?.value || '';
    const { email: studentEmail } = getStudentData();

    if (!date || !time) { alert('Please select date and time'); return; }

    let modeDetails = '';
    if (mode === 'online') {
        const link = document.getElementById('meetingLink')?.value;
        if (!link) { alert('Please provide a meeting link for online interview'); return; }
        modeDetails = `\nMeeting Link: ${link}`;
    } else if (mode === 'offline') {
        const location = document.getElementById('location')?.value;
        if (!location) { alert('Please provide a location for offline interview'); return; }
        modeDetails = `\nLocation: ${location}`;
    }

    const subject = 'Interview Invitation';
    const body = `Dear Candidate,\n\nYou have been invited for an interview.\n\nDate: ${date}\nTime: ${time}\nMode: ${mode}${modeDetails}\n\nAdditional Notes: ${notes}\n\nBest regards,\nHR Team`;

    window.location.href = `mailto:${studentEmail}?subject=${encodeURIComponent(subject)}&body=${encodeURIComponent(body)}`;

    const modal = document.getElementById('scheduleInterviewModal');
    const bsModal = bootstrap.Modal.getInstance(modal);
    if (bsModal) bsModal.hide();
}

function initializeContactModal() {
    if (document.getElementById('viewCandidateStyleInjected')) return;
    const style = document.createElement('style');
    style.id = 'viewCandidateStyleInjected';
    style.textContent = `
        .futuristic-modal { background: var(--glass-bg); backdrop-filter: blur(10px); border: 1px solid var(--glass-border); border-radius: 20px; }
        .modal-header { border-bottom: 1px solid var(--glass-border); padding: 20px; }
        .modal-header .modal-title { color: var(--dark); font-weight: 600; }
        .modal-body { padding: 20px; }
        .modal-footer { border-top: 1px solid var(--glass-border); padding: 20px; }
        .form-group-futuristic label { color: var(--dark); font-weight: 500; margin-bottom: 5px; }
        .form-group-futuristic .form-control { background: var(--glass-bg); border: 1px solid var(--glass-border); color: var(--dark); border-radius: 10px; padding: 10px 15px; }
        .form-group-futuristic .form-control:focus { border-color: var(--primary); box-shadow: 0 0 0 3px rgba(99,102,241,0.1); }
        .btn-modal-primary { padding: 10px 20px; background: linear-gradient(135deg, var(--primary), var(--secondary)); color: white; border: none; border-radius: 10px; cursor: pointer; }
        .btn-modal-primary:hover { transform: translateY(-2px); box-shadow: 0 10px 20px -5px var(--primary); }
        .btn-modal-secondary { padding: 10px 20px; background: transparent; color: var(--dark); border: 1px solid var(--glass-border); border-radius: 10px; cursor: pointer; }
        .contact-info { background: rgba(99,102,241,0.05); padding: 15px; border-radius: 10px; margin-bottom: 20px; }
    `;
    document.head.appendChild(style);
}

function updateStatus(appId, status) {
    const statusMessages = { shortlisted: 'shortlist', selected: 'select', rejected: 'reject' };
    if (!confirm(`Are you sure you want to ${statusMessages[status]} this application?`)) return;

    fetch(`/company/application/${appId}/status`, { method: 'POST', headers: { 'Content-Type': 'application/json' }, body: JSON.stringify({ status }) })
    .then(r => r.json())
    .then(data => { if (data.success) location.reload(); else alert('Error updating status'); })
    .catch(e => { console.error(e); alert('Error updating status'); });
}
