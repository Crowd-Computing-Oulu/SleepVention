const ctx = document.getElementById('sleepChart').getContext('2d');
let sleepChart;
let chartVisibility;

// Convert minutes to hours
function convertToHours(minutes) {
    return (minutes / 60).toFixed(2);
}

// Get weekday name from date string
function getWeekday(dateString) {
    const days = ["Sunday", "Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday"];
    const date = new Date(dateString);
    return days[date.getUTCDay()];
}

// Prepare weekly data
function prepareWeeklyData(data) {
    const now = new Date();
    const pastWeek = new Date();
    pastWeek.setDate(now.getDate() - 6); // 7 days including today

    const weeklyEntries = data
        .filter(entry => {
            const entryDate = new Date(entry.date);
            return entryDate >= pastWeek && entryDate <= now;
        })
        .sort((a, b) => new Date(a.date) - new Date(b.date)); // Sort by date ascending

    const labels = weeklyEntries.map(entry => {
        const date = new Date(entry.date);
        return date.toLocaleDateString('en-US', { weekday: 'short', month: 'short', day: 'numeric' });
    });

    const deepHours = weeklyEntries.map(entry => convertToHours(entry.deep_minutes));
    const lightHours = weeklyEntries.map(entry => convertToHours(entry.light_minutes));
    const remHours = weeklyEntries.map(entry => convertToHours(entry.rem_minutes));
    const wakeHours = weeklyEntries.map(entry => convertToHours(entry.wake_minutes));
    const asleepHours = weeklyEntries.map(entry => convertToHours(entry.minutesAsleep));

    return { labels, deepHours, lightHours, remHours, wakeHours, asleepHours };
}

// Prepare monthly data
function prepareMonthlyData(data, selectedMonth) {
    const labels = [];
    const deepHours = [];
    const lightHours = [];
    const remHours = [];
    const wakeHours = [];
    const asleepHours = [];

    // Generate a Date object for the first and last day of the selected month
    const [year, month] = selectedMonth.split("-");
    const daysInMonth = new Date(year, month, 0).getDate(); // Gets the last date of the month

    // Create an object to quickly access data entries by date
    const dataMap = {};
    data.forEach(entry => {
        const entryDate = new Date(entry.date).toISOString().split("T")[0];
        dataMap[entryDate] = entry;
    });

    // Loop over all days in the selected month
    for (let day = 1; day <= daysInMonth; day++) {
        const dayString = day.toString().padStart(2, '0');
        const fullDate = `${selectedMonth}-${dayString}`;

        // Add the day label (e.g., "Day 1", "Day 2", etc.)
        labels.push(`Day ${day}`);

        // Check if data exists for this date
        if (dataMap[fullDate]) {
            const entry = dataMap[fullDate];
            deepHours.push(convertToHours(entry.deep_minutes));
            lightHours.push(convertToHours(entry.light_minutes));
            remHours.push(convertToHours(entry.rem_minutes));
            wakeHours.push(convertToHours(entry.wake_minutes));
            asleepHours.push(convertToHours(entry.minutesAsleep));
        } else {
            // If there's no data for this date, push `null` to leave the chart bar/point empty
            deepHours.push(null);
            lightHours.push(null);
            remHours.push(null);
            wakeHours.push(null);
            asleepHours.push(null);
        }
    }

    return { labels, deepHours, lightHours, remHours, wakeHours, asleepHours };
}

