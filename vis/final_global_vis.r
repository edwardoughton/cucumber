###VISUALISE MODEL OUTPUTS###
library(tidyverse)
library(ggpubr)

threshold = 10

folder <- dirname(rstudioapi::getSourceEditorContext()$path)

filename = 'decile_market_cost_results_technology_options.csv'
data <- read.csv(file.path(folder, '..', 'results', 'global_results', filename))

data$scenario_capacity = ''
data$scenario_capacity[grep("25_25_25", data$scenario)] = '25 GB/Month'
data$scenario_capacity[grep("50_50_50", data$scenario)] = '50 GB/Month'
data$scenario_capacity[grep("75_75_75", data$scenario)] = '75 GB/Month'

data = data[(data$scenario_capacity == '25 GB/Month' |
               data$scenario_capacity == '50 GB/Month' |
               data$scenario_capacity == '75 GB/Month'),]

data$pop_density_km2 = round(data$population_total / data$area_km2,1)

excluded = data[(data$pop_density_km2 < threshold),]
excluded = excluded[(excluded$scenario == "baseline_50_50_50" &
                       excluded$strategy == "4G_epc_fiber_baseline_baseline_baseline_baseline_baseline"),]
ex_sum = sum(excluded$population_total)

included = data[(data$pop_density_km2 > threshold),]
included = included[(included$scenario == "baseline_50_50_50" &
                       included$strategy == "4G_epc_fiber_baseline_baseline_baseline_baseline_baseline"),]
inc_sum = sum(included$population_total)
coverage = round(inc_sum/(inc_sum + ex_sum) * 100,1)

data = data[(data$pop_density_km2 > threshold),]

country_info = read_csv(file.path(folder, '..', '..','data_raw', 'countries.csv'))
country_info = select(country_info, iso3, continent)
data = merge(data, country_info, by.x="GID_0", by.y="iso3")

data$scenario_capacity = ''
data$scenario_capacity[grep("25_25_25", data$scenario)] = '25 GB/Month'
data$scenario_capacity[grep("50_50_50", data$scenario)] = '50 GB/Month'
data$scenario_capacity[grep("75_75_75", data$scenario)] = '75 GB/Month'

by_continent = data %>%
  group_by(scenario, strategy, continent) %>%
  summarise(
    private_cost = round(sum(private_cost, na.rm=TRUE)/1e9,1),
    government_cost = round(sum(government_cost, na.rm=TRUE)/1e9,1),
    societal_cost = round(sum(societal_cost, na.rm=TRUE)/1e9,1)
  )

data = data %>%
  group_by(GID_0, scenario, strategy) %>%
  summarise(
    private_cost = round(sum(private_cost, na.rm=TRUE),0),
    government_cost = round(sum(government_cost, na.rm=TRUE),0),
    societal_cost = round(sum(societal_cost, na.rm=TRUE),0)
  )

data = data %>%
  group_by(scenario, strategy) %>%
  summarise(
    private_cost = round(sum(private_cost, na.rm=TRUE),0),
    government_cost = round(sum(government_cost, na.rm=TRUE),0),
    societal_cost = round(sum(societal_cost, na.rm=TRUE),0)
  )


names(data)[names(data) == 'GID_0'] <- 'country'

data$scenario_adopt = ''
data$scenario_adopt[grep("low", data$scenario)] = 'Low (1.3% Adoption CAGR)'
data$scenario_adopt[grep("baseline", data$scenario)] = 'Baseline (2.5% Adoption CAGR)'
data$scenario_adopt[grep("high", data$scenario)] = 'High (4.4% Adoption CAGR)'

data$scenario_capacity = ''
data$scenario_capacity[grep("25_25_25", data$scenario)] = '25 GB/Month'
data$scenario_capacity[grep("50_50_50", data$scenario)] = '50 GB/Month'
data$scenario_capacity[grep("75_75_75", data$scenario)] = '75 GB/Month'

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
                                levels=c('25 GB/Month', #'20 GB/Month',
                                         '50 GB/Month',#'40 GB/Month',
                                         '75 GB/Month'#'60 GB/Month'#,
                                ))

data = data[complete.cases(data), ]

data$scenario_adopt = factor(data$scenario_adopt, 
                             levels=c("Low (1.3% Adoption CAGR)",
                                      "Baseline (2.5% Adoption CAGR)",
                                      "High (4.4% Adoption CAGR)"))

data <- select(data, scenario_adopt, scenario_capacity, strategy_short, 
               private_cost, government_cost, societal_cost)

totals <- data %>%
  group_by(scenario_adopt, scenario_capacity, strategy_short) %>%
  summarize(social_cost = round(
    (societal_cost)/1e12,2))

min_value = min(totals$social_cost)
max_value = max(totals$social_cost) + 1.5
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

data$value = round(data$value/1e12, 3)

ggplot(data, aes(y=value, x=strategy_short, fill=Cost_Type)) + 
  geom_bar(position="stack", stat="identity") +
  geom_text(aes(strategy_short, social_cost, label = social_cost,  #y=0, 
                fill = NULL), show.legend = FALSE, ##FF0000FF
            size = 2, data = totals, vjust=-.9, hjust=.5) +
  scale_fill_manual(values=c("#29af7f", "#482173"), name=NULL) +
  theme(legend.position = "bottom",
        axis.text.x = element_text(angle = 45, hjust=1)) +
  labs(title = "Financial Cost of Universal Broadband by Technology", 
       colour=NULL,
       subtitle = "Reported for all adoption scenarios and capacity per user targets (2020-2030)",
       x = NULL, y = "Financial Cost (Trillions $USD)") +
  scale_y_continuous(expand = c(0, 0), limits = c(0, max_value)) +
  theme(panel.spacing = unit(0.5, "lines")) +
  guides(fill=guide_legend(ncol=3, reverse = TRUE)) +
  facet_grid(scenario_capacity~scenario_adopt)

