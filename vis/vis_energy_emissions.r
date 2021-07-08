###VISUALISE MODEL OUTPUTS###
library(tidyverse)
library(ggpubr)

folder <- dirname(rstudioapi::getSourceEditorContext()$path)

filename = 'emissions_technology_options.csv'
data <- read.csv(file.path(folder, '..', 'results', 'model_results', 'CHL', filename))

names(data)[names(data) == 'GID_0'] <- 'country'

# data$scenario_adopt[grep("high", data$scenario)] = 'High (6% Adoption Growth)'
# data$scenario_adopt[grep("baseline", data$scenario)] = 'Baseline (4% Adoption Growth)'
# data$scenario_adopt[grep("low", data$scenario)] = 'Low (2% Adoption Growth)'
# data <- data[(data$scenario_adopt == 'Baseline (4% Adoption Growth)'),]
data$scenario_adopt[grep("high", data$scenario)] = 'high'
data$scenario_adopt[grep("baseline", data$scenario)] = 'baseline'
data$scenario_adopt[grep("low", data$scenario)] = 'low'
# data <- data[(data$scenario_adopt == 'Baseline (4% Adoption Growth)'),]

data$scenario_capacity[grep("5_5_5", data$scenario)] = '~5 Mbps Per User'
data$scenario_capacity[grep("10_10_10", data$scenario)] = '~10 Mbps Per User'
data$scenario_capacity[grep("20_20_20", data$scenario)] = '~20 Mbps Per User'
# data <- data[(data$scenario_capacity == '~10 Mbps Per User'),]

data$strategy_short = ''
# data$strategy_short[grep("3G_umts_fiber", data$strategy)] = '3G (F)'
# data$strategy_short[grep("3G_umts_wireless", data$strategy)] = '3G (W)'
data$strategy_short[grep("4G_epc_fiber", data$strategy)] = '4G (F)'
data$strategy_short[grep("4G_epc_wireless", data$strategy)] = '4G (W)'
data$strategy_short[grep("5G_nsa_fiber", data$strategy)] = '5G (F)'
data$strategy_short[grep("5G_nsa_wireless", data$strategy)] = '5G (W)'

data$strategy_short = factor(data$strategy_short, levels=c(
                                     # "3G (F)",
                                     "4G (F)",
                                     '5G (F)',
                                     # "3G (W)",
                                     "4G (W)",
                                     '5G (W)'
                                     ))

data$scenario_capacity = factor(data$scenario_capacity,
                                levels=c("~5 Mbps Per User",
                                         "~10 Mbps Per User",
                                         "~20 Mbps Per User"
                                         ))

data = data[complete.cases(data),]

# data$scenario_adopt = factor(data$scenario_adopt, 
#                              levels=c("Low (2% Adoption Growth)",
#                                       "Baseline (4% Adoption Growth)",
#                                       "High (6% Adoption Growth)"))

# data$grid_type = factor(data$grid_type, 
#                         levels=c("off_grid",
#                                       "on_grid"),
#                         labels=c("Diesel",
#                                        "Renewables"))

data <- select(data, 
               scenario_adopt, scenario_capacity, strategy_short, #grid_type,
               total_annual_energy_demand_kwh,
               demand_carbon_per_kwh, 
               nitrogen_oxide_per_kwh,
               sulpher_dioxide_per_kwh,
               pm10_per_kwh)

# data <- data %>%
#   group_by(scenario_adopt, scenario_capacity, strategy_short) %>% #, grid_type
#   summarize(
#     total_annual_energy_demand_kwh = round(sum(total_annual_energy_demand_kwh)),
#     demand_carbon_per_kwh = round(sum(demand_carbon_per_kwh)),
#     nitrogen_oxide_per_kwh = round(sum(nitrogen_oxide_per_kwh)),
#     sulpher_dioxide_per_kwh = round(sum(sulpher_dioxide_per_kwh)),
#     pm10_per_kwh = round(sum(pm10_per_kwh)),
#   )

############
sample <- data %>%
  group_by(scenario_adopt, scenario_capacity, strategy_short) %>% #, grid_type
  summarize(
    value = round(sum(total_annual_energy_demand_kwh)),
    # demand_carbon_per_kwh = round(sum(demand_carbon_per_kwh)),
    # nitrogen_oxide_per_kwh = round(sum(nitrogen_oxide_per_kwh)),
    # sulpher_dioxide_per_kwh = round(sum(sulpher_dioxide_per_kwh)),
    # pm10_per_kwh = round(sum(pm10_per_kwh)),
  )

sample$value = sample$value / 1e6

min_value = min(round(sample$value))
max_value = max(round(sample$value)) + 1
min_value[min_value > 0] = 0

sample = spread(sample, scenario_adopt, value)

totals <- sample %>%
  group_by(scenario_capacity, strategy_short) %>%
  summarize(value2 = round(
    (baseline), 0))

