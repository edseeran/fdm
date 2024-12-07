import { computed } from "vue";

export default computed(() => {
  return [
    {
      title: "FDM",
      to: "apps-ipm",
      icon: { icon: "tabler-server" },
      children: [
        {
          title: "Main Dashboard",
          to: "apps-ipm-main-dashboard",
        },
      ],
    },
  ];
});
