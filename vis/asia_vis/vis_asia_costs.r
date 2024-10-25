###VISUALISE MODEL OUTPUTS###
library(tidyverse)
library(ggpubr)

folder <- dirname(rstudioapi::getSourceEditorContext()$path)

filename = 'global_cost_results.csv'
data <- read.csv(file.path(folder, '..', '..','results', 'global_results', filename))

data = data[(data$sharing_scenario == 'baseline'),]
data = data[(data$energy_scenario == "aps-2030"),]
data$tech = paste(data$generation, data$backhaul)

data = select(data, GID_0, #capacity,
              tech, capacity, energy_scenario,
              income, adb_region,
              # population_total, area_km2,
              # population_with_phones,
              population_with_smartphones,
              total_cost_equipment_usd,
              total_cost_backhaul_usd,
              total_cost_site_build_usd,
              total_cost_installation_usd,
              total_cost_operation_and_maintenance_usd,
              total_cost_power_usd,
)

data = data %>%
  group_by(GID_0, tech, capacity, income, adb_region,) %>%
  summarise(
    # population_total = round(sum(population_total, na.rm=TRUE),0),
    # area_km2 = round(sum(area_km2, na.rm=TRUE),0),
    # population_with_phones = round(sum(population_with_phones, na.rm=TRUE),0),
    population_with_smartphones = round(sum(population_with_smartphones, na.rm=TRUE),0),
    total_cost_equipment_usd = sum(total_cost_equipment_usd),
    total_cost_backhaul_usd = sum(total_cost_backhaul_usd),
    total_cost_site_build_usd = sum(total_cost_site_build_usd),
    total_cost_installation_usd = sum(total_cost_installation_usd),
    total_cost_operation_and_maintenance_usd = sum(total_cost_operation_and_maintenance_usd),
    total_cost_power_usd = sum(total_cost_power_usd),
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

#### Costs: income group
subset = select(data, income, tech, capacity,
                total_cost_equipment_usd,
                total_cost_backhaul_usd,
                total_cost_site_build_usd,
                total_cost_installation_usd,
                total_cost_operation_and_maintenance_usd,
                total_cost_power_usd)

subset <- subset %>%
  pivot_longer(
    cols = `total_cost_equipment_usd`:`total_cost_power_usd`,
    names_to = "metric",
    values_to = "value"
  )

subset$income = factor(
  subset$income,
  levels = c('LIC','LMIC','UMIC','HIC'),
  labels = c('Low Income','Lower-Middle Income',
             'Upper-Middle Income','High Income')
)

subset <- subset %>%
  group_by(income, tech, capacity) %>%
  summarize(
    value = sum(value)
    )

subset$value = subset$value / 1e9 

max_value = max(round(subset$value,3)) + (max(round(subset$value,3))/5)

plot1 =
  ggplot(subset, aes(x = tech, y = value, fill=income)) +
  geom_bar(stat="identity", position='dodge') +
  geom_text(aes(label = paste(round(value,0),"")), size=2, vjust=.5,hjust=-.2,
              position = position_dodge(.9), angle=90) +
  theme(legend.position = 'bottom',
        axis.text.x = element_text(angle = 45, hjust=1, size =8,vjust=1)) +
  labs(title=expression(paste("(A) Financial Cost of Universal Broadband by Income Group.")),
       fill=NULL,
       subtitle = "Reported for Emerging Asia.",
       x = NULL, y="Financial Cost (US$Bn)")  +
  scale_y_continuous(expand = c(0, 0), limits = c(0, max_value)) +
  guides(fill=guide_legend(nrow=1)) +
  scale_fill_viridis_d() +
  facet_grid(~capacity)

# dir.create(file.path(folder, 'figures'), showWarnings = FALSE)
# path = file.path(folder, 'figures',  'energy.png')
# ggsave(path, units="in", width=8, height=5, dpi=300)
# while (!is.null(dev.list()))  dev.off()

#### Emissions demand: regions
subset = select(data, adb_region, tech, capacity,
                total_cost_equipment_usd,
                total_cost_backhaul_usd,
                total_cost_site_build_usd,
                total_cost_installation_usd,
                total_cost_operation_and_maintenance_usd,
                total_cost_power_usd)

subset <- subset %>%
  pivot_longer(
    cols = `total_cost_equipment_usd`:`total_cost_power_usd`,
    names_to = "metric",
    values_to = "value"
  )

subset$adb_region = factor(
  subset$adb_region,
  levels = c('Caucasus and Central Asia','East Asia',
             'South Asia','Southeast Asia','The Pacific'
  ),
  labels = c('Caucasus and Central Asia','East Asia',
             'South Asia','Southeast Asia','The Pacific')
)

subset <- subset %>%
  group_by(adb_region, tech, capacity) %>%
  summarize(
    value = sum(value)
  )

subset$value = subset$value / 1e9 #convert t -> mt

# df_errorbar <-
#   subset |>
#   group_by(wb_region, tech, energy_scenario) |>
#   summarize(
#     # low = sum(low),
#     value = sum(value)#,
#     # high = sum(high)
#   ) |>
#   group_by(tech, energy_scenario) |>
#   summarize(
#     wb_region = 'South Asia',
#     # low = sum(low),
#     value = sum(value)#,
#     # high = sum(high)
#   )

# min_value = min(round(df_errorbar$low,3))
# max_value = max(round(df_errorbar$high,3)) + .5
max_value = max(round(subset$value,3)) + + (max(round(subset$value,3))/5)

plot2 =
  ggplot(subset, aes(x = tech, y = value, fill=adb_region)) +
  geom_bar(stat="identity", position='dodge') +
  geom_text(aes(label = paste(round(value,0),"")), size=2, vjust=.5,hjust=-.2,
            position = position_dodge(.9), angle=90) +
  theme(legend.position = 'bottom',
        axis.text.x = element_text(angle = 45, hjust=1)) +
    labs(title=expression(paste("(B) Financial Cost of Universal Broadband by Region.")),
         fill=NULL,
         subtitle = "Reported for Emerging Asia.",
         x = NULL, y="Financial Cost (US$Bn)")  +
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
path = file.path(folder, 'figures', 'g_costs_panel.png')
ggsave(path, units="in", width=8, height=8, dpi=300)
while (!is.null(dev.list()))  dev.off()
