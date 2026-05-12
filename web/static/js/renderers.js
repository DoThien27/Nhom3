window.PAGE_RENDERERS = {};

/* ─── DASHBOARD ────────────────────────────────────────────────────────────── */
PAGE_RENDERERS['dashboard'] = async (container) => {
  try {
    const res = await API.get('/api/dashboard/stats');
    if (!res.success) throw new Error(res.error);
    const d = res.stats;
    container.innerHTML = `
      <div class="page-enter">
        <div class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4 mb-8">
          ${renderKPI('Tổng Hội viên', d.totalMembers, 'users', 'blue')}
          ${renderKPI('Hội viên Active', d.activeMembers, 'check-circle', 'green')}
          ${renderKPI('HĐ chưa thanh toán', d.unpaidCount, 'clock', 'orange')}
          ${renderKPI('Doanh thu', fmtCurrency(d.totalRevenue), 'banknote', 'purple')}
        </div>
        <div class="grid grid-cols-1 lg:grid-cols-2 gap-6">
          <div class="bg-darkcard p-6 rounded-3xl border border-darkborder"><h3 class="text-sm font-bold text-white uppercase mb-6 flex items-center gap-2"><i data-lucide="alert-triangle" class="w-4 h-4 text-orange-500"></i> Lớp học sắp đầy</h3>
            <div class="overflow-x-auto">
              <table class="data-table">
                <thead><tr><th>Tên lớp</th><th>Sĩ số</th><th>Trạng thái</th></tr></thead>
                <tbody>${(d.classesSoonFull || []).map(c => `<tr>
                  <td class="text-white font-bold">${escHtml(c.name)}</td>
                  <td class="text-slate-500">${c.enrolled}/${c.capacity}</td>
                  <td><span class="text-[10px] px-2 py-0.5 bg-orange-500/10 text-orange-500 rounded-full font-bold">Sắp đầy</span></td>
                </tr>`).join('')}</tbody>
              </table>
              ${(d.classesSoonFull || []).length === 0 ? '<div class="p-10 text-center text-slate-500 text-xs">Không có lớp nào quá tải.</div>' : ''}
            </div>
          </div>
          <div class="bg-darkcard p-6 rounded-3xl border border-darkborder"><h3 class="text-sm font-bold text-white uppercase mb-6 flex items-center gap-2"><i data-lucide="trending-up" class="w-4 h-4 text-primary-500"></i> Biểu đồ doanh thu</h3><div class="h-64"><canvas id="rev-chart"></canvas></div></div>
        </div>
      </div>`;
    lucide.createIcons({ nodes: [container] });
    
    // Load chart data from reports
    const r = await API.get('/api/reports');
    if (r.success) {
      new Chart(document.getElementById('rev-chart'), { 
        type: 'line', 
        data: { 
          labels: r.data.dt_theo_thang.map(m => m[0]), 
          datasets: [{ 
            label: 'Doanh thu', 
            data: r.data.dt_theo_thang.map(m => m[1]), 
            borderColor: '#f97316', 
            tension: 0.4, 
            fill: true, 
            backgroundColor: 'rgba(249,115,22,0.1)' 
          }] 
        }, 
        options: { 
          maintainAspectRatio: false, 
          plugins: { legend: { display: false } }, 
          scales: { 
            x: { ticks: { color: '#64748b' }, grid: { display: false } }, 
            y: { ticks: { color: '#64748b' }, grid: { color: 'rgba(255,255,255,0.05)' } } 
          } 
        } 
      });
    }
  } catch (e) { console.error(e); container.innerHTML = `<div class="p-20 text-center text-red-400">Lỗi: ${e.message}</div>`; }
};

function renderKPI(l,v,i,c) {
  const cls = { orange:'text-orange-500 bg-orange-500/10', purple:'text-purple-500 bg-purple-500/10', blue:'text-blue-500 bg-blue-500/10', green:'text-green-500 bg-green-500/10', yellow:'text-yellow-500 bg-yellow-500/10' };
  return `<div class="bg-darkcard p-5 rounded-2xl border border-darkborder"><div class="w-10 h-10 rounded-xl flex items-center justify-center mb-3 ${cls[c]}"><i data-lucide="${i}" class="w-5 h-5"></i></div><div class="text-xl font-black text-white">${v}</div><div class="text-[10px] font-bold text-slate-500 uppercase tracking-widest">${l}</div></div>`;
}

/* ─── MEMBERS ──────────────────────────────────────────────────────────────── */
PAGE_RENDERERS['members'] = async (container) => {
  container.innerHTML = `
    <div class="page-enter">
      <div class="flex items-center justify-between mb-8">
        <h2 class="text-2xl font-black text-white uppercase tracking-tight">QUẢN LÝ HỘI VIÊN</h2>
        <button onclick="editMember()" class="orange-gradient px-6 py-2.5 rounded-xl text-white font-bold text-sm shadow-lg flex items-center gap-2 hover:scale-105 transition-transform">
          <i data-lucide="plus" class="w-4 h-4"></i> Thêm mới
        </button>
      </div>
      <div class="mb-8 max-w-xs">
        <div class="relative group">
          <i data-lucide="search" class="absolute left-4 top-1/2 -translate-y-1/2 w-4 h-4 text-slate-500 group-focus-within:text-primary-500 transition-colors"></i>
          <input type="text" id="member-search" placeholder="Tìm kiếm hội viên..." class="w-full bg-darkcard border border-darkborder rounded-xl py-3 pl-11 pr-4 text-sm text-white focus:outline-none focus:ring-2 focus:ring-primary-500/50 transition-all" oninput="loadMembers(this.value)">
        </div>
      </div>
      <div class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6" id="member-grid-wrap"></div>
    </div>`;
  lucide.createIcons({ nodes:[container] });
  loadMembers();
};
window.loadMembers = async function(keyword = '') {
  try {
    const res = await API.get('/api/members');
    let data = res.data || [];
    if (keyword) {
      const k = keyword.toLowerCase();
      data = data.filter(m => (m.fullName||'').toLowerCase().includes(k) || (m.phone||'').includes(k) || (m.username||'').toLowerCase().includes(k));
    }
    document.getElementById('member-grid-wrap').innerHTML = data.map(m => `
      <div class="bg-darkcard border border-darkborder rounded-[32px] p-6 shadow-xl hover:shadow-primary-500/5 transition-all group page-enter">
        <div class="flex items-center gap-4 mb-6">
          <div class="w-16 h-16 rounded-2xl bg-orange-500/10 flex items-center justify-center text-primary-500 text-2xl font-black border border-primary-500/20 shadow-inner">${(m.fullName||'H')[0].toUpperCase()}</div>
          <div><h4 class="text-lg font-black text-white uppercase tracking-tight">${escHtml(m.fullName)}</h4><div class="text-xs font-bold text-slate-500">@${escHtml(m.username || 'chua_co')}</div></div>
        </div>
        <div class="space-y-4 mb-8">
          <div class="flex items-center justify-between py-2 border-b border-darkborder/50"><span class="text-[10px] font-bold text-slate-500 uppercase flex items-center gap-2"><i data-lucide="phone" class="w-3 h-3"></i> Liên hệ</span><span class="text-sm font-bold text-white">${escHtml(m.phone)}</span></div>
          <div class="flex items-center justify-between py-2 border-b border-darkborder/50"><span class="text-[10px] font-bold text-slate-500 uppercase flex items-center gap-2"><i data-lucide="calendar" class="w-3 h-3"></i> Ngày sinh</span><span class="text-sm font-bold text-white">${m.birthDate ? fmtDate(m.birthDate) : '---'}</span></div>
          <div class="flex items-center justify-between py-2 border-b border-darkborder/50"><span class="text-[10px] font-bold text-slate-500 uppercase flex items-center gap-2"><i data-lucide="user" class="w-3 h-3"></i> Giới tính</span><span class="text-sm font-bold text-white">${escHtml(m.gender || 'Nam')}</span></div>
          <div class="flex items-center justify-between py-2"><span class="text-[10px] font-bold text-slate-500 uppercase flex items-center gap-2"><i data-lucide="map-pin" class="w-3 h-3"></i> Quê quán</span><span class="text-sm font-bold text-white truncate max-w-[150px]">${escHtml(m.homeTown || '---')}</span></div>
        </div>
        <div class="grid grid-cols-2 gap-3 pt-4 border-t border-darkborder/50">
          <button onclick='editMember(${JSON.stringify(m).replace(/'/g,"&#39;")})' class="flex items-center justify-center gap-2 py-3 bg-slate-800 hover:bg-slate-700 text-white text-[10px] font-bold uppercase rounded-2xl transition-all"><i data-lucide="edit-3" class="w-3 h-3"></i> Sửa </button>
          <button onclick="deleteItem('members','${m.id}',loadMembers)" class="flex items-center justify-center gap-2 py-3 bg-red-500/10 hover:bg-red-500 text-red-500 hover:text-white text-[10px] font-bold uppercase rounded-2xl transition-all"><i data-lucide="trash-2" class="w-3 h-3"></i> Xóa </button>
        </div>
      </div>`).join('') + (data.length === 0 ? '<div class="col-span-full p-20 text-center text-slate-500 font-bold uppercase tracking-widest opacity-50">Không tìm thấy hội viên</div>' : '');
    lucide.createIcons({ nodes: [document.getElementById('member-grid-wrap')] });
  } catch(e) { document.getElementById('member-grid-wrap').innerHTML = `<div class="col-span-full p-20 text-center text-red-400">Lỗi: ${e.message}</div>`; }
}
window.editMember = async function(m=null) {
  const [tr, pl] = await Promise.all([API.get('/api/trainers'), API.get('/api/plans')]);
  const trainers = tr.data||[], plans = pl.data||[];
  openModal(`<div class="p-8"><h3 class="text-xl font-black text-white uppercase mb-6">${m?'Sửa hội viên':'Thêm hội viên'}</h3><div class="grid grid-cols-2 gap-4 mb-8">
    <div class="space-y-2"><label class="lbl">Họ tên *</label><input id="m-name" type="text" value="${escHtml(m?.fullName||'')}" class="form-input" placeholder="Nguyễn Văn A"></div>
    <div class="space-y-2"><label class="lbl">SĐT *</label><input id="m-phone" type="text" value="${escHtml(m?.phone||'')}" class="form-input" placeholder="0912345678"></div>
    <div class="space-y-2"><label class="lbl">Email</label><input id="m-email" type="email" value="${escHtml(m?.email||'')}" class="form-input" placeholder="email@example.com"></div>
    <div class="space-y-2"><label class="lbl">Ngày sinh</label><input id="m-dob" type="date" value="${m?.birthDate||''}" class="form-input"></div>
    <div class="space-y-2"><label class="lbl">Giới tính</label><select id="m-gender" class="form-input"><option value="Nam" ${m?.gender==='Nam'?'selected':''}>Nam</option><option value="Nữ" ${m?.gender==='Nữ'?'selected':''}>Nữ</option></select></div>
    <div class="space-y-2"><label class="lbl">Trạng thái</label><select id="m-status" class="form-input"><option value="ACTIVE" ${(m?.status||'ACTIVE')==='ACTIVE'?'selected':''}>Hoạt động</option><option value="EXPIRED" ${m?.status==='EXPIRED'?'selected':''}>Hết hạn</option><option value="PENDING" ${m?.status==='PENDING'?'selected':''}>Chờ duyệt</option></select></div>
    <div class="col-span-2 space-y-2"><label class="lbl">Quê quán</label><input id="m-hometown" type="text" value="${escHtml(m?.homeTown||'')}" class="form-input"></div>
    <div class="space-y-2"><label class="lbl">HLV Phụ trách</label><select id="m-pt" class="form-input"><option value="">-- Không có --</option>${trainers.map(t=>`<option value="${t.id}" ${m?.assignedPTId==t.id?'selected':''}>${escHtml(t.fullName)}</option>`).join('')}</select></div>
    <div class="col-span-2 space-y-2"><label class="lbl">Gói tập</label><select id="m-plan" class="form-input"><option value="">-- Không có --</option>${plans.map(p=>`<option value="${p.id}" ${m?.activePlanId==p.id?'selected':''}>${escHtml(p.name)}</option>`).join('')}</select></div>
  </div><div class="flex justify-end gap-3"><button onclick="closeModal()" class="btn-gray">Hủy</button><button onclick="saveMember('${m?.id||''}')" class="btn-primary">Lưu lại</button></div></div>`);
}
window.saveMember = async function(id) {
  const body = { fullName:document.getElementById('m-name').value, phone:document.getElementById('m-phone').value, email:document.getElementById('m-email').value||'', birthDate:document.getElementById('m-dob').value, gender:document.getElementById('m-gender').value, homeTown:document.getElementById('m-hometown').value, assignedPTId:document.getElementById('m-pt').value, activePlanId:document.getElementById('m-plan').value, status:document.getElementById('m-status').value };
  const res = id ? await API.put(`/api/members/${id}`, body) : await API.post('/api/members', body);
  if (res.success) { showToast('Đã lưu thành công!', 'success'); closeModal(); loadMembers(); } else showToast(res.error, 'error');
}

