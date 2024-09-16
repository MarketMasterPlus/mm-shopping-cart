// mm-shopping-cart/pact/tests/shoppingCartCustomerPact.spec.js
import { customerProvider } from '../pactSetup.js';
import { expect } from 'chai';
import { Matchers } from '@pact-foundation/pact';
import { hypotheticalGetUserDetails } from '../utils/hypotheticalRequests.js';

describe('Pact with Customer service', () => {
  before(() => customerProvider.setup());

  after(() => customerProvider.finalize());

  afterEach(() => customerProvider.verify());

  describe('when a request to get user details is made', () => {
    before(() => {
      return customerProvider.addInteraction({
        state: 'it has a customer with cpf 11111111111',
        uponReceiving: 'a request for customer details',
        withRequest: {
          method: 'GET',
          path: '/customers/11111111111',
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
            addressid: "14",
            cpf: "11111111111",
            email: "r@r.com",
            fullname: "Rodrigo Alves Costa"
          }),
        },
      });
    });

    it('can process the user details', async () => {
      const fullUrl = `http://localhost:${customerProvider.opts.port}/customers/11111111111`;
      const response = await hypotheticalGetUserDetails(fullUrl);
      expect(response.status).to.equal(200);
      expect(response.data).to.deep.include({
        addressid: "14",
        cpf: "11111111111",
        email: "r@r.com",
        fullname: "Rodrigo Alves Costa"
      });
    });
  });
});
