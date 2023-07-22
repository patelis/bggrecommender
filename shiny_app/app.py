from shiny import Inputs, Outputs, Session, App, reactive, render, req, ui
import shiny.experimental as x
import numpy as np
import polars as pl
from pathlib import Path
from html import unescape
import shinyswatch
from sklearn import svm
from funcs import retrieve_game_info, parse_bgg_xml, fetch_similar_implementations

app_directory = Path(__file__).parent
data_directory = app_directory/"data"

games=pl.read_csv(data_directory/"bgg_gamelist.csv")
embeddings = np.load(data_directory/"embeddings.npz")["embeddings"]
games = games.with_columns(name_date = pl.col("name") + " (" + pl.col("year_published").cast(pl.Utf8) + ")")
names_list = games.select("name_date").to_series().to_list()
names = games.select("name_date").to_series().to_numpy()
ids = games.select("id").to_series().to_numpy()

app_ui = x.ui.page_fillable(
    shinyswatch.theme.quartz(),
    ui.tags.style(
        """
        .selectize-input, 
        .selectize-control.single .selectize-input.input-active {
            background: rgba(255,255,255,0.2);
            cursor: text;
            display: inline-block;
        }
        .selectize-input.full {
            background-color: rgba(255,255,255,0.2);
        }
        .selectize-dropdown .active {
            background-color: rgba(255,255,255,0.2);
        }
        .selectize-dropdown,
        .selectize-input,
        .selectize-input input {
            color: #e9e9e8;
        }
        """
    ),
    ui.row(ui.h1("Board Game Recommender", class_ = "text-center")),
    ui.row(x.ui.card(ui.markdown(
        """
        This app allows users to discover board games that are similar to other board games that 
        the users have played before. Simply start typing the name of 
        a game in the textbox below and select a game from the dropdown. Click search for an overview of 
        the most similar games based on the selected game's description. When using an __SVM__ model to find 
        similar games, users are able to specify more than one game and the model tries to find the games that 
        are most similar to all selections.
        """
        ))),
    ui.row(ui.input_checkbox("remove_implementations", "Remove similar implementations: ", False)),
    ui.row(
        ui.column(8, ui.output_ui("game_selector")),
        ui.column(2, ui.input_action_button("run_model", "Search", class_= "btn-sm btn-light", width = "100%")),
        ui.column(1, ui.input_radio_buttons("model_select", label=None, choices={"knn":"k-NN", "svm":"SVM"}, selected="knn", width="100%", inline=True)), 
        ui.column(1, 
                  ui.div({"class":"btn-group", "role":"group"}, 
                         ui.input_action_button("go_left", "Previous", class_= "btn-sm btn-light"), 
                         ui.input_action_button("go_right", "Next", class_= "btn-sm btn-light")
                         )
                  )
        ), 
    x.ui.output_ui("cards", fill=True, fillable=True),

)

