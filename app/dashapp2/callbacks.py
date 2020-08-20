

from dash.dependencies import Output, Input, State



def register_callbacks(dashapp):
    
    '''------------------------------------------------------------------------------------------- 
                                            INTERACTIVITÉ
   ------------------------------------------------------------------------------------------- 
    '''
# Présentation du bouton étude detailée
    @dashapp.callback(
        Output("collapse_0", "is_open"),
        [Input("collapse_button_0", "n_clicks")],
        [State("collapse_0", "is_open")],
    )
    def toggle_collapse_0(n, is_open):
        if n:
            return not is_open
        return is_open

    # 1. Analyse des produits,bouton analyse detailée
    @dashapp.callback(
        Output("collapse_1", "is_open"),
        [Input("collapse_button_1", "n_clicks")],
        [State("collapse_1", "is_open")],
    )
    def toggle_collapse_1(n, is_open):
        if n:
            return not is_open
        return is_open

    # 2. Analyse des lieux de ventes,bouton analyse detailée
    @dashapp.callback(
        Output("collapse_2", "is_open"),
        [Input("collapse_button_2", "n_clicks")],
        [State("collapse_2", "is_open")],
    )
    def toggle_collapse_2(n, is_open):
        if n:
            return not is_open
        return is_open

    # 3. Analyse temporelle, bouton analyse detailée 
    @dashapp.callback(
        Output("collapse_3", "is_open"),
        [Input("collapse_button_3", "n_clicks")],
        [State("collapse_3", "is_open")],
    )
    def toggle_collapse_2(n, is_open):
        if n:
            return not is_open
        return is_open
