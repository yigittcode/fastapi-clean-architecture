// API Base URL
const API_BASE = 'http://localhost:8000';

// Global state
let currentToken = localStorage.getItem('token');
let currentUser = null;
let currentItemsView = 'my'; // 'my' or 'all'

// Initialize app
document.addEventListener('DOMContentLoaded', function() {
    if (currentToken) {
        loadUserProfile();
    }
    
    // Form event listeners
    document.getElementById('loginForm').addEventListener('submit', handleLogin);
    document.getElementById('registerForm').addEventListener('submit', handleRegister);
    document.getElementById('itemForm').addEventListener('submit', handleAddItem);
});

// Tab switching
function showTab(tabName, clickedButton = null) {
    // Hide all tabs
    document.getElementById('loginTab').style.display = 'none';
    document.getElementById('registerTab').style.display = 'none';
    
    // Remove active class from all buttons
    document.querySelectorAll('.tab-btn').forEach(btn => btn.classList.remove('active'));
    
    // Show selected tab
    document.getElementById(tabName + 'Tab').style.display = 'block';
    
    // Add active class to clicked button or find by text
    if (clickedButton) {
        clickedButton.classList.add('active');
    } else {
        // Find button by tab name
        const buttons = document.querySelectorAll('.tab-btn');
        buttons.forEach(btn => {
            if (btn.textContent.toLowerCase() === tabName.toLowerCase()) {
                btn.classList.add('active');
            }
        });
    }
}

// Authentication functions
async function handleLogin(e) {
    e.preventDefault();
    
    const username = document.getElementById('loginUsername').value;
    const password = document.getElementById('loginPassword').value;
    
    try {
        const response = await fetch(`${API_BASE}/auth/login`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({ username, password })
        });
        
        const data = await response.json();
        
        if (response.ok) {
            currentToken = data.access_token;
            localStorage.setItem('token', currentToken);
            showMessage('Login successful!', 'success');
            await loadUserProfile();
        } else {
            // Handle different error formats
            let errorMessage = 'Login failed';
            if (data.detail) {
                errorMessage = data.detail;
            } else if (data.error && data.error.message) {
                errorMessage = data.error.message;
            } else if (data.message) {
                errorMessage = data.message;
            }
            showMessage(errorMessage, 'error');
            console.error('Login error:', data);
        }
    } catch (error) {
        showMessage('Network error', 'error');
    }
}

async function handleRegister(e) {
    e.preventDefault();
    
    const email = document.getElementById('registerEmail').value;
    const username = document.getElementById('registerUsername').value;
    const full_name = document.getElementById('registerFullName').value;
    const password = document.getElementById('registerPassword').value;
    
    try {
        const response = await fetch(`${API_BASE}/auth/register`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({ email, username, full_name, password })
        });
        
        const data = await response.json();
        
        if (response.ok) {
            showMessage('Registration successful! Please login.', 'success');
            showTab('login');
            document.getElementById('registerForm').reset();
        } else {
            // Handle different error formats
            let errorMessage = 'Registration failed';
            if (data.detail) {
                errorMessage = data.detail;
            } else if (data.error && data.error.message) {
                errorMessage = data.error.message;
            } else if (data.message) {
                errorMessage = data.message;
            }
            showMessage(errorMessage, 'error');
            console.error('Registration error:', data);
        }
    } catch (error) {
        showMessage(`Network error: ${error.message}`, 'error');
        console.error('Network error:', error);
    }
}

function logout() {
    currentToken = null;
    currentUser = null;
    localStorage.removeItem('token');
    
    document.getElementById('authSection').style.display = 'block';
    document.getElementById('dashboard').style.display = 'none';
    
    showMessage('Logged out successfully', 'info');
}

// User profile functions
async function loadUserProfile() {
    try {
        const response = await fetch(`${API_BASE}/users/me/`, {
            headers: {
                'Authorization': `Bearer ${currentToken}`
            }
        });
        
        if (response.ok) {
            currentUser = await response.json();
            showDashboard();
            await loadUserItems();
        } else {
            logout();
        }
    } catch (error) {
        showMessage('Failed to load profile', 'error');
        logout();
    }
}

