"""
Generate and open the comprehensive fuzzy analysis report
"""
import os
import webbrowser
from plot_rules import FuzzyRulesPlotter
import matplotlib.pyplot as plt

def generate_complete_report():
    """Generate all plots and open the HTML report"""
    print("Generating complete fuzzy analysis report...")
    
    # Create analysis directories if they don't exist
    import os
    os.makedirs("analysis/fuzzy_rules", exist_ok=True)
    os.makedirs("analysis/elevator_performance", exist_ok=True)
    os.makedirs("analysis/test_results", exist_ok=True)
    
    plotter = FuzzyRulesPlotter()
    
    # Generate all required plots in the fuzzy_rules folder
    print("1. Creating rule table...")
    table_fig = plotter.plot_rule_table()
    table_fig.savefig("analysis/fuzzy_rules/fuzzy_rules_table.png", dpi=300, bbox_inches='tight')
    plt.close(table_fig)
    
    print("2. Creating rule surface...")
    surface_fig = plotter.plot_rule_surface()
    surface_fig.savefig("analysis/fuzzy_rules/fuzzy_rules_surface.png", dpi=300, bbox_inches='tight')
    plt.close(surface_fig)
    
    print("3. Creating 2D membership functions...")
    membership_fig = plotter.plot_membership_functions()
    membership_fig.savefig("analysis/fuzzy_rules/fuzzy_membership_functions_2d.png", dpi=300, bbox_inches='tight')
    plt.close(membership_fig)
    
    print("4. Creating rule activation examples...")
    examples = [
        (5.0, 2.0, "Medium error, positive delta"),
        (15.0, -1.0, "Large error, negative delta"), 
        (0.5, 0.0, "Small error, zero delta"),
        (25.0, 5.0, "Very large error, large positive delta")
    ]
    
    for i, (error, delta, description) in enumerate(examples):
        activation_fig = plotter.plot_rule_activation(error, delta)
        filename = f"analysis/fuzzy_rules/fuzzy_rules_activation_example_{i+1}.png"
        activation_fig.savefig(filename, dpi=300, bbox_inches='tight')
        plt.close(activation_fig)
        print(f"   Saved: {filename}")
    
    print("\nAll visualizations created successfully!")
    
    # Open the HTML report
    report_path = os.path.abspath("analysis/fuzzy_analysis_report.html")
    if os.path.exists(report_path):
        print(f"Opening HTML report: {report_path}")
        webbrowser.open(f"file://{report_path}")
        print("HTML report opened in your default browser!")
    else:
        print("HTML report file not found. Please check if analysis/fuzzy_analysis_report.html exists.")
    
    print("\nReport generation complete!")
    print("All plots are organized in the analysis/ folder structure:")
    print("- analysis/fuzzy_rules/ - Fuzzy logic visualizations")
    print("- analysis/elevator_performance/ - Elevator behavior analysis")
    print("- analysis/test_results/ - Test result files")

if __name__ == "__main__":
    generate_complete_report()