dir.create(file.path(folder, 'figures', 'global'), showWarnings = FALSE)
path = file.path(folder, 'figures', 'global', 'financial_cost_by_strategy.png')
ggsave(path, units="in", width=8, height=6, dpi=300)
dir.create(file.path(folder, '..', 'reports', 'images', 'global'), showWarnings = FALSE)
path = file.path(folder, '..', 'reports', 'images', 'global', 'financial_cost_by_strategy.png')
ggsave(path, units="in", width=8, height=6, dpi=300)
dev.off()

################################################################################

folder <- dirname(rstudioapi::getSourceEditorContext()$path)

filename = 'national_market_cost_results_business_model_options.csv'
data <- read.csv(file.path(folder, '..', 'results', 'global_results', filename))

data$scenario_capacity = ''
data$scenario_capacity[grep("25_25_25", data$scenario)] = '25 GB/Month'
data$scenario_capacity[grep("50_50_50", data$scenario)] = '50 GB/Month'
data$scenario_capacity[grep("75_75_75", data$scenario)] = '75 GB/Month'

data = data[(data$scenario_capacity == '25 GB/Month' |
               data$scenario_capacity == '50 GB/Month' |
               data$scenario_capacity == '75 GB/Month'),]

country_info = read_csv(file.path(folder, '..', '..','data_raw', 'countries.csv'))
country_info = select(country_info, iso3, continent)
data = merge(data, country_info, by.x="GID_0", by.y="iso3")

by_continent = data %>%
  group_by(scenario, strategy, continent) %>%
  summarise(
    private_cost = round(sum(private_cost, na.rm=TRUE)/1e9,1),
    government_cost = round(sum(government_cost, na.rm=TRUE)/1e9,1),
    societal_cost = round(sum(societal_cost, na.rm=TRUE)/1e9,1)
  )

data$GID_0 = NULL

data = data %>%
  group_by(scenario, strategy) %>%
  summarise(
    private_cost = sum(private_cost),
    government_cost = sum(government_cost),
    societal_cost = sum(societal_cost)
  )

names(data)[names(data) == 'GID_0'] <- 'country'

data$scenario_adopt = ''
data$scenario_adopt[grep("low", data$scenario)] = 'Low (1.3% Adoption CAGR)'
data$scenario_adopt[grep("baseline", data$scenario)] = 'Baseline (2.5% Adoption CAGR)'
data$scenario_adopt[grep("high", data$scenario)] = 'High (4.4% Adoption CAGR)'
data$scenario_capacity = ''
data$scenario_capacity[grep("25_25_25", data$scenario)] = '25 GB/Month'
data$scenario_capacity[grep("50_50_50", data$scenario)] = '50 GB/Month'
data$scenario_capacity[grep("75_75_75", data$scenario)] = '75 GB/Month'

data$strategy_short = ''
data$strategy_short[grep("4G_epc_wireless", data$strategy)] = '4G (W)'

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
                                levels=c('25 GB/Month',
                                         '50 GB/Month',
                                         '75 GB/Month'
                                ))

data$scenario_adopt = factor(data$scenario_adopt, 
                             levels=c("Low (1.3% Adoption CAGR)",
                                      "Baseline (2.5% Adoption CAGR)",
                                      "High (4.4% Adoption CAGR)"))

data <- select(data, scenario_adopt, scenario_capacity, strategy,
               private_cost, government_cost, societal_cost)

totals <- data %>%
  group_by(scenario_adopt, scenario_capacity, strategy) %>%
  summarize(social_cost = round(
    (societal_cost)/1e12,2))

min_value = min(round(totals$social_cost))
max_value = max(round(totals$social_cost)) + 1.5
min_value[min_value > 0] = 0

data$social_cost = data$private_cost + data$government_cost

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

data$value = round(data$value/1e12, 3)

ggplot(data, aes(y=value, x=strategy, fill=Cost_Type)) +
  geom_bar(position="stack", stat="identity") +
  geom_text(aes(strategy, social_cost, label = social_cost,  #y=0, 
                fill = NULL), show.legend = FALSE,
            size = 2, data = totals, vjust=-.9, hjust=.5) +
  scale_fill_manual(values=c("#29af7f", "#482173"), name=NULL) +
  theme(legend.position = "bottom",
        axis.text.x = element_text(angle = 45, hjust=1)) +
  labs(title = "Financial Cost of Universal Broadband by Infrastructure Sharing Strategy",
       colour=NULL,
       subtitle = "Reported using 4G (W) for all adoption scenarios and capacity per user targets (2020-2030)",
       x = NULL, y = "Financial Cost (Trillions $USD)") +
  scale_y_continuous(expand = c(0, 0), limits = c(-min_value, max_value)) +
  theme(panel.spacing = unit(0.6, "lines")) +
  guides(fill=guide_legend(ncol=3, reverse = TRUE)) +
  facet_grid(scenario_capacity~scenario_adopt)

path = file.path(folder, 'figures', 'global', 'financial_cost_by_sharing_strategy.png')
ggsave(path, units="in", width=8, height=6, dpi=300)
dir.create(file.path(folder, '..', 'reports', 'images', 'global'), showWarnings = FALSE)
path = file.path(folder, '..', 'reports', 'images', 'global', 'financial_cost_by_sharing_strategy.png')
ggsave(path, units="in", width=8, height=6, dpi=300)
dev.off()

