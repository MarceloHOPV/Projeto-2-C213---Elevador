from plot_rules import FuzzyRulesPlotter
import matplotlib.pyplot as plt

# Criar o plotter
plotter = FuzzyRulesPlotter()

# Gerar e salvar a tabela de regras
print("Gerando tabela de regras fuzzy atualizada...")
fig = plotter.plot_rule_table()
plt.savefig('analysis/fuzzy_rules/fuzzy_rules_table.png', dpi=300, bbox_inches='tight')
print("Tabela salva em: analysis/fuzzy_rules/fuzzy_rules_table.png")

# Gerar e salvar as funções de pertinência
print("Gerando funções de pertinência...")
fig2 = plotter.plot_membership_functions()
plt.savefig('analysis/fuzzy_rules/fuzzy_membership_functions_2d.png', dpi=300, bbox_inches='tight')
print("Funções de pertinência salvas em: analysis/fuzzy_rules/fuzzy_membership_functions_2d.png")

print("✅ Atualização concluída!")
