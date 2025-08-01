// static/js/app.js

// Function to fetch and update live display data
function updateLiveDisplay() {
    fetch('/api/live-display-data/')
        .then(response => response.json())
        .then(data => {
            const container = document.getElementById('live-display');
            container.innerHTML = ''; // Clear previous

            data.members.forEach(member => {
                const div = document.createElement('div');
                div.className = 'member-card';
                div.innerHTML = `
                    <img src="/media/${member.image}" alt="${member.name}" />
                    <h4>${member.name}</h4>
                    <p>${member.time}</p>
                `;
                container.appendChild(div);
            });

            if (data.new_recognized) {
showToast(`🎉 ${data.new_recognized} marked present`);
            }
        })
        .catch(error => console.error('Live display fetch error:', error));
}

// Function to fetch and update logs
function updateLogs() {
    fetch('/api/logs/')
        .then(response => response.json())
        .then(data => {
            const logTable = document.getElementById('logs-body');
            logTable.innerHTML = '';
            data.logs.forEach(log => {
                const row = document.createElement('tr');
                row.innerHTML = `
                    <td>${log.name}</td>
                    <td>${log.date}</td>
                    <td>${log.time}</td>
                `;
                logTable.appendChild(row);
            });
        })
        .catch(error => console.error('Logs fetch error:', error));
}

// Function to show toast message
function showToast(message) {
    const toast = document.createElement('div');
    toast.className = 'toast';
    toast.innerText = message;
    document.body.appendChild(toast);
    setTimeout(() => toast.remove(), 3000);
}

// Auto-refresh every 10 seconds
setInterval(() => {
    if (document.getElementById('live-display')) {
        updateLiveDisplay();
    }
    if (document.getElementById('logs-body')) {
        updateLogs();
    }
}, 10000);

// Initial load
document.addEventListener('DOMContentLoaded', () => {
    updateLiveDisplay();
    updateLogs();
});