/* ─── TRAINERS ─────────────────────────────────────────────────────────────── */
PAGE_RENDERERS['trainers'] = async (container) => {
  container.innerHTML = `
    <div class="page-enter">
      <div class="flex items-center justify-between mb-8">
        <div class="flex items-center gap-4">
          <h2 class="text-2xl font-black text-white uppercase tracking-tight">HUẤN LUYỆN VIÊN</h2>
          <button onclick="editTrainer()" class="orange-gradient px-6 py-2.5 rounded-xl text-white font-bold text-sm shadow-lg flex items-center gap-2 hover:scale-105 transition-transform">
            <i data-lucide="plus" class="w-4 h-4"></i> Thêm HLV mới
          </button>
        </div>
        <div class="max-w-xs w-full">
          <div class="relative group">
            <i data-lucide="search" class="absolute left-4 top-1/2 -translate-y-1/2 w-4 h-4 text-slate-500 group-focus-within:text-primary-500 transition-colors"></i>
            <input type="text" id="trainer-search" placeholder="Tìm kiếm HLV..." 
              class="w-full bg-darkcard border border-darkborder rounded-xl py-3 pl-11 pr-4 text-sm text-white focus:outline-none focus:ring-2 focus:ring-primary-500/50 transition-all"
              oninput="loadTrainers(this.value)">
          </div>
        </div>
      </div>
      <div class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6" id="trainer-grid-wrap"></div>
    </div>`;
  lucide.createIcons({ nodes:[container] });
  loadTrainers();
};

window.loadTrainers = async function(keyword = '') {
  try {
    const res = await API.get('/api/trainers');
    let data = res.data || [];
    if (keyword) {
      const k = keyword.toLowerCase();
      data = data.filter(t => t.fullName.toLowerCase().includes(k) || (t.username||'').toLowerCase().includes(k) || (t.specialty||'').toLowerCase().includes(k));
    }
    document.getElementById('trainer-grid-wrap').innerHTML = data.map(t => `
      <div class="bg-darkcard border border-darkborder rounded-[32px] p-6 shadow-xl hover:shadow-primary-500/5 transition-all group page-enter text-center">
        <div class="flex flex-col items-center mb-6">
          <div class="w-20 h-20 rounded-2xl bg-blue-500/10 flex items-center justify-center text-blue-500 text-3xl font-black border border-blue-500/20 shadow-inner mb-4">
            ${(t.fullName||'T')[0].toUpperCase()}
          </div>
          <h4 class="text-xl font-black text-white uppercase tracking-tight">${escHtml(t.fullName)}</h4>
          <div class="text-xs font-bold text-slate-500">@${escHtml(t.username || 'hlv_id')}</div>
        </div>

        <div class="space-y-4 mb-8 text-left">
          <div class="flex items-center justify-between py-2 border-b border-darkborder/50">
            <span class="text-[10px] font-bold text-slate-500 uppercase flex items-center gap-2"><i data-lucide="phone" class="w-3 h-3"></i> Số điện thoại</span>
            <span class="text-sm font-bold text-white">${escHtml(t.phone || '---')}</span>
          </div>
          <div class="flex items-center justify-between py-2 border-b border-darkborder/50">
            <span class="text-[10px] font-bold text-slate-500 uppercase flex items-center gap-2"><i data-lucide="map-pin" class="w-3 h-3"></i> Quê quán</span>
            <span class="text-sm font-bold text-white">${escHtml(t.address || '---')}</span>
          </div>
          <div class="flex items-center justify-between py-2 border-b border-darkborder/50">
            <span class="text-[10px] font-bold text-slate-500 uppercase flex items-center gap-2"><i data-lucide="award" class="w-3 h-3"></i> Chuyên môn</span>
            <span class="text-sm font-bold text-white">${escHtml(t.specialty || 'Chưa cập nhật')}</span>
          </div>
          <div class="flex items-center justify-between py-2">
            <span class="text-[10px] font-bold text-slate-500 uppercase flex items-center gap-2"><i data-lucide="users" class="w-3 h-3"></i> Học viên</span>
            <span class="text-sm font-bold text-white">${t.activeStudents || 0} người</span>
          </div>
        </div>

        <div class="grid grid-cols-2 gap-3 pt-4 border-t border-darkborder/50">
          <button onclick='editTrainer(${JSON.stringify(t).replace(/'/g,"&#39;")})' class="flex items-center justify-center gap-2 py-3 bg-slate-800 hover:bg-slate-700 text-white text-[10px] font-bold uppercase rounded-2xl transition-all">Sửa</button>
          <button onclick="deleteItem('trainers','${t.id}',loadTrainers)" class="flex items-center justify-center gap-2 py-3 bg-red-500/10 hover:bg-red-500 text-red-500 hover:text-white text-[10px] font-bold uppercase rounded-2xl transition-all">Xóa</button>
        </div>
      </div>`).join('') + (data.length === 0 ? '<div class="col-span-full p-20 text-center text-slate-500 font-bold uppercase tracking-widest opacity-50">Không tìm thấy huấn luyện viên</div>' : '');
    lucide.createIcons({ nodes: [document.getElementById('trainer-grid-wrap')] });
  } catch(e) { document.getElementById('trainer-grid-wrap').innerHTML = `<div class="col-span-full p-20 text-center text-red-400">Lỗi: ${e.message}</div>`; }
}

window.editTrainer = function(t=null) {
  openModal(`<div class="p-8"><h3 class="text-xl font-black text-white uppercase mb-6">${t?'Sửa HLV':'Thêm HLV mới'}</h3><div class="grid grid-cols-2 gap-4 mb-8">
    <div class="col-span-2 space-y-2"><label class="lbl">Họ tên</label><input id="t-name" type="text" value="${escHtml(t?.fullName||'')}" class="form-input"></div>
    <div class="space-y-2"><label class="lbl">Số điện thoại</label><input id="t-phone" type="text" value="${escHtml(t?.phone||'')}" class="form-input"></div>
    <div class="space-y-2"><label class="lbl">Chuyên môn</label><input id="t-spec" type="text" value="${escHtml(t?.specialty||'')}" class="form-input"></div>
    <div class="col-span-2 space-y-2"><label class="lbl">Quê quán (Địa chỉ)</label><input id="t-addr" type="text" value="${escHtml(t?.address||'')}" class="form-input"></div>
    <div class="space-y-2"><label class="lbl">Username</label><input id="t-user" type="text" value="${escHtml(t?.username||'')}" class="form-input" ${t?'readonly':''}></div>
    <div class="space-y-2"><label class="lbl">Mật khẩu</label><input id="t-pass" type="password" class="form-input" placeholder="${t?'Bỏ trống để giữ nguyên':'Nhập mật khẩu'}"></div>
  </div><div class="flex justify-end gap-3"><button onclick="closeModal()" class="btn-gray">Hủy</button><button onclick="saveTrainer('${t?.id||''}')" class="btn-primary">Lưu lại</button></div></div>`);
}

window.saveTrainer = async function(id) {
  const body = { fullName:document.getElementById('t-name').value, phone:document.getElementById('t-phone').value, specialty:document.getElementById('t-spec').value, address:document.getElementById('t-addr').value, username:document.getElementById('t-user').value, password:document.getElementById('t-pass').value };
  const res = id ? await API.put(`/api/trainers/${id}`, body) : await API.post('/api/trainers', body);
  if (res.success) { showToast('Đã lưu thành công!', 'success'); closeModal(); loadTrainers(); } else showToast(res.error, 'error');
}

/* ─── OTHER RENDERERS ──────────────────────────────────────────────────────── */
PAGE_RENDERERS['sports'] = async (container) => {
  container.innerHTML = `
    <div class="page-enter">
      <div class="flex items-center justify-between mb-8">
        <h2 class="text-2xl font-black text-white uppercase tracking-tight">MÔN THẾ THAO</h2>
        <div class="flex items-center gap-4">
          <div class="relative group w-64">
            <i data-lucide="search" class="absolute left-4 top-1/2 -translate-y-1/2 w-4 h-4 text-slate-500 group-focus-within:text-primary-500 transition-colors"></i>
            <input type="text" id="sport-search" placeholder="Tìm môn tập..." 
              class="w-full bg-darkcard border border-darkborder rounded-xl py-3 pl-11 pr-4 text-sm text-white focus:outline-none focus:ring-2 focus:ring-primary-500/50 transition-all"
              oninput="loadSports(this.value)">
          </div>
          <button onclick="editSport()" class="orange-gradient px-6 py-2.5 rounded-xl text-white font-bold text-sm shadow-lg flex items-center gap-2 hover:scale-105 transition-transform">
            <i data-lucide="plus" class="w-4 h-4"></i> Thêm môn
          </button>
        </div>
      </div>
      <div class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6" id="sport-grid-wrap"></div>
    </div>`;
  lucide.createIcons({ nodes:[container] });
  loadSports();
};

