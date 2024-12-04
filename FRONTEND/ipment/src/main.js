import { createApp } from 'vue';
import App from '@/App.vue';
import { registerPlugins } from '@core/utils/plugins';
import { createPinia } from 'pinia'
import piniaPersistedState from 'pinia-plugin-persistedstate';

// Toastification
import Toast, { POSITION } from 'vue-toastification';
import 'vue-toastification/dist/index.css'; // Import the styles for toastification

// Styles
import '@core/scss/template/index.scss';
import '@styles/styles.scss';

// Create vue app
const app = createApp(App);
const pinia = createPinia()
pinia.use(piniaPersistedState);

// Register plugins
registerPlugins(app);

// Toastification options
const toastOptions = {
  position: POSITION.TOP_RIGHT, // Position of the toast notification
  timeout: 3000, // Auto close time in milliseconds
};

// Register vue-toastification plugin
app.use(Toast, toastOptions);
app.use(pinia);

// Mount vue app
app.mount('#app');
