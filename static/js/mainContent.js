import { attachLoginFormHandler } from './login.js';
import { attachSignupFormHandler } from './signup.js';

const contentMap = {
    homeLink: `<section class="search-section">
                    <h3>找房子</h3>
                    <form action="/search" method="get">
                        <input type="text" name="query" placeholder="輸入地區、類型或關鍵字...">
                        <button type="submit">搜尋</button>
                    </form>
                </section>

                <section class="listings-section">
                    <h3>房屋推薦</h3>
                    <div class="listing-grid">
                        <a href="/listing/123" class="listing-item">
                            <img src="placeholder-house1.jpg" alt="房屋圖片1">
                            <h4>市中心溫馨套房</h4>
                            <p>地點：台北市大安區</p>
                            <p>價格：$15,000/月</p>
                            <p>類型：套房</p>
                        </a>

                        <a href="/listing/124" class="listing-item">
                            <img src="placeholder-house2.jpg" alt="房屋圖片2">
                            <h4>近捷運三房兩廳</h4>
                            <p>地點：新北市板橋區</p>
                            <p>價格：$30,000/月</p>
                            <p>類型：整層住家</p>
                        </a>

                            <a href="/listing/125" class="listing-item">
                            <img src="placeholder-house3.jpg" alt="房屋圖片3">
                            <h4>淡水河景小豪宅</h4>
                            <p>地點：新北市淡水區</p>
                            <p>價格：$45,000/月</p>
                            <p>類型：華廈/大樓</p>
                        </a>

                        </div>
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
                <form id="addHouseForm">
                    <label>房屋名稱：</label>
                    <input type="text" id="houseName" required><br><br>
                    <label>城市：</label>
                    <input type="text" id="city" required><br><br>
                    <label>行政區：</label>
                    <input type="text" id="district" required><br><br>
                    <label>道路：</label>
                    <input type="text" id="road"><br><br>
                    <label>巷：</label>
                    <input type="text" id="lane"><br><br>
                    <label>弄：</label>
                    <input type="text" id="alley"><br><br>
                    <label>號：</label>
                    <input type="text" id="number"><br><br>
                    <label>郵遞區號：</label>
                    <input type="text" id="zip_code"><br><br>
                    <label>租金/月：</label>
                    <input type="number" id="price_per_month" required><br><br>
                    <label>房屋類型：</label>
                    <select id="house_type" required>
                        <option value="APARTMENT">APARTMENT</option>
                        <option value="SUITE">SUITE</option>
                        <option value="ROOM">ROOM</option>
                        <option value="HOUSE">HOUSE</option>
                        <option value="OTHER">OTHER</option>
                    </select><br><br>
                    <label>房屋狀態：</label>
                    <select id="house_status" required>
                        <option value="DRAFT">DRAFT</option>
                        <option value="PUBLISHED">PUBLISHED</option>
                        <option value="RENTED">RENTED</option>
                        <option value="OFFLINE">OFFLINE</option>
                        <option value="ARCHIVED">ARCHIVED</option>
                    </select><br><br>
                    <label>房屋描述：</label>
                    <textarea id="houseDescription" rows="3"></textarea><br><br>
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

function setupLandlordFunctions() {
    const addHouseBtn = document.getElementById('addHouseBtn');
    const modal = document.getElementById('addHouseModal');
    const closeBtn = document.querySelector('.close');
    const cancelBtn = document.getElementById('cancelBtn');
    const form = document.getElementById('addHouseForm');

    // 顯示新增房屋表單
    addHouseBtn.onclick = () => {
        modal.style.display = 'block';
    };

    // 關閉表單
    closeBtn.onclick = cancelBtn.onclick = () => {
        modal.style.display = 'none';
        form.reset();
    };

    // 點擊背景關閉
    window.onclick = (e) => {
        if (e.target === modal) {
            modal.style.display = 'none';
            form.reset();
        }
    };

    // 表單送出
    form.onsubmit = async (e) => {
        e.preventDefault();

        const formData = {
            country: document.getElementById('country').value,
            city: document.getElementById('city').value,
            district: document.getElementById('district').value,
            road: document.getElementById('road').value,
            lane: document.getElementById('lane').value,
            alley: document.getElementById('alley').value,
            number: document.getElementById('number').value,
            zip_code: document.getElementById('zip_code').value,
            full_address: document.getElementById('full_address').value,
            house_title: document.getElementById('houseName').value,
            house_desc: document.getElementById('houseDescription').value,
            //house_price: document.getElementById('house_price').value,
            //house_area: document.getElementById('house_area').value,
            //house_floor: document.getElementById('house_floor').value,
            house_type: document.getElementById('house_type').value,
            house_status: document.getElementById('house_status').value,
            price_per_month: document.getElementById('price_per_month').value
            //max_months: document.getElementById('max_months').value
            //media_list: JSON.parse(document.getElementById('media_list').value || '[]')
        };

        const response = await fetch('/api/houses', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify(formData)
        });

        if (response.ok) {
            alert('房屋新增成功！');
            modal.style.display = 'none';
            form.reset();
            loadHousesList(); // 重新載入列表
        } else {
            const error = await response.json();
            alert(error.error || '新增失敗');
        }
    };
}

// 載入房屋列表
async function loadHousesList() {
    const housesList = document.getElementById('housesList');
    try {
        const response = await fetch('/api/houses');
        const houses = await response.json();
        
        if (houses.length === 0) {
            housesList.innerHTML = '<p class="no-houses">目前尚無房屋</p>';
        } else {
            housesList.innerHTML = houses.map(house => `
                <div class="house-item">
                    <h4>${house.house_title}</h4>
                    <p>地址：${house.address ? house.address.full_address : ''}</p>
                    <p>租金：$${house.price_per_month}/月</p>
                    <p>類型：${house.house_type}</p>
                    <button onclick="editHouse(${house.house_id})">編輯</button>
                    <button onclick="deleteHouse(${house.house_id})">刪除</button>
                </div>
            `).join('');
        }
    } catch (error) {
        housesList.innerHTML = '<p class="error">載入失敗</p>';
    }
}

export function setHomeContent() {
    setContent('homeLink');
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