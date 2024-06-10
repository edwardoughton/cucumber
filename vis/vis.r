###VISUALISE MODEL OUTPUTS###
library(tidyverse)
library(ggpubr)

folder <- dirname(rstudioapi::getSourceEditorContext()$path)

filename = 'global_results.csv'
data <- read.csv(file.path(folder, '..', 'results', 'global_results', filename))

data = select(data, GID_0, capacity, generation, backhaul, energy_scenario,
              income, wb_region,
              population_total, area_km2, 
              population_with_phones, population_with_smartphones,
              total_existing_sites, total_existing_sites_4G, total_new_sites,
              total_existing_energy_kwh, total_new_energy_kwh,
              new_total_emissions_t_co2, existing_total_emissions_t_co2,
              total_new_cost_usd
              )

subset = data %>%
  group_by(GID_0, capacity, generation, backhaul, energy_scenario,
           income, wb_region) %>%
  summarise(
    population_total = round(sum(population_total, na.rm=TRUE),0), 
    area_km2 = round(sum(area_km2, na.rm=TRUE),0), 
    population_with_phones = round(sum(population_with_phones, na.rm=TRUE),0), 
    population_with_smartphones = round(sum(population_with_smartphones, na.rm=TRUE),0),
    total_existing_sites = round(sum(total_existing_sites, na.rm=TRUE),0), 
    total_existing_sites_4G = round(sum(total_existing_sites_4G, na.rm=TRUE),0), 
    total_new_sites = round(sum(total_new_sites, na.rm=TRUE),0),
    total_existing_energy_kwh = round(sum(total_existing_energy_kwh, na.rm=TRUE),0), 
    total_new_energy_kwh = round(sum(total_new_energy_kwh, na.rm=TRUE),0),
    new_total_emissions_t_co2 = round(sum(new_total_emissions_t_co2, na.rm=TRUE),0), 
    existing_total_emissions_t_co2 = round(sum(existing_total_emissions_t_co2, na.rm=TRUE),0),
    total_new_cost_usd = round(sum(total_new_cost_usd, na.rm=TRUE),0)
 )

data$scenario_capacity = ''
data$scenario_capacity[grep("20_20_20", data$scenario)] = '20 GB/Month'
data$scenario_capacity[grep("30_30_30", data$scenario)] = '30 GB/Month'
data$scenario_capacity[grep("40_40_40", data$scenario)] = '40 GB/Month'

data = data[(data$scenario_capacity == '20 GB/Month' |
               data$scenario_capacity == '30 GB/Month' |
               data$scenario_capacity == '40 GB/Month'),]
