/* ── Baby Album — App Logic ────────────────────────────────────────── */

let STATE = {
  member: null,           // {id, name, is_admin} or null
  babyName: 'Baby Album',
  babyBirthDate: null,
  page: 1,
  totalPages: 1,
  loading: false,
  hasMore: true,
};

// ── Init ─────────────────────────────────────────────────────────────

document.addEventListener('DOMContentLoaded', async () => {
  const res = await fetch('/api/settings');
  const settings = await res.json();

  if (settings.baby_name) STATE.babyName = settings.baby_name;
  if (settings.baby_birth_date) STATE.babyBirthDate = settings.baby_birth_date;

  if (!settings.setup_done) {
    showSetup();
    return;
  }

  // Check if logged in
  const stored = sessionStorage.getItem('baby_album_member');
  if (stored) {
    STATE.member = JSON.parse(stored);
    showApp();
  } else {
    showLogin();
  }
});

// ── Page Switching ───────────────────────────────────────────────────

function showSetup() {
  document.getElementById('setupPage').classList.add('active');
  document.getElementById('loginPage').classList.remove('active');
  document.getElementById('appContainer').style.display = 'none';
  document.getElementById('appHeader').style.display = 'none';
}

function showLogin() {
  const title = STATE.babyName || 'Baby Album';
  document.getElementById('loginTitle').textContent = `🩷 ${title}`;
  document.getElementById('setupPage').classList.remove('active');
  document.getElementById('loginPage').classList.add('active');
  document.getElementById('appContainer').style.display = 'none';
  document.getElementById('appHeader').style.display = 'none';
}

function showApp() {
  document.getElementById('setupPage').classList.remove('active');
  document.getElementById('loginPage').classList.remove('active');
  document.getElementById('appContainer').style.display = 'block';
  document.getElementById('appHeader').style.display = 'block';

  const title = STATE.babyName || 'Baby Album';
  document.getElementById('headerTitle').textContent = `🩷 ${title}`;
  document.getElementById('headerSubtitle').textContent = `Welcome, ${STATE.member.name}`;

  // Show/hide admin features
  document.getElementById('fabUpload').style.display = STATE.member.is_admin ? 'flex' : 'none';
  document.getElementById('btnMembers').style.display = STATE.member.is_admin ? 'inline-block' : 'none';

  loadPhotos(true);
}

// ── Setup ────────────────────────────────────────────────────────────

async function saveSetup() {
  const name = document.getElementById('babyName').value.trim();
  const date = document.getElementById('birthDate').value;

  if (!name) { toast('Please enter your baby\'s name'); return; }
  if (!date) { toast('Please select the birth date'); return; }

  const form = new FormData();
  form.append('baby_name', name);
  form.append('birth_date', date);

  const res = await fetch('/api/setup', { method: 'POST', body: form });
  if (!res.ok) { toast('Something went wrong'); return; }

  STATE.babyName = name;
  STATE.babyBirthDate = date;

  toast('All set! Now log in as Mom or Dad 🎉');
  document.getElementById('loginTitle').textContent = `🩷 ${name}`;
  showLogin();
}

// ── Login ────────────────────────────────────────────────────────────

async function login() {
  const code = document.getElementById('accessCode').value.trim().toLowerCase();
  if (!code) { toast('Enter your access code'); return; }

  const form = new FormData();
  form.append('access_code', code);

  const res = await fetch('/api/login', { method: 'POST', body: form });
  if (!res.ok) { toast('Invalid access code'); return; }

  STATE.member = await res.json();
  sessionStorage.setItem('baby_album_member', JSON.stringify(STATE.member));
  document.getElementById('accessCode').value = '';

  showApp();
}

function logout() {
  STATE.member = null;
  sessionStorage.removeItem('baby_album_member');
  STATE.page = 1;
  STATE.hasMore = true;
  document.getElementById('timeline').innerHTML = '';
  showLogin();
}

// ── Timeline ─────────────────────────────────────────────────────────

