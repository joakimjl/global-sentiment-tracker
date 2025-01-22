# GlobalSentimentTracker WIP
Global national and international news sentiment analysis and visualization using ETL pipelines, sentiment models, and interactive 3D visualizations.

# Hosted at: https://globalsentiment.xyz

# Overview
ETL is performed by fetching data from GDELT every 4 hours, matching websites to website popularity metrics in nations, and inserting popular website articles for relevance.
Sentiment analysis runs with VADER (NLTK) and roBERTa (https://huggingface.co/cardiffnlp/twitter-roberta-base-sentiment-latest), and a fine-tuned model (TBD) that is improved and verified for the specific dataset.
This is all (WIP) displayed on a 3D interactive website where you can query certain subjects for different countries or globally.

# Dataset
Partitioned databases for each day, the dataset consists of 270k headlines all translated from their original languages, each with sentiment labels, more processing TBD.

Note: this repo is a little messy due to some initial rushing of the project.