window.loadSports = async function(keyword = '') {
  try {
    const res = await API.get('/api/sports');
    let data = res.data || [];
    if (keyword) {
      const k = keyword.toLowerCase();
      data = data.filter(s => s.sport_name.toLowerCase().includes(k));
    }
    document.getElementById('sport-grid-wrap').innerHTML = data.map(s => `
      <div class="bg-darkcard border border-darkborder rounded-[32px] overflow-hidden shadow-xl hover:shadow-primary-500/5 transition-all group page-enter">
        <div class="orange-gradient p-8 text-center relative">
          <div class="w-12 h-12 bg-white/20 rounded-xl flex items-center justify-center mx-auto mb-3 text-white">
            <i data-lucide="trophy" class="w-6 h-6"></i>
          </div>
          <h4 class="text-xl font-black text-white uppercase tracking-tight">${escHtml(s.sport_name)}</h4>
        </div>
        
        <div class="p-6">
          <p class="text-center text-[10px] text-slate-500 font-bold uppercase mb-6 leading-relaxed px-4 line-clamp-2">${escHtml(s.description || 'Chưa có mô tả chi tiết cho môn tập này')}</p>
          
          <div class="space-y-4 mb-6">
            <div class="flex items-center justify-between text-[10px] font-bold uppercase">
              <span class="text-slate-500 flex items-center gap-2"><i data-lucide="map-pin" class="w-3.5 h-3.5"></i> Sân bãi</span>
              <span class="text-white">0 sân</span>
            </div>
            <div class="flex items-center justify-between text-[10px] font-bold uppercase">
              <span class="text-slate-500 flex items-center gap-2"><i data-lucide="activity" class="w-3.5 h-3.5"></i> Lớp học</span>
              <span class="text-white">0 lớp</span>
            </div>
          </div>

          <div class="flex justify-center mb-6">
            <div class="px-3 py-1.5 bg-green-500/10 text-green-500 text-[9px] font-black uppercase rounded-full flex items-center gap-2">
              <div class="w-1.5 h-1.5 bg-green-500 rounded-full animate-pulse"></div> Đang hoạt động
            </div>
          </div>

          <div class="grid grid-cols-2 gap-2 mb-2">
            <button onclick='editSport(${JSON.stringify(s).replace(/'/g,"&#39;")})' class="py-2.5 bg-slate-800 hover:bg-slate-700 text-white text-[10px] font-bold uppercase rounded-xl transition-all flex items-center justify-center gap-2">
              <i data-lucide="edit-3" class="w-3 h-3"></i> Sửa
            </button>
            <button onclick="deleteItem('sports','${s.sport_id}',loadSports)" class="py-2.5 bg-red-500/10 hover:bg-red-500 text-red-500 hover:text-white text-[10px] font-bold uppercase rounded-xl transition-all flex items-center justify-center gap-2">
              <i data-lucide="trash-2" class="w-3 h-3"></i> Xóa
            </button>
          </div>
          <button onclick="navigate('classes')" class="w-full py-2.5 bg-blue-500/10 hover:bg-blue-500 text-blue-500 hover:text-white text-[10px] font-bold uppercase rounded-xl transition-all flex items-center justify-center gap-2">
            <i data-lucide="eye" class="w-3 h-3"></i> Xem lớp
          </button>
        </div>
      </div>`).join('') + (data.length === 0 ? '<div class="col-span-full p-20 text-center text-slate-500 font-bold uppercase tracking-widest opacity-50">Không tìm thấy môn học</div>' : '');
    lucide.createIcons({ nodes: [document.getElementById('sport-grid-wrap')] });
  } catch(e) { document.getElementById('sport-grid-wrap').innerHTML = `<div class="col-span-full p-20 text-center text-red-400">Lỗi: ${e.message}</div>`; }
}
PAGE_RENDERERS['classes'] = async (c) => {
  c.innerHTML = `<div class="page-enter"><div class="flex items-center justify-between mb-8"><div><h2 class="text-2xl font-black text-white uppercase">Lớp học & Buổi tập</h2></div><button onclick="editClass()" class="btn-primary flex items-center gap-2"><i data-lucide="plus" class="w-4 h-4"></i> Thêm lớp học</button></div><div class="grid grid-cols-1 md:grid-cols-3 gap-6" id="class-list-wrap"></div></div>`;
  lucide.createIcons({ nodes:[c] });
  loadClasses();
};
window.loadClasses = async function() {
  const res = await API.get('/api/classes');
  const data = res.data || [];
  document.getElementById('class-list-wrap').innerHTML = data.map(cl=>`<div class="bg-darkcard rounded-3xl border border-darkborder p-6 group relative">
    <h4 class="text-white font-bold uppercase mb-1 text-sm pr-6">${escHtml(cl.name)}</h4>
    <div class="text-[10px] text-slate-500 font-bold uppercase mb-4">${cl.enrolledCount||0}/${cl.capacity} học viên</div>
    <div class="space-y-2 mb-6 text-xs text-slate-500 font-medium">
      <div class="flex items-center gap-2"><i data-lucide="calendar" class="w-3.5 h-3.5 text-primary-500"></i> ${escHtml(cl.dayOfWeek)}</div>
      <div class="flex items-center gap-2"><i data-lucide="clock" class="w-3.5 h-3.5 text-primary-500"></i> ${cl.time}</div>
      <div class="flex items-center gap-2"><i data-lucide="map-pin" class="w-3.5 h-3.5 text-primary-500"></i> ${escHtml(cl.facilityName || 'Chưa định danh')}</div>
    </div>
    <div class="flex items-center justify-between pt-3 border-t border-darkborder mb-3">
      <div class="text-base font-black text-white">${fmtCurrency(cl.price)}</div>
      ${statusBadge(cl.status)}
    </div>
    <div class="grid grid-cols-3 gap-2">
      <button onclick='editClass(${JSON.stringify(cl).replace(/'/g,"&#39;")})' class="py-2 bg-slate-800 hover:bg-slate-700 text-white text-[10px] font-bold uppercase rounded-xl transition-all flex items-center justify-center gap-1"><i data-lucide="edit-3" class="w-3 h-3"></i>Sửa</button>
      <button onclick='manageEnrollment(${JSON.stringify(cl).replace(/'/g,"&#39;")})' class="py-2 bg-blue-500/10 hover:bg-blue-500 text-blue-400 hover:text-white text-[10px] font-bold uppercase rounded-xl transition-all flex items-center justify-center gap-1"><i data-lucide="users" class="w-3 h-3"></i>HV</button>
      <button onclick="deleteItem('classes','${cl.id}',loadClasses)" class="py-2 bg-red-500/10 hover:bg-red-500 text-red-500 hover:text-white text-[10px] font-bold uppercase rounded-xl transition-all flex items-center justify-center gap-1"><i data-lucide="trash-2" class="w-3 h-3"></i>Xóa</button>
    </div>
  </div>`).join('') + (data.length===0?'<div class="col-span-3 p-20 text-center text-slate-500">Chưa có dữ liệu.</div>':'');
  lucide.createIcons({ nodes:[document.getElementById('class-list-wrap')] });
}
PAGE_RENDERERS['facilities'] = async (c) => {
  c.innerHTML = `<div class="page-enter"><div class="flex items-center justify-between mb-8"><div><h2 class="text-2xl font-black text-white uppercase">Cơ sở vật chất</h2></div><button onclick="editFacility()" class="btn-primary flex items-center gap-2"><i data-lucide="plus" class="w-4 h-4"></i> Thêm khu vực</button></div><div class="grid grid-cols-1 md:grid-cols-2 gap-6" id="fac-list-wrap"></div></div>`;
  lucide.createIcons({ nodes:[c] });
  loadFacilities();
};
window.loadFacilities = async function() {
  const res = await API.get('/api/facilities');
  const data = res.data || [];
  document.getElementById('fac-list-wrap').innerHTML = data.map(f=>`<div class="bg-darkcard p-6 rounded-3xl border border-darkborder flex gap-6 relative group">
    <div class="w-16 h-16 bg-green-500/10 text-green-500 rounded-2xl flex items-center justify-center shrink-0"><i data-lucide="map-pin" class="w-8 h-8"></i></div>
    <div class="flex-1">
      <h4 class="text-white font-bold uppercase mb-1 text-sm">${escHtml(f.facility_name)}</h4>
      <p class="text-slate-500 text-xs mb-3 font-medium">${escHtml(f.location || 'Chưa có vị trí')}</p>
      <div class="flex gap-2">
        <button onclick='editFacility(${JSON.stringify(f).replace(/'/g,"&#39;")})' class="py-1.5 px-3 bg-slate-800 hover:bg-slate-700 text-white text-[10px] font-bold uppercase rounded-lg transition-all flex items-center gap-1"><i data-lucide="edit-3" class="w-3 h-3"></i>Sửa</button>
        <button onclick="deleteItem('facilities','${f.facility_id}',loadFacilities)" class="py-1.5 px-3 bg-red-500/10 hover:bg-red-500 text-red-500 hover:text-white text-[10px] font-bold uppercase rounded-lg transition-all flex items-center gap-1"><i data-lucide="trash-2" class="w-3 h-3"></i>Xóa</button>
      </div>
    </div>
  </div>`).join('') + (data.length===0?'<div class="col-span-2 p-20 text-center text-slate-500">Chưa có dữ liệu.</div>':'');
  lucide.createIcons({ nodes:[document.getElementById('fac-list-wrap')] });
}
PAGE_RENDERERS['events'] = async (c) => {
  c.innerHTML = `<div class="page-enter"><div class="flex items-center justify-between mb-8"><div><h2 class="text-2xl font-black text-white uppercase">Sự kiện & Giải đấu</h2></div><button onclick="editEvent()" class="btn-primary flex items-center gap-2"><i data-lucide="plus" class="w-4 h-4"></i> Tạo sự kiện</button></div><div class="grid grid-cols-1 lg:grid-cols-2 gap-6" id="event-list-wrap"></div></div>`;
  lucide.createIcons({ nodes:[c] });
  loadEvents();
};
window.loadEvents = async function() {
  const res = await API.get('/api/events');
  const data = res.data || [];
  document.getElementById('event-list-wrap').innerHTML = data.map(e=>`<div class="bg-darkcard rounded-3xl border border-darkborder p-6 flex gap-6 group">
    <div class="w-16 h-16 bg-slate-900 rounded-xl flex flex-col items-center justify-center shrink-0 border border-darkborder shadow-inner">
      <div class="text-xl font-black text-primary-500">${new Date(e.ngay).getDate()}</div>
      <div class="text-[8px] font-bold text-slate-500 uppercase">Th${new Date(e.ngay).getMonth()+1}</div>
    </div>
    <div class="flex-1 min-w-0">
      <div class="flex items-start justify-between gap-2 mb-1">
        <h4 class="text-sm font-bold text-white uppercase leading-tight">${escHtml(e.ten)}</h4>
        ${statusBadge(e.trang_thai||'UPCOMING')}
      </div>
      <p class="text-slate-500 text-[10px] mb-2 leading-relaxed line-clamp-2">${escHtml(e.mo_ta)}</p>
      <div class="flex items-center gap-3 text-[10px] text-slate-400 font-bold uppercase mb-3">
        <span class="flex items-center gap-1"><i data-lucide="map-pin" class="w-3 h-3 text-blue-500"></i>${escHtml(e.dia_diem)}</span>
        <span class="flex items-center gap-1"><i data-lucide="clock" class="w-3 h-3 text-green-500"></i>${e.gio} - ${e.gio_ket_thuc}</span>
        ${e.gia>0?`<span class="text-primary-500">${fmtCurrency(e.gia)}</span>`:''}
      </div>
      <div class="flex gap-2">
        <button onclick='editEvent(${JSON.stringify(e).replace(/'/g,"&#39;")})' class="py-1.5 px-3 bg-slate-800 hover:bg-slate-700 text-white text-[10px] font-bold uppercase rounded-lg transition-all flex items-center gap-1"><i data-lucide="edit-3" class="w-3 h-3"></i>Sửa</button>
        <button onclick='manageEventParticipants(${JSON.stringify(e).replace(/'/g,"&#39;")})' class="py-1.5 px-3 bg-blue-500/10 hover:bg-blue-500 text-blue-400 hover:text-white text-[10px] font-bold uppercase rounded-lg transition-all flex items-center gap-1"><i data-lucide="users" class="w-3 h-3"></i>Tham gia</button>
        <button onclick="deleteItem('events','${e.id}',loadEvents)" class="py-1.5 px-3 bg-red-500/10 hover:bg-red-500 text-red-500 hover:text-white text-[10px] font-bold uppercase rounded-lg transition-all flex items-center gap-1"><i data-lucide="trash-2" class="w-3 h-3"></i>Xóa</button>
      </div>
    </div>
  </div>`).join('') + (data.length===0?'<div class="col-span-2 p-20 text-center text-slate-500">Chưa có dữ liệu.</div>':'');
  lucide.createIcons({ nodes:[document.getElementById('event-list-wrap')] });
}

window.manageEventParticipants = async function(ev) {
  window._lastEventManage = ev;
  const [mr, pr] = await Promise.all([API.get('/api/members'), API.get(`/api/events/${ev.id}/participants`)]);
  const allMembers = mr.data||[];
  const participants = pr.data||[];
  const participantIds = new Set(participants.map(p=>String(p.memberId)));
  openModal(`<div class="p-8"><h3 class="text-xl font-black text-white uppercase mb-1">${escHtml(ev.ten)}</h3>
    <p class="text-slate-500 text-xs mb-6">${participants.length}/${ev.suc_chua} người tham gia</p>
    <div class="space-y-2 max-h-80 overflow-y-auto custom-scrollbar mb-6">${allMembers.map(m=>`
      <div class="flex items-center justify-between p-3 rounded-xl ${participantIds.has(String(m.id))?'bg-primary-500/10 border border-primary-500/20':'bg-slate-900/50 border border-slate-800'}">
        <div><span class="text-sm font-bold text-white">${escHtml(m.fullName)}</span><div class="text-xs text-slate-500">${escHtml(m.phone)}</div></div>
        ${participantIds.has(String(m.id))
          ? `<button onclick="removeEventParticipant('${ev.id}','${m.id}')" class="text-xs px-3 py-1 bg-red-500/10 text-red-400 rounded-lg hover:bg-red-500 hover:text-white transition-all">Xóa</button>`
          : `<button onclick="addEventParticipant('${ev.id}','${m.id}')" class="text-xs px-3 py-1 bg-green-500/10 text-green-400 rounded-lg hover:bg-green-500 hover:text-white transition-all">Thêm</button>`}
      </div>`).join('')}
    </div><div class="flex justify-end"><button onclick="closeModal()" class="btn-gray">Đóng</button></div></div>`);
}
window.addEventParticipant = async function(eventId, memberId) {
  const res = await API.post(`/api/events/${eventId}/participants`, { memberId });
  if (res.success) { showToast('Đã thêm!', 'success'); manageEventParticipants(window._lastEventManage); } else showToast(res.error, 'error');
}
window.removeEventParticipant = async function(eventId, memberId) {
  const res = await API.delete(`/api/events/${eventId}/participants/${memberId}`);
  if (res.success) { showToast('Đã xóa!', 'success'); manageEventParticipants(window._lastEventManage); } else showToast(res.error, 'error');
}

