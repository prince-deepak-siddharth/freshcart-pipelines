# freshcart-pipelines

Assignment "From Git to Gold": Git + CI, FreshCart ELT on Snowflake, a Mage ML pipeline and a RabbitMQ order stream.

```
freshcart-pipelines/
├── elt/                FreshCart ELT notebook (Part B + bonus)
├── iris_project/       Mage project: load_iris -> validate_iris -> prepare_data -> train_model -> save_results / evaluate_model (Part C)
├── stream/             dispatcher.py, driver.py (+ bonus consumer) (Part D)
├── tests/              pytest tests, run by CI (Part A3)
├── report/             report sources + generated PDF
└── .github/workflows/ci.yml
```

## Run the tests
```
pip install -r requirements.txt
pytest
```

## Run the ML pipeline
```
pip install -r requirements-mage.txt
mage run iris_project iris_classifier --test
mage run iris_project iris_classifier --runtime-vars '{"max_depth": 3}'
# without Mage installed:
python iris_project/run_local.py --max-depth 3
```

## Run the stream (needs RabbitMQ on localhost, or set RABBITMQ_URL)
```
docker run -d --name rabbit -p 5672:5672 -p 15672:15672 rabbitmq:3-management
python stream/driver.py Ravi  "bangalore.koramangala.*"
python stream/driver.py Arjun "bangalore.*.ride"
python stream/driver.py Control "bangalore.#"
python stream/dispatcher.py
```
Secrets (Snowflake password, CloudAMQP URL) are never committed: they are read from `getpass` / environment variables.
