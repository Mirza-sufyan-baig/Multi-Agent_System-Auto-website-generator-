let ws;
let currentProject = "";
let building = false;
let deployUrl = "";

// Init
connect();
loadProjects();

// --- Sidebar Logic ---
function toggleSidebar() {
    const sidebar = document.getElementById('sidebar');
    sidebar.classList.toggle('collapsed');
    
    // Rotate icon logic could go here if needed
}

// --- Textarea Logic ---
const promptInput = document.getElementById("promptInput");
promptInput.addEventListener("input", function() {
    this.style.height = "auto";
    this.style.height = (this.scrollHeight) + "px";
    if (this.value === "") this.style.height = "auto";
});
promptInput.addEventListener("keypress", (e) => {
    if(e.key === 'Enter' && !e.shiftKey) {
        e.preventDefault();
        sendMessage();
    }
});

// --- Device Preview Logic ---
function setDevice(mode) {
    const wrapper = document.getElementById("deviceWrapper");
    const btns = document.querySelectorAll(".device-toggles .icon-btn");
    
    // Update State
    wrapper.className = `device-wrapper mode-${mode}`;
    
    // Update Buttons
    btns.forEach(btn => {
        if(btn.title.toLowerCase() === mode) btn.classList.add("active");
        else btn.classList.remove("active");
    });
}

// --- WebSocket & App Logic ---
function connect() {
    ws = new WebSocket(`ws://${window.location.host}/ws`);
    
    ws.onopen = () => {
        document.querySelector('.status-indicator').classList.add('connected');
        document.getElementById('statusText').innerText = "Online";
        if(currentProject) selectProject(currentProject);
    };
    
    ws.onclose = () => {
        document.querySelector('.status-indicator').classList.remove('connected');
        document.getElementById('statusText').innerText = "Reconnecting...";
        setTimeout(connect, 3000);
    };

    ws.onmessage = (event) => {
        const data = JSON.parse(event.data);
        handleMessage(data);
    };
}

function handleMessage(data) {
    const chatArea = document.getElementById("chatArea");
    
    switch(data.type) {
        case 'user_message':
            addMessage('user', data.content);
            break;
        case 'assistant_message':
            addMessage('system', data.content);
            break;
        case 'clear_chat':
            chatArea.innerHTML = '';
            break;
        case 'log':
            addLog(data.message);
            break;
        case 'deployed':
            deployUrl = data.url;
            document.getElementById("projectUrl").innerText = deployUrl;
            reloadPreview();
            break;
        case 'build_complete':
            setBuilding(false);
            loadProjects();
            break;
        case 'project_created':
            currentProject = data.project;
            loadProjects();
            break;
        case 'error':
            addMessage('system', `❌ Error: ${data.message}`);
            setBuilding(false);
            break;
    }
}

async function loadProjects() {
    const res = await fetch('/api/projects');
    const data = await res.json();
    const list = document.getElementById("projectList");
    list.innerHTML = '';
    
    data.projects.forEach(p => {
        const div = document.createElement('div');
        div.className = `project-item ${p.name === currentProject ? 'active' : ''}`;
        div.innerHTML = `<span class="project-name">${p.name}</span>`;
        div.title = p.name;
        div.onclick = () => selectProject(p.name);
        list.appendChild(div);
    });
}

function selectProject(projectId) {
    currentProject = projectId;
    ws.send(JSON.stringify({ type: "select_project", project: projectId }));
    loadProjects();
}

async function createNewProject() {
    const res = await fetch('/api/projects/new', { method: "POST" });
    const data = await res.json();
    selectProject(data.project);
}

function sendMessage() {
    const text = promptInput.value.trim();
    if(!text || building) return;
    
    ws.send(JSON.stringify({ type: "message", content: text }));
    promptInput.value = "";
    promptInput.style.height = "auto";
    setBuilding(true);
}

function setBuilding(isBuilding) {
    building = isBuilding;
    const btn = document.getElementById("sendBtn");
    btn.disabled = isBuilding;
    document.querySelector('.send-icon').style.display = isBuilding ? 'none' : 'block';
    document.querySelector('.spinner-icon').style.display = isBuilding ? 'block' : 'none';
}

function addMessage(role, text) {
    const chatArea = document.getElementById("chatArea");
    const div = document.createElement('div');
    div.className = role === 'user' ? 'msg-user' : 'msg-system';
    if(role === 'system') {
        div.innerHTML = marked.parse(text);
        div.className += ' markdown-body';
    } else {
        div.innerText = text;
    }
    chatArea.appendChild(div);
    chatArea.scrollTop = chatArea.scrollHeight;
}

function addLog(text) {
    const chatArea = document.getElementById("chatArea");
    const div = document.createElement('div');
    div.className = 'msg-log';
    div.innerText = `⚙️ ${text}`;
    chatArea.appendChild(div);
    chatArea.scrollTop = chatArea.scrollHeight;
}

function reloadPreview() {
    if(deployUrl) {
        const iframe = document.getElementById("previewFrame");
        iframe.src = `${deployUrl}?t=${Date.now()}`;
    }
}

function openExternal() {
    if(deployUrl) window.open(deployUrl, '_blank');
}