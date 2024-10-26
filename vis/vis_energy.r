###VISUALISE MODEL OUTPUTS###
library(tidyverse)
library(ggpubr)

folder <- dirname(rstudioapi::getSourceEditorContext()$path)

filename = 'global_results.csv'
test <- read.csv(file.path(folder, '..', 'results', 'global_results', filename))

data = test
# data = data[(data$GID_0 == 'ARM'),]

data = data[(data$sharing_scenario == 'baseline'),]
data$tech = paste(data$generation, data$backhaul)

data = select(data, GID_0, iteration,
              tech, capacity, energy_scenario,
              income, wb_region,
              population_total, area_km2,
              # population_with_phones,
              population_with_smartphones,
              total_existing_sites, total_existing_sites_4G, total_new_sites,
              total_existing_energy_kwh, total_new_energy_kwh,
              total_new_emissions_t_co2,
              total_existing_emissions_t_co2,
              total_new_cost_usd
)

data = data %>%
  group_by(GID_0, iteration, tech, capacity, energy_scenario,
           income, wb_region) %>%
  summarise(
    population_total = round(sum(population_total, na.rm=TRUE),0),
    area_km2 = round(sum(area_km2, na.rm=TRUE),0),
    # population_with_phones = round(sum(population_with_phones, na.rm=TRUE),0),
    population_with_smartphones = round(sum(population_with_smartphones, na.rm=TRUE),0),
    # total_existing_sites = round(sum(total_existing_sites, na.rm=TRUE),0),
    # total_existing_sites_4G = round(sum(total_existing_sites_4G, na.rm=TRUE),0),
    # total_new_sites = round(sum(total_new_sites, na.rm=TRUE),0),
    total_existing_energy_kwh = round(sum(total_existing_energy_kwh, na.rm=TRUE),0),
    total_new_energy_kwh = round(sum(total_new_energy_kwh, na.rm=TRUE),0),
    # total_new_emissions_t_co2 = round(sum(total_new_emissions_t_co2, na.rm=TRUE),2),
    # total_existing_emissions_t_co2 = round(sum(total_existing_emissions_t_co2, na.rm=TRUE),2)#,
    # total_new_cost_usd = round(sum(total_new_cost_usd, na.rm=TRUE),0)
)

data$tech = factor(
  data$tech,
  levels = c("4G wireless","4G fiber","5G wireless","5G fiber"),
  labels = c('4G (W)','4G (F)', '5G (W)', '5G (F)')
)

data$capacity = factor(
  data$capacity,
  levels = c(10, 20, 30),
  labels = c('10 GB / Month / Smartphone', 
             '20 GB / Month / Smartphone', 
             '30 GB / Month / Smartphone')
)

data$energy_scenario = factor(
  data$energy_scenario,
  levels = c("sps-2022","sps-2030","aps-2030"),
  labels = c("Stated Policy Scenario 2022",
             "Stated Policy Scenario 2030",
             "Announced Policy Scenario 2030")
)

data = data[(data$energy_scenario == "Announced Policy Scenario 2030"),]

#### Emissions: income group
subset = select(data, iteration, income, tech, capacity,
                total_existing_energy_kwh, total_new_energy_kwh)

subset <- subset %>%
  pivot_longer(
    cols = `total_existing_energy_kwh`:`total_new_energy_kwh`,
    names_to = "metric",
    values_to = "value"
  )

subset$income = factor(
  subset$income,
  levels = c('LIC','LMIC','UMIC','HIC'),
  labels = c('Low Income Country (LIC)','Lower-Middle Income Country (LMIC)',
             'Upper-Middle Income Country (LMIC)','High Income Country (HIC)')
)

subset <- subset %>%
  group_by(iteration, income, tech, capacity) %>%
  summarize(
    value = sum(value)
    )

subset <- subset %>%
  ungroup() %>%
  group_by(income, tech, capacity) %>%
  mutate(
    value_mean = round(mean(value)/ 1e9,3), #convert kwh -> twh
    value_sd = round(sd(value)/ 1e9,3)      #convert kwh -> twh
  )

subset = select(subset, income, tech, capacity, value_mean, value_sd)
subset = unique(subset)         

max_value = max(round(subset$value_mean,3)) + (max(round(subset$value_mean,3))/5)

