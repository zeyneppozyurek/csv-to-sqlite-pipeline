[README.md](https://github.com/user-attachments/files/33268274/README.md)
# CSV to SQLite Data Pipeline

Transform raw session records into validated data and load them into a queryable SQLite database.

## Tools

Python, pandas, SQLite

## Workflow

1. Read a sample CSV and remove exact duplicate rows.
2. Validate timestamps, identifiers, scenarios and numerical values.
3. Export rejected records with reasons.
4. Load valid records into SQLite and summarize them with SQL.
5. Verify that loading the same records twice does not create duplicates.

## Data and method

Uses fictional session records. Existing database records are retained when their identifiers are loaded again.

## Run locally

```bash
python -m pip install -r requirements.txt
python main.py
```

For the package versions used to verify the project, install `requirements-tested.txt` instead.

## Run in Google Colab

Upload `project.ipynb` to Google Colab and select **Run all**.

## Files

- `main.py`: executable Python script.
- `project.ipynb`: notebook with the same workflow and example outputs.
- `requirements.txt`: required Python packages.
- `requirements-tested.txt`: package versions used for verification.
- `outputs/`: generated data, reports and results.

## About

This is a learning project prepared with AI assistance.
