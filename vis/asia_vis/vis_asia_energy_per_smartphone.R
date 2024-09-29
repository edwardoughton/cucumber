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

data = select(data, GID_0, #capacity,
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
    total_existing_energy_kwh = round(sum(total_existing_energy_kwh, na.rm=TRUE),0),
    total_new_energy_kwh = round(sum(total_new_energy_kwh, na.rm=TRUE),0),
    # total_new_emissions_t_co2 = round(sum(total_new_emissions_t_co2, na.rm=TRUE),2),
    # total_existing_emissions_t_co2 = round(sum(total_existing_emissions_t_co2, na.rm=TRUE),2)#,
    # total_new_cost_usd = round(sum(total_new_cost_usd, na.rm=TRUE),0)
)

# data$total_existing_energy_kwh_per_user = (
#   (data$total_existing_energy_kwh) / data$population_with_smartphones
# ) 
# 
# data$total_new_energy_kwh_per_user = (
#   (data$total_new_energy_kwh) / data$population_with_smartphones
# )  

data$tech = factor(
  data$tech,
  levels = c("4G wireless","4G fiber","5G wireless","5G fiber"),
  labels = c('4G (W)','4G (F)', '5G (W)', '5G (F)')
)

data$capacity = factor(
  data$capacity,
  levels = c(20, 30, 40),
  labels = c('20 GB / Month / Smartphone', '30 GB / Month / Smartphone',
             '40 GB / Month / Smartphone')
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

subset$adb_region = factor(
  subset$adb_region,
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
subset = data %>% ungroup()
subset = select(subset, income, tech, capacity,
                total_existing_energy_kwh, total_new_energy_kwh)

subset <- subset %>%
  pivot_longer(
    cols = `total_existing_energy_kwh`:`total_new_energy_kwh`,
    names_to = "metric",
    values_to = "value"
  )

subset <- subset %>%
  group_by(income, tech, capacity) %>%
  summarize(
    value = sum(value)
  )
subset = subset %>% ungroup()
subset = merge(subset, total_smartphones)
subset$value = (
  subset$value / subset$population_with_smartphones)

# subset$value = subset$value / 1e9 #convert kwh -> twh

max_value = max(round(subset$value,3)) + (max(round(subset$value,3))/5)

plot1 =
  ggplot(subset, aes(x = tech, y = value, fill=income)) +
  geom_bar(stat="identity", position='dodge') +
  geom_text(aes(label = paste(round(value,0),"")), size=2, vjust=.5,hjust=-.2,
              position = position_dodge(.9), angle=90) +
  theme(legend.position = 'bottom',
        axis.text.x = element_text(angle = 45, hjust=1, size =8,vjust=1)) +
  labs(title="(A) Cell Site Energy Consumption per Served Smartphone by Income Group.",
       fill=NULL,
       subtitle = "Reported for Emerging Asia by the IEA Announced Policy Scenario 2030.",
       x = NULL, y="Kilowatt Hours (kWh)")  +
  scale_y_continuous(expand = c(0, 0), limits = c(0, max_value)) +
  guides(fill=guide_legend(nrow=1)) +
  scale_fill_viridis_d() +
  facet_grid(~capacity)

####
subset = data %>% ungroup()
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
subset = select(subset, adb_region, tech, capacity,
                total_existing_energy_kwh, total_new_energy_kwh)

subset <- subset %>%
  pivot_longer(
    cols = `total_existing_energy_kwh`:`total_new_energy_kwh`,
    names_to = "metric",
    values_to = "value"
  )

subset <- subset %>%
  group_by(adb_region, tech, capacity) %>%
  summarize(
    value = sum(value)
  )
subset = subset %>% ungroup()
subset = merge(subset, total_smartphones)
subset$value = (
  subset$value / subset$population_with_smartphones)

# subset <- subset %>%
#   group_by(adb_region, tech, capacity) %>%
#   summarize(
#     value = sum(value)
# )

# subset$value = subset$value / 1e9 #convert kwh -> twh

# df_errorbar <-
#   subset |>
#   group_by(adb_region, tech, energy_scenario) |>
#   summarize(
#     # low = sum(low),
#     value = sum(value)#,
#     # high = sum(high)
#   ) |>
#   group_by(tech, energy_scenario) |>
#   summarize(
#     adb_region = 'South Asia',
#     # low = sum(low),
#     value = sum(value)#,
#     # high = sum(high)
#   )

# min_value = min(round(df_errorbar$low,3))
# max_value = max(round(df_errorbar$high,3)) + .5
max_value = max(round(subset$value,3)) + + (max(round(subset$value,3))/5)

# min_value[min_value > 0] = 0

plot2 =
  ggplot(subset, aes(x = tech, y = value, fill=adb_region)) +
  geom_bar(stat="identity", position='dodge') +
  geom_text(aes(label = paste(round(value,0),"")), size=2, vjust=.5,hjust=-.2,
            position = position_dodge(.9), angle=90) +
  theme(legend.position = 'bottom',
        axis.text.x = element_text(angle = 45, hjust=1)) +
  labs(title="(B) Cell Site Energy Consumption per Served Smartphone by Region.",
       fill=NULL,
       subtitle = "Reported for Emerging Asia by the IEA Announced Policy Scenario 2030.",
       x = NULL, y="Kilowatt Hours (kWh)")  +
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

# #### emissions: new vs old
# subset = select(data, tech, capacity, income,
#         total_existing_energy_kwh_per_user, total_new_energy_kwh_per_user)
# 
# subset <- subset %>%
#   pivot_longer(
#     cols = `total_existing_energy_kwh_per_user`:`total_new_energy_kwh_per_user`,
#     names_to = "metric",
#     values_to = "value"
#   )
# 
# subset = subset[(subset$income != 'HIC'),]
# 
# subset$income = factor(
#   subset$income,
#   levels = c('HIC','UMIC','LMIC','LIC'),
#   labels = c('High Income\nCountries (HICs)','Upper-Middle Income\nCountries (LMICs)',
#              'Lower-Middle Income\nCountries (LMICs)','Low Income\nCountries (LICs)')
# )
# 
# subset$metric = factor(
#   subset$metric,
#   levels = c('total_new_energy_kwh_per_user','total_existing_energy_kwh_per_user'),
#   labels = c('New', 'Existing')
# )
# 
# subset <- subset %>%
#   group_by(metric, tech, capacity, income) %>%
#   summarize(
#     value = sum(value)
#   )
# 
# # subset$value = subset$value / 1e9 #convert kwh -> twh
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
#   labs(title="Cell Site Energy Consumption per Served Smartphone by Income Group",
#        fill=NULL,
#        subtitle = "Reported for Emerging Asia by the IEA Announced Policy Scenario 2030.",
#        x = NULL, y="Kilowatt Hours")  +
#   scale_y_continuous(expand = c(0, 0), limits = c(0, max_value)) +
#   scale_fill_viridis_d() +
#   facet_grid(income~capacity)
# 
# dir.create(file.path(folder, 'figures'), showWarnings = FALSE)
# path = file.path(folder, 'figures', 'energy_new_vs_existing_income_per_smartphone.png')
# ggsave(path, units="in", width=8, height=6, dpi=300)
# while (!is.null(dev.list()))  dev.off()
# 
# #### emissions: new vs old
# subset = select(data, tech, capacity, adb_region,
#                 total_existing_energy_kwh, total_new_energy_kwh)
# 
# subset <- subset %>%
#   pivot_longer(
#     cols = `total_existing_energy_kwh`:`total_new_energy_kwh`,
#     names_to = "metric",
#     values_to = "value"
#   )
# 
# subset$adb_region = factor(
#   subset$adb_region,
#   levels = c('Caucasus and Central Asia','East Asia',
#              'South Asia','Southeast Asia','The Pacific'
#   ),
#   labels = c('Caucasus and Central Asia','East Asia',
#              'South Asia','Southeast Asia','The Pacific')
# )
# 
# subset$metric = factor(
#   subset$metric,
#   levels = c('total_new_energy_kwh','total_existing_energy_kwh'),
#   labels = c('New', 'Existing')
# )
# 
# subset <- subset %>%
#   group_by(metric, tech, capacity, adb_region) %>%
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
#   group_by(metric, tech, capacity, adb_region) |>
#   summarize(
#     # low = sum(low),
#     value = sum(value)#,
#     # high = sum(high)
#   ) |>
#   group_by(tech, capacity, adb_region) |>
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
#     ggplot(subset, aes(x = tech, y = value, fill=metric)) +
#   geom_bar(stat="identity", position='stack') +
#   geom_text(data = df_errorbar,
#             aes(label = paste(round(value,1),"")), size = 2,angle=0,
#             vjust =-0.7, hjust =.3, angle = 0)+
#   theme(legend.position = 'bottom',
#         axis.text.x = element_text(angle = 45, hjust=1)) +
#   labs(title="Cell Site Energy Consumption per Served Smartphone by Region",
#        fill=NULL,
#        subtitle = "Reported for Emerging Asia by the IEA Announced Policy Scenario 2030.",
#        x = NULL, y="Kilowatt Hours") +
#   scale_y_continuous(expand = c(0, 0), limits = c(0, max_value)) +
#   scale_fill_viridis_d() +
#   facet_grid(adb_region~capacity)
# 
# dir.create(file.path(folder, 'figures'), showWarnings = FALSE)
# path = file.path(folder, 'figures', 'energy_new_vs_existing_regions_per_smartphone.png')
# ggsave(path, units="in", width=8, height=10, dpi=300)
# while (!is.null(dev.list()))  dev.off()
