###VISUALISE MODEL OUTPUTS###
library(tidyverse)
library(ggpubr)

folder <- dirname(rstudioapi::getSourceEditorContext()$path)

iso3 = 'COL'

filename = 'national_market_cost_results_technology_options.csv'
data <- read.csv(file.path(folder, '..', 'results', 'model_results', iso3, filename))

names(data)[names(data) == 'GID_0'] <- 'country'

data$scenario_adopt = ''
data$scenario_adopt[grep("low", data$scenario)] = 'Low (2% Adoption CAGR)'
data$scenario_adopt[grep("baseline", data$scenario)] = 'Baseline (4% Adoption CAGR)'
data$scenario_adopt[grep("high", data$scenario)] = 'High (6% Adoption CAGR)'

data$scenario_capacity = ''
data$scenario_capacity[grep("20_20_20", data$scenario)] = '20 GB/Month'
data$scenario_capacity[grep("30_30_30", data$scenario)] = '30 GB/Month'
data$scenario_capacity[grep("40_40_40", data$scenario)] = '40 GB/Month'

data$strategy_short = ''
data$strategy_short[grep("4G_epc_fiber", data$strategy)] = '4G (F)'
data$strategy_short[grep("4G_epc_wireless", data$strategy)] = '4G (W)'
data$strategy_short[grep("5G_nsa_fiber", data$strategy)] = '5G (F)'
data$strategy_short[grep("5G_nsa_wireless", data$strategy)] = '5G (W)'

data$strategy_short = factor(data$strategy_short, levels=c(
                                    "4G (F)",
                                    "4G (W)",
                                    '5G (F)',
                                    '5G (W)'
                                     ))

data$scenario_capacity = factor(data$scenario_capacity,
                                levels=c('20 GB/Month',
                                         '30 GB/Month',
                                         '40 GB/Month'
                                ))

data = data[complete.cases(data), ]

data$scenario_adopt = factor(data$scenario_adopt, 
                             levels=c("Low (2% Adoption CAGR)",
                                      "Baseline (4% Adoption CAGR)",
                                      "High (6% Adoption CAGR)"))

data <- data[(data$confidence == 50),]

totals <- data %>%
  group_by(scenario_adopt, scenario_capacity, strategy_short) %>%
  summarize(financial_cost = round(
    (societal_cost)/1e9))

min_value = min(round(data$societal_cost/ 1e9))
max_value = max(round(data$societal_cost/ 1e9))
min_value[min_value > 0] = 0

data <- select(data, scenario_adopt, scenario_capacity, strategy_short, 
               cost_per_network_user, cost_per_smartphone_user, 
               private_cost, government_cost)

colnames(data)[colnames(data) == 'private_cost'] <- 'Private Investment Cost ($USD)'
colnames(data)[colnames(data) == 'government_cost'] <- 'Government Cost ($USD)'
# colnames(data)[colnames(data) == 'societal_cost'] <- 'Financial Cost ($USD)'

data <- data %>% gather(key="Cost_Type", value = "value",
                        'Private Investment Cost ($USD)', 
                        'Government Cost ($USD)', 
)

data$Cost_Type = factor(data$Cost_Type, 
                             levels=c("Government Cost ($USD)",
                                      "Private Investment Cost ($USD)"
                                      ))

data$value = round(data$value/1e9, 3)

ggplot(data, aes(y=value, x=strategy_short, fill=Cost_Type)) + 
  geom_bar(position="stack", stat="identity") +
  geom_text(y=0, aes(strategy_short, financial_cost, label = financial_cost, 
                     fill = NULL, color="#FF0000FF"), show.legend = FALSE,
            size = 3, data = totals, vjust=-.3, hjust=.5) +
  scale_fill_manual(values=c("#29af7f", "#482173"), name=NULL) +
  theme(legend.position = "bottom",
        axis.text.x = element_text(angle = 45, hjust=1)) +
  labs(title = "Financial Cost of Universal Broadband by Technology in Colombia", 
       colour=NULL,
       subtitle = "Reported for all adoption scenarios and capacity per user targets (2020-2030)",
       x = NULL, y = "Financial Cost (Billions $USD)") +
  scale_y_continuous(expand = c(0, 0), limits = c(0, max_value+8)) +
  theme(panel.spacing = unit(0.5, "lines")) +
  guides(fill=guide_legend(ncol=3, reverse = TRUE)) +
  facet_grid(scenario_capacity~scenario_adopt)

dir.create(file.path(folder, 'figures', iso3), showWarnings = FALSE)
path = file.path(folder, 'figures', iso3, 'financial_costs_by_strategy.png')
ggsave(path, units="in", width=8, height=6, dpi=300)
dir.create(file.path(folder, '..', 'reports', 'images', 'COL'), showWarnings = FALSE)
path = file.path(folder, '..', 'reports', 'images', 'COL', 'financial_costs_by_strategy.png')
ggsave(path, units="in", width=8, height=6, dpi=300)
dev.off()