async function loadPhotos(reset = false) {
  if (STATE.loading) return;
  if (!reset && !STATE.hasMore) return;

  STATE.loading = true;

  if (reset) {
    STATE.page = 1;
    document.getElementById('timeline').innerHTML = '';
  }

  document.getElementById('loadingMore').style.display = 'block';

  try {
    const res = await fetch(`/api/photos?page=${STATE.page}&per_page=20`);
    const data = await res.json();

    STATE.totalPages = data.total_pages;
    STATE.hasMore = data.has_more;

    if (data.photos.length === 0 && STATE.page === 1) {
      document.getElementById('emptyState').style.display = 'block';
      document.getElementById('loadingMore').style.display = 'none';
      STATE.loading = false;
      return;
    }

    document.getElementById('emptyState').style.display = 'none';

    const timeline = document.getElementById('timeline');
    for (const photo of data.photos) {
      timeline.appendChild(createPhotoCard(photo));
    }

    STATE.page++;
  } catch (e) {
    console.error('Failed to load photos:', e);
    toast('Failed to load photos');
  }

  document.getElementById('loadingMore').style.display = 'none';
  STATE.loading = false;
}

function createPhotoCard(photo) {
  const card = document.createElement('div');
  card.className = 'card photo-card';
  card.id = `photo-${photo.id}`;

  const ageHtml = photo.age
    ? `<span class="photo-age">${photo.age}</span>`
    : '';

  // Build reactions html
  let reactionsHtml = '';
  if (photo.reactions && photo.reactions.length > 0) {
    reactionsHtml = photo.reactions.map(r =>
      `<button class="reaction-btn active" onclick="toggleReaction(${photo.id}, '${r.emoji}')">
        ${r.emoji} <span class="count">${r.count}</span>
      </button>`
    ).join('');
  }

  // Quick reaction buttons
  const quickEmojis = ['❤️', '😊', '👶', '💕', '🎉'];
  const quickReactionsHtml = quickEmojis.map(e =>
    `<button class="quick-reaction-btn" onclick="toggleReaction(${photo.id}, '${e}')">${e}</button>`
  ).join('');

  card.innerHTML = `
    <img src="${photo.image_url}" alt="${photo.caption || 'Baby photo'}" loading="lazy" onclick="openPhoto(${photo.id})">
    <div class="photo-body">
      <div class="photo-meta">
        <span class="photo-date">${photo.photo_date}</span>
        ${ageHtml}
      </div>
      ${photo.caption ? `<div class="photo-caption">${escapeHtml(photo.caption)}</div>` : ''}
    </div>
    <div class="reactions-bar" id="reactions-${photo.id}">
      ${reactionsHtml}
    </div>
    <div class="quick-reactions">
      ${quickReactionsHtml}
    </div>
  `;

  return card;
}

// ── Reactions ────────────────────────────────────────────────────────

async function toggleReaction(photoId, emoji) {
  if (!STATE.member) return;

  const form = new FormData();
  form.append('member_id', STATE.member.id);
  form.append('emoji', emoji);

  const res = await fetch(`/api/photos/${photoId}/react`, {
    method: 'POST',
    body: form,
  });

  if (!res.ok) return;

  const data = await res.json();

  // Refresh the reactions display for this photo
  const photoRes = await fetch(`/api/photos?page=1&per_page=1000`);
  const allData = await photoRes.json();
  const photo = allData.photos.find(p => p.id === photoId);
  if (photo) {
    updateReactionsBar(photoId, photo.reactions);
  }
}

function updateReactionsBar(photoId, reactions) {
  const bar = document.getElementById(`reactions-${photoId}`);
  if (!bar) return;

  if (reactions && reactions.length > 0) {
    bar.innerHTML = reactions.map(r =>
      `<button class="reaction-btn active" onclick="toggleReaction(${photoId}, '${r.emoji}')">
        ${r.emoji} <span class="count">${r.count}</span>
      </button>`
    ).join('');
  } else {
    bar.innerHTML = '';
  }
}

// ── Upload ───────────────────────────────────────────────────────────

function openUploadModal() {
  document.getElementById('uploadModal').classList.add('active');
  document.getElementById('photoFile').value = '';
  document.getElementById('photoCaption').value = '';
  document.getElementById('photoPreview').classList.remove('show');
}

function closeUploadModal() {
  document.getElementById('uploadModal').classList.remove('active');
}

function previewPhoto() {
  const file = document.getElementById('photoFile').files[0];
  if (!file) return;
  const reader = new FileReader();
  reader.onload = (e) => {
    const preview = document.getElementById('photoPreview');
    preview.src = e.target.result;
    preview.classList.add('show');
  };
  reader.readAsDataURL(file);
}

