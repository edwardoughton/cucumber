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
                                levels=c("~5 Mbps Per User",
                                         "~10 Mbps Per User",
                                         "~20 Mbps Per User"
                                         ))

data = data[complete.cases(data),]

data$scenario_adopt = factor(data$scenario_adopt, 
                             levels=c("Low (2% Adoption Growth)",
                                      "Baseline (4% Adoption Growth)",
                                      "High (6% Adoption Growth)"))

data$grid_type = factor(data$grid_type, 
                        levels=c("off_grid",
                                      "on_grid"),
                        labels=c("Diesel",
                                       "Renewables"))

data <- select(data, 
               scenario_adopt, scenario_capacity, strategy_short, grid_type,
               total_annual_energy_demand_kwh,
               demand_carbon_per_kwh, 
               nitrogen_oxide_per_kwh,
               sulpher_dioxide_per_kwh,
               pm10_per_kwh)

############
min_value = min(round(data$total_annual_energy_demand_kwh/ 1e6))
max_value = max(round(data$total_annual_energy_demand_kwh/ 1e6))
min_value[min_value > 0] = 0

energy = ggplot(data, 
 aes(x=strategy_short, y=(total_annual_energy_demand_kwh/1e6), 
     fill=grid_type)) + 
  geom_boxplot(outlier.shape = NA) +
  theme(legend.position = "right",
        axis.text.x = element_text(angle = 45, hjust=1)) +
  labs(title = "Universal Broadband Energy Demand by Technology",
       fill=NULL,
       subtitle = "Reported for all scenarios and capacity per user targets",
       x = NULL, y = "Million kWh") +
  scale_y_continuous(expand = c(0, 0), limits = c(0, max_value-48)) +
  facet_grid(~scenario_capacity)

############
min_value = min(round(data$demand_carbon_per_kwh/ 1e6))
max_value = max(round(data$demand_carbon_per_kwh/ 1e6))
min_value[min_value > 0] = 0

carbon_dioxide = ggplot(data, 
                aes(x=strategy_short, y=(demand_carbon_per_kwh/1e6), 
                    fill=grid_type)) + 
  geom_boxplot(outlier.shape = NA) +
  theme(legend.position = "right",
        axis.text.x = element_text(angle = 45, hjust=1)) +
  labs(title = "Universal Broadband Carbon Emissions by Technology",
       fill=NULL,
       subtitle = "Reported for all scenarios and capacity per user targets",
       x = NULL, y = "Kilotonnes of Carbon") +
  scale_y_continuous(expand = c(0, 0), limits = c(0, max_value-24)) +
  facet_grid(~scenario_capacity)

############
min_value = min(round(data$nitrogen_oxide_per_kwh/1e3))
max_value = max(round(data$nitrogen_oxide_per_kwh/1e3))
min_value[min_value > 0] = 0

nitrogen_dioxide = ggplot(data, aes(x=strategy_short, y=(nitrogen_oxide_per_kwh/1e3), 
       fill=grid_type)) + 
  geom_boxplot(outlier.shape = NA) +
  theme(legend.position = "right",
        axis.text.x = element_text(angle = 45, hjust=1)) +
  labs(title = "Universal Broadband Nitrogen Dioxide Emissions by Technology",
       fill=NULL,
       subtitle = "Reported for all scenarios and capacity per user targets",
       x = NULL, y = "Tonnes of Nitrogen Dioxide") +
  scale_y_continuous(expand = c(0, 0), limits = c(0, max_value-3.8)) +
  facet_grid(~scenario_capacity)

############
min_value = min(round(data$sulpher_dioxide_per_kwh/1e3))
max_value = max(round(data$sulpher_dioxide_per_kwh/1e3))
min_value[min_value > 0] = 0

suplher_dioxide = ggplot(data, 
                 aes(x=strategy_short, y=(sulpher_dioxide_per_kwh/1e3), 
                 fill=grid_type)) + 
  geom_boxplot(outlier.shape = NA) +
  theme(legend.position = "right",
        axis.text.x = element_text(angle = 45, hjust=1)) +
  labs(title = "Universal Broadband Sulphur Dioxide Emissions by Technology",
       fill=NULL,
       subtitle = "Reported for all scenarios and capacity per user targets",
       x = NULL, y = "Tonnes of Sulphur Dioxide") +
  scale_y_continuous(expand = c(0, 0), limits = c(0, max_value-335)) +
  facet_grid(~scenario_capacity)

############
min_value = min(round(data$pm10_per_kwh/1e3))
max_value = max(round(data$pm10_per_kwh/1e3))
min_value[min_value > 0] = 0

pm10 = ggplot(data, 
                         aes(x=strategy_short, y=(pm10_per_kwh/1e3), 
                             fill=grid_type)) + 
  geom_boxplot(outlier.shape = NA) +
  theme(legend.position = "right",
        axis.text.x = element_text(angle = 45, hjust=1)) +
  labs(title = "Universal Broadband PM10 Emissions by Technology",
       fill=NULL,
       subtitle = "Reported for all scenarios and capacity per user targets",
       x = NULL, y = "Tonnes of PM10") +
  scale_y_continuous(expand = c(0, 0), limits = c(0, max_value-97)) +
  facet_grid(~scenario_capacity)

############
ggarrange(
  energy, 
  carbon_dioxide, 
  labels = c("A", "B"),
  ncol = 1, nrow = 2)

dir.create(file.path(folder, 'figures'), showWarnings = FALSE)
path = file.path(folder, 'figures', 'energy_emissions.png')
ggsave(path, units="in", width=8, height=8, dpi=300)
dir.create(file.path(folder, '..', 'reports', 'images', 'CHL'), showWarnings = FALSE)
path = file.path(folder, '..', 'reports', 'images', 'CHL', 'energy_emissions.png')
ggsave(path, units="in", width=8, height=8, dpi=300)
dev.off()

ggarrange(
  nitrogen_dioxide, 
  suplher_dioxide,
  pm10, 
  labels = c("A", "B", "C"),
  ncol = 1, nrow = 3)

dir.create(file.path(folder, 'figures'), showWarnings = FALSE)
path = file.path(folder, 'figures', 'health_emissions.png')
ggsave(path, units="in", width=8, height=10, dpi=300)
dir.create(file.path(folder, '..', 'reports', 'images', 'CHL'), showWarnings = FALSE)
path = file.path(folder, '..', 'reports', 'images', 'CHL', 'health_emissions.png')
ggsave(path, units="in", width=8, height=10, dpi=300)
dev.off()