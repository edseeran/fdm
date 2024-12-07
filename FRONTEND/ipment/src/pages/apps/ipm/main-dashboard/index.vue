<script setup>
import { ref, computed, watch, onMounted } from "vue";
import { format, startOfDay, isAfter, isBefore, isSameDay, endOfDay } from 'date-fns';
import ChartJsBarChart from "@/views/apps/ipm/LineChart.vue";
import axios from "axios";
import endpoints from "../../../../utils/endpoint";
import { useToast } from "vue-toastification";
import { Chart, Filler, registerables } from "chart.js";

// Register the Chart.js components and Filler plugin
Chart.register(...registerables, Filler);

// V-Models for filter
const toast = useToast();
const circuit = ref("MC038688-BIR-CER/GigabitEthernet0/0/1");
const isFiltersExpanded = ref(true);
const selectedRows = ref([]);
const isLoading = ref(false);
const circuitList = ref([]);
const unitOfMeasurement = ref(null);
const isFiltered = ref(false);
const hasCircuit = ref(true);

// Human-readable date format
const tempStartDate = ref('');
const tempEndDate = ref('');

const startDate = ref('');
const endDate = ref('');

// Convert human-readable date back to YYYY-MM-DD for query
watch([tempStartDate, tempEndDate], () => {
  if (tempStartDate.value && tempEndDate.value) {
    startDate.value = format(new Date(tempStartDate.value), "yyyy-MM-dd HH:mm:ss");
    endDate.value = format(new Date(tempEndDate.value), "yyyy-MM-dd HH:mm:ss");
  }
});

// Set initial dates when the component mounts
onMounted(async () => {
  const today = new Date();

  // Set the initial start date to today at 00:00:00
  const initialStart = new Date(today);
  initialStart.setHours(0, 0, 0, 0);

  // Set the initial end date to today at 23:59:59
  const initialEnd = new Date(today);
  initialEnd.setHours(23, 59, 59, 999);

  // Initialize both startDate and tempStartDate
  startDate.value = format(initialStart, "yyyy-MM-dd HH:mm:ss");
  endDate.value = format(initialEnd, "yyyy-MM-dd HH:mm:ss");

  // Set human-readable dates
  tempStartDate.value = format(initialStart, "MMMM d, yyyy HH:mm");
  tempEndDate.value = format(initialEnd, "MMMM d, yyyy HH:mm");

  
 await fetchData();
});

watch([circuit], () => {
  if (circuit.value === null) {  // Use '===' for comparison
    hasCircuit.value = false;
    console.log(hasCircuit.value);
  } else {
    hasCircuit.value = true;
  }
});


// Table headers
const headers = [
  { title: "Identity", key: "id", sortable: false },
  { title: "Usage", key: "usage", sortable: false },
  { title: "Data Plan", key: "data_plan", sortable: false },
  { title: "Subscriber's Name", key: "subscribers_name", sortable: false },
  { title: "OLT Name", key: "olt_name", sortable: false },
  { title: "NAP Code", key: "nap_code", sortable: false },
  { title: "Site Name", key: "nap_code", sortable: false },
  { title: "Port 1", key: "port_one", sortable: false },
  { title: "Port 2", key: "port_two", sortable: false },
  { title: "Port 3", key: "port_three", sortable: false },
  { title: "Port 4", key: "port_four", sortable: false },
];

// Computed property for dynamic headers
const dynamicHeaders = computed(() =>
  headers.map((header) => {
    if (header.key === "inbound_rate" || header.key === "outbound_rate") {
      return {
        ...header,
        title: `${header.title} (${unitOfMeasurement.value}/s)`,
      };
    }
    return header;
  })
);

// Pagination logic
const itemsPerPage = ref(10);
const page = ref(1);
const searchQuery = ref("");

const formattedData = computed(() => {
  return fetchedData.value.map((item) => ({
    ...item,
    // Format the date to 'yyyy-MM-dd HH:mm:ss' in UTC
    time: new Date(item.time).toISOString().replace("T", " ").split(".")[0],
  }));
});

// Filter the records based on the selected start and end dates
const filteredData = computed(() => {
  return formattedData.value.filter((item) => {
    // Parse the item's time as a date object in local time
    const itemDate = new Date(item.time); // Converts to local time automatically

    // Normalize the start and end dates to the start of the day (local time)
    const start = startDate.value ? startOfDay(new Date(startDate.value)) : null;
    const end = endDate.value ? startOfDay(new Date(endDate.value)) : null;

    // Compare the dates without timezone interference
    if (start && end) {
      return (
        (isAfter(itemDate, start) || isSameDay(itemDate, start)) &&
        (isBefore(itemDate, end) || isSameDay(itemDate, end))
      );
    } else if (start) {
      return isAfter(itemDate, start) || isSameDay(itemDate, start);
    } else if (end) {
      return isBefore(itemDate, end) || isSameDay(itemDate, end);
    } else {
      return true; // No start or end date, return all records
    }
  });
});