dir.create(file.path(folder, 'report_data'), showWarnings = FALSE)
filename = 'technology_costs_colombia_2.17.csv'
path = file.path(folder, 'report_data', filename)
write.csv(data, path)

################################################################################

folder <- dirname(rstudioapi::getSourceEditorContext()$path)

filename = 'national_market_cost_results_business_model_options.csv'
data <- read.csv(file.path(folder, '..', 'results', 'model_results', 'COL', filename))

names(data)[names(data) == 'GID_0'] <- 'country'

data$scenario_adopt[grep("low", data$scenario)] = 'Low (2% Adoption Growth)'
data$scenario_adopt[grep("baseline", data$scenario)] = 'Baseline (4% Adoption Growth)'
data$scenario_adopt[grep("high", data$scenario)] = 'High (6% Adoption Growth)'

data$scenario_capacity = ''
data$scenario_capacity[grep("20_20_20", data$scenario)] = '20 GB/Month'
data$scenario_capacity[grep("30_30_30", data$scenario)] = '30 GB/Month'
data$scenario_capacity[grep("40_40_40", data$scenario)] = '40 GB/Month'

data$strategy_short = ''
data$strategy_short[grep("4G_epc_wireless", data$strategy)] = '4G (W)'

data = data %>% filter(data$strategy_short == '4G (W)')

data$strategy = factor(data$strategy, levels=c(
  "4G_epc_wireless_baseline_baseline_baseline_baseline_baseline",
  "4G_epc_wireless_passive_baseline_baseline_baseline_baseline",
  "4G_epc_wireless_srn_baseline_baseline_baseline_baseline",
  "4G_epc_wireless_active_baseline_baseline_baseline_baseline"
),
labels=c(
  "Baseline",
  "Passive",
  "SRN",
  "Active"
))

data$scenario_capacity = factor(data$scenario_capacity,
                                levels=c('20 GB/Month',
                                         '30 GB/Month',
                                         '40 GB/Month'
                                ))

data$scenario_adopt = factor(data$scenario_adopt,
                             levels=c("Low (2% Adoption Growth)",
                                      "Baseline (4% Adoption Growth)",
                                      "High (6% Adoption Growth)"))

data <- data[(data$confidence == 50),]

data <- select(data, scenario_adopt, scenario_capacity, strategy,
               cost_per_network_user, cost_per_smartphone_user,
               private_cost, government_cost, societal_cost)

totals <- data %>%
  group_by(scenario_adopt, scenario_capacity, strategy) %>%
  summarize(financial_cost = round(
    (societal_cost)/1e9))

min_value = min(round(data$societal_cost/ 1e9))
max_value = max(round(data$societal_cost/ 1e9))
min_value[min_value > 0] = 0

data$financial_cost = data$private_cost + data$government_cost
# write.csv(data, file.path(folder, 'business_model_percentages.csv'))

colnames(data)[colnames(data) == 'private_cost'] <- 'Private Investment Cost ($USD)'
colnames(data)[colnames(data) == 'government_cost'] <- 'Government Cost ($USD)'
colnames(data)[colnames(data) == 'societal_cost'] <- 'Financial Cost ($USD)'

data <- data %>% gather(key="Cost_Type", value = "value",
                        'Private Investment Cost ($USD)',
                        'Government Cost ($USD)',
)

data$Cost_Type = factor(data$Cost_Type,
                        levels=c("Government Cost ($USD)",
                                 "Private Investment Cost ($USD)"
                        ))

data$value = round(data$value/1e9, 3)

ggplot(data, aes(y=value, x=strategy, fill=Cost_Type)) +
  geom_bar(position="stack", stat="identity") +
  geom_text(y=0, aes(strategy, financial_cost, label = financial_cost,
                     fill = NULL, color="#FF0000FF"), show.legend = FALSE,
            size = 3, data = totals, vjust=-.5, hjust=.5) +
  scale_fill_manual(values=c("#29af7f", "#482173"), name=NULL) +
  theme(legend.position = "bottom",
        axis.text.x = element_text(angle = 45, hjust=1)) +
  labs(title = "Financial Cost of Universal Broadband by Infrastructure Sharing Strategy in Colombia",
       colour=NULL,
       subtitle = "Reported using 4G (W) for all adoption scenarios and capacity per user targets (2020-2030)",
       x = NULL, y = "Financial Cost (Billions $USD)") +
  scale_y_continuous(expand = c(0, 0), limits = c(-min_value, max_value+10)) +
  theme(panel.spacing = unit(0.6, "lines")) +
  guides(fill=guide_legend(ncol=3, reverse = TRUE)) +
  facet_grid(scenario_capacity~scenario_adopt)

path = file.path(folder, 'figures', iso3, 'financial_costs_by_sharing_strategy.png')
ggsave(path, units="in", width=8, height=6, dpi=300)
dir.create(file.path(folder, '..', 'reports', 'images', 'COL'), showWarnings = FALSE)
path = file.path(folder, '..', 'reports', 'images', 'COL', 'financial_costs_by_sharing_strategy.png')
ggsave(path, units="in", width=8, height=6, dpi=300)
dev.off()