PAGE_RENDERERS['billing'] = async (c) => {
  try {
    const res = await API.get('/api/billing');
    const data = res.data || [];
    const totalPaid = data.reduce((s, h) => s + parseFloat(h.paidAmount || 0), 0);
    const totalRemaining = data.filter(h => h.paymentStatus !== 'CANCELLED').reduce((s, h) => s + parseFloat(h.remainingAmount || 0), 0);

    c.innerHTML = `<div class="page-enter">
      <div class="flex items-center justify-between mb-8">
        <h2 class="text-2xl font-black text-white uppercase">Tài chính & Hóa đơn</h2>
        <button onclick="addInvoice()" class="btn-primary flex items-center gap-2"><i data-lucide="plus" class="w-4 h-4"></i> Tạo hóa đơn</button>
      </div>
      <div class="grid grid-cols-1 md:grid-cols-3 gap-4 mb-8">
        <div class="bg-darkcard p-6 rounded-2xl border border-darkborder">
          <div class="text-[10px] text-slate-500 font-bold uppercase mb-1 text-center">Tổng đã thu</div>
          <div class="text-2xl font-black text-green-400 text-center">${fmtCurrency(totalPaid)}</div>
        </div>
        <div class="bg-darkcard p-6 rounded-2xl border border-darkborder">
          <div class="text-[10px] text-slate-500 font-bold uppercase mb-1 text-center">Còn nợ</div>
          <div class="text-2xl font-black text-red-400 text-center">${fmtCurrency(totalRemaining)}</div>
        </div>
        <div class="bg-darkcard p-6 rounded-2xl border border-darkborder">
          <div class="text-[10px] text-slate-500 font-bold uppercase mb-1 text-center">Số hóa đơn</div>
          <div class="text-2xl font-black text-white text-center">${data.length}</div>
        </div>
      </div>
      <div class="bg-darkcard rounded-3xl border border-darkborder overflow-hidden">
        <div class="overflow-x-auto">
          <table class="data-table min-w-full">
            <thead>
              <tr>
                <th>Mã HĐ</th><th>Hội viên</th><th>Loại</th><th>Ngày</th><th>Tổng tiền</th><th>Đã trả</th><th>Còn lại</th><th>Trạng thái</th><th>Thao tác</th>
              </tr>
            </thead>
            <tbody>${data.map(h => `<tr>
              <td class="font-mono text-primary-500 font-bold">#${h.id}</td>
              <td class="text-white font-bold">${escHtml(h.memberName || '---')}</td>
              <td><span class="text-[10px] font-black px-2 py-1 rounded bg-slate-800 text-slate-400">${h.sourceType}</span></td>
              <td class="text-slate-500 text-sm">${fmtDate(h.date)}</td>
              <td class="font-bold text-white">${fmtCurrency(h.finalAmount)}</td>
              <td class="text-green-400 text-sm">${fmtCurrency(h.paidAmount)}</td>
              <td class="text-red-400 text-sm font-bold">${fmtCurrency(h.remainingAmount)}</td>
              <td>${statusBadge(h.paymentStatus)}</td>
              <td>
                <div class="flex items-center gap-2">
                  ${h.paymentStatus !== 'PAID' && h.paymentStatus !== 'CANCELLED' ? `
                    <button onclick="payInvoiceModal('${h.id}', ${h.remainingAmount})" class="text-xs px-2 py-1 bg-primary-500 text-white rounded-lg hover:bg-primary-600 transition-all font-bold">Thanh toán</button>
                  ` : ''}
                  <button onclick="deleteItem('billing','${h.id}',()=>navigate('billing'))" class="p-1.5 text-red-500 hover:bg-red-500/10 rounded-lg"><i data-lucide="trash-2" class="w-3.5 h-3.5"></i></button>
                </div>
              </td>
            </tr>`).join('')}</tbody>
          </table>
        </div>
        ${data.length === 0 ? '<div class="p-20 text-center text-slate-500">Chưa có giao dịch.</div>' : ''}
      </div>
    </div>`;
    lucide.createIcons({ nodes: [c] });
  } catch (e) { console.error(e); c.innerHTML = `<div class="p-20 text-center text-red-400">Lỗi: ${e.message}</div>`; }
};

window.payInvoiceModal = function(id, remaining) {
  openModal(`<div class="p-8">
    <h3 class="text-xl font-black text-white uppercase mb-6">Thanh toán hóa đơn #${id}</h3>
    <div class="space-y-4 mb-8">
      <div class="space-y-2">
        <label class="lbl">Số tiền thanh toán (Còn nợ: ${fmtCurrency(remaining)})</label>
        <input id="pay-amount" type="number" value="${remaining}" class="form-input" min="0" max="${remaining}">
      </div>
      <div class="space-y-2">
        <label class="lbl">Phương thức</label>
        <select id="pay-method" class="form-input">
          <option value="CASH">Tiền mặt</option>
          <option value="TRANSFER">Chuyển khoản</option>
          <option value="CARD">Quẹt thẻ</option>
        </select>
      </div>
      <div class="space-y-2">
        <label class="lbl">Ghi chú</label>
        <input id="pay-note" type="text" class="form-input" placeholder="...">
      </div>
    </div>
    <div class="flex justify-end gap-3">
      <button onclick="closeModal()" class="btn-gray">Hủy</button>
      <button onclick="doPayInvoice('${id}')" class="btn-primary">Xác nhận thanh toán</button>
    </div>
  </div>`);
};

window.doPayInvoice = async function(id) {
  const body = {
    amount: document.getElementById('pay-amount').value,
    method: document.getElementById('pay-method').value,
    note: document.getElementById('pay-note').value
  };
  const res = await API.post(`/api/billing/${id}/pay`, body);
  if (res.success) {
    showToast('Thanh toán thành công!', 'success');
    closeModal();
    navigate('billing');
  } else {
    showToast(res.error, 'error');
  }
};

PAGE_RENDERERS['reports'] = async (c) => {
  try {
    const res = await API.get('/api/reports');
    if (!res.success) throw new Error(res.error);
    const d = res.data;
    c.innerHTML = `<div class="page-enter">
      <h2 class="text-2xl font-black text-white uppercase mb-8">Báo cáo & Thống kê</h2>
      <div class="grid grid-cols-2 lg:grid-cols-4 gap-4 mb-8">
        <div class="bg-darkcard p-6 rounded-2xl border border-darkborder">
          <div class="text-[10px] text-slate-500 font-bold uppercase mb-1">Doanh thu tháng này</div>
          <div class="text-2xl font-black text-green-400">${fmtCurrency(d.doanh_thu_thang)}</div>
        </div>
        <div class="bg-darkcard p-6 rounded-2xl border border-darkborder">
          <div class="text-[10px] text-slate-500 font-bold uppercase mb-1">Tổng doanh thu</div>
          <div class="text-2xl font-black text-white">${fmtCurrency(d.tong_doanh_thu||0)}</div>
        </div>
        <div class="bg-darkcard p-6 rounded-2xl border border-darkborder">
          <div class="text-[10px] text-slate-500 font-bold uppercase mb-1">Hội viên mới</div>
          <div class="text-2xl font-black text-blue-400">${d.hoi_vien_moi}</div>
        </div>
        <div class="bg-darkcard p-6 rounded-2xl border border-darkborder">
          <div class="text-[10px] text-slate-500 font-bold uppercase mb-1">Lớp đang hoạt động</div>
          <div class="text-2xl font-black text-orange-400">${d.lop_hoat_dong||0}</div>
        </div>
      </div>
      <div class="grid grid-cols-1 lg:grid-cols-2 gap-6 mb-6">
        <div class="bg-darkcard p-6 rounded-3xl border border-darkborder">
          <h3 class="text-white font-bold mb-4 uppercase text-sm">Doanh thu theo tháng</h3>
          <div class="h-64"><canvas id="report-chart"></canvas></div>
        </div>
        <div class="bg-darkcard p-6 rounded-3xl border border-darkborder">
          <h3 class="text-white font-bold mb-4 uppercase text-sm">Hội viên theo gói tập</h3>
          <div class="h-64"><canvas id="plan-chart"></canvas></div>
        </div>
      </div>
      <div class="grid grid-cols-1 lg:grid-cols-2 gap-6">
        <div class="bg-darkcard p-6 rounded-3xl border border-darkborder">
          <h3 class="text-white font-bold mb-4 uppercase text-sm">Hóa đơn theo trạng thái</h3>
          <div class="space-y-3">${(d.hd_theo_tt||[]).map(h=>`
            <div class="flex items-center justify-between p-3 bg-slate-900/50 rounded-xl">
              <div class="flex items-center gap-3">${statusBadge(h.status)}<span class="text-sm text-slate-400">${h.count} hóa đơn</span></div>
              <span class="font-bold text-white">${fmtCurrency(h.total)}</span>
            </div>`).join('')}</div>
        </div>
        <div class="bg-darkcard p-6 rounded-3xl border border-darkborder">
          <h3 class="text-white font-bold mb-4 uppercase text-sm">Top hội viên đóng góp</h3>
          <div class="space-y-3">${(d.top_hv||[]).map((h,i)=>`
            <div class="flex items-center gap-3 p-3 bg-slate-900/50 rounded-xl">
              <div class="w-7 h-7 rounded-full flex items-center justify-center text-xs font-black ${i===0?'bg-yellow-500 text-black':i===1?'bg-slate-400 text-black':i===2?'bg-orange-600 text-white':'bg-slate-800 text-slate-400'}">${i+1}</div>
              <span class="flex-1 text-sm font-bold text-white truncate">${escHtml(h.name)}</span>
              <span class="text-green-400 font-black text-sm">${fmtCurrency(h.total)}</span>
            </div>`).join('')}</div>
        </div>
      </div>
    </div>`;
    new Chart(document.getElementById('report-chart'), { type:'bar', data: { labels: d.dt_theo_thang.map(m=>m[0]), datasets: [{ label:'Doanh thu', data: d.dt_theo_thang.map(m=>m[1]), backgroundColor:'rgba(249,115,22,0.7)', borderColor:'#f97316', borderWidth:2, borderRadius:6 }] }, options:{ maintainAspectRatio:false, plugins:{legend:{display:false}}, scales:{x:{ticks:{color:'#64748b'},grid:{color:'rgba(30,41,59,0.5)'}},y:{ticks:{color:'#64748b'},grid:{color:'rgba(30,41,59,0.5)'}}} } });
    if (d.hv_theo_goi?.length) {
      new Chart(document.getElementById('plan-chart'), { type:'doughnut', data: { labels: d.hv_theo_goi.map(p=>p.name), datasets: [{ data: d.hv_theo_goi.map(p=>p.total), backgroundColor:['#f97316','#3b82f6','#8b5cf6','#10b981','#ef4444'] }] }, options:{ maintainAspectRatio:false, plugins:{legend:{position:'bottom',labels:{color:'#64748b',font:{size:10}}}} } });
    }
  } catch(e) { c.innerHTML = `<div class="p-20 text-center text-red-400">Lỗi: ${e.message}</div>`; }
};
PAGE_RENDERERS['system_users'] = async (c) => {
  c.innerHTML = `<div class="page-enter"><div class="flex items-center justify-between mb-8"><div><h2 class="text-2xl font-black text-white uppercase">Người dùng hệ thống</h2></div><button onclick="editUser()" class="btn-primary flex items-center gap-2"><i data-lucide="plus" class="w-4 h-4"></i> Thêm User</button></div><div class="bg-darkcard rounded-3xl border border-darkborder overflow-hidden" id="user-table-wrap"></div></div>`;
  lucide.createIcons({ nodes:[c] });
  loadUsers();
};
window.loadUsers = async function() {
  const res = await API.get('/api/users');
  const data = res.data || [];
  document.getElementById('user-table-wrap').innerHTML = `<table class="data-table"><thead><tr><th>Tên đăng nhập</th><th>Họ tên</th><th>Vai trò</th><th>Thao tác</th></tr></thead><tbody>${data.map(u=>`<tr><td class="font-mono text-white">${escHtml(u.username)}</td><td class="font-bold">${escHtml(u.fullName)}</td><td>${statusBadge(u.role)}</td><td><button onclick='editUser(${JSON.stringify(u).replace(/'/g,"&#39;")})' class="p-2 text-blue-500 hover:bg-blue-500/10 rounded-lg"><i data-lucide="edit-3" class="w-4 h-4"></i></button><button onclick="deleteItem('users','${u.id}',loadUsers)" class="p-2 text-red-500 hover:bg-red-500/10 rounded-lg"><i data-lucide="trash-2" class="w-4 h-4"></i></button></td></tr>`).join('')}</tbody></table>${data.length===0?'<div class="p-10 text-center text-slate-500">Chưa có dữ liệu.</div>':''}`;
  lucide.createIcons({ nodes: [document.getElementById('user-table-wrap')] });
}
window.editUser = function(u=null) {
  openModal(`<div class="p-8"><h3 class="text-xl font-black text-white uppercase mb-6">${u?'Sửa người dùng':'Thêm người dùng'}</h3><div class="grid grid-cols-2 gap-4 mb-8">
    <div class="col-span-2 space-y-2"><label class="lbl">Họ tên</label><input id="u-name" type="text" value="${escHtml(u?.fullName||'')}" class="form-input" placeholder="Nguyễn Văn A"></div>
    <div class="space-y-2"><label class="lbl">Vai trò</label><select id="u-role" class="form-input"><option value="PT" ${u?.role==='PT'?'selected':''}>HLV (PT)</option><option value="ADMIN" ${u?.role==='ADMIN'?'selected':''}>Quản trị viên</option></select></div>
    <div class="space-y-2"><label class="lbl">Tên đăng nhập</label><input id="u-user" type="text" value="${escHtml(u?.username||'')}" class="form-input" ${u?'readonly':''}></div>
    <div class="space-y-2"><label class="lbl">Mật khẩu</label><input id="u-pass" type="password" class="form-input" placeholder="${u?'Bỏ trống để giữ nguyên':'Nhập mật khẩu'}"></div>
  </div><div class="flex justify-end gap-3"><button onclick="closeModal()" class="btn-gray">Hủy</button><button onclick="saveUser('${u?.id||''}')" class="btn-primary">Lưu lại</button></div></div>`);
}
window.saveUser = async function(id) {
  const body = { fullName: document.getElementById('u-name').value, role: document.getElementById('u-role').value, username: document.getElementById('u-user').value, password: document.getElementById('u-pass').value };
  const res = id ? await API.put(`/api/users/${id}`, body) : await API.post('/api/users', body);
  if (res.success) { showToast(id?'Đã cập nhật!':'Đã tạo người dùng!', 'success'); closeModal(); loadUsers(); } else showToast(res.error, 'error');
}

