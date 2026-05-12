window.fmt = (n) => new Intl.NumberFormat('vi-VN').format(Math.round(n || 0));
window.fmtCurrency = (n) => new Intl.NumberFormat('vi-VN', { style: 'currency', currency: 'VND' }).format(n || 0);
window.fmtDate = (s) => s ? new Date(s).toLocaleDateString('vi-VN') : '';
window.escHtml = (s) => String(s || '').replace(/&/g,'&amp;').replace(/</g,'&lt;').replace(/>/g,'&gt;').replace(/"/g,'&quot;');

window.statusBadge = function(status) {
  const map = { 
    'ACTIVE':['badge-green','Hoạt động'], 
    'INACTIVE':['badge-gray','Tạm dừng'], 
    'EXPIRED':['badge-red','Hết hạn'], 
    'PENDING':['badge-yellow','Chờ duyệt'], 
    'PAID':['badge-green','Đã TT'], 
    'UNPAID':['badge-yellow','Chưa TT'], 
    'CANCELLED':['badge-red','Đã hủy'], 
    'UPCOMING':['badge-blue','Sắp tới'], 
    'ONGOING':['badge-green','Đang diễn ra'], 
    'COMPLETED':['badge-gray','Hoàn thành'], 
    'REGISTERED':['badge-blue','Đã ĐK'], 
    'REVOKED':['badge-red','Đã thu hồi'], 
    'LOST':['badge-orange','Mất thẻ'], 
    'PT':['badge-purple','HLV'], 
    'ADMIN':['badge-orange','Quản trị'],
    'MEMBER':['badge-blue','Hội viên'],
    'PRESENT':['badge-green','Có mặt'],
    'ABSENT':['badge-red','Vắng mặt'],
    'LATE':['badge-yellow','Đi muộn'],
    'HALF':['badge-gray','Nửa ngày'],
  };
  const [cls, lbl] = map[status] || ['badge-gray', status];
  return `<span class="badge ${cls}">${lbl}</span>`;
}

window.showToast = function(msg, type = 'info') {
  const container = document.getElementById('toast-container');
  if (!container) return;
  const el = document.createElement('div');
  el.className = `toast flex items-center gap-3 px-6 py-4 rounded-2xl border backdrop-blur-md shadow-xl ${type==='error'?'border-red-500/50 bg-red-500/10 text-red-400':'border-green-500/50 bg-green-500/10 text-green-400'}`;
  el.innerHTML = `<i data-lucide="${type==='error'?'x-circle':'check-circle'}" class="w-5 h-5"></i><span class="font-medium">${escHtml(msg)}</span>`;
  container.appendChild(el); lucide.createIcons({ nodes:[el] });
  setTimeout(() => { el.classList.add('hiding'); setTimeout(() => el.remove(), 300); }, 3000);
}

window.openModal = function(html) {
  const container = document.getElementById('modal-container'); container.innerHTML = html;
  document.getElementById('modal-overlay').classList.remove('hidden');
  setTimeout(() => { container.classList.remove('scale-95','opacity-0'); container.classList.add('scale-100','opacity-100'); }, 10);
  lucide.createIcons({ nodes: [container] });
}

window.closeModal = function() { 
  const c = document.getElementById('modal-container');
  c.classList.add('scale-95','opacity-0');
  setTimeout(() => { document.getElementById('modal-overlay').classList.add('hidden'); }, 200);
}

window.closeModalOnOverlay = function(e) { if(e.target.id === 'modal-overlay') closeModal(); }
window.toggleSidebar = function() { document.getElementById('sidebar').classList.toggle('collapsed'); }
window.togglePassword = function() {
  const p = document.getElementById('login-password');
  p.type = p.type === 'password' ? 'text' : 'password';
  const i = document.getElementById('eye-icon');
  i.setAttribute('data-lucide', p.type === 'password' ? 'eye' : 'eye-off');
  lucide.createIcons({ nodes: [i.parentElement] });
}

window.confirmLogout = function() { document.getElementById('logout-modal').classList.remove('hidden'); }
window.closeLogoutModal = function() { document.getElementById('logout-modal').classList.add('hidden'); }
window.doLogout = async function() { await API.post('/auth/logout'); window._appLogout(); }

window.deleteItem = async function(mod, id, cb) {
  if (!confirm('Bạn có chắc muốn xóa không?')) return;
  const res = await API.delete(`/api/${mod}/${id}`);
  if (res.success) { showToast('Đã xóa thành công!', 'success'); cb(); } else showToast(res.error, 'error');
}

window.handleGlobalSearch = function(query) {
    if (!query) query = '';
    const term = query.toLowerCase().trim();
    
    // Tìm trên tất cả các bảng
    const tables = document.querySelectorAll('#page-content table');
    tables.forEach(table => {
        const rows = table.querySelectorAll('tbody tr');
        rows.forEach(row => {
            if (row.textContent.toLowerCase().includes(term)) {
                row.style.display = '';
            } else {
                row.style.display = 'none';
            }
        });
    });
    
    // Tìm trên các khối thẻ (nếu có grid/card)
    const cards = document.querySelectorAll('#page-content .searchable-card');
    cards.forEach(card => {
        if (card.textContent.toLowerCase().includes(term)) {
            card.style.display = '';
        } else {
            card.style.display = 'none';
        }
    });
};

window.filterCustomSelect = function(inputId, dropdownId) {
    const term = document.getElementById(inputId).value.toLowerCase().trim();
    const dropdown = document.getElementById(dropdownId);
    if (!dropdown) return;
    const options = dropdown.querySelectorAll('.custom-option');
    options.forEach(opt => {
        if (opt.textContent.toLowerCase().includes(term)) {
            opt.style.display = '';
        } else {
            opt.style.display = 'none';
        }
    });
};

window.selectCustomOption = function(hiddenInputId, searchInputId, value, text) {
    document.getElementById(hiddenInputId).value = value;
    document.getElementById(searchInputId).value = text;
};
