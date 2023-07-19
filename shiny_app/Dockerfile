FROM python:3.10-slim

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

#Commands to run container
#docker build --tag bggrecommender .
#docker run -d --name bggrecommender_container -p 0.0.0.0:8080:8080 bggrecommender

#To deploy to shinyapps.io
#<NAME> is the name of the account
#rsconnect deploy shiny /home/kpatelis/projects/bggrecommender/shiny_app/ --name <NAME>  --title BoardGameRecommender