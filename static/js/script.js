let currentPage = 1;
let isLoading = false;
let hasMoreData = true;
let currentTrendingPeriod = 0;

const trendingPeriods = ['실시간 인기순위', 'TODAY 인기순위', '주간 인기순위', '월간 인기순위'];

const trendingData = {
    '실시간 인기순위': [
        { rank: 1, title: '의대 정원 확대, 과연 필요한가?', agree: 2124, disagree: 1297, views: 15200 },
        { rank: 2, title: '최저임금을 대폭 인상해야 하는가?', agree: 2357, disagree: 2175, views: 21700 },
        { rank: 3, title: '온라인 투표로 대통령 선거를 진행해도 되는가?', agree: 1163, disagree: 2258, views: 18300 },
        { rank: 4, title: 'AI가 인간의 일자리를 대체하는 것을 막아야 하는가?', agree: 970, disagree: 1186, views: 8700 },
        { rank: 5, title: '부동산 양도소득세를 완화해야 하는가?', agree: 1222, disagree: 1621, views: 12100 }
    ],
    'TODAY 인기순위': [
        { rank: 1, title: '사형제도를 폐지해야 하는가?', agree: 5678, disagree: 6012, views: 28900 },
        { rank: 2, title: '재택근무를 법적으로 보장해야 하는가?', agree: 3210, disagree: 1590, views: 14500 },
        { rank: 3, title: '대학 입시에서 정시 비중을 늘려야 하는가?', agree: 1066, disagree: 501, views: 7800 },
        { rank: 4, title: '군 복무 기간을 단축해야 하는가?', agree: 2187, disagree: 513, views: 9400 },
        { rank: 5, title: '학교 체벌, 완전히 금지해야 하나?', agree: 1476, disagree: 416, views: 6300 }
    ],
    '주간 인기순위': [
        { rank: 1, title: '원자력 발전소를 더 늘려야 하는가?', agree: 8503, disagree: 8184, views: 45200 },
        { rank: 2, title: '공무원 연금을 개혁해야 하는가?', agree: 12340, disagree: 4560, views: 38600 },
        { rank: 3, title: '전기차 보조금을 계속 지급해야 하는가?', agree: 6330, disagree: 2590, views: 32100 },
        { rank: 4, title: '반려동물 등록제를 의무화해야 하는가?', agree: 10980, disagree: 1360, views: 28700 },
        { rank: 5, title: '택시 기본요금을 인상해야 하는가?', agree: 2870, disagree: 10130, views: 24300 }
    ],
    '월간 인기순위': [
        { rank: 1, title: '의대 정원 확대, 과연 필요한가?', agree: 42124, disagree: 31297, views: 152000 },
        { rank: 2, title: '부동산 양도소득세를 완화해야 하는가?', agree: 38222, disagree: 41621, views: 121000 },
        { rank: 3, title: '최저임금을 대폭 인상해야 하는가?', agree: 35570, disagree: 32750, views: 108000 },
        { rank: 4, title: '사형제도를 폐지해야 하는가?', agree: 28900, disagree: 31100, views: 95400 },
        { rank: 5, title: '온라인 투표로 대통령 선거를 진행해도 되는가?', agree: 21630, disagree: 42580, views: 87300 }
    ]
};

const sampleTopics = [
    {
        title: "부동산 양도소득세를 완화해야 하는가?",
        time: "3시간 전",
        author: "경제정책연구",
        agreePercent: 43,
        disagreePercent: 57,
        totalVotes: 2843,
        comments: 692,
        views: "12.1K",
        heat: "hot"
    },
    {
        title: "대학 입시에서 정시 비중을 늘려야 하는가?",
        time: "6시간 전",
        author: "교육평등실현",
        agreePercent: 68,
        disagreePercent: 32,
        totalVotes: 1567,
        comments: 423,
        views: "7.8K",
        heat: "warm"
    },
    {
        title: "전기차 보조금을 계속 지급해야 하는가?",
        time: "9시간 전",
        author: "그린모빌리티",
        agreePercent: 71,
        disagreePercent: 29,
        totalVotes: 892,
        comments: 234,
        views: "4.5K",
        heat: "normal"
    },
    {
        title: "온라인 투표로 대통령 선거를 진행해도 되는가?",
        time: "14시간 전",
        author: "디지털민주주의",
        agreePercent: 34,
        disagreePercent: 66,
        totalVotes: 3421,
        comments: 867,
        views: "18.3K",
        heat: "hot"
    },
    {
        title: "최저임금을 대폭 인상해야 하는가?",
        time: "18시간 전",
        author: "노동자권익",
        agreePercent: 52,
        disagreePercent: 48,
        totalVotes: 4532,
        comments: 1243,
        views: "21.7K",
        heat: "hot"
    }
];

function formatNumber(num) {
    if (num >= 1000) {
        return (num / 1000).toFixed(1) + 'K';
    }
    return num.toString();
}

function loadTrendingTopics() {
    const period = trendingPeriods[currentTrendingPeriod];
    const topics = trendingData[period];
    const trendingList = document.getElementById('trendingList');
    
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
    if (isLoading || !hasMoreData) return;
    
    isLoading = true;
    const loadingIndicator = document.getElementById('loadingIndicator');
    loadingIndicator.classList.add('active');
    
    setTimeout(() => {
        const topicsList = document.getElementById('topicsList');
        const itemsToLoad = 5;
        
        for (let i = 0; i < itemsToLoad; i++) {
            const randomTopic = sampleTopics[Math.floor(Math.random() * sampleTopics.length)];
            const modifiedTopic = {
                ...randomTopic,
                title: randomTopic.title.replace(/\?$/, '') + ' (더보기 ' + (currentPage * 5 + i + 1) + ')?',
                time: Math.floor(Math.random() * 24 + 1) + '시간 전',
                totalVotes: Math.floor(Math.random() * 5000 + 500),
                comments: Math.floor(Math.random() * 1000 + 50),
                views: (Math.random() * 20 + 1).toFixed(1) + 'K',
                agreePercent: Math.floor(Math.random() * 80 + 10),
                disagreePercent: 0
            };
            modifiedTopic.disagreePercent = 100 - modifiedTopic.agreePercent;
            
            topicsList.insertAdjacentHTML('beforeend', createTopicElement(modifiedTopic));
        }
        
        currentPage++;
        isLoading = false;
        loadingIndicator.classList.remove('active');
        
        if (currentPage > 10) {
            hasMoreData = false;
        }
    }, 1000);
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
            console.log('토론 상세 페이지로 이동');
        });
    });
    
    document.querySelector('.create-topic-btn').addEventListener('click', function() {
        console.log('새 토론 만들기');
    });
    
    document.querySelector('.btn-login').addEventListener('click', function() {
        console.log('로그인 페이지로 이동');
    });
    
    document.querySelector('.btn-signup').addEventListener('click', function() {
        console.log('회원가입 페이지로 이동');
    });
    
    document.querySelector('.search-btn').addEventListener('click', function() {
        const searchValue = document.querySelector('.search-input').value;
        if (searchValue) {
            console.log('검색어:', searchValue);
        }
    });
    
    document.querySelector('.search-input').addEventListener('keypress', function(e) {
        if (e.key === 'Enter') {
            const searchValue = this.value;
            if (searchValue) {
                console.log('검색어:', searchValue);
            }
        }
    });
});