################################################################################

folder <- dirname(rstudioapi::getSourceEditorContext()$path)

filename = 'national_market_cost_results_policy_options.csv'
data <- read.csv(file.path(folder, '..', 'results', 'model_results', 'COL', filename))

names(data)[names(data) == 'GID_0'] <- 'country'

data$scenario_adopt[grep("low", data$scenario)] = 'Low (2% Adoption Growth)'
data$scenario_adopt[grep("baseline", data$scenario)] = 'Baseline (4% Adoption Growth)'
data$scenario_adopt[grep("high", data$scenario)] = 'High (6% Adoption Growth)'

data$scenario_capacity = ''
data$scenario_capacity[grep("20_20_20", data$scenario)] = '20 GB/Month'
data$scenario_capacity[grep("30_30_30", data$scenario)] = '30 GB/Month'
data$scenario_capacity[grep("40_40_40", data$scenario)] = '40 GB/Month'

data$strategy_short = ''
data$strategy_short[grep("4G_epc_wireless", data$strategy)] = '4G (W)'

data = data %>% filter(data$strategy_short == '4G (W)')

data$strategy = factor(data$strategy, levels=c(
  "4G_epc_wireless_baseline_baseline_baseline_baseline_baseline",
  "4G_epc_wireless_baseline_baseline_baseline_low_baseline",
  "4G_epc_wireless_baseline_baseline_baseline_high_baseline",
  "4G_epc_wireless_baseline_baseline_low_baseline_baseline",
  "4G_epc_wireless_baseline_baseline_high_baseline_baseline"
  ),
labels=c(
  "Baseline",
  "Low Tax",
  "High Tax",
  "Low Fees",
  "High Fees"
  ))

data = data[complete.cases(data),]

data$scenario_capacity = factor(data$scenario_capacity,
                                levels=c('20 GB/Month',
                                         '30 GB/Month',
                                         '40 GB/Month'
                                ))

data$scenario_adopt = factor(data$scenario_adopt,
                             levels=c("Low (2% Adoption Growth)",
                                      "Baseline (4% Adoption Growth)",
                                      "High (6% Adoption Growth)"))

data <- data[(data$confidence == 50),]

data <- select(data, scenario_adopt, scenario_capacity, strategy,
               cost_per_network_user, cost_per_smartphone_user,
               private_cost, government_cost, societal_cost)

totals <- data %>%
  group_by(scenario_adopt, scenario_capacity, strategy) %>%
  summarize(financial_cost = round(
    (societal_cost)/1e9, 1))

min_value = min(round(data$societal_cost/ 1e9, 2))
max_value = max(round(data$societal_cost/ 1e9, 2))
min_value[min_value > 0] = 0

colnames(data)[colnames(data) == 'private_cost'] <- 'Private Investment Cost ($USD)'
colnames(data)[colnames(data) == 'government_cost'] <- 'Government Cost ($USD)'
colnames(data)[colnames(data) == 'societal_cost'] <- 'Financial Cost ($USD)'

data <- data %>% gather(key="Cost_Type", value = "value",
                        'Private Investment Cost ($USD)',
                        'Government Cost ($USD)',
)

data$Cost_Type = factor(data$Cost_Type,
                        levels=c("Government Cost ($USD)",
                                 "Private Investment Cost ($USD)"
                        ))

data$value = round(data$value/1e9, 2)

ggplot(data, aes(y=value, x=strategy, fill=Cost_Type)) +
  geom_bar(position="stack", stat="identity") +
  geom_text(y=0, aes(strategy, financial_cost, label = financial_cost,
                     fill = NULL, color="#FF0000FF"), show.legend = FALSE,
            size = 3, data = totals, vjust=-1, hjust=.5) +
  scale_fill_manual(values=c("#29af7f", "#482173"), name=NULL) +
  theme(legend.position = "bottom",
        axis.text.x = element_text(angle = 45, hjust=1)) +
  labs(title = "Financial Cost of Universal Broadband by Policy Strategy in Colombia",
       colour=NULL,
       subtitle = "Reported using 4G (W) for all adoption scenarios and capacity per user targets (2020-2030)",
       x = NULL, y = "Financial Cost (Billions $USD)") +
  scale_y_continuous(expand = c(0, 0), limits = c(-0, max_value+10)) +
  theme(panel.spacing = unit(0.6, "lines")) +
  guides(fill=guide_legend(ncol=3, reverse = TRUE)) +
  facet_grid(scenario_capacity~scenario_adopt)

path = file.path(folder, 'figures', iso3, 'financial_costs_by_policy_options.png')
ggsave(path, units="in", width=8, height=6, dpi=300)
path = file.path(folder, '..', 'reports', 'images', 'COL', 'financial_costs_by_policy_options.png')
ggsave(path, units="in", width=8, height=6, dpi=300)
dev.off()