// Prepare yearly data
function prepareYearlyData(data, selectedYear) {
    const monthNames = [
        "January", "February", "March", "April", "May", "June",
        "July", "August", "September", "October", "November", "December"
    ];
    
    const labels = monthNames;
    const deepHours = Array(12).fill(0);
    const lightHours = Array(12).fill(0);
    const remHours = Array(12).fill(0);
    const wakeHours = Array(12).fill(0);
    const asleepHours = Array(12).fill(0);
    const count = Array(12).fill(0);

    data.forEach(entry => {
        const date = new Date(entry.date);
        const year = date.getFullYear();
        const month = date.getMonth(); // 0 = January, 11 = December

        if (year === parseInt(selectedYear, 10)) {
            deepHours[month] += parseFloat(convertToHours(entry.deep_minutes));
            lightHours[month] += parseFloat(convertToHours(entry.light_minutes));
            remHours[month] += parseFloat(convertToHours(entry.rem_minutes));
            wakeHours[month] += parseFloat(convertToHours(entry.wake_minutes));
            asleepHours[month] += parseFloat(convertToHours(entry.minutesAsleep));
            count[month] += 1;
        }
    });

    // Calculate average for each month
    for (let i = 0; i < 12; i++) {
        if (count[i] > 0) {
            deepHours[i] = (deepHours[i] / count[i]).toFixed(2);
            lightHours[i] = (lightHours[i] / count[i]).toFixed(2);
            remHours[i] = (remHours[i] / count[i]).toFixed(2);
            wakeHours[i] = (wakeHours[i] / count[i]).toFixed(2);
            asleepHours[i] = (asleepHours[i] / count[i]).toFixed(2);
        } else {
            // Keep data empty if no records for the month
            deepHours[i] = null;
            lightHours[i] = null;
            remHours[i] = null;
            wakeHours[i] = null;
            asleepHours[i] = null;
        }
    }

    return { labels, deepHours, lightHours, remHours, wakeHours, asleepHours };
}

function createChart(type, labels, deepData, lightData, remData, wakeData, asleepData, visibility, isAverage=false) {
    const skipped = (ctx, value) => ctx.p0.skip || ctx.p1.skip ? value : undefined;

    if (sleepChart) {
        sleepChart.destroy(); // Destroy existing chart
    }

    sleepChart = new Chart(ctx, {
        type: type,
        data: {
            labels: labels,
            datasets: [
                {
                    label: isAverage ? 'Average Sleep' : 'Total Sleep',
                    data: asleepData,
                    backgroundColor: 'rgba(54, 162, 235, 0.6)',
                    borderColor: 'rgba(54, 162, 235, 1)',
                    borderWidth: 1,
                    lineTension: 0.2,
                    hidden: visibility.sleep,
                    segment: {
                        borderColor: ctx => skipped(ctx, 'rgba(54, 162, 235, 1)'),
                        borderDash: ctx => skipped(ctx, [6, 6]),
                    },
                    spanGaps: true
                },
                {
                    label: isAverage ? 'Average Deep Sleep' : 'Deep Sleep',
                    data: deepData,
                    backgroundColor: 'rgba(75, 192, 192, 0.6)',
                    borderColor: 'rgba(75, 192, 192, 1)',
                    borderWidth: 1,
                    lineTension: 0.2,
                    hidden: visibility.deep,
                    segment: {
                        borderColor: ctx => skipped(ctx, 'rgba(75, 192, 192, 1)'),
                        borderDash: ctx => skipped(ctx, [6, 6]),
                    },
                    spanGaps: true
                },
                {
                    label: isAverage ? 'Average Light Sleep' : 'Light Sleep',
                    data: lightData,
                    backgroundColor: 'rgba(153, 102, 255, 0.6)',
                    borderColor: 'rgba(153, 102, 255, 1)',
                    borderWidth: 1,
                    lineTension: 0.2,
                    hidden: visibility.light,
                    segment: {
                        borderColor: ctx => skipped(ctx, 'rgba(153, 102, 255, 1)'),
                        borderDash: ctx => skipped(ctx, [6, 6]),
                    },
                    spanGaps: true
                },
                {
                    label: isAverage ? 'Average REM Sleep' : 'REM Sleep',
                    data: remData,
                    backgroundColor: 'rgba(255, 206, 86, 0.6)',
                    borderColor: 'rgba(255, 206, 86, 1)',
                    borderWidth: 1,
                    lineTension: 0.2,
                    hidden: visibility.rem,
                    segment: {
                        borderColor: ctx => skipped(ctx, 'rgba(255, 206, 86, 1)'),
                        borderDash: ctx => skipped(ctx, [6, 6]),
                    },
                    spanGaps: true
                },
                {
                    label: isAverage ? 'Average Awake Time' : 'Awake Time',
                    data: wakeData,
                    backgroundColor: 'rgba(255, 99, 132, 0.6)',
                    borderColor: 'rgba(255, 99, 132, 1)',
                    borderWidth: 1,
                    lineTension: 0.2,
                    hidden: visibility.wake,
                    segment: {
                        borderColor: ctx => skipped(ctx, 'rgba(255, 99, 132, 1)'),
                        borderDash: ctx => skipped(ctx, [6, 6]),
                    },
                    spanGaps: true
                }
            ]
        },
        options: {
            scales: {
                x: {
                    title: {
                        display: true,
                        text: 'Date'
                    },
                    grid: {
                        display: false      
                    }
                },
                y: {
                    beginAtZero: true,
                    title: {
                        display: true,
                        text: 'Hours'
                    },
                    grid: {
                        display: false      
                    }
                }
            },
            plugins: {
                tooltip: {
                    callbacks: {
                        label: function (tooltipItem) {
                            return `${tooltipItem.dataset.label}: ${tooltipItem.raw} hours`;
                        }
                    }
                }
            }
        }
    });
}

