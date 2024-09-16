// mm-shopping-cart/pact/tests/shoppingCartPact.spec.js
import { inventoryProvider } from '../pactSetup.js';
import { expect } from 'chai';
import { Matchers } from '@pact-foundation/pact';
import { hypotheticalGetInventoryItem } from '../utils/hypotheticalRequests.js';

describe('Pact with Inventory service', () => {
  before(() => inventoryProvider.setup());

  after(() => inventoryProvider.finalize());

  afterEach(() => inventoryProvider.verify());

  describe('when a request to get inventory item details is made', () => {
    before(() => {
      return inventoryProvider.addInteraction({
        state: 'it has inventory item details',
        uponReceiving: 'a request for inventory item details',
        withRequest: {
          method: 'GET',
          path: '/mm-inventory/1',
          headers: {
            Accept: 'application/json',
          },
        },
        willRespondWith: {
          status: 200,
          headers: {
            'Content-Type': 'application/json',
          },
          body: Matchers.somethingLike({
            id: 1,
            productid: 36,
            storeid: 34,
            price: 6,
            stock: 10
          }),
        },
      });
    });

    it('can process the inventory item details', async () => {
      const fullUrl = `http://localhost:${inventoryProvider.opts.port}/mm-inventory/1`;
      const response = await hypotheticalGetInventoryItem(fullUrl);
      expect(response.status).to.equal(200);
      expect(response.data).to.deep.include({
        id: 1,
        productid: 36,
        storeid: 34,
        price: 6,
        stock: 10
      });
    });
  });
});
