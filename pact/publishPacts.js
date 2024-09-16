// mm-shopping-cart/pact/publishPacts.js
import dotenv from 'dotenv';
dotenv.config({ path: './.env' });
import { execSync } from 'child_process';
import path from 'path';
import { fileURLToPath } from 'url';

const __dirname = path.dirname(fileURLToPath(import.meta.url));
const pactFiles = path.resolve(__dirname, 'pacts');
const pactBrokerUrl = process.env.PACT_BROKER_URL;
const pactBrokerUsername = process.env.PACT_BROKER_USERNAME;
const pactBrokerPassword = process.env.PACT_BROKER_PASSWORD;
const applicationVersion = process.env.APP_VERSION;

// Assemble command
const command = `npx pact-broker publish ${pactFiles} --consumer-app-version=${applicationVersion} --broker-base-url=${pactBrokerUrl} --broker-username=${pactBrokerUsername} --broker-password=${pactBrokerPassword}`;

try {
    const output = execSync(command);
    console.log(output.toString());
} catch (error) {
    console.error('Failed to publish pact:', error);
}
