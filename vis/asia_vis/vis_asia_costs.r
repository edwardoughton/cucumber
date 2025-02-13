###VISUALISE MODEL OUTPUTS###
library(tidyverse)
library(ggpubr)

folder <- dirname(rstudioapi::getSourceEditorContext()$path)

filename = 'global_cost_results.csv'
data_all <- read.csv(file.path(folder, '..', '..', 'results', 'global_results', filename))
data = data_all

data = data[(data$sharing_scenario == 'baseline'),]
data = data[(data$energy_scenario == "aps-2030"),]
data$tech = paste(data$generation, data$backhaul)

data = select(data, GID_0, iteration,
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
  group_by(GID_0, iteration, tech, capacity, income, adb_region,) %>%
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
subset = select(data, iteration, income, tech, capacity,
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

max_value = max(round(subset$value_mean,3)) + (max(round(subset$value_mean,3))/4)

plot1 =
  ggplot(subset, aes(x = tech, y = value_mean, fill=reorder(income, -value_mean))) +
  geom_bar(stat="identity", position='dodge') +
  geom_errorbar(data = subset,
                aes(y = value_mean, ymin = value_mean-value_sd, ymax =  value_mean+value_sd),
                position = position_dodge(width = .9),lwd = 0.5,show.legend = FALSE,
                width = 0.1, color = "#FF0000FF") +
  geom_text(aes(label = paste(round(value_mean, 1), ""), 
                y = value_mean + value_sd + (max_value_countries * 0.03)),  
            size = 2, vjust = 0.5, hjust = -0.15,  
            position = position_dodge(.9), angle = 90) +
  theme(legend.position = 'bottom') +
  labs(title=expression(paste("(A) Financial Cost of Universal Broadband by Income Group.")),
       fill=NULL,
       subtitle = "Ordered by magnitude and reported for developing Asia.",
       x = NULL, y="Financial Cost (US$Bn)")  +
  scale_y_continuous(expand = c(0, 0), limits = c(0, max_value * 1.2)) +  
  guides(fill=guide_legend(nrow=1)) +
  scale_fill_viridis_d(breaks=c('Low Income','Lower-Middle Income',
                                'Upper-Middle Income','High Income')) +
  facet_grid(~capacity)

# dir.create(file.path(folder, 'figures'), showWarnings = FALSE)
# path = file.path(folder, 'figures',  'energy.png')
# ggsave(path, units="in", width=8, height=5, dpi=300)
# while (!is.null(dev.list()))  dev.off()

#### Emissions demand: regions
subset = select(data, iteration, adb_region, tech, capacity,
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
  group_by(iteration, adb_region, tech, capacity) %>%
  summarize(
    value = sum(value)
  )

subset <- subset %>%
  ungroup() %>%
  group_by(adb_region, tech, capacity) %>%
  mutate(
    value_mean = round(mean(value)/ 1e9,3), #convert kwh -> twh
    value_sd = round(sd(value)/ 1e9,3)      #convert kwh -> twh
  )

subset = select(subset, adb_region, tech, capacity, value_mean, value_sd)
subset = unique(subset)         

max_value = max(round(subset$value_mean,3)) + + (max(round(subset$value_mean,3))/4)

plot2 =
  ggplot(subset, aes(x = tech, y = value_mean, fill=reorder(adb_region, -value_mean))) +
  geom_bar(stat="identity", position='dodge') +
  geom_errorbar(data = subset,
                aes(y = value_mean, ymin = value_mean-value_sd, ymax =  value_mean+value_sd),
                position = position_dodge(width = .9),lwd = 0.5,show.legend = FALSE,
                width = 0.1, color = "#FF0000FF") +
  geom_text(aes(label = paste(round(value_mean, 1), ""), 
                y = value_mean + value_sd + (max_value_countries * 0.03)),  
            size = 2, vjust = 0.5, hjust = -0.15,  
            position = position_dodge(.9), angle = 90) +
  theme(legend.position = 'bottom') +
    labs(title=expression(paste("(B) Financial Cost of Universal Broadband by Region.")),
         fill=NULL,
         subtitle = "Ordered by magnitude and reported for developing Asia.",
         x = NULL, y="Financial Cost (US$Bn)")  +
  scale_y_continuous(expand = c(0, 0), limits = c(0, max_value * 1.2)) +  
  scale_fill_viridis_d(breaks=c('Caucasus and Central Asia','East Asia',
                                'South Asia','Southeast Asia','The Pacific')) +
  facet_grid(~capacity)

############
subset = select(data, iteration, GID_0, tech, capacity,
                total_cost_equipment_usd,
                total_cost_backhaul_usd,
                total_cost_site_build_usd,
                total_cost_installation_usd,
                total_cost_operation_and_maintenance_usd,
                total_cost_power_usd)

top_countries <- c("CHN", "IND", "IDN", "PAK")
subset <- subset %>%
  filter(GID_0 %in% top_countries)

subset <- subset %>%
  pivot_longer(
    cols = `total_cost_equipment_usd`:`total_cost_power_usd`,
    names_to = "metric",
    values_to = "value"
  )

subset <- subset %>%
  group_by(iteration, GID_0, tech, capacity) %>%
  summarize(value = sum(value), .groups = "drop")

# Compute mean and standard deviation per country, tech, and capacity
subset <- subset %>%
  group_by(GID_0, tech, capacity) %>%
  mutate(
    value_mean = round(mean(value) / 1e9, 3), # Convert USD to billion USD
    value_sd = round(sd(value) / 1e9, 3)      # Convert USD to billion USD
  ) %>%
  ungroup()

# Select distinct rows for plotting
subset = subset %>%
  select(GID_0, tech, capacity, value_mean, value_sd) %>%
  unique()

subset$GID_0 = factor(
  subset$GID_0,
  levels = c('CHN', 'IND', 'IDN', 'PAK'),
  labels = c('China', 'India', 'Indonesia', 'Pakistan')
)

# Define maximum value for scaling
max_value = max(round(subset$value_mean,3)) + (max(round(subset$value_mean,3))/4)
top_countries <- c('China', 'India', 'Indonesia', 'Pakistan')

# Generate plot
plot3 = ggplot(subset, aes(x = tech, y = value_mean, fill = reorder(GID_0, -value_mean))) +
  geom_bar(stat="identity", position='dodge') +
  geom_errorbar(
    aes(y = value_mean, ymin = value_mean - value_sd, ymax = value_mean + value_sd),
    position = position_dodge(width = .9), lwd = 0.5, show.legend = FALSE,
    width = 0.1, color = "#FF0000FF"
  ) +
  geom_text(aes(label = paste(round(value_mean, 1), ""), 
                y = value_mean + value_sd + (max_value_countries * 0.03)),  
            size = 2, vjust = 0.5, hjust = -0.15,  
            position = position_dodge(.9), angle = 90) +
  theme(legend.position = 'bottom') +
  labs(
    title = "(C) Financial Cost of Universal Broadband by Top Four Countries.",
    fill = NULL,
    subtitle = "Ordered by magnitude and reported for selected Asian countries.",
    x = NULL, y = "Financial Cost (US$Bn)"
  ) +
  scale_y_continuous(expand = c(0, 0), limits = c(0, max_value * 1.2)) +  
  scale_fill_viridis_d(breaks = c("China", "India", "Indonesia", "Pakistan")) +
  facet_grid(~capacity)

################
adjusted_legend_theme <- theme(
  legend.margin = margin(-10, 0, 0, 0),  # Moves legend up
  legend.position = 'bottom'
)

plot1 <- plot1 + adjusted_legend_theme
plot2 <- plot2 + adjusted_legend_theme
plot3 <- plot3 + adjusted_legend_theme

panel <- ggarrange(
  plot1, plot2, plot3,
  ncol = 1, nrow = 3,
  common.legend = FALSE,
  legend = 'bottom',
  heights = c(1, 1, 1)  # Equal height distribution
)

dir.create(file.path(folder, 'figures'), showWarnings = FALSE)
folder <- dirname(rstudioapi::getSourceEditorContext()$path)
path = file.path(folder, 'figures', 'g_costs_panel.png')
ggsave(path, units="in", width=8, height=8, dpi=300)
while (!is.null(dev.list()))  dev.off()
