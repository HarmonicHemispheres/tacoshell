
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
<img alt="bad taco text" src="static/show_sessions.png" width="80%">

<br>

## 3. Easily see available OpenAi models you have access to
<img alt="model list" src="static/openai_models_list.png" width="80%">

<br>

## 4. Data is stored in `DuckDB` making analysis on chat sessions easy!
<img alt="duckdb persistant sessions" src="static/duckdb_session.png" width="80%">



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

# 🌮  Commands

```
🌮 .help

<TEXT>               --  ask openai a question

.quit                --  exit taco shell
.help                --  list builtin commands
.clear               --  clears the console
.clr                 --  clears the console
.cfg                 --  show the config settings
.session             --  show the details of the current session and its history
.sessions            --  list chat sessions
.ai-models           --  shows available OpenAi models
.set-session=<NAME>  --  switch to a different chat session
.set-s=<NAME>        --  switch to a different chat session
```

<br>

### Start a Fresh Session
this command will drop the local `taco.db` database and start a fresh one.
```
taco chat --new
```