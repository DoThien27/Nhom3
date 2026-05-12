window._currentUser = null;
window._currentPage = null;

window.ROLE_MENU = {
  ADMIN: ['dashboard','members','member_cards','checkin','trainers','trainer_attendance','trainer_salary','sports','classes','facilities','events','plans','billing','reports','system_users'],
  PT:    ['dashboard','members','checkin','sports','classes','facilities','events','billing','reports'],
};

window.MENU_CONFIG = {
  dashboard:         { label:'Tổng quan', icon:'layout-dashboard' },
  members:           { label:'Hội viên', icon:'users' },
  member_cards:      { label:'Thẻ hội viên', icon:'credit-card' },
  checkin:           { label:'Check-in / Check-out', icon:'log-in' },
  trainers:          { label:'Danh sách HLV', icon:'award' },
  trainer_attendance:{ label:'Chấm công HLV', icon:'clipboard-list' },
  trainer_salary:    { label:'Tính lương HLV', icon:'wallet' },
  sports:            { label:'Môn thể thao', icon:'trophy' },
  classes:           { label:'Lớp/Buổi tập', icon:'activity' },
  facilities:        { label:'Sân bãi', icon:'map-pin' },
  events:            { label:'Sự kiện', icon:'calendar-days' },
  plans:             { label:'Gói tập', icon:'package' },
  billing:           { label:'Tài chính', icon:'banknote' },
  reports:           { label:'Báo cáo', icon:'bar-chart-3' },
  system_users:      { label:'Tài khoản hệ thống', icon:'settings' },
};

window.MENU_GROUPS = [
  { key: 'dashboard_group', label: 'Tổng quan', icon: 'layout-dashboard', items: ['dashboard'] },
  { key: 'member_group', label: 'Quản lý Hội viên', icon: 'users', items: ['members', 'member_cards', 'checkin'] },
  { key: 'trainer_group', label: 'Huấn luyện viên', icon: 'award', items: ['trainers', 'trainer_attendance', 'trainer_salary'] },
  { key: 'service_group', label: 'Dịch vụ & Cơ sở', icon: 'activity', items: ['sports', 'classes', 'plans', 'facilities', 'events'] },
  { key: 'system_group', label: 'Hệ thống & Báo cáo', icon: 'settings', items: ['billing', 'reports', 'system_users'] }
];

window.handleLogin = async function(e) {
  e.preventDefault();
  const btn = document.getElementById('login-btn');
  btn.disabled = true;
  document.getElementById('login-spinner').classList.remove('hidden');
  document.getElementById('login-btn-text').classList.add('invisible');

  try {
    const res = await API.post('/auth/login', { 
      username: document.getElementById('login-username').value, 
      password: document.getElementById('login-password').value 
    });

    if (res.success) { 
      window._currentUser = res.user; 
      showMainApp(); 
      showToast('Chào mừng quay trở lại!', 'success'); 
    } else { 
      const err = document.getElementById('login-error'); 
      err.textContent = res.message; 
      err.classList.remove('hidden'); 
    }
  } catch(err) {
    showToast('Lỗi kết nối máy chủ', 'error');
  } finally {
    btn.disabled = false;
    document.getElementById('login-spinner').classList.add('hidden');
    document.getElementById('login-btn-text').classList.remove('invisible');
  }
};

window.showLoginPage = function() { 
  document.getElementById('login-page').classList.remove('hidden'); 
  document.getElementById('main-app').classList.add('hidden'); 
};

window.showMainApp = function() {
  document.getElementById('login-page').classList.add('hidden'); 
  document.getElementById('main-app').classList.remove('hidden');
  buildSidebar(); 
  updateUserPanel();
  const pages = ROLE_MENU[_currentUser.role] || [];
  if (pages.length) navigate(pages[0]);
};