energy = 
  ggplot(sample, 
  aes(x=strategy_short, y=baseline, fill=strategy_short)) + 
  geom_bar(stat="identity", position=position_dodge()) +
  geom_errorbar(data=sample, aes(y = baseline, ymin = low, ymax = high),
                position = position_dodge(width = .9), lwd = 0.5, 
                show.legend = FALSE, width=0.1,  color="#FF0000FF") +
  geom_text(y=0, aes(strategy_short, value2, label = value2, color="#FF0000FF"),
            size = 3, data = totals, vjust=-1, hjust=.5) +
  theme(legend.position = 'none',
        axis.text.x = element_text(angle = 45, hjust=1)) +
  labs(title = "Universal Broadband Energy Demand for Chile 2020-2030",
       fill=NULL,
       subtitle = "Interval bars reflect estimates for low and high adoption scenarios",
       x = NULL, y = "Gigawatt hours (GWh)") +
  scale_y_continuous(expand = c(0, 0), limits = c(0, max_value)) +
  scale_fill_viridis_d() + 
  facet_grid(~scenario_capacity)

############
sample <- data %>%
  group_by(scenario_adopt, scenario_capacity, strategy_short) %>% #, grid_type
  summarize(
    # value = round(sum(total_annual_energy_demand_kwh)),
    value = round(sum(demand_carbon_per_kwh)),
    # nitrogen_oxide_per_kwh = round(sum(nitrogen_oxide_per_kwh)),
    # sulpher_dioxide_per_kwh = round(sum(sulpher_dioxide_per_kwh)),
    # pm10_per_kwh = round(sum(pm10_per_kwh)),
  )

sample$value = sample$value / 1e6

min_value = min(round(sample$value))
max_value = max(round(sample$value)) + 1
min_value[min_value > 0] = 0

sample = spread(sample, scenario_adopt, value)

totals <- sample %>%
  group_by(scenario_capacity, strategy_short) %>%
  summarize(value2 = round(
    (baseline), 0))

carbon_dioxide = ggplot(sample, 
                aes(x=strategy_short, y=baseline, fill=strategy_short)) + 
  geom_bar(stat="identity", position=position_dodge()) +
  geom_errorbar(data=sample, aes(y = baseline, ymin = low, ymax = high),
                position = position_dodge(width = .9), lwd = 0.5, 
                show.legend = FALSE, width=0.1,  color="#FF0000FF") +
  geom_text(y=0, aes(strategy_short, value2, label = value2, color="#FF0000FF"),
            size = 3, data = totals, vjust=-1, hjust=.5) +
  theme(legend.position = 'none',
        axis.text.x = element_text(angle = 45, hjust=1)) +
  labs(title=expression(paste("Universal Broadband Emissions for Chile 2020-2030 (", CO[2], ")")),
       fill=NULL,
       subtitle = "Interval bars reflect estimates for low and high adoption scenarios",
       x=NULL, y=expression(paste("Kilotonnes of ", CO[2])),sep="") + 
  scale_y_continuous(expand = c(0, 0), limits = c(0, max_value)) +
  scale_fill_viridis_d() + 
  facet_grid(~scenario_capacity)

############
sample <- data %>%
  group_by(scenario_adopt, scenario_capacity, strategy_short) %>% #, grid_type
  summarize(
    # value = round(sum(total_annual_energy_demand_kwh)),
    # value = round(sum(demand_carbon_per_kwh)),
    value = round(sum(nitrogen_oxide_per_kwh)),
    # sulpher_dioxide_per_kwh = round(sum(sulpher_dioxide_per_kwh)),
    # pm10_per_kwh = round(sum(pm10_per_kwh)),
  )

sample$value = sample$value / 1e3

min_value = min(round(sample$value))
max_value = max(round(sample$value)) + 1
min_value[min_value > 0] = 0

sample = spread(sample, scenario_adopt, value)

totals <- sample %>%
  group_by(scenario_capacity, strategy_short) %>%
  summarize(value2 = round(baseline, 0))

nitrogen_dioxide = ggplot(sample, 
                        aes(x=strategy_short, y=baseline, fill=strategy_short)) + 
  geom_bar(stat="identity", position=position_dodge()) +
  geom_errorbar(data=sample, aes(y = baseline, ymin = low, ymax = high),
                position = position_dodge(width = .9), lwd = 0.5, 
                show.legend = FALSE, width=0.1,  color="#FF0000FF") +
  geom_text(y=0, aes(strategy_short, value2, label = value2, color="#FF0000FF"),
            size = 3, data = totals, vjust=-1, hjust=.5) +
  theme(legend.position = 'none',
        axis.text.x = element_text(angle = 45, hjust=1)) +
  labs(title=expression(paste("Universal Broadband Emissions for Chile 2020-2030 (", NO[x], ")")),
    # title = "Universal Broadband Emissions for Chile 2020-2030 (Nitrogen Oxides)",
       fill=NULL,
       subtitle = "Interval bars reflect estimates for low and high adoption scenarios",
       x = NULL, y=expression(paste("Tonnes of ", NO[x])), sep="")  +
  scale_y_continuous(expand = c(0, 0), limits = c(0, max_value)) +
  scale_fill_viridis_d() + 
  facet_grid(~scenario_capacity)

