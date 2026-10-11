// https://nuxt.com/docs/api/configuration/nuxt-config
export default defineNuxtConfig({
  compatibilityDate: '2025-01-15',
  future: {
    compatibilityVersion: 4,
  },
  devtools: { enabled: false },
  telemetry: false,
  app: {
    head: {
      title: 'VEDANAM — Technology Value Intelligence',
      meta: [
        { charset: 'utf-8' },
        { name: 'viewport', content: 'width=device-width, initial-scale=1, viewport-fit=cover' },
        { name: 'theme-color', content: '#f5f5f7' },
        {
          name: 'description',
          content: 'Vedanam is an architectural and sensory intelligence platform for enterprise technology value, dependency topologies, and proactive governance.'
        }
      ],
      link: [
        { rel: 'preconnect', href: 'https://fonts.googleapis.com' },
        { rel: 'preconnect', href: 'https://fonts.gstatic.com', crossorigin: '' },
        {
          rel: 'stylesheet',
          href: 'https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:ital,wght@0,300;0,400;0,500;0,600;0,700;0,800;1,400&family=JetBrains+Mono:wght@400;500;600&display=swap'
        },
        {
          rel: 'stylesheet',
          href: 'https://cdn.jsdelivr.net/npm/katex@0.16.11/dist/katex.min.css'
        }
      ],
      script: [
        {
          src: 'https://cdn.jsdelivr.net/npm/katex@0.16.11/dist/katex.min.js',
          defer: true
        }
      ]
    }
  },
  css: [
    '~/assets/css/main.css'
  ]
})
