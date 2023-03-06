###VISUALISE MODEL OUTPUTS###
library(tidyverse)
library(ggpubr)

threshold = 10

folder <- dirname(rstudioapi::getSourceEditorContext()$path)

# filename = 'national_market_cost_results_technology_options.csv'
filename = 'decile_market_cost_results_technology_options.csv'
data <- read.csv(file.path(folder, '..', 'results', 'global_results', filename))

data$scenario_capacity = ''
data$scenario_capacity[grep("25_25_25", data$scenario)] = '25 GB/Month'
data$scenario_capacity[grep("50_50_50", data$scenario)] = '50 GB/Month'
data$scenario_capacity[grep("100_100_100", data$scenario)] = '100 GB/Month'

data = data[(data$scenario_capacity == '25 GB/Month' |
               data$scenario_capacity == '50 GB/Month' |
               data$scenario_capacity == '100 GB/Month'),]

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

country_info = read_csv(file.path(folder, '..', 'data','raw', 'countries.csv'))
country_info = select(country_info, iso3, continent)
data = merge(data, country_info, by.x="GID_0", by.y="iso3")

data$scenario_capacity = ''
data$scenario_capacity[grep("25_25_25", data$scenario)] = '25 GB/Month'
data$scenario_capacity[grep("50_50_50", data$scenario)] = '50 GB/Month'
data$scenario_capacity[grep("100_100_100", data$scenario)] = '100 GB/Month'
# data$scenario_capacity[grep("100_100_100", data$scenario)] = '100 GB/Month'

# data = data[(data$scenario_capacity != '100 GB/Month'),]
# test = select(data, GID_0, total_ran, total_backhaul_fronthaul, scenario, strategy)
# test$total_backhaul_fronthaul = round(test$total_backhaul_fronthaul/1e9,1)              

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
data$scenario_adopt[grep("low", data$scenario)] = 'Low (1% Adoption CAGR)'
data$scenario_adopt[grep("baseline", data$scenario)] = 'Baseline (2% Adoption CAGR)'
data$scenario_adopt[grep("high", data$scenario)] = 'High (4% Adoption CAGR)'

data$scenario_capacity = ''
data$scenario_capacity[grep("25_25_25", data$scenario)] = '25 GB/Month'
data$scenario_capacity[grep("50_50_50", data$scenario)] = '50 GB/Month'
data$scenario_capacity[grep("100_100_100", data$scenario)] = '100 GB/Month'

data$strategy_short = ''
# data$strategy_short[grep("3G_umts_fiber", data$strategy)] = '3G (F)'
# data$strategy_short[grep("3G_umts_wireless", data$strategy)] = '3G (W)'
data$strategy_short[grep("4G_epc_fiber", data$strategy)] = '4G (F)'
data$strategy_short[grep("4G_epc_wireless", data$strategy)] = '4G (W)'
data$strategy_short[grep("5G_nsa_fiber", data$strategy)] = '5G (F)'
data$strategy_short[grep("5G_nsa_wireless", data$strategy)] = '5G (W)'

# data$strategy_short = factor(data$strategy_short, levels=c(
#                                      # "3G (F)",
#                                      "4G (F)",
#                                      '5G (F)',
#                                      # "3G (W)",
#                                      "4G (W)",
#                                      '5G (W)'
#                                      ))

data$strategy_short = factor(data$strategy_short, levels=c(
  "4G (F)",
  "4G (W)",
  '5G (F)',
  '5G (W)'
))
# unique(data$scenario_capacity)

data$scenario_capacity = factor(data$scenario_capacity,
                                levels=c('25 GB/Month', #'20 GB/Month',
                                         '50 GB/Month',#'40 GB/Month',
                                         '100 GB/Month'#'60 GB/Month'#,
                                         # '100 GB/Month'
                                ))

data = data[complete.cases(data), ]

data$scenario_adopt = factor(data$scenario_adopt, 
                             levels=c("Low (1% Adoption CAGR)",
                                      "Baseline (2% Adoption CAGR)",
                                      "High (4% Adoption CAGR)"))

# data <- data[(data$confidence == 50),]

