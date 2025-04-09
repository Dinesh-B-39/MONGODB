let transactions = JSON.parse(localStorage.getItem('transactions')) || [];

function addTransaction(description, amount, category, date, type) {
    const transaction = {
        id: Date.now(),
        description: description.trim(),
        amount: parseFloat(amount) * (type === 'expense' ? -1 : 1),
        category: category.trim(),
        date: date,
        type: type
    };
    transactions.push(transaction);
    localStorage.setItem('transactions', JSON.stringify(transactions));
    renderTransactions();
}

function deleteTransaction(id) {
    transactions = transactions.filter(t => t.id !== id);
    localStorage.setItem('transactions', JSON.stringify(transactions));
    renderTransactions();
}

function renderTransactions() {
    const transactionList = document.getElementById('transactionList');
    if (!transactionList) return;
    transactionList.innerHTML = '';
    const sortedTransactions = [...transactions].sort((a, b) => new Date(b.date) - new Date(a.date));
    sortedTransactions.forEach(transaction => {
        const li = document.createElement('li');
        li.className = `list-group-item transaction-row ${transaction.type}`;
        li.innerHTML = `
            <div class="d-flex w-100 justify-content-between">
                <h6 class="mb-1">${transaction.description}</h6>
                <span class="transaction-amount ${transaction.type}">
                    ${Math.abs(transaction.amount).toFixed(2)}
                </span>
            </div>
            <div class="d-flex justify-content-between align-items-center">
                <small class="transaction-category">${transaction.category}</small>
                <small class="transaction-date text-muted">${new Date(transaction.date).toLocaleDateString()}</small>
                <button class="btn btn-sm btn-danger" onclick="deleteTransaction(${transaction.id})">Delete</button>
            </div>
        `;
        transactionList.appendChild(li);
    });
}

document.addEventListener('DOMContentLoaded', renderTransactions);