<script setup>
import { useTheme } from "vuetify";
import { getLineChartConfig } from "@core/libs/chartjs/chartjsConfig"; // Assuming a LineChart config function
import LineChart from "@core/libs/chartjs/components/LineChart"; // Use LineChart instead of BarChart

// Define the props to accept dynamic data and labels
const props = defineProps({
  labels: {
    type: Array,
    required: true,
  },
  datasets: {
    type: Array, 
    required: true,
  },
});

const vuetifyTheme = useTheme();

// Dynamically create chart data from the props
const chartData = computed(() => ({
  labels: props.labels,
  datasets: props.datasets.map((dataset, index) => ({
    ...dataset,
    borderColor: ['#FF6384', '#36A2EB', '#FFCE56', '#4BC0C0', '#9966FF', '#FF9F40'][index % 6], // Line color
    backgroundColor: ['rgba(255, 99, 132, 0.2)', 'rgba(54, 162, 235, 0.2)', 'rgba(255, 206, 86, 0.2)', 'rgba(75, 192, 192, 0.2)', 'rgba(153, 102, 255, 0.2)', 'rgba(255, 159, 64, 0.2)'][index % 6], // Fill color under the line
    borderWidth: 2, // Line thickness
    fill: true, // Enable fill for the area under the line
    pointBackgroundColor: '#fff', // Color of the point itself
    pointBorderColor: ['#FF6384', '#36A2EB', '#FFCE56', '#4BC0C0', '#9966FF', '#FF9F40'][index % 6], // Point border color
    pointRadius: 4, // Size of the points
    pointHoverRadius: 6, // Point size on hover
  })),
}));

// Get chart configuration dynamically based on the theme
const chartConfig = computed(() => ({
  ...getLineChartConfig(vuetifyTheme.current.value), // Assuming this returns LineChart config
  scales: {
    x: { beginAtZero: true },
    y: { beginAtZero: true },
  },
  responsive: true,
  maintainAspectRatio: false,
  plugins: {
    legend: {
      display: true,
      position: 'top', // Keep legend position at the top
      align: 'end',
    },
  },
}));
</script>

<template>
  <LineChart
    :chart-options="chartConfig"
    :height="650"
    :chart-data="chartData"
  />
</template>
