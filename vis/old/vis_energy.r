###VISUALISE MODEL OUTPUTS###
library(tidyverse)
library(ggpubr)

folder <- dirname(rstudioapi::getSourceEditorContext()$path)

filename = 'global_results.csv'
data <- read.csv(file.path(folder, '..', 'results', 'global_results', filename))

data$tech = paste(data$generation, data$backhaul, data$capacity)

data = select(data, GID_0, #capacity, 
              tech, energy_scenario,
              income, wb_region,
              population_total, area_km2, 
              # population_with_phones, 
              population_with_smartphones,
              total_existing_sites, total_existing_sites_4G, total_new_sites,
              total_existing_energy_kwh, total_new_energy_kwh,
              total_new_emissions_t_co2, total_existing_emissions_t_co2,
              total_new_cost_usd
              )

data = data %>%
  group_by(GID_0, tech, energy_scenario,
           income, wb_region) %>%
  summarise(
    population_total = round(sum(population_total, na.rm=TRUE),0), 
    area_km2 = round(sum(area_km2, na.rm=TRUE),0), 
    # population_with_phones = round(sum(population_with_phones, na.rm=TRUE),0), 
    population_with_smartphones = round(sum(population_with_smartphones, na.rm=TRUE),0),
    total_existing_sites = round(sum(total_existing_sites, na.rm=TRUE),0), 
    total_existing_sites_4G = round(sum(total_existing_sites_4G, na.rm=TRUE),0), 
    total_new_sites = round(sum(total_new_sites, na.rm=TRUE),0),
    total_existing_energy_kwh = round(sum(total_existing_energy_kwh, na.rm=TRUE),0), 
    total_new_energy_kwh = round(sum(total_new_energy_kwh, na.rm=TRUE),0),
    total_new_emissions_t_co2 = round(sum(total_new_emissions_t_co2, na.rm=TRUE),0), 
    total_existing_emissions_t_co2 = round(sum(total_existing_emissions_t_co2, na.rm=TRUE),0),
    total_new_cost_usd = round(sum(total_new_cost_usd, na.rm=TRUE),0)
 )

# data$capacity[grep("20", data$capacity)] = '20 GB/Month'
# data$capacity[grep("30", data$capacity)] = '30 GB/Month'
# data$capacity[grep("40", data$capacity)] = '40 GB/Month'

# data$tech[grep("4G wireless 20", data$tech)] = '4G (W) 20 GB/Month'
# data$tech[grep("4G wireless 30", data$tech)] = '4G (W) 30 GB/Month'
# data$tech[grep("4G wireless 40", data$tech)] = '4G (W) 40 GB/Month'
# data$tech[grep("4G fiber 20", data$tech)] = '4G (F) 20 GB/Month'
# data$tech[grep("4G fiber 30", data$tech)] = '4G (F) 30 GB/Month'
# data$tech[grep("4G fiber 40", data$tech)] = '4G (F) 40 GB/Month'
# data$tech[grep("5G wireless 20", data$tech)] = '5G (W) 20 GB/Month'
# data$tech[grep("5G wireless 30", data$tech)] = '5G (W) 30 GB/Month'
# data$tech[grep("5G wireless 40", data$tech)] = '5G (W) 40 GB/Month'
# data$tech[grep("5G fiber 20", data$tech)] = '5G (F) 20 GB/Month'
# data$tech[grep("5G fiber 30", data$tech)] = '5G (F) 30 GB/Month'
# data$tech[grep("5G fiber 40", data$tech)] = '5G (F) 40 GB/Month'

data$tech = factor(
  data$tech,
  levels = c(
    "4G wireless 20","4G wireless 30","4G wireless 40",
    "4G fiber 20","4G fiber 30","4G fiber 40",
    "5G wireless 20","5G wireless 30","5G wireless 40",
    "5G fiber 20","5G fiber 30","5G fiber 40"
    ),
  labels = c(
    '4G (W) 20 GB/Month', '4G (W) 30 GB/Month', '4G (W) 40 GB/Month',
    '4G (F) 20 GB/Month', '4G (F) 30 GB/Month', '4G (F) 40 GB/Month',
    '5G (W) 20 GB/Month', '5G (W) 30 GB/Month', '5G (W) 40 GB/Month',
    '5G (F) 20 GB/Month', '5G (F) 30 GB/Month', '5G (F) 40 GB/Month'
    )
)

data$energy_scenario[grep("sps-2022", data$energy_scenario)] = 'SPS 2022'
data$energy_scenario[grep("sps-2030", data$energy_scenario)] = 'SPS 2030'
data$energy_scenario[grep("aps-2030", data$energy_scenario)] = 'APS 2030'


#### Energy demand: new vs old
subset = select(data, tech, energy_scenario, 
                total_existing_energy_kwh, total_new_energy_kwh)

subset <- subset %>%
  group_by(tech, energy_scenario) %>%
  summarize(
    total_existing_energy_kwh = sum(total_existing_energy_kwh)/1e9,
    total_new_energy_kwh = sum(total_new_energy_kwh)/1e9,
    ) 

subset <- subset %>% 
  pivot_longer(
    cols = `total_existing_energy_kwh`:`total_new_energy_kwh`, 
    names_to = "energy",
    values_to = "value"
  )

subset$energy = factor(
  subset$energy,
  levels = c('total_existing_energy_kwh','total_new_energy_kwh'),
  labels = c('Existing', 'New')
)

totals <- subset %>%
  group_by(tech) %>%
  summarize(value = round(sum(value),1)) #convert kwh -> twh

