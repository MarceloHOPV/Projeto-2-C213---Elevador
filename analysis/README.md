# Analysis Folder Structure

This folder contains all analysis files organized by category for better project organization.

## 📁 Folder Structure

```
analysis/
├── fuzzy_rules/                    # Fuzzy Logic Analysis
│   ├── fuzzy_rules_table.png           # Rules heatmap table
│   ├── fuzzy_rules_surface.png         # 3D control surface
│   ├── fuzzy_membership_functions_2d.png # 2D membership functions
│   └── fuzzy_rules_activation_example_*.png # Rule activation examples
│
├── elevator_performance/           # Elevator Behavior Analysis
│   ├── elevator_analysis_*.png         # Individual scenario analysis
│   ├── elevator_comparison_analysis.png # Comparison between scenarios
│   └── elevator_fuzzy_analysis.png     # Fuzzy system behavior
│
├── test_results/                   # Test Results
│   └── resultados_teste_oficial_*.json # Official test results
│
└── fuzzy_analysis_report.html     # Complete HTML Report
```

## 📊 File Descriptions

### Fuzzy Rules Analysis
- **fuzzy_rules_table.png**: Heatmap showing all 20 fuzzy rules mapping Error × Delta Error → Motor Power
- **fuzzy_rules_surface.png**: 3D surface plot showing the complete fuzzy control behavior
- **fuzzy_membership_functions_2d.png**: 2D plots of all membership functions for inputs and outputs
- **fuzzy_rules_activation_example_*.png**: Examples showing how rules activate for specific input combinations

### Elevator Performance Analysis
- **elevator_analysis_*.png**: Individual analysis plots for each movement scenario (terreo↔andar_1, terreo↔andar_4, terreo↔andar_8)
- **elevator_comparison_analysis.png**: Comparative analysis showing all scenarios together
- **elevator_fuzzy_analysis.png**: Analysis of fuzzy system behavior and surfaces

### Test Results
- **resultados_teste_oficial_*.json**: JSON files containing complete test results with timestamps, success rates, and detailed data

### HTML Report
- **fuzzy_analysis_report.html**: Comprehensive HTML report with all visualizations embedded and detailed technical analysis

## 🛠️ How to Generate Files

### Generate All Analysis Files
```bash
python generate_report.py
```

### Generate Performance Analysis
```bash
python plot_analysis.py
```

### Generate Fuzzy Rules Analysis
```bash
python plot_rules.py
```

### Run Official Tests
```bash
python teste_oficial.py
```

## 📋 Usage Notes

- All scripts automatically create the necessary folder structure
- Files are organized by type for easy navigation and sharing
- The HTML report references files using relative paths within this structure
- PNG files are saved at 300 DPI for high-quality output
- JSON test results include timestamps for version tracking

## 🔗 File Relationships

The HTML report (`fuzzy_analysis_report.html`) automatically references all image files in their respective subfolders, creating a complete, self-contained analysis document that can be easily shared or presented.