################################################################################

folder <- dirname(rstudioapi::getSourceEditorContext()$path)

filename = 'national_market_cost_results_policy_options.csv'
data <- read.csv(file.path(folder, '..', 'results', 'global_results', filename))

data$GID_0 = NULL

data = data %>%
  group_by(scenario, strategy) %>%
  summarise(
    private_cost = sum(private_cost),
    government_cost = sum(government_cost),
    societal_cost = sum(societal_cost)
  )

data$scenario_adopt = ''
data$scenario_adopt[grep("low", data$scenario)] = 'Low (1.3% Adoption CAGR)'
data$scenario_adopt[grep("baseline", data$scenario)] = 'Baseline (2.5% Adoption CAGR)'
data$scenario_adopt[grep("high", data$scenario)] = 'High (4.4% Adoption CAGR)'

data$scenario_capacity = ''
data$scenario_capacity[grep("25_25_25", data$scenario)] = '25 GB/Month'
data$scenario_capacity[grep("50_50_50", data$scenario)] = '50 GB/Month'
data$scenario_capacity[grep("75_75_75", data$scenario)] = '75 GB/Month'

data = data[(data$scenario_capacity == '25 GB/Month' |
               data$scenario_capacity == '50 GB/Month' |
               data$scenario_capacity == '75 GB/Month'),]

data$strategy_short = ''
data$strategy_short[grep("4G_epc_wireless", data$strategy)] = '4G (W)'

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
                                levels=c('25 GB/Month',
                                         '50 GB/Month',
                                         '75 GB/Month'
                                ))

data$scenario_adopt = factor(data$scenario_adopt, 
                             levels=c("Low (1.3% Adoption CAGR)",
                                      "Baseline (2.5% Adoption CAGR)",
                                      "High (4.4% Adoption CAGR)"))

data <- select(data, scenario_adopt, scenario_capacity, strategy,
               private_cost, government_cost, societal_cost)

totals <- data %>%
  group_by(scenario_adopt, scenario_capacity, strategy) %>%
  summarize(social_cost = round(
    (societal_cost)/1e12, 2))

min_value = min(round(totals$social_cost, 2))
max_value = max(round(totals$social_cost, 2)) + 1.5
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

data$value = round(data$value/1e12, 2)

ggplot(data, aes(y=value, x=strategy, fill=Cost_Type)) +
  geom_bar(position="stack", stat="identity") +
  geom_text(aes(strategy, social_cost, label = social_cost,  #y=0, 
                fill = NULL), show.legend = FALSE,
            size = 2, data = totals, vjust=-.9, hjust=.5) +
  scale_fill_manual(values=c("#29af7f", "#482173"), name=NULL) +
  theme(legend.position = "bottom",
        axis.text.x = element_text(angle = 45, hjust=1)) +
  labs(title = "Financial Cost of Universal Broadband by Policy Strategy",
       colour=NULL,
       subtitle = "Reported using 4G (W) for all adoption scenarios and capacity per user targets (2020-2030)",
       x = NULL, y = "Financial Cost (Trillions $USD)") +
  scale_y_continuous(expand = c(0, 0), limits = c(-0, max_value)) +
  theme(panel.spacing = unit(0.6, "lines")) +
  guides(fill=guide_legend(ncol=3, reverse = TRUE)) +
  facet_grid(scenario_capacity~scenario_adopt)

path = file.path(folder, 'figures', 'global', 'financial_cost_by_policy_options.png')
ggsave(path, units="in", width=8, height=6, dpi=300)
path = file.path(folder, '..', 'reports', 'images', 'global', 'financial_cost_by_policy_options.png')
ggsave(path, units="in", width=8, height=6, dpi=300)
dev.off()

#############################
###EMISSIONS MODEL OUTPUTS###

folder <- dirname(rstudioapi::getSourceEditorContext()$path)

filename = 'emissions_technology_options.csv'
data <- read.csv(file.path(folder, '..', 'results', 'global_results', filename))

data$GID_0 = NULL

data = data %>%
  group_by(income, scenario, strategy, asset_type, grid_type) %>%
  summarise(
    total_energy_annual_demand_kwh = sum(total_energy_annual_demand_kwh),
    total_demand_carbon_tonnes = sum(total_demand_carbon_tonnes),
    total_nitrogen_oxide_tonnes = sum(total_nitrogen_oxide_tonnes),
    total_sulpher_dioxide_tonnes = sum(total_sulpher_dioxide_tonnes),
    total_pm10_tonnes = sum(total_pm10_tonnes),
  )

data$scenario_adopt = ''
data$scenario_adopt[grep("high", data$scenario)] = 'high'
data$scenario_adopt[grep("baseline", data$scenario)] = 'baseline'
data$scenario_adopt[grep("low", data$scenario)] = 'low'

data$scenario_capacity = ''
data$scenario_capacity[grep("25_25_25", data$scenario)] = '25 GB/Month'
data$scenario_capacity[grep("50_50_50", data$scenario)] = '50 GB/Month'
data$scenario_capacity[grep("75_75_75", data$scenario)] = '75 GB/Month'

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
                                levels=c('25 GB/Month',
                                         '50 GB/Month',
                                         '75 GB/Month'
                                ))

data$income = factor(data$income,
                     levels=c('LIC',
                              'LMIC',
                              'UMIC',
                              'HIC'
                     ))

data = data[complete.cases(data),]

