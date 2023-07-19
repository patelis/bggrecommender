## BGG Recommender App

This is a repository for a project to create a recommender for board games using data from the Board Game Geeks website.
By providing one (or more based on the selected model) board game as reference, the recommender provides a selection of similar games.  

The recommender uses embeddings from the description of all ranked board games from the website to create suggestions which are ordered using either a k-NN or a SVM model.
The embeddings are created using the [instructor-xl](https://huggingface.co/hkunlp/instructor-xl), but alternatives such as OpenAI's [text-embedding-ada-002](https://platform.openai.com/docs/guides/embeddings/what-are-embeddings) can also be used. See [this notebook](https://github.com/patelis/bggrecommender/blob/main/notebooks/calc_token_req.ipynb) for a cost estimation of that approach.  

The application is built using [Shiny for Python](https://shiny.posit.co/py/).  

The [`bgg_scraper.ipynb`](https://github.com/patelis/bggrecommender/blob/main/notebooks/bgg_scraper.ipynb) notebook can be used to extract the game information.
To get the list of all ranked games an account with Board Game Geeks is required, otherwise you cannot view more than the 20 first pages of ranking.
Chromedriver is required to get that list using Selenium. You can look up instructions on downloading and linking online, but in general you just need to download the version that matches your system's Chrome installation. 
Credentials are saved as variables in the virtual environment.
The rest of the information required is accessed through the BBG v2 API, using the game ids scraped from the ranking page. 
The game ids used in the application are of all games that are ranked as of 12th July 2023.

The data for the Shiny app are saved in a shiny_app/data folder, which is not part of the repository.
The data from the API calls as well as all cleaned versions are saved in a data folder in the main project folder, which is not part of the repository.
To get the data one has to run the `bgg_scraper.ipynb` and `cleaning_and_tokenization.ipynb` notebooks.

A Dockerfile is also included to allow one to build a container in which to place and run the app.
If Docker is installed (and it works), one can navigate to the shiny_app folder in the terminal and run the commands commented out at the bottom of the Dockerfile.