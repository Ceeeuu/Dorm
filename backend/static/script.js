const reportList = document.getElementById('reportList');
const roomInput = document.getElementById('room');
const contentInput = document.getElementById('content');
const sendBtn = document.getElementById('sendBtn');

const usernameInput = document.getElementById('username');
const passwordInput = document.getElementById('password');
const loginBtn = document.getElementById('loginBtn');
const registerBtn = document.getElementById('registerBtn');

const userDisplay = document.getElementById('userDisplay');
const logoutBtn = document.getElementById('logoutBtn');

let currentUser = null;

// helper: build report element using textContent (避免 XSS)
function buildReportDOM(report) {
    const div = document.createElement('div');
    div.classList.add('report', 'new');
    const meta = document.createElement('div');
    meta.className = 'meta';
    const nick = document.createElement('span');
    nick.className = 'nickname';
    nick.textContent = report.nickname;
    const room = document.createElement('span');
    room.className = 'room';
    room.textContent = report.room;
    const likeBtn = document.createElement('span');
    likeBtn.className = 'like-btn';
    likeBtn.textContent = `❤ ${report.likes}`;
    likeBtn.style.marginLeft = 'auto';
    meta.appendChild(nick);
    meta.appendChild(room);
    meta.appendChild(likeBtn);

    const content = document.createElement('div');
    content.className = 'content';
    content.textContent = report.content;

    div.appendChild(meta);
    div.appendChild(content);

    // like handler (requires login)
    likeBtn.addEventListener('click', async () => {
        if (!currentUser) {
            alert('請先登入才能讚賞');
            return;
        }
        try {
            const resp = await fetch(`/report/${report.id}/like`, { method: 'POST' });
            const j = await resp.json();
            if (resp.status === 200) {
                likeBtn.textContent = `❤ ${j.likes}`;
            } else {
                alert(j.error || j.message || '點讚失敗');
            }
        } catch (e) {
            console.error(e);
            alert('網路錯誤');
        }
    });

    return div;
}

async function loadReports() {
    const resp = await fetch('/reports');
    const list = await resp.json();
    reportList.innerHTML = '';
    list.forEach(r => {
        const el = buildReportDOM(r);
        reportList.prepend(el); // newest on top
        setTimeout(() => el.classList.remove('new'), 320);
    });
}

function disableForSeconds(btn, s=3) {
    btn.disabled = true;
    setTimeout(() => btn.disabled = false, s*1000);
}

sendBtn.addEventListener('click', async () => {
    const room = roomInput.value.trim();
    const content = contentInput.value.trim();
    if (!room || !content) return alert("請填寫房號與回報內容");
    // client-side quick checks
    if (room.length > 20 || content.length > 1000) return alert("輸入過長");

    try {
        // 發送到後端 (不傳 nickname，後端會自己產生)
        const resp = await fetch('/report', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ room, content })
        });
        const j = await resp.json();
        if (resp.status === 201) {
            // 使用回傳（已被 escape）
            const report = {
                id: j.id,
                room: j.room,
                content: j.content,
                nickname: j.nickname,
                likes: j.likes
            };
            const el = buildReportDOM(report);
            reportList.prepend(el);
            setTimeout(() => el.classList.remove('new'), 320);
            roomInput.value = '';
            contentInput.value = '';
            disableForSeconds(sendBtn, 3); // client-side rate-limit UX
        } else {
            alert(j.error || '發送失敗');
        }
    } catch (e) {
        console.error(e);
        alert('網路錯誤，請稍後再試');
    }
});

// Auth functions
async function doRegister() {
    const u = usernameInput.value.trim(), p = passwordInput.value;
    if (u.length < 3 || p.length < 6) return alert('帳號最少 3 字元，密碼最少 6 字元');
    const resp = await fetch('/register', {
        method: 'POST',
        headers: {'Content-Type': 'application/json'},
        body: JSON.stringify({ username: u, password: p })
    });
    const j = await resp.json();
    if (resp.status === 201) {
        alert('註冊成功，請登入');
    } else {
        alert(j.error || '註冊失敗');
    }
}

async function doLogin() {
    const u = usernameInput.value.trim(), p = passwordInput.value;
    if (!u || !p) return alert('請輸入帳密');
    const resp = await fetch('/login', {
        method: 'POST',
        headers: {'Content-Type': 'application/json'},
        body: JSON.stringify({ username: u, password: p })
    });
    const j = await resp.json();
    if (resp.status === 200) {
        currentUser = j.username;
        updateUserUI();
        alert('登入成功');
    } else {
        alert(j.error || '登入失敗');
    }
}

async function doLogout() {
    const resp = await fetch('/logout', { method: 'POST' });
    const j = await resp.json();
    if (resp.status === 200) {
        currentUser = null;
        updateUserUI();
        alert('已登出');
    } else {
        alert(j.error || '登出失敗');
    }
}

async function checkMe() {
    try {
        const resp = await fetch('/me');
        const j = await resp.json();
        if (j.authenticated) {
            currentUser = j.username;
        } else {
            currentUser = null;
        }
        updateUserUI();
    } catch (e) {
        currentUser = null;
        updateUserUI();
    }
}

function updateUserUI() {
    if (currentUser) {
        userDisplay.textContent = `已登入：${currentUser}`;
        logoutBtn.style.display = 'inline-block';
    } else {
        userDisplay.textContent = '未登入';
        logoutBtn.style.display = 'none';
    }
}

// events
registerBtn.addEventListener('click', doRegister);
loginBtn.addEventListener('click', doLogin);
logoutBtn.addEventListener('click', doLogout);

// initial load
checkMe();
loadReports();
