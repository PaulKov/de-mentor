export default defineNuxtConfig({
  compatibilityDate: '2026-06-14',
  devtools: { enabled: false },
  css: ['~/assets/css/main.css'],
  app: {
    head: {
      title: 'Greenplum Academy Portal',
      meta: [
        {
          name: 'description',
          content: 'Academy Experience v5 portal for Greenplum mentor sessions'
        }
      ]
    }
  }
})
