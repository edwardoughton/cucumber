###VISUALISE MODEL OUTPUTS###
library(tidyverse)
library(ggpubr)

folder <- dirname(rstudioapi::getSourceEditorContext()$path)

filename = 'global_results.csv'
data <- read.csv(file.path(folder, '..', '..', 'results', 'global_results', filename))
ls = c("ARM","AZE","GEO","KAZ","KGZ","TJK","TKM","UZB","CHN","HKG","KOR","MNG",
       "TWN","BTN","NPL","MDV","AFG","BGD","IND","PAK","LKA","BRN","KHM","IDN",
       "LAO","MYS","MMR","PHL","SGP","THA","TLS","VNM","FJI","PNG","VUT","COK",
       "KIR","MHL","FSM","NRU","NIU","PLW","WSM","SLB","TON","TUV")
data = data%>% filter(GID_0 %in% ls)
data = data[(data$capacity == 20),]
data$tech = paste(data$generation, data$backhaul)

data = select(data, GID_0, #capacity,
              tech, #capacity, 
              energy_scenario,sharing_scenario,
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
  group_by(GID_0, tech, sharing_scenario, energy_scenario,
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
    total_new_emissions_t_co2 = round(sum(total_new_emissions_t_co2, na.rm=TRUE),2),
    total_existing_emissions_t_co2 = round(sum(total_existing_emissions_t_co2, na.rm=TRUE),2)#,
    # total_new_cost_usd = round(sum(total_new_cost_usd, na.rm=TRUE),0)
  )

data$tech = factor(
  data$tech,
  levels = c("4G wireless","4G fiber","5G wireless","5G fiber"),
  labels = c('4G (W)','4G (F)', '5G (W)', '5G (F)')
)

data$sharing_scenario = factor(
  data$sharing_scenario,
  levels = c('baseline','passive','active','srn'),
  labels = c('Baseline (No Sharing)','Passive Sharing',
             'Active Sharing','Shared Rural Network (SRN)')
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
subset = select(data, income, tech, sharing_scenario,
                total_existing_emissions_t_co2, total_new_emissions_t_co2)

subset <- subset %>%
  pivot_longer(
    cols = `total_existing_emissions_t_co2`:`total_new_emissions_t_co2`,
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
  group_by(income, tech, sharing_scenario) %>%
  summarize(
    value = sum(value)
    )

subset$value = subset$value / 1e6 #convert t -> mt

max_value = max(round(subset$value,3)) + (max(round(subset$value,3))/5)

plot1 =
  ggplot(subset, aes(x = tech, y = value, fill=income)) +
  geom_bar(stat="identity", position='dodge') +
  geom_text(aes(label = paste(round(value,0),"")), size=2, vjust=.5,hjust=-.2,
              position = position_dodge(.9), angle=90) +
  theme(legend.position = 'bottom',
        axis.text.x = element_text(angle = 45, hjust=1, size =8,vjust=1)) +
  labs(title=expression(paste("(A) Infrastructure Sharing Cell Site Operational Emissions (", CO[2], ") by Income Group.")),
       fill=NULL,
       subtitle = "Reported for 20 GB/Month under the IEA Announced Policy Scenario 2030.",
       x = NULL, y=expression(paste("Megatonnes of ", CO[2])), sep="")  +
  scale_y_continuous(expand = c(0, 0), limits = c(0, max_value)) +
  guides(fill=guide_legend(nrow=1)) +
  scale_fill_viridis_d() +
  facet_grid(~sharing_scenario)

# dir.create(file.path(folder, 'figures'), showWarnings = FALSE)
# path = file.path(folder, 'figures',  'energy.png')
# ggsave(path, units="in", width=8, height=5, dpi=300)
# while (!is.null(dev.list()))  dev.off()

#### Emissions demand: regions
subset = select(data, adb_region, tech, sharing_scenario,
                total_existing_emissions_t_co2, total_new_emissions_t_co2)

subset <- subset %>%
  pivot_longer(
    cols = `total_existing_emissions_t_co2`:`total_new_emissions_t_co2`,
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
  group_by(adb_region, tech, sharing_scenario) %>%
  summarize(
    value = sum(value)
  )

subset$value = subset$value / 1e6 #convert t -> mt

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
  labs(title=expression(paste("(B) Infrastructure Sharing Cell Site Operational Emissions (", CO[2], ") by Region.")),
       fill=NULL,
       subtitle = "Reported for 20 GB/Month under the IEA Announced Policy Scenario 2030.",
       x = NULL, y=expression(paste("Megatonnes of ", CO[2])), sep="")  +
  scale_y_continuous(expand = c(0, 0), limits = c(0, max_value)) +
  scale_fill_viridis_d() +
  facet_grid(~sharing_scenario)

panel = ggarrange(
  plot1,
  plot2,
  # labels = c("A", "B", "C"),
  ncol = 1, nrow = 2,
  common.legend = FALSE,
  legend = 'bottom')

dir.create(file.path(folder, 'figures'), showWarnings = FALSE)
path = file.path(folder, 'figures', 'f_emissions_panel_sharing.png')
ggsave(path, units="in", width=8, height=8, dpi=300)
while (!is.null(dev.list()))  dev.off()
