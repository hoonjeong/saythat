let currentPage = 1;
let isLoading = false;
let hasMoreData = true;
let currentTrendingPeriod = 0;

const trendingPeriods = ['실시간 인기순위', 'TODAY 인기순위', '주간 인기순위', '월간 인기순위'];

// 트렌딩 데이터는 API에서 받아옴
let trendingData = {};

function formatNumber(num) {
    if (num >= 1000) {
        return (num / 1000).toFixed(1) + 'K';
    }
    return num.toString();
}

function loadTrendingTopics() {
    // TODO: API에서 트렌딩 데이터 로드
    const period = trendingPeriods[currentTrendingPeriod];
    const topics = trendingData[period] || [];
    const trendingList = document.getElementById('trendingList');
    
    if (topics.length === 0) {
        trendingList.innerHTML = '<div class="trending-item">트렌딩 데이터를 불러오는 중...</div>';
        return;
    }
    
    trendingList.innerHTML = topics.map(topic => `
        <div class="trending-item">
            <span class="trending-rank">${topic.rank}</span>
            <div class="trending-content">
                <span class="trending-topic">${topic.title}</span>
                <div class="trending-stats">
                    <div class="trending-votes">
                        <span class="trending-agree">찬성 ${formatNumber(topic.agree)}</span>
                        <span class="trending-disagree">반대 ${formatNumber(topic.disagree)}</span>
                    </div>
                    <span>👁 ${formatNumber(topic.views)}</span>
                </div>
            </div>
        </div>
    `).join('');
}

function changeTrendingPeriod(direction) {
    currentTrendingPeriod = (currentTrendingPeriod + direction + trendingPeriods.length) % trendingPeriods.length;
    document.getElementById('trendingTitle').textContent = trendingPeriods[currentTrendingPeriod];
    loadTrendingTopics();
}

function createTopicElement(topic) {
    const heatLabel = topic.heat === 'hot' ? '🔥 HOT' : 
                     topic.heat === 'warm' ? '🌡 논란중' : '💭 활발';
    
    return `
        <div class="topic-item">
            <div class="topic-main">
                <h3 class="topic-title">${topic.title}</h3>
                <div class="topic-meta">
                    <span class="topic-time">${topic.time}</span>
                    <span class="topic-author">by ${topic.author}</span>
                </div>
            </div>
            <div class="topic-stats">
                <div class="vote-section">
                    <div class="vote-bar">
                        <div class="vote-progress agree" style="width: ${topic.agreePercent}%;">
                            <span class="vote-label">찬성 ${topic.agreePercent}%</span>
                        </div>
                        <div class="vote-progress disagree" style="width: ${topic.disagreePercent}%;">
                            <span class="vote-label">반대 ${topic.disagreePercent}%</span>
                        </div>
                    </div>
                    <div class="vote-count">총 ${topic.totalVotes.toLocaleString()}표</div>
                </div>
                <div class="topic-engagement">
                    <span class="comment-count">💬 ${topic.comments} 댓글</span>
                    <span class="view-count">👁 ${topic.views} 조회</span>
                    <span class="heat-indicator ${topic.heat}">${heatLabel}</span>
                </div>
            </div>
        </div>
    `;
}

function loadMoreTopics() {
    // TODO: API로 데이터 받아오기
    // 현재는 새로운 토론 시스템을 사용하므로 비활성화
}

window.addEventListener('scroll', () => {
    if (window.innerHeight + window.scrollY >= document.documentElement.scrollHeight - 100) {
        loadMoreTopics();
    }
});

document.addEventListener('DOMContentLoaded', function() {
    loadTrendingTopics();
    
    document.querySelectorAll('.topic-item').forEach(item => {
        item.addEventListener('click', function() {
            // 토론 상세 페이지로 이동
        });
    });
    
    document.querySelector('.create-topic-btn')?.addEventListener('click', function() {
        window.location.href = '/new-discussion';
    });
    
    document.querySelector('.btn-login')?.addEventListener('click', function() {
        window.location.href = '/login';
    });
    
    document.querySelector('.btn-signup')?.addEventListener('click', function() {
        window.location.href = '/register';
    });
    
    document.querySelector('.search-btn')?.addEventListener('click', function() {
        const searchValue = document.querySelector('.search-input').value;
        if (searchValue) {
            // TODO: 검색 기능 구현
        }
    });
    
    document.querySelector('.search-input')?.addEventListener('keypress', function(e) {
        if (e.key === 'Enter') {
            const searchValue = this.value;
            if (searchValue) {
                // TODO: 검색 기능 구현
            }
        }
    });
});