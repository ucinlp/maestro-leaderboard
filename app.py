from tokenize import String
from typing import Dict
import flask
from flask import request, jsonify
from flask import Flask, render_template
import json
from os import path
import yaml
import pandas as pd

server_config_file = "config.json"
with open(server_config_file, "r") as f:
    server_config = json.load(f)
IP_ADDR = server_config["ip"]
PORT = server_config["port"]

app = flask.Flask(__name__)
# app.config["DEBUG"] = True

class Leaderboard:
    """A single leaderboard page"""

    @staticmethod
    def config_file(id): return f"{server_config['data_path']}/{id}-config.yml"

    @staticmethod
    def data_file(id): return f"{server_config['data_path']}/{id}.csv"

    @classmethod
    def check(cls, id):
        """Checks whether the leaderboard exists"""
        return path.exists(cls.config_file(id)) and path.exists(cls.data_file(id)) 

    def __init__(self, id):
        self.id = id
        self.title = None
        self.results: Dict[String,pd.DataFrame] = None
        self.table_name_column = None
        self.sort_cols = []
        self.table_names = {}
        self.default_sort_col = None
    
    def load_config(self):
        with open(self.config_file(self.id), "r") as f:
            config = yaml.safe_load(f)
            self.title = config['title']
            self.sort_cols = []
            self.cols_config = {}
            try:
                self.default_sort_col = config['default_sort_col']
            except:
                self.default_sort_col = None
            for i, col in enumerate(config['sort_cols']):
                if isinstance(col, str):
                    self.sort_cols.append(col)
                    self.cols_config[col] = {}
                else:
                    key = list(col.keys())[0]
                    self.sort_cols.append(key)
                    self.cols_config[key] = config['sort_cols'][i][key]
            print(self.cols_config)
            print(f'Sort cols: {self.sort_cols}')
            if "table_name_column" in config:
                self.table_name_column = config['table_name_column']
                self.table_names = config['table_names']

    def load_data(self):
        self.results = {}
        try:
            table = pd.read_csv(Leaderboard.data_file(self.id)).round(2)
        except:
            table = pd.DataFrame()
        print(self.sort_cols)
        self.tables = {}
        if not table.empty and self.table_name_column is None:
            table = table[self.sort_cols]
            self.tables[""] = table
        elif not table.empty:
            table = table[self.sort_cols + [self.table_name_column]]
            for value_id, table_name in self.table_names.items():
                subtable = table[table[self.table_name_column] == value_id]
                subtable = subtable.drop(columns=[self.table_name_column])
                self.tables[table_name] = subtable
        print(table.head())
    def get_render_data(self, sortby=None, student_name=None):
        render_data = {}
        render_data['title'] = self.title
        render_data['tables'] = {}
        render_data['sort_col'] = sortby if sortby else self.sort_cols[0]
        render_data['sort_cols'] = self.sort_cols
        for table_id, table in self.tables.items():
            if student_name is not None:
                table = table.loc[(table['Name'].str.lower()).str.contains(student_name.lower())]
            else:
                table = table.groupby('Name', as_index=False).apply(lambda x: x.sort_values(render_data['sort_col']).iloc[-1])
            render_data['tables'][table_id] = table.sort_values(
                by=render_data['sort_col'], 
                ascending=self.cols_config[render_data['sort_col']]['sort'] != 'ascending'
            )
        print(render_data)
        return render_data

def main():
    @app.route("/", methods=["GET"])
    def home():
        return render_template("home.html", message=None)

    @app.route("/leaderboard/<leaderboard_id>", methods=['GET', 'POST'])
    def leaderboard(leaderboard_id, student_name=None):
        sortby = request.args.get("sortby")
        if flask.request.method == 'POST':
            student_name = flask.request.values.get('student_name')
            student_name = None if student_name == '' else student_name
            return flask.redirect(
                flask.url_for('leaderboard', 
                    leaderboard_id=request.view_args['leaderboard_id'],
                    sortby=sortby,
                    student_name=student_name
                )
            )
        else:
            student_name = request.args.get("student_name")
            if Leaderboard.check(leaderboard_id):
                leaderboard = Leaderboard(leaderboard_id)
                leaderboard.load_config()
                leaderboard.load_data()
                if sortby is None: sortby = leaderboard.default_sort_col
                data = leaderboard.get_render_data(
                    sortby=sortby,
                    student_name=student_name
                )
                return render_template(
                    "index.html",
                    data=data,
                    cols=leaderboard.cols_config,
                    server=server_config
                )
            else:
                return f"<h1>Cannot find leaderboard with id {leaderboard_id}</p>"

    @app.errorhandler(Exception)
    def exception_handler(error):
        print(error)
        print(repr(error))
        return render_template("home.html", message=error)
        #return "If the error persists, please contact the Maestro Administrators on Ed Discussions. Thank you."

    # ------------------ END ATTACK SERVER FUNCTIONS ---------------------------

    print("Server Running...........")
    # app.run(debug=True)
    # app.run(host="0.0.0.0", port=4999)
    app.run(host=IP_ADDR, port=PORT)


if __name__ == "__main__":
    main()
