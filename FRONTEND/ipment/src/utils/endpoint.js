let BASE_URL = "";

// Detect the current hostname and set the base URL dynamically
if (window.location.hostname === "198.18.110.203") {
    BASE_URL = "https://198.18.110.203/api";
} else if (window.location.hostname === "161.49.62.203") {
    BASE_URL = "https://161.49.62.203/api";
} else if (window.location.hostname === "netops-tool.convergeict.com") {
    BASE_URL = "https://enterprise-trafficmonitoring.convergeict.com/api";
} else {
    // Default to local development URL
    BASE_URL = "http://127.0.0.1:8000";
}

const userAccountEndpoint = (resource, method = "") =>
    `${BASE_URL}/UserAccount/${method}/${resource}`;
const ipmDashboardEndpoint = (resource, method = "") =>
    `${BASE_URL}/iPM/${method}/${resource}`;

const endpoints = {
    // ***** AUTHENTICATION ***** //

    // Authentication Endpoints //
    login: `${BASE_URL}/UserAccount/login/`,
    verifyAuth: `${BASE_URL}/UserAccount/check-login/`,
    logout: `${BASE_URL}/UserAccount/logout/`,

    // ***** USER ENDPOINTS ***** //

    // User
    userAccount: {
        list: userAccountEndpoint("user", "list"),
        view: userAccountEndpoint("user", "view"),
        create: userAccountEndpoint("user", "create"),
        update: userAccountEndpoint("user", "update"),
        delete: userAccountEndpoint("user", "delete"),
    },
    // User Profile
    userProfile: {
        list: userAccountEndpoint("user-profile", "list"),
        view: userAccountEndpoint("user-profile", "view"),
        create: userAccountEndpoint("user-profile", "create"),
        update: userAccountEndpoint("user-profile", "update"),
        delete: userAccountEndpoint("user-profile", "delete"),
    },
    // User Name
    userName: {
        list: userAccountEndpoint("user-name", "list"),
        view: userAccountEndpoint("user-name", "view"),
    },
    // Group
    userGroup: {
        list: userAccountEndpoint("group", "list"),
        view: userAccountEndpoint("group", "view"),
        create: userAccountEndpoint("group", "create"),
        update: userAccountEndpoint("group", "update"),
        delete: userAccountEndpoint("group", "delete"),
    },
    // Permission
    userGroup: {
        list: userAccountEndpoint("permission", "list"),
        view: userAccountEndpoint("permission", "view"),
    },

    // ***** IPM ENDPOINTS ***** //

    // Dashboard
    ipmDashboard: {
        list: ipmDashboardEndpoint("dashboard", "list"),
        view: ipmDashboardEndpoint("dashboard", "view"),
        create: ipmDashboardEndpoint("dashboard", "create"),
        update: ipmDashboardEndpoint("dashboard", "update"),
        delete: ipmDashboardEndpoint("dashboard", "delete"),
    },
    // IPM LIST DATA
    ipmListData: `${BASE_URL}/iPM/list/data`,
    // IPM LIST TOP DATA
    ipmListTopData: `${BASE_URL}/iPM/list-top/data`,
    // IPM LIST CIRCUIT
    ipmListCircuit: `${BASE_URL}/iPM/list-circuit/data`,
    // IPM DELETE DATA
    ipmDeleteData: `${BASE_URL}/iPM/delete/data`,
    // IPM LIST UNIT
    ipmListConfig: `${BASE_URL}/Configuration/list/unit`,
};

export default endpoints;
