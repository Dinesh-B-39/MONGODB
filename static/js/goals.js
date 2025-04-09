let goals = JSON.parse(localStorage.getItem('goals')) || [];

function addGoal(name, targetAmount, deadline) {
    const goal = { id: Date.now(), name, targetAmount: parseFloat(targetAmount), deadline, currentAmount: 0 };
    goals.push(goal);
    localStorage.setItem('goals', JSON.stringify(goals));
    renderGoals();
}

function updateGoal(id, amount) {
    const goal = goals.find(g => g.id === id);
    if (goal) {
        goal.currentAmount += parseFloat(amount);
        localStorage.setItem('goals', JSON.stringify(goals));
        renderGoals();
    }
}

function deleteGoal(id) {
    goals = goals.filter(g => g.id !== id);
    localStorage.setItem('goals', JSON.stringify(goals));
    renderGoals();
}

function renderGoals() {
    const goalList = document.getElementById('goalList');
    if (!goalList) return;
    goalList.innerHTML = '';
    goals.slice(0, 3).forEach(goal => {
        const progress = (goal.currentAmount / goal.targetAmount) * 100 || 0;
        const li = document.createElement('div');
        li.className = 'mb-3 goal-card';
        li.innerHTML = `
            <div class="d-flex justify-content-between">
                <h6>${goal.name}</h6>
                <span class="badge bg-primary">${progress.toFixed(0)}%</span>
            </div>
            <div class="progress goal-progress">
                <div class="progress-bar" style="width: ${progress}%;"></div>
            </div>
            <div class="d-flex justify-content-between">
                <small>${goal.currentAmount.toFixed(2)}</small>
                <small>${goal.targetAmount.toFixed(2)}</small>
                <button class="btn btn-sm btn-danger" onclick="deleteGoal(${goal.id})">Delete</button>
            </div>
        `;
        goalList.appendChild(li);
    });
}

document.addEventListener('DOMContentLoaded', renderGoals);