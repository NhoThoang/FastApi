# from flask import Flask
# import asyncio
# import time
# from insert_db_async import bulk_insert_users

# app = Flask(__name__)

# @app.route("/insert")
# async def insert():
#     start = time.time()
#     await bulk_insert_users(1000)
#     return {"message": "Inserted 1000 users!", "time": time.time() - start}

# if __name__ == "__main__":
#     app.run(debug=True)

# block new request 
from flask import Flask
import asyncio
import time
from insert_db_async import bulk_insert_users

app = Flask(__name__)

@app.route("/insert")
def insert():
    start = time.time()
    asyncio.run(bulk_insert_users(1000))  # Chạy async function trong event loop mới
    return {"message": "Inserted 1000 users!", "time": time.time() - start}

if __name__ == "__main__":
    app.run(debug=True)


# ok not block new request 
# from flask import Flask
# import asyncio
# import time
# from insert_db_async import bulk_insert_users

# app = Flask(__name__)

# @app.route("/insert")
# def insert():
#     start = time.time()
#     loop = asyncio.new_event_loop()
#     asyncio.set_event_loop(loop)
#     loop.run_in_executor(None, asyncio.run, bulk_insert_users(1000))  # Chạy background
#     return {"message": "Task started!", "time": time.time() - start}

# if __name__ == "__main__":
#     app.run(debug=True)
