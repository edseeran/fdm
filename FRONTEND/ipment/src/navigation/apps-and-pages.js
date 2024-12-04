import { computed } from "vue";

export default computed(() => {
  return [
    {
      title: "IPM",
      to: "apps-ipm",
      icon: { icon: "tabler-server" },
      children: [
        {
          title: "Main Dashboard",
          to: "apps-ipm-main-dashboard",
        },
        {
          title: "Utilization",
          to: "apps-ipm-utilization",
        }  
      ],
    },
  ];
});