const fetchCircuits = async () => {
  isLoading.value = true;
  try {
    const response = await axios.get(endpoints.ipmListCircuit, {
      headers: {
        "Content-Type": "application/json", // Ensure the CSRF token is defined and valid
        Accept: "application/json",
        "Cache-Control": "no-cache",
      },
      withCredentials: true, // Ensure cookies are sent with the request
    });
    isLoading.value = false;
    circuitList.value = response.data;
  } catch (error) {
    console.error("Fetch error:", error);
    toast.error("Error fetching records.");
    isLoading.value = false;
  }
};

const fetchUnit = async () => {
  isLoading.value = true;
  try {
    const response = await axios.get(endpoints.ipmListConfig, {
      headers: {
        "Content-Type": "application/json", // Ensure the CSRF token is defined and valid
        Accept: "application/json",
        "Cache-Control": "no-cache",
      },
      withCredentials: true, // Ensure cookies are sent with the request
    });
    isLoading.value = false;
    unitOfMeasurement.value = response.data[0].unit;
  } catch (error) {
    console.error("Fetch error:", error);
    toast.error("Error fetching records.");
    isLoading.value = false;
  }
};

await fetchUnit();
await fetchCircuits();

// Filter records based on search query
const filterRecords = (records, query) => {
  const lowerCaseQuery = query.toLowerCase();
  return records.filter((record) =>
    record.name.toLowerCase().includes(lowerCaseQuery)
  );
};

// Paginated records computed property
const paginatedRecords = computed(() => {
  const records = filteredData.value;
  const filteredRecords = filterRecords(records, searchQuery.value);
  const start = (page.value - 1) * itemsPerPage.value;
  const end = start + itemsPerPage.value;
  return filteredRecords.slice(start, end);
});

const totalRecords = computed(
  () => filterRecords(filteredData.value, searchQuery.value).length
);

// Data for Line Chart
const chartLabels = computed(() =>
  filteredData.value.map((item) => {
    // Convert the item's time to a Date object in UTC and extract only the date part (YYYY-MM-DD)
    return new Date(item.time).toISOString().split("T")[0];
  })
);

const chartDatasets = computed(() => [
  {
    label: "Inbound",
    data: filteredData.value.map((item) => parseFloat(item.inbound_rate) || 0),
    borderColor: "#36A2EB",
    backgroundColor: "#36A2EB",
    fill: false,
    tension: 0.5,
  },
  {
    label: "Outbound",
    data: filteredData.value.map((item) => parseFloat(item.outbound_rate) || 0),
    borderColor: "#FF6384",
    backgroundColor: "#FF6384",
    fill: false,
    tension: 0.5,
  },
]);

const fetchedData = ref([]);

// Apply filters (this is automatic in this implementation)
const fetchData = async () => {
  try {
    const response = await axios.get(endpoints.ipmListData, {
      params: {
        start_date: startDate.value,
        end_date: endDate.value,
        circuit: circuit.value,
      },
      headers: {
        "Content-Type": "application/json", // Ensure the CSRF token is defined and valid
        Accept: "application/json",
        "Cache-Control": "no-cache",
      },
      withCredentials: true, // Ensure cookies are sent with the request
    });

    fetchedData.value = response.data; // Correct way to update a ref
    toast.success("Records fetched successfully!");
    isFiltered.value = true;
  } catch (error) {
    console.error("Fetch error:", error);
    toast.error("Error fetching records!");
  }
};

// Apply filters (this is automatic in this implementation)
const applyFilters = async () => {
  try {
    const response = await axios.get(endpoints.ipmListData, {
      params: {
        start_date: startDate.value,
        end_date: endDate.value,
        circuit: circuit.value,
      },
      headers: {
        "Content-Type": "application/json", // Ensure the CSRF token is defined and valid
        Accept: "application/json",
        "Cache-Control": "no-cache",
      },
      withCredentials: true, // Ensure cookies are sent with the request
    });

    fetchedData.value = response.data; // Correct way to update a ref
    toast.success("Records fetched successfully!");
    isFiltered.value = true;
  } catch (error) {
    console.error("Fetch error:", error);
    toast.error("Error fetching records!");
  }
};

