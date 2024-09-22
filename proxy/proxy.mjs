import { initializeAuthProxy } from '@propelauth/auth-proxy'
import dotenv from 'dotenv'
import { fileURLToPath } from 'url'
import path from 'path'
// Get the directory of the current file
const __filename = fileURLToPath(import.meta.url)
const __dirname = path.dirname(__filename)

// Load .env file from parent of parent directory
dotenv.config({ path: path.join(__dirname, '..', '.env') })
const propelAuthUrl = process.env.PROPEL_AUTH_URL
const propelApiKey = process.env.PROPEL_AUTH_API_KEY

await initializeAuthProxy({
    authUrl: propelAuthUrl,
    integrationApiKey: propelApiKey,
    proxyPort: 8000,
    urlWhereYourProxyIsRunning: 'http://127.0.0.1:8000',
    target: {
        host: '127.0.0.1',
        port: 8501,
        protocol: 'http:'
    },
})