function getCurrentVisibility() {
    if (!chartVisibility) {
        chartVisibility = {sleep: false, deep: true, light: true, rem: true, wake: true};
        return chartVisibility;
    }
    
    if (sleepChart.getDatasetMeta(0).hidden !== null) {
        chartVisibility.sleep = sleepChart.getDatasetMeta(0).hidden
    }
    if (sleepChart.getDatasetMeta(1).hidden !== null) {
        chartVisibility.deep = sleepChart.getDatasetMeta(1).hidden
    }
    if (sleepChart.getDatasetMeta(2).hidden !== null) {
        chartVisibility.light = sleepChart.getDatasetMeta(2).hidden
    }
    if (sleepChart.getDatasetMeta(3).hidden !== null) {
        chartVisibility.rem = sleepChart.getDatasetMeta(3).hidden
    }
    if (sleepChart.getDatasetMeta(4).hidden !== null) {
        chartVisibility.wake = sleepChart.getDatasetMeta(4).hidden
    }

    return chartVisibility;
}

// Function to initialize the month selector with the current month as default
function setDefaultMonthSelector() {
    const monthSelector = document.getElementById('monthSelector');
    const today = new Date();
    const year = today.getFullYear();
    const month = today.getMonth(); // 0 = January, 1 = February, ..., 11 = December

    // Format the month value as a 2-digit number (e.g., "03" for March)
    const monthValue = `${year}-${String(month + 1).padStart(2, '0')}`;
    
    // Set the month selector's default value to the current month
    monthSelector.value = monthValue;
}