def server(input: Inputs, output: Outputs, session: Session):
    
    index = reactive.Value([0])
    
    @reactive.Effect
    @reactive.event(input.run_model)
    @reactive.event(input.game_dropdown)
    def _():
        index.set([0])

    @reactive.Effect
    @reactive.event(input.go_right)
    def _():
        i = index().copy()[0]
        index.set([i + 5])
        
    @reactive.Effect
    @reactive.event(input.go_left)
    def _():
        if (index()[0] < 5):
            index.set([0])
        else:
            i = index().copy()[0]
            index.set([i - 5])
    
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
            select_menu = ui.input_selectize("game_dropdown", None, choices=[], selected=[],multiple=False, width="100%")
        else:
            select_menu = ui.input_selectize("game_dropdown", None, choices=[], selected=[],multiple=True, width="100%")
            
        select_menu = ui.div({"class":"text-light"}, select_menu)
        
        return select_menu
      
                
    @reactive.Calc
    def model():
        
        req(input.game_dropdown())
        type = input.model_select()
        name = input.game_dropdown()
        
        query = embeddings[names == name].squeeze()
        
        if type == "knn":
            
            similarities = embeddings.dot(query)
            sorted_ix = np.argsort(-similarities)
            
            sorted_ids = ids[sorted_ix]
            
            return sorted_ids.tolist()
            
        else:
            
            x = embeddings
            y = np.zeros(x.shape[0])
            for i in name:
                y[names == i] = 1
            
            clf = svm.LinearSVC(class_weight='balanced', verbose=False, max_iter=10000, tol=1e-6, C=0.1)
            clf.fit(x, y)
            
            similarities = clf.decision_function(x)
            sorted_ix = np.argsort(-similarities)
            
            sorted_ids = ids[sorted_ix]
            
            return sorted_ids.tolist()
    
    @reactive.Calc
    def similar_implementation_ids():
        
        req(input.game_dropdown())
        
        type = input.model_select()
        name = input.game_dropdown()
        
        if (type == "knn"):
            
            searched_ids = ids[names == name]
            
        else:
            searched_ids = []
            for i in name:
                searched_ids.append(ids[names == i][0])
                
        if (input.remove_implementations() == True):
            
            xml_implementations = retrieve_game_info(searched_ids)
            similar_games_ids = fetch_similar_implementations(xml_implementations)
            
            similar_games_ids = [int(x) for x in similar_games_ids]
            
            for game_id in searched_ids:
                similar_games_ids.append(game_id)
                
        else:
            similar_games_ids = searched_ids
        
        return set(similar_games_ids)
        
        
    
    @output
    @render.ui
    @reactive.event(index)
    @reactive.event(input.remove_implementations)
    @reactive.event(input.run_model)
    
    def cards():
        ids_all=model()
        ids_similar_implementation = similar_implementation_ids()
        card_list = []
        
        ids_subset = [x for x in ids_all if x not in ids_similar_implementation]
        
        i = index().copy()[0]
              
        ids_to_search = ids_subset[i:(i+5)]
        
        xml_data = retrieve_game_info(ids_to_search)
        game_info = parse_bgg_xml(xml_data)
        
        for game in game_info:
            
            game_name = f"{game['name']} ({game['year_published']})"
            avg_rating = round(float(game['avg_rating']), 2)
            bgg_rating = round(float(game['bgg_rating']), 2)
            
            if (game['min_players'] == game['max_players']):
                players = game['min_players']
            else:
                players = f"{game['min_players']}-{game['max_players']}"
                
            if (game['min_playtime'] == game['max_playtime']):
                playtime = f"{game['min_playtime']}"
            else:
                playtime = f"{game['min_playtime']}-{game['max_playtime']}"
            
            game_description = unescape(game['description'])
            
            link_to_game = ui.tags.a({"href":f"https://boardgamegeek.com/boardgame/{game['id']}/", "target":"_blank"}, f"Link to {game['name']} on BGG")
            
            game_categories = f"Category: {game['categories']}"
            game_mechanics = f"Mechanics: {game['mechanics']}"
            
            y = x.ui.layout_sidebar(
                    x.ui.sidebar(
                        game_description, 
                        open="closed", 
                    ),
                    x.ui.card(
                        x.ui.card_header(game_name),
                        x.ui.card_image(file=None, src=game['image'], border_radius="all"), 
                        x.ui.card_body(
                            ui.tags.ul({"class":"list-group list-group-flush"}, 
                                ui.tags.li({"class":"list-group-item bg-secondary"}, 
                                            ui.row(
                                                   ui.column(9, "Average Rating:"), 
                                                   ui.column(3, ui.tags.span({"class":"badge bg-info"}, f"{avg_rating}"))
                                                   )
                                          ), 
                                ui.tags.li({"class":"list-group-item bg-secondary"}, 
                                            ui.row(
                                                   ui.column(9, "BGG Rating:"), 
                                                   ui.column(3, ui.tags.span({"class":"badge bg-info"}, f"{bgg_rating}"))
                                                  )
                                          ), 
                                ui.tags.li({"class":"list-group-item bg-secondary"}, 
                                            ui.row(
                                                   ui.column(9, "Players:"), 
                                                   ui.column(3, ui.tags.span({"class":"badge bg-info"}, players))
                                                  )
                                          ),
                                ui.tags.li({"class":"list-group-item bg-secondary"}, 
                                            ui.row(
                                                   ui.column(9, "Playtime (minutes):"), 
                                                   ui.column(3, ui.tags.span({"class":"badge bg-info"}, playtime))
                                                  )
                                          ),
                                ui.tags.li({"class":"list-group-item bg-secondary"}, game_categories), 
                                ui.tags.li({"class":"list-group-item bg-secondary"}, game_mechanics),
                                ), 
                            ), 
                        x.ui.card_footer({"class":"bg-primary"}, link_to_game)
                        ), 
                    padding = 0
                    )
        
            card_list.append(y)
            
        return x.ui.layout_column_wrap(1/5, *card_list),

app = App(app_ui, server)