function showDashboard() {
    document.getElementById('authSection').style.display = 'none';
    document.getElementById('dashboard').style.display = 'block';
    
    document.getElementById('currentUser').textContent = currentUser.username;
    
    // Show user profile
    const profileHtml = `
        <p><strong>Email:</strong> ${currentUser.email}</p>
        <p><strong>Username:</strong> ${currentUser.username}</p>
        <p><strong>Full Name:</strong> ${currentUser.full_name || 'Not provided'}</p>
        <p><strong>Status:</strong> ${currentUser.is_active ? 'Active' : 'Inactive'}</p>
        <p><strong>Role:</strong> ${currentUser.is_superuser ? 'Admin' : 'User'}</p>
    `;
    document.getElementById('userProfile').innerHTML = profileHtml;
    
    // Show admin panel if user is admin
    if (currentUser.is_superuser) {
        document.getElementById('adminSection').style.display = 'block';
    } else {
        document.getElementById('adminSection').style.display = 'none';
    }
}

// Items functions
async function loadUserItems() {
    try {
        const response = await fetch(`${API_BASE}/items/my/`, {
            headers: {
                'Authorization': `Bearer ${currentToken}`
            }
        });
        
        if (response.ok) {
            const items = await response.json();
            displayItems(items);
        } else {
            showMessage('Failed to load items', 'error');
        }
    } catch (error) {
        showMessage('Network error', 'error');
    }
}

function displayItems(items) {
    const itemsList = document.getElementById('itemsList');
    
    if (items.length === 0) {
        itemsList.innerHTML = '<p>No items yet. Add your first item!</p>';
        return;
    }
    
    const itemsHtml = items.map(item => {
        // REST API best practice: sadece gerekli bilgiyi göster
        const ownerName = item.owner_username || 'Unknown';
        const isOwner = currentUser && item.owner_id === currentUser.id;
        const canEdit = isOwner || (currentUser && currentUser.is_superuser);
        
        return `
        <div class="item-card">
            <div class="item-header">
                <div class="item-title">${item.title}</div>
                ${item.owner_username ? `<div class="item-owner">👤 ${ownerName}</div>` : ''}
                ${canEdit ? `
                <div class="item-actions">
                    <button class="edit-btn" onclick="editItem(${item.id})">Edit</button>
                    <button class="delete-btn" onclick="deleteItem(${item.id})">Delete</button>
                </div>
                ` : ''}
            </div>
            ${item.description ? `<div class="item-description">${item.description}</div>` : ''}
        </div>
        `;
    }).join('');
    
    itemsList.innerHTML = itemsHtml;
}

function showAddItem() {
    document.getElementById('addItemForm').style.display = 'block';
}

function hideAddItem() {
    document.getElementById('addItemForm').style.display = 'none';
    document.getElementById('itemForm').reset();
}

async function handleAddItem(e) {
    e.preventDefault();
    
    const title = document.getElementById('itemTitle').value;
    const description = document.getElementById('itemDescription').value;
    
    try {
        const response = await fetch(`${API_BASE}/items/`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                'Authorization': `Bearer ${currentToken}`
            },
            body: JSON.stringify({ title, description })
        });
        
        if (response.ok) {
            showMessage('Item added successfully!', 'success');
            hideAddItem();
            await loadUserItems();
        } else {
            const data = await response.json();
            showMessage(data.detail || 'Failed to add item', 'error');
        }
    } catch (error) {
        showMessage('Network error', 'error');
    }
}

async function deleteItem(itemId) {
    if (!confirm('Are you sure you want to delete this item?')) {
        return;
    }
    
    try {
        const response = await fetch(`${API_BASE}/items/${itemId}`, {
            method: 'DELETE',
            headers: {
                'Authorization': `Bearer ${currentToken}`
            }
        });
        
        if (response.ok) {
            showMessage('Item deleted successfully!', 'success');
            await loadUserItems();
        } else {
            const data = await response.json();
            showMessage(data.detail || 'Failed to delete item', 'error');
        }
    } catch (error) {
        showMessage('Network error', 'error');
    }
}

async function editItem(itemId) {
    const newTitle = prompt('Enter new title:');
    if (!newTitle) return;
    
    const newDescription = prompt('Enter new description (optional):');
    
    try {
        const response = await fetch(`${API_BASE}/items/${itemId}`, {
            method: 'PUT',
            headers: {
                'Content-Type': 'application/json',
                'Authorization': `Bearer ${currentToken}`
            },
            body: JSON.stringify({ 
                title: newTitle, 
                description: newDescription || undefined 
            })
        });
        
        if (response.ok) {
            showMessage('Item updated successfully!', 'success');
            await loadUserItems();
        } else {
            const data = await response.json();
            showMessage(data.detail || 'Failed to update item', 'error');
        }
    } catch (error) {
        showMessage('Network error', 'error');
    }
}

// Items view switching
function switchItemsView(view) {
    currentItemsView = view;
    
    // Update button states
    document.getElementById('myItemsBtn').classList.toggle('active', view === 'my');
    document.getElementById('allItemsBtn').classList.toggle('active', view === 'all');
    
    // Load appropriate items
    if (view === 'my') {
        loadUserItems();
    } else {
        loadAllItems();
    }
}