data <- select(data, income,
               scenario_adopt, scenario_capacity, strategy_short, grid_type,
               total_energy_annual_demand_kwh,
               total_demand_carbon_tonnes,
               total_nitrogen_oxide_tonnes,
               total_sulpher_dioxide_tonnes,
               total_pm10_tonnes)

############
sample <- data %>%
  group_by(income, scenario_adopt, scenario_capacity, strategy_short) %>% #, grid_type
  summarize(
    value = round(sum(total_energy_annual_demand_kwh)),
  )

sample$value = sample$value / 1e12 #already in kwh, so /1e12 converts to pwh

sample = spread(sample, scenario_adopt, value)

totals <- sample %>%
  group_by(scenario_capacity, strategy_short) %>%
  summarize(value2 = round(
    sum(baseline), 2))

df_errorbar <- 
  sample |>
  group_by(income, scenario_capacity, strategy_short) |>
  summarize(
    low = sum(low),
    baseline = sum(baseline),
    high = sum(high)
  ) |>
  group_by(scenario_capacity, strategy_short) |>
  summarize(
    income = 'LIC', 
    low = sum(low),
    baseline = sum(baseline),
    high = sum(high)
  )

min_value = min(round(df_errorbar$low,3))
max_value = max(round(df_errorbar$high,3)) + .01
min_value[min_value > 0] = 0

energy = 
  ggplot(sample, aes(x=strategy_short, y=baseline, fill=income)) +
  geom_bar(stat="identity", position='stack') +
  geom_errorbar(data=df_errorbar, aes(y = baseline, ymin = low, ymax = high),
                show.legend = FALSE, width=0.1,  color="#FF0000FF"
  ) +
  geom_text(data = df_errorbar, 
            aes(label = paste(round(baseline, 2),"")), size = 2,#.25,
            vjust =-.7, hjust =-.2, angle = 0)+
  theme(legend.position = 'bottom',
        axis.text.x = element_text(angle = 45, hjust=1)) +
  labs(title = "Total Cell Site Energy Demand over 2020-2030",
       fill=NULL,
       subtitle = "Interval bars reflect estimates for low and high adoption scenarios",
       x = NULL, y = "Petawatt hours (PWh)") +
  scale_y_continuous(expand = c(0, 0), limits = c(0, max_value)) +
  scale_fill_viridis_d() +
  facet_grid(~scenario_capacity)

############
sample <- data %>%
  group_by(income, scenario_adopt, scenario_capacity, strategy_short) %>% #, grid_type
  summarize(
    value = round(sum(total_demand_carbon_tonnes)),
  )

sample$value = sample$value / 1e9

sample = spread(sample, scenario_adopt, value)

totals <- sample %>%
  group_by(scenario_capacity, strategy_short) %>%
  summarize(value = round(
    sum(baseline), 2))

df_errorbar <- 
  sample |>
  group_by(income, scenario_capacity, strategy_short) |>
  summarize(
    low = sum(low),
    baseline = sum(baseline),
    high = sum(high)
  ) |>
  group_by(scenario_capacity, strategy_short) |>
  summarize(
    income = 'LIC', 
    low = sum(low),
    baseline = sum(baseline),
    high = sum(high)
  )

min_value = min(round(df_errorbar$low,3))
max_value = max(round(df_errorbar$high,3)) + .001
min_value[min_value > 0] = 0

carbon_dioxide = ggplot(sample,
                        aes(x=strategy_short, y=baseline, fill=income)) +
  geom_bar(stat="identity", position='stack') +
  geom_errorbar(data=df_errorbar, aes(y = baseline, ymin = low, ymax = high),
                lwd = .5, 
                show.legend = FALSE, width=0.1,  color="#FF0000FF") +
  geom_text(data = df_errorbar, 
            aes(label = paste(round(baseline, 2),"")), size = 2,#.25,
            vjust =-.7, hjust =-.2, angle = 0)+
  theme(legend.position = 'bottom',
        axis.text.x = element_text(angle = 45, hjust=1)) +
  labs(title=expression(paste("Total Cell Site Emissions over 2020-2030 (", CO[2], ")")),
       fill=NULL,
       subtitle = "Interval bars reflect estimates for low and high adoption scenarios",
       x=NULL, y=expression(paste("Gigatonnes of ", CO[2])),sep="") +
  scale_y_continuous(expand = c(0, 0), limits = c(0, max_value)) +
  scale_fill_viridis_d() +
  facet_grid(~scenario_capacity)

############
sample <- data %>%
  group_by(income, scenario_adopt, scenario_capacity, strategy_short) %>% #, grid_type
  summarize(
    value = round(sum(total_nitrogen_oxide_tonnes)),
  )

sample$value = sample$value / 1e6

sample = spread(sample, scenario_adopt, value)

totals <- sample %>%
  group_by(scenario_capacity, strategy_short) %>%
  summarize(value = round(sum(baseline), 2))

df_errorbar <- 
  sample |>
  group_by(income, scenario_capacity, strategy_short) |>
  summarize(
    low = sum(low),
    baseline = sum(baseline),
    high = sum(high)
  ) |>
  group_by(scenario_capacity, strategy_short) |>
  summarize(
    income = 'LIC', 
    low = sum(low),
    baseline = sum(baseline),
    high = sum(high)
  )

min_value = min(round(df_errorbar$low,3))
max_value = max(round(df_errorbar$high,3)) + .001
min_value[min_value > 0] = 0