async function uploadPhoto() {
  const fileInput = document.getElementById('photoFile');
  const caption = document.getElementById('photoCaption').value.trim();

  if (!fileInput.files.length) { toast('Select a photo first'); return; }

  const form = new FormData();
  form.append('file', fileInput.files[0]);
  form.append('caption', caption);

  const res = await fetch('/api/photos/upload', { method: 'POST', body: form });
  if (!res.ok) { toast('Upload failed 😢'); return; }

  toast('Photo uploaded! 🎉');
  closeUploadModal();

  // Reload timeline from the beginning
  loadPhotos(true);
  window.scrollTo({ top: 0, behavior: 'smooth' });
}

// ── Members ──────────────────────────────────────────────────────────

async function showMembers() {
  document.getElementById('membersModal').classList.add('active');
  await refreshMembersList();
}

function closeMembersModal() {
  document.getElementById('membersModal').classList.remove('active');
}

async function refreshMembersList() {
  const res = await fetch('/api/members');
  const members = await res.json();
  const list = document.getElementById('membersList');

  list.innerHTML = '<ul class="member-list">' + members.map(m =>
    `<li class="member-item">
      <span class="member-name">
        ${escapeHtml(m.name)}
        ${m.is_admin ? '<span class="member-badge">Admin</span>' : ''}
      </span>
      <span class="member-code">${escapeHtml(m.access_code)}</span>
    </li>`
  ).join('') + '</ul>';
}

async function addMember() {
  const name = document.getElementById('newMemberName').value.trim();
  const code = document.getElementById('newMemberCode').value.trim().toLowerCase();

  if (!name) { toast('Enter a name'); return; }
  if (!code) { toast('Enter an access code'); return; }

  const form = new FormData();
  form.append('name', name);
  form.append('access_code', code);

  const res = await fetch('/api/members', { method: 'POST', body: form });
  if (!res.ok) {
    const err = await res.json();
    toast(err.detail || 'Failed to add member');
    return;
  }

  toast(`${name} added! Their code is: ${code}`);
  document.getElementById('newMemberName').value = '';
  document.getElementById('newMemberCode').value = '';
  await refreshMembersList();
}

// ── Infinite Scroll ──────────────────────────────────────────────────

let scrollTimeout = null;
window.addEventListener('scroll', () => {
  // Scroll to top button
  const scrollTop = document.getElementById('scrollTop');
  if (window.scrollY > 600) {
    scrollTop.classList.add('show');
  } else {
    scrollTop.classList.remove('show');
  }

  // Infinite scroll
  if (scrollTimeout) clearTimeout(scrollTimeout);
  scrollTimeout = setTimeout(() => {
    const { scrollTop, scrollHeight, clientHeight } = document.documentElement;
    if (scrollTop + clientHeight >= scrollHeight - 600) {
      loadPhotos();
    }
  }, 200);
});

// ── Photo lightbox ───────────────────────────────────────────────────

function openPhoto(photoId) {
  const img = document.querySelector(`#photo-${photoId} img`);
  if (!img) return;

  const overlay = document.createElement('div');
  overlay.style.cssText = `
    position: fixed; inset: 0; background: rgba(0,0,0,0.85);
    display: flex; align-items: center; justify-content: center;
    z-index: 500; cursor: pointer; padding: 20px;
  `;

  const enlarged = document.createElement('img');
  enlarged.src = img.src;
  enlarged.style.cssText = `
    max-width: 100%; max-height: 90vh; border-radius: 12px;
    object-fit: contain; box-shadow: 0 20px 60px rgba(0,0,0,0.5);
  `;

  overlay.appendChild(enlarged);
  overlay.addEventListener('click', () => overlay.remove());
  document.body.appendChild(overlay);
}

// ── Helpers ──────────────────────────────────────────────────────────

function escapeHtml(str) {
  const div = document.createElement('div');
  div.textContent = str;
  return div.innerHTML;
}

let toastTimeout = null;
function toast(msg) {
  const el = document.getElementById('toast');
  el.textContent = msg;
  el.classList.add('show');
  if (toastTimeout) clearTimeout(toastTimeout);
  toastTimeout = setTimeout(() => el.classList.remove('show'), 2500);
}