async function loadAllItems() {
    try {
        const response = await fetch(`${API_BASE}/items/`, {
            headers: {
                'Authorization': `Bearer ${currentToken}`
            }
        });
        
        if (response.ok) {
            const items = await response.json();
            displayAllItems(items);
        } else {
            showMessage('Failed to load all items', 'error');
        }
    } catch (error) {
        showMessage('Network error', 'error');
    }
}

function displayAllItems(items) {
    const itemsList = document.getElementById('itemsList');
    
    if (items.length === 0) {
        itemsList.innerHTML = '<p>No items found.</p>';
        return;
    }
    
    const itemsHtml = items.map(item => `
        <div class="item-card">
            <div class="item-header">
                <div class="item-title">${item.title}</div>
                <div class="item-owner">👤 ${item.owner?.username || 'Unknown'}</div>
            </div>
            ${item.description ? `<div class="item-description">${item.description}</div>` : ''}
            <div class="item-meta">
                <small>Created: ${new Date(item.created_at).toLocaleDateString()}</small>
            </div>
        </div>
    `).join('');
    
    itemsList.innerHTML = itemsHtml;
}

// Admin functions
async function loadAllUsers() {
    try {
        const response = await fetch(`${API_BASE}/users/`, {
            headers: {
                'Authorization': `Bearer ${currentToken}`
            }
        });
        
        if (response.ok) {
            const users = await response.json();
            displayAllUsers(users);
        } else {
            const data = await response.json();
            showMessage(data.detail || 'Failed to load users', 'error');
        }
    } catch (error) {
        showMessage('Network error', 'error');
    }
}

function displayAllUsers(users) {
    const adminContent = document.getElementById('adminContent');
    
    if (users.length === 0) {
        adminContent.innerHTML = '<p>No users found.</p>';
        return;
    }
    
    const usersHtml = `
        <h4>👥 All Users (${users.length})</h4>
        <div class="users-grid">
            ${users.map(user => `
                <div class="user-card">
                    <div class="user-info">
                        <strong>${user.username}</strong>
                        <span class="user-email">${user.email}</span>
                        <span class="user-role ${user.is_superuser ? 'admin' : 'user'}">
                            ${user.is_superuser ? '👑 Admin' : '👤 User'}
                        </span>
                        <span class="user-status ${user.is_active ? 'active' : 'inactive'}">
                            ${user.is_active ? '✅ Active' : '❌ Inactive'}
                        </span>
                    </div>
                    <small>Joined: ${new Date(user.created_at).toLocaleDateString()}</small>
                </div>
            `).join('')}
        </div>
    `;
    
    adminContent.innerHTML = usersHtml;
}

function showUserStats() {
    // Placeholder for user statistics
    const adminContent = document.getElementById('adminContent');
    adminContent.innerHTML = `
        <h4>📊 User Statistics</h4>
        <div class="stats-grid">
            <div class="stat-card">
                <div class="stat-number">-</div>
                <div class="stat-label">Total Users</div>
            </div>
            <div class="stat-card">
                <div class="stat-number">-</div>
                <div class="stat-label">Active Users</div>
            </div>
            <div class="stat-card">
                <div class="stat-number">-</div>
                <div class="stat-label">Total Items</div>
            </div>
            <div class="stat-card">
                <div class="stat-number">-</div>
                <div class="stat-label">Admins</div>
            </div>
        </div>
        <p><em>Click "View All Users" to load actual statistics.</em></p>
    `;
}

// Utility functions
function showMessage(message, type) {
    const messageEl = document.getElementById('message');
    messageEl.textContent = message;
    messageEl.className = `message ${type} show`;
    
    setTimeout(() => {
        messageEl.classList.remove('show');
    }, 3000);
}

// Admin Functions
async function loadAllUsers() {
    if (!currentUser || !currentUser.is_superuser) {
        showMessage('Access denied: Admin only', 'error');
        return;
    }

    try {
        const response = await fetch(`${API_BASE}/users/`, {
            headers: {
                'Authorization': `Bearer ${currentToken}`
            }
        });

        if (response.ok) {
            const users = await response.json();
            displayAllUsers(users);
        } else {
            const error = await response.json();
            showMessage(error.message || 'Failed to load users', 'error');
        }
    } catch (error) {
        showMessage('Failed to load users', 'error');
    }
}

