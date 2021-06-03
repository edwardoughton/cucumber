###VISUALISE MODEL OUTPUTS###
library(tidyverse)
library(ggpubr)

folder <- dirname(rstudioapi::getSourceEditorContext()$path)

filename = 'national_market_cost_results_technology_options.csv'
data <- read.csv(file.path(folder, '..', 'results', 'model_results', 'CHL', filename))

names(data)[names(data) == 'GID_0'] <- 'country'

data$scenario_adopt[grep("low", data$scenario)] = 'Low (2% Adoption Growth)'
data$scenario_adopt[grep("baseline", data$scenario)] = 'Baseline (4% Adoption Growth)'
data$scenario_adopt[grep("high", data$scenario)] = 'High (6% Adoption Growth)'

data$scenario_capacity[grep("5_5_5", data$scenario)] = '~5 Mbps Per User'
data$scenario_capacity[grep("10_10_10", data$scenario)] = '~10 Mbps Per User'
data$scenario_capacity[grep("20_20_20", data$scenario)] = '~20 Mbps Per User'

data$strategy_short = ''
data$strategy_short[grep("3G_umts_fiber", data$strategy)] = '3G (F)'
data$strategy_short[grep("3G_umts_wireless", data$strategy)] = '3G (W)'
data$strategy_short[grep("4G_epc_fiber", data$strategy)] = '4G (F)'
data$strategy_short[grep("4G_epc_wireless", data$strategy)] = '4G (W)'
data$strategy_short[grep("5G_nsa_fiber", data$strategy)] = '5G (F)'
data$strategy_short[grep("5G_nsa_wireless", data$strategy)] = '5G (W)'

data$strategy_short = factor(data$strategy_short, levels=c(
                                     "3G (F)",
                                     "4G (F)",
                                     '5G (F)',
                                     "3G (W)",
                                     "4G (W)",
                                     '5G (W)'
                                     ))

data$scenario_capacity = factor(data$scenario_capacity, 
                                levels=c("~20 Mbps Per User",
                                         "~10 Mbps Per User",
                                         "~5 Mbps Per User"))

data = data[complete.cases(data), ]

data$scenario_adopt = factor(data$scenario_adopt, 
                             levels=c("Low (2% Adoption Growth)",
                                      "Baseline (4% Adoption Growth)",
                                      "High (6% Adoption Growth)"))

data <- data[(data$confidence == 50),]

data <- select(data, scenario_adopt, scenario_capacity, strategy_short, 
               cost_per_network_user, cost_per_smartphone_user, 
               private_cost, government_cost, societal_cost)

totals <- data %>%
  group_by(scenario_adopt, scenario_capacity, strategy_short) %>%
  summarize(social_cost = round(
    (societal_cost)/1e9))

min_value = min(round(data$societal_cost/ 1e9))
max_value = max(round(data$societal_cost/ 1e9))
min_value[min_value > 0] = 0

colnames(data)[colnames(data) == 'private_cost'] <- 'Private Cost ($USD)'
colnames(data)[colnames(data) == 'government_cost'] <- 'Government Cost ($USD)'
colnames(data)[colnames(data) == 'societal_cost'] <- 'Social Cost ($USD)'

data <- data %>% gather(key="Cost_Type", value = "value",
                        'Private Cost ($USD)', 
                        'Government Cost ($USD)', 
)

data$value = round(data$value/1e9, 3)

ggplot(data, aes(y=value, x=strategy_short, fill=Cost_Type)) + 
  geom_bar(position="stack", stat="identity") +
  geom_text(aes(strategy_short, social_cost, label = social_cost, fill = NULL),
            size = 2.5, data = totals, hjust=-.2) +
  coord_flip() +
  scale_fill_manual(values=c("#E1BE6A", "#40B0A6"), name=NULL) +
  theme(legend.position = "bottom",
        axis.text.x = element_text(angle = 45, hjust=1)) +
  labs(title = "Social Cost of Universal Broadband by Technology", 
       colour=NULL,
       subtitle = "Reported for all scenarios and capacity per user targets",
       x = NULL, y = "Social Cost (Billions $USD)") +
  scale_y_continuous(expand = c(0, 0), limits = c(0, max_value+100)) +
  theme(panel.spacing = unit(0.6, "lines")) +
  guides(fill=guide_legend(ncol=3, reverse = TRUE)) +
  facet_grid(scenario_capacity~scenario_adopt)

