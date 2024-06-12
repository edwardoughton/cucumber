###VISUALISE MODEL OUTPUTS###
library(tidyverse)
library(ggpubr)

folder <- dirname(rstudioapi::getSourceEditorContext()$path)

filename = 'global_results.csv'
data <- read.csv(file.path(folder, '..', 'results', 'global_results', filename))

data = data[(data$capacity != 30),]

data$tech = paste(data$generation, data$backhaul, data$capacity)

data = select(data, GID_0, #capacity, 
              tech, energy_scenario,
              income, wb_region,
              population_total, area_km2, 
              population_with_phones, population_with_smartphones,
              total_existing_sites, total_existing_sites_4G, total_new_sites,
              total_existing_energy_kwh, total_new_energy_kwh,
              total_new_emissions_t_co2, 
              total_existing_emissions_t_co2,
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
  levels = c(
    "4G wireless 20","4G wireless 30","4G wireless 40",
    "4G fiber 20","4G fiber 30","4G fiber 40",
    "5G wireless 20","5G wireless 30","5G wireless 40",
    "5G fiber 20","5G fiber 30","5G fiber 40"
  ),
  labels = c(
    '4G (W) 20 GB', '4G (W) 30 GB', '4G (W) 40 GB',
    '4G (F) 20 GB', '4G (F) 30 GB', '4G (F) 40 GB',
    '5G (W) 20 GB', '5G (W) 30 GB', '5G (W) 40 GB',
    '5G (F) 20 GB', '5G (F) 30 GB', '5G (F) 40 GB'
  )
)

data$energy_scenario = factor(
  data$energy_scenario,
  levels = c("sps-2022","sps-2030","aps-2030"),
  labels = c("Stated Policy Scenario 2022",
             "Stated Policy Scenario 2030",
             "Announced Policy Scenario 2030")
)

#### Emissions: income group
subset = select(data, income, tech, energy_scenario, 
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
  labels = c('Low Income Country (LIC)','Lower-Middle Income Country (LMIC)',
             'Upper-Middle Income Country (LMIC)','High Income Country (HIC)')
)

subset$value = subset$value / 1e6 #convert t -> Mt

df_errorbar <- 
  subset |>
  group_by(income, tech, energy_scenario) |>
  summarize(
    # low = sum(low),
    value = sum(value)#,
    # high = sum(high)
  ) |>
  group_by(tech, energy_scenario) |>
  summarize(
    income = 'Low Income Country (LIC)', 
    # low = sum(low),
    value = sum(value)#,
    # high = sum(high)
  )

# min_value = min(round(df_errorbar$low,3))
# max_value = max(round(df_errorbar$high,3)) + .5
max_value = max(round(df_errorbar$value,3)) + .2
# min_value[min_value > 0] = 0

plot1 = ggplot(subset, aes(x = tech, y = value, fill=income)) +
  geom_bar(stat="identity", position='stack') +
  # geom_errorbar(data=df_errorbar, aes(y = baseline, ymin = low, ymax = high),
  #               lwd = .5, 
  #               show.legend = FALSE, width=0.1,  color="#FF0000FF") +
  geom_text(data = df_errorbar,
            aes(label = paste(round(value,2),"")), size = 2,angle=90,
            vjust =0.2, hjust =-.2, angle = 0)+
  theme(legend.position = 'bottom',
        axis.text.x = element_text(angle = 45, hjust=1, size =8,vjust=1)) +
  labs(title=expression(paste("(A) Total Cell Site Operational Emissions (", CO[2], ") by World Bank Income Group.")),
       fill=NULL,
       subtitle = "Interval bars reflect estimates for low and high adoption scenarios for...",
       x = NULL, y=expression(paste("Megatonnes of ", CO[2])), sep="")  +
  scale_y_continuous(expand = c(0, 0), limits = c(0, max_value)) +
  guides(fill=guide_legend(nrow=2)) +
  scale_fill_viridis_d() +
  facet_grid(~energy_scenario)

# dir.create(file.path(folder, 'figures', 'global'), showWarnings = FALSE)
# path = file.path(folder, 'figures', 'global', 'energy.png')
# ggsave(path, units="in", width=8, height=5, dpi=300)
# while (!is.null(dev.list()))  dev.off()

#### Emissions demand: regions
subset = select(data, wb_region, tech, energy_scenario, 
                total_existing_emissions_t_co2, total_new_emissions_t_co2)

