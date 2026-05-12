window.API = {
  async request(url, method = 'GET', body = null) {
    const opts = { method, credentials: 'include', headers: { 'Content-Type': 'application/json' } };
    if (body) opts.body = JSON.stringify(body);
    
    try {
      const res = await fetch(url, opts);
      
      // Xử lý lỗi Unauthorized (401)
      if (res.status === 401) { 
          if (window._appLogout) window._appLogout(); 
          return { success: false, error: 'Hết phiên làm việc' }; 
      }
      
      // Kiểm tra nếu không phải JSON
      const contentType = res.headers.get("content-type");
      if (!contentType || !contentType.includes("application/json")) {
          const text = await res.text();
          console.error("Server returned non-JSON:", text);
          return { success: false, error: 'Phản hồi từ máy chủ không đúng định dạng JSON' };
      }

      return await res.json();
    } catch (err) {
      console.error("API Request failed:", err);
      return { success: false, error: 'Không thể kết nối tới máy chủ' };
    }
  },
  get: (url) => window.API.request(url, 'GET'),
  post: (url, body) => window.API.request(url, 'POST', body),
  put: (url, body) => window.API.request(url, 'PUT', body),
  delete: (url) => window.API.request(url, 'DELETE'),
};
