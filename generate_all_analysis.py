"""
Master Analysis Generator
Generates all analysis files in organized folder structure
"""

import os

def create_all_analysis():
    """Generate all analysis files in organized folders"""
    print("🚀 Master Analysis Generator")
    print("Generating all elevator analysis files in organized structure...")
    print("="*60)
    
    # 1. Generate fuzzy rules analysis
    print("\n1️⃣ Generating Fuzzy Rules Analysis...")
    try:
        os.system("python generate_report.py")
        print("✅ Fuzzy rules analysis completed")
    except Exception as e:
        print(f"❌ Error in fuzzy rules analysis: {e}")
    
    # 2. Generate elevator performance analysis
    print("\n2️⃣ Generating Elevator Performance Analysis...")
    try:
        os.system("python plot_analysis.py")
        print("✅ Elevator performance analysis completed")
    except Exception as e:
        print(f"❌ Error in performance analysis: {e}")
    
    # 3. Run official tests
    print("\n3️⃣ Running Official Tests...")
    print("Note: This will run interactive tests. You can skip by pressing Ctrl+C")
    try:
        response = input("Run official tests? (y/n): ").lower()
        if response == 'y':
            os.system("python teste_oficial.py")
            print("✅ Official tests completed")
        else:
            print("⏭️ Official tests skipped")
    except KeyboardInterrupt:
        print("\n⏭️ Official tests skipped")
    except Exception as e:
        print(f"❌ Error in official tests: {e}")
    
    print("\n" + "="*60)
    print("🎉 Analysis Generation Complete!")
    print("\n📁 Generated files are organized in:")
    print("   analysis/")
    print("   ├── fuzzy_rules/          # Fuzzy logic visualizations")
    print("   ├── elevator_performance/ # Elevator behavior analysis") 
    print("   ├── test_results/         # Test result files")
    print("   ├── README.md             # Documentation")
    print("   └── fuzzy_analysis_report.html # Complete HTML report")
    print("\n🌐 Open the HTML report for a comprehensive view!")

if __name__ == "__main__":
    create_all_analysis()