############
sample <- data %>%
  group_by(scenario_adopt, scenario_capacity, strategy_short) %>% #, grid_type
  summarize(
    # value = round(sum(total_annual_energy_demand_kwh)),
    # value = round(sum(demand_carbon_per_kwh)),
    # value = round(sum(nitrogen_oxide_per_kwh)),
    value = round(sum(sulpher_dioxide_per_kwh)),
    # pm10_per_kwh = round(sum(pm10_per_kwh)),
  )

sample$value = sample$value / 1e6

min_value = min(round(sample$value))
max_value = max(round(sample$value)) + 1
min_value[min_value > 0] = 0

sample = spread(sample, scenario_adopt, value)

totals <- sample %>%
  group_by(scenario_capacity, strategy_short) %>%
  summarize(value2 = round(baseline, 1))

suplher_dioxide = ggplot(sample, 
                          aes(x=strategy_short, y=baseline, fill=strategy_short)) + 
  geom_bar(stat="identity", position=position_dodge()) +
  geom_errorbar(data=sample, aes(y = baseline, ymin = low, ymax = high),
                position = position_dodge(width = .9), lwd = 0.5, 
                show.legend = FALSE, width=0.1,  color="#FF0000FF") +
  geom_text(y=0, aes(strategy_short, value2, label = value2, color="#FF0000FF"),
            size = 3, data = totals, vjust=-1, hjust=.5) +
  theme(legend.position = 'none',
        axis.text.x = element_text(angle = 45, hjust=1)) +
  labs(title=expression(paste("Universal Broadband Emissions for Chile 2020-2030 (", SO[x], ")")),
    # title = "Universal Broadband Emissions for Chile 2020-2030 (Sulphur Oxides)",
       fill=NULL,
       subtitle = "Interval bars reflect estimates for low and high adoption scenarios",
       x = NULL, y=expression(paste("Tonnes of ", SO[x])), sep="") +
  scale_y_continuous(expand = c(0, 0), limits = c(0, max_value)) +
  scale_fill_viridis_d() + 
  facet_grid(~scenario_capacity)

############

sample <- data %>%
  group_by(scenario_adopt, scenario_capacity, strategy_short) %>% #, grid_type
  summarize(
    # value = round(sum(total_annual_energy_demand_kwh)),
    # value = round(sum(demand_carbon_per_kwh)),
    # value = round(sum(nitrogen_oxide_per_kwh)),
    # value = round(sum(sulpher_dioxide_per_kwh)),
    value = round(sum(pm10_per_kwh)),
  )

sample$value = sample$value / 1e3

min_value = min(round(sample$value))
max_value = max(round(sample$value)) + 1
min_value[min_value > 0] = 0

sample = spread(sample, scenario_adopt, value)

totals <- sample %>%
  group_by(scenario_capacity, strategy_short) %>%
  summarize(value2 = round(baseline, 0))

pm10 = ggplot(sample, 
                         aes(x=strategy_short, y=baseline, fill=strategy_short)) + 
  geom_bar(stat="identity", position=position_dodge()) +
  geom_errorbar(data=sample, aes(y = baseline, ymin = low, ymax = high),
                position = position_dodge(width = .9), lwd = 0.5, 
                show.legend = FALSE, width=0.1,  color="#FF0000FF") +
  geom_text(y=0, aes(strategy_short, value2, label = value2, color="#FF0000FF"),
            size = 3, data = totals, vjust=-1, hjust=.5) +
  theme(legend.position = 'none',
        axis.text.x = element_text(angle = 45, hjust=1)) +
  labs(title=expression(paste("Universal Broadband Emissions for Chile 2020-2030 (", PM[10], ")")),
       fill=NULL,
       subtitle = "Interval bars reflect estimates for low and high adoption scenarios",
       x = NULL, y=expression(paste("Tonnes of ", PM[10])), sep="") + #y ="Tonnes of PM10") +
  scale_y_continuous(expand = c(0, 0), limits = c(0, max_value)) +
  scale_fill_viridis_d() + 
  facet_grid(~scenario_capacity)

############
ggarrange(
  energy, 
  carbon_dioxide, 
  labels = c("A", "B"),
  ncol = 1, nrow = 2)

dir.create(file.path(folder, 'figures'), showWarnings = FALSE)
path = file.path(folder, 'figures', 'energy_emissions.png')
ggsave(path, units="in", width=8, height=7, dpi=300)
dir.create(file.path(folder, '..', 'reports', 'images', 'CHL'), showWarnings = FALSE)
path = file.path(folder, '..', 'reports', 'images', 'CHL', 'energy_emissions.png')
ggsave(path, units="in", width=8, height=7, dpi=300)
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