ggplot(subset, aes(x = tech, y = value, fill=energy)) +
  geom_bar(stat="identity", position='stack') +
  # geom_errorbar(data=df_errorbar, aes(y = baseline, ymin = low, ymax = high),
  #               lwd = .5, 
  #               show.legend = FALSE, width=0.1,  color="#FF0000FF") +
  # geom_text(data = totals,
  #           aes(label = value), size = 2,#.25,
  #           vjust =-.7, hjust =-.2, angle = 0) +
  theme(legend.position = 'bottom',
        axis.text.x = element_text(angle = 45, hjust=1)) +
  labs(title=expression(paste("Total Cell Site Energy Demand")),
       fill=NULL,
       subtitle = "Reported for new versus existing energy demand.",
       x = NULL, y=expression(paste("Terawatt hours (TWh)")), sep="")  +
  # scale_y_continuous(expand = c(0, 0), limits = c(0, max_value)) +
  scale_fill_viridis_d() +
  facet_grid(~energy_scenario)

dir.create(file.path(folder, 'figures', 'global'), showWarnings = FALSE)
path = file.path(folder, 'figures', 'global', 'energy_new_vs_existing.png')
ggsave(path, units="in", width=8, height=5, dpi=300)
while (!is.null(dev.list()))  dev.off()

#### Energy demand: income group
subset = select(data, income, tech, energy_scenario, 
                total_existing_energy_kwh, total_new_energy_kwh)

subset <- subset %>%
  pivot_longer(
    cols = `total_existing_energy_kwh`:`total_new_energy_kwh`,
    names_to = "energy",
    values_to = "kwh"
  )

subset$income = factor(
  subset$income,
  levels = c('LIC','LMIC','UMIC','HIC'),
  labels = c('LIC','LMIC','UMIC','HIC')
)

# totals <- subset %>%
#   group_by(tech) %>%
#   summarize(value = signif(sum(kwh)/1e9)) #convert kwh -> twh

ggplot(subset, aes(x = tech, y = kwh/1e9, fill=income)) +
  geom_bar(stat="identity", position='stack') +
  # geom_errorbar(data=df_errorbar, aes(y = baseline, ymin = low, ymax = high),
  #               lwd = .5, 
  #               show.legend = FALSE, width=0.1,  color="#FF0000FF") +
  # geom_text(data = totals,
  #           aes(label = paste(round(value, 1),"")), size = 2,#.25,
  #           vjust =-.7, hjust =-.2, angle = 0)+
  theme(legend.position = 'bottom',
        axis.text.x = element_text(angle = 45, hjust=1)) +
  labs(title=expression(paste("Total Cell Site Energy Demand")),
       fill=NULL,
       subtitle = "Interval bars reflect estimates for low and high adoption scenarios for",
       x = NULL, y=expression(paste("Terawatt hours (TWh)")), sep="")  +
  # scale_y_continuous(expand = c(0, 0), limits = c(0, max_value)) +
  scale_fill_viridis_d() +
  facet_grid(~energy_scenario)

dir.create(file.path(folder, 'figures', 'global'), showWarnings = FALSE)
path = file.path(folder, 'figures', 'global', 'energy_by_income_group.png')
ggsave(path, units="in", width=8, height=5, dpi=300)
while (!is.null(dev.list()))  dev.off()

#### Energy demand: regions
subset = select(data, wb_region, tech, energy_scenario, total_existing_energy_kwh, total_new_energy_kwh)

subset <- subset %>%
  pivot_longer(
    cols = `total_existing_energy_kwh`:`total_new_energy_kwh`,
    names_to = "energy",
    values_to = "kwh"
  )

subset$wb_region = factor(
  subset$wb_region,
  levels = c('East Asia and Pacific','Europe and Central Asia',
             'Latin America and Caribbean','Middle East and North Africa',
             'North America','South Asia','Sub-Saharan Africa'
             ),
  labels = c('East Asia and Pacific','Europe and Central Asia',
             'Latin America and Caribbean','Middle East and North Africa',
             'North America','South Asia','Sub-Saharan Africa')
)

# totals <- subset %>%
#   group_by(tech) %>%
#   summarize(value = signif(sum(kwh)/1e9)) #convert kwh -> twh

ggplot(subset, aes(x = tech, y = kwh/1e9, fill=wb_region)) +
  geom_bar(stat="identity", position='stack') +
  # geom_errorbar(data=df_errorbar, aes(y = baseline, ymin = low, ymax = high),
  #               lwd = .5, 
  #               show.legend = FALSE, width=0.1,  color="#FF0000FF") +
  # geom_text(data = totals,
  #           aes(label = paste(round(value, 1),"")), size = 2,#.25,
  #           vjust =-.7, hjust =-.2, angle = 0)+
  theme(legend.position = 'bottom',
        axis.text.x = element_text(angle = 45, hjust=1)) +
  labs(title=expression(paste("Total Cell Site Energy Demand")),
       fill=NULL,
       subtitle = "Interval bars reflect estimates for low and high adoption scenarios for",
       x = NULL, y=expression(paste("Terawatt hours (TWh)")), sep="")  +
  # scale_y_continuous(expand = c(0, 0), limits = c(0, max_value)) +
  scale_fill_viridis_d() +
  facet_grid(~energy_scenario)

dir.create(file.path(folder, 'figures', 'global'), showWarnings = FALSE)
path = file.path(folder, 'figures', 'global', 'energy_by_region.png')
ggsave(path, units="in", width=8, height=5, dpi=300)
while (!is.null(dev.list()))  dev.off()