data <- select(data, scenario_adopt, scenario_capacity, strategy_short, 
               # cost_per_network_user, cost_per_smartphone_user, 
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

print(coverage)

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

# data$scenario_capacity = ''
# data$scenario_capacity[grep("25_25_25", data$scenario)] = '25 GB/Month'
# data$scenario_capacity[grep("50_50_50", data$scenario)] = '50 GB/Month'
# data$scenario_capacity[grep("100_100_100", data$scenario)] = '100 GB/Month'
# 
# data = data[(data$scenario_capacity == '25 GB/Month' |
#                data$scenario_capacity == '50 GB/Month' |
#                data$scenario_capacity == '100 GB/Month'),]
# 
# data$pop_density_km2 = round(data$population_total / data$area_km2,1)
# 
# excluded = data[(data$pop_density_km2 < threshold),]
# excluded = excluded[(excluded$scenario == "baseline_50_50_50" &
#                        excluded$strategy == "4G_epc_fiber_baseline_baseline_baseline_baseline_baseline"),]
# ex_sum = sum(excluded$population_total)
# 
# included = data[(data$pop_density_km2 > threshold),]
# included = included[(included$scenario == "baseline_50_50_50" &
#                        included$strategy == "4G_epc_fiber_baseline_baseline_baseline_baseline_baseline"),]
# inc_sum = sum(included$population_total)
# coverage = round(inc_sum/(inc_sum + ex_sum) * 100,1)
# 
# data = data[(data$pop_density_km2 > threshold),]

country_info = read_csv(file.path(folder, '..', 'data','raw', 'countries.csv'))
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

# filename = 'national_market_cost_results_business_model_options.csv'
# data <- read.csv(file.path(folder, '..', 'results', 'model_results', 'COL', filename))
#
# names(data)[names(data) == 'GID_0'] <- 'country'

data$scenario_adopt = ''
data$scenario_adopt[grep("low", data$scenario)] = 'Low (1% Adoption CAGR)'
data$scenario_adopt[grep("baseline", data$scenario)] = 'Baseline (2% Adoption CAGR)'
data$scenario_adopt[grep("high", data$scenario)] = 'High (4% Adoption CAGR)'
data$scenario_capacity = ''
data$scenario_capacity[grep("25_25_25", data$scenario)] = '25 GB/Month'
data$scenario_capacity[grep("50_50_50", data$scenario)] = '50 GB/Month'
data$scenario_capacity[grep("100_100_100", data$scenario)] = '100 GB/Month'

data$strategy_short = ''
data$strategy_short[grep("4G_epc_wireless", data$strategy)] = '4G (W)'

# data = data %>%
#   filter(data$strategy_short == '4G (W)')

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
                                         '100 GB/Month'
                                ))

data$scenario_adopt = factor(data$scenario_adopt, 
                             levels=c("Low (1% Adoption CAGR)",
                                      "Baseline (2% Adoption CAGR)",
                                      "High (4% Adoption CAGR)"))

# data <- data[(data$confidence == 50),]

data <- select(data, scenario_adopt, scenario_capacity, strategy,
               # cost_per_network_user, cost_per_smartphone_user,
               private_cost, government_cost, societal_cost)

totals <- data %>%
  group_by(scenario_adopt, scenario_capacity, strategy) %>%
  summarize(social_cost = round(
    (societal_cost)/1e12,2))

min_value = min(round(totals$social_cost))
max_value = max(round(totals$social_cost)) + 1.5
min_value[min_value > 0] = 0

data$social_cost = data$private_cost + data$government_cost
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
data$scenario_adopt[grep("low", data$scenario)] = 'Low (1% Adoption CAGR)'
data$scenario_adopt[grep("baseline", data$scenario)] = 'Baseline (2% Adoption CAGR)'
data$scenario_adopt[grep("high", data$scenario)] = 'High (4% Adoption CAGR)'

data$scenario_capacity = ''
data$scenario_capacity[grep("25_25_25", data$scenario)] = '25 GB/Month'
data$scenario_capacity[grep("50_50_50", data$scenario)] = '50 GB/Month'
data$scenario_capacity[grep("100_100_100", data$scenario)] = '100 GB/Month'

data$strategy_short = ''
data$strategy_short[grep("4G_epc_wireless", data$strategy)] = '4G (W)'

# data = data %>% filter(data$strategy_short == '4G (W)')

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
                                         '100 GB/Month'
                                ))

data$scenario_adopt = factor(data$scenario_adopt, 
                             levels=c("Low (1% Adoption CAGR)",
                                      "Baseline (2% Adoption CAGR)",
                                      "High (4% Adoption CAGR)"))

# data <- data[(data$confidence == 50),]

data <- select(data, scenario_adopt, scenario_capacity, strategy,
               # cost_per_network_user, cost_per_smartphone_user,
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

