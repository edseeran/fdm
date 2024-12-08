<script setup>
import { ref, computed, watch } from "vue";
import { useToast } from "vue-toastification";

// Dummy data array
const dummyData = ref([
  {
    id:"485754434393989E",
    usage:"22.5 TB",
    data_plan:"FTTX_600MB",
    subscribers_name:"ENCARNACION EDNA",
    olt_name:"TAG001-OLT-03",
    nap_code:"TAG001 LP124 NP1-2",
    site_name:"BALIBAGO - MIGRATE ",
    number_of_hosts:"8",
    user_idleness:"1",
    intensive_downloading_user:"0.00%",
    total_data_received:"22.5 TB",
    total_data_sent:"9.7 TB",
  },
 
]);

// Control the state of the drawer from the parent component
const isAddDrawerOpen = ref(false);
const openAddDrawer = () => {
  isAddDrawerOpen.value = true;
};

const isUpdateDrawerOpen = ref(false);
const openUpdateDrawer = () => {
  isUpdateDrawerOpen.value = true;
};

const showModal = ref(false);
const selectedItem = ref(null);

const openModal = (item) => {
  selectedItem.value = item;
  showModal.value = true;
};

// V-Models for filter
const toast = useToast();
const status = ref("down");
const isFiltersExpanded = ref(true);
const isFiltered = ref(false);
const selectedRows = ref([]);

const statusFilter = [
  { value: "down", title: "Down" },
  { value: "warning", title: "Warning" },
];

// Table headers
const headers = [
  { title: "Identity", key: "id", sortable: true },
  { title: "Usage", key: "usage", sortable: true },
  { title: "Data Plan", key: "data_plan", sortable: true },
  { title: "Subscriber's Name", key: "subscribers_name", sortable: true },
  { title: "OLT Name", key: "olt_name", sortable: true },
  { title: "NAP Code", key: "nap_code", sortable: true },
  { title: "Site Name", key: "site_name", sortable: true },
  { title: "Number Of Hosts", key: "number_of_hosts", sortable: true },
  { title: "User Idleness", key: "user_idleness", sortable: true },
  { title: "Intensive Downloading User", key: "intensive_downloading_user", sortable: true },
  { title: "Total Data Received", key: "total_data_received", sortable: true },
  { title: "Total Data Sent", key: "total_data_sent", sortable: true },
];

// Pagination logic
const itemsPerPage = ref(10);
const page = ref(1);
const searchQuery = ref("");

// Display all records with a search filter based on the data in the headers
const filteredData = computed(() => {
  if (!searchQuery.value) {
    return dummyData.value;
  }

  const lowerCaseQuery = searchQuery.value.toLowerCase();
  const headerKeys = headers.map(header => header.key); // Extract the keys from headers

  return dummyData.value.filter((item) => {
    // Check if any column defined in headers contains the search query
    return headerKeys.some((key) => {
      const field = item[key];
      if (field && typeof field === 'string') {
        return field.toLowerCase().includes(lowerCaseQuery);
      }
      return false;
    });
  });
});


// Paginated records computed property
const paginatedRecords = computed(() => {
  const start = (page.value - 1) * itemsPerPage.value;
  const end = start + itemsPerPage.value;
  return filteredData.value.slice(start, end);
});

const totalRecords = computed(() => filteredData.value.length);

const fetchedData = ref([]);

// Apply filters (this is automatic in this implementation)
const applyFilters = () => {
  try {
    fetchedData.value = dummyData.value; // Directly set fetchedData to dummyData
    isFiltered.value = true;
    toast.success("Records loaded!");
  } catch (error) {
    console.error("Error using dummy data:", error);
    toast.error("Error loading dummy data!");
  }
};
</script>

<template>
  <section>
    <!-- Data Table Section -->
    <VCard class="mb-6">
      <VCardItem class="pb-4">
        <VCardTitle>Fraud Detection and Management Records</VCardTitle>
      </VCardItem>

      <VCardText class="d-flex flex-wrap gap-4">
        <div class="me-3 d-flex gap-3">
          <AppSelect
            :model-value="itemsPerPage"
            :items="[{ value: 10, title: '10' }, { value: 25, title: '25' }, { value: 50, title: '50' }, { value: 100, title: '100' }, { value: -1, title: 'All' }]"
            @update:model-value="itemsPerPage = parseInt($event, 10)"
          />
        </div>

        <VSpacer />

        <div class="app-user-search-filter d-flex align-center flex-wrap gap-4">
          <!-- Search -->
          <div style="inline-size: 15.625rem">
            <AppTextField v-model="searchQuery" placeholder="Search Record" />
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
        :headers="headers"
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

        <!-- Other table columns -->
        <template #item.actions="{ item }">

          <IconBtn @click="openModal(item)" title="More Information">
            <VIcon icon="tabler-eye" />
          </IconBtn>

          <IconBtn @click="openUpdateDrawer" title="Edit Utilization">
            <VIcon icon="tabler-pencil" />
          </IconBtn>

          <IconBtn title="Delete Record">
            <VIcon icon="tabler-trash" />
          </IconBtn>

        </template>
      </VDataTableServer>
    </VCard>

    <!-- Modal for showing detailed item data -->
    <v-dialog v-model="showModal" max-width="600" max-length="200">
      <v-card>
        <v-card-title class="mt-6 ml-2">Details for {{ selectedItem?.name }}</v-card-title>
        <v-card-text>
          <div v-if="selectedItem">
            <p><strong>Utility:</strong> {{ selectedItem.util_type }}</p>
            <p><strong>Name:</strong> {{ selectedItem.name }}</p>
            <p><strong>Sensor ID:</strong> {{ selectedItem.sensor_id }}</p>
            <p><strong>Capacity:</strong> {{ selectedItem.capacity }}</p>
            <p><strong>Status:</strong> {{ selectedItem.status }}</p>
            <p><strong>Group:</strong> {{ selectedItem.group }}</p>
            <p><strong>Ping:</strong> {{ selectedItem.ping }}</p>
            <p><strong>In Volume:</strong> {{ selectedItem.in_volume }}</p>
            <p><strong>In Speed:</strong> {{ selectedItem.in_speed }}</p>
            <p><strong>Out Volume:</strong> {{ selectedItem.out_volume }}</p>
            <p><strong>Out Speed:</strong> {{ selectedItem.out_speed }}</p>
            <p><strong>Total Volume:</strong> {{ selectedItem.total_volume }}</p>
            <p><strong>Total Speed:</strong> {{ selectedItem.total_speed }}</p>
            <p><strong>In Volume Utilization:</strong> {{ selectedItem.in_volume_utilization }}</p>
            <p><strong>In Speed Utilization:</strong> {{ selectedItem.in_speed_utilization }}</p>
            <p><strong>Out Volume Utilization:</strong> {{ selectedItem.out_volume_utilization }}</p>
            <p><strong>Out Speed Utilization:</strong> {{ selectedItem.out_speed_utilization }}</p>
            <p><strong>Total Volume Utilization:</strong> {{ selectedItem.total_volume_utilization }}</p>
            <p><strong>Total Speed Utilization:</strong> {{ selectedItem.total_speed_utilization }}</p>
          </div>
        </v-card-text>
        <v-card-actions>
          <v-btn color="primary" text @click="showModal = false">Close</v-btn>
        </v-card-actions>
      </v-card>
    </v-dialog>

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
