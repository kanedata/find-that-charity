var financeChart = new Chart('financeChart', {
    type: 'line',
    data: {
        labels: FINANCES.map(f => f['fyend']),
        datasets: [
            {
                label: 'Income',
                data: FINANCES.map(f => f['income']),
                fill: false,
                lineTension: 0,
                borderColor: '#00449e',
                pointRadius: 1,
                hitRadius: 5,
            },
            {
                label: 'Spending',
                data: FINANCES.map(f => f['spending']),
                fill: false,
                lineTension: 0,
                borderColor: '#19a974',
                pointRadius: 1,
                hitRadius: 5,
            }
        ]
    },
    options: {
        legend: {
            align: 'end',
        },
        scales: {
            yAxes: [{
                ticks: {
                    beginAtZero: true
                }
            }],
            xAxes: [{
                type: 'time',
                time: {
                    unit: 'month'
                },
                gridLines: {
                    display: false,
                }
            }]
        }
    }
});

function sparkline(field, el, finances) {
    return new Chart(el, {
        type: 'line',
        data: {
            labels: finances.map(f => f['fyend']),
            datasets: [
                {
                    label: field,
                    data: finances.map(f => f[field]),
                    fill: false,
                    lineTension: 0,
                    borderColor: '#00449e',
                    pointRadius: 1,
                    hitRadius: 5,
                }
            ]
        },
        options: {
            legend: {
                display: false,
            },
            scales: {
                yAxes: [{
                    ticks: {
                        beginAtZero: false,
                        display: false,
                    },
                    gridLines: {
                        display: false,
                    }
                }],
                xAxes: [{
                    type: 'time',
                    time: {
                        unit: 'month'
                    },
                    ticks: {
                        display: false,
                    },
                    gridLines: {
                        display: false,
                    }
                }]
            },
            tooltips: {
                enabled: false
            }
        }
    });
}

document.querySelectorAll('.sparkline').forEach((el) => {
    sparkline(el.dataset.field, el, FINANCES);
})