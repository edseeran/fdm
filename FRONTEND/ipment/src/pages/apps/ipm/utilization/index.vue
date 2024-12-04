<script setup>
import { ref, computed, watch } from "vue";
import { format, parse, parseISO } from "date-fns";
import ChartJsBarChart from "@/views/apps/ipm/BarChart.vue";
import axios from "axios";
import endpoints from "../../../../utils/endpoint";
import { useToast } from "vue-toastification";
import { Chart, Filler, registerables } from 'chart.js';

// Register the Chart.js components and Filler plugin
Chart.register(...registerables, Filler);


// V-Models for date filter
const startDate = ref('');
const endDate = ref('');
const tempStartDate = ref('');
const tempEndDate = ref('');
const value = ref("inbound_rate");
const topNumber = ref(10);
const sortBy = ref("desc");
const isFiltersExpanded = ref(true);
const selectedRows = ref([]);
const toast = useToast();
const fetchedData = ref([]);
const unitOfMeasurement = ref(null)
const isFiltered = ref(false)

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

const valueItems = [
  { title: "Inbound Rate", value: "inbound_rate" },
  { title: "Outbound Rate", value: "outbound_rate" },
];
const sortByItems = [
  { title: "Ascending", value: "asc" },
  { title: "Descending", value: "desc" },
];

// Table headers
const headers = [
  { title: "No.", key: "index", sortable: true },
  { title: "Name", key: "name", sortable: true },
  { title: "Average Inbound Rate",
    key: "avg_inbound_rate",
    sortable: true 
  },

  {
    title: "Average Outbound Rate",
    key: "avg_outbound_rate",
    sortable: true,
  },
];

// Computed property for dynamic headers
const dynamicHeaders = computed(() =>
  headers.map((header) => {
    if (header.key === "avg_inbound_rate" || header.key === "avg_outbound_rate") {
      return {
        ...header,
        title: `${header.title} (${unitOfMeasurement.value}/s)`,
      };
    }
    return header;
  })
);

const fetchUnit = async () => {
  try {
    const response = await axios.get(endpoints.ipmListConfig, {
      headers: {
        "Content-Type": "application/json", // Ensure the CSRF token is defined and valid
        Accept: "application/json",
        "Cache-Control": "no-cache",
      },
      withCredentials: true, // Ensure cookies are sent with the request
    });
    unitOfMeasurement.value = response.data[0].unit;
  } catch (error) {
    console.error("Fetch error:", error);
    toast.error("Error fetching records.");
  }
};

await fetchUnit();

// Pagination logic
const itemsPerPage = ref(10);
const page = ref(1);
const searchQuery = ref("");

// Filter records based on search query
const filterRecords = (records, query) => {
  const lowerCaseQuery = query.toLowerCase();
  return records.filter((record) =>
    record.name.toLowerCase().includes(lowerCaseQuery)
  );
};

// Paginated records computed property
const paginatedRecords = computed(() => {
  const records = fetchedData.value;
  const filteredRecords = filterRecords(records, searchQuery.value);
  const start = (page.value - 1) * itemsPerPage.value;
  const end = start + itemsPerPage.value;
  return filteredRecords.slice(start, end);
});

const totalRecords = computed(
  () => filterRecords(fetchedData.value, searchQuery.value).length
);

// Fix the chartLabels and chartDatasets
const chartLabels = computed(() => 
  fetchedData.value.map((item) => item.name)
);

const chartDatasets = computed(() => [
  {
    label: "Average Inbound Rate",
    data: fetchedData.value.map((item) => parseFloat(item.avg_inbound_rate) || 0),
    borderColor: "#36A2EB",
    backgroundColor: "#36A2EB",
    borderWidth: 1,
  },
  {
    label: "Average Outbound Rate",
    data: fetchedData.value.map((item) => parseFloat(item.avg_outbound_rate) || 0),
    borderColor: "#FF6384",
    backgroundColor: "#FF6384",
    borderWidth: 1,
  },
]);

// Apply filters (this is automatic in this implementation)
const fetchData = async () => {
  try {
    const response = await axios.get(endpoints.ipmListTopData, {
      params: {
        start_date: startDate.value,
        end_date: endDate.value,
        value: value.value,
        top_n: topNumber.value,
        order_by: sortBy.value
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
    const response = await axios.get(endpoints.ipmListTopData, {
      params: {
        start_date: startDate.value,
        end_date: endDate.value,
        value: value.value,
        top_n: topNumber.value,
        order_by: sortBy.value
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
  const headers = Object.keys(data[0]).filter(header => header).join(',');

  // Map through the data and exclude 'id' from the rows
  const rows = data.map(row => {
    return [
      row.index,
      row.name,
      `${row.avg_inbound_rate} ${unitOfMeasurement.value}/s`, // Append unit dynamically
      `${row.avg_outbound_rate} ${unitOfMeasurement.value}/s`, // Append unit dynamically
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
                <v-select
                  v-model="value"
                  label="Value"
                  :items="valueItems"
                  outlined
                />
              </v-col>
              <v-col cols="12" md="3" class="mt-6">
                <v-text-field
                  v-model="topNumber"
                  label="Top Number"
                  outlined
                />
              </v-col>
              <v-col cols="12" md="3" class="mt-6">
                <v-select
                  v-model="sortBy"
                  label="Sort By"
                  :items="sortByItems"
                  outlined
                />
              </v-col>
              <v-col cols="12" md="3">
                <v-btn block @click="applyFilters" class="mt-6"
                  >Apply Filter</v-btn
                >
              </v-col>
            </v-row>
          </v-container>
        </VExpansionPanelText>
      </VExpansionPanel>
    </VExpansionPanels>

    <!-- Chart Section -->
    <VCard class="mb-6">
      <VCardItem class="pb-4">
        <VCardTitle>Bar Chart: Device Interface Data</VCardTitle>
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
        <VCardTitle>IPM Data Records</VCardTitle>
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

        <div>
          <v-btn @click="exportCSV(fetchedData)" class="" :disabled="!isFiltered">Export</v-btn>
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
