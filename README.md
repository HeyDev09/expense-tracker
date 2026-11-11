\# Personal Expense Tracker



A full-stack web app to record, categorise and analyse daily expenses.



\- \*\*Backend:\*\* FastAPI REST API with CRUD endpoints and Pydantic validation

\- \*\*Database:\*\* SQLite, with SQL GROUP BY queries for monthly and category-wise summaries

\- \*\*Frontend:\*\* Streamlit dashboard with charts



!\[Dashboard](shot.png)



\## API endpoints

| Method | Endpoint | Description |

|---|---|---|

| POST | /expenses | Add an expense |

| GET | /expenses | List expenses (optional ?category=) |

| GET | /expenses/{id} | Get one expense |

| PUT | /expenses/{id} | Update an expense |

| DELETE | /expenses/{id} | Delete an expense |

| GET | /summary/category | Total spent per category |

| GET | /summary/monthly | Total spent per month |



\## How to run

```

pip install -r requirements.txt

python -m uvicorn backend:app --reload

python -m streamlit run frontend.py

```

API docs: http://127.0.0.1:8000/docs

