
<p align="center">
    <img src="./art/0.1_wallpaper.jpg" />
    <br />
    <br />
    <i>
    A smart python shell for data processing, automation and much more with OpenAi's API
    </i>
    <br />
    <br />
    <a href="https://github.com/HarmonicHemispheres/tacoshell">
    <img
        src="https://img.shields.io/badge/🌮 Taco-0.1.0-black?color=black&style=for-the-badge"
        alt="Tacoshell version"
    /></a>
    <img
        src="https://img.shields.io/badge/License-MIT-black?color=black&style=for-the-badge"
        alt="License"/>
    <br>
    <img
        src="https://img.shields.io/badge/Powered By OpenAi-black?color=black&style=for-the-badge&logo=OpenAi"
        alt="Credit to OpenAi"/>
    <img
        src="https://img.shields.io/badge/Powered By DUCKDB-black?color=black&style=for-the-badge&logo=DuckDB"
        alt="Credit to DuckDB"/>
</p>

<br>

# 🌮 Why Tacos for Dinner?
## 1. Because they are delicious! 🌮😄

## 2. Taco lets you view session history with OpenAi models easily
<img alt="bad taco text" src="static/show_sessions.png" width="70%">

<br>

## 3. Easily see available OpenAi models you have access to
<img alt="model list" src="static/openai_models_list.png" width="70%">

<br>

## 4. Data is stored in `DuckDB` making analysis on chat sessions easy!
<img alt="duckdb persistant sessions" src="static/duckdb_session.png" width="70%">

## 5. Export Chat Sessions for external uses and analysis 
<img alt="export options" src="static/export_options.png" width="70%">


<br>
<br>
<br>

# 🌮 Get Cookin!
### Install
```
python -m pip install 'tacoshell @ git+https://github.com/HarmonicHemispheres/tacoshell@main'
```

### Create Config
Taco stores settings and configuration in the `taco.toml` file and stores chat conversation data and a few other runtime settings in `taco.db`. Note, you can get your open-ai API key from here: https://platform.openai.com/account/api-keys
```
taco init
```

### Launch Shell
```
taco chat
```


<br>
<br>
<br>

# 🦾  Commands

```
🌮 .help

<TEXT>               --  ask openai a question

.quit                --  exit taco shell
.help                --  list builtin commands
.clear/.clr          --  clears the console
.cfg                 --  show the config settings
.session             --  show the details of the current session and its history
.sessions            --  list chat sessions
.models              --  shows available OpenAi models
.set-session <NAME>  --  switch to a different chat session
.export              --  export the current chat session to csv
.export-csv          --  export the current chat session to csv
.export-json         --  export the current chat session to json
.export-xlsx         --  export the current chat session to xlsx
.export-html         --  export the current chat session to html
```

<br>

### Start a Fresh Session
this command will drop the local `taco.db` database and start a fresh one.
```
taco chat --new
```

<br>
<br>
<br>

# 🛣️ Roadmap & Ideas
- [ ] add way to set a system message for a chat session to guide the ai model
- [x] chat session content export options (simple)
  - [x] json
  - [x] csv
  - [x] xlsx
  - [x] html
- [ ] file import system to add file content to chat context without copy paste
- [ ] add system to use sql to query the `taco.duckdb` database from the taco shell
- [ ] add "Chat Commands" that allow GPT to specify commands that will run predefined python functions to enable a auto-GPT system
  - [ ] add config setting for custom "Chat Commands"
- [ ] add way to modify temperature of models for variable control of model response behavior
- [ ] add way to remove\inactivate chat sessions
- [ ] add way to deactivate specific messages in chat session to shape session focus
- [ ] add update or chat content migration mechanism for database updates
- [ ] add application logging to `.log` files for enhanced troubleshooting and details
- [ ] add a `watch` mode, where agent tasks can perform scheduled jobs and triggers can cause a specific chat session to be prompted with some data.
- [ ] add a documentation site in sphinx
- [ ] add streamlit app to interact with Taco 