function displayAllUsers(users) {
    const adminContent = document.getElementById('adminContent');
    
    let html = '<div class="users-list"><h4>All Users</h4>';
    
    users.forEach(user => {
        html += `
            <div class="user-card">
                <div class="user-info">
                    <h5>${user.username}</h5>
                    <p>Email: ${user.email}</p>
                    <p>Full Name: ${user.full_name || 'Not provided'}</p>
                    <p>Status: ${user.is_active ? 'Active' : 'Inactive'}</p>
                    <p>Role: ${user.is_superuser ? 'Admin' : 'User'}</p>
                </div>
                <div class="user-actions">
                    <button onclick="editUser(${user.id})" class="edit-btn">Edit</button>
                    <button onclick="toggleUserStatus(${user.id}, ${!user.is_active})" 
                            class="status-btn">${user.is_active ? 'Deactivate' : 'Activate'}</button>
                    ${!user.is_superuser ? `<button onclick="deleteUser(${user.id})" class="delete-btn">Delete</button>` : ''}
                </div>
            </div>
        `;
    });
    
    html += '</div>';
    adminContent.innerHTML = html;
}

async function editUser(userId) {
    // Simple edit functionality - you can expand this
    const newFullName = prompt('Enter new full name:');
    if (!newFullName) return;

    try {
        const response = await fetch(`${API_BASE}/users/${userId}`, {
            method: 'PUT',
            headers: {
                'Content-Type': 'application/json',
                'Authorization': `Bearer ${currentToken}`
            },
            body: JSON.stringify({
                full_name: newFullName
            })
        });

        if (response.ok) {
            showMessage('User updated successfully', 'success');
            loadAllUsers(); // Refresh the list
        } else {
            const error = await response.json();
            showMessage(error.message || 'Failed to update user', 'error');
        }
    } catch (error) {
        showMessage('Failed to update user', 'error');
    }
}

async function toggleUserStatus(userId, newStatus) {
    try {
        const response = await fetch(`${API_BASE}/users/${userId}`, {
            method: 'PUT',
            headers: {
                'Content-Type': 'application/json',
                'Authorization': `Bearer ${currentToken}`
            },
            body: JSON.stringify({
                is_active: newStatus
            })
        });

        if (response.ok) {
            showMessage(`User ${newStatus ? 'activated' : 'deactivated'} successfully`, 'success');
            loadAllUsers(); // Refresh the list
        } else {
            const error = await response.json();
            showMessage(error.message || 'Failed to update user status', 'error');
        }
    } catch (error) {
        showMessage('Failed to update user status', 'error');
    }
}

async function deleteUser(userId) {
    if (!confirm('Are you sure you want to delete this user?')) return;

    try {
        const response = await fetch(`${API_BASE}/users/${userId}`, {
            method: 'DELETE',
            headers: {
                'Authorization': `Bearer ${currentToken}`
            }
        });

        if (response.ok) {
            showMessage('User deleted successfully', 'success');
            loadAllUsers(); // Refresh the list
        } else {
            const error = await response.json();
            showMessage(error.message || 'Failed to delete user', 'error');
        }
    } catch (error) {
        showMessage('Failed to delete user', 'error');
    }
}

async function showUserStats() {
    if (!currentUser || !currentUser.is_superuser) {
        showMessage('Access denied: Admin only', 'error');
        return;
    }

    try {
        const response = await fetch(`${API_BASE}/users/`, {
            headers: {
                'Authorization': `Bearer ${currentToken}`
            }
        });

        if (response.ok) {
            const users = await response.json();
            displayUserStats(users);
        } else {
            const error = await response.json();
            showMessage(error.message || 'Failed to load user statistics', 'error');
        }
    } catch (error) {
        showMessage('Failed to load user statistics', 'error');
    }
}

function displayUserStats(users) {
    const adminContent = document.getElementById('adminContent');
    
    const totalUsers = users.length;
    const activeUsers = users.filter(u => u.is_active).length;
    const adminUsers = users.filter(u => u.is_superuser).length;
    const regularUsers = totalUsers - adminUsers;
    
    const html = `
        <div class="stats-container">
            <h4>User Statistics</h4>
            <div class="stats-grid">
                <div class="stat-card">
                    <h3>${totalUsers}</h3>
                    <p>Total Users</p>
                </div>
                <div class="stat-card">
                    <h3>${activeUsers}</h3>
                    <p>Active Users</p>
                </div>
                <div class="stat-card">
                    <h3>${adminUsers}</h3>
                    <p>Admin Users</p>
                </div>
                <div class="stat-card">
                    <h3>${regularUsers}</h3>
                    <p>Regular Users</p>
                </div>
            </div>
        </div>
    `;
    
    adminContent.innerHTML = html;
}