plot1 = ggplot(subset, aes(x = tech, y = value_mean, fill=income)) +
  geom_bar(stat="identity", position='dodge') +
  geom_errorbar(
    data = subset,
    aes(y = value_mean, ymin = value_mean-value_sd, ymax =  value_mean+value_sd),
    position = position_dodge(width = .9),
    lwd = 0.5,
    show.legend = FALSE,
    width = 0.1,
    color = "#FF0000FF"
  ) +
  geom_text(aes(label = paste(round(value_mean,0),"")), size=2, vjust=-.5,hjust=-.2,
              position = position_dodge(.9), angle=90) +
  theme(legend.position = 'bottom',
        axis.text.x = element_text(angle = 45, hjust=1, size =8,vjust=1)) +
  labs(title="(A) Total Mobile Site Energy Consumption by World Bank Income Group.",
       fill=NULL,
       subtitle = "Reported for the IEA Announced Policy Scenario 2030.",
       x = NULL, y="Kilowatt Hours (kWh)")  +
  scale_y_continuous(expand = c(0, 0), limits = c(0, max_value)) +
  guides(fill=guide_legend(nrow=2)) +
  scale_fill_viridis_d() +
  facet_grid(~capacity)


#### Emissions demand: regions
subset = select(data, iteration, wb_region, tech, capacity,
                total_existing_energy_kwh, total_new_energy_kwh)