subset <- subset %>% 
  pivot_longer(
    cols = `total_existing_emissions_t_co2`:`total_new_emissions_t_co2`, 
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

subset$value = subset$value / 1e6 #convert t -> Mt

df_errorbar <- 
  subset |>
  group_by(wb_region, tech, energy_scenario) |>
  summarize(
    # low = sum(low),
    value = sum(value)#,
    # high = sum(high)
  ) |>
  group_by(tech, energy_scenario) |>
  summarize(
    wb_region = 'South Asia', 
    # low = sum(low),
    value = sum(value)#,
    # high = sum(high)
  )

# min_value = min(round(df_errorbar$low,3))
# max_value = max(round(df_errorbar$high,3)) + .5
max_value = max(round(df_errorbar$value,3)) + .2
# min_value[min_value > 0] = 0

plot2 = ggplot(subset, aes(x = tech, y = value, fill=wb_region)) +
  geom_bar(stat="identity", position='stack') +
  # geom_errorbar(data=df_errorbar, aes(y = baseline, ymin = low, ymax = high),
  #               lwd = .5, 
  #               show.legend = FALSE, width=0.1,  color="#FF0000FF") +
  geom_text(data = df_errorbar,
            aes(label = paste(round(value,2),"")), size = 2,angle=90,
            vjust =0.2, hjust =-.2, angle = 0)+
  theme(legend.position = 'bottom',
        axis.text.x = element_text(angle = 45, hjust=1)) +
  labs(title=expression(paste("(B) Total Cell Site Operational Emissions (", CO[2], ") by World Bank Region.")),
       fill=NULL,
       subtitle = "Interval bars reflect estimates for low and high adoption scenarios for...",
       x = NULL, y=expression(paste("Megatonnes of ", CO[2])), sep="")  +
  scale_y_continuous(expand = c(0, 0), limits = c(0, max_value)) +
  scale_fill_viridis_d() +
  facet_grid(~energy_scenario)

panel = ggarrange(
  plot1,
  plot2,
  # labels = c("A", "B", "C"),
  ncol = 1, nrow = 2,  
  common.legend = FALSE,
  legend = 'bottom')


dir.create(file.path(folder, 'figures', 'global'), showWarnings = FALSE)
path = file.path(folder, 'figures', 'global', 'emissions_panel.png')
ggsave(path, units="in", width=8, height=8, dpi=300)
while (!is.null(dev.list()))  dev.off()








# #### emissions: new vs old
# subset = select(data, tech, energy_scenario, 
#                 total_existing_emissions_t_co2, total_new_emissions_t_co2)
# 
# subset <- subset %>% 
#   pivot_longer(
#     cols = `total_existing_emissions_t_co2`:`total_new_emissions_t_co2`, 
#     names_to = "metric",
#     values_to = "value"
#   )
# 
# subset$metric = factor(
#   subset$metric,
#   levels = c('total_existing_emissions_t_co2','total_new_emissions_t_co2'),
#   labels = c('Existing', 'New')
# )
# 
# totals <- subset %>%
#   group_by(tech) %>%
#   summarize(value = signif(sum(value))) #convert kwh -> twh
# 
# ggplot(subset, aes(x = tech, y = value, fill=metric)) +
#   geom_bar(stat="identity", position='stack') +
#   # geom_errorbar(data=df_errorbar, aes(y = baseline, ymin = low, ymax = high),
#   #               lwd = .5, 
#   #               show.legend = FALSE, width=0.1,  color="#FF0000FF") +
#   # geom_text(data = totals,
#   #           aes(label = paste(round(value, 1),"")), size = 2,#.25,
#   #           vjust =-.7, hjust =-.2, angle = 0)+
#   theme(legend.position = 'bottom',
#         axis.text.x = element_text(angle = 45, hjust=1)) +
#   labs(title=expression(paste("Total Cell Site Operational Emissions")),
#        fill=NULL,
#        subtitle = "Interval bars reflect estimates for low and high adoption scenarios for",
#        x = NULL, y=expression(paste("Terawatt hours (TWh)")), sep="")  +
#   # scale_y_continuous(expand = c(0, 0), limits = c(0, max_value)) +
#   scale_fill_viridis_d() +
#   facet_grid(~energy_scenario)

# dir.create(file.path(folder, 'figures', 'global'), showWarnings = FALSE)
# path = file.path(folder, 'figures', 'global', 'energy.png')
# ggsave(path, units="in", width=8, height=5, dpi=300)
# while (!is.null(dev.list()))  dev.off()

