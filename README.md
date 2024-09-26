```
PUC-Rio
Especialização em Desenvolvimento Fullstack
Disciplina: Desenvolvimento Back-end Avançado

Aluno: Rodrigo Alves Costa
```

# PUC-Rio  
**Especialização em Desenvolvimento Fullstack**  
**Disciplina: Desenvolvimento Back-end Avançado**  

Aluno: Rodrigo Alves Costa  

## Market Master: Shopping Cart Management Service

The `mm-shopping-cart` service is part of the Market Master project, a suite of microservices designed to manage various aspects of a supermarket e-commerce platform. This service handles shopping cart operations, including adding and removing items, updating cart status, and calculating totals. It integrates with the `mm-customer` and `mm-inventory` services for customer validation and inventory management.

### Related Market Master Microservices:
- [mm-inventory](https://github.com/MarketMasterPlus/mm-inventory) — Inventory (available items) Management
- [mm-product](https://github.com/MarketMasterPlus/mm-product) — Product (item registry) Management
- [mm-store](https://github.com/MarketMasterPlus/mm-store) — Store Management
- [mm-address](https://github.com/MarketMasterPlus/mm-address) — Address Management with ViaCEP API integration
- [mm-customer](https://github.com/MarketMasterPlus/mm-customer) — Customer/User Management
- [mm-pact-broker](https://github.com/MarketMasterPlus/mm-pact-broker) — Pact Broker for Contract tests
- [mm-ui](https://github.com/MarketMasterPlus/mm-ui) — User Interface for Market Master

---

## Quick Start

### Prerequisites
- **Docker** and **Docker Compose** are required to run this service.

### Steps to Run the Service
1. Clone the repository:  
   git clone https://github.com/MarketMasterPlus/mm-shopping-cart

2. Navigate to the project directory:  
   cd mm-shopping-cart

3. Start the services with Docker Compose:  
   docker-compose up -d

4. Access the Shopping Cart Management API at:  
   http://localhost:5706/

---

## Project Description

The `mm-shopping-cart` service handles the creation and management of shopping carts. Customers can add or remove items from their cart, and the service calculates totals based on item prices retrieved from the `mm-inventory` service. The service also communicates with the `mm-customer` service to validate customer data.

### Key Features
- **Shopping Cart Management**: Allows customers to manage their shopping cart, including adding, updating, and removing items.
- **Cart Checkout**: Finalizes cart payments by updating item stock and marking the cart as purchased.
- **Integration with Other Services**: Validates customer data with `mm-customer` and checks stock availability with `mm-inventory`.

---

## Docker Setup

The `docker-compose.yml` file configures the `mm-shopping-cart` service and a PostgreSQL database for data storage.

### Docker Compose Configuration:

version: '3.8'

services:
  db:
    image: postgres:latest
    container_name: mm-shopping-cart-db
    environment:
      POSTGRES_DB: postgres
      POSTGRES_USER: marketmaster
      POSTGRES_PASSWORD: password
    volumes:
      - postgres_data:/var/lib/postgresql/data
      - ./db/mm-shopping-cart.sql:/docker-entrypoint-initdb.d/mm-shopping-cart.sql
    ports:
      - 5437:5432
    networks:
      - marketmaster-network

  product_service:
    build: .
    container_name: mm-shopping-cart
    ports:
      - 5706:5706
    depends_on:
      - db
    environment:
      FLASK_APP: app.py
      FLASK_ENV: development
    volumes:
      - .:/app
    networks:
      - marketmaster-network

volumes:
  postgres_data:

networks:
  marketmaster-network:
    external: true

To start the service using Docker, run:

docker-compose up -d

---

## API Endpoints

### Shopping Cart Management:
- **GET /mm-shopping-cart/**  
  Retrieves a list of all shopping carts or filters by customer CPF.  
  Example:  
  curl http://localhost:5706/mm-shopping-cart/?customercpf=12345678901

- **POST /mm-shopping-cart/**  
  Creates a new shopping cart for a customer.  
  Example:  
  curl -X POST http://localhost:5706/mm-shopping-cart/ -d '{"customercpf": "12345678901"}'

- **GET /mm-shopping-cart/{id}**  
  Retrieves detailed information for a shopping cart, including the total sum of items.  
  Example:  
  curl http://localhost:5706/mm-shopping-cart/1

- **PUT /mm-shopping-cart/{id}**  
  Updates a shopping cart.  
  Example:  
  curl -X PUT http://localhost:5706/mm-shopping-cart/1 -d '{"status": true}'

- **DELETE /mm-shopping-cart/{id}**  
  Deletes a shopping cart by its unique identifier.  
  Example:  
  curl -X DELETE http://localhost:5706/mm-shopping-cart/1

### Cart Item Management:
- **GET /mm-shopping-cart/{cartid}/items**  
  Retrieves all items in a specific shopping cart.  
  Example:  
  curl http://localhost:5706/mm-shopping-cart/1/items

- **POST /mm-shopping-cart/{cartid}/items**  
  Adds a new item to the shopping cart or updates the quantity if the item already exists.  
  Example:  
  curl -X POST http://localhost:5706/mm-shopping-cart/1/items -d '{"productitemid": 1, "quantity": 2}'

- **DELETE /mm-shopping-cart/{cartid}/items/{productitemid}**  
  Deletes a specific item from a shopping cart.  
  Example:  
  curl -X DELETE http://localhost:5706/mm-shopping-cart/1/items/1

### Cart Checkout:
- **POST /mm-shopping-cart/pay/{id}**  
  Finalizes the cart payment by verifying item stock and updating inventory.  
  Example:  
  curl -X POST http://localhost:5706/mm-shopping-cart/pay/1

---

## Pact Consumer Tests

The `mm-shopping-cart` service includes consumer-side Pact contract tests to ensure compatibility with the `mm-customer` and `mm-inventory` services.

### Pact Setup

Pact consumer tests are located in the `pact` directory and verify that the shopping cart service's interactions with other microservices (like `mm-customer` and `mm-inventory`) are correct.

### Pact Dependencies:

{
  "name": "pact",
  "version": "1.0.0",
  "scripts": {
    "test": "mocha --recursive ./tests/*.spec.js",
    "pact:publish": "node publishPact.js"
  },
  "dependencies": {
    "@pact-foundation/pact": "^13.1.3",
    "axios": "^1.7.7",
    "chai": "^5.1.1",
    "dotenv": "^16.4.5",
    "mocha": "^10.7.3"
  },
  "devDependencies": {
    "@pact-foundation/pact-cli": "^16.0.0"
  }
}

### Running Pact Tests

To run Pact consumer tests and publish the results, use the following commands:

npm test  
npm run pact:publish

This will execute the tests and publish the results to the configured Pact broker.

---

## Swagger Documentation

The `mm-shopping-cart` service comes with built-in **Swagger** documentation, allowing easy interaction with the API.

### Accessing Swagger UI

Once the service is running, the **Swagger UI** is accessible at:

http://localhost:5706/swagger/

The Swagger UI provides a user-friendly interface to explore and test the API endpoints directly from your browser.

### How to Use Swagger UI

1. Navigate to the **Swagger UI** link mentioned above.
2. Explore the various API endpoints by clicking on them.
3. Try out the endpoints by providing the required parameters and executing the requests directly from the UI.

Swagger makes it easy to document and interact with the API, ensuring that developers and users can quickly test and understand the system.

---

## Running the Flask Application Locally

If you prefer to run the service without Docker, follow the steps below.

### Step 1: Install Dependencies

Make sure you have Python 3 and `pip` installed. Then, install the required dependencies:

pip install -r requirements.txt

### Step 2: Configure Environment Variables

Create a `.env` file in the root of the project with the following content:

FLASK_APP=app.py  
FLASK_ENV=development  
DATABASE_URL=postgresql://marketmaster:password@localhost:5437/postgres

### Step 3: Run the Application

With the environment variables set, you can run the Flask application:

flask run

By default, the service will be accessible at `http://localhost:5706`.

---

## Additional Information

This microservice is part of the Market Master system, providing shopping cart management features that are essential for supermarket operations. It is closely integrated with other services in the system, such as the `mm-customer` and `mm-inventory` services.

For more details about the Market Master project and to explore other microservices, visit the respective repositories:

- [mm-inventory](https://github.com/MarketMasterPlus/mm-inventory)
- [mm-product](https://github.com/MarketMasterPlus/mm-product)
- [mm-store](https://github.com/MarketMasterPlus/mm-store)
- [mm-address](https://github.com/MarketMasterPlus/mm-address)
- [mm-customer](https://github.com/MarketMasterPlus/mm-customer)
- [mm-pact-broker](https://github.com/MarketMasterPlus/mm-pact-broker)
- [mm-ui](https://github.com/MarketMasterPlus/mm-ui)

For any further questions, feel free to open an issue on GitHub or consult the provided documentation within each repository.
