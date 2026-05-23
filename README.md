# Item Processor

## Prerequisites

Make sure the following are installed on your system:
- Python 3.10+
- RabbitMQ 4.3.1 (running on localhost:5672)
- Erlang OTP 27.3.4.6

> This project was developed and tested on RabbitMQ 4.3.1 with Erlang OTP 27.3.4.6

---

## Installation Steps

### 1. Clone the repository
```bash
git clone <repo-url>
cd item_processor
```

### 2. Create a virtual environment
```bash
python -m venv venv
```

### 3. Activate the virtual environment

Windows:
```bash
venv\Scripts\activate
```

Mac/Linux:
```bash
source venv/bin/activate
```

### 4. Install dependencies
```bash
pip install -r requirements.txt
```

---

## How to Run

You will need **two terminals** running simultaneously.

### Terminal 1 — Start Flask Server
```bash
python run.py
```

Flask will start on `http://127.0.0.1:5000`

### Terminal 2 — Start Celery Worker
```bash
celery -A app.worker.celery_app worker --loglevel=info -Q item_processing_queue --without-mingle --without-gossip
```

---

## API Endpoints

### 1. POST /items
Accepts an item, inserts it into the database with status `pending`, and sends it to RabbitMQ for processing.

- **Method:** POST
- **URL:** `http://127.0.0.1:5000/items`
- **Content-Type:** application/json
- **Body:**
```json
{"item": "book"}
```
- **Response:** 202 Accepted
```json
{"id": 1, "message": "Item accepted"}
```

### 2. GET /process
Triggers 5 concurrent requests to an external URL using threading and returns the time taken.

- **Method:** GET
- **URL:** `http://127.0.0.1:5000/process?delay_value=2`
- **Response:** 200 OK
```json
{"time_taken": 2.35}
```

---

## Note for RabbitMQ 4.x Users

RabbitMQ 4.x has deprecated classic queues. This project uses **quorum queues** to handle that.

### Step 1 — Create advanced.config file

Create a file named `advanced.config` at `%APPDATA%\RabbitMQ\` (Windows) with the following content:

```erlang
[{rabbit, [
    {permit_deprecated_features, #{
      transient_nonexcl_queues => true
    }}
]}].
```

This allows Celery's internal control queue to work with RabbitMQ 4.x.

### Step 2 — Restart RabbitMQ

```bash
net stop RabbitMQ
net start RabbitMQ
```

### Step 3 — If you face this error:
```
PRECONDITION_FAILED - inequivalent arg 'x-queue-type'
```

Make sure `queue_arguments={'x-queue-type': 'quorum'}` is present in `worker.py` and `arguments={'x-queue-type': 'quorum'}` is present in `producer.py`.

If you are on RabbitMQ 3.x, quorum queues will still work — no changes needed.
