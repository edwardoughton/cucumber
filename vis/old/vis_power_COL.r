###VISUALISE MODEL OUTPUTS###
library(tidyverse)
library(ggpubr)

folder <- dirname(rstudioapi::getSourceEditorContext()$path)

filename = 'power_emissions_power_options.csv'
data <- read.csv(file.path(folder, '..', 'results', 'model_results', 'COL', filename))

names(data)[names(data) == 'GID_0'] <- 'country'

data$scenario_adopt = ''
data$scenario_adopt[grep("high", data$scenario)] = 'high'
data$scenario_adopt[grep("baseline", data$scenario)] = 'baseline'
data$scenario_adopt[grep("low", data$scenario)] = 'low'

data$scenario_capacity = ''
# data$scenario_capacity[grep("5_5_5", data$scenario)] = '~5 Mbps Per User'
data$scenario_capacity[grep("10_10_10", data$scenario)] = '~10 Mbps Per User'
# data$scenario_capacity[grep("20_20_20", data$scenario)] = '~20 Mbps Per User'
data <- data[(data$scenario_capacity == '~10 Mbps Per User'),]
data = data[(data$scenario_capacity == '~10 Mbps Per User'),]

data$strategy_short = ''
# data$strategy_short[grep("3G_umts_fiber", data$strategy)] = '3G (F)'
# data$strategy_short[grep("3G_umts_wireless", data$strategy)] = '3G (W)'
data$strategy_short[grep("4G_epc_fiber", data$strategy)] = '4G (F)'
data$strategy_short[grep("4G_epc_wireless", data$strategy)] = '4G (W)'
data$strategy_short[grep("5G_nsa_fiber", data$strategy)] = '5G (F)'
data$strategy_short[grep("5G_nsa_wireless", data$strategy)] = '5G (W)'

data$strategy_power = ''
data$strategy_power[grep("baseline_baseline_baseline_baseline_baseline", data$strategy)] = 'Baseline'
data$strategy_power[grep("baseline_baseline_baseline_baseline_renewable", data$strategy)] = 'Renewables'

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

data <- select(data, scenario_adopt, scenario_capacity, 
               strategy_short, strategy_power,
               # total_energy_annual_demand_kwh,
               demand_carbon_per_kwh, 
               nitrogen_oxide_per_kwh,
               sulpher_dioxide_per_kwh,
               pm10_per_kwh)

data = data %>% 
  group_by(scenario_adopt, scenario_capacity, strategy_short, strategy_power) %>% 
  summarise(
    # total_energy_annual_demand_kwh = sum(total_energy_annual_demand_kwh),
    demand_carbon_per_kwh = sum(demand_carbon_per_kwh),
    nitrogen_oxide_per_kwh = sum(nitrogen_oxide_per_kwh),
    sulpher_dioxide_per_kwh = sum(sulpher_dioxide_per_kwh),
    pm10_per_kwh = sum(pm10_per_kwh)
  )

############

data$demand_carbon_per_kwh = data$demand_carbon_per_kwh / 1e6
data$nitrogen_oxide_per_kwh = data$nitrogen_oxide_per_kwh / 1e3
data$sulpher_dioxide_per_kwh = data$sulpher_dioxide_per_kwh / 1e6
data$pm10_per_kwh = data$pm10_per_kwh / 1e6

long <- data %>% gather(type, value, -c(scenario_adopt, scenario_capacity, strategy_short, strategy_power))

long$type = factor(long$type,
                                levels=c("demand_carbon_per_kwh",
                                         "nitrogen_oxide_per_kwh",
                                         "sulpher_dioxide_per_kwh",
                                         "pm10_per_kwh"
                                ),
                                labels=c(
                                  expression(paste("Kilotonnes of ", CO[2])),
                                  expression(paste("Tonnes of ", NO[x])),
                                  expression(paste("Kilotonnes of ", SO[x])),
                                  expression(paste("Kilotonnes of ", PM[10]))
                                ))

long = spread(long, scenario_adopt, value)

ggplot(long, aes(x=strategy_short, y=baseline, fill=strategy_power)) + 
  geom_bar(stat="identity", position=position_dodge()) +
  geom_errorbar(data=long, aes(y = baseline, ymin = low, ymax = high),
                position = position_dodge(width = .9), lwd = 0.5, 
                show.legend = FALSE, width=0.1,  color="#FF0000FF") +
  theme(legend.position = 'bottom',
        axis.text.x = element_text(angle = 45, hjust=1)) +
  labs(title="Impact of Shifting Off-Grid Diesel Generators to Renewable Site Power",
       fill=NULL,
       subtitle = "Using a ~10 Mbps per user target with interval bars reflecting low and high adoption scenarios",
       x=NULL, y='') + 
  scale_y_continuous(expand = c(0, 0)) +
  scale_fill_viridis_d() + 
  facet_wrap(~type, scales = "free", labeller=label_parsed)

path = file.path(folder, 'figures', iso3, 'power_strategies.png')
ggsave(path, units="in", width=8, height=6, dpi=300)
path = file.path(folder, '..', 'reports', 'images', 'COL', 'power_strategies.png')
ggsave(path, units="in", width=8, height=6, dpi=300)
dev.off()