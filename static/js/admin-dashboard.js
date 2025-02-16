document.addEventListener('DOMContentLoaded', function() {
    const qrDisplay = document.getElementById('qrDisplay');
    const qrCode = document.getElementById('qrCode');
    const qrTimer = document.getElementById('qrTimer');
    const generateQRBtn = document.getElementById('generateQR');
    const departmentSelect = document.getElementById('department');
    const yearSelect = document.getElementById('year');
    const activityList = document.getElementById('activityList');

    let qrUpdateInterval;
    let timeLeft = 15;

    // Update stats
    function updateStats() {
        fetch('/api/admin/stats')
            .then(response => response.json())
            .then(data => {
                document.getElementById('totalStudents').textContent = data.totalStudents;
                document.getElementById('todayAttendance').textContent = data.todayAttendance;
                document.getElementById('activeSessions').textContent = data.activeSessions;
            })
            .catch(error => console.error('Error fetching stats:', error));
    }

    // Update activity list
    function updateActivityList() {
        fetch('/api/admin/recent-activity')
            .then(response => response.json())
            .then(data => {
                activityList.innerHTML = data.activities.map(activity => `
                    <div class="activity-item">
                        <p><strong>${activity.student}</strong> marked attendance for ${activity.department} ${activity.year}</p>
                        <small>${new Date(activity.timestamp).toLocaleString()}</small>
                    </div>
                `).join('');
            })
            .catch(error => console.error('Error fetching activities:', error));
    }

    // Generate new QR code
    function generateQR() {
        const department = departmentSelect.value;
        const year = yearSelect.value;

        fetch('/api/admin/generate-qr', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({ department, year })
        })
        .then(response => response.json())
        .then(data => {
            qrCode.src = data.qrCodeUrl;
            qrCode.classList.remove('hidden');
            startQRTimer();
        })
        .catch(error => console.error('Error generating QR:', error));
    }

    // Start QR timer
    function startQRTimer() {
        timeLeft = 15;
        updateTimerDisplay();

        if (qrUpdateInterval) {
            clearInterval(qrUpdateInterval);
        }

        qrUpdateInterval = setInterval(() => {
            timeLeft--;
            updateTimerDisplay();

            if (timeLeft <= 0) {
                generateQR();
            }
        }, 1000);
    }

    // Update timer display
    function updateTimerDisplay() {
        qrTimer.textContent = `New QR code in: ${timeLeft}s`;
    }

    // Event listeners
    generateQRBtn.addEventListener('click', generateQR);

    // Initial load
    updateStats();
    updateActivityList();

    // Update stats and activity list periodically
    setInterval(updateStats, 30000);
    setInterval(updateActivityList, 10000);
});
