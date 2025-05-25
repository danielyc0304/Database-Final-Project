import { showFormMessage } from './formMessage.js';

export function attachSignupFormHandler() {
    const form = document.getElementById('signupForm');
    const nextStepBtn = document.getElementById('nextStepBtn');

    nextStepBtn.addEventListener('click', async function () {
        const username = document.getElementById('username_signup').value.trim();
        const password = document.getElementById('password_signup').value;
        const confirmPassword = document.getElementById('confirmPassword_signup').value;

        // 檢查必填
        if (!username || !password || !confirmPassword) {
            showFormMessage(form, '請完整填寫帳號與密碼', 'red');
            return;
        }
        // 檢查密碼一致
        if (password !== confirmPassword) {
            showFormMessage(form, '密碼與確認密碼不一致！', 'red');
            document.getElementById('password_signup').value = '';
            document.getElementById('confirmPassword_signup').value = '';
            return;
        }
        // 檢查帳號是否存在
        const res = await fetch('/api/check_username', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ username })
        });
        const result = await res.json();
        if (result.exists) {
            showFormMessage(form, '帳號已存在，請換一個', 'red');
            return;
        }

        // 儲存目前帳密資料
        const step1HTML = form.innerHTML;

        // 換成詳細資料畫面，並加上「上一步」按鈕
        form.innerHTML = `
            <button type="button" id="prevStepBtn">上一步</button>
            <input type="hidden" id="username_signup" value="${username}">
            <input type="hidden" id="password_signup" value="${password}">
            <input type="hidden" id="confirmPassword_signup" value="${confirmPassword}">
            <h2>填寫詳細資料</h2>
            <p>*為必填</p> <!--紅字-->
            <label>姓氏*：</label><br>
            <input type="text" id="lastName_signup" required><br><br>
            <label>名字*：</label><br>
            <input type="text" id="firstName_signup" required><br><br>
            <label>暱稱*：</label><br>
            <input type="text" id="nickname_signup"><br><br>
            <label>信箱：</label><br>
            <input type="email" id="email_signup" required><br><br>
            <label>腳色*：</label><br>
            <select id="role_signup" required>
                <option value="">請選擇</option>
                <option value="Tenant">租客</option>
                <option value="Landlord">房東</option>
            </select><br><br>
            <label>頭像：</label><br>
            <input type="file" id="avatar_signup" accept="image/*"><br><br>
            <button type="submit">送出註冊</button>
        `;

        // 綁定「上一步」按鈕
        document.getElementById('prevStepBtn').addEventListener('click', function () {
            form.innerHTML = step1HTML;
            attachSignupFormHandler(); // 重新綁定事件
            // 填回原本的帳密
            document.getElementById('username_signup').value = username;
            document.getElementById('password_signup').value = password;
            document.getElementById('confirmPassword_signup').value = confirmPassword;
        });

        // 綁定送出註冊事件
        form.addEventListener('submit', async (e) => {
            e.preventDefault();
            const lastName = document.getElementById('lastName_signup').value;
            const firstName = document.getElementById('firstName_signup').value;
            const nickname = document.getElementById('nickname_signup').value;
            const email = document.getElementById('email_signup').value;
            const role = document.getElementById('role_signup').value;
            const avatar = document.getElementById('avatar_signup').files[0];

            // 檢查必填
            if (!lastName || !firstName || !nickname || !role) {
                showFormMessage(form, '請完整填寫所有必填欄位', 'red');
                return;
            }

            const formData = new FormData();
            formData.append('account', username);
            formData.append('password', password);
            formData.append('last_name', lastName);
            formData.append('first_name', firstName);
            formData.append('nickname', nickname);
            formData.append('email', email);
            formData.append('role', role);
            if (avatar) formData.append('avatar', avatar);

            const response = await fetch('/api/signup', {
                method: 'POST',
                body: formData,
            });

            const result = await response.json();
            if (response.ok) {
                form.innerHTML = `
                    <p>註冊成功，請登入您的帳號</p>
                `;
                //showFormMessage(form, '註冊成功，請登入', 'green');
                form.reset();
            } else {
                showFormMessage(form, result.error, 'red');
            }
        });
    });
}