/* ─── SPORT edit/save ──────────────────────────────────────────────────────── */
window.editSport = function(s=null) {
  openModal(`<div class="p-8"><h3 class="text-xl font-black text-white uppercase mb-6">${s?'Sửa môn tập':'Thêm môn tập'}</h3><div class="space-y-4 mb-8">
    <div class="space-y-2"><label class="lbl">Tên môn</label><input id="sp-name" type="text" value="${escHtml(s?.sport_name||'')}" class="form-input"></div>
    <div class="space-y-2"><label class="lbl">Mô tả</label><textarea id="sp-desc" class="form-input h-24 resize-none">${escHtml(s?.description||'')}</textarea></div>
  </div><div class="flex justify-end gap-3"><button onclick="closeModal()" class="btn-gray">Hủy</button><button onclick="saveSport('${s?.sport_id||''}')" class="btn-primary">Lưu lại</button></div></div>`);
}
window.saveSport = async function(id) {
  const body = { name: document.getElementById('sp-name').value, description: document.getElementById('sp-desc').value };
  const res = id ? await API.put(`/api/sports/${id}`, body) : await API.post('/api/sports', body);
  if (res.success) { showToast('Đã lưu!', 'success'); closeModal(); loadSports(); } else showToast(res.error, 'error');
}

/* ─── FACILITY edit/save ───────────────────────────────────────────────────── */
window.editFacility = function(f=null) {
  openModal(`<div class="p-8"><h3 class="text-xl font-black text-white uppercase mb-6">${f?'Sửa sân bãi':'Thêm khu vực'}</h3><div class="space-y-4 mb-8">
    <div class="space-y-2"><label class="lbl">Tên sân / Phòng</label><input id="fac-name" type="text" value="${escHtml(f?.facility_name||'')}" class="form-input"></div>
    <div class="space-y-2"><label class="lbl">Vị trí / Tầng</label><input id="fac-loc" type="text" value="${escHtml(f?.location||'')}" class="form-input"></div>
  </div><div class="flex justify-end gap-3"><button onclick="closeModal()" class="btn-gray">Hủy</button><button onclick="saveFacility('${f?.facility_id||''}')" class="btn-primary">Lưu lại</button></div></div>`);
}
window.saveFacility = async function(id) {
  const body = { name: document.getElementById('fac-name').value, location: document.getElementById('fac-loc').value };
  const res = id ? await API.put(`/api/facilities/${id}`, body) : await API.post('/api/facilities', body);
  if (res.success) { showToast('Đã lưu!', 'success'); closeModal(); loadFacilities(); } else showToast(res.error, 'error');
}

/* ─── CLASS edit/save ──────────────────────────────────────────────────────── */
window.editClass = async function(cl=null) {
  const [tr, sp, fa] = await Promise.all([API.get('/api/trainers'), API.get('/api/sports'), API.get('/api/facilities')]);
  const trainers = tr.data||[], sports = sp.data||[], facs = fa.data||[];
  const days = ['Thứ 2','Thứ 3','Thứ 4','Thứ 5','Thứ 6','Thứ 7','Chủ nhật','Hằng ngày'];
  openModal(`<div class="p-8"><h3 class="text-xl font-black text-white uppercase mb-6">${cl?'Sửa lớp học':'Thêm lớp học'}</h3><div class="grid grid-cols-2 gap-4 mb-8">
    <div class="col-span-2 space-y-2"><label class="lbl">Tên lớp</label><input id="cl-name" type="text" value="${escHtml(cl?.name||'')}" class="form-input"></div>
    <div class="space-y-2"><label class="lbl">Huấn luyện viên</label><select id="cl-trainer" class="form-input">${trainers.map(t=>`<option value="${t.id}" ${cl?.trainerId==t.id?'selected':''}>${escHtml(t.fullName)}</option>`).join('')}</select></div>
    <div class="space-y-2"><label class="lbl">Môn thể thao</label><select id="cl-sport" class="form-input">${sports.map(s=>`<option value="${s.sport_id}" ${cl?.sportId==s.sport_id?'selected':''}>${escHtml(s.sport_name)}</option>`).join('')}</select></div>
    <div class="space-y-2"><label class="lbl">Sân bãi</label><select id="cl-fac" class="form-input">${facs.map(f=>`<option value="${f.facility_id}" ${cl?.facilityId==f.facility_id?'selected':''}>${escHtml(f.facility_name)}</option>`).join('')}</select></div>
    <div class="space-y-2"><label class="lbl">Buổi trong tuần</label><select id="cl-day" class="form-input">${days.map(d=>`<option value="${d}" ${cl?.dayOfWeek==d?'selected':''}>${d}</option>`).join('')}</select></div>
    <div class="space-y-2"><label class="lbl">Giờ (VD: 08:00 - 09:30)</label><input id="cl-time" type="text" value="${cl?.time||'08:00 - 09:30'}" class="form-input"></div>
    <div class="space-y-2"><label class="lbl">Sức chứa</label><input id="cl-cap" type="number" value="${cl?.capacity||20}" class="form-input"></div>
    <div class="space-y-2"><label class="lbl">Học phí (VND)</label><input id="cl-price" type="number" value="${cl?.price||0}" class="form-input"></div>
  </div><div class="flex justify-end gap-3"><button onclick="closeModal()" class="btn-gray">Hủy</button><button onclick="saveClass('${cl?.id||''}')" class="btn-primary">Lưu lại</button></div></div>`);
}
window.saveClass = async function(id) {
  const body = { name: document.getElementById('cl-name').value, trainerId: document.getElementById('cl-trainer').value, sportId: document.getElementById('cl-sport').value, facilityId: document.getElementById('cl-fac').value, dayOfWeek: document.getElementById('cl-day').value, time: document.getElementById('cl-time').value, capacity: document.getElementById('cl-cap').value, price: document.getElementById('cl-price').value };
  const res = id ? await API.put(`/api/classes/${id}`, body) : await API.post('/api/classes', body);
  if (res.success) { showToast('Đã lưu!', 'success'); closeModal(); loadClasses(); } else showToast(res.error, 'error');
}

/* ─── EVENT edit/save ──────────────────────────────────────────────────────── */
window.editEvent = async function(ev=null) {
  const fa = await API.get('/api/facilities');
  const facs = fa.data||[];
  const statuses = ['UPCOMING','ONGOING','COMPLETED','CANCELLED'];
  openModal(`<div class="p-8"><h3 class="text-xl font-black text-white uppercase mb-6">${ev?'Sửa sự kiện':'Tạo sự kiện'}</h3><div class="grid grid-cols-2 gap-4 mb-8">
    <div class="col-span-2 space-y-2"><label class="lbl">Tên sự kiện</label><input id="ev-name" type="text" value="${escHtml(ev?.ten||'')}" class="form-input"></div>
    <div class="col-span-2 space-y-2"><label class="lbl">Mô tả</label><textarea id="ev-desc" class="form-input h-20 resize-none">${escHtml(ev?.mo_ta||'')}</textarea></div>
    <div class="space-y-2"><label class="lbl">Ngày tổ chức</label><input id="ev-date" type="date" value="${ev?.ngay||''}" class="form-input"></div>
    <div class="space-y-2"><label class="lbl">Địa điểm</label><input id="ev-loc" type="text" value="${escHtml(ev?.dia_diem||'')}" class="form-input"></div>
    <div class="space-y-2"><label class="lbl">Giờ bắt đầu</label><input id="ev-start" type="time" value="${ev?.gio||'08:00'}" class="form-input"></div>
    <div class="space-y-2"><label class="lbl">Giờ kết thúc</label><input id="ev-end" type="time" value="${ev?.gio_ket_thuc||'17:00'}" class="form-input"></div>
    <div class="space-y-2"><label class="lbl">Sân bãi</label><select id="ev-fac" class="form-input"><option value="">-- Không chọn --</option>${facs.map(f=>`<option value="${f.facility_id}" ${ev?.facility_id==f.facility_id?'selected':''}>${escHtml(f.facility_name)}</option>`).join('')}</select></div>
    <div class="space-y-2"><label class="lbl">Sức chứa</label><input id="ev-cap" type="number" value="${ev?.suc_chua||50}" class="form-input"></div>
    <div class="space-y-2"><label class="lbl">Phí tham gia (VND)</label><input id="ev-price" type="number" value="${ev?.gia||0}" class="form-input"></div>
    <div class="space-y-2"><label class="lbl">Trạng thái</label><select id="ev-status" class="form-input">${statuses.map(s=>`<option value="${s}" ${(ev?.trang_thai||'UPCOMING')==s?'selected':''}>${s}</option>`).join('')}</select></div>
  </div><div class="flex justify-end gap-3"><button onclick="closeModal()" class="btn-gray">Hủy</button><button onclick="saveEvent('${ev?.id||''}')" class="btn-primary">Lưu lại</button></div></div>`);
}
window.saveEvent = async function(id) {
  const body = { ten: document.getElementById('ev-name').value, mo_ta: document.getElementById('ev-desc').value, ngay: document.getElementById('ev-date').value, dia_diem: document.getElementById('ev-loc').value, gio: document.getElementById('ev-start').value, gio_ket_thuc: document.getElementById('ev-end').value, facility_id: document.getElementById('ev-fac').value, suc_chua: document.getElementById('ev-cap').value, gia: document.getElementById('ev-price').value, trang_thai: document.getElementById('ev-status').value };
  const res = id ? await API.put(`/api/events/${id}`, body) : await API.post('/api/events', body);
  if (res.success) { showToast('Đã lưu!', 'success'); closeModal(); loadEvents(); } else showToast(res.error, 'error');
}

