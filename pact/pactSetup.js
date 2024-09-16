// mm-shopping-cart/pact/pactSetup.js
import { Pact } from '@pact-foundation/pact';
import path from 'path';

const provider = new Pact({
    consumer: 'mm-shopping-cart',
    provider: 'mm-inventory',
    port: 0, // Dynamic port assignment
    log: path.resolve(process.cwd(), 'logs', 'pact.log'),
    dir: path.resolve(process.cwd(), 'pacts'),
    logLevel: 'DEBUG',
});

export default provider;
