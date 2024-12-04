import { setupLayouts } from 'virtual:generated-layouts';
import { createRouter, createWebHistory } from 'vue-router/auto';
import { redirects } from './additional-routes';
import { useUserStore } from "@/utils/store.js";

// Recursively apply layouts to child routes
function recursiveLayouts(route) {
  if (route.children && route.children.length) {
    route.children = route.children.map(child => recursiveLayouts(child));
    return route;
  }
  
  return setupLayouts([route])[0];
}

// Router setup
const router = createRouter({
  history: createWebHistory(import.meta.env.VITE_APP_BASE_URL),
  scrollBehavior(to) {
    // Smooth scroll to hash or top of the page
    if (to.hash) {
      return { el: to.hash, behavior: 'smooth', top: 60 };
    }
    return { top: 0 };
  },
  extendRoutes: pages => [
    ...redirects,  // Include additional redirects
    ...pages.map(route => recursiveLayouts(route))  // Apply layouts recursively
  ],
});

// //Navigation guard for authentication
// router.beforeEach(async (to, from, next) => {
//   const userStore = useUserStore();
//   const isAuthenticated = userStore.getToken || await userStore.checkAuth();  // Check auth status
  
//   if (!isAuthenticated && to.path !== '/login') {
//     // Redirect to login if not authenticated and trying to access non-login pages
//     next({ path: '/login' });
//   } else if (isAuthenticated && to.path === '/login') {
//     // Redirect to home if already authenticated and trying to access login page
//     next({ path: '/apps/ipm/main-dashboard' });
//   } else {
//     // Allow navigation if authenticated or accessing login
//     next();
//   }
// });

export { router };

export default function (app) {
  app.use(router);  // Apply router to the app
}
