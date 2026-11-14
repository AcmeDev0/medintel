// MedIntel AI - Chat Logic

document.addEventListener('DOMContentLoaded', () => {
    const chatForm = document.getElementById('chat-form');
    if (!chatForm) return; // Not on chat page

    const chatInput = document.getElementById('chat-input');
    const sendBtn = document.getElementById('send-btn');
    const messagesContainer = document.getElementById('chat-messages');
    const loadingOverlay = document.getElementById('chat-loading');
    const sourcesContainer = document.getElementById('sources-container');

    // Configure marked for Markdown parsing
    if (typeof marked !== 'undefined') {
        marked.setOptions({
            breaks: true,
            gfm: true
        });
    }

    chatForm.addEventListener('submit', async (e) => {
        e.preventDefault();
        
        const message = chatInput.value.trim();
        if (!message) return;

        // 1. Add user message to UI
        appendMessage('user', message);
        chatInput.value = '';
        
        // 2. Show loading state
        sendBtn.disabled = true;
        chatInput.disabled = true;
        loadingOverlay.classList.remove('d-none');
        sourcesContainer.innerHTML = '<div class="text-center text-muted mt-5"><div class="spinner-border spinner-border-sm text-success mb-2"></div><br>Searching regulatory knowledge base...</div>';

        try {
            // 3. Send to API
            const response = await fetch('/api/chat', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({ message })
            });

            if (!response.ok) {
                throw new Error('API request failed');
            }

            const data = await response.json();
            
            // 4. Add AI response to UI
            appendMessage('ai', data.answer);
            
            // 5. Update sources panel
            updateSources(data.sources);

        } catch (error) {
            console.error('Chat error:', error);
            appendMessage('error', 'Sorry, an error occurred while connecting to the regulatory intelligence engine. Please try again.');
            sourcesContainer.innerHTML = '<div class="text-danger p-3">Failed to load sources.</div>';
        } finally {
            // 6. Restore UI state
            sendBtn.disabled = false;
            chatInput.disabled = false;
            loadingOverlay.classList.add('d-none');
            chatInput.focus();
        }
    });

    function appendMessage(sender, text) {
        const wrapper = document.createElement('div');
        wrapper.className = `d-flex mb-4 ${sender === 'user' ? 'justify-content-end' : ''}`;
        
        let iconHtml = '';
        let bubbleClass = 'bg-white border text-dark';
        
        if (sender === 'ai') {
            iconHtml = `<div class="flex-shrink-0 bg-primary bg-opacity-10 text-primary rounded-circle d-flex align-items-center justify-content-center me-3" style="width: 40px; height: 40px;"><i class="bi bi-robot"></i></div>`;
        } else if (sender === 'error') {
            iconHtml = `<div class="flex-shrink-0 bg-danger bg-opacity-10 text-danger rounded-circle d-flex align-items-center justify-content-center me-3" style="width: 40px; height: 40px;"><i class="bi bi-exclamation-triangle"></i></div>`;
            bubbleClass = 'bg-danger bg-opacity-10 border-danger text-danger';
        } else {
            bubbleClass = 'user-message';
        }

        const parsedContent = sender === 'ai' ? marked.parse(text) : text;
        const contentHtml = sender === 'user' 
            ? `<div class="message-bubble p-3 rounded-3 shadow-sm ${bubbleClass}" style="max-width: 80%;">${text}</div>`
            : `<div class="message-bubble p-3 rounded-3 shadow-sm markdown-content ${bubbleClass}" style="max-width: 80%;">${parsedContent}</div>`;

        wrapper.innerHTML = sender === 'user' ? contentHtml : iconHtml + contentHtml;
        
        messagesContainer.appendChild(wrapper);
        messagesContainer.scrollTop = messagesContainer.scrollHeight;
    }

    function updateSources(sources) {
        sourcesContainer.innerHTML = '';
        
        if (!sources || sources.length === 0) {
            sourcesContainer.innerHTML = `
                <div class="alert alert-warning mb-0 small">
                    <i class="bi bi-exclamation-triangle me-2"></i> No specific regulatory documents were matched for this query. The answer is based on general regulatory principles.
                </div>`;
            return;
        }
        
        sources.forEach((source, index) => {
            const card = document.createElement('div');
            card.className = 'source-card bg-white p-3 rounded border mb-2 shadow-sm';
            card.innerHTML = `
                <div class="d-flex justify-content-between align-items-start mb-2">
                    <span class="badge bg-success bg-opacity-10 text-success rounded-pill">Source ${index + 1}</span>
                    <small class="text-muted">Page ${source.page}</small>
                </div>
                <h6 class="fw-bold mb-1 text-truncate" title="${source.document}">${source.document}</h6>
                ${source.section ? `<small class="text-primary d-block mb-2"><i class="bi bi-bookmark me-1"></i>${source.section}</small>` : ''}
                <div class="text-muted small mt-2 bg-light p-2 rounded" style="max-height: 80px; overflow-y: auto;">
                    <em>"...${source.excerpt}..."</em>
                </div>
            `;
            sourcesContainer.appendChild(card);
        });
    }
});
