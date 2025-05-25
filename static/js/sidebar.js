import { setContent } from './mainContent.js';

export function setupSidebar(userRole = null) {
    const sidebar = document.querySelector('.sidebar nav ul');
    // 根據登入狀態與角色渲染 sidebar
    if (userRole === 'Tenant') {
        sidebar.innerHTML = `
            <li><a href="#" id="homeLink">首頁</a></li>
            <li><a href="#" id="tenantLink" class="active">租客專區</a></li>
        `;
    } else if (userRole === 'Landlord') {
        sidebar.innerHTML = `
            <li><a href="#" id="homeLink">首頁</a></li>
            <li><a href="#" id="landlordLink" class="active">房東專區</a></li>
        `;
    } else {
        sidebar.innerHTML = `
            <li><a href="#" id="homeLink" class="active">首頁</a></li>
            <li><a href="#" id="loginLink">登入</a></li>
            <li><a href="#" id="signupLink">註冊</a></li>
        `;
    }

    // 綁定事件
    sidebar.querySelectorAll('a').forEach(link => {
        link.addEventListener('click', (e) => {
            e.preventDefault();
            sidebar.querySelectorAll('a').forEach(l => l.classList.remove('active'));
            link.classList.add('active');
            setContent(link.id); // 呼叫 setContent
        });
    });
}