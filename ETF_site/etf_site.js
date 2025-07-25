// Sample ETF data structure
const etfData = [
    {
        id: 1,
        name: "NIFTY 50 ETF",
        category: "equity",
        fund: "ICICI Prudential",
        etfCount: 8,
        aum: "₹2,450 Cr",
        expenseRatio: "0.05%",
        description: "Tracks NIFTY 50 index with low expense ratio",
        constituents: ["Reliance", "TCS", "HDFC Bank", "Infosys", "ICICI Bank"],
        returns: {
            "1Y": "12.5%",
            "3Y": "15.2%",
            "5Y": "11.8%"
        }
    },
    {
        id: 2,
        name: "Gold ETF",
        category: "gold",
        fund: "SBI Mutual Fund",
        etfCount: 3,
        aum: "₹1,200 Cr",
        expenseRatio: "0.40%",
        description: "Physical gold investment through stock exchange",
        constituents: ["Gold Bars", "Gold Coins"],
        returns: {
            "1Y": "8.2%",
            "3Y": "9.5%",
            "5Y": "7.8%"
        }
    },
    {
        id: 3,
        name: "Liquid ETF",
        category: "debt",
        fund: "Nippon India",
        etfCount: 2,
        aum: "₹850 Cr",
        expenseRatio: "0.15%",
        description: "High liquidity debt instrument with stable returns",
        constituents: ["Treasury Bills", "Commercial Papers", "CDs"],
        returns: {
            "1Y": "4.2%",
            "3Y": "5.1%",
            "5Y": "4.8%"
        }
    },
    {
        id: 4,
        name: "NASDAQ 100 ETF",
        category: "international",
        fund: "Motilal Oswal",
        etfCount: 1,
        aum: "₹680 Cr",
        expenseRatio: "0.30%",
        description: "Exposure to top 100 US technology companies",
        constituents: ["Apple", "Microsoft", "Amazon", "Tesla", "Google"],
        returns: {
            "1Y": "18.5%",
            "3Y": "22.1%",
            "5Y": "16.8%"
        }
    }
];

// DOM Elements
const tilesContainer = document.getElementById('tilesContainer');
const searchInput = document.getElementById('searchInput');
const filterTabs = document.querySelectorAll('.filter-tab');
const modal = document.getElementById('detailModal');
const modalBody = document.getElementById('modalBody');
const closeModal = document.querySelector('.close');

// Initialize dashboard
function initDashboard() {
    renderTiles(etfData);
    updateSummaryCards();
    setupEventListeners();
}

// Render ETF tiles
function renderTiles(data) {
    tilesContainer.innerHTML = '';
    
    data.forEach(etf => {
        const tile = document.createElement('div');
        tile.className = 'etf-tile';
        tile.dataset.category = etf.category;
        tile.dataset.etfId = etf.id;
        
        tile.innerHTML = `
            <div class="tile-header">
                <h3 class="tile-title">${etf.name}</h3>
                <span class="tile-badge">${etf.category.toUpperCase()}</span>
            </div>
            <div class="tile-stats">
                <div class="stat-item">
                    <div class="stat-value">${etf.etfCount}</div>
                    <div class="stat-label">ETFs</div>
                </div>
                <div class="stat-item">
                    <div class="stat-value">${etf.aum}</div>
                    <div class="stat-label">AUM</div>
                </div>
            </div>
            <div class="tile-description">${etf.description}</div>
            <div class="tile-footer">
                <span>Fund: ${etf.fund}</span>
                <span>ER: ${etf.expenseRatio}</span>
            </div>
        `;
        
        tile.addEventListener('click', () => showETFDetails(etf));
        tilesContainer.appendChild(tile);
    });
}

// Show ETF details in modal
function showETFDetails(etf) {
    modalBody.innerHTML = `
        <h2>${etf.name}</h2>
        <div style="margin: 20px 0;">
            <div style="display: grid; grid-template-columns: repeat(auto-fit, minmax(150px, 1fr)); gap: 15px; margin-bottom: 20px;">
                <div style="text-align: center; padding: 15px; background: #f7fafc; border-radius: 8px;">
                    <div style="font-size: 1.5rem; font-weight: bold; color: #667eea;">${etf.returns['1Y']}</div>
                    <div style="font-size: 12px; color: #718096;">1 Year Return</div>
                </div>
                <div style="text-align: center; padding: 15px; background: #f7fafc; border-radius: 8px;">
                    <div style="font-size: 1.5rem; font-weight: bold; color: #667eea;">${etf.returns['3Y']}</div>
                    <div style="font-size: 12px; color: #718096;">3 Year Return</div>
                </div>
                <div style="text-align: center; padding: 15px; background: #f7fafc; border-radius: 8px;">
                    <div style="font-size: 1.5rem; font-weight: bold; color: #667eea;">${etf.returns['5Y']}</div>
                    <div style="font-size: 12px; color: #718096;">5 Year Return</div>
                </div>
            </div>
            
            <h4 style="margin-bottom: 10px; color: #2d3748;">Fund Details</h4>
            <div style="display: grid; grid-template-columns: 1fr 1fr; gap: 10px; margin-bottom: 20px;">
                <div><strong>Fund House:</strong> ${etf.fund}</div>
                <div><strong>Expense Ratio:</strong> ${etf.expenseRatio}</div>
                <div><strong>AUM:</strong> ${etf.aum}</div>
                <div><strong>Category:</strong> ${etf.category.toUpperCase()}</div>
            </div>
            
            <h4 style="margin-bottom: 10px; color: #2d3748;">Top Holdings</h4>
            <div style="display: flex; flex-wrap: wrap; gap: 8px;">
                ${etf.constituents.map(constituent => 
                    `<span style="padding: 5px 12px; background: #edf2f7; border-radius: 15px; font-size: 12px;">${constituent}</span>`
                ).join('')}
            </div>
        </div>
    `;
    modal.style.display = 'block';
}

// Update summary cards
function updateSummaryCards() {
    document.getElementById('totalETFs').textContent = etfData.reduce((sum, etf) => sum + etf.etfCount, 0);
    document.getElementById('totalCategories').textContent = [...new Set(etfData.map(etf => etf.category))].length;
    document.getElementById('totalFunds').textContent = [...new Set(etfData.map(etf => etf.fund))].length;
}

// Setup event listeners
function setupEventListeners() {
    // Search functionality
    searchInput.addEventListener('input', handleSearch);
    
    // Filter tabs
    filterTabs.forEach(tab => {
        tab.addEventListener('click', handleFilter);
    });
    
    // Modal close
    closeModal.addEventListener('click', () => {
        modal.style.display = 'none';
    });
    
    window.addEventListener('click', (e) => {
        if (e.target === modal) {
            modal.style.display = 'none';
        }
    });
}

// Handle search
function handleSearch(e) {
    const searchTerm = e.target.value.toLowerCase();
    const filteredData = etfData.filter(etf => 
        etf.name.toLowerCase().includes(searchTerm) ||
        etf.category.toLowerCase().includes(searchTerm) ||
        etf.fund.toLowerCase().includes(searchTerm)
    );
    renderTiles(filteredData);
}

// Handle filter
function handleFilter(e) {
    // Update active tab
    filterTabs.forEach(tab => tab.classList.remove('active'));
    e.target.classList.add('active');
    
    const filter = e.target.dataset.filter;
    const filteredData = filter === 'all' ? etfData : etfData.filter(etf => etf.category === filter);
    renderTiles(filteredData);
}

// Initialize dashboard when DOM is loaded
document.addEventListener('DOMContentLoaded', initDashboard);