const exportCSV = (data) => {
  // Get headers, excluding 'id'
  const headers = Object.keys(data[0]).filter(header => header !== 'id').join(',');

  // Map through the data and exclude 'id' from the rows
  const rows = data.map(row => {
    return [
      row.name,
      `${row.inbound_rate} ${unitOfMeasurement.value}/s`, // Append unit dynamically
      `${row.outbound_rate} ${unitOfMeasurement.value}/s`, // Append unit dynamically
      row.time,
    ].join(',');
  }).join('\n');

  const csvContent = `${headers}\n${rows}`;
  const blob = new Blob([csvContent], { type: 'text/csv' });
  const url = URL.createObjectURL(blob);

  const link = document.createElement('a');
  link.href = url;
  link.download = 'export.csv';
  link.click();

  URL.revokeObjectURL(url); // Clean up after download
};

</script>

<template>
  <section>
    <!-- Filters Section -->
    <VExpansionPanels v-model="isFiltersExpanded" class="mb-6">
      <VExpansionPanel>
        <VExpansionPanelTitle>Filters</VExpansionPanelTitle>
        <VExpansionPanelText>
          <v-container fluid>
            <v-row>
              <v-col cols="12" md="3">
                <AppDateTimePicker
                  v-model="tempStartDate"
                  :config="{ enableTime: true, dateFormat: 'F j, Y H:i' }"
                  label="Start Date"
                  outlined
                />
              </v-col>
              <v-col cols="12" md="3">
                <AppDateTimePicker
                  v-model="tempEndDate"
                  :config="{ enableTime: true, dateFormat: 'F j, Y H:i' }"
                  label="End Date"
                  outlined
                />
              </v-col>
              <v-col cols="12" md="3" class="mt-6">
                <v-autocomplete
                  v-model="circuit"
                  label="Circuit"
                  :items="circuitList"
                  outlined
                  clearable
                />
              </v-col>
              <v-col cols="12" md="3">
                <v-btn block @click="applyFilters" class="mt-6"
                  >Apply Filter</v-btn
                >
              </v-col>
              <!-- <v-col cols="12" md="3">
                <v-btn block @click="clearFilters" class="mt-6">Reset Filter</v-btn>
              </v-col> -->
            </v-row>
          </v-container>
        </VExpansionPanelText>
      </VExpansionPanel>
    </VExpansionPanels>

    <!-- Chart Section -->
    <VCard class="mb-6" v-if="hasCircuit">
      <VCardItem class="pb-4">
        <VCardTitle>Line Graph: Device Interface Data</VCardTitle>
      </VCardItem>

      <VCardText>
        <ChartJsBarChart
          :labels="chartLabels"
          :datasets="chartDatasets"
          style="max-width: 100%; height: auto"
        />
      </VCardText>
    </VCard>

    <!-- Data Table Section -->
    <VCard class="mb-6">
      <VCardItem class="pb-4">
        <VCardTitle>FDM Data Records</VCardTitle>
      </VCardItem>

      <VCardText class="d-flex flex-wrap gap-4">
        <div class="me-3 d-flex gap-3">
          <AppSelect
            :model-value="itemsPerPage"
            :items="[
              { value: 10, title: '10' },
              { value: 25, title: '25' },
              { value: 50, title: '50' },
              { value: 100, title: '100' },
              { value: -1, title: 'All' },
            ]"
            @update:model-value="itemsPerPage = parseInt($event, 10)"
          />
        </div>

        <VSpacer />

        <div class="app-user-search-filter d-flex align-center flex-wrap gap-4">
          <div style="inline-size: 15.625rem">
            <AppTextField v-model="searchQuery" placeholder="Search by Name" />
          </div>
        </div>
        
      </VCardText>

      <VDivider />

      <VDataTableServer
        v-model:items-per-page="itemsPerPage"
        v-model:model-value="selectedRows"
        v-model:page="page"
        :items="paginatedRecords"
        item-value="id"
        :items-length="totalRecords"
        :headers="dynamicHeaders"
        class="text-no-wrap"
        loading-text="Fetching records, please wait."
      >
        <!-- Pagination -->
        <template #bottom>
          <TablePagination
            v-model:page="page"
            :items-per-page="itemsPerPage"
            :total-items="totalRecords"
          />
        </template>
      </VDataTableServer>
    </VCard>
  </section>
</template>

<style scoped>
.table-container {
  max-width: 100%;
  overflow-x: auto;
  padding: 16px;
}

.styled-table {
  width: 100%;
  border-collapse: collapse;
  font-size: 14px;
  text-align: left;
  border-spacing: 0;
}

.styled-table th {
  padding: 12px 15px;
  border: 1px solid #ddd;
  font-weight: bold;
}

.styled-table td {
  padding: 12px 15px;
  border: 1px solid #ddd;
  text-align: center;
}

@media (max-width: 768px) {
  .styled-table {
    font-size: 12px;
  }
}
</style>
