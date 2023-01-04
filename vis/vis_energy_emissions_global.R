###VISUALISE MODEL OUTPUTS###
library(tidyverse)
library(ggpubr)

folder <- dirname(rstudioapi::getSourceEditorContext()$path)

filename = 'emissions_technology_options.csv'
data <- read.csv(file.path(folder, '..', 'results', 'global_results', filename))

data$GID_0 = NULL

data = data %>%
  group_by(scenario, strategy, grid_type) %>%
  summarise(
    total_energy_annual_demand_kwh = sum(total_energy_annual_demand_kwh),
    total_demand_carbon_tonnes = sum(total_demand_carbon_tonnes),
    total_nitrogen_oxide_tonnes = sum(total_nitrogen_oxide_tonnes),
    total_sulpher_dioxide_tonnes = sum(total_sulpher_dioxide_tonnes),
    total_pm10_tonnes = sum(total_pm10_tonnes),
  )


# data$scenario_adopt[grep("high", data$scenario)] = 'High (6% Adoption Growth)'
# data$scenario_adopt[grep("baseline", data$scenario)] = 'Baseline (4% Adoption Growth)'
# data$scenario_adopt[grep("low", data$scenario)] = 'Low (2% Adoption Growth)'
# data <- data[(data$scenario_adopt == 'Baseline (4% Adoption Growth)'),]
data$scenario_adopt = ''
data$scenario_adopt[grep("high", data$scenario)] = 'high'
data$scenario_adopt[grep("baseline", data$scenario)] = 'baseline'
data$scenario_adopt[grep("low", data$scenario)] = 'low'
# data <- data[(data$scenario_adopt == 'Baseline (4% Adoption Growth)'),]

data$scenario_capacity = ''
data$scenario_capacity[grep("25_25_25", data$scenario)] = '25 GB/Month'
data$scenario_capacity[grep("50_50_50", data$scenario)] = '50 GB/Month'
data$scenario_capacity[grep("100_100_100", data$scenario)] = '100 GB/Month'
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
                                levels=c('25 GB/Month',
                                         '50 GB/Month',
                                         '100 GB/Month'
                                         ))

data = data[complete.cases(data),]

data <- select(data,
               scenario_adopt, scenario_capacity, strategy_short, grid_type,
               total_energy_annual_demand_kwh,
               total_demand_carbon_tonnes,
               total_nitrogen_oxide_tonnes,
               total_sulpher_dioxide_tonnes,
               total_pm10_tonnes)

# data = data %>%
#   group_by(scenario_adopt, scenario_capacity, strategy_short, grid_type) %>%
#   summarise(
#     total_energy_annual_demand_kwh = sum(total_energy_annual_demand_kwh),
#     total_demand_carbon_tonnes = sum(total_demand_carbon_tonnes),
#     total_nitrogen_oxide_tonnes = sum(total_nitrogen_oxide_tonnes),
#     total_sulpher_dioxide_tonnes = sum(total_sulpher_dioxide_tonnes),
#     total_pm10_tonnes = sum(total_pm10_tonnes)
#     )

############
sample <- data %>%
  group_by(scenario_adopt, scenario_capacity, strategy_short) %>% #, grid_type
  summarize(
    value = round(sum(total_energy_annual_demand_kwh)),
  )

sample$value = sample$value / 1e9

min_value = min(round(sample$value))
max_value = max(round(sample$value)) + 1
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
            size = 3, data = totals, vjust=-.5, hjust=.5) +
  theme(legend.position = 'none',
        axis.text.x = element_text(angle = 45, hjust=1)) +
  labs(title = "Cumulative Cell Site Energy Demand over 2020-2030",
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

sample$value = sample$value / 1e6

min_value = min(round(sample$value))
max_value = max(round(sample$value)) + 1
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
            size = 3, data = totals, vjust=-.5, hjust=.5) +
  theme(legend.position = 'none',
        axis.text.x = element_text(angle = 45, hjust=1)) +
       labs(title=expression(paste("Cumulative Cell Site Emissions over 2020-2030 (", CO[2], ")")),
       fill=NULL,
       subtitle = "Interval bars reflect estimates for low and high adoption scenarios",
       x=NULL, y=expression(paste("Megatonnes of ", CO[2])),sep="") +
  scale_y_continuous(expand = c(0, 0), limits = c(0, max_value)) +
  scale_fill_viridis_d() +
  facet_grid(~scenario_capacity)