/* ─── BILLING add invoice ──────────────────────────────────────────────────── */
window.addInvoice = async function() {
  const mr = await API.get('/api/members');
  const members = mr.data||[];
  openModal(`<div class="p-8"><h3 class="text-xl font-black text-white uppercase mb-6">Tạo hóa đơn</h3><div class="grid grid-cols-2 gap-4 mb-8">
    <div class="col-span-2 space-y-2"><label class="lbl">Hội viên</label><select id="inv-member" class="form-input"><option value="">-- Chọn hội viên --</option>${members.map(m=>`<option value="${m.id}">${escHtml(m.fullName)}</option>`).join('')}</select></div>
    <div class="space-y-2"><label class="lbl">Số tiền (VND)</label><input id="inv-amount" type="number" class="form-input" placeholder="500000"></div>
    <div class="space-y-2"><label class="lbl">Phương thức</label><select id="inv-method" class="form-input"><option value="Cash">Tiền mặt</option><option value="Transfer">Chuyển khoản</option><option value="Card">Thẻ</option></select></div>
    <div class="space-y-2"><label class="lbl">Trạng thái</label><select id="inv-status" class="form-input"><option value="PAID">Đã thanh toán</option><option value="UNPAID">Chưa thanh toán</option></select></div>
  </div><div class="flex justify-end gap-3"><button onclick="closeModal()" class="btn-gray">Hủy</button><button onclick="saveInvoice()" class="btn-primary">Tạo hóa đơn</button></div></div>`);
}
window.saveInvoice = async function() {
  const memberId = document.getElementById('inv-member').value;
  if (!memberId) { showToast('Vui lòng chọn hội viên', 'error'); return; }
  const body = { memberId, totalAmount: document.getElementById('inv-amount').value, paymentMethod: document.getElementById('inv-method').value, paymentStatus: document.getElementById('inv-status').value };
  const res = await API.post('/api/billing', body);
  if (res.success) { showToast('Đã tạo hóa đơn!', 'success'); closeModal(); navigate('billing'); } else showToast(res.error, 'error');
}

/* ─── CLASS enrollment UI ──────────────────────────────────────────────────── */
window.manageEnrollment = async function(cl) {
  window._lastEnrollClass = cl;
  const [mr, allCls] = await Promise.all([API.get('/api/members'), API.get('/api/classes')]);
  const allMembers = mr.data||[];
  const clData = (allCls.data||[]).find(c=>c.id===cl.id) || cl;
  const enrolled = clData.enrolledIds||[];
  const enrolledSet = new Set(enrolled);
  openModal(`<div class="p-8"><h3 class="text-xl font-black text-white uppercase mb-2">${escHtml(cl.name)}</h3><p class="text-slate-500 text-xs mb-6">${enrolled.length}/${cl.capacity} học viên</p>
    <div class="space-y-2 max-h-80 overflow-y-auto custom-scrollbar mb-6">${allMembers.map(m=>`
      <div class="flex items-center justify-between p-3 rounded-xl ${enrolledSet.has(m.id)?'bg-primary-500/10 border border-primary-500/20':'bg-slate-900/50 border border-slate-800'}">
        <div><span class="text-sm font-bold text-white">${escHtml(m.fullName)}</span><div class="text-xs text-slate-500">${escHtml(m.phone)}</div></div>
        ${enrolledSet.has(m.id)
          ? `<button onclick="unenrollMember('${cl.id}','${m.id}')" class="text-xs px-3 py-1 bg-red-500/10 text-red-400 rounded-lg hover:bg-red-500 hover:text-white transition-all">Xóa</button>`
          : `<button onclick="enrollMember('${cl.id}','${m.id}')" class="text-xs px-3 py-1 bg-green-500/10 text-green-400 rounded-lg hover:bg-green-500 hover:text-white transition-all">Thêm</button>`}
      </div>`).join('')}
    </div><div class="flex justify-end"><button onclick="closeModal()" class="btn-gray">Đóng</button></div></div>`);
}
window.enrollMember = async function(classId, memberId) {
  const res = await API.post(`/api/classes/${classId}/enroll`, { memberId });
  if (res.success) { showToast('Đã đăng ký!', 'success'); manageEnrollment({id:classId, ten:window._lastEnrollClass?.ten, suc_chua:window._lastEnrollClass?.suc_chua}); } else showToast(res.error, 'error');
}
window.unenrollMember = async function(class_id, member_id) {
  const res = await API.delete(`/api/classes/${class_id}/enroll/${member_id}`);
  if (res.success) { showToast('Đã xóa!', 'success'); manageEnrollment({id:class_id, ten:window._lastEnrollClass?.ten, suc_chua:window._lastEnrollClass?.suc_chua}); } else showToast(res.error, 'error');
}

/* ─── PLANS ─────────────────────────────────────────────────────────────────── */
PAGE_RENDERERS['plans'] = async (c) => {
  c.innerHTML = `<div class="page-enter"><div class="flex items-center justify-between mb-8"><div><h2 class="text-2xl font-black text-white uppercase">Gói tập & Dịch vụ</h2></div><button onclick="editPlan()" class="btn-primary flex items-center gap-2"><i data-lucide="plus" class="w-4 h-4"></i> Thêm gói tập</button></div><div class="grid grid-cols-1 md:grid-cols-3 gap-6" id="plan-list-wrap"></div></div>`;
  lucide.createIcons({ nodes:[c] });
  loadPlans();
};
window.loadPlans = async function() {
  const res = await API.get('/api/plans');
  const data = res.data || [];
  document.getElementById('plan-list-wrap').innerHTML = data.map(p=>`<div class="bg-darkcard rounded-3xl border border-darkborder p-6 group relative">
    <h4 class="text-white font-bold uppercase mb-2 text-sm">${escHtml(p.name)}</h4>
    <p class="text-slate-500 text-[10px] mb-4 leading-relaxed">${escHtml(p.description || 'Chưa có mô tả')}</p>
    <div class="space-y-2 mb-6 text-xs text-slate-500 font-medium">
      <div class="flex items-center gap-2"><i data-lucide="tag" class="w-3.5 h-3.5 text-primary-500"></i> Loai: ${p.type}</div>
      <div class="flex items-center gap-2"><i data-lucide="clock" class="w-3.5 h-3.5 text-primary-500"></i> Thời hạn: ${p.durationMonths || 0} tháng</div>
    </div>
    <div class="flex items-center justify-between pt-4 border-t border-darkborder mb-4">
      <div class="text-lg font-black text-white">${fmtCurrency(p.price)}</div>
      ${statusBadge('ACTIVE')}
    </div>
    <div class="flex gap-2">
      <button onclick='editPlan(${JSON.stringify(p).replace(/'/g,"&#39;")})' class="flex-1 py-2 bg-slate-800 hover:bg-slate-700 text-white text-[10px] font-bold uppercase rounded-xl transition-all">Sửa</button>
      <button onclick="deleteItem('plans','${p.id}',loadPlans)" class="py-2 px-3 bg-red-500/10 text-red-500 hover:bg-red-500 hover:text-white rounded-xl transition-all"><i data-lucide="trash-2" class="w-3.5 h-3.5"></i></button>
    </div>
  </div>`).join('') + (data.length===0?'<div class="col-span-3 p-20 text-center text-slate-500">Chưa có dữ liệu.</div>':'');
  lucide.createIcons({ nodes:[document.getElementById('plan-list-wrap')] });
}
window.editPlan = function(p=null) {
  const types = ['MEMBERSHIP', 'CLASS', 'PT'];
  openModal(`<div class="p-8"><h3 class="text-xl font-black text-white uppercase mb-6">${p?'Sửa gói tập':'Thêm gói tập'}</h3><div class="grid grid-cols-2 gap-4 mb-8">
    <div class="col-span-2 space-y-2"><label class="lbl">Tên gói</label><input id="p-name" type="text" value="${escHtml(p?.name||'')}" class="form-input"></div>
    <div class="space-y-2"><label class="lbl">Loại</label><select id="p-type" class="form-input">${types.map(t=>`<option value="${t}" ${p?.type==t?'selected':''}>${t}</option>`).join('')}</select></div>
    <div class="space-y-2"><label class="lbl">Giá (VND)</label><input id="p-price" type="number" value="${p?.price||0}" class="form-input"></div>
    <div class="space-y-2"><label class="lbl">Thời hạn (Tháng)</label><input id="p-duration" type="number" value="${p?.durationMonths||1}" class="form-input"></div>
    <div class="col-span-2 space-y-2"><label class="lbl">Mô tả</label><textarea id="p-desc" class="form-input h-20 resize-none">${escHtml(p?.description||'')}</textarea></div>
  </div><div class="flex justify-end gap-3"><button onclick="closeModal()" class="btn-gray">Hủy</button><button onclick="savePlan('${p?.id||''}')" class="btn-primary">Lưu lại</button></div></div>`);
}
window.savePlan = async function(id) {
  const body = { name: document.getElementById('p-name').value, type: document.getElementById('p-type').value, price: document.getElementById('p-price').value, durationMonths: document.getElementById('p-duration').value, description: document.getElementById('p-desc').value };
  const res = id ? await API.put(`/api/plans/${id}`, body) : await API.post('/api/plans', body);
  if (res.success) { showToast('Đã lưu!', 'success'); closeModal(); loadPlans(); } else showToast(res.error, 'error');
}

/* ─── THE HỘI VIÊN ──────────────────────────────────────────────────────────── */
PAGE_RENDERERS['member_cards'] = async (c) => {
  c.innerHTML = `<div class="page-enter">
    <div class="flex items-center justify-between mb-8">
      <h2 class="text-2xl font-black text-white uppercase">Thẻ Hội Viên</h2>
      <button onclick="issueCard()" class="btn-primary flex items-center gap-2"><i data-lucide="plus" class="w-4 h-4"></i> Cấp thẻ mới</button>
    </div>
    <div class="bg-darkcard rounded-3xl border border-darkborder overflow-hidden">
      <table class="data-table w-full"><thead><tr>
        <th>Họ tên</th><th>Số thẻ</th><th>Ngày cấp</th><th>Hạn SD</th><th>Trạng thái</th><th>Thao tác</th>
      </tr></thead><tbody id="card-table-body"></tbody></table>
    </div></div>`;
  lucide.createIcons({nodes:[c]});
  loadMemberCards();
};
window.loadMemberCards = async function() {
  const res = await API.get('/api/member-cards');
  const data = res.data||[];
  document.getElementById('card-table-body').innerHTML = data.length===0
    ? '<tr><td colspan="6" class="text-center py-10 text-slate-500">Chua co the nao duoc cap.</td></tr>'
    : data.map(c=>`<tr>
        <td><span class="font-bold text-white">${escHtml(c.fullName)}</span><div class="text-xs text-slate-500">${escHtml(c.phone)}</div></td>
        <td><span class="font-mono text-primary-400 font-bold">${escHtml(c.cardNumber)}</span></td>
        <td class="text-slate-400">${c.issueDate||'-'}</td>
        <td class="text-slate-400">${c.expiryDate||'-'}</td>
        <td>${statusBadge(c.status)}</td>
        <td><div class="flex gap-2">
          <button onclick="revokeCard('${c.id}')" class="text-xs px-2 py-1 bg-red-500/10 text-red-400 rounded-lg hover:bg-red-500 hover:text-white transition-all">Thu hoi</button>
          <button onclick="deleteItem('member-cards','${c.id}',loadMemberCards)" class="text-xs px-2 py-1 bg-slate-800 text-slate-400 rounded-lg hover:bg-red-500 hover:text-white transition-all">Xóa</button>
        </div></td>
      </tr>`).join('');
};
window.issueCard = async function() {
  const mr = await API.get('/api/members');
  const members = mr.data||[];
  const today = new Date().toISOString().split('T')[0];
  const expiry = new Date(Date.now()+365*24*3600*1000).toISOString().split('T')[0];
  openModal(`<div class="p-8"><h3 class="text-xl font-black text-white uppercase mb-6">Cap the hội viên</h3>
    <div class="space-y-4 mb-8">
      <div class="space-y-2"><label class="lbl">Hội viên *</label>
        <select id="card-member" class="form-input"><option value="">-- Chon hội viên --</option>
          ${members.map(m=>`<option value="${m.id}">${escHtml(m.fullName)} - ${escHtml(m.phone)}</option>`).join('')}
        </select></div>
      <div class="grid grid-cols-2 gap-4">
        <div class="space-y-2"><label class="lbl">Ngày cấp</label><input id="card-issue" type="date" value="${today}" class="form-input"></div>
        <div class="space-y-2"><label class="lbl">Han su dung</label><input id="card-expiry" type="date" value="${expiry}" class="form-input"></div>
      </div>
      <div class="space-y-2"><label class="lbl">Ghi chú</label><input id="card-note" type="text" class="form-input" placeholder="Ghi chú them..."></div>
    </div>
    <div class="flex justify-end gap-3"><button onclick="closeModal()" class="btn-gray">Hủy</button>
      <button onclick="saveCard()" class="btn-primary">Cap the</button></div></div>`);
};
window.saveCard = async function() {
  const body = { memberId: document.getElementById('card-member').value, issueDate: document.getElementById('card-issue').value, expiryDate: document.getElementById('card-expiry').value, note: document.getElementById('card-note').value };
  if (!body.memberId) { showToast('Vui long chon hội viên', 'error'); return; }
  const res = await API.post('/api/member-cards', body);
  if (res.success) { showToast(`Da cap the: ${res.cardNumber}`, 'success'); closeModal(); loadMemberCards(); } else showToast(res.error, 'error');
};
window.revokeCard = async function(id) {
  const res = await API.put(`/api/member-cards/${id}`, {status:'REVOKED'});
  if (res.success) { showToast('Da thu hoi the!', 'success'); loadMemberCards(); } else showToast(res.error, 'error');
};

