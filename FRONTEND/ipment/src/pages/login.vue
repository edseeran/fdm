<script setup>
import { VForm } from "vuetify/components/VForm";
import { VNodeRenderer } from "@layouts/components/VNodeRenderer";
import { themeConfig } from "@themeConfig";
import endpoints from "../utils/endpoint.js";
import { ref, watch } from 'vue';  // Import ref and watch from Vue
import { useUserStore } from "@/utils/store.js";

const userStore = useUserStore();

definePage({
  meta: {
    layout: "blank",
    unauthenticatedOnly: true,
  },
});

const isPasswordVisible = ref(false);
const route = useRoute();
const router = useRouter();
const errors = ref({
  username: undefined,
  password: undefined,
  general: undefined, // Add a general error for invalid login attempts
});

const refVForm = ref();
const formIsValid = ref(false);  // Track overall form validity
const loading = ref(false);  // Track the loading state

const credentials = ref({
  username: "",
  password: "",
});

const rememberMe = ref(false);

// Validation rules
const requiredValidator = value => !!value || 'This field is required';
const minLengthValidator = value => value.length >= 6 || 'Minimum 6 characters required';

// Watch both username and password validity to control the formIsValid state
watch(
  () => [credentials.value.username, credentials.value.password],
  ([username, password]) => {
    formIsValid.value = username.length > 0 && password.length >= 6;
  }
);

const login = async () => {
  loading.value = true;  // Start loading

  try {
    const res = await fetch(endpoints.login, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({
        username: credentials.value.username,
        password: credentials.value.password,
      }),
      credentials: 'include',
    });

    if (!res.ok) {
      const errorData = await res.json();
      throw new Error(errorData.message || 'Invalid credentials');
    }

    const data = await res.json();
    const { session_id, csrf_token } = data; // Adjusted to match response keys

    // Store session and CSRF token
    useCookie('sessionid').value = session_id; // Updated to session_id
    useCookie('csrftoken').value = csrf_token; // Updated to csrf_token

    userStore.setToken(csrf_token);

    // Redirect to the desired page
    await nextTick(() => {
      router.replace(route.query.to ? String(route.query.to) : '/apps/ipm/main-dashboard');
    });
  } catch (error) {
    console.error('Login error:', error);
    if (error.message === 'Invalid credentials') {
      errors.value.general = 'Incorrect username or password. Please try again.';
    } else {
      errors.value.general = 'An error occurred during login. Please try again later.';
    }
  } finally {
    loading.value = false;  // Stop loading after login attempt
  }
};

const onSubmit = () => {
  refVForm.value?.validate().then(({ valid: isValid }) => {
    if (isValid) {
      errors.value.general = undefined; // Clear general error message before attempting login
      login();
    }
  });
};
</script>

<template>
  <div class="auth-wrapper d-flex align-center justify-center pa-4">
    <div class="position-relative my-sm-16">
      <!-- Top and Bottom Shapes -->
      <VNodeRenderer
        :nodes="h('div', { innerHTML: authV1TopShape })"
        class="text-primary auth-v1-top-shape d-none d-sm-block"
      />
      <VNodeRenderer
        :nodes="h('div', { innerHTML: authV1BottomShape })"
        class="text-primary auth-v1-bottom-shape d-none d-sm-block"
      />

      <!-- Auth Card -->
      <VCard class="auth-card" max-width="460" :class="$vuetify.display.smAndUp ? 'pa-6' : 'pa-0'">
        <VCardItem class="justify-center">
          <VCardTitle>
            <RouterLink to="/">
              <div class="app-logo">
                <VNodeRenderer :nodes="themeConfig.app.logo" />
                <h1 class="app-logo-title">{{ themeConfig.app.title }}</h1>
              </div>
            </RouterLink>
          </VCardTitle>
        </VCardItem>

        <VCardText>
          <!-- Display general error message -->
          <VAlert v-if="errors.general" type="error" class="mb-4">{{ errors.general }}</VAlert>

          <!-- Show loading indicator if loading -->
          <div v-if="loading" class="text-center my-4">
            <VProgressCircular indeterminate color="primary"></VProgressCircular>
            <p>Loading, please wait...</p>
          </div>

          <!-- Login form -->
          <VForm ref="refVForm" @submit.prevent="onSubmit" v-if="!loading">
            <VRow>
              <!-- Username -->
              <VCol cols="12">
                <AppTextField
                  v-model="credentials.username"
                  autofocus
                  label="Username"
                  type="text"
                  :rules="[requiredValidator]"
                  placeholder="Enter your username"
                />
              </VCol>

              <!-- Password -->
              <VCol cols="12">
                <AppTextField
                  v-model="credentials.password"
                  label="Password"
                  :rules="[requiredValidator, minLengthValidator]"
                  placeholder="············"
                  :type="isPasswordVisible ? 'text' : 'password'"
                  :append-inner-icon="isPasswordVisible ? 'tabler-eye-off' : 'tabler-eye'"
                  @click:append-inner="isPasswordVisible = !isPasswordVisible"
                />

                <!-- Remember me and forgot password -->
                <div class="d-flex align-center justify-space-between flex-wrap" style="visibility: hidden; margin: 0;">
                  <VCheckbox v-model="rememberMe" label="Remember me" />
                  <RouterLink class="text-primary" :to="{}">Forgot Password?</RouterLink>
                </div>

                <!-- Login button (disabled if form is not valid or loading) -->
                <VBtn block type="submit" :disabled="!formIsValid || loading">Login</VBtn>
              </VCol>
            </VRow>
          </VForm>
        </VCardText>
      </VCard>
    </div>
  </div>
</template>

<style lang="scss">
@use "@core/scss/template/pages/page-auth.scss";
</style>
