#!/bin/sh

if python3 main.py $1 $2;
	then echo "success"
else
	python main.py $1 $2
fi

if python3 app.py;
	then pass
else
	python app.py
fi