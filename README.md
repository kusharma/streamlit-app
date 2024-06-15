# Streamlit app to view renewwable energy sources in switzerland

This Streamlit app visualizes energy production data across Switzerland. It provides interactive tools to explore the distribution and sources of renewable energy in different cantons and over different years.

[Streamlit App](https://app-app-k9pdqxj4hzdawnurqfxtbl.streamlit.app/)

## Features

- **Interactive Visualizations**: Utilize Plotly and Folium for dynamic and interactive maps and charts.
- **Data Filtering**: Filter data by energy source and year to focus on specific insights.
- **Geographical Context**: View energy production data overlaid on Swiss cantons using GeoJSON data.

## Installation

1. Clone the repository:
    ```sh
    git clone https://github.com/yourusername/swiss-energy-visualization.git
    cd swiss-energy-visualization
    ```

2. Install the required dependencies:
    ```sh
    pip install -r requirements.txt
    ```

3. Place the required data files (`renewable_power_plants_CH.csv`, `georef-switzerland-kanton.geojson`, and `swiss_cantons.csv`) in the `data/` directory.

## Usage

Run the Streamlit app:
```sh
streamlit run app3_v2.py
```

## Data Sources

- **Renewable Power Plants**: `renewable_power_plants_CH.csv`
- **Swiss Cantons GeoJSON**: `georef-switzerland-kanton.geojson`
- **Swiss Cantons Metadata**: `swiss_cantons.csv`

## App Structure

- **Data Loading and Caching**: Load and cache data for efficient processing.
- **User Interface**: Select energy sources and years to filter data.
- **Visualization**: Display interactive maps and charts of energy production.

## Contributing

Contributions are welcome! Please create a pull request or open an issue to discuss improvements or fixes.

## License

This project is licensed under the MIT License.
