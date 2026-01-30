# Hybrid Movie Recommendation System

## Overview
This project implements a **hybrid movie recommendation system** that combines **Content-Based Filtering** and **Collaborative Filtering**.  
Users can explore movie recommendations based on their favorite movies or user ratings.  
The system is interactive and built with **Streamlit** for real-time recommendations.

## Installation / Requirements
To run the project locally, install the required libraries:

```bash
pip install -r requirements.txt
Make sure you have Python 3.8+ installed.

## Usage

To launch the Streamlit app: streamlit run app.py
Follow the instructions on the web interface to get movie recommendations.


## Features

Hybrid recommendations (Content-Based + Collaborative Filtering)
Interactive movie search
Movie details display (title, genres, cast, overview)
Works with pre-trained models (svd.pkl, sim.pkl)

## Notes

The dataset is not included due to large size.
Set your OMDB_API_KEY in Streamlit Secrets to access movie details.
