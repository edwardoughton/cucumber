###VISUALISE MODEL OUTPUTS###
library(tidyverse)
library(ggpubr)

folder <- dirname(rstudioapi::getSourceEditorContext()$path)

filename = 'decile_market_cost_results_technology_options.csv'
data <- read.csv(file.path(folder, '..', 'results', 'global_results', filename))

data$scenario_capacity = ''
data$scenario_capacity[grep("50_50_50", data$scenario)] = '50 GB/Month'

metrics = data[(data$scenario == 'baseline_50_50_50' &
    data$strategy == '4G_epc_wireless_baseline_baseline_baseline_baseline_baseline'
    ),]

#GSMA: 1.2tn annual revenue 2030
#6.975 trillion over ~8 years
round(sum(metrics$total_market_revenue)/1e9,0) 
#per year
round((sum(metrics$total_market_revenue)/1e9)/7,0) 

#GSMA: 6.3 unique mobile subs. 2030
#6.3 billion unique mobile subs
round(((sum(metrics$total_phones) / sum(metrics$population_total)) * 100), 1) 

#GSMA: 92% smartphones by 2030
#3.8 billion smartphones
round(((sum(metrics$total_smartphones) / sum(metrics$population_total)) * 100), 1) 

#GSMA: 2023-2030 $1.5 trillion capex
#3.8 billion smartphones
round(sum(metrics$total_ran, metrics$total_backhaul_fronthaul,
      metrics$total_civils, metrics$total_core_network)/1e9,1)
#per year
round((sum(metrics$total_ran, metrics$total_backhaul_fronthaul,
          metrics$total_civils, metrics$total_core_network)/1e9)/7,0)
