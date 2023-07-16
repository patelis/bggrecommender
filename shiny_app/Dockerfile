FROM python:3.9-slim

# Add user an change working directory and user
#RUN addgroup --system app && adduser --system --ingroup app app
WORKDIR /app
#RUN chown app:app -R /home/app
#USER app

# Install requirements
COPY requirements.txt requirements.txt
RUN pip3 install -r requirements.txt

# Copy the app
COPY . .

# Run app on port 8080
EXPOSE 7860

CMD ["shiny", "run", "app.py", "--host", "0.0.0.0", "--port", "7860"]

# sudo docker build --tag shiny_app .