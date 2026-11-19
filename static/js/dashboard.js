const chartData = document.querySelector("#evenza-charts");

if (chartData && window.Chart) {
    const data = JSON.parse(chartData.textContent);
    const monthCanvas = document.querySelector("#month-chart");
    const statusCanvas = document.querySelector("#status-chart");
    const animation = !window.matchMedia("(prefers-reduced-motion: reduce)").matches;
    const statusColors = {
        "Brouillon": "#806879",
        "En préparation": "#ab763d",
        "Confirmé": "#542d3b",
        "Terminé": "#557260",
        "Annulé": "#a35767",
    };

    Chart.defaults.color = "#6d5c61";
    Chart.defaults.font.family = '"DM Sans", system-ui, sans-serif';

    if (monthCanvas) new Chart(monthCanvas, {
        type: "bar",
        data: {
            labels: data.months,
            datasets: [{label: "Événements", data: data.monthly, backgroundColor: "#79475b",
                        hoverBackgroundColor: "#542d3b", borderRadius: 5, maxBarThickness: 42}],
        },
        options: {
            maintainAspectRatio: false,
            animation,
            plugins: {legend: {display: false}},
            scales: {
                y: {beginAtZero: true, suggestedMax: 1, ticks: {precision: 0}, grid: {color: "#efe3dd"}},
                x: {grid: {display: false}},
            },
        },
    });

    if (statusCanvas) new Chart(statusCanvas, {
        type: "doughnut",
        data: {
            labels: data.statuses,
            datasets: [{data: data.totals, backgroundColor: data.statuses.map((status) => statusColors[status] || "#795666"),
                        borderColor: "#fffdfa", borderWidth: 3}],
        },
        options: {
            animation,
            maintainAspectRatio: false,
            cutout: "69%",
            plugins: {legend: {position: "bottom", labels: {usePointStyle: true, boxWidth: 9}}},
        },
    });
}
