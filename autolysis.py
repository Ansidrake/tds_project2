# /// script
# requires-python = ">=3.11"
# dependencies = [
#     "matplotlib",
#     "numpy",
#     "pandas",
#     "seaborn",
#     "scipy",
#     "requests",
# ]
# ///

import os
import sys
import json
import re
import numpy as np
import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt
from scipy import stats
from typing import Dict, List, Any
import requests
from functools import wraps
import time

def retry_with_backoff(max_retries=3, base_delay=1):
    """
    Decorator for retrying a function with exponential backoff.
    Helps handle transient API or network errors.
    """
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            retries = 0
            while retries < max_retries:
                try:
                    return func(*args, **kwargs)
                except (requests.RequestException, json.JSONDecodeError) as e:
                    retries += 1
                    if retries == max_retries:
                        raise
                    wait_time = base_delay * (2 ** retries)
                    print(f"Retry {retries}: {str(e)}. Waiting {wait_time} seconds.")
                    time.sleep(wait_time)
        return wrapper
    return decorator

class GoodreadsAnalysis:
    def __init__(self, file_path: str):
        """
        Initialize the analysis with the given dataset.
        
        :param file_path: Path to the Goodreads CSV file
        """
        self.file_path = file_path
        self.df = self._load_dataset()
        self.output_dir = os.path.basename(file_path).split('.')[0]
        os.makedirs(self.output_dir, exist_ok=True)
        
    def _load_dataset(self) -> pd.DataFrame:
        """
        Load the dataset with robust encoding handling.
        
        :return: Pandas DataFrame
        """
        encodings = ['utf-8', 'ISO-8859-1', 'Windows-1252']
        for encoding in encodings:
            try:
                df = pd.read_csv(self.file_path, encoding=encoding)
                
                # Data cleaning steps
                df = df.dropna(subset=['title', 'ratings_count'])  # Drop rows with missing critical data
                df['ratings_count'] = pd.to_numeric(df['ratings_count'], errors='coerce')
                df['average_rating'] = pd.to_numeric(df['average_rating'], errors='coerce')
                
                return df.dropna(subset=['ratings_count', 'average_rating'])
            except (UnicodeDecodeError, KeyError):
                continue
        raise ValueError("Unable to load dataset with any encoding")

    def _analyze_dataset(self) -> Dict[str, Any]:
        """
        Perform comprehensive dataset analysis.
        
        :return: Dictionary with analysis insights
        """
        analysis = {
            'total_books': len(self.df),
            'genres': self.df['genres'].nunique(),
            'rating_stats': {
                'mean_rating': self.df['average_rating'].mean(),
                'median_rating': self.df['average_rating'].median(),
                'rating_std': self.df['average_rating'].std()
            },
            'top_genres': self.df['genres'].value_counts().head(5).to_dict(),
            'ratings_distribution': {
                'low_rated': (self.df['average_rating'] < 3).sum(),
                'mid_rated': ((self.df['average_rating'] >= 3) & (self.df['average_rating'] < 4)).sum(),
                'high_rated': (self.df['average_rating'] >= 4).sum()
            }
        }
        return analysis

    def _generate_visualizations(self, analysis: Dict[str, Any]):
        """
        Create visualizations for the dataset.
        
        :param analysis: Dictionary containing analysis insights
        """
        plt.figure(figsize=(10, 6))
        
        # Genre Distribution
        top_genres = list(analysis['top_genres'].keys())
        top_genre_counts = list(analysis['top_genres'].values())
        plt.subplot(1, 2, 1)
        plt.pie(top_genre_counts, labels=top_genres, autopct='%1.1f%%')
        plt.title('Top 5 Book Genres')
        
        # Ratings Distribution
        plt.subplot(1, 2, 2)
        ratings_dist = analysis['ratings_distribution']
        plt.bar(ratings_dist.keys(), ratings_dist.values())
        plt.title('Book Ratings Distribution')
        plt.xlabel('Rating Categories')
        plt.ylabel('Number of Books')
        
        plt.tight_layout()
        plt.savefig(os.path.join(self.output_dir, 'genre_ratings_distribution.png'), dpi=100)
        plt.close()

        # Rating vs Ratings Count Scatter
        plt.figure(figsize=(10, 6))
        sns.scatterplot(data=self.df, x='ratings_count', y='average_rating', alpha=0.5)
        plt.title('Book Ratings vs Number of Ratings')
        plt.xlabel('Number of Ratings')
        plt.ylabel('Average Rating')
        plt.xscale('log')
        plt.savefig(os.path.join(self.output_dir, 'ratings_scatter.png'), dpi=100)
        plt.close()

    @retry_with_backoff()
    def _generate_narrative(self, analysis: Dict[str, Any]):
        """
        Generate a narrative using OpenAI GPT-4o-mini.
        
        :param analysis: Dictionary containing analysis insights
        :return: Generated narrative text
        """
        token = os.getenv("AIPROXY_TOKEN")
        if not token:
            raise ValueError("AIPROXY_TOKEN not set")

        headers = {
            "Authorization": f"Bearer {token}",
            "Content-Type": "application/json"
        }

        prompt = f"""
        Write an engaging narrative about a Goodreads book dataset analysis:
        
        Dataset Overview:
        - Total Books: {analysis['total_books']}
        - Unique Genres: {analysis['genres']}
        
        Rating Insights:
        - Mean Rating: {analysis['rating_stats']['mean_rating']:.2f}
        - Rating Standard Deviation: {analysis['rating_stats']['rating_std']:.2f}
        
        Genre Distribution:
        {json.dumps(analysis['top_genres'], indent=2)}
        
        Ratings Categories:
        - Low Rated Books (< 3): {analysis['ratings_distribution']['low_rated']}
        - Mid Rated Books (3-4): {analysis['ratings_distribution']['mid_rated']}
        - High Rated Books (>= 4): {analysis['ratings_distribution']['high_rated']}

        Provide insights, potential reasons for these patterns, and implications for readers and publishers.
        """

        data = {
            "model": "gpt-4o-mini",
            "messages": [
                {"role": "system", "content": "You are a data scientist writing an engaging analysis narrative."},
                {"role": "user", "content": prompt}
            ]
        }

        response = requests.post(
            "https://aiproxy.sanand.workers.dev/openai/v1/chat/completions",
            headers=headers,
            json=data
        )

        if response.status_code == 200:
            narrative = response.json()['choices'][0]['message']['content']
            
            # Add visualization references
            narrative += "\n\n## Visualizations\n"
            narrative += "### Genre and Ratings Distribution\n"
            narrative += "![Genre Ratings Distribution](genre_ratings_distribution.png)\n\n"
            narrative += "### Ratings vs Number of Ratings\n"
            narrative += "![Ratings Scatter Plot](ratings_scatter.png)\n"

            with open(os.path.join(self.output_dir, 'README.md'), 'w', encoding='utf-8') as f:
                f.write(narrative)
        else:
            raise Exception(f"API Error: {response.status_code}, {response.text}")

    def analyze(self):
        """
        Orchestrate the entire analysis process.
        """
        analysis = self._analyze_dataset()
        self._generate_visualizations(analysis)
        self._generate_narrative(analysis)
        print(f"Analysis complete. Results saved in {self.output_dir}")

def main():
    if len(sys.argv) != 2:
        print("Usage: python autolysis.py <goodreads_dataset.csv>")
        sys.exit(1)

    analysis = GoodreadsAnalysis(sys.argv[1])
    analysis.analyze()

if __name__ == "__main__":
    main()