import { showFormMessage } from './formMessage.js';
import { setupSidebar } from './sidebar.js';
import { setTenantContent, setLandlordContent } from './mainContent.js';

export function attachLoginFormHandler() {
    const form = document.getElementById('loginForm');
    form.addEventListener('submit', async (e) => {
        e.preventDefault();
        const username = document.getElementById('username').value;
        const password = document.getElementById('password').value;

        const response = await fetch('/api/login', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ username, password }),
        });

        const result = await response.json();
        if (response.ok) {
            showFormMessage(form, `你好，${username}！登入成功`, 'green');
            // 根據角色切換 sidebar 與內容
            setupSidebar(result.role);
            if (result.role === 'Tenant') {
                setupSidebar('Tenant');
                setTenantContent();
            } else if (result.role === 'Landlord') {
                setupSidebar('Landlord');
                setLandlordContent();
            }
        } else {
            showFormMessage(form, result.error, 'red');
            document.getElementById('password').value = '';
        }
    });
}