# Photo GPS Visualization Tool
A tool for extracting GPS information from photos and visualizing them on maps.

## Installation

1. Clone this repository:   ```bash
   git clone <repository-url>
   cd <repository-directory>   ```

2. Create a conda environment:   ```bash
   conda create --name photo-gps-env python=3.9   ```

3. Activate the conda environment:   ```bash
   conda activate photo-gps-env   ```

4. Install the required packages:   ```bash
   pip install -r requirements.txt   ```

## Scripts

### Script 1: `extract_gps.py`
- **Functionality**: Extracts GPS information from photos.
- **Usage**:   ```bash
  python extract_gps.py <photo-directory>  ```

### Script 2: `visualize_gps.py`
- **Functionality**: Visualizes GPS data on a map.
- **Usage**:   ```bash
  python visualize_gps.py <gps-data-file>  ```
