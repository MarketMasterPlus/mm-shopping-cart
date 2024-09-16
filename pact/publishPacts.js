// mm-shopping-cart/pact/publishPacts.js
import dotenv from 'dotenv';
dotenv.config({ path: './.env' });
import { exec } from 'child_process';
import path from 'path';
import { fileURLToPath } from 'url';

const __dirname = path.dirname(fileURLToPath(import.meta.url));
const pactFiles = path.resolve(__dirname, 'pacts');
const pactBrokerUrl = process.env.PACT_BROKER_URL;
const pactBrokerUsername = process.env.PACT_BROKER_USERNAME;
const pactBrokerPassword = process.env.PACT_BROKER_PASSWORD;

// Use a single-line command to avoid shell parsing issues
const pactBrokerPath = './node_modules/.bin/pact-broker';
const publishCommand = `${pactBrokerPath} publish ${pactFiles} --consumer-app-version=1.0.0 --broker-base-url=${pactBrokerUrl} --broker-username=${pactBrokerUsername} --broker-password=${pactBrokerPassword}`;

exec(publishCommand, (error, stdout, stderr) => {
  if (error) {
    console.error(`exec error: ${error}`);
    return;
  }
  console.log(`stdout: ${stdout}`);
  console.error(`stderr: ${stderr}`);
});
