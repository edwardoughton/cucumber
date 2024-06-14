###VISUALISE MODEL OUTPUTS###
library(tidyverse)
library(ggpubr)

folder <- dirname(rstudioapi::getSourceEditorContext()$path)
iso3 = 'COL'

filename = 'emissions_technology_options.csv'
data <- read.csv(file.path(folder, '..', 'results', 'model_results', iso3, filename))

names(data)[names(data) == 'GID_0'] <- 'country'

data$scenario_adopt[grep("high", data$scenario)] = 'high'
data$scenario_adopt[grep("baseline", data$scenario)] = 'baseline'
data$scenario_adopt[grep("low", data$scenario)] = 'low'

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

data = data[complete.cases(data),]

data <- select(data, 
               scenario_adopt, scenario_capacity, strategy_short, #grid_type,
               total_energy_annual_demand_kwh,
               total_demand_carbon_tonnes, 
               total_nitrogen_oxide_tonnes,
               total_sulpher_dioxide_tonnes,
               total_pm10_tonnes)

data = data %>% 
  group_by(scenario_adopt, scenario_capacity, strategy_short) %>% 
  summarise(
    total_energy_annual_demand_kwh = sum(total_energy_annual_demand_kwh),
    total_demand_carbon_tonnes = sum(total_demand_carbon_tonnes),
    total_nitrogen_oxide_tonnes = sum(total_nitrogen_oxide_tonnes),
    total_sulpher_dioxide_tonnes = sum(total_sulpher_dioxide_tonnes),
    total_pm10_tonnes = sum(total_pm10_tonnes)
    )

############
sample <- data %>%
  group_by(scenario_adopt, scenario_capacity, strategy_short) %>% #, grid_type
  summarize(
    value = round(sum(total_energy_annual_demand_kwh)),
  )

sample$value = sample$value / 1e9

min_value = min(round(sample$value))
max_value = max(round(sample$value)) 
min_value[min_value > 0] = 0

sample = spread(sample, scenario_adopt, value)

totals <- sample %>%
  group_by(scenario_capacity, strategy_short) %>%
  summarize(value2 = round(
    (baseline), 1))

energy = 
  ggplot(sample, 
  aes(x=strategy_short, y=baseline, fill=strategy_short)) + 
  geom_bar(stat="identity", position=position_dodge()) +
  geom_errorbar(data=sample, aes(y = baseline, ymin = low, ymax = high),
                position = position_dodge(width = .9), lwd = 0.5, 
                show.legend = FALSE, width=0.1,  color="#FF0000FF") +
  geom_text(y=0, aes(strategy_short, value2, label = value2, color="#FF0000FF"),
            size = 3, data = totals, vjust=-.2, hjust=.5) +
  theme(legend.position = 'none',
        axis.text.x = element_text(angle = 45, hjust=1)) +
  labs(title = "Total Universal Broadband Energy Demand for Colombia over 2023-2030",
       fill=NULL,
       subtitle = "Interval bars reflect estimates for low and high adoption scenarios",
       x = NULL, y = "Terawatt hours (TWh)") +
  scale_y_continuous(expand = c(0, 0), limits = c(0, max_value)) +
  scale_fill_viridis_d() + 
  facet_grid(~scenario_capacity)

############
sample <- data %>%
  group_by(scenario_adopt, scenario_capacity, strategy_short) %>% #, grid_type
  summarize(
    value = round(sum(total_demand_carbon_tonnes)),
  )

sample$value = sample$value / 1e3

min_value = min(round(sample$value))
max_value = max(round(sample$value)) + 5
min_value[min_value > 0] = 0

sample = spread(sample, scenario_adopt, value)

totals <- sample %>%
  group_by(scenario_capacity, strategy_short) %>%
  summarize(value2 = round(
    (baseline), 1))

carbon_dioxide = ggplot(sample, 
                aes(x=strategy_short, y=baseline, fill=strategy_short)) + 
  geom_bar(stat="identity", position=position_dodge()) +
  geom_errorbar(data=sample, aes(y = baseline, ymin = low, ymax = high),
                position = position_dodge(width = .9), lwd = 0.5, 
                show.legend = FALSE, width=0.1,  color="#FF0000FF") +
  geom_text(y=0, aes(strategy_short, value2, label = value2, color="#FF0000FF"),
            size = 3, data = totals, vjust=-.2, hjust=.5) +
  theme(legend.position = 'none',
        axis.text.x = element_text(angle = 45, hjust=1)) +
  labs(title=expression(paste("Universal Broadband Emissions for Colombia 2023-2030 (", CO[2], ")")),
       fill=NULL,
       subtitle = "Interval bars reflect estimates for low and high adoption scenarios",
       x=NULL, y=expression(paste("Kilotonnes of ", CO[2])),sep="") + 
  scale_y_continuous(expand = c(0, 0), limits = c(0, max_value)) +
  scale_fill_viridis_d() + 
  facet_grid(~scenario_capacity)

dir.create(file.path(folder, 'report_data'), showWarnings = FALSE)
filename = 'technology_emissions_colombia_2.18.csv'
path = file.path(folder, 'report_data', filename)
write.csv(sample, path)

############
sample <- data %>%
  group_by(scenario_adopt, scenario_capacity, strategy_short) %>% #, grid_type
  summarize(
    value = round(sum(total_nitrogen_oxide_tonnes)),
  )

