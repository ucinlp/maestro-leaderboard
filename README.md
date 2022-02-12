# maestro-leaderboard
Server for rendering the results for the Maestro course.

## Server Configuration

Stored in `config.json`, and specifies server address, and details common to all leaderboards:
```json
{
    "ip": "0.0.0.0",
    "port": "443",
    "subtitle": "Leaderboard for the CS175 AI Project Course",
    "data_path": "./data/" # stores the leaderboards data
}
```

## Leaderboard

Each leaderboard is specified using an `ID`, such as `attack-homework`. This `ID` becomes the URL of the leaderboard, i.e. `/leaderboard/<ID>`, such as `/leaderboard/attack-homework`.

Each leaderboard is specified using two files (in `data_path`):

- **Configuration** (`<ID>-config.yml`): A YAML file that specifies information about the leaderboard, such as:
  ```yaml
  title: Attack Project # Name of Leaderboard
  sort_cols: # Column names to show as candidates for sorting (first one is used as default)
    - Targeted
    - Untargeted
  table_name_column: Type # (optional) Column to use to split into multiple tables
  table_names: # (needed if splitting) Mapping of column values to readable names of the tables
    black: "Black-box Attacks"
    white: "White-box Attacks"
  ``` 
- **Data** (`<ID>.csv`): A CSV file (with headers) that store the data to be displayed. Should contain at least `sort_cols` and `table_name_column` (if splitting into multiple files). Example data:
  ```csv
  Name,Targeted,Untargeted,Type
  Zhou,10.0,100.0,white
  Sergio,100.0,10.0,white
  Sameer,5.0,5.0,black
  Mani,95.0,95.0,black
  ```
## Run the Server

To install the requirements:
```bash
pip install -r requirements.txt
```

To run the server:
```bash
python app.py
```