#!/bin/bash


mkdir -p "data"
mkdir -p "data/raw_novels"
mkdir -p "data/final_novels"

if [ $? -eq 0 ]; then
    echo "Folder created successfully."
    
    FILE="data/scraped.json"
    touch $FILE
    if [ ! -s $FILE ]; then
        echo "File $FILE created"
        echo "{}" > $FILE 
    else
        echo "Error: Could not create $FILE. File has been created already."
    fi
    
    FILE="data/translated.json" 
    touch $FILE
    if [ ! -s $FILE ]; then
        echo "File $FILE created"
        echo "{}" > $FILE 
    else
        echo "Error: Could not create $FILE. File has been created already."
    fi    
    
    FILE="data/uploaded.json" 
    touch $FILE
    if [ ! -s $FILE ]; then
        echo "File $FILE created"
        echo "{}" > $FILE 
    else
        echo "Error: Could not create $FILE. File has been created already."
    fi    

    FILE="data/prompts.json" 
    touch $FILE
    if [ ! -s $FILE ]; then
        echo "File $FILE created"
        echo "{}" > $FILE 
    else
        echo "Error: Could not create $FILE. File has been created already."
    fi    
    
else
    echo "Error: Could not create folder'."
fi