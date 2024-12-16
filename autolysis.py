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
import numpy as np
import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt
from scipy import stats
from typing import Dict, Any
import requests

class DatasetAnalysis:
    def __init__(self, file_path: str):
        """
        Initialize the analysis with the given dataset.
        
        :param file_path: Path to the CSV file
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
                
                # Print available columns for debugging
                print("Available columns:", list(df.columns))
                
                return df
            except (UnicodeDecodeError, pd.errors.EmptyDataError) as e:
                print(f"Error with encoding {encoding}: {e}")
                continue
        raise ValueError("Unable to load dataset with any encoding")

    def _analyze_dataset(self) -> Dict[str, Any]:
        """
        Perform comprehensive dataset analysis.
        
        :return: Dictionary with analysis insights
        """
        analysis = {
            'total_rows': int(len(self.df)),  # Convert to standard int
            'columns': list(self.df.columns),
            'column_types': {col: str(self.df[col].dtype) for col in self.df.columns}
        }
        
        # Numeric column analysis
        numeric_columns = self.df.select_dtypes(include=[np.number]).columns
        analysis['numeric_columns'] = {
            col: {
                'mean': float(self.df[col].mean()),
                'median': float(self.df[col].median()),
                'std': float(self.df[col].std()),
                'min': float(self.df[col].min()),
                'max': float(self.df[col].max())
            } for col in numeric_columns
        }
        
        # Missing values analysis
        analysis['missing_values'] = {k: int(v) for k, v in self.df.isnull().sum().to_dict().items()}
        
        # Correlation matrix for numeric columns
        if len(numeric_columns) > 1:
            try:
                correlation_matrix = self.df[numeric_columns].corr()
                analysis['correlation_matrix'] = correlation_matrix.applymap(float).to_dict()  # Convert all values to float
            except Exception as e:
                print(f"Correlation matrix generation failed: {e}")
        
        return analysis

    def _generate_visualizations(self, analysis: Dict[str, Any]):
        """
        Create visualizations for the dataset.
        
        :param analysis: Dictionary containing analysis insights
        """
        numeric_columns = [col for col in self.df.columns if pd.api.types.is_numeric_dtype(self.df[col])]
        
        # Correlation Heatmap (if multiple numeric columns)
        if len(numeric_columns) > 1:
            plt.figure(figsize=(10, 8))
            correlation_matrix = self.df[numeric_columns].corr()
            sns.heatmap(correlation_matrix, annot=True, cmap='coolwarm', center=0)
            plt.title('Correlation Heatmap')
            plt.tight_layout()
            plt.savefig(os.path.join(self.output_dir, 'correlation_heatmap.png'), dpi=100)
            plt.close()
        
        # Distribution of Numeric Columns
        plt.figure(figsize=(15, 5))
        for i, col in enumerate(numeric_columns[:3], 1):  # Limit to first 3 numeric columns
            plt.subplot(1, 3, i)
            sns.histplot(self.df[col], kde=True)
            plt.title(f'Distribution of {col}')
            plt.xlabel(col)
            plt.ylabel('Frequency')
        plt.tight_layout()
        plt.savefig(os.path.join(self.output_dir, 'numeric_distributions.png'), dpi=100)
        plt.close()

    def _generate_narrative(self, analysis: Dict[str, Any]):
        """
        Generate a narrative using GPT-4o-mini.
        
        :param analysis: Dictionary containing analysis insights
        """
        token = os.environ.get("AIPROXY_TOKEN")
        if not token:
            raise ValueError("AIPROXY_TOKEN not set")

        # Prepare a concise summary for the LLM
        summary = json.dumps({
            'Dataset Overview': {
                'Total Rows': analysis['total_rows'],
                'Columns': analysis['columns'],
                'Column Types': analysis['column_types']
            },
            'Numeric Column Insights': analysis.get('numeric_columns', {}),
            'Missing Values': analysis['missing_values']
        }, indent=2)

        prompt = f"""
        Write an engaging narrative about the dataset analysis:

        Dataset Context:
        {summary}

        Please write a markdown document that:
        1. Briefly describes the dataset
        2. Highlights key insights from the analysis
        3. Suggests potential further investigations or implications
        4. Integrates the generated visualizations

        Use clear headings, markdown formatting, and an engaging storytelling approach.
        """

        headers = {
            "Authorization": f"Bearer {token}",
            "Content-Type": "application/json"
        }

        data = {
            "model": "gpt-4o-mini",
            "messages": [
                {"role": "system", "content": "You are a data scientist writing an engaging analysis narrative."},
                {"role": "user", "content": prompt}
            ]
        }

        try:
            response = requests.post(
                "https://aiproxy.sanand.workers.dev/openai/v1/chat/completions",
                headers=headers,
                json=data
            )

            if response.status_code == 200:
                narrative = response.json()['choices'][0]['message']['content']
                
                # Add visualization references
                narrative += "\n\n## Visualizations\n"
                if len(self.df.select_dtypes(include=[np.number]).columns) > 1:
                    narrative += "### Correlation Heatmap\n"
                    narrative += "![Correlation Heatmap](correlation_heatmap.png)\n\n"
                narrative += "### Numeric Columns Distribution\n"
                narrative += "![Numeric Distributions](numeric_distributions.png)\n"

                with open(os.path.join(self.output_dir, 'README.md'), 'w', encoding='utf-8') as f:
                    f.write(narrative)
            else:
                raise Exception(f"API Error: {response.status_code}, {response.text}")
        except Exception as e:
            print(f"Narrative generation failed: {e}")
            # Fallback narrative if LLM generation fails
            fallback_narrative = f"""
            # Dataset Analysis

            ## Overview
            - Total Rows: {analysis['total_rows']}
            - Columns: {', '.join(analysis['columns'])}

            ## Key Insights
            ### Numeric Columns
            {json.dumps(analysis.get('numeric_columns', {}), indent=2)}

            ### Missing Values
            {json.dumps(analysis['missing_values'], indent=2)}

            ## Visualizations
            See attached PNG files for more insights.
            """
            with open(os.path.join(self.output_dir, 'README.md'), 'w', encoding='utf-8') as f:
                f.write(fallback_narrative)

    def analyze(self):
        """
        Orchestrate the entire analysis process.
        """
        try:
            analysis = self._analyze_dataset()
            self._generate_visualizations(analysis)
            self._generate_narrative(analysis)
            print(f"Analysis complete. Results saved in {self.output_dir}")
        except Exception as e:
            print(f"Analysis failed: {e}")

def main():
    if len(sys.argv) != 2:
        print("Usage: uv run autolysis.py <dataset.csv>")
        sys.exit(1)

    analysis = DatasetAnalysis(sys.argv[1])
    analysis.analyze()

if __name__ == "__main__":
    main()