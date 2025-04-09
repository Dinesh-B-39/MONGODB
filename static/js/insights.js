let budgets = JSON.parse(localStorage.getItem('budgets')) || [];

function addBudget(category, limit, period) {
    const budget = { id: Date.now(), category, limit: parseFloat(limit), period, spent: 0 };
    budgets.push(budget);
    localStorage.setItem('budgets', JSON.stringify(budgets));
    renderBudgets();
}

function renderBudgets() {
    const budgetList = document.getElementById('budgetList');
    if (!budgetList) return;
    budgetList.innerHTML = '';
    budgets.slice(0, 3).forEach(budget => {
        const percentage = (budget.spent / budget.limit) * 100 || 0;
        const status = percentage >= 100 ? 'danger' : percentage >= 80 ? 'warning' : 'success';
        const li = document.createElement('div');
        li.className = 'mb-3';
        li.innerHTML = `
            <div class="d-flex justify-content-between">
                <h6>${budget.category}</h6>
                <span class="badge bg-${status}">${percentage.toFixed(0)}%</span>
            </div>
            <div class="progress budget-progress">
                <div class="progress-bar bg-${status}" style="width: ${percentage}%;"></div>
            </div>
            <div class="d-flex justify-content-between">
                <small>${budget.spent.toFixed(2)} spent</small>
                <small>${budget.limit.toFixed(2)} limit</small>
            </div>
        `;
        budgetList.appendChild(li);
    });
}

document.addEventListener('DOMContentLoaded', renderBudgets);