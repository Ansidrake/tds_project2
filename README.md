# Automated Data Analysis Project

## Project Description

### Overview
This project is an advanced data analysis pipeline designed for the Tools in Data Science course. The primary goal is to create a flexible, intelligent Python script that can automatically analyze, visualize, and generate narrative insights from various CSV datasets using Large Language Models (LLMs).

### Key Features
- **Automated Analysis**: Dynamically explores and analyzes CSV datasets
- **Machine Learning Integration**: Utilizes GPT-4o-Mini for intelligent insights
- **Visualization**: Generates informative charts and graphs
- **Narrative Generation**: Creates human-readable markdown reports

## Project Structure

```
project-root/
│
├── autolysis.py         # Main analysis script
│
├── goodreads/           # Output for Goodreads dataset
│   ├── README.md        # Narrative analysis
│   ├── correlation_heatmap.png
│   └── numeric_distributions.png
│
├── happiness/           # Output for Happiness dataset
│   ├── README.md
│   ├── correlation_heatmap.png
│   └── numeric_distributions.png
│
└── media/               # Output for Media dataset
    ├── README.md
    ├── correlation_heatmap.png
    └── numeric_distributions.png
```

## Technical Components

### Script Capabilities
The `autolysis.py` script provides comprehensive data analysis through several key methods:

1. **Dataset Loading**
   - Supports multiple file encodings
   - Robust error handling
   - Automatic column type detection

2. **Statistical Analysis**
   - Calculate summary statistics
   - Identify missing values
   - Generate correlation matrices
   - Detect numeric column distributions

3. **Visualization**
   - Correlation heatmaps
   - Numeric column distributions
   - Customizable chart generation

4. **Narrative Generation**
   - Uses GPT-4o-Mini to create engaging, informative markdown reports
   - Integrates statistical insights with natural language

### Visualization Techniques
- **Correlation Heatmap**: 
  - Uses Seaborn's heatmap visualization
  - Color-coded correlation strength
  - Annotated with exact correlation values

- **Numeric Distributions**:
  - Histogram with kernel density estimation
  - Shows distribution shape and key characteristics
  - Supports multiple numeric columns

## Requirements and Dependencies

### System Requirements
- Python 3.11+
- `uv` package manager
- AI Proxy token

### Python Dependencies
- pandas
- numpy
- seaborn
- matplotlib
- scipy
- requests

## Installation and Setup

### 1. Install uv
```bash
# macOS/Linux
curl -LsSf https://astral.sh/uv/install.sh | sh

# Windows
powershell -c "irm https://astral.sh/uv/install.ps1 | iex"
```

### 2. Set Environment Variables
```bash
# Set AI Proxy token
export AIPROXY_TOKEN=your_token_here
```

## Usage

### Running the Script
```bash
# Analyze a dataset
uv run autolysis.py dataset.csv
```

### Example Datasets
1. Goodreads Books Dataset
2. World Happiness Report
3. Media Ratings Dataset

## Evaluation Criteria

### Code Quality (7 marks)
- Structural organization
- Analytical techniques
- Visualization effectiveness
- LLM prompt crafting
- Efficiency of LLM usage
- Dynamic prompting
- Agentic workflow implementation

### Output Quality (9 marks)
- Markdown document structure
- Depth of data understanding
- Visualization relevance and design

### Bonus Opportunities
- Code diversity
- Engaging and interesting analysis

## Troubleshooting

### Common Issues
- **HTTP 429 Error**: Retry the analysis
- **Missing Dependencies**: Ensure all required packages are installed
- **Token Limitations**: Monitor AI Proxy token usage

### Debugging Tips
- Use environment variable for AI Proxy token
- Check dataset compatibility
- Verify Python version (3.11+)

## Contributing
1. Fork the repository
2. Create a feature branch
3. Commit your changes
4. Push to the branch
5. Create a Pull Request

## License
MIT License

## Acknowledgments
- Course Instructors
- Anthropic (Claude AI)
- OpenAI (GPT-4o-Mini)
```