/* ─── CHECK-IN / CHECK-OUT ──────────────────────────────────────────────────── */
PAGE_RENDERERS['checkin'] = async (c) => {
  const today = new Date().toISOString().split('T')[0];
  c.innerHTML = `<div class="page-enter">
    <div class="flex items-center justify-between mb-6">
      <h2 class="text-2xl font-black text-white uppercase">Check-in / Check-out</h2>
      <div class="flex items-center gap-3">
        <input id="ci-date" type="date" value="${today}" class="form-input w-44" onchange="loadCheckins()">
        <button onclick="doCheckin()" class="btn-primary flex items-center gap-2"><i data-lucide="log-in" class="w-4 h-4"></i> Check-in</button>
      </div>
    </div>
    <div class="grid grid-cols-3 gap-4 mb-6" id="ci-stats">
      <div class="bg-darkcard p-5 rounded-2xl border border-darkborder text-center">
        <div class="text-3xl font-black text-blue-400" id="stat-today">-</div>
        <div class="text-xs text-slate-500 font-bold uppercase mt-1">Luot hom nay</div>
      </div>
      <div class="bg-darkcard p-5 rounded-2xl border border-darkborder text-center">
        <div class="text-3xl font-black text-green-400" id="stat-inside">-</div>
        <div class="text-xs text-slate-500 font-bold uppercase mt-1">Dang trong CLB</div>
      </div>
      <div class="bg-darkcard p-5 rounded-2xl border border-darkborder text-center">
        <div class="text-3xl font-black text-orange-400" id="stat-chart-wrap">-</div>
        <div class="text-xs text-slate-500 font-bold uppercase mt-1">Trung binh 7 ngay</div>
      </div>
    </div>
    <div class="bg-darkcard rounded-3xl border border-darkborder overflow-hidden">
      <table class="data-table"><thead><tr>
        <th>Họ tên</th><th>Số thẻ</th><th>Giờ vào</th><th>Giờ ra</th><th>Loai</th><th>Thao tác</th>
      </tr></thead><tbody id="ci-table-body"></tbody></table>
    </div></div>`;
  lucide.createIcons({nodes:[c]});
  loadCheckins();
  loadCheckinStats();
};
window.loadCheckins = async function() {
  const date = document.getElementById('ci-date')?.value || new Date().toISOString().split('T')[0];
  const res = await API.get(`/api/checkins?date=${date}`);
  const data = res.data||[];
  document.getElementById('ci-table-body').innerHTML = data.length===0
    ? '<tr><td colspan="6" class="text-center py-10 text-slate-500">Chua co luot check-in nao.</td></tr>'
    : data.map(r=>`<tr>
        <td><span class="font-bold text-white">${escHtml(r.fullName)}</span><div class="text-xs text-slate-500">${escHtml(r.phone)}</div></td>
        <td><span class="font-mono text-xs text-slate-400">${r.cardNumber||'MANUAL'}</span></td>
        <td class="text-green-400 font-bold">${r.checkInTime ? new Date(r.checkInTime).toLocaleTimeString('vi-VN',{hour:'2-digit',minute:'2-digit'}) : '-'}</td>
        <td class="${r.checkOutTime?'text-red-400':'text-yellow-400'} font-bold">${r.checkOutTime ? new Date(r.checkOutTime).toLocaleTimeString('vi-VN',{hour:'2-digit',minute:'2-digit'}) : 'Chua ra'}</td>
        <td><span class="badge ${r.checkType==='CARD'?'badge-blue':'badge-gray'}">${r.checkType}</span></td>
        <td><div class="flex gap-2">
          ${!r.checkOutTime ? `<button onclick="doCheckout('${r.id}')" class="text-xs px-2 py-1 bg-green-500/10 text-green-400 rounded-lg hover:bg-green-500 hover:text-white transition-all">Check-out</button>` : ''}
          <button onclick="deleteItem('checkins','${r.id}',loadCheckins)" class="text-xs px-2 py-1 bg-slate-800 text-slate-400 rounded-lg hover:bg-red-500 hover:text-white transition-all">Xóa</button>
        </div></td>
      </tr>`).join('');
};
window.loadCheckinStats = async function() {
  const res = await API.get('/api/checkins/stats');
  if (!res.success) return;
  const d = res.data;
  const todayEl = document.getElementById('stat-today');
  const insideEl = document.getElementById('stat-inside');
  const avgEl = document.getElementById('stat-chart-wrap');
  if (todayEl) todayEl.textContent = d.today;
  if (insideEl) insideEl.textContent = d.inside;
  if (avgEl && d.by_day.length) {
    const avg = Math.round(d.by_day.reduce((a,b)=>a+b.luot,0)/d.by_day.length);
    avgEl.textContent = avg;
  }
};
window.doCheckin = async function() {
  const mr = await API.get('/api/members');
  const members = mr.data||[];
  openModal(`<div class="p-8"><h3 class="text-xl font-black text-white uppercase mb-6">Check-in hội viên</h3>
    <div class="space-y-4 mb-8">
      <div class="space-y-2 relative">
        <label class="lbl">Hội viên *</label>
        <input type="hidden" id="ci-member" value="">
        <div class="relative">
          <i data-lucide="search" class="w-4 h-4 absolute left-4 top-1/2 -translate-y-1/2 text-slate-400"></i>
          <input type="text" id="ci-member-search" class="form-input pl-11 focus:ring-primary-500 focus:border-primary-500" placeholder="Nhập tên hoặc số điện thoại..." autocomplete="off" onfocus="document.getElementById('ci-dropdown').classList.remove('hidden')" onblur="setTimeout(()=>document.getElementById('ci-dropdown').classList.add('hidden'), 200)" onkeyup="filterCustomSelect('ci-member-search', 'ci-dropdown')">
        </div>
        <div id="ci-dropdown" class="hidden absolute z-50 w-full mt-1 bg-slate-800 border border-slate-700 rounded-xl shadow-2xl max-h-56 overflow-y-auto custom-scrollbar p-1">
          ${members.map(m=>`<div class="custom-option px-4 py-2.5 hover:bg-primary-500/20 cursor-pointer rounded-lg text-sm transition-colors text-white flex items-center justify-between" onclick="selectCustomOption('ci-member', 'ci-member-search', '${m.id}', '${escHtml(m.ho_ten || m.fullName)} - ${escHtml(m.so_dien_thoai || m.phone)}')"><span>${escHtml(m.ho_ten || m.fullName)}</span><span class="text-xs text-slate-400 font-mono">${escHtml(m.so_dien_thoai || m.phone)}</span></div>`).join('')}
        </div>
      </div>
      <div class="space-y-2"><label class="lbl">Phương thức</label>
        <select id="ci-type" class="form-input"><option value="MANUAL">Thu cong</option><option value="CARD">Quet the</option></select></div>
      <div class="space-y-2"><label class="lbl">Ghi chú</label><input id="ci-note" type="text" class="form-input" placeholder="..."></div>
    </div>
    <div class="flex justify-end gap-3"><button onclick="closeModal()" class="btn-gray">Hủy</button>
      <button onclick="saveCheckin()" class="btn-primary">Check-in ngay</button></div></div>`);
};
window.saveCheckin = async function() {
  const body = { memberId: document.getElementById('ci-member').value, checkType: document.getElementById('ci-type').value, note: document.getElementById('ci-note').value };
  if (!body.memberId) { showToast('Vui long chon hội viên', 'error'); return; }
  const res = await API.post('/api/checkins', body);
  if (res.success) { showToast(`Check-in luc ${res.checkInTime}`, 'success'); closeModal(); loadCheckins(); loadCheckinStats(); } else showToast(res.error, 'error');
};
window.doCheckout = async function(id) {
  const res = await API.put(`/api/checkins/${id}/checkout`, {});
  if (res.success) { showToast(`Check-out luc ${res.checkOutTime}`, 'success'); loadCheckins(); loadCheckinStats(); } else showToast(res.error, 'error');
};