# dir.create(file.path(folder, 'figures', iso3), showWarnings = FALSE)
# path = file.path(folder, 'figures', iso3, 'carbon.png')
# ggsave(path, units="in", width=8, height=4, dpi=300)
# dir.create(file.path(folder, '..', 'reports', 'images', iso3), showWarnings = FALSE)
# path = file.path(folder, '..', 'reports', 'images', iso3, 'carbon.png')
# ggsave(path, units="in", width=8, height=4, dpi=300)
# while (!is.null(dev.list()))  dev.off()

############
sample <- data %>%
  group_by(scenario_adopt, scenario_capacity, strategy_short) %>% #, grid_type
  summarize(
    value = round(sum(total_nitrogen_oxide_tonnes)),
  )

sample$value = sample$value / 1e3

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
  labs(title=expression(paste("Cumulative Cell Site Emissions over 2020-2030 (", NO[x], ")")),
    # title = "Cell Site Emissions for Colombia 2020-2030 (Nitrogen Oxides)",
       fill=NULL,
       subtitle = "Interval bars reflect estimates for low and high adoption scenarios for",
       x = NULL, y=expression(paste("Kilotonnes of ", NO[x])), sep="")  +
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
            size = 3, data = totals, vjust=-.5, hjust=.5) +
  theme(legend.position = 'none',
        axis.text.x = element_text(angle = 45, hjust=1)) +
  labs(title=expression(paste("Cumulative Cell Site Emissions over 2020-2030 (", SO[x], ")")),
    # title = "Cell Site Emissions for Colombia 2020-2030 (Sulphur Oxides)",
       fill=NULL,
       subtitle = "Interval bars reflect estimates for low and high adoption scenarios for",
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
max_value = max(round(sample$value)) + 1
min_value[min_value > 0] = 0

sample = spread(sample, scenario_adopt, value)

totals <- sample %>%
  group_by(scenario_capacity, strategy_short) %>%
  summarize(value2 = round(baseline, 1))

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
  labs(title=expression(paste("Cumulative Cell Site Emissions over 2020-2030 (", PM[10], ")")),
       fill=NULL,
       subtitle = "Interval bars reflect estimates for low and high adoption scenarios for",
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

dir.create(file.path(folder, 'figures', 'global'), showWarnings = FALSE)
path = file.path(folder, 'figures', 'global', 'energy_emissions.png')
ggsave(path, units="in", width=8, height=7, dpi=300)
dir.create(file.path(folder, '..', 'reports', 'images', 'global'), showWarnings = FALSE)
path = file.path(folder, '..', 'reports', 'images', 'global', 'energy_emissions.png')
ggsave(path, units="in", width=8, height=7, dpi=300)
while (!is.null(dev.list()))  dev.off()

ggarrange(
  nitrogen_dioxide,
  suplher_dioxide,
  pm10,
  labels = c("A", "B", "C"),
  ncol = 1, nrow = 3)

dir.create(file.path(folder, 'figures', 'global'), showWarnings = FALSE)
path = file.path(folder, 'figures', 'global', 'health_emissions.png')
ggsave(path, units="in", width=8, height=10, dpi=300)
dir.create(file.path(folder, '..', 'reports', 'images', 'global'), showWarnings = FALSE)
path = file.path(folder, '..', 'reports', 'images', 'global', 'health_emissions.png')
ggsave(path, units="in", width=8, height=10, dpi=300)
while (!is.null(dev.list()))  dev.off()

##########################################################################

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
# data$scenario_capacity[grep("25_25_25", data$scenario)] = '25 GB/Month'
data$scenario_capacity[grep("50_50_50", data$scenario)] = '50 GB/Month'
# data$scenario_capacity[grep("100_100_100", data$scenario)] = '100 GB/Month'
data <- data[(data$scenario_capacity == '50 GB/Month'),]

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
                                levels=c('25 GB/Month',
                                         '50 GB/Month',
                                         '100 GB/Month'
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

data$total_demand_carbon_tonnes = data$total_demand_carbon_tonnes / 1e6
data$total_nitrogen_oxide_tonnes = data$total_nitrogen_oxide_tonnes / 1e3
data$total_sulpher_dioxide_tonnes = data$total_sulpher_dioxide_tonnes / 1e3
data$total_pm10_tonnes = data$total_pm10_tonnes / 1e3

# data$scenario = NULL
# data$strategy = NULL

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


############################
### Infra Sharing
############################


folder <- dirname(rstudioapi::getSourceEditorContext()$path)

filename = 'emissions_national_business_model_power_options.csv'
data <- read.csv(file.path(folder, '..', 'results', 'global_results', filename))
names(data)[names(data) == 'GID_0'] <- 'country'

data$scenario_adopt = ''
data$scenario_adopt[grep("high", data$scenario)] = 'high'
data$scenario_adopt[grep("baseline", data$scenario)] = 'baseline'
data$scenario_adopt[grep("low", data$scenario)] = 'low'

data$scenario_capacity = ''
data$scenario_capacity[grep("50_50_50", data$scenario)] = '50 GB/Month'
data <- data[(data$scenario_capacity == '50 GB/Month'),]

data$scenario_sharing = ''
data$scenario_sharing[grep("baseline_baseline_baseline_baseline_baseline", data$strategy)] = 'Baseline'
data$scenario_sharing[grep("passive_baseline_baseline_baseline_baseline", data$strategy)] = 'Passive'
data$scenario_sharing[grep("active_baseline_baseline_baseline_baseline", data$strategy)] = 'Active'
data$scenario_sharing[grep("srn_baseline_baseline_baseline_baseline", data$strategy)] = 'SRN'

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

data$scenario_sharing = factor(data$scenario_sharing,
                               levels=c("Baseline",
                                        "Passive",
                                        "Active",
                                        'SRN'
                               ))

data = data[complete.cases(data),]

data <- select(data,
               scenario_adopt, scenario_sharing, strategy_short, #grid_type,
               total_energy_annual_demand_kwh,
               total_demand_carbon_tonnes,
               total_nitrogen_oxide_tonnes,
               total_sulpher_dioxide_tonnes,
               total_pm10_tonnes)

data = data %>%
  group_by(scenario_adopt, scenario_sharing, strategy_short) %>%
  summarise(
    total_energy_annual_demand_kwh = sum(total_energy_annual_demand_kwh),
    total_demand_carbon_tonnes = sum(total_demand_carbon_tonnes),
    total_nitrogen_oxide_tonnes = sum(total_nitrogen_oxide_tonnes),
    total_sulpher_dioxide_tonnes = sum(total_sulpher_dioxide_tonnes),
    total_pm10_tonnes = sum(total_pm10_tonnes)
  )

############
sample <- data %>%
  group_by(scenario_adopt, scenario_sharing, strategy_short) %>% #, grid_type
  summarize(
    value = round(sum(total_energy_annual_demand_kwh)),
  )

sample$value = sample$value / 1e9

min_value = min(round(sample$value))
max_value = max(round(sample$value)) + 1
min_value[min_value > 0] = 0

sample = spread(sample, scenario_adopt, value)

totals <- sample %>%
  group_by(scenario_sharing, strategy_short) %>%
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
            size = 3, data = totals, vjust=-.5, hjust=.5) +
  theme(legend.position = 'none',
        axis.text.x = element_text(angle = 45, hjust=1)) +
  labs(title = "Cumulative Cell Site Energy Demand over 2020-2030 by Infrastructure Sharing Strategy",
       fill=NULL,
       subtitle = "For 50 GB/Month per user with interval bars reflecting low and high adoption scenarios",
       x = NULL, y = "Terawatt hours (TWh)") +
  scale_y_continuous(expand = c(0, 0), limits = c(0, max_value)) +
  scale_fill_viridis_d() +
  facet_grid(~scenario_sharing)

############
sample <- data %>%
  group_by(scenario_adopt, scenario_sharing, strategy_short) %>% #, grid_type
  summarize(
    value = round(sum(total_demand_carbon_tonnes)),
  )

sample$value = sample$value / 1e6

min_value = min(round(sample$value))
max_value = max(round(sample$value)) + 1
min_value[min_value > 0] = 0

sample = spread(sample, scenario_adopt, value)

totals <- sample %>%
  group_by(scenario_sharing, strategy_short) %>%
  summarize(value2 = round(
    (baseline), 1))

carbon_dioxide = ggplot(sample,
                        aes(x=strategy_short, y=baseline, fill=strategy_short)) +
  geom_bar(stat="identity", position=position_dodge()) +
  geom_errorbar(data=sample, aes(y = baseline, ymin = low, ymax = high),
                position = position_dodge(width = .9), lwd = 0.5,
                show.legend = FALSE, width=0.1,  color="#FF0000FF") +
  geom_text(y=0, aes(strategy_short, value2, label = value2, color="#FF0000FF"),
            size = 3, data = totals, vjust=-.5, hjust=.5) +
  theme(legend.position = 'none',
        axis.text.x = element_text(angle = 45, hjust=1)) +
  labs(title=expression(paste("Cumulative Cell Site Emissions over 2020-2030 (", CO[2], ") by Infrastructure Sharing Strategy")),
       fill=NULL,
       subtitle = "For 50 GB/Month per user with interval bars reflecting low and high adoption scenarios",
       x=NULL, y=expression(paste("Megatonnes of ", CO[2])),sep="") +
  scale_y_continuous(expand = c(0, 0), limits = c(0, max_value)) +
  scale_fill_viridis_d() +
  facet_grid(~scenario_sharing)

# dir.create(file.path(folder, 'figures', iso3), showWarnings = FALSE)
# path = file.path(folder, 'figures', iso3, 'carbon_sharing.png')
# ggsave(path, units="in", width=8, height=4, dpi=300)
# dir.create(file.path(folder, '..', 'reports', 'images', iso3), showWarnings = FALSE)
# path = file.path(folder, '..', 'reports', 'images', iso3, 'carbon_sharing.png')
# ggsave(path, units="in", width=8, height=4, dpi=300)
# while (!is.null(dev.list()))  dev.off()

############
sample <- data %>%
  group_by(scenario_adopt, scenario_sharing, strategy_short) %>% #, grid_type
  summarize(
    value = round(sum(total_nitrogen_oxide_tonnes)),
  )

sample$value = sample$value / 1e3

min_value = min(round(sample$value))
max_value = max(round(sample$value)) + 1
min_value[min_value > 0] = 0

sample = spread(sample, scenario_adopt, value)

totals <- sample %>%
  group_by(scenario_sharing, strategy_short) %>%
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
  labs(title=expression(paste("Cumulative Cell Site Emissions over 2020-2030 (", NO[x], ") by Infrastructure Sharing Strategy")),
       # title = "Cell Site Emissions for Colombia 2020-2030 (Nitrogen Oxides)",
       fill=NULL,
       subtitle = "For 50 GB/Month per user with interval bars reflecting low and high adoption scenarios",
       x = NULL, y=expression(paste("Kilotonnes of ", NO[x])), sep="")  +
  scale_y_continuous(expand = c(0, 0), limits = c(0, max_value)) +
  scale_fill_viridis_d() +
  facet_grid(~scenario_sharing)

############
sample <- data %>%
  group_by(scenario_adopt, scenario_sharing, strategy_short) %>% #, grid_type
  summarize(
    value = round(sum(total_sulpher_dioxide_tonnes)),
  )

sample$value = sample$value / 1e3

min_value = min(round(sample$value))
max_value = max(round(sample$value)) + 1
min_value[min_value > 0] = 0

sample = spread(sample, scenario_adopt, value)

totals <- sample %>%
  group_by(scenario_sharing, strategy_short) %>%
  summarize(value2 = round(baseline, 0))

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
  labs(title=expression(paste("Cumulative Cell Site Emissions over 2020-2030 (", SO[x], ") by Infrastructure Sharing Strategy")),
       # title = "Cell Site Emissions for Colombia 2020-2030 (Sulphur Oxides)",
       fill=NULL,
       subtitle = "For 50 GB/Month per user with interval bars reflecting low and high adoption scenarios",
       x = NULL, y=expression(paste("Kilotonnes of ", SO[x])), sep="") +
  scale_y_continuous(expand = c(0, 0), limits = c(0, max_value)) +
  scale_fill_viridis_d() +
  facet_grid(~scenario_sharing)

############

sample <- data %>%
  group_by(scenario_adopt, scenario_sharing, strategy_short) %>% #, grid_type
  summarize(
    value = round(sum(total_pm10_tonnes)),
  )

sample$value = sample$value / 1e3

min_value = min(round(sample$value))
max_value = max(round(sample$value)) + 1
min_value[min_value > 0] = 0

sample = spread(sample, scenario_adopt, value)

totals <- sample %>%
  group_by(scenario_sharing, strategy_short) %>%
  summarize(value2 = round(baseline, 0))

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
  labs(title=expression(paste("Cumulative Cell Site Emissions over 2020-2030 (", PM[10], ") by Infrastructure Sharing Strategy")),
       fill=NULL,
       subtitle = "For 50 GB/Month per user with interval bars reflecting low and high adoption scenarios",
       x = NULL, y=expression(paste("Kilotonnes of ", PM[10])), sep="") + #y ="Tonnes of PM10") +
  scale_y_continuous(expand = c(0, 0), limits = c(0, max_value)) +
  scale_fill_viridis_d() +
  facet_grid(~scenario_sharing)

############
ggarrange(
  energy,
  carbon_dioxide,
  labels = c("A", "B"),
  ncol = 1, nrow = 2)

dir.create(file.path(folder, 'figures', 'global'), showWarnings = FALSE)
path = file.path(folder, 'figures', 'global', 'energy_emissions_sharing.png')
ggsave(path, units="in", width=8, height=7, dpi=300)
dir.create(file.path(folder, '..', 'reports', 'images', 'global'), showWarnings = FALSE)
path = file.path(folder, '..', 'reports', 'images', 'global', 'energy_emissions_sharing.png')
ggsave(path, units="in", width=8, height=7, dpi=300)
while (!is.null(dev.list()))  dev.off()

ggarrange(
  nitrogen_dioxide,
  suplher_dioxide,
  pm10,
  labels = c("A", "B", "C"),
  ncol = 1, nrow = 3)

dir.create(file.path(folder, 'figures', 'global'), showWarnings = FALSE)
path = file.path(folder, 'figures', 'global', 'health_emissions_sharing.png')
ggsave(path, units="in", width=8, height=10, dpi=300)
dir.create(file.path(folder, '..', 'reports', 'images', 'global'), showWarnings = FALSE)
path = file.path(folder, '..', 'reports', 'images', 'global', 'health_emissions_sharing.png')
ggsave(path, units="in", width=8, height=10, dpi=300)
while (!is.null(dev.list()))  dev.off()
