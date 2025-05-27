import { attachLoginFormHandler } from './login.js';
import { attachSignupFormHandler } from './signup.js';
import { setupLandlordFunctions, loadHousesList, houseTypeMap, editHouse } from './landlord.js';

const contentMap = {
    homeLink: `<section class="search-section">
                    <h3>找房子</h3>
                    <form id="searchForm">
                        <label>城市：</label>
                        <select id="citySelect" name="city">
                            <option value="">全部</option>
                            <option value="新竹市">新竹市</option>
                            <option value="新竹縣">新竹縣</option>
                        </select>
                        <label>行政區：</label>
                        <select id="districtSelect" name="district">
                            <option value="">全部</option>
                        </select>
                        <button type="submit">搜尋</button>
                        <button type="button" id="resetBtn">重設</button>
                    </form>
                </section>
                <section class="listings-section">
                    <h3>房屋推薦</h3>
                    <div class="listing-grid"></div>
                    <div class="pagination"></div>
                </section>`,
    loginLink: `<h1>登入</h1>
                <form id="loginForm">
                    <label>帳號：</label><br>
                    <input type="text" id="username" required><br><br>
                    <label>密碼：</label><br>
                    <input type="password" id="password" required><br><br>
                    <button type="submit">登入</button>
                </form>`,
    signupLink: `<h1>註冊</h1>
                <form id="signupForm">
                    <div id="step1">
                        <label>帳號：</label><br>
                        <input type="text" id="username_signup" required><br><br>
                        <label>密碼：</label><br>
                        <input type="password" id="password_signup" required><br><br>
                        <label>確認密碼：</label><br>
                        <input type="password" id="confirmPassword_signup" required><br><br>
                        <button type="button" id="nextStepBtn">下一步</button>
                    </div>
                    <div id="detailFields" style="display:none">
                        <label>姓氏：</label><br>
                        <input type="text" id="lastName_signup" required><br><br>
                        <label>名字：</label><br>
                        <input type="text" id="firstName_signup" required><br><br>
                        <label>暱稱：</label><br>
                        <input type="text" id="nickname_signup"><br><br>
                        <label>地址：</label><br>
                        <input type="text" id="address_signup"><br><br>
                        <label>信箱：</label><br>
                        <input type="email" id="email_signup" required><br><br>
                        <label>腳色：</label><br>
                        <select id="role_signup" required>
                            <option value="">請選擇</option>
                            <option value="tenant">租客</option>
                            <option value="landlord">房東</option>
                        </select><br><br>
                        <label>頭像：</label><br>
                        <input type="file" id="avatar_signup" accept="image/*"><br><br>
                        <button type="submit">送出註冊</button>
                    </div>
                </form>`,
    tenantLink: `<h2>租客專區</h2>
        <button id="logoutBtn">登出</button>`,
    landlordLink: `
    <h2>房東專區</h2>
        <div class="house-management">
            <h3>房屋管理</h3>
            <button id="addHouseBtn" class="add-house-btn">
                <span class="plus-icon">+</span>
                新增房屋
            </button>
            <div id="housesList" class="houses-list">
                <!-- 房屋列表將動態載入 -->
            </div>
        </div>
        
        <!-- 新增房屋表單（預設隱藏） -->
        <div id="addHouseModal" class="modal" style="display:none;">
            <div class="modal-content">
                <span class="close">&times;</span>
                <h3>新增房屋</h3>
                <form id="addHouseForm" enctype="multipart/form-data">
                    <label>房屋名稱*：</label>
                    <input type="text" id="houseName" name="house_title" required><br><br>
                    <label>城市*：</label>
                    <select id="city" name="city" required>
                        <option value="">請選擇城市</option>
                        <option value="新竹市">新竹市</option>
                        <option value="新竹縣">新竹縣</option>
                    </select><br><br>
                    <label>行政區*：</label>
                    <select id="district" name="district" required>
                        <option value="">請先選擇城市</option>
                    </select><br><br>
                    <label>道路*：</label>
                    <input type="text" id="road" name="road"><br><br>
                    <label>巷：</label>
                    <input type="text" id="lane" name="lane"><br><br>
                    <label>弄：</label>
                    <input type="text" id="alley" name="alley"><br><br>
                    <label>號：</label>
                    <input type="text" id="number" name="number"><br><br>
                    <label>郵遞區號：</label>
                    <input type="text" id="zip_code" name="zip_code"><br><br>
                    <label>租金/月：</label>
                    <input type="number" id="price_per_month" name="price_per_month" required><br><br>
                    <label>房屋類型：</label>
                    <select id="house_type" name="house_type" required>
                        <option value="APARTMENT">公寓</option>
                        <option value="SUITE">套房</option>
                        <option value="ROOM">雅房</option>
                        <option value="HOUSE">獨棟</option>
                        <option value="OTHER">其它</option>
                    </select><br><br>
                    <label>房屋狀態：</label>
                    <select id="house_status" name="house_status" required>
                        <option value="DRAFT">草稿</option>
                        <option value="PUBLISHED">發布</option>
                        <option value="RENTED">已出租</option>
                        <option value="OFFLINE">下架</option>
                        <option value="ARCHIVED">典藏</option>
                    </select><br><br>
                    <label>房屋描述：</label>
                    <textarea id="houseDescription" name="house_desc" rows="3"></textarea><br><br>
                    <label>上傳照片：</label>
                    <input type="file" id="media_list" name="media_list" accept="image/*" multiple><br><br>
                    <button type="submit">送出</button>
                    <button type="button" id="cancelBtn">取消</button>
                </form>
            </div>
        </div>
        
        <button id="logoutBtn">登出</button>`
};

