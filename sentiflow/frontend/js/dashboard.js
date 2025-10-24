// SentiFlow Analytics Dashboard

const API_BASE_URL = window.location.origin;

// Chart instances
let sentimentChart = null;
let trendChart = null;

// Initialize
document.addEventListener('DOMContentLoaded', () => {
    initCharts();
    loadAnalytics();
    
    // Auto-refresh every 10 seconds
    setInterval(loadAnalytics, 10000);
    
    // Manual refresh button
    document.getElementById('refreshBtn').addEventListener('click', () => {
        loadAnalytics(true);
    });
    
    console.log('✅ Dashboard initialized');
});

// Initialize charts
function initCharts() {
    // Sentiment Distribution Pie Chart
    const sentimentCtx = document.getElementById('sentimentChart').getContext('2d');
    sentimentChart = new Chart(sentimentCtx, {
        type: 'doughnut',
        data: {
            labels: ['Positive', 'Neutral', 'Negative', 'Frustrated', 'Urgent'],
            datasets: [{
                data: [0, 0, 0, 0, 0],
                backgroundColor: [
                    '#10B981', // positive
                    '#6B7280', // neutral
                    '#EF4444', // negative
                    '#DC2626', // frustrated
                    '#F59E0B'  // urgent
                ],
                borderWidth: 0
            }]
        },
        options: {
            responsive: true,
            maintainAspectRatio: true,
            plugins: {
                legend: {
                    position: 'bottom',
                    labels: {
                        padding: 15,
                        font: {
                            size: 12
                        }
                    }
                },
                tooltip: {
                    callbacks: {
                        label: function(context) {
                            const label = context.label || '';
                            const value = context.parsed || 0;
                            const total = context.dataset.data.reduce((a, b) => a + b, 0);
                            const percentage = total > 0 ? ((value / total) * 100).toFixed(1) : 0;
                            return `${label}: ${value} (${percentage}%)`;
                        }
                    }
                }
            }
        }
    });
    
    // Trend Line Chart
    const trendCtx = document.getElementById('trendChart').getContext('2d');
    trendChart = new Chart(trendCtx, {
        type: 'line',
        data: {
            labels: [],
            datasets: [{
                label: 'Sentiment Score',
                data: [],
                borderColor: '#4F46E5',
                backgroundColor: 'rgba(79, 70, 229, 0.1)',
                borderWidth: 2,
                fill: true,
                tension: 0.4
            }]
        },
        options: {
            responsive: true,
            maintainAspectRatio: true,
            scales: {
                y: {
                    beginAtZero: true,
                    max: 1,
                    ticks: {
                        callback: function(value) {
                            return value.toFixed(1);
                        }
                    }
                }
            },
            plugins: {
                legend: {
                    display: false
                },
                tooltip: {
                    callbacks: {
                        label: function(context) {
                            return `Score: ${context.parsed.y.toFixed(2)}`;
                        }
                    }
                }
            }
        }
    });
}

// Load analytics data
async function loadAnalytics(showAnimation = false) {
    try {
        if (showAnimation) {
            const refreshBtn = document.getElementById('refreshBtn');
            refreshBtn.classList.add('spinning');
            setTimeout(() => refreshBtn.classList.remove('spinning'), 1000);
        }
        
        // Fetch overview
        const overviewResponse = await fetch(`${API_BASE_URL}/api/analytics/overview`);
        const overviewData = await overviewResponse.json();
        
        // Fetch recent queries
        const recentResponse = await fetch(`${API_BASE_URL}/api/analytics/recent?limit=10`);
        const recentData = await recentResponse.json();
        
        // Update metrics
        updateMetrics(overviewData);
        
        // Update charts
        updateCharts(overviewData, recentData);
        
        // Update recent queries list
        updateRecentQueries(recentData);
        
    } catch (error) {
        console.error('Error loading analytics:', error);
    }
}

// Update metric cards
function updateMetrics(data) {
    // Total queries
    document.getElementById('totalQueries').textContent = data.total_queries.toLocaleString();
    
    // Average sentiment score
    document.getElementById('avgSentiment').textContent = data.avg_sentiment_score.toFixed(2);
    
    // Positive rate
    const total = data.total_queries;
    const positive = data.sentiment_distribution.positive;
    const positiveRate = total > 0 ? ((positive / total) * 100).toFixed(1) : 0;
    document.getElementById('positiveRate').textContent = `${positiveRate}%`;
}

// Update charts
function updateCharts(overviewData, recentData) {
    // Update sentiment distribution chart
    const dist = overviewData.sentiment_distribution;
    sentimentChart.data.datasets[0].data = [
        dist.positive,
        dist.neutral,
        dist.negative,
        dist.frustrated,
        dist.urgent
    ];
    sentimentChart.update();
    
    // Update trend chart
    if (recentData.queries && recentData.queries.length > 0) {
        // Reverse to show oldest first
        const queries = [...recentData.queries].reverse();
        
        // Map sentiment labels to scores
        const sentimentScores = {
            'positive': 1.0,
            'neutral': 0.5,
            'negative': 0.0,
            'frustrated': 0.0,
            'urgent': 0.3
        };
        
        trendChart.data.labels = queries.map((_, i) => `Q${i + 1}`);
        trendChart.data.datasets[0].data = queries.map(q => 
            sentimentScores[q.sentiment] || 0.5
        );
        trendChart.update();
    }
}

// Update recent queries list
function updateRecentQueries(data) {
    const listContainer = document.getElementById('recentQueriesList');
    
    if (!data.queries || data.queries.length === 0) {
        listContainer.innerHTML = '<p style="color: #6B7280; text-align: center; padding: 20px;">No queries yet</p>';
        return;
    }
    
    listContainer.innerHTML = '';
    
    data.queries.forEach(query => {
        const item = document.createElement('div');
        item.className = 'query-item';
        
        const textDiv = document.createElement('div');
        textDiv.className = 'query-text';
        textDiv.textContent = query.message;
        
        const sentimentBadge = document.createElement('span');
        sentimentBadge.className = `query-sentiment sentiment-badge ${query.sentiment}`;
        sentimentBadge.textContent = getSentimentIcon(query.sentiment) + ' ' + capitalizeFirst(query.sentiment);
        
        item.appendChild(textDiv);
        item.appendChild(sentimentBadge);
        listContainer.appendChild(item);
    });
}

// Helper: Get sentiment icon
function getSentimentIcon(sentiment) {
    const icons = {
        positive: '😊',
        neutral: '😐',
        negative: '😟',
        frustrated: '😠',
        urgent: '⚡'
    };
    return icons[sentiment] || '😐';
}

// Helper: Capitalize first letter
function capitalizeFirst(str) {
    return str.charAt(0).toUpperCase() + str.slice(1);
}
