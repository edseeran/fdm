import { useUserStore } from "@/utils/store.js";

export const redirects = [
  {
    path: "/",
    name: "index",
    beforeEnter: async (to, from, next) => {
      const userStore = useUserStore();
  
      try {
        const isAuthenticated = userStore.getToken
  
        // Redirect based on authentication status
        if (isAuthenticated) {
          next({ name: "apps-ipm-main-dashboard" });
        } else {
          next({ name: "login", query: to.query });
        }
      } catch (error) {
        console.error("Error checking authentication:", error);
        next({ name: "login", query: to.query }); // Fallback to login on error
      }
    }
  },  
  {
    path: '/login',
    name: 'login',
    beforeEnter: async (to, from, next) => {
      console.log('Checking authentication for login route...');
      const userStore = useUserStore();

      try {
        const isAuthenticated = userStore.getToken;
        console.log('Authenticated:', isAuthenticated);

        // Redirect authenticated users away from the login page
        if (isAuthenticated) {
          next({ name: 'apps-ipm-main-dashboard' });
        } else {
          next(); // Stay on the login page
        }
      } catch (error) {
        console.error('Error checking authentication on login route:', error);
        next(); // Allow access to the login page in case of an error
      }
    },
  },
  {
    path: '/apps/ipm/main-dashboard',
    name: 'apps-ipm-main-dashboard',
    beforeEnter: async (to, from, next) => {
      const userStore = useUserStore();

      try {
        const isAuthenticated = userStore.getToken;
        console.log('Authenticated:', isAuthenticated);

        // Redirect authenticated users away from the login page
        if (isAuthenticated) {
          next();
        } else {
          next({ name: 'login' });
        }
      } catch (error) {
        console.error('Error checking authentication on route:', error);
        next({ name: 'login' }); // Allow access to the login page in case of an error
      }
    },
  },
  {
    path: '/apps/ipm/utilization',
    name: 'apps-ipm-utilization',
    beforeEnter: async (to, from, next) => {
      const userStore = useUserStore();

      try {
        const isAuthenticated = userStore.getToken;
        console.log('Authenticated:', isAuthenticated);

        // Redirect authenticated users away from the login page
        if (isAuthenticated) {
          next();
        } else {
          next({ name: 'login' }); // Stay on the login page
        }
      } catch (error) {
        console.error('Error checking authentication on route:', error);
        next({ name: 'login' }); // Allow access to the login page in case of an error
      }
    },
  },
];
