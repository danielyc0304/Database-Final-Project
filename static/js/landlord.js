const districtMap = {
    "新竹市": ["東區", "北區", "香山區"],
    "新竹縣": ["竹北市", "湖口鄉", "新豐鄉", "新埔鎮", "關西鎮", "芎林鄉", "寶山鄉", "竹東鎮", "五峰鄉", "橫山鄉", "尖石鄉", "北埔鄉", "峨眉鄉"]
};

async function uploadImages(files) {
    const uploaded = [];
    for (let i = 0; i < files.length; i++) {
        const file = files[i];
        const filename = `house_${Date.now()}_${i}_${file.name}`;
        // 用 fetch 上傳到 Supabase Storage API
        const { data, error } = await supabase.storage.from('dbfinal-housemedia').upload(filename, file);
        if (!error) {
            const url = supabase.storage.from('dbfinal-housemedia').getPublicUrl(filename).data.publicUrl;
            uploaded.push({
                media_type: 'Image',
                media_url: url,
                thumbnail_url: url, // 可用同一張，或之後做縮圖
                order_index: i
            });
        }
    }
    return uploaded;
}

export function setupLandlordFunctions() {
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

    // 城市-行政區聯動
    const citySelect = document.getElementById('city');
    const districtSelect = document.getElementById('district');
    if (citySelect && districtSelect) {
        citySelect.addEventListener('change', () => {
            const city = citySelect.value;
            districtSelect.innerHTML = '<option value="">請選擇行政區</option>';
            if (districtMap[city]) {
                districtMap[city].forEach(d => {
                    districtSelect.innerHTML += `<option value="${d}">${d}</option>`;
                });
            }
        });
    }

    // 表單送出
    form.onsubmit = async (e) => {
        e.preventDefault();
        
        const formData = new FormData(form);
        const response = await fetch('/api/houses', {
            method: 'POST',
            body: formData
        });
        if (response.ok) {
            alert('房屋新增成功！');
            modal.style.display = 'none';
            form.reset();
            loadHousesList();
        } else {
            const error = await response.json();
            alert(error.error || '新增失敗');
        }
    };
}

// 類型對應表
export const houseTypeMap = {
    APARTMENT: '公寓',
    SUITE: '套房',
    ROOM: '雅房',
    HOUSE: '獨棟',
    OTHER: '其它'
};

// 載入房屋列表
export async function loadHousesList() {
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
                    <div class="house-media-list">
                        ${house.media_list && house.media_list.length
                            ? house.media_list.map(media => `<img src="${media.media_url}" alt="房屋圖片" class="house-thumb">`).join('')
                            : `<img src="${house.main_image_url}" alt="房屋主圖" class="house-thumb">`
                        }
                    </div>
                    <p>地址：${house.address ? house.address.full_address : ''}</p>
                    <p>租金：$${house.price_per_month}/月</p>
                    <p>類型：${houseTypeMap[house.house_type]}</p>
                    <button class="edit-house-btn">編輯</button>
                    <button class="delete-house-btn">刪除</button>
                </div>
            `).join('');
            
            // Add event listeners for edit and delete buttons
            housesList.querySelectorAll('.edit-house-btn').forEach((btn, idx) => {
                btn.addEventListener('click', () => editHouse(houses[idx].house_id));
            });
            housesList.querySelectorAll('.delete-house-btn').forEach((btn, idx) => {
                btn.addEventListener('click', () => deleteHouse(houses[idx].house_id));
            });
        }
    } catch (error) {
        housesList.innerHTML = '<p class="error">載入失敗</p>';
    }
}

// 編輯房屋
export async function editHouse(houseId) {
    const response = await fetch(`/api/houses/${houseId}`);
    if (!response.ok) {
        alert('載入房屋資料失敗');
        return;
    }
    const house = await response.json();
    
    // 填充表單
    document.getElementById('houseName').value = house.house_title;
    document.getElementById('city').value = house.address.city;
    // 觸發城市選單的 change 事件，讓行政區選單刷新
    document.getElementById('city').dispatchEvent(new Event('change'));

    // 等行政區選單刷新後再設值
    setTimeout(() => {
        document.getElementById('district').value = house.address.distrit;
    }, 0);
    //document.getElementById('district').value = house.address.distrit;
    document.getElementById('road').value = house.address.road || '';
    document.getElementById('lane').value = house.address.lane || '';
    document.getElementById('alley').value = house.address.alley || '';
    document.getElementById('number').value = house.address.number || '';
    document.getElementById('zip_code').value = house.address.zip_code || '';
    document.getElementById('houseDescription').value = house.house_desc;
    document.getElementById('price_per_month').value = house.price_per_month;
    document.getElementById('house_type').value = house.house_type;
    document.getElementById('house_status').value = house.house_status;

    // 顯示表單
    const modal = document.getElementById('addHouseModal');
    modal.style.display = 'block';

    // 更新表單標題
    const modalTitle = modal.querySelector('h3');
    modalTitle.textContent = '編輯房屋';
    // 更新表單提交按鈕
    const submitBtn = modal.querySelector('button[type="submit"]');
    submitBtn.textContent = '更新房屋';

    // 更新表單提交事件
    const closeBtn = document.querySelector('.close');
    const cancelBtn = document.getElementById('cancelBtn');
    closeBtn.onclick = cancelBtn.onclick = () => {
        modal.style.display = 'none';
        document.getElementById('addHouseForm').reset();
    }
    const form = document.getElementById('addHouseForm');
    form.onsubmit = async (e) => {
        e.preventDefault();

        form.onsubmit = async (e) => {
            e.preventDefault();
            const formData = new FormData(form);
            const response = await fetch(`/api/houses/${houseId}`, {
                method: 'PUT', // 或 'PUT'，依你的後端設計
                body: formData
            });
            if (response.ok) {
                alert('房屋更新成功！');
                modal.style.display = 'none';
                form.reset();
                loadHousesList();
            } else {
                const error = await response.json();
                alert(error.error || '更新失敗');
            }
        };
    }
}
