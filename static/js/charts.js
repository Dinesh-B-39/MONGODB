window.initCharts = function() {
    console.log('Charts initialized');
};

window.initExpenseByCategoryChart = function(data) {
    if (window.Chart && document.getElementById('expenseByCategoryChart')) {
        new Chart(document.getElementById('expenseByCategoryChart').getContext('2d'), {
            type: 'pie',
            data: { 
                labels: data.labels || [], 
                datasets: [{ 
                    data: data.data || [], 
                    backgroundColor: ['#FF6384', '#36A2EB', '#FFCE56'] 
                }] 
            }
        });
    }
};

window.initMonthlyExpensesChart = function(data) {
    if (window.Chart && document.getElementById('monthlyExpensesChart')) {
        new Chart(document.getElementById('monthlyExpensesChart').getContext('2d'), {
            type: 'bar',
            data: { 
                labels: data.labels || [], 
                datasets: [{ 
                    data: data.data || [], 
                    backgroundColor: '#36A2EB' 
                }] 
            }
        });
    }
};