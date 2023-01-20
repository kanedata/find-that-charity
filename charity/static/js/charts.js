Chart.defaults.font.size = 14;
Chart.defaults.font.family = '"Raleway", sans-serif';

function chart_options(prefix = "£") {
    return {
        plugins: {
            legend: {
                display: false,
            },
        },
        scales: {
            y: {
                suggestedMin: 0,
                ticks: {
                    callback: function (value, index, values) {
                        if (value > 1000000000) {
                            return prefix + (value / 1000000000) + "bn";
                        } else if (value > 1000000) {
                            return prefix + (value / 1000000) + "m";
                        } else if (value > 1000) {
                            return prefix + (value / 1000) + "k";
                        }
                        return prefix + value;
                    },
                    count: 2,
                },
                grid: {
                    display: false,
                }
            },
            x: {
                type: 'time',
                time: {
                    unit: 'month',
                    displayFormats: {
                        month: 'YYYY',
                    }
                },
                ticks: {
                    stepSize: 24,
                },
                distribution: 'series',
                grid: {
                    display: false,
                }
            }
        }
    }
}

if (FINANCES.filter(f => f['fyend']).length > 1) {
    document.querySelector('#financeChartFigure').classList.remove('dn');
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
        options: chart_options(),
    });
    if (FINANCES.filter(f => f['funds_total']).length > 0 || FINANCES.filter(f => f['reserves']).length > 0) {
        document.querySelector('#fundsChartFigure').classList.remove('dn');
        var fundsChart = new Chart('fundsChart', {
            type: 'line',
            data: {
                labels: FINANCES.map(f => f['fyend']),
                datasets: [{
                    label: 'Funds',
                    data: FINANCES.map(f => f['funds_total']),
                    fill: false,
                    lineTension: 0,
                    borderColor: '#ff6300',
                    pointRadius: 1,
                    hitRadius: 5,
                }, {
                    label: 'Reserves',
                    data: FINANCES.map(f => f['reserves']),
                    fill: false,
                    lineTension: 0,
                    borderColor: '#ff4136',
                    pointRadius: 1,
                    hitRadius: 5,
                }]
            },
            options: chart_options(),
        });
    }
    if (FINANCES.filter(f => f['employees']).length > 0) {
        console.log(FINANCES.filter(f => f['employees']))
        document.querySelector('#employeesChartFigure').classList.remove('dn');
        var employeesChart = new Chart('employeesChart', {
            type: 'line',
            data: {
                labels: FINANCES.map(f => f['fyend']),
                datasets: [{
                    label: 'Employees',
                    data: FINANCES.map(f => f['employees']),
                    fill: false,
                    lineTension: 0,
                    borderColor: '#19a974',
                    pointRadius: 1,
                    hitRadius: 5,
                }]
            },
            options: chart_options(""),
        });
    }
    if (FINANCES.filter(f => f['volunteers']).length > 0) {
        document.querySelector('#volunteersChartFigure').classList.remove('dn');
        var volunteersChart = new Chart('volunteersChart', {
            type: 'line',
            data: {
                labels: FINANCES.map(f => f['fyend']),
                datasets: [{
                    label: 'Volunteers',
                    data: FINANCES.map(f => f['volunteers']),
                    fill: false,
                    lineTension: 0,
                    borderColor: '#00449e',
                    pointRadius: 1,
                    hitRadius: 5,
                }]
            },
            options: chart_options(""),
        });
    }
}

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