nitrogen_dioxide = ggplot(sample,
                          aes(x=strategy_short, y=baseline, fill=income)) +
  geom_bar(stat="identity", position='stack') +
  geom_errorbar(data=df_errorbar, aes(y = baseline, ymin = low, ymax = high),
                lwd = .5, 
                show.legend = FALSE, width=0.1,  color="#FF0000FF") +
  geom_text(data = df_errorbar, 
            aes(label = paste(round(baseline, 2),"")), size = 2,#.25,
            vjust =-.7, hjust =-.2, angle = 0)+
  theme(legend.position = 'none',
        axis.text.x = element_text(angle = 45, hjust=1)) +
  labs(title=expression(paste("Total Cell Site Emissions over 2020-2030 (", NO[x], ")")),
       fill=NULL,
       subtitle = "Interval bars reflect estimates for low and high adoption scenarios for",
       x = NULL, y=expression(paste("Megatonnes of ", NO[x])), sep="")  +
  scale_y_continuous(expand = c(0, 0), limits = c(0, max_value)) +
  scale_fill_viridis_d() +
  facet_grid(~scenario_capacity)

############
sample <- data %>%
  group_by(income, scenario_adopt, scenario_capacity, strategy_short) %>% #, grid_type
  summarize(
    value = round(sum(total_sulpher_dioxide_tonnes)),
  )

sample$value = sample$value / 1e6

sample = spread(sample, scenario_adopt, value)

totals <- sample %>%
  group_by(scenario_capacity, strategy_short) %>%
  summarize(value = round(sum(baseline), 2))

df_errorbar <- 
  sample |>
  group_by(income, scenario_capacity, strategy_short) |>
  summarize(
    low = sum(low),
    baseline = sum(baseline),
    high = sum(high)
  ) |>
  group_by(scenario_capacity, strategy_short) |>
  summarize(
    income = 'LIC', 
    low = sum(low),
    baseline = sum(baseline),
    high = sum(high)
  )

min_value = min(round(df_errorbar$low,3))
max_value = max(round(df_errorbar$high,3)) + .01
min_value[min_value > 0] = 0

suplher_dioxide = ggplot(sample,
                         aes(x=strategy_short, y=baseline, fill=income)) +
  geom_bar(stat="identity", position='stack') +
  geom_errorbar(data=df_errorbar, aes(y = baseline, ymin = low, ymax = high),
                lwd = .5, 
                show.legend = FALSE, width=0.1,  color="#FF0000FF") +
  geom_text(data = df_errorbar, 
            aes(label = paste(round(baseline, 2),"")), size = 2,#.25,
            # position = position_dodge(1), 
            vjust =-.7, hjust =-.2, angle = 0)+
  theme(legend.position = 'none',
        axis.text.x = element_text(angle = 45, hjust=1)) +
  labs(title=expression(paste("Total Cell Site Emissions over 2020-2030 (", SO[x], ")")),
       fill=NULL,
       subtitle = "Interval bars reflect estimates for low and high adoption scenarios for",
       x = NULL, y=expression(paste("Megatonnes of ", SO[x])), sep="") +
  scale_y_continuous(expand = c(0, 0), limits = c(0, max_value)) +
  scale_fill_viridis_d() +
  facet_grid(~scenario_capacity)

############

sample <- data %>%
  group_by(income, scenario_adopt, scenario_capacity, strategy_short) %>% #, grid_type
  summarize(
    value = round(sum(total_pm10_tonnes)),
  )

sample$value = sample$value / 1e6

sample = spread(sample, scenario_adopt, value)

totals <- sample %>%
  group_by(scenario_capacity, strategy_short) %>%
  summarize(value = round(sum(baseline), 2))

df_errorbar <- 
  sample |>
  group_by(income, scenario_capacity, strategy_short) |>
  summarize(
    low = sum(low),
    baseline = sum(baseline),
    high = sum(high)
  ) |>
  group_by(scenario_capacity, strategy_short) |>
  summarize(
    income = 'LIC', 
    low = sum(low),
    baseline = sum(baseline),
    high = sum(high)
  )

min_value = min(round(df_errorbar$low,3))
max_value = max(round(df_errorbar$high,3)) + .01
min_value[min_value > 0] = 0

pm10 = ggplot(sample,
              aes(x=strategy_short, y=baseline, fill=income)) +
  geom_bar(stat="identity", position='stack') +
  geom_errorbar(data=df_errorbar, aes(y = baseline, ymin = low, ymax = high),
                position = position_dodge(.75), lwd = .5,
                show.legend = FALSE, width=0.1,  color="#FF0000FF") +
  geom_text(data = df_errorbar, 
            aes(label = paste(round(baseline, 2),"")), size = 2,#.25,
            vjust =-.7, hjust =-.2, angle = 0) +
  theme(legend.position = 'none',
        axis.text.x = element_text(angle = 45, hjust=1)) +
  labs(title=expression(paste("Total Cell Site Emissions over 2020-2030 (", PM[10], ")")),
       fill=NULL,
       subtitle = "Interval bars reflect estimates for low and high adoption scenarios for",
       x = NULL, y=expression(paste("Megatonnes of ", PM[10])), sep="") + 
  scale_y_continuous(expand = c(0, 0), limits = c(0, max_value)) +
  scale_fill_viridis_d() +
  facet_grid(~scenario_capacity)

############
ggarrange(
  energy,
  carbon_dioxide,
  labels = c("A", "B"),
  ncol = 1, nrow = 2,
  common.legend = TRUE,
  legend = 'bottom')

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
  ncol = 1, nrow = 3,
  common.legend = TRUE,
  legend = 'bottom')

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
  "4G (W)",
  '5G (F)',
  '5G (W)'
))