sample$value = sample$value #/ 1e3

min_value = min(round(sample$value))
max_value = max(round(sample$value)) + 1
min_value[min_value > 0] = 0

sample = spread(sample, scenario_adopt, value)

totals <- sample %>%
  group_by(scenario_capacity, strategy_short) %>%
  summarize(value2 = round(baseline, 1))

nitrogen_dioxide = ggplot(sample, 
                        aes(x=strategy_short, y=baseline, fill=strategy_short)) + 
  geom_bar(stat="identity", position=position_dodge()) +
  geom_errorbar(data=sample, aes(y = baseline, ymin = low, ymax = high),
                position = position_dodge(width = .9), lwd = 0.5, 
                show.legend = FALSE, width=0.1,  color="#FF0000FF") +
  geom_text(y=0, aes(strategy_short, value2, label = value2, color="#FF0000FF"),
            size = 3, data = totals, vjust=-.5, hjust=.5) +
  theme(legend.position = 'none',
        axis.text.x = element_text(angle = 45, hjust=1)) +
  labs(title=expression(paste("Universal Broadband Emissions for Colombia 2023-2030 (", NO[x], ")")),
    # title = "Universal Broadband Emissions for Colombia 2020-2030 (Nitrogen Oxides)",
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
    value = round(sum(total_sulpher_dioxide_tonnes)),
  )

sample$value = sample$value / 1e3

min_value = min(round(sample$value))
max_value = max(round(sample$value)) + .5
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
            size = 3, data = totals, vjust=-.5, hjust=.5) +
  theme(legend.position = 'none',
        axis.text.x = element_text(angle = 45, hjust=1)) +
  labs(title=expression(paste("Universal Broadband Emissions for Colombia 2023-2030 (", SO[x], ")")),
    # title = "Universal Broadband Emissions for Colombia 2020-2030 (Sulphur Oxides)",
       fill=NULL,
       subtitle = "Interval bars reflect estimates for low and high adoption scenarios",
       x = NULL, y=expression(paste("Kilotonnes of ", SO[x])), sep="") +
  scale_y_continuous(expand = c(0, 0), limits = c(0, max_value)) +
  scale_fill_viridis_d() + 
  facet_grid(~scenario_capacity)

############

sample <- data %>%
  group_by(scenario_adopt, scenario_capacity, strategy_short) %>% #, grid_type
  summarize(
    value = round(sum(total_pm10_tonnes)),
  )

sample$value = sample$value / 1e3

min_value = min(round(sample$value))
max_value = max(round(sample$value)) + .5
min_value[min_value > 0] = 0

sample = spread(sample, scenario_adopt, value)

totals <- sample %>%
  group_by(scenario_capacity, strategy_short) %>%
  summarize(value2 = round(baseline, 2))

pm10 = ggplot(sample, 
                         aes(x=strategy_short, y=baseline, fill=strategy_short)) + 
  geom_bar(stat="identity", position=position_dodge()) +
  geom_errorbar(data=sample, aes(y = baseline, ymin = low, ymax = high),
                position = position_dodge(width = .9), lwd = 0.5, 
                show.legend = FALSE, width=0.1,  color="#FF0000FF") +
  geom_text(y=0, aes(strategy_short, value2, label = value2, color="#FF0000FF"),
            size = 3, data = totals, vjust=-.5, hjust=.5) +
  theme(legend.position = 'none',
        axis.text.x = element_text(angle = 45, hjust=1)) +
  labs(title=expression(paste("Universal Broadband Emissions for Colombia 2023-2030 (", PM[10], ")")),
       fill=NULL,
       subtitle = "Interval bars reflect estimates for low and high adoption scenarios",
       x = NULL, y=expression(paste("Kilotonnes of ", PM[10])), sep="") + #y ="Tonnes of PM10") +
  scale_y_continuous(expand = c(0, 0), limits = c(0, max_value)) +
  scale_fill_viridis_d() + 
  facet_grid(~scenario_capacity)

############
ggarrange(
  energy, 
  carbon_dioxide, 
  labels = c("A", "B"),
  ncol = 1, nrow = 2)

dir.create(file.path(folder, 'figures', iso3), showWarnings = FALSE)
path = file.path(folder, 'figures', iso3, 'energy_emissions.png')
ggsave(path, units="in", width=8, height=7, dpi=300)
# dir.create(file.path(folder, '..', 'reports', 'images', 'CHL'), showWarnings = FALSE)
# path = file.path(folder, '..', 'reports', 'images', 'CHL', 'energy_emissions.png')
# ggsave(path, units="in", width=8, height=7, dpi=300)
dev.off()

ggarrange(
  nitrogen_dioxide, 
  suplher_dioxide,
  pm10, 
  labels = c("A", "B", "C"),
  ncol = 1, nrow = 3)

dir.create(file.path(folder, 'figures', iso3), showWarnings = FALSE)
path = file.path(folder, 'figures', iso3, 'health_emissions.png')
ggsave(path, units="in", width=8, height=10, dpi=300)
# dir.create(file.path(folder, '..', 'reports', 'images', 'CHL'), showWarnings = FALSE)
# path = file.path(folder, '..', 'reports', 'images', 'CHL', 'health_emissions.png')
# ggsave(path, units="in", width=8, height=10, dpi=300)
dev.off()