# How to run

### OS constraints:
- Ubuntu 16
- Python 3.6.0 
- chromedriver

## Create a directory
This directory will be the virtualenv for this project
You could name it `webscrapper_env`

## cd to the directory
`cd webscrapper_env`

## create the virtualenv
`virtualenv .`

## clone this repository
`git clone https://github.com/mikael19/py_web_scrapper.git`

## cd to the cloned repo
`cd py_web_scrapper`

## Install the scrapper app
`pip install -e .`

## Install the app's requirements
`pip install -r requirements.txt`

## activate the virtualenv 
`source ../bin/activate`

## Scrappe the website
`webscraper_cli --url a`
The excel sheet will be in the current directory, open it to see your results !


