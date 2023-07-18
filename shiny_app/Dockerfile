FROM python:3.9-slim

WORKDIR /app

# Install requirements
COPY requirements.txt requirements.txt
RUN pip3 install --no-cache-dir --upgrade -r requirements.txt

# Copy the app
COPY data data
COPY app.py app.py
COPY funcs.py funcs.py

# Run app on port 8080
EXPOSE 8080

CMD ["shiny", "run", "app.py", "--host", "0.0.0.0", "--port", "8080"]

#docker build --tag shiny_app .
#docker run -d -p 0.0.0.0:8080:8080 shiny_app