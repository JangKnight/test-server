import { defineConfig } from "vite";
import react from "@vitejs/plugin-react";
import tailwindcss from "@tailwindcss/vite";

export default defineConfig({
  plugins: [react(), tailwindcss()],
  server: {
    host: true, // Needed for Docker
    port: 4444,
    strictPort: true,
    allowedHosts: ["anthonysjhenry.com", "www.anthonysjhenry.com", "client"],
    hmr: {
      // The browser connects to Caddy on 443, which then proxies to 4444
      clientPort: 443,
    },
    watch: {
      usePolling: true,
    },
  },
});

// https: {
//   key: fs.readFileSync(
//     path.resolve(__dirname, "certs/localhost+3-key.pem"),
//   ),
//   cert: fs.readFileSync(path.resolve(__dirname, "certs/localhost+3.pem")),
// },