dir.create(file.path(folder, 'figures'), showWarnings = FALSE)
path = file.path(folder, 'figures', 'social_costs_by_strategy.png')
ggsave(path, units="in", width=8, height=7, dpi=300)
dir.create(file.path(folder, '..', 'reports', 'images', 'CHL'), showWarnings = FALSE)
path = file.path(folder, '..', 'reports', 'images', 'CHL', 'social_costs_by_strategy.png')
ggsave(path, units="in", width=8, height=7, dpi=300)
dev.off()

################################################################################

folder <- dirname(rstudioapi::getSourceEditorContext()$path)

filename = 'national_market_cost_results_business_model_options.csv'
data <- read.csv(file.path(folder, '..', 'results', 'model_results', 'CHL', filename))

names(data)[names(data) == 'GID_0'] <- 'country'

data$scenario_adopt[grep("low", data$scenario)] = 'Low (2% Adoption Growth)'
data$scenario_adopt[grep("baseline", data$scenario)] = 'Baseline (4% Adoption Growth)'
data$scenario_adopt[grep("high", data$scenario)] = 'High (6% Adoption Growth)'

data$scenario_capacity[grep("5_5_5", data$scenario)] = '~5 Mbps Per User'
data$scenario_capacity[grep("10_10_10", data$scenario)] = '~10 Mbps Per User'
data$scenario_capacity[grep("20_20_20", data$scenario)] = '~20 Mbps Per User'

data$strategy_short = ''
data$strategy_short[grep("4G_epc_wireless", data$strategy)] = '4G (W)'

data = data %>% filter(data$strategy_short == '4G (W)')

data$strategy = factor(data$strategy, levels=c(
  "4G_epc_wireless_active_baseline_baseline_baseline",
  "4G_epc_wireless_passive_baseline_baseline_baseline",
  "4G_epc_wireless_srn_baseline_baseline_baseline",
  "4G_epc_wireless_baseline_baseline_baseline_baseline"
),
labels=c(
  "Active",
  "Passive",
  "SRN",
  "Baseline"
))

data$scenario_capacity = factor(data$scenario_capacity, 
                                levels=c("~20 Mbps Per User",
                                         "~10 Mbps Per User",
                                         "~5 Mbps Per User"))

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
  summarize(social_cost = round(
    (societal_cost)/1e9, 1))

min_value = min(round(data$societal_cost/ 1e9))
max_value = max(round(data$societal_cost/ 1e9))
min_value[min_value > 0] = 0

data$social_cost = data$private_cost + data$government_cost
# write.csv(data, file.path(folder, 'business_model_percentages.csv'))

colnames(data)[colnames(data) == 'private_cost'] <- 'Private Cost ($USD)'
colnames(data)[colnames(data) == 'government_cost'] <- 'Government Cost ($USD)'
colnames(data)[colnames(data) == 'societal_cost'] <- 'Social Cost ($USD)'

data <- data %>% gather(key="Cost_Type", value = "value",
                        'Private Cost ($USD)', 
                        'Government Cost ($USD)', 
)

data$value = round(data$value/1e9, 3)


ggplot(data, aes(y=value, x=strategy, fill=Cost_Type)) + 
  geom_bar(position="stack", stat="identity") +
  geom_text(aes(strategy, social_cost, label = social_cost, fill = NULL),
            size = 2.5, data = totals, hjust=-.3) +
  coord_flip() +
  scale_fill_manual(values=c("#E1BE6A", "#40B0A6"), name=NULL) +
  theme(legend.position = "bottom",
        axis.text.x = element_text(angle = 45, hjust=1)) +
  labs(title = "Social Cost of Universal Broadband by Infrastructure Sharing Strategy", 
       colour=NULL,
       subtitle = "Reported using 4G (W) for all scenarios and capacity per user targets",
       x = NULL, y = "Social Cost (Billions $USD)") +
  scale_y_continuous(expand = c(0, 0), limits = c(-min_value, max_value+100)) +
  theme(panel.spacing = unit(0.6, "lines")) +
  guides(fill=guide_legend(ncol=3, reverse = TRUE)) +
  facet_grid(scenario_capacity~scenario_adopt)

