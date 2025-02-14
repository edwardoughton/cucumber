###VISUALISE MODEL OUTPUTS###
library(tidyverse)
library(ggpubr)

folder <- dirname(rstudioapi::getSourceEditorContext()$path)
filename = 'global_results.csv'
data_all <- read.csv(file.path(folder, '..', '..', 'results', 'global_results', filename))

data = data_all
# data = data[(data$GID_0 == 'ARM'),]

ls = c("ARM","AZE","GEO","KAZ","KGZ","TJK","TKM","UZB","CHN","HKG","KOR","MNG",
       "TWN","BTN","NPL","MDV","AFG","BGD","IND","PAK","LKA","BRN","KHM","IDN",
       "LAO","MYS","MMR","PHL","SGP","THA","TLS","VNM","FJI","PNG","VUT","COK",
       "KIR","MHL","FSM","NRU","NIU","PLW","WSM","SLB","TON","TUV")
data = data%>% filter(GID_0 %in% ls)
data = data[(data$sharing_scenario == 'baseline'),]
data$tech = paste(data$generation, data$backhaul)

data = select(data, GID_0, iteration,
              tech, capacity, energy_scenario,
              income, adb_region,
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
           income, adb_region) %>%
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
  labels = c('10 GB / month / smartphone',
             '20 GB / month / smartphone', 
             '30 GB / month / smartphone')
)

data$energy_scenario = factor(
  data$energy_scenario,
  levels = c("sps-2022","sps-2030","aps-2030"),
  labels = c("Stated Policy Scenario 2022",
             "Stated Policy Scenario 2030",
             "Announced Policy Scenario 2030")
)

data = data[(data$energy_scenario == "Announced Policy Scenario 2030"),]

data$income = factor(
  data$income,
  levels = c('LIC','LMIC','UMIC','HIC'),
  labels = c('Low income','Lower-middle income',
             'Upper-middle income','High income')
)

data$adb_region = factor(
  data$adb_region,
  levels = c('Caucasus and Central Asia','East Asia',
             'South Asia','Southeast Asia','The Pacific'
  ),
  labels = c('Caucasus and Central Asia','East Asia',
             'South Asia','Southeast Asia','The Pacific')
)

subset = data %>% ungroup()
subset = subset[(subset$iteration == '0'),] 
subset = subset[(subset$capacity == '10 GB / month / smartphone'),]
subset = subset[(subset$tech == '4G (W)'),] 
unique_smartphones = select(subset, GID_0, income, population_with_smartphones)
unique_smartphones = unique(unique_smartphones)
total_smartphones = unique_smartphones %>%
  group_by(income) %>%
  summarize(
    population_with_smartphones = sum(population_with_smartphones)
  )
remove(unique_smartphones)

#### Emissions: income group
subset = data %>% ungroup()
subset = select(subset, iteration, income, tech, capacity,
                total_existing_energy_kwh, total_new_energy_kwh)

subset <- subset %>%
  pivot_longer(
    cols = `total_existing_energy_kwh`:`total_new_energy_kwh`,
    names_to = "metric",
    values_to = "value"
  )

subset <- subset %>%
  group_by(iteration, income, tech, capacity) %>%
  summarize(
    value = sum(value)
  )
subset = subset %>% ungroup()
subset = merge(subset, total_smartphones)
subset$value = (
  subset$value / subset$population_with_smartphones)

subset <- subset %>%
  ungroup() %>%
  group_by(income, tech, capacity) %>%
  mutate(
    value_mean = round(mean(value),3), 
    value_sd = round(sd(value),3)      
  )

subset = select(subset, income, tech, capacity, value_mean, value_sd)
subset = unique(subset)         

max_value = max(round(subset$value_mean,3)) + (max(round(subset$value_mean,3))/5)