export function setContent(contentId) {
    const mainContent = document.getElementById('mainContent');
    mainContent.innerHTML = contentMap[contentId] || ''; // 找不到就顯示空
    // 判斷是否需要綁定事件
    if (contentId === 'homeLink') {
        setTimeout(() => {
            loadHomeHouses();
            // 城市-行政區對應
            const districtMap = {
                "新竹市": ["東區", "北區", "香山區"],
                "新竹縣": ["竹北市", "湖口鄉", "新豐鄉", "新埔鎮", "關西鎮", "芎林鄉", "寶山鄉", "竹東鎮", "五峰鄉", "橫山鄉", "尖石鄉", "北埔鄉", "峨眉鄉"]
            };
            const citySelect = document.getElementById('citySelect');
            const districtSelect = document.getElementById('districtSelect');
            if (citySelect && districtSelect) {
                citySelect.addEventListener('change', () => {
                    const city = citySelect.value;
                    districtSelect.innerHTML = '<option value="">全部</option>';
                    if (districtMap[city]) {
                        districtMap[city].forEach(d => {
                            districtSelect.innerHTML += `<option value="${d}">${d}</option>`;
                        });
                    }
                });
            }
            // 搜尋
            const searchForm = document.getElementById('searchForm');
            if (searchForm) {
                searchForm.addEventListener('submit', function(e) {
                    e.preventDefault();
                    loadHomeHouses(1); // 搜尋時回到第1頁
                });
            }
            // 重設
            const resetBtn = document.getElementById('resetBtn');
            if (resetBtn) {
                resetBtn.onclick = () => {
                    citySelect.value = '';
                    districtSelect.innerHTML = '<option value="">全部</option>';
                    loadHomeHouses(1);
                };
            }
        }, 0);
    }
    if (contentId === 'loginLink') attachLoginFormHandler();
    if (contentId === 'signupLink') attachSignupFormHandler();
    if (contentId === 'tenantLink' || contentId === 'landlordLink') {
        document.getElementById('logoutBtn').onclick = () => window.location.href = '/logout';
    }

    // 房東專區特殊處理
    if (contentId === 'landlordLink') {
        setupLandlordFunctions();
        loadHousesList(); // 載入房屋列表
    }
}

export async function loadHomeHouses(page = 1) {
    const grid = document.querySelector('.listing-grid');
    const pagination = document.querySelector('.pagination');
    if (!grid) return;
    grid.innerHTML = '<p>載入中...</p>';
    pagination.innerHTML = '';
    const city = document.getElementById('citySelect')?.value || '';
    const district = document.getElementById('districtSelect')?.value || '';
    const pageSize = 6;
    let url = `/api/home_houses?page=${page}&page_size=${pageSize}`;
    if (city) url += `&city=${encodeURIComponent(city)}`;
    if (district) url += `&district=${encodeURIComponent(district)}`;
    try {
        const res = await fetch(url);
        const { houses, total } = await res.json();
        if (!houses.length) {
            grid.innerHTML = '<p>目前尚無房屋</p>';
            return;
        }
        grid.innerHTML = houses.map(house => `
            <a href="/house/${house.house_id}" class="listing-item" target="_blank">
            <img src="${house.main_image_url}" alt="房屋圖片">
                <div class="listing-info">
                    <h4>${house.house_title}</h4>
                    <p>地點：${house.address ? house.address.full_address : ''}</p>
                    <p>價格：$${house.price_per_month}/月</p>
                    <p>類型：${houseTypeMap[house.house_type] || house.house_type}</p>
                </div>
            </a>
        `).join('');
        // 分頁
        const totalPages = Math.ceil(total / pageSize);
        if (totalPages > 1) {
            pagination.innerHTML = Array.from({length: totalPages}, (_, i) => `
                <button class="page-btn${i+1 === page ? ' active' : ''}" data-page="${i+1}">${i+1}</button>
            `).join('');
            pagination.querySelectorAll('.page-btn').forEach(btn => {
                btn.onclick = () => loadHomeHouses(Number(btn.dataset.page));
            });
        }
    } catch (e) {
        grid.innerHTML = '<p>載入失敗</p>';
    }
}

export function setHomeContent() {
    setContent('homeLink');
    setTimeout(loadHomeHouses, 0); // 等 DOM 渲染完再載入
}

export function setLoginContent() {
    setContent('loginLink');
}

export function setSignupContent() {
    setContent('signupLink');
}

export function setTenantContent() {
    setContent('tenantLink');
}

export function setLandlordContent() {
    setContent('landlordLink');
}