window.buildSidebar = function() {
  const nav = document.getElementById('sidebar-nav'); nav.innerHTML = '';
  const allowedPages = window.ROLE_MENU[_currentUser.role] || [];
  
  window.MENU_GROUPS.forEach(group => {
    const visibleItems = group.items.filter(k => allowedPages.includes(k));
    if (visibleItems.length === 0) return;
    
    if (group.items.length === 1 && group.key === 'dashboard_group') {
      const key = group.items[0];
      const cfg = MENU_CONFIG[key];
      const el = document.createElement('div');
      el.className = 'nav-item flex items-center gap-3 px-4 py-3.5 rounded-xl text-slate-400 hover:text-white hover:bg-slate-800/50 cursor-pointer transition-all group';
      el.id = `nav-${key}`; 
      el.innerHTML = `<i data-lucide="${group.icon}" class="w-5 h-5 transition-transform group-hover:scale-110"></i><span class="font-medium nav-label">${cfg.label}</span>`;
      el.onclick = () => navigate(key); 
      nav.appendChild(el);
      return;
    }
    
    const groupEl = document.createElement('div');
    groupEl.className = 'mb-2 group/menu';
    
    const headerEl = document.createElement('div');
    headerEl.className = 'flex items-center justify-between px-4 py-3 rounded-xl text-slate-400 hover:text-white hover:bg-slate-800/30 cursor-pointer transition-all';
    headerEl.innerHTML = `
      <div class="flex items-center gap-3">
        <i data-lucide="${group.icon}" class="w-5 h-5 transition-transform group-hover/menu:scale-110"></i>
        <span class="font-bold nav-label text-[11px] uppercase tracking-wider group-hover/menu:text-white transition-colors">${group.label}</span>
      </div>
    `;
    
    const childrenEl = document.createElement('div');
    childrenEl.className = 'pl-11 pr-2 space-y-1 mt-1 overflow-hidden transition-all duration-300 max-h-0 opacity-0 group-hover/menu:max-h-[500px] group-hover/menu:opacity-100';
    
    visibleItems.forEach(key => {
      const cfg = MENU_CONFIG[key];
      const childEl = document.createElement('div');
      childEl.className = 'nav-item flex items-center gap-3 px-4 py-2.5 rounded-xl text-sm text-slate-400 hover:text-white hover:bg-slate-800/50 cursor-pointer transition-all';
      childEl.id = `nav-${key}`; 
      childEl.innerHTML = `<span class="font-medium nav-label">${cfg.label}</span>`;
      childEl.onclick = (e) => { e.stopPropagation(); navigate(key); };
      childrenEl.appendChild(childEl);
    });
    
    groupEl.appendChild(headerEl);
    groupEl.appendChild(childrenEl);
    nav.appendChild(groupEl);
  });
  
  lucide.createIcons({ nodes: [nav] });
};

window.navigate = function(page) {
  window._currentPage = page;
  
  const searchInput = document.getElementById('global-search');
  if (searchInput) searchInput.value = '';

  document.querySelectorAll('.nav-item').forEach(el => el.classList.remove('sidebar-item-active','text-white'));
  document.querySelectorAll('.group\\/menu > div:nth-child(2)').forEach(el => {
    el.classList.remove('!max-h-[500px]', '!opacity-100');
  });
  document.querySelectorAll('.group\\/menu > div:first-child span').forEach(el => {
    el.classList.remove('!text-white');
  });

  const activeItem = document.getElementById(`nav-${page}`);
  if (activeItem) {
    activeItem.classList.add('sidebar-item-active','text-white');
    const groupEl = activeItem.closest('.group\\/menu');
    if (groupEl) {
      const childrenEl = groupEl.lastElementChild;
      if (childrenEl) {
        childrenEl.classList.add('!max-h-[500px]', '!opacity-100');
      }
      const headerSpan = groupEl.querySelector('div:first-child span');
      if (headerSpan) {
        headerSpan.classList.add('!text-white');
      }
    }
  }

  document.getElementById('page-title').textContent = MENU_CONFIG[page]?.label || page;
  const content = document.getElementById('page-content'); 
  content.innerHTML = '<div class="flex justify-center p-20 page-enter"><div class="spinner"></div></div>';
  
  if (window.PAGE_RENDERERS && window.PAGE_RENDERERS[page]) {
    window.PAGE_RENDERERS[page](content);
  } else {
    content.innerHTML = `<div class="p-20 text-center text-slate-500">Trang ${page} đang được phát triển hoặc thiếu Renderer.</div>`;
  }
};

window.updateUserPanel = function() {
  document.getElementById('user-name').textContent = _currentUser.fullName;
  const roleMap = { ADMIN: 'Quản trị viên', PT: 'Huấn luyện viên' };
  document.getElementById('user-role').textContent = roleMap[_currentUser.role] || _currentUser.role;
  document.getElementById('user-avatar').textContent = (_currentUser.fullName||'A')[0].toUpperCase();
  // Live clock
  function updateClock() {
    const now = new Date();
    const opts = { weekday:'long', year:'numeric', month:'long', day:'numeric' };
    const el = document.getElementById('current-date');
    if (el) el.textContent = now.toLocaleDateString('vi-VN', opts);
  }
  updateClock();
  if (window._clockInterval) clearInterval(window._clockInterval);
  window._clockInterval = setInterval(updateClock, 60000);
};

window.initApp = async function() {
  try {
    const res = await API.get('/auth/me');
    if (res.success) { window._currentUser = res.user; showMainApp(); } else showLoginPage();
  } catch(e) { showLoginPage(); }
};

window._appLogout = () => { window._currentUser = null; showLoginPage(); closeLogoutModal(); };