path = file.path(folder, 'figures', 'social_costs_by_sharing_strategy.png')
ggsave(path, units="in", width=8, height=7, dpi=300)
path = file.path(folder, '..', 'reports', 'images', 'CHL', 'social_costs_by_sharing_strategy.png')
ggsave(path, units="in", width=8, height=7, dpi=300)
dev.off()

################################################################################

folder <- dirname(rstudioapi::getSourceEditorContext()$path)

filename = 'national_market_cost_results_policy_options.csv'
data <- read.csv(file.path(folder, '..', 'results', 'model_results', 'CHL', filename))

names(data)[names(data) == 'GID_0'] <- 'country'

data$scenario_adopt[grep("low", data$scenario)] = 'Low (2% Adoption Growth)'
data$scenario_adopt[grep("baseline", data$scenario)] = 'Baseline (4% Adoption Growth)'
data$scenario_adopt[grep("high", data$scenario)] = 'High (6% Adoption Growth)'

data$scenario_capacity[grep("5_5_5", data$scenario)] = '5 Mbps Per User'
data$scenario_capacity[grep("10_10_10", data$scenario)] = '10 Mbps Per User'
data$scenario_capacity[grep("20_20_20", data$scenario)] = '20 Mbps Per User'

data$strategy_short = ''
data$strategy_short[grep("4G_epc_wireless", data$strategy)] = '4G (W)'

data = data %>% filter(data$strategy_short == '4G (W)')

data$strategy = factor(data$strategy, levels=c(
  "4G_epc_wireless_baseline_baseline_high_baseline",
  "4G_epc_wireless_baseline_baseline_low_baseline",
  "4G_epc_wireless_baseline_baseline_baseline_high",
  "4G_epc_wireless_baseline_baseline_baseline_low",
  "4G_epc_wireless_baseline_baseline_baseline_baseline"
  ),
labels=c(
  "High Spectrum\nFees",
  "Low Spectrum\nFees",
  "High Tax",
  "Low Tax",
  "Baseline"
  ))

data = data[complete.cases(data),]

data$scenario_capacity = factor(data$scenario_capacity, 
                                levels=c("20 Mbps Per User",
                                         "10 Mbps Per User",
                                         "5 Mbps Per User"),
                                labels=c(
                                  "~20 Mbps Per User",
                                  "~10 Mbps Per User",
                                  "~5 Mbps Per User"
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
  summarize(social_cost = round(
    (societal_cost)/1e9, 1))

min_value = min(round(data$societal_cost/ 1e9, 2))
max_value = max(round(data$societal_cost/ 1e9, 2))
min_value[min_value > 0] = 0

colnames(data)[colnames(data) == 'private_cost'] <- 'Private Cost ($USD)'
colnames(data)[colnames(data) == 'government_cost'] <- 'Government Cost ($USD)'
colnames(data)[colnames(data) == 'societal_cost'] <- 'Social Cost ($USD)'

data <- data %>% gather(key="Cost_Type", value = "value",
                        'Private Cost ($USD)', 
                        'Government Cost ($USD)', 
)

data$value = round(data$value/1e9, 2)

ggplot(data, aes(y=value, x=strategy, fill=Cost_Type)) + 
  geom_bar(position="stack", stat="identity") +
  geom_text(aes(strategy, social_cost, label = social_cost, fill = NULL),
            size = 2.5, data = totals, hjust=-.3) +
  coord_flip() +
  scale_fill_manual(values=c("#E1BE6A", "#40B0A6"), name=NULL) +
  theme(legend.position = "bottom",
        axis.text.x = element_text(angle = 45, hjust=1)) +
  labs(title = "Social Cost of Universal Broadband by Policy Strategy", 
       colour=NULL,
       subtitle = "Reported using 4G (W) for all scenarios and capacity per user targets",
       x = NULL, y = "Social Cost (Billions $USD)") +
  scale_y_continuous(expand = c(0, 0), limits = c(-0, max_value+100)) +
  theme(panel.spacing = unit(0.6, "lines")) +
  guides(fill=guide_legend(ncol=3, reverse = TRUE)) +
  facet_grid(scenario_capacity~scenario_adopt)

path = file.path(folder, 'figures', 'social_costs_by_policy_options.png')
ggsave(path, units="in", width=8, height=7, dpi=300)
path = file.path(folder, '..', 'reports', 'images', 'CHL', 'social_costs_by_policy_options.png')
ggsave(path, units="in", width=8, height=7, dpi=300)
dev.off()