plot1 =
  ggplot(subset, aes(x = tech, y = value_mean, fill=reorder(income, -value_mean))) +
  geom_bar(stat="identity", position='dodge') +
  geom_errorbar(data = subset,
                aes(y = value_mean, ymin = value_mean-value_sd, ymax =  value_mean+value_sd),
                position = position_dodge(width = .9),lwd = 0.5,show.legend = FALSE,
                width = 0.1, color = "#FF0000FF") +
  geom_text(aes(label = paste(round(value_mean,1),"")), size=1.8,
            vjust=1.5,hjust=-.15,
            position = position_dodge(.9), angle=90) +
  theme(legend.position = 'bottom',
        axis.text.x = element_text(angle = 45, hjust=1, size =8,vjust=1)) +
  labs(title="(A) Cell Site Energy Consumption Per Served Smartphone by Income Group.",
       fill=NULL,
       subtitle = "Reported for Emerging Asia by the IEA Announced Policy Scenario 2030.",
       x = NULL, y="Kilowatt hours (kWh)")  +
  scale_y_continuous(expand = c(0, 0), limits = c(0, max_value)) +
  guides(fill=guide_legend(nrow=1)) +
  scale_fill_viridis_d() +
  facet_grid(~capacity)

####
subset = data %>% ungroup()
subset = subset[(subset$iteration == '0'),] 
subset = subset[(subset$capacity == '10 GB / month / smartphone'),]
subset = subset[(subset$tech == '4G (W)'),] 
unique_smartphones = select(subset, GID_0, adb_region, population_with_smartphones)
unique_smartphones = unique(unique_smartphones)
total_smartphones = unique_smartphones %>%
  group_by(adb_region) %>%
  summarize(
    population_with_smartphones = sum(population_with_smartphones)
  )
remove(unique_smartphones)

#### Emissions demand: regions
subset = data %>% ungroup()
subset = select(subset, iteration, adb_region, tech, capacity,
                total_existing_energy_kwh, total_new_energy_kwh)

subset <- subset %>%
  pivot_longer(
    cols = `total_existing_energy_kwh`:`total_new_energy_kwh`,
    names_to = "metric",
    values_to = "value"
  )

subset <- subset %>%
  group_by(iteration, adb_region, tech, capacity) %>%
  summarize(
    value = sum(value)
  )
subset = subset %>% ungroup()
subset = merge(subset, total_smartphones)
subset$value = (
  subset$value / subset$population_with_smartphones)

subset <- subset %>%
  ungroup() %>%
  group_by(adb_region, tech, capacity) %>%
  mutate(
    value_mean = round(mean(value),3),
    value_sd = round(sd(value),3)     
  )

subset = select(subset, adb_region, tech, capacity, value_mean, value_sd)
subset = unique(subset)         

max_value = max(round(subset$value_mean,3)) + + (max(round(subset$value_mean,3))/5)

plot2 =
  ggplot(subset, aes(x = tech, y = value_mean, fill=reorder(adb_region, -value_mean))) +
  geom_bar(stat="identity", position='dodge') +
  geom_errorbar(data = subset,
                aes(y = value_mean, ymin = value_mean-value_sd, ymax =  value_mean+value_sd),
                position = position_dodge(width = .9),lwd = 0.5,show.legend = FALSE,
                width = 0.1, color = "#FF0000FF") +
  geom_text(aes(label = paste(round(value_mean,1),"")), size=1.8,
            vjust=1.5,hjust=-.15,
            position = position_dodge(.9), angle=90) +
  theme(legend.position = 'bottom',
        axis.text.x = element_text(angle = 45, hjust=1)) +
  labs(title="(B) Cell Site Energy Consumption Per Served Smartphone by Region.",
       fill=NULL,
       subtitle = "Reported for Emerging Asia by the IEA Announced Policy Scenario 2030.",
       x = NULL, y="Kilowatt hours (kWh)")  +
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
path = file.path(folder, 'figures', 'c_energy_panel_per_smartphone.png')
ggsave(path, units="in", width=8, height=8, dpi=300)
while (!is.null(dev.list()))  dev.off()
