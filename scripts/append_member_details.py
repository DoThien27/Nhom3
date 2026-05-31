import codecs

code = """
window.viewMemberDetails = async function(id) {
  const [mRes, cRes, bRes] = await Promise.all([
    API.get('/api/members'),
    API.get('/api/member-cards'),
    API.get('/api/billing')
  ]);
  const m = (mRes.data || []).find(x => x.id === id);
  if (!m) return showToast('Không tìm thấy hội viên', 'error');
  
  const cards = (cRes.data || []).filter(c => c.memberId === id);
  const bills = (bRes.data || []).filter(b => b.memberId === id);
  
  openModal(`<div class="p-8">
    <div class="flex items-center gap-4 mb-8 border-b border-darkborder/50 pb-6">
      <div class="w-20 h-20 rounded-2xl bg-orange-500/10 flex items-center justify-center text-primary-500 text-3xl font-bold border border-primary-500/20 shadow-inner">${(m.fullName||'H')[0].toUpperCase()}</div>
      <div>
        <h3 class="text-2xl font-bold text-white uppercase tracking-tight">${escHtml(m.fullName)}</h3>
        <div class="text-sm font-bold text-slate-500 mt-1">${m.email ? escHtml(m.email) : (m.username ? '@' + escHtml(m.username) : 'Chưa có thông tin')}</div>
      </div>
      <div class="ml-auto">${statusBadge(m.status)}</div>
    </div>
    
    <div class="grid grid-cols-2 gap-8 mb-8">
      <div>
        <h4 class="text-xs font-bold text-slate-500 uppercase tracking-widest mb-4 flex items-center gap-2"><i data-lucide="user" class="w-4 h-4"></i> Thông tin cá nhân</h4>
        <div class="space-y-3 bg-darkcard p-4 rounded-2xl border border-darkborder">
          <div class="flex justify-between"><span class="text-xs text-slate-400">Số điện thoại</span><span class="text-sm font-bold text-white">${escHtml(m.phone)}</span></div>
          <div class="flex justify-between"><span class="text-xs text-slate-400">Ngày sinh</span><span class="text-sm font-bold text-white">${m.birthDate ? fmtDate(m.birthDate) : '---'}</span></div>
          <div class="flex justify-between"><span class="text-xs text-slate-400">Giới tính</span><span class="text-sm font-bold text-white">${escHtml(m.gender)}</span></div>
          <div class="flex justify-between"><span class="text-xs text-slate-400">Quê quán</span><span class="text-sm font-bold text-white">${escHtml(m.homeTown || '---')}</span></div>
        </div>
      </div>
      
      <div>
        <h4 class="text-xs font-bold text-slate-500 uppercase tracking-widest mb-4 flex items-center gap-2"><i data-lucide="credit-card" class="w-4 h-4"></i> Thẻ hội viên</h4>
        <div class="space-y-3 bg-darkcard p-4 rounded-2xl border border-darkborder max-h-48 overflow-y-auto custom-scrollbar">
          ${cards.length === 0 ? '<div class="text-center text-xs text-slate-500 py-4">Chưa có thẻ</div>' : cards.map(c => `
            <div class="flex items-center justify-between p-3 bg-slate-800/50 rounded-xl">
              <div>
                <div class="text-sm font-bold text-white">${escHtml(c.cardNumber)}</div>
                <div class="text-xs text-slate-400 mt-1">HSD: ${c.expiryDate ? fmtDate(c.expiryDate) : '---'}</div>
              </div>
              ${statusBadge(c.status)}
            </div>
          `).join('')}
        </div>
      </div>
    </div>
    
    <div>
      <h4 class="text-xs font-bold text-slate-500 uppercase tracking-widest mb-4 flex items-center gap-2"><i data-lucide="banknote" class="w-4 h-4"></i> Lịch sử hóa đơn</h4>
      <div class="bg-darkcard border border-darkborder rounded-2xl overflow-hidden max-h-48 overflow-y-auto custom-scrollbar">
        <table class="w-full text-left border-collapse">
          <thead>
            <tr class="bg-slate-800/50 text-xs font-bold text-slate-500 uppercase tracking-widest">
              <th class="p-3">Mã HĐ</th>
              <th class="p-3">Loại</th>
              <th class="p-3">Số tiền</th>
              <th class="p-3 text-right">Trạng thái</th>
            </tr>
          </thead>
          <tbody>
            ${bills.length === 0 ? '<tr><td colspan="4" class="p-4 text-center text-xs text-slate-500">Không có hóa đơn</td></tr>' : bills.map(b => `
              <tr class="border-t border-darkborder/50 hover:bg-slate-800/20">
                <td class="p-3 text-sm font-bold text-white">${escHtml(b.id)}</td>
                <td class="p-3 text-xs text-slate-400">${escHtml(b.sourceType)}</td>
                <td class="p-3 text-sm font-bold text-primary-500">${fmtCurrency(b.finalAmount)}</td>
                <td class="p-3 text-right">${statusBadge(b.paymentStatus)}</td>
              </tr>
            `).join('')}
          </tbody>
        </table>
      </div>
    </div>
    
    <div class="mt-8 flex justify-end">
      <button onclick="closeModal()" class="btn-gray">Đóng</button>
    </div>
  </div>`);
}
"""

with codecs.open('web/static/js/renderers.js', 'a', encoding='utf-8') as f:
    f.write('\\n' + code + '\\n')
