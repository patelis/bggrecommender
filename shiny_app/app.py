from shiny import Inputs, Outputs, Session, App, reactive, render, req, ui
import shiny.experimental as x
from htmltools import css
import numpy as np
import polars as pl
import requests
from lxml import etree
from pathlib import Path
from funcs import retrieve_game_info, parse_bgg_xml

app_directory = Path(__file__).parent
data_directory = app_directory/"data"

games=pl.read_csv(data_directory/"bgg_gamelist_all_details.csv").filter(pl.col("id") != 170984)
embeddings = np.load(data_directory/"embeddings.npz")["embeddings"]
embeddings = embeddings / np.sqrt((embeddings**2).sum(1, keepdims=True))
games = games.with_columns(name_date = pl.col("name") + " (" + pl.col("year_published").cast(pl.Utf8) + ")")
names_list = games.select("name_date").to_series().to_list()
names = games.select("name_date").to_series().to_numpy()
ids = games.select("id").to_series().to_numpy()

y = x.ui.card("A simple card")#, style = "border: none;")

app_ui = x.ui.page_fillable(
    ui.row(ui.h1("Board Game Recommender", class_ = "text-center")),
    ui.row(x.ui.card(ui.markdown(
        """
        This app allows users to discover board games that are similar to other board games that 
        are similar to other games the users have played before. Simply start typing the name of 
        a game in the textbox below and select a game from the dropdown. Click search for an overview of 
        the most similar games based on the selected game's description. When using an SVM model to find 
        similar games, users are able to specify more than one game and the model tries to find the games that 
        are most similar to all selections.
        """
        ))),
    ui.row(
        #ui.column(1, ui.h5("Find game similar to:", class_ = "text-center")),
        #ui.column(6, ui.input_selectize("game_dropdown", None, choices=[], selected=[],multiple=False, width="100%")),
        ui.column(8, ui.output_ui("game_selector")),
        ui.column(2, ui.input_action_button("run_model", "Search", class_= "btn-sm btn-success", width = "100%")),
        ui.column(2, ui.input_radio_buttons("model_select", label=None, choices=["knn", "svm"], selected="knn", width="100%", inline=True))
        ), 
    ui.input_text("test_outputs", "List games...", width= "100%"),
    x.ui.output_ui("cards", fill=True, fillable=True),

)

def server(input: Inputs, output: Outputs, session: Session):
    
    @reactive.Effect
    def _():
        ui.update_selectize(
            "game_dropdown",
            choices=names_list,
            selected=[],
            server=True,
        )
        
    @reactive.Effect
    @reactive.event(input.model_select)
    def _():
        ui.update_selectize(
            "game_dropdown",
            choices=names_list,
            selected=[],
            server=True,
        )
    
    @output
    @render.ui
    @reactive.event(input.model_select)
    def game_selector():
        z = input.model_select()
        if z == "knn":
            return ui.input_selectize("game_dropdown", None, choices=[], selected=[],multiple=False, width="100%")
        else:
            return ui.input_selectize("game_dropdown", None, choices=[], selected=[],multiple=True, width="100%")
        
    @reactive.Calc
    def model():
        
        #req(input.game_dropdown)
        #req(input.run_model)
        type = input.model_select()
        name = input.game_dropdown()
        
        query = embeddings[names == name].squeeze()
        
        if type == "knn":
            
            similarities = embeddings.dot(query)
            sorted_ix = np.argsort(-similarities)
            #sorted_ix = sorted_ix[:5]
            #sorted_names = names[sorted_ix][1:]
            
            #names_string = ", ".join(sorted_names[:5].tolist())
            
            #return names_string
            
            sorted_ids = ids[sorted_ix][1:]
            
            return sorted_ids[:5].tolist()
            
        
        else:
            
            from sklearn import svm
            x = embeddings
            y = np.zeros(x.shape[0])
            for i in name:
                y[names == i] = 1
            
            clf = svm.LinearSVC(class_weight='balanced', verbose=False, max_iter=10000, tol=1e-6, C=0.1)
            clf.fit(x, y)
            
            similarities = clf.decision_function(x)
            sorted_ix = np.argsort(-similarities)
            #sorted_names = names[sorted_ix][len(name):]
            
            #names_string = ", ".join(sorted_names[:5].tolist())
            
            #return names_string
            
            sorted_ids = ids[sorted_ix][len(name):]
            
            return sorted_ids[:5].tolist()
            
    
    @reactive.Effect
    @reactive.event(input.run_model)
    def _():
        
        #req(input.game_dropdown)
        #req(input.run_model)
        
        id_list = model()
        ids = ", ".join([str(id) for id in id_list])
        
        ui.update_text(
            "test_outputs",
            value = "Ids: " + ids
        )
    
    @output
    @render.ui
    @reactive.event(input.run_model)
    def cards():
        ids_to_search=model()
        card_list = []
        
        xml_data, xml_text = retrieve_game_info(ids_to_search)
        game_info = parse_bgg_xml(xml_data)
        
        for game in game_info:
            
            y = x.ui.card(
                x.ui.card_header(game['game_name']),
                x.ui.card_image(file=None, src=game['image']), 
                x.ui.card_body(game["description"])            
            )
        
            card_list.append(y)
            
        return x.ui.layout_column_wrap(1/5, *card_list),
        #return x.ui.layout_column_wrap(1/5, y,y,y,y,y),

app = App(app_ui, server)
