###VISUALISE MODEL OUTPUTS###
library(tidyverse)
library(ggpubr)

folder <- dirname(rstudioapi::getSourceEditorContext()$path)

filename = 'emissions_technology_options.csv'
data <- read.csv(file.path(folder, '..', 'results', 'model_results', 'CHL', filename))

names(data)[names(data) == 'GID_0'] <- 'country'

data$scenario_adopt[grep("high", data$scenario)] = 'High (6% Adoption Growth)'
data$scenario_adopt[grep("baseline", data$scenario)] = 'Baseline (4% Adoption Growth)'
data$scenario_adopt[grep("low", data$scenario)] = 'Low (2% Adoption Growth)'
data <- data[(data$scenario_adopt == 'Baseline (4% Adoption Growth)'),]

data$scenario_capacity[grep("5_5_5", data$scenario)] = '~5 Mbps Per User'
data$scenario_capacity[grep("10_10_10", data$scenario)] = '~10 Mbps Per User'
data$scenario_capacity[grep("20_20_20", data$scenario)] = '~20 Mbps Per User'
# data <- data[(data$scenario_capacity == '~10 Mbps Per User'),]

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

data = data[complete.cases(data),]

data$scenario_adopt = factor(data$scenario_adopt, 
                             levels=c("Low (2% Adoption Growth)",
                                      "Baseline (4% Adoption Growth)",
                                      "High (6% Adoption Growth)"))

data <- select(data, 
               scenario_adopt, scenario_capacity, strategy_short, grid_type,
               total_annual_energy_demand_kwh,
               demand_carbon_per_kwh, 
               nitrogen_oxide_per_kwh,
               sulpher_dioxide_per_kwh,
               pm10_per_kwh)

data <- data %>%
  group_by(scenario_adopt, scenario_capacity, strategy_short, grid_type) %>%
  summarize(
    energy = round(sum(total_annual_energy_demand_kwh)),
    demand_carbon_per_kwh = round(sum(demand_carbon_per_kwh)),
    nitrogen_oxide_per_kwh = round(sum(nitrogen_oxide_per_kwh)),
    sulpher_dioxide_per_kwh = round(sum(sulpher_dioxide_per_kwh)),
    pm10_per_kwh = round(sum(pm10_per_kwh)),
  )

# totals <- data %>%
#   group_by(scenario_adopt, scenario_capacity, strategy_short) %>%
#   summarize(social_cost = round(
#     (societal_cost)/1e9))
# 
# min_value = min(round(data$societal_cost/ 1e9))
# max_value = max(round(data$societal_cost/ 1e9))
# min_value[min_value > 0] = 0

# colnames(data)[colnames(data) == 'private_cost'] <- 'Private Cost ($USD)'
# colnames(data)[colnames(data) == 'government_cost'] <- 'Government Cost ($USD)'
# colnames(data)[colnames(data) == 'societal_cost'] <- 'Social Cost ($USD)'

data <- data %>% gather(key="metric", value = "value",
                        'demand_carbon_per_kwh', 
                        'nitrogen_oxide_per_kwh',
                        'sulpher_dioxide_per_kwh',
                        'pm10_per_kwh'
)

# data$value = round(data$value/1e9, 3)


ggplot(data, aes(x=variety, y=note, fill=treatment)) + 
  geom_boxplot()


ggplot(data, aes(y=value, x=strategy_short, fill=grid_type)) + 
  geom_bar(stat="identity", position=position_dodge())+
  # geom_text(aes(strategy_short, social_cost, label = social_cost, fill = NULL),
  #           size = 2.5, data = totals, hjust=-.2) +
  coord_flip() +
  scale_fill_manual(values=c("#E1BE6A", "#40B0A6"), name=NULL) +
  theme(legend.position = "bottom",
        axis.text.x = element_text(angle = 45, hjust=1)) +
  labs(title = "Social Cost of Universal Broadband by Technology",
       colour=NULL,
       subtitle = "Reported for all scenarios and capacity per user targets",
       x = NULL, y = "Social Cost (Billions $USD)") +
  # scale_y_continuous(expand = c(0, 0), limits = c(0, max_value+100)) +
  theme(panel.spacing = unit(0.6, "lines")) +
  guides(fill=guide_legend(ncol=3, reverse = TRUE)) +
  facet_wrap(metric~scenario_capacity, scales='free_x')

dir.create(file.path(folder, 'figures'), showWarnings = FALSE)
path = file.path(folder, 'figures', 'social_costs_by_strategy.png')
ggsave(path, units="in", width=8, height=7, dpi=300)
dir.create(file.path(folder, '..', 'reports', 'images', 'CHL'), showWarnings = FALSE)
path = file.path(folder, '..', 'reports', 'images', 'CHL', 'social_costs_by_strategy.png')
ggsave(path, units="in", width=8, height=7, dpi=300)
dev.off()