subset <- subset %>%
  pivot_longer(
    cols = `total_existing_energy_kwh`:`total_new_energy_kwh`,
    names_to = "metric",
    values_to = "value"
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

subset <- subset %>%
  group_by(iteration, wb_region, tech, capacity) %>%
  summarize(
    value = sum(value)
  )

subset <- subset %>%
  ungroup() %>%
  group_by(wb_region, tech, capacity) %>%
  mutate(
    value_mean = round(mean(value)/ 1e9,3), #convert kwh -> twh
    value_sd = round(sd(value)/ 1e9,3)      #convert kwh -> twh
  )

subset = select(subset, wb_region, tech, capacity, value_mean, value_sd)
subset = unique(subset)         

max_value = max(round(subset$value_mean,3)) + + (max(round(subset$value_mean,3))/5)

plot2 =
  ggplot(subset, aes(x = tech, y = value_mean, fill=wb_region)) +
  geom_bar(stat="identity", position='dodge') +
  geom_errorbar(
    data = subset,
    aes(y = value_mean, ymin = value_mean-value_sd, ymax =  value_mean+value_sd),
    position = position_dodge(width = .9),
    lwd = 0.5,
    show.legend = FALSE,
    width = 0.1,
    color = "#FF0000FF"
  ) +
  geom_text(aes(label = paste(round(value_mean,0),"")), size=2, vjust=.5,hjust=-.2,
            position = position_dodge(.9), angle=90) +
  theme(legend.position = 'bottom',
        axis.text.x = element_text(angle = 45, hjust=1)) +
  labs(title="(B) Total Mobile Site Energy Consumption by World Bank Region.",
       fill=NULL,
       subtitle = "Reported for the IEA Announced Policy Scenario 2030.",
       x = NULL, y="Terawatt Hours (tWhs)")  +
  scale_y_continuous(expand = c(0, 0), limits = c(0, max_value)) +
  scale_fill_viridis_d() +
  facet_grid(~capacity)

panel = ggarrange(
  plot1,
  plot2,
  # labels = c("A", "B", "C"),
  ncol = 1, nrow = 2,
  common.legend = FALSE,
  legend = 'bottom')

dir.create(file.path(folder, 'figures'), showWarnings = FALSE)
path = file.path(folder, 'figures', 'energy_panel.png')
ggsave(path, units="in", width=8, height=8, dpi=300)
while (!is.null(dev.list()))  dev.off()

# #### emissions: new vs old
# subset = select(data, tech, capacity, income,
#                 total_existing_energy_kwh, total_new_energy_kwh)
# 
# subset <- subset %>%
#   pivot_longer(
#     cols = `total_existing_energy_kwh`:`total_new_energy_kwh`,
#     names_to = "metric",
#     values_to = "value"
#   )
# 
# subset$income = factor(
#   subset$income,
#   levels = c('LIC','LMIC','UMIC','HIC'),
#   labels = c('Low Income\nCountries (LICs)','Lower-Middle Income\nCountries (LMICs)',
#              'Upper-Middle Income\nCountries (LMICs)','High Income\nCountries (HICs)')
# )
# 
# subset$metric = factor(
#   subset$metric,
#   levels = c('total_new_energy_kwh','total_existing_energy_kwh'),
#   labels = c('New', 'Existing')
# )
# 
# subset <- subset %>%
#   group_by(metric, tech, capacity, income) %>%
#   summarize(
#     value = sum(value)
#   )
# 
# subset$value = subset$value / 1e9 #convert kwh -> twh
# 
# df_errorbar <-
#   subset |>
#   group_by(metric, tech, capacity, income) |>
#   summarize(
#     # low = sum(low),
#     value = sum(value)#,
#     # high = sum(high)
#   ) |>
#   group_by(tech, capacity, income) |>
#   summarize(
#     metric = 'New',
#     # low = sum(low),
#     value = sum(value)#,
#     # high = sum(high)
#   )
# 
# max_value = max(round(df_errorbar$value,3)) + (max(round(df_errorbar$value,3))/5)
# 
# plot3 =
#   ggplot(subset, aes(x = tech, y = value, fill=metric)) +
#   geom_bar(stat="identity", position='stack') +
#   geom_text(data = df_errorbar,
#             aes(label = paste(round(value,0),"")), size = 2,angle=0,
#             vjust =-0.7, hjust =.3, angle = 0)+
#   theme(legend.position = 'bottom',
#         axis.text.x = element_text(angle = 45, hjust=1)) +
#   labs(title="Total Mobile Site Energy Consumption by Income Group",
#        fill=NULL,
#        subtitle = "Reported for the IEA Announced Policy Scenario 2030.",
#        x = NULL, y="Terawatt Hours")  +
#   scale_y_continuous(expand = c(0, 0), limits = c(0, max_value)) +
#   scale_fill_viridis_d() +
#   facet_grid(income~capacity)
# 
# dir.create(file.path(folder, 'figures'), showWarnings = FALSE)
# path = file.path(folder, 'figures', 'energy_new_vs_existing_income.png')
# ggsave(path, units="in", width=8, height=8, dpi=300)
# while (!is.null(dev.list()))  dev.off()
# 
# #### emissions: new vs old
# subset = select(data, tech, capacity, wb_region,
#                 total_existing_energy_kwh, total_new_energy_kwh)
# 
# subset <- subset %>%
#   pivot_longer(
#     cols = `total_existing_energy_kwh`:`total_new_energy_kwh`,
#     names_to = "metric",
#     values_to = "value"
#   )
# 
# subset$wb_region = factor(
#   subset$wb_region,
#   levels = c('East Asia and Pacific','Europe and Central Asia',
#              'Latin America and Caribbean','Middle East and North Africa',
#              'North America','South Asia','Sub-Saharan Africa'
#   ),
#   labels = c('East Asia\nand Pacific','Europe and\nCentral Asia',
#              'Latin America and\nCaribbean','Middle East and\nNorth Africa',
#              'North\nAmerica','South\nAsia','Sub-Saharan\nAfrica')
# )
# 
# subset$metric = factor(
#   subset$metric,
#   levels = c('total_new_energy_kwh','total_existing_energy_kwh'),
#   labels = c('New', 'Existing')
# )
# 
# subset <- subset %>%
#   group_by(metric, tech, capacity, wb_region) %>%
#   summarize(
#     value = sum(value)
#   )
# 
# subset$value = subset$value / 1e9 #convert kwh -> twh
# 
# # totals <- subset %>%
# #   group_by(tech, capacity) %>%
# #   summarize(value = signif(sum(value))) #convert kwh -> twh
# 
# df_errorbar <-
#   subset |>
#   group_by(metric, tech, capacity, wb_region) |>
#   summarize(
#     # low = sum(low),
#     value = sum(value)#,
#     # high = sum(high)
#   ) |>
#   group_by(tech, capacity, wb_region) |>
#   summarize(
#     metric = 'New',
#     # low = sum(low),
#     value = sum(value)#,
#     # high = sum(high)
#   )
# 
# max_value = max(round(df_errorbar$value,3)) + (max(round(df_errorbar$value,3))/5)
# 
# plot4 =
#   ggplot(subset, aes(x = tech, y = value, fill=metric)) +
#   geom_bar(stat="identity", position='stack') +
#   geom_text(data = df_errorbar,
#             aes(label = paste(round(value,1),"")), size = 2,angle=0,
#             vjust =-0.7, hjust =.3, angle = 0)+
#   theme(legend.position = 'bottom',
#         axis.text.x = element_text(angle = 45, hjust=1)) +
#   labs(title="Total Mobile Site Energy Consumption by Income Group",
#        fill=NULL,
#        subtitle = "Reported for the IEA Announced Policy Scenario 2030.",
#        x = NULL, y="Terawatt Hours") +
#   scale_y_continuous(expand = c(0, 0), limits = c(0, max_value)) +
#   scale_fill_viridis_d() +
#   facet_grid(wb_region~capacity)
# 
# dir.create(file.path(folder, 'figures'), showWarnings = FALSE)
# path = file.path(folder, 'figures', 'energy_new_vs_existing_regions.png')
# ggsave(path, units="in", width=8, height=10, dpi=300)
# while (!is.null(dev.list()))  dev.off()
