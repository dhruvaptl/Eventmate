document.addEventListener('DOMContentLoaded', () => {
  initSearch();
  initFilters();
  initStatusToggle();
  initTabs();
  initMobileMenu();
  initFlashDismiss();
});

function initSearch() {
  const searchInput = document.getElementById('searchInput');
  if (!searchInput) return;
  let debounce;
  searchInput.addEventListener('input', () => {
    clearTimeout(debounce);
    debounce = setTimeout(filterCards, 250);
  });
}

function initFilters() {
  const btns = document.querySelectorAll('.filter-btn');
  btns.forEach(btn => {
    btn.addEventListener('click', () => {
      btns.forEach(b => b.classList.remove('active'));
      btn.classList.add('active');
      filterCards();
    });
  });
}

function filterCards() {
  const query = (document.getElementById('searchInput')?.value || '').toLowerCase().trim();
  const activeFilter = document.querySelector('.filter-btn.active')?.dataset.type || 'all';
  const cards = document.querySelectorAll('.event-card');

  let visible = 0;
  cards.forEach((card) => {
    const title = card.dataset.title || '';
    const location = card.dataset.location || '';
    const type = card.dataset.type || '';
    const matchesQuery = !query || title.includes(query) || location.includes(query);
    const matchesFilter = activeFilter === 'all' || type === activeFilter;
    const show = matchesQuery && matchesFilter;
    card.style.display = show ? '' : 'none';
    if (show) { card.style.animationDelay = `${visible * 0.05}s`; visible++; }
  });

  let emptyState = document.getElementById('noResults');
  if (visible === 0 && cards.length > 0) {
    if (!emptyState) {
      emptyState = document.createElement('div');
      emptyState.id = 'noResults';
      emptyState.className = 'empty-state';
      emptyState.innerHTML = '<div class="empty-icon">🔍</div><h3>No events found</h3><p>Try a different search or filter</p>';
      document.getElementById('eventsGrid')?.appendChild(emptyState);
    }
    emptyState.style.display = '';
  } else if (emptyState) {
    emptyState.style.display = 'none';
  }
}

function initStatusToggle() {
  const btn = document.getElementById('statusBtn');
  if (!btn) return;
  btn.addEventListener('click', async () => {
    const current = btn.dataset.status;
    const next = current === 'Free' ? 'Busy' : 'Free';
    const fd = new FormData();
    fd.append('status', next);
    const res = await fetch('/availability', { method: 'POST', body: fd });
    const data = await res.json();
    if (data.success) {
      btn.dataset.status = next;
      btn.className = 'status-btn ' + (next === 'Free' ? 'active-free' : 'active-busy');
      btn.innerHTML = '<span class="status-dot"></span>' + next;
    }
  });
}

function initTabs() {
  const tabBtns = document.querySelectorAll('.tab-btn');
  tabBtns.forEach(btn => {
    btn.addEventListener('click', () => {
      tabBtns.forEach(b => b.classList.remove('active'));
      document.querySelectorAll('.tab-content').forEach(c => c.classList.remove('active'));
      btn.classList.add('active');
      const target = document.getElementById('tab-' + btn.dataset.tab);
      if (target) target.classList.add('active');
    });
  });
}

function initMobileMenu() {
  const btn = document.getElementById('hamburger');
  const menu = document.getElementById('mobileMenu');
  if (!btn || !menu) return;
  btn.addEventListener('click', () => menu.classList.toggle('open'));
  document.addEventListener('click', (e) => {
    if (!menu.contains(e.target) && e.target !== btn) menu.classList.remove('open');
  });
}

function initFlashDismiss() {
  document.querySelectorAll('.flash').forEach(el => {
    setTimeout(() => {
      el.style.transition = 'opacity 0.5s, transform 0.5s';
      el.style.opacity = '0';
      el.style.transform = 'translateY(-8px)';
      setTimeout(() => el.remove(), 500);
    }, 4000);
  });
}

async function sendRequest(receiverId, eventId) {
  const res = await fetch('/requests/send', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ receiver_id: receiverId, event_id: eventId })
  });
  const data = await res.json();
  showToast(data.success ? 'Connection request sent! ⚡' : (data.error || 'Could not send request'), data.success ? 'success' : 'error');
}

async function handleRequest(reqId, action) {
  const res = await fetch('/requests/' + action + '/' + reqId, { method: 'POST' });
  const data = await res.json();
  if (data.success) {
    const card = document.getElementById('req-' + reqId);
    if (card) {
      card.style.transition = 'all 0.3s ease';
      card.style.opacity = '0';
      card.style.transform = 'translateX(20px)';
      setTimeout(() => card.remove(), 300);
    }
    showToast(action === 'accept' ? 'Request accepted! 🎉' : 'Request declined', action === 'accept' ? 'success' : 'error');
  }
}

function showToast(message, type) {
  const existing = document.getElementById('toast');
  if (existing) existing.remove();
  const toast = document.createElement('div');
  toast.id = 'toast';
  toast.textContent = message;
  const isSuccess = type === 'success';
  toast.style.cssText = [
    'position:fixed', 'bottom:24px', 'right:24px',
    'padding:14px 22px', 'border-radius:12px',
    'font-size:14px', 'font-weight:600',
    "font-family:'DM Sans',sans-serif",
    'z-index:9999', 'box-shadow:0 8px 32px rgba(0,0,0,0.4)',
    isSuccess
      ? 'background:rgba(67,224,151,0.15);color:#43e097;border:1px solid rgba(67,224,151,0.3)'
      : 'background:rgba(250,109,109,0.15);color:#fa6d6d;border:1px solid rgba(250,109,109,0.25)'
  ].join(';');
  document.body.appendChild(toast);
  setTimeout(() => {
    toast.style.transition = 'opacity 0.4s,transform 0.4s';
    toast.style.opacity = '0';
    toast.style.transform = 'translateY(10px)';
    setTimeout(() => toast.remove(), 400);
  }, 3000);
}
