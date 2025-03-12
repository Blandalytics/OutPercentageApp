# Out Percentage Analysis

A Streamlit application for analyzing MLB player out percentages by pitch type using Statcast data.

![App Screenshot](https://i.imgur.com/placeholder.png)

## Overview

This application allows baseball analysts, fans, and researchers to explore how effective different pitch types are at generating outs for MLB players. The app calculates and visualizes out percentages by pitch type, providing insights into which pitches are most effective for specific players.

## Features

- **Player Selection**: Search and select any MLB player
- **Year Filter**: Analyze data from 2014 to present
- **Minimum Pitch Threshold**: Set minimum number of pitches for analysis
- **Interactive Visualizations**:
  - Pie chart showing out distribution by pitch type
  - Bar chart comparing out percentages across pitch types
  - Sortable data table with detailed statistics
- **Summary Statistics**: View overall out percentage and pitch counts
- **High-Quality Visualizations**: Uses serif fonts and high-resolution settings (300 DPI)

## Data Source

The application uses MLB Statcast data accessed through the [pybaseball](https://github.com/jldbc/pybaseball) package, which provides a Python interface to baseball data.

## How Out Percentage is Calculated

Out percentage is calculated as the number of pitches that resulted in an out divided by the total number of pitches of that type. The following events are considered outs:

- Field out
- Strikeout
- Double play (various types)
- Force out
- Sacrifice fly/bunt
- Other outs

## Local Installation

1. Clone this repository:
   ```
   git clone https://github.com/yourusername/out-percentage-analysis.git
   cd out-percentage-analysis
   ```

2. Create a virtual environment and install dependencies:
   ```
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   pip install -r requirements.txt
   ```

3. Run the application:
   ```
   streamlit run streamlit_app.py
   ```

## Deployment

This application is deployed on Streamlit Cloud and can be accessed at:
[https://out-percentage-analysis.streamlit.app](https://out-percentage-analysis.streamlit.app)

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## License

This project is licensed under the MIT License - see the LICENSE file for details.

## Acknowledgements

- [MLB Statcast](https://baseballsavant.mlb.com/) for providing the data
- [pybaseball](https://github.com/jldbc/pybaseball) for the Python interface to baseball data
- [Streamlit](https://streamlit.io/) for the web application framework 