data$scenario_capacity = factor(data$scenario_capacity,
                                levels=c('25 GB/Month',
                                         '50 GB/Month',
                                         '75 GB/Month'
                                ))

data$income = factor(data$income,
                     levels=c('LIC',
                              'LMIC',
                              'UMIC',
                              'HIC'
                     ))

data = data[complete.cases(data),]

data = data %>%
  group_by(income, 
           scenario_adopt, scenario_capacity, strategy_short, strategy_power) %>%
  summarise(
    total_demand_carbon_tonnes = sum(total_demand_carbon_tonnes),
    total_nitrogen_oxide_tonnes = sum(total_nitrogen_oxide_tonnes),
    total_sulpher_dioxide_tonnes = sum(total_sulpher_dioxide_tonnes),
    total_pm10_tonnes = sum(total_pm10_tonnes)
  )

############

data$total_demand_carbon_tonnes = data$total_demand_carbon_tonnes / 1e9
data$total_nitrogen_oxide_tonnes = data$total_nitrogen_oxide_tonnes / 1e6
data$total_sulpher_dioxide_tonnes = data$total_sulpher_dioxide_tonnes / 1e6
data$total_pm10_tonnes = data$total_pm10_tonnes / 1e6

long <- data %>% 
  gather(type, value, -c(
    income, scenario_adopt, scenario_capacity, strategy_short, strategy_power))

long$strategy_long <- paste(long$strategy_short, data$strategy_power)

long$strategy_long = factor(long$strategy_long,
                            levels=c(
                              "4G (F) Baseline",
                              "4G (F) Renewables",
                              "4G (W) Baseline",
                              "4G (W) Renewables",
                              "5G (F) Baseline",
                              "5G (F) Renewables",
                              "5G (W) Baseline",
                              "5G (W) Renewables"
                              
                            ),
                            labels=c(
                              "4G (F)\nBaseline",
                              "4G (F)\nRenewables",
                              "4G (W)\nBaseline",
                              "4G (W)\nRenewables",
                              "5G (F)\nBaseline",
                              "5G (F)\nRenewables",
                              "5G (W)\nBaseline",
                              "5G (W)\nRenewables"
                              
                            )
)

long$strategy_short = NULL
long$strategy_power = NULL
long$scenario_capacity = NULL

long$type = factor(long$type,
                   levels=c("total_demand_carbon_tonnes",
                            "total_nitrogen_oxide_tonnes",
                            "total_sulpher_dioxide_tonnes",
                            "total_pm10_tonnes"
                   ),
                   labels=c(
                     expression(paste("(A) Gigatonnes of ", CO[2])),
                     expression(paste("(B) Megatonnes of ", NO[x])),
                     expression(paste("(C) Megatonnes of ", SO[x])),
                     expression(paste("(D) Megatonnes of ", PM[10]))
                   ))

long = spread(long, scenario_adopt, value)

df_errorbar <- 
  long |>
  group_by(income, type, strategy_long) |>
  summarize(
    low = sum(low),
    baseline = sum(baseline),
    high = sum(high)
  ) |>
  group_by(type, strategy_long) |>
  summarize(
    income = 'LIC', 
    low = sum(low),
    baseline = sum(baseline),
    high = sum(high)
  )

