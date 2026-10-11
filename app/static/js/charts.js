document.addEventListener("DOMContentLoaded", function() {
    const ctx = document.getElementById("projectsChart");
    if (ctx) {
        new Chart(ctx, {
            type: 'doughnut',
            data: {
                labels: ['ورشات (Workshops)', 'ماراثون تحرير (Edit-a-thons)', 'جولات تصوير (Photo Walks)'],
                datasets: [{
                    data: [12, 19, 7],
                    backgroundColor: ['#16a34a', '#3366cc', '#dc2626']
                }]
            },
            options: {
                responsive: true,
                plugins: {
                    legend: { position: 'bottom' }
                }
            }
        });
    }
});
