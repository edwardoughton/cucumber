###VISUALISE MODEL OUTPUTS###
library(tidyverse)
library(ggpubr)

folder <- dirname(rstudioapi::getSourceEditorContext()$path)

filename = 'power_emissions_power_options.csv'
data <- read.csv(file.path(folder, '..', 'results', 'global_results', filename))

data$GID_0 = NULL

names(data)[names(data) == 'GID_0'] <- 'country'

data$scenario_adopt = ''
data$scenario_adopt[grep("high", data$scenario)] = 'high'
data$scenario_adopt[grep("baseline", data$scenario)] = 'baseline'
data$scenario_adopt[grep("low", data$scenario)] = 'low'

data$scenario_capacity = ''
data$scenario_capacity[grep("50_50_50", data$scenario)] = '50 GB/Month'
data <- data[(data$scenario_capacity == '50 GB/Month'),]

data$strategy_short = ''
data$strategy_short[grep("4G_epc_fiber", data$strategy)] = '4G (F)'
data$strategy_short[grep("4G_epc_wireless", data$strategy)] = '4G (W)'
data$strategy_short[grep("5G_nsa_fiber", data$strategy)] = '5G (F)'
data$strategy_short[grep("5G_nsa_wireless", data$strategy)] = '5G (W)'

data$strategy_power = ''
data$strategy_power[grep("baseline_baseline_baseline_baseline_baseline", data$strategy)] = 'Baseline'
data$strategy_power[grep("baseline_baseline_baseline_baseline_renewable", data$strategy)] = 'Renewables'

data$strategy_short = factor(data$strategy_short, levels=c(
  "4G (F)",
  '5G (F)',
  "4G (W)",
  '5G (W)'
))

data = data[complete.cases(data),]

data = data %>%
  group_by(scenario_adopt, scenario_capacity, strategy_short, strategy_power) %>%
  summarise(
    # total_energy_annual_demand_kwh = sum(total_energy_annual_demand_kwh),
    total_demand_carbon_tonnes = sum(total_demand_carbon_tonnes),
    total_nitrogen_oxide_tonnes = sum(total_nitrogen_oxide_tonnes),
    total_sulpher_dioxide_tonnes = sum(total_sulpher_dioxide_tonnes),
    total_pm10_tonnes = sum(total_pm10_tonnes)
  )

############

data$total_demand_carbon_tonnes = data$total_demand_carbon_tonnes / 1e3
data$total_nitrogen_oxide_tonnes = data$total_nitrogen_oxide_tonnes / 1e3
data$total_sulpher_dioxide_tonnes = data$total_sulpher_dioxide_tonnes / 1e3
data$total_pm10_tonnes = data$total_pm10_tonnes / 1e3

long <- data %>% 
  gather(type, value, -c(
    scenario_adopt, scenario_capacity, strategy_short, strategy_power))

long$type = factor(long$type,
                   levels=c("total_demand_carbon_tonnes",
                            "total_nitrogen_oxide_tonnes",
                            "total_sulpher_dioxide_tonnes",
                            "total_pm10_tonnes"
                   ),
                   labels=c(
                     expression(paste("Megatonnes of ", CO[2])),
                     expression(paste("Kilotonnes of ", NO[x])),
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
       subtitle = "For 50 GB/Month per user with interval bars reflecting low and high adoption scenarios",
       x=NULL, y='') +
  scale_y_continuous(expand = c(0, 0)) +
  scale_fill_viridis_d() +
  facet_wrap(~type, scales = "free", labeller=label_parsed)

path = file.path(folder, 'figures', 'global', 'power_strategies.png')
ggsave(path, units="in", width=8, height=6, dpi=300)
path = file.path(folder, '..', 'reports', 'images', 'global', 'power_strategies.png')
ggsave(path, units="in", width=8, height=6, dpi=300)
while (!is.null(dev.list()))  dev.off()