ggplot(long, aes(x=strategy_long, y=baseline, fill=income)) +
  geom_bar(stat="identity", position='stack') +
  geom_errorbar(data=df_errorbar, aes(y = baseline, ymin = low, ymax = high),
                lwd = 0.5, 
                show.legend = FALSE, width=0.1,  color="#FF0000FF") +
  geom_text(data = df_errorbar, 
            aes(label = paste(round(baseline, 2),"")), size = 2,
            vjust =-.5, hjust =-.2, angle = 0)+
  theme(legend.position = 'bottom',
        axis.text.x = element_text(angle = 45, hjust=1)) +
  labs(title="Impact of Transitioning Off-Grid Diesel Generators to Renewable Site Power",
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

data$scenario_sharing = factor(data$scenario_sharing,
                               levels=c("Baseline",
                                        "Passive",
                                        "Active",
                                        'SRN'
                               ))

data$income = factor(data$income,
                     levels=c('LIC',
                              'LMIC',
                              'UMIC',
                              'HIC'
                     ))

data = data[complete.cases(data),]

data <- select(data, income, 
               scenario_adopt, scenario_sharing, strategy_short, #grid_type,
               total_energy_annual_demand_kwh,
               total_demand_carbon_tonnes,
               total_nitrogen_oxide_tonnes,
               total_sulpher_dioxide_tonnes,
               total_pm10_tonnes)

data = data %>%
  group_by(income, scenario_adopt, scenario_sharing, strategy_short) %>%
  summarise(
    total_energy_annual_demand_kwh = sum(total_energy_annual_demand_kwh),
    total_demand_carbon_tonnes = sum(total_demand_carbon_tonnes),
    total_nitrogen_oxide_tonnes = sum(total_nitrogen_oxide_tonnes),
    total_sulpher_dioxide_tonnes = sum(total_sulpher_dioxide_tonnes),
    total_pm10_tonnes = sum(total_pm10_tonnes)
  )

############
sample <- data %>%
  group_by(income, scenario_adopt, scenario_sharing, strategy_short) %>% #, grid_type
  summarize(
    value = round(sum(total_energy_annual_demand_kwh)),
  )

sample$value = sample$value / 1e12

sample = spread(sample, scenario_adopt, value)

totals <- sample %>%
  group_by(scenario_sharing, strategy_short) %>%
  summarize(value = round(sum(baseline), 1))

df_errorbar <- 
  sample |>
  group_by(income, scenario_sharing, strategy_short) |>
  summarize(
    low = sum(low),
    baseline = sum(baseline),
    high = sum(high)
  ) |>
  group_by(scenario_sharing, strategy_short) |>
  summarize(
    income = 'LIC', 
    low = sum(low),
    baseline = sum(baseline),
    high = sum(high)
  )

min_value = min(round(df_errorbar$low,3))
max_value = max(round(df_errorbar$high,3)) + .01
min_value[min_value > 0] = 0

energy =
  ggplot(sample,
         aes(x=strategy_short, y=baseline, fill=income)) +
  geom_bar(stat="identity", position='stack') +
  geom_errorbar(data=df_errorbar, aes(y = baseline, ymin = low, ymax = high),
                lwd = 0.5,
                show.legend = FALSE, width=0.1,  color="#FF0000FF") +
  geom_text(data = df_errorbar,
            aes(label = paste(round(baseline, 2),"")), size = 2,#.25,
            vjust =-.7, hjust =-.2, angle = 0) +
  theme(legend.position = 'bottom',
        axis.text.x = element_text(angle = 45, hjust=1)) +
  labs(title = "Total Cell Site Energy Demand over 2020-2030 by Infrastructure Sharing Strategy",
       fill=NULL,
       subtitle = "For 50 GB/Month per user with interval bars reflecting low and high adoption scenarios",
       x = NULL, y = "Petawatt hours (PWh)") +
  scale_y_continuous(expand = c(0, 0), limits = c(0, max_value)) +
  scale_fill_viridis_d() +
  facet_grid(~scenario_sharing)

############
sample <- data %>%
  group_by(income, scenario_adopt, scenario_sharing, strategy_short) %>% #, grid_type
  summarize(
    value = round(sum(total_demand_carbon_tonnes)),
  )

sample$value = sample$value / 1e9

sample = spread(sample, scenario_adopt, value)

totals <- sample %>%
  group_by(scenario_sharing, strategy_short) %>%
  summarize(value = round(sum(baseline), 1))

df_errorbar <- 
  sample |>
  group_by(income, scenario_sharing, strategy_short) |>
  summarize(
    low = sum(low),
    baseline = sum(baseline),
    high = sum(high)
  ) |>
  group_by(scenario_sharing, strategy_short) |>
  summarize(
    income = 'LIC', 
    low = sum(low),
    baseline = sum(baseline),
    high = sum(high)
  )

min_value = min(round(df_errorbar$low,3))
max_value = max(round(df_errorbar$high,3)) + .001
min_value[min_value > 0] = 0

carbon_dioxide = ggplot(sample,
                        aes(x=strategy_short, y=baseline, fill=income)) +
  geom_bar(stat="identity", position='stack') +
  geom_errorbar(data=df_errorbar, aes(y = baseline, ymin = low, ymax = high),
                lwd = 0.5, 
                show.legend = FALSE, width=0.1,  color="#FF0000FF") +
  geom_text(data = df_errorbar,
            aes(label = paste(round(baseline, 2),"")), size = 2,#.25,
            vjust =-.7, hjust =-.2, angle = 0) +
  theme(legend.position = 'none',
        axis.text.x = element_text(angle = 45, hjust=1)) +
  labs(title=expression(paste("Total Cell Site Emissions over 2020-2030 (", CO[2], ") by Infrastructure Sharing Strategy")),
       fill=NULL,
       subtitle = "For 50 GB/Month per user with interval bars reflecting low and high adoption scenarios",
       x=NULL, y=expression(paste("Gigatonnes of ", CO[2])),sep="") +
  scale_y_continuous(expand = c(0, 0), limits = c(0, max_value)) +
  scale_fill_viridis_d() +
  facet_grid(~scenario_sharing)

############
sample <- data %>%
  group_by(income, scenario_adopt, scenario_sharing, strategy_short) %>% #, grid_type
  summarize(
    value = round(sum(total_nitrogen_oxide_tonnes)),
  )

sample$value = sample$value / 1e3

sample = spread(sample, scenario_adopt, value)

totals <- sample %>%
  group_by(scenario_sharing, strategy_short) %>%
  summarize(value = round(sum(baseline), 1))

df_errorbar <- 
  sample |>
  group_by(income, scenario_sharing, strategy_short) |>
  summarize(
    low = sum(low),
    baseline = sum(baseline),
    high = sum(high)
  ) |>
  group_by(scenario_sharing, strategy_short) |>
  summarize(
    income = 'LIC', 
    low = sum(low),
    baseline = sum(baseline),
    high = sum(high)
  )

min_value = min(round(df_errorbar$low,3))
max_value = max(round(df_errorbar$high,3)) + .01
min_value[min_value > 0] = 0

nitrogen_dioxide = ggplot(sample,
                          aes(x=strategy_short, y=baseline, fill=income)) +
  geom_bar(stat="identity", position='stack') +
  geom_errorbar(data=df_errorbar, aes(y = baseline, ymin = low, ymax = high),
                lwd = 0.5, 
                show.legend = FALSE, width=0.1,  color="#FF0000FF") +
  geom_text(data = df_errorbar,
            aes(label = paste(round(baseline, 2),"")), size = 2,#.25,
            vjust =-.7, hjust =-.2, angle = 0) +
  theme(legend.position = 'none',
        axis.text.x = element_text(angle = 45, hjust=1)) +
  labs(title=expression(paste("Total Cell Site Emissions over 2020-2030 (", NO[x], ") by Infrastructure Sharing Strategy")),
       fill=NULL,
       subtitle = "For 50 GB/Month per user with interval bars reflecting low and high adoption scenarios",
       x = NULL, y=expression(paste("Megatonnes of ", NO[x])), sep="")  +
  scale_y_continuous(expand = c(0, 0), limits = c(0, max_value)) +
  scale_fill_viridis_d() +
  facet_grid(~scenario_sharing)

############
sample <- data %>%
  group_by(income, scenario_adopt, scenario_sharing, strategy_short) %>% #, grid_type
  summarize(
    value = round(sum(total_sulpher_dioxide_tonnes)),
  )

sample$value = sample$value / 1e6

sample = spread(sample, scenario_adopt, value)

totals <- sample %>%
  group_by(scenario_sharing, strategy_short) %>%
  summarize(value = round(sum(baseline), 1))

df_errorbar <- 
  sample |>
  group_by(income, scenario_sharing, strategy_short) |>
  summarize(
    low = sum(low),
    baseline = sum(baseline),
    high = sum(high)
  ) |>
  group_by(scenario_sharing, strategy_short) |>
  summarize(
    income = 'LIC', 
    low = sum(low),
    baseline = sum(baseline),
    high = sum(high)
  )

min_value = min(round(df_errorbar$low,3))
max_value = max(round(df_errorbar$high,3)) + .01
min_value[min_value > 0] = 0

suplher_dioxide = ggplot(sample,
                         aes(x=strategy_short, y=baseline, fill=income)) +
  geom_bar(stat="identity", position='stack') +
  geom_errorbar(data=df_errorbar, aes(y = baseline, ymin = low, ymax = high),
                lwd = 0.5, #position = position_dodge(width = .9),
                show.legend = FALSE, width=0.1,  color="#FF0000FF") +
  geom_text(data = df_errorbar,
            aes(label = paste(round(baseline, 2),"")), size = 2,#.25,
            vjust =-.7, hjust =-.2, angle = 0) +
  theme(legend.position = 'none',
        axis.text.x = element_text(angle = 45, hjust=1)) +
  labs(title=expression(paste("Total Cell Site Emissions over 2020-2030 (", SO[x], ") by Infrastructure Sharing Strategy")),
       fill=NULL,
       subtitle = "For 50 GB/Month per user with interval bars reflecting low and high adoption scenarios",
       x = NULL, y=expression(paste("Megatonnes of ", SO[x])), sep="") +
  scale_y_continuous(expand = c(0, 0), limits = c(0, max_value)) +
  scale_fill_viridis_d() +
  facet_grid(~scenario_sharing)

############

sample <- data %>%
  group_by(income, scenario_adopt, scenario_sharing, strategy_short) %>% #, grid_type
  summarize(
    value = round(sum(total_pm10_tonnes)),
  )

sample$value = sample$value / 1e6

sample = spread(sample, scenario_adopt, value)

totals <- sample %>%
  group_by(scenario_sharing, strategy_short) %>%
  summarize(value = round(sum(baseline), 1))

df_errorbar <- 
  sample |>
  group_by(income, scenario_sharing, strategy_short) |>
  summarize(
    low = sum(low),
    baseline = sum(baseline),
    high = sum(high)
  ) |>
  group_by(scenario_sharing, strategy_short) |>
  summarize(
    income = 'LIC', 
    low = sum(low),
    baseline = sum(baseline),
    high = sum(high)
  )

min_value = min(round(df_errorbar$low,3))
max_value = max(round(df_errorbar$high,3)) + .01
min_value[min_value > 0] = 0

pm10 = ggplot(sample,
              aes(x=strategy_short, y=baseline, fill=income)) +
  geom_bar(stat="identity", position='stack') +
  geom_errorbar(data=df_errorbar, aes(y = baseline, ymin = low, ymax = high),
                lwd = 0.5, #position = position_dodge(width = .9),
                show.legend = FALSE, width=0.1,  color="#FF0000FF") +
  geom_text(data = df_errorbar,
            aes(label = paste(round(baseline, 2),"")), size = 2,#.25,
            vjust =-.7, hjust =-.2, angle = 0) +
  theme(legend.position = 'none',
        axis.text.x = element_text(angle = 45, hjust=1)) +
  labs(title=expression(paste("Total Cell Site Emissions over 2020-2030 (", PM[10], ") by Infrastructure Sharing Strategy")),
       fill=NULL,
       subtitle = "For 50 GB/Month per user with interval bars reflecting low and high adoption scenarios",
       x = NULL, y=expression(paste("Megatonnes of ", PM[10])), sep="") + 
  scale_y_continuous(expand = c(0, 0), limits = c(0, max_value)) +
  scale_fill_viridis_d() +
  facet_grid(~scenario_sharing)

############
ggarrange(
  energy,
  carbon_dioxide,
  labels = c("A", "B"),
  ncol = 1, nrow = 2,
  common.legend = TRUE,
  legend = 'bottom')

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
  ncol = 1, nrow = 3,  
  common.legend = TRUE,
  legend = 'bottom')

dir.create(file.path(folder, 'figures', 'global'), showWarnings = FALSE)
path = file.path(folder, 'figures', 'global', 'health_emissions_sharing.png')
ggsave(path, units="in", width=8, height=10, dpi=300)
dir.create(file.path(folder, '..', 'reports', 'images', 'global'), showWarnings = FALSE)
path = file.path(folder, '..', 'reports', 'images', 'global', 'health_emissions_sharing.png')
ggsave(path, units="in", width=8, height=10, dpi=300)
while (!is.null(dev.list()))  dev.off()

