import { setupSidebar } from './sidebar.js';
import { setContent } from './mainContent.js';

document.addEventListener('DOMContentLoaded', () => {
    setContent('homeLink'); // 初始載入時設定首頁內容
    setupSidebar();
});