/* ─── CHẤM CÔNG HLV ─────────────────────────────────────────────────────────── */
PAGE_RENDERERS['trainer_attendance'] = async (c) => {
  const now = new Date();
  const m = now.getMonth()+1, y = now.getFullYear();
  c.innerHTML = `<div class="page-enter">
    <div class="flex items-center justify-between mb-6">
      <h2 class="text-2xl font-black text-white uppercase">Chấm công & Lương HLV</h2>
      <div class="flex items-center gap-3">
        <select id="att-month" class="form-input w-32" onchange="loadAttendance()">
          ${[1,2,3,4,5,6,7,8,9,10,11,12].map(i=>`<option value="${i}" ${i===m?'selected':''}>Tháng ${i}</option>`).join('')}
        </select>
        <input id="att-year" type="number" value="${y}" class="form-input w-24" onchange="loadAttendance()">
        <button onclick="addAttendance()" class="btn-primary flex items-center gap-2"><i data-lucide="plus" class="w-4 h-4"></i> Thêm công</button>
      </div>
    </div>

    <div class="mb-12">
      <h3 class="text-sm font-bold text-slate-500 uppercase mb-4 tracking-wider flex items-center gap-2">
        <i data-lucide="calculator" class="w-4 h-4"></i> Bảng lương dự kiến
      </h3>
      <div id="payroll-grid" class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4"></div>
    </div>

    <h3 class="text-sm font-bold text-slate-500 uppercase mb-4 tracking-wider flex items-center gap-2">
      <i data-lucide="list" class="w-4 h-4"></i> Chi tiết chấm công
    </h3>
    <div class="bg-darkcard rounded-3xl border border-darkborder overflow-hidden">
      <table class="data-table"><thead><tr>
        <th>HLV</th><th>Ngày</th><th>Giờ vào</th><th>Giờ ra</th><th>Số buổi</th><th>Trạng thái</th><th>Thao tác</th>
      </tr></thead><tbody id="att-table-body"></tbody></table>
    </div></div>`;
  lucide.createIcons({nodes:[c]});
  loadAttendance();
};
window.loadAttendance = async function() {
  const month = document.getElementById('att-month')?.value;
  const year = document.getElementById('att-year')?.value;
  
  // Load Attendance
  const res = await API.get(`/api/trainer-attendance?month=${month}&year=${year}`);
  const data = res.data||[];
  document.getElementById('att-table-body').innerHTML = data.length===0
    ? '<tr><td colspan="7" class="text-center py-10 text-slate-500">Chưa có dữ liệu chấm công.</td></tr>'
    : data.map(r=>`<tr>
        <td class="font-bold text-white">${escHtml(r.trainerName)}</td>
        <td class="text-slate-400">${r.attendanceDate}</td>
        <td class="text-green-400 font-mono text-xs">${r.checkIn||'-'}</td>
        <td class="text-red-400 font-mono text-xs">${r.checkOut||'-'}</td>
        <td><span class="badge badge-blue">${r.sessionsCount} buổi</span></td>
        <td>${statusBadge(r.status)}</td>
        <td><button onclick="deleteItem('trainer-attendance','${r.id}',loadAttendance)" class="text-xs px-2 py-1 bg-red-500/10 text-red-400 rounded-lg hover:bg-red-500 hover:text-white transition-all font-bold">Xóa</button></td>
      </tr>`).join('');

  // Load Payroll
  const payRes = await API.get(`/api/trainer-payroll?month=${month}&year=${year}`);
  const payroll = payRes.data || [];
  document.getElementById('payroll-grid').innerHTML = payroll.map(p => `
    <div class="bg-darkcard border border-darkborder rounded-2xl p-5 shadow-lg">
      <div class="flex items-center justify-between mb-4">
        <h4 class="font-black text-white uppercase">${escHtml(p.trainerName)}</h4>
        <div class="text-xs font-bold text-primary-500">${escHtml(p.specialty)}</div>
      </div>
      <div class="grid grid-cols-3 gap-2 mb-4">
        <div class="text-center p-2 bg-slate-900/50 rounded-xl">
          <div class="text-[10px] text-slate-500 uppercase font-bold">Buổi</div>
          <div class="text-lg font-black text-white">${p.sessions}</div>
        </div>
        <div class="text-center p-2 bg-slate-900/50 rounded-xl">
          <div class="text-[10px] text-slate-500 uppercase font-bold">Lớp</div>
          <div class="text-lg font-black text-white">${p.classes}</div>
        </div>
        <div class="text-center p-2 bg-slate-900/50 rounded-xl">
          <div class="text-[10px] text-slate-500 uppercase font-bold">HV</div>
          <div class="text-lg font-black text-white">${p.students}</div>
        </div>
      </div>
      <div class="pt-4 border-t border-darkborder flex justify-between items-center">
        <span class="text-[10px] font-bold text-slate-500 uppercase">Lương dự kiến</span>
        <span class="text-lg font-black text-green-400">${fmtCurrency(p.totalSalary)}</span>
      </div>
    </div>
  `).join('');
};
window.addAttendance = async function() {
  const tr = await API.get('/api/trainers');
  const trainers = tr.data||[];
  const today = new Date().toISOString().split('T')[0];
  openModal(`<div class="p-8"><h3 class="text-xl font-black text-white uppercase mb-6">Them cham cong HLV</h3>
    <div class="grid grid-cols-2 gap-4 mb-8">
      <div class="col-span-2 space-y-2 relative">
        <label class="lbl">Huấn luyện viên *</label>
        <input type="hidden" id="att-trainer" value="">
        <div class="relative">
          <i data-lucide="search" class="w-4 h-4 absolute left-4 top-1/2 -translate-y-1/2 text-slate-400"></i>
          <input type="text" id="att-trainer-search" class="form-input pl-11 focus:ring-primary-500 focus:border-primary-500" placeholder="Nhập tên HLV..." autocomplete="off" onfocus="document.getElementById('att-dropdown').classList.remove('hidden')" onblur="setTimeout(()=>document.getElementById('att-dropdown').classList.add('hidden'), 200)" onkeyup="filterCustomSelect('att-trainer-search', 'att-dropdown')">
        </div>
        <div id="att-dropdown" class="hidden absolute z-50 w-full mt-1 bg-slate-800 border border-slate-700 rounded-xl shadow-2xl max-h-48 overflow-y-auto custom-scrollbar p-1">
          ${trainers.map(t=>`<div class="custom-option px-4 py-2.5 hover:bg-primary-500/20 cursor-pointer rounded-lg text-sm transition-colors text-white" onclick="selectCustomOption('att-trainer', 'att-trainer-search', '${t.id}', '${escHtml(t.fullName)}')">${escHtml(t.fullName)}</div>`).join('')}
        </div>
      </div>
      <div class="space-y-2"><label class="lbl">Ngày</label><input id="att-date" type="date" value="${today}" class="form-input"></div>
      <div class="space-y-2"><label class="lbl">Trạng thái</label>
        <select id="att-status" class="form-input"><option value="PRESENT">Co mat</option><option value="LATE">Đi muộn</option><option value="HALF">Nua ngay</option><option value="ABSENT">Vắng mặt</option></select></div>
      <div class="space-y-2"><label class="lbl">Giờ vào</label><input id="att-ci" type="time" value="08:00" class="form-input"></div>
      <div class="space-y-2"><label class="lbl">Giờ ra</label><input id="att-co" type="time" value="17:00" class="form-input"></div>
      <div class="space-y-2"><label class="lbl">Số buổi day</label><input id="att-sessions" type="number" value="0" min="0" class="form-input"></div>
      <div class="space-y-2"><label class="lbl">Ghi chú</label><input id="att-note" type="text" class="form-input" placeholder="..."></div>
    </div>
    <div class="flex justify-end gap-3"><button onclick="closeModal()" class="btn-gray">Hủy</button>
      <button onclick="saveAttendance()" class="btn-primary">Luu cong</button></div></div>`);
};
window.saveAttendance = async function() {
  const body = { trainerId: document.getElementById('att-trainer').value, attendanceDate: document.getElementById('att-date').value, checkIn: document.getElementById('att-ci').value, checkOut: document.getElementById('att-co').value, status: document.getElementById('att-status').value, sessionsCount: document.getElementById('att-sessions').value, note: document.getElementById('att-note').value };
  if (!body.trainerId) { showToast('Vui long chon HLV', 'error'); return; }
  const res = await API.post('/api/trainer-attendance', body);
  if (res.success) { showToast('Da luu cham cong!', 'success'); closeModal(); loadAttendance(); } else showToast(res.error, 'error');
};

/* ─── TÍNH LƯƠNG HLV ────────────────────────────────────────────────────────── */
PAGE_RENDERERS['trainer_salary'] = async (c) => {
  const now = new Date();
  const m = now.getMonth()+1, y = now.getFullYear();
  c.innerHTML = `<div class="page-enter">
    <div class="flex items-center justify-between mb-6">
      <h2 class="text-2xl font-black text-white uppercase">Tính lương HLV</h2>
      <div class="flex items-center gap-3">
        <select id="sal-month" class="form-input w-32" onchange="loadSalary()">
          ${[1,2,3,4,5,6,7,8,9,10,11,12].map(i=>`<option value="${i}" ${i===m?'selected':''}>Thang ${i}</option>`).join('')}
        </select>
        <input id="sal-year" type="number" value="${y}" class="form-input w-24" onchange="loadSalary()">
        <button onclick="calcSalary()" class="btn-primary flex items-center gap-2"><i data-lucide="calculator" class="w-4 h-4"></i> Tính lương</button>
      </div>
    </div>
    <div id="sal-summary" class="grid grid-cols-3 gap-4 mb-6"></div>
    <div class="bg-darkcard rounded-3xl border border-darkborder overflow-hidden">
      <table class="data-table"><thead><tr>
        <th>HLV</th><th>Chuyên môn</th><th>Lương cơ bản</th><th>Số buổi</th><th>Thưởng buổi</th><th>Tổng lương</th><th>Trạng thái</th><th>Thao tác</th>
      </tr></thead><tbody id="sal-table-body"></tbody></table>
    </div></div>`;
  lucide.createIcons({nodes:[c]});
  loadSalary();
};
window.loadSalary = async function() {
  const month = document.getElementById('sal-month')?.value;
  const year = document.getElementById('sal-year')?.value;
  const res = await API.get(`/api/trainer-salary?month=${month}&year=${year}`);
  const data = res.data||[];
  // Summary
  const totalPaid = data.filter(r=>r.paymentStatus==='PAID').reduce((a,b)=>a+parseFloat(b.totalAmount||0),0);
  const totalPending = data.filter(r=>r.paymentStatus==='PENDING').reduce((a,b)=>a+parseFloat(b.totalAmount||0),0);
  const sumEl = document.getElementById('sal-summary');
  if (sumEl) sumEl.innerHTML = `
    <div class="bg-darkcard p-5 rounded-2xl border border-darkborder text-center"><div class="text-2xl font-black text-green-400">${fmtCurrency(totalPaid)}</div><div class="text-xs text-slate-500 font-bold uppercase mt-1">Da thanh toan</div></div>
    <div class="bg-darkcard p-5 rounded-2xl border border-darkborder text-center"><div class="text-2xl font-black text-yellow-400">${fmtCurrency(totalPending)}</div><div class="text-xs text-slate-500 font-bold uppercase mt-1">Cho thanh toan</div></div>
    <div class="bg-darkcard p-5 rounded-2xl border border-darkborder text-center"><div class="text-2xl font-black text-white">${data.length}</div><div class="text-xs text-slate-500 font-bold uppercase mt-1">Tong HLV</div></div>`;
  document.getElementById('sal-table-body').innerHTML = data.length===0
    ? '<tr><td colspan="8" class="text-center py-10 text-slate-500">Chua co du lieu. Nhan "Tính lương" de tinh tu dong.</td></tr>'
    : data.map(r=>`<tr>
        <td class="font-bold text-white">${escHtml(r.trainerName)}</td>
        <td class="text-slate-400 text-xs">${escHtml(r.specialty||'-')}</td>
        <td class="text-white">${fmtCurrency(r.baseSalary)}</td>
        <td><span class="badge badge-blue">${r.totalSessions} buoi</span></td>
        <td class="text-blue-400">${fmtCurrency(r.sessionBonus)}</td>
        <td class="font-black text-green-400 text-base">${fmtCurrency(r.totalAmount)}</td>
        <td>${r.paymentStatus==='PAID'?'<span class="badge badge-green">Da tra</span>':'<span class="badge badge-yellow">Chua tra</span>'}</td>
        <td><div class="flex gap-2">
          ${r.paymentStatus==='PENDING'?`<button onclick="paySalary('${r.id}')" class="text-xs px-2 py-1 bg-green-500/10 text-green-400 rounded-lg hover:bg-green-500 hover:text-white transition-all">Thanh toan</button>`:''}
        </div></td>
      </tr>`).join('');
};
window.calcSalary = async function() {
  openModal(`<div class="p-8"><h3 class="text-xl font-black text-white uppercase mb-6">Cau hinh tinh luong</h3>
    <div class="space-y-4 mb-8">
      <div class="space-y-2"><label class="lbl">Lương cơ bản (VND)</label><input id="sal-base" type="number" value="5000000" class="form-input"></div>
      <div class="space-y-2"><label class="lbl">Thuong moi buoi day (VND)</label><input id="sal-bonus" type="number" value="150000" class="form-input"></div>
      <div class="p-4 bg-slate-900/50 rounded-xl text-xs text-slate-400">
        Cong thuc: Tổng lương = Lương cơ bản + (Số buổi x Thuong moi buoi)
      </div>
    </div>
    <div class="flex justify-end gap-3"><button onclick="closeModal()" class="btn-gray">Hủy</button>
      <button onclick="runCalcSalary()" class="btn-primary">Tinh ngay</button></div></div>`);
};
window.runCalcSalary = async function() {
  const month = document.getElementById('sal-month').value;
  const year = document.getElementById('sal-year').value;
  const body = { month, year, baseSalary: document.getElementById('sal-base').value, bonusPerSession: document.getElementById('sal-bonus').value };
  const res = await API.post('/api/trainer-salary/calculate', body);
  if (res.success) { showToast('Da tinh luong xong!', 'success'); closeModal(); loadSalary(); } else showToast(res.error, 'error');
};
window.paySalary = async function(id) {
  const res = await API.put(`/api/trainer-salary/${id}/pay`, {});
  if (res.success) { showToast('Da thanh toan luong!', 'success'); loadSalary(); } else showToast(res.error, 'error');
};
