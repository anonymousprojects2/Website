document.addEventListener('DOMContentLoaded', function() {
    const startScannerBtn = document.getElementById('startScanner');
    const scannerPlaceholder = document.getElementById('scanner-placeholder');
    const qrScanner = document.getElementById('qrScanner');
    const scanResult = document.getElementById('scanResult');
    const scanMessage = document.getElementById('scanMessage');
    const attendanceList = document.getElementById('attendanceList');

    let scanner = null;

    // Update attendance stats
    function updateStats() {
        fetch('/api/student/stats')
            .then(response => response.json())
            .then(data => {
                document.getElementById('totalClasses').textContent = data.totalClasses;
                document.getElementById('classesAttended').textContent = data.classesAttended;
                document.getElementById('attendancePercentage').textContent = 
                    data.totalClasses > 0 
                        ? Math.round((data.classesAttended / data.totalClasses) * 100) + '%'
                        : '0%';
            })
            .catch(error => console.error('Error fetching stats:', error));
    }

    // Update attendance history
    function updateAttendanceHistory() {
        fetch('/api/student/attendance-history')
            .then(response => response.json())
            .then(data => {
                attendanceList.innerHTML = data.history.map(record => `
                    <div class="attendance-item">
                        <p><strong>${record.subject}</strong> - ${record.department} ${record.year}</p>
                        <small>${new Date(record.timestamp).toLocaleString()}</small>
                    </div>
                `).join('');
            })
            .catch(error => console.error('Error fetching attendance history:', error));
    }

    // Start QR scanner
    async function startScanner() {
        try {
            const stream = await navigator.mediaDevices.getUserMedia({ video: { facingMode: "environment" } });
            qrScanner.srcObject = stream;
            qrScanner.classList.remove('hidden');
            scannerPlaceholder.classList.add('hidden');
            
            scanner = new QrScanner(qrScanner, result => handleScan(result), {
                highlightScanRegion: true,
                highlightCodeOutline: true,
            });
            
            scanner.start();
        } catch (error) {
            console.error('Error accessing camera:', error);
            showScanResult('Error accessing camera. Please make sure you have granted camera permissions.', false);
        }
    }

    // Handle QR scan result
    function handleScan(result) {
        // Stop scanner after successful scan
        if (scanner) {
            scanner.stop();
            qrScanner.srcObject.getTracks().forEach(track => track.stop());
            qrScanner.classList.add('hidden');
            scannerPlaceholder.classList.remove('hidden');
        }

        // Send scan result to server
        fetch('/api/student/mark-attendance', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({ qrData: result })
        })
        .then(response => response.json())
        .then(data => {
            showScanResult(data.message, data.success);
            if (data.success) {
                updateStats();
                updateAttendanceHistory();
            }
        })
        .catch(error => {
            console.error('Error marking attendance:', error);
            showScanResult('Error marking attendance. Please try again.', false);
        });
    }

    // Show scan result message
    function showScanResult(message, success) {
        scanResult.classList.remove('hidden', 'success', 'error');
        scanResult.classList.add(success ? 'success' : 'error');
        scanMessage.textContent = message;
    }

    // Event listeners
    startScannerBtn.addEventListener('click', startScanner);

    // Initial load
    updateStats();
    updateAttendanceHistory();

    // Update stats and history periodically
    setInterval(updateStats, 30000);
    setInterval(updateAttendanceHistory, 10000);
});
