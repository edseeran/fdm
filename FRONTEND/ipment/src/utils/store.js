// stores/user.js
import { defineStore } from "pinia";
import axios from "axios";
import endpoints from "./endpoint";

export const useUserStore = defineStore("user", {
  state: () => ({
    userToken: null,
    userId: null,
    userProfile: null,
    permissions: null,
    userGroup: null,
    isAuthenticated: false
  }),
  persist: {
    paths: ['userToken', 'userGroup'], // Only persist `token` and `session` (optional)
  },
  actions: {

    // Fetch User ID
    async setToken(token) {
      this.userToken = token;
    },

    clearToken() {
      this.userToken = null;
    },

    logout() {
      this.userId = null;
      this.userProfile = null;
      this.permissions = null;
      this.userGroup = null;
      this.isAuthenticated = false;
    },

    // Check Authentication
    async checkAuth() {
      try {
        const response = await axios.get(endpoints.verifyAuth, {
          headers: {
            'Content-Type': 'application/json',
            Accept: 'application/json',
            'Cache-Control': 'no-cache',
          },
          withCredentials: true,
        });

        this.userId = response.data.user_id;
        this.isAuthenticated = true;
      } catch (error) {
        console.error('Error checking authentication:', error);

        // Reset authentication state if it fails
        this.userId = null;
        this.isAuthenticated = false;

        return false;
      }
    },

    // Fetch User Profile
    async fetchUserProfile() {     
      try {
        const response = await axios.get(endpoints.userProfile.view, {
          headers: {
            "Content-Type": "application/json", // Ensure the CSRF token is defined and valid
            Accept: "application/json",
            "Cache-Control": "no-cache",
            "X-Csrftoken": this.userToken,
          },
          params: {
            id: this.userId
          },
          withCredentials: true,
        });
        this.userProfile = response.data; // Assuming the response has a `userId` field
        this.permissions = response.data.permissions;
        this.userGroup = response.data.group;
      } catch (error) {
        console.error("Error fetching user profile:", error);
      }
    },
    // New function to fetch user name by ID
    async fetchUserNameById(userId) {
        try {
        const response = await axios.get(endpoints.userName.view, {
            headers: {
            "Content-Type": "application/json",
            Accept: "application/json",
            "Cache-Control": "no-cache",
            "X-Csrftoken": this.userToken,
            },
            params: {
            id: userId
            },
            withCredentials: true,
        });

        return response.data.name;
        } catch (error) {
        console.error(`Error fetching user name for ID ${userId}:`, error);
        return "Unknown";
        }
    },
  },
  getters: {
    getToken: (state) => state.userToken,
    getUserId: (state) => state.userId,
    getUserProfile: (state) => state.userProfile,
    getPermissions: (state) => state.permissions,
    getGroup: (state) => state.userGroup,
  },
});
