<script setup>
import { useTheme } from "vuetify";
import { getLatestBarChartConfig } from "@core/libs/chartjs/chartjsConfig";
import BarChart from "@core/libs/chartjs/components/BarChart";

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
    borderColor: ['#FF6384', '#36A2EB', '#FFCE56', '#4BC0C0', '#9966FF', '#FF9F40'][index % 6], // Hardcoded color codes
    backgroundColor: ['#FF6384', '#36A2EB', '#FFCE56', '#4BC0C0', '#9966FF', '#FF9F40'][index % 6],
    // Removed line-specific properties
    borderWidth: 1, // Add borderWidth for bar chart
  })),
}));

// Get chart configuration dynamically based on the theme
const chartConfig = computed(() => ({
  ...getLatestBarChartConfig(vuetifyTheme.current.value),
  scales: {
    x: { beginAtZero: true },
    y: { beginAtZero: true },
  },
  responsive: true,
  maintainAspectRatio: false,
  plugins: {
    legend: {
      display: true,
      position: 'top', // Move legend to the right
      align: 'end',
    },
  },
}));

</script>

<template>
  <BarChart
    :chart-options="chartConfig"
    :height="650"
    :chart-data="chartData"
  />
</template>
