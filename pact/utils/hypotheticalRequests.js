// mm-shopping-cart/pact/utils/hypotheticalRequests.js
import axios from 'axios';

// Now expects a full URL to be passed in, including path and query if necessary
export async function hypotheticalGetInventoryItem(fullUrl) {
  try {
    const response = await axios.get(fullUrl, {
        headers: {
          Accept: 'application/json',
        }
    });
    return {
      status: response.status,
      data: response.data
    };
  } catch (error) {
    return {
      status: error.response ? error.response.status : 500,
      data: error.response ? error.response.data : {}
    };
  }
}

// Now expects a full URL to be passed in, including path and query if necessary
export async function hypotheticalGetUserDetails(fullUrl) {
  try {
    const response = await axios.get(fullUrl, {
        headers: {
          Accept: 'application/json',
        }
    });
    return {
      status: response.status,
      data: response.data
    };
  } catch (error) {
    return {
      status: error.response ? error.response.status : 500,
      data: error.response ? error.response.data : {}
    };
  }
}
