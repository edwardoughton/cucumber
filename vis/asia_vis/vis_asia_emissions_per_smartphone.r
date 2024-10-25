###VISUALISE MODEL OUTPUTS###
library(tidyverse)
library(ggpubr)

folder <- dirname(rstudioapi::getSourceEditorContext()$path)

folder <- dirname(rstudioapi::getSourceEditorContext()$path)
filename = 'global_results.csv'
data <- read.csv(file.path(folder, '..', '..', 'results', 'global_results', filename))
ls = c("ARM","AZE","GEO","KAZ","KGZ","TJK","TKM","UZB","CHN","HKG","KOR","MNG",
       "TWN","BTN","NPL","MDV","AFG","BGD","IND","PAK","LKA","BRN","KHM","IDN",
       "LAO","MYS","MMR","PHL","SGP","THA","TLS","VNM","FJI","PNG","VUT","COK",
       "KIR","MHL","FSM","NRU","NIU","PLW","WSM","SLB","TON","TUV")
data = data%>% filter(GID_0 %in% ls)
data = data[(data$sharing_scenario == 'baseline'),]

data$tech = paste(data$generation, data$backhaul)

data = select(data, GID_0, tech, capacity, 
              energy_scenario,
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
  group_by(GID_0, tech, capacity, energy_scenario,
           income, adb_region) %>%
  summarise(
    population_total = round(sum(population_total, na.rm=TRUE),0), 
    area_km2 = round(sum(area_km2, na.rm=TRUE),0), 
    # population_with_phones = round(sum(population_with_phones, na.rm=TRUE),0), 
    population_with_smartphones = round(sum(population_with_smartphones, na.rm=TRUE),0),
    # total_existing_sites = round(sum(total_existing_sites, na.rm=TRUE),0), 
    # total_existing_sites_4G = round(sum(total_existing_sites_4G, na.rm=TRUE),0), 
    # total_new_sites = round(sum(total_new_sites, na.rm=TRUE),0),
    # total_existing_energy_kwh = round(sum(total_existing_energy_kwh, na.rm=TRUE),0), 
    # total_new_energy_kwh = round(sum(total_new_energy_kwh, na.rm=TRUE),0),
    total_new_emissions_t_co2 = round(sum(total_new_emissions_t_co2, na.rm=TRUE),0), 
    total_existing_emissions_t_co2 = round(sum(total_existing_emissions_t_co2, na.rm=TRUE),0)#,
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

data$income = factor(
  data$income,
  levels = c('LIC','LMIC','UMIC','HIC'),
  labels = c('Low Income','Lower-Middle Income',
             'Upper-Middle Income','High Income')
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
unique_smartphones = select(subset, GID_0, income, population_with_smartphones)
unique_smartphones = unique(unique_smartphones)
total_smartphones = unique_smartphones %>%
  group_by(income) %>%
  summarize(
    population_with_smartphones = sum(population_with_smartphones)
  )
remove(unique_smartphones)

#### Emissions: income group
data = data %>% ungroup() 
subset = select(data, income, tech, capacity,
                population_with_smartphones,
                total_new_emissions_t_co2, 
                total_existing_emissions_t_co2)

subset = subset %>%
  group_by(income, tech, capacity) %>%
  summarize(
    population_with_smartphones = sum(population_with_smartphones),
    total_new_emissions_t_co2 = sum(total_new_emissions_t_co2), 
    total_existing_emissions_t_co2 = sum(total_existing_emissions_t_co2)
  )
  
subset$total_new_emissions_kg_co2_per_user = (
  (subset$total_new_emissions_t_co2 * 1e3) / subset$population_with_smartphones
)  #(convert to kg)

subset$total_existing_emissions_kg_co2_per_user = (
  (subset$total_existing_emissions_t_co2 * 1e3) / subset$population_with_smartphones
)  #(convert to kg)

subset <- subset %>% 
  pivot_longer(
    cols = `total_new_emissions_kg_co2_per_user`:`total_existing_emissions_kg_co2_per_user`, 
    names_to = "metric",
    values_to = "value"
  )

subset <- subset %>%
  group_by(income, tech, capacity) %>%
  summarize(
    value = sum(value)
  )

max_value = max(round(subset$value,3)) + (max(round(subset$value,3))/5)

plot1 = 
  ggplot(subset, aes(x = tech, y = value, fill=income)) +
  geom_bar(stat="identity", position='dodge') +
  geom_text(aes(label = paste(round(value,0),"")), size=2, vjust=.5,hjust=-.2,
            position = position_dodge(.9), angle=90) +
  theme(legend.position = 'bottom',
        axis.text.x = element_text(angle = 45, hjust=1, size =8,vjust=1)) +
  labs(title=expression(paste("(A) Cell Site Operational Emissions Per Served Smartphone (", CO[2], ") by Income Group.")),
       fill=NULL,
       subtitle = "Reported for Emerging Asia by the IEA Announced Policy Scenario 2030.",
       x = NULL, y=expression(paste("Kilograms of ", CO[2])), sep="")  +
  scale_y_continuous(expand = c(0, 0), limits = c(0, max_value)) +
  guides(fill=guide_legend(nrow=1)) +
  scale_fill_viridis_d() +
  facet_grid(~capacity)

subset = select(data, adb_region, tech, capacity,
                population_with_smartphones,
                total_new_emissions_t_co2, 
                total_existing_emissions_t_co2)

subset = subset %>%
  group_by(adb_region, tech, capacity) %>%
  summarize(
    population_with_smartphones = sum(population_with_smartphones),
    total_new_emissions_t_co2 = sum(total_new_emissions_t_co2), 
    total_existing_emissions_t_co2 = sum(total_existing_emissions_t_co2)
  )

subset$total_new_emissions_kg_co2_per_user = (
  (subset$total_new_emissions_t_co2 * 1e3) / subset$population_with_smartphones
)  #(convert to kg)

subset$total_existing_emissions_kg_co2_per_user = (
  (subset$total_existing_emissions_t_co2 * 1e3) / subset$population_with_smartphones
)  #(convert to kg)

subset <- subset %>%
  pivot_longer(
    cols = `total_new_emissions_kg_co2_per_user`:`total_existing_emissions_kg_co2_per_user`,
    names_to = "metric",
    values_to = "value"
  )

subset <- subset %>%
  group_by(adb_region, tech, capacity) %>%
  summarize(
    value = sum(value)
  )

max_value = max(round(subset$value,3)) + (max(round(subset$value,3))/5)

plot2 = 
  ggplot(subset, aes(x = tech, y = value, fill=adb_region)) +
  geom_bar(stat="identity", position='dodge') +
  geom_text(aes(label = paste(round(value,0),"")), size=2, vjust=.5,hjust=-.2,
            position = position_dodge(.9), angle=90) +
  theme(legend.position = 'bottom',
        axis.text.x = element_text(angle = 45, hjust=1)) +
  labs(title=expression(paste("(B) Cell Site Operational Emissions Per Served Smartphone (", CO[2], ") by Region.")),
       fill=NULL,
       subtitle = "Reported for Emerging Asia by the IEA Announced Policy Scenario 2030.",
       x = NULL, y=expression(paste("Kilograms of ", CO[2])), sep="")  +
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
path = file.path(folder, 'figures', 'd_emissions_per_smartphone_panel.png')
ggsave(path, units="in", width=8, height=8, dpi=300)
while (!is.null(dev.list()))  dev.off()