function createCharts(data) {

    // Initial chart (last week data)
    const weeklyChartData = prepareWeeklyData(data);
    createChart(
        "bar",
        weeklyChartData.labels,
        weeklyChartData.deepHours,
        weeklyChartData.lightHours,
        weeklyChartData.remHours,
        weeklyChartData.wakeHours,
        weeklyChartData.asleepHours,
        getCurrentVisibility()
    );

    // Switch between weekly, monthly, and yearly data
    document.getElementById("timePeriodSelector").addEventListener("change", function (event) {
        const type = document.getElementById("chartTypeSelector").value;
        const visibility = getCurrentVisibility();
        document.getElementById("monthSelectorContainer").style.display = "none";
        document.getElementById("yearSelectorContainer").style.display = "none";

        if (event.target.value === "week") {
            const weeklyChartData = prepareWeeklyData(data);
            createChart(
                type,
                weeklyChartData.labels,
                weeklyChartData.deepHours,
                weeklyChartData.lightHours,
                weeklyChartData.remHours,
                weeklyChartData.wakeHours,
                weeklyChartData.asleepHours,
                visibility
            );
        } else if (event.target.value === "month") {
            document.getElementById("monthSelectorContainer").style.display = "block";
            const selectedMonth = document.getElementById("monthSelector").value;
            const monthlyChartData = prepareMonthlyData(data, selectedMonth);
            createChart(
                type,
                monthlyChartData.labels,
                monthlyChartData.deepHours,
                monthlyChartData.lightHours,
                monthlyChartData.remHours,
                monthlyChartData.wakeHours,
                monthlyChartData.asleepHours,
                visibility
            );
        } else if (event.target.value === "year") {
            document.getElementById("yearSelectorContainer").style.display = "block";
            const selectedYear = document.getElementById("yearSelector").value;
            const yearlyChartData = prepareYearlyData(data, selectedYear);
            createChart(
                type,
                yearlyChartData.labels,
                yearlyChartData.deepHours,
                yearlyChartData.lightHours,
                yearlyChartData.remHours,
                yearlyChartData.wakeHours,
                yearlyChartData.asleepHours,
                visibility,
                true
            );
        }
    });

    document.getElementById("monthSelector").addEventListener("change", function () {
        const selectedMonth = this.value;
        const type = document.getElementById("chartTypeSelector").value;
        const visibility = getCurrentVisibility();

        const monthlyChartData = prepareMonthlyData(data, selectedMonth);
        createChart(
            type,
            monthlyChartData.labels,
            monthlyChartData.deepHours,
            monthlyChartData.lightHours,
            monthlyChartData.remHours,
            monthlyChartData.wakeHours,
            monthlyChartData.asleepHours,
            visibility
        );
    });

    // Handle year selection change
    document.getElementById("yearSelector").addEventListener("change", function () {
        const selectedYear = this.value;
        const type = document.getElementById("chartTypeSelector").value;
        const visibility = getCurrentVisibility();

        const yearlyChartData = prepareYearlyData(data, selectedYear);
        createChart(
            type,
            yearlyChartData.labels,
            yearlyChartData.deepHours,
            yearlyChartData.lightHours,
            yearlyChartData.remHours,
            yearlyChartData.wakeHours,
            yearlyChartData.asleepHours,
            visibility,
            true
        );
    });

    document.getElementById("chartTypeSelector").addEventListener("change", function (event) {
        const period = document.getElementById("timePeriodSelector").value;
        const type = event.target.value;
        const visibility = getCurrentVisibility();

        if (period === "week") {
            const weeklyChartData = prepareWeeklyData(data);
            createChart(
                type,
                weeklyChartData.labels,
                weeklyChartData.deepHours,
                weeklyChartData.lightHours,
                weeklyChartData.remHours,
                weeklyChartData.wakeHours,
                weeklyChartData.asleepHours,
                visibility
            );
        } else if (period === "month") {
            const selectedMonth = document.getElementById("monthSelector").value;
            const monthlyChartData = prepareMonthlyData(data, selectedMonth);
            createChart(
                type,
                monthlyChartData.labels,
                monthlyChartData.deepHours,
                monthlyChartData.lightHours,
                monthlyChartData.remHours,
                monthlyChartData.wakeHours,
                monthlyChartData.asleepHours,
                visibility
            );
        } else if (period === "year") {
            const selectedYear = document.getElementById("yearSelector").value;
            const yearlyChartData = prepareYearlyData(data, selectedYear);
            createChart(
                type,
                yearlyChartData.labels,
                yearlyChartData.deepHours,
                yearlyChartData.lightHours,
                yearlyChartData.remHours,
                yearlyChartData.wakeHours,
                yearlyChartData.asleepHours,
                visibility,
                true
            );
        }
    });

    setDefaultMonthSelector();

}