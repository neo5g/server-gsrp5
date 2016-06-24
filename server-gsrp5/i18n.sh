#!/usr/bin/bash

pybabel extract -F babel.cfg -o message.pot .
pybabel update -d i18n -l ru_RU -i message.pot

