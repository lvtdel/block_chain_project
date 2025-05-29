const API_URL = window.location.origin;

function formatTimestamp(timestamp) {
    return new Date(timestamp * 1000).toLocaleString('vi-VN', {
        year: 'numeric',
        month: '2-digit',
        day: '2-digit',
        hour: '2-digit',
        minute: '2-digit',
        second: '2-digit'
    });
}

function truncateString(str, length = 16) {
    if (str.length <= length) return str;
    return str.substring(0, length) + '...';
}

async function loadBlockchain() {
    const blockchainView = document.getElementById('blockchain-view');
    blockchainView.innerHTML = `
        <h2 style="margin-bottom: 20px; color: #2d3748;">Các khối gần đây</h2>
        <div class="loading">
            <div class="spinner"></div>
            Đang tải dữ liệu blockchain...
        </div>
    `;

    try {
        const response = await fetch(`${API_URL}/chain`);
        const blocks = await response.json();

        const tableHTML = `
            <h2 style="margin-bottom: 20px; color: #2d3748;">Các khối gần đây</h2>
            <table class="blockchain-table">
                <thead>
                    <tr>
                        <th>Số Block</th>
                        <th>Hash</th>
                        <th>Thời gian</th>
                        <th>Số giao dịch</th>
                        <th>Hành động</th>
                    </tr>
                </thead>
                <tbody>
                    ${blocks.map(block => `
                        <tr>
                            <td>${block.index}</td>
                            <td class="hash-cell">${block.hash}</td>
                            <td>${formatTimestamp(block.timestamp)}</td>
                            <td>${block.transactions.length}</td>
                            <td><button class="action-btn" onclick="viewBlockTransactions('${block.hash}')">Xem giao dịch</button></td>
                        </tr>
                    `).join('')}
                </tbody>
            </table>
        `;

        blockchainView.innerHTML = tableHTML;
    } catch (error) {
        blockchainView.innerHTML = `
            <h2 style="margin-bottom: 20px; color: #2d3748;">Các khối gần đây</h2>
            <div class="no-data">Lỗi khi tải dữ liệu blockchain</div>
        `;
    }
}

async function loadAllTransactions() {
    const transactionsView = document.getElementById('transactions-view');
    transactionsView.innerHTML = `
        <h2 style="margin-bottom: 20px; color: #2d3748;">Tất cả giao dịch</h2>
        <div class="loading">
            <div class="spinner"></div>
            Đang tải dữ liệu giao dịch...
        </div>
    `;

    try {
        const response = await fetch(`${API_URL}/transactions`);
        const transactions = await response.json();

        const transactionsHTML = `
            <h2 style="margin-bottom: 20px; color: #2d3748;">Tất cả giao dịch</h2>
            <div class="transactions-list">
                ${transactions.map(tx => createTransactionCard(tx)).join('')}
            </div>
        `;

        transactionsView.innerHTML = transactions.length ? transactionsHTML : `
            <h2 style="margin-bottom: 20px; color: #2d3748;">Tất cả giao dịch</h2>
            <div class="no-data">Không có giao dịch nào</div>
        `;
    } catch (error) {
        transactionsView.innerHTML = `
            <h2 style="margin-bottom: 20px; color: #2d3748;">Tất cả giao dịch</h2>
            <div class="no-data">Lỗi khi tải dữ liệu giao dịch</div>
        `;
    }
}

async function loadPendingTransactions() {
    const pendingView = document.getElementById('pending-view');
    pendingView.innerHTML = `
        <h2 style="margin-bottom: 20px; color: #2d3748;">Giao dịch đang chờ</h2>
        <div class="loading">
            <div class="spinner"></div>
            Đang tải dữ liệu giao dịch đang chờ...
        </div>
    `;

    try {
        const response = await fetch(`${API_URL}/pending`);
        const transactions = await response.json();

        const pendingHTML = `
            <h2 style="margin-bottom: 20px; color: #2d3748;">Giao dịch đang chờ</h2>
            <div class="transactions-list">
                ${transactions.map(tx => createTransactionCard(tx)).join('')}
            </div>
        `;

        pendingView.innerHTML = transactions.length ? pendingHTML : `
            <h2 style="margin-bottom: 20px; color: #2d3748;">Giao dịch đang chờ</h2>
            <div class="no-data">Không có giao dịch đang chờ</div>
        `;
    } catch (error) {
        pendingView.innerHTML = `
            <h2 style="margin-bottom: 20px; color: #2d3748;">Giao dịch đang chờ</h2>
            <div class="no-data">Lỗi khi tải dữ liệu giao dịch đang chờ</div>
        `;
    }
}

function createTransactionCard(tx) {
    let value = '';
    if (tx.tx_type === 'payment' && tx.payload) {
        try {
            const payload = JSON.parse(tx.payload);
            value = `${payload.amount} ${payload.currency}`;
        } catch (e) {
            value = 'Invalid payload';
        }
    } else if (tx.payload) {
        try {
            const payload = JSON.parse(tx.payload);
            value = truncateString(JSON.stringify(payload), 100); // Chỉ hiện 20 ký tự đầu
        } catch (e) {
            value = truncateString(tx.payload, 100); // Nếu không phải JSON, hiện 20 ký tự đầu của payload
        }
    }

    const txType = tx.tx_type.toLowerCase();


    return `
        <div class="transaction-card">
            <div class="tx-card-header">
                <div class="tx-hash-section">
                    <div class="tx-hash-label">TX HASH</div>
                    <div class="tx-hash-value">${tx.hash}</div>
                </div>
                <div class="tx-type-badge ${txType}">${tx.tx_type}</div>
            </div>
            <div class="tx-card-content">
                <div class="tx-info-row">
                    <div class="tx-info-item">
                        <div class="tx-info-label">FROM ADDRESS</div>
                        <div class="tx-info-value">${tx.sender}</div>
                    </div>
                    <div class="tx-info-item">
                        <div class="tx-info-label">TO ADDRESS</div>
                        <div class="tx-info-value">${tx.receiver || ''}</div>
                    </div>
                    <div class="tx-info-item">
                        <div class="tx-info-label">VALUE</div>
                        <div class="tx-info-value tx-value ${txType}">${value}</div>
                    </div>
                </div>
            </div>
        </div>
    `;
}

function showTab(tabName) {
    // Update active tab
    document.querySelectorAll('.nav-tab').forEach(tab => {
        tab.classList.remove('active');
    });
    document.getElementById(tabName).classList.add('active');

    // Hide all views
    document.getElementById('transaction-view').style.display = 'none';
    document.getElementById('blockchain-view').style.display = 'none';
    document.getElementById('transactions-view').style.display = 'none';
    document.getElementById('pending-view').style.display = 'none';

    // Show and load selected view
    switch (tabName) {
        case 'blockchain':
            document.getElementById('blockchain-view').style.display = 'block';
            loadBlockchain();
            break;
        case 'transactions':
            document.getElementById('transactions-view').style.display = 'block';
            loadAllTransactions();
            break;
        case 'pending':
            document.getElementById('pending-view').style.display = 'block';
            loadPendingTransactions();
            break;
    }
}

// Initialize with blockchain view
document.addEventListener('DOMContentLoaded', function () {
    showTab('blockchain');

    // Auto refresh data every 10 seconds
    // setInterval(() => {
    //     const activeTab = document.querySelector('.nav-tabs .active');
    //     console.log(activeTab)
    //     if (activeTab) {
    //         console.log("Refreshing data...")
    //         showTab(activeTab.id);
    //     }
    // }, 5000);
});