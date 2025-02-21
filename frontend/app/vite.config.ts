/// <reference types="vitest" />
import { builtinModules } from 'module';
import { join, resolve } from 'path';
import { VuetifyResolver } from 'unplugin-vue-components/resolvers';
import Components from 'unplugin-vue-components/vite';
import ScriptSetup from 'unplugin-vue2-script-setup/vite';
import { splitVendorChunkPlugin, defineConfig } from 'vite';
// @ts-ignore
import istanbul from 'vite-plugin-istanbul';
import { VitePWA } from 'vite-plugin-pwa';
import { createVuePlugin as vue } from 'vite-plugin-vue2';

const PACKAGE_ROOT = __dirname;
const envPath = process.env.VITE_PUBLIC_PATH;
const publicPath = envPath ? envPath : '/';
const isDevelopment = process.env.NODE_ENV === 'development';
const isTest = !!process.env.VITE_TEST;

if (isTest) {
  console.log('Running in test mode. Enabling Coverage');
}

if (envPath) {
  console.log(`A custom publicPath has been specified, using ${envPath}`);
}

export default defineConfig({
  resolve: {
    alias: {
      '@': resolve(PACKAGE_ROOT, 'src'),
      '~@': resolve(PACKAGE_ROOT, 'src')
    }
  },
  // @ts-ignore
  test: {
    globals: true,
    environment: 'jsdom',
    deps: {
      inline: ['vuetify']
    },
    coverage: {
      reportsDirectory: 'tests/unit/coverage',
      reporter: ['json'],
      include: ['src/*'],
      exclude: ['node_modules', 'tests/', '**/*.d.ts']
    }
  },
  base: publicPath,
  define: {
    'process.env': { ...process.env }
  },
  plugins: [
    splitVendorChunkPlugin(),
    vue(),
    ScriptSetup(),
    Components({
      dts: true,
      include: [/\.vue$/, /\.vue\?vue/],
      resolvers: [VuetifyResolver()]
    }),
    ...(isTest
      ? [
          istanbul({
            include: 'src/*',
            exclude: ['node_modules', 'tests/', '**/*.d.ts'],
            extension: ['.ts', '.vue']
          })
        ]
      : []),
    VitePWA({
      base: '',
      registerType: 'prompt',
      manifest: false
    })
  ],
  server: {
    port: 8080
  },
  build: {
    sourcemap: isDevelopment,
    outDir: 'dist',
    assetsDir: '.',
    minify: true,
    rollupOptions: {
      external: [
        'electron',
        'electron-devtools-installer',
        ...builtinModules.flatMap(p => [p, `node:${p}`])
      ],
      input: join(PACKAGE_ROOT, 'index.html')
    },
    emptyOutDir: false
  }
});
