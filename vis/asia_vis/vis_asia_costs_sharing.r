###VISUALISE MODEL OUTPUTS###
library(tidyverse)
library(ggpubr)

folder <- dirname(rstudioapi::getSourceEditorContext()$path)
filename = 'global_cost_results.csv'
data_all <- read.csv(file.path(folder, '..', '..', 'results', 'global_results', filename))
data = data_all
# data = data[(data$GID_0 == 'ARM'),]

ls = c("ARM","AZE","GEO","KAZ","KGZ","TJK","TKM","UZB","CHN","HKG","KOR","MNG",
       "TWN","BTN","NPL","MDV","AFG","BGD","IND","PAK","LKA","BRN","KHM","IDN",
       "LAO","MYS","MMR","PHL","SGP","THA","TLS","VNM","FJI","PNG","VUT","COK",
       "KIR","MHL","FSM","NRU","NIU","PLW","WSM","SLB","TON","TUV")
data = data%>% filter(GID_0 %in% ls)
data = data[(data$capacity == 20),]
data = data[(data$energy_scenario == "aps-2030"),]
data$tech = paste(data$generation, data$backhaul)

data = select(data, GID_0, iteration,
              tech, capacity, sharing_scenario,
              income, adb_region,
              # population_total, area_km2,
              # population_with_phones,
              population_with_smartphones,
              total_cost_equipment_usd,
              total_cost_site_build_usd,
              total_cost_installation_usd,
              total_cost_operation_and_maintenance_usd,
              total_cost_power_usd,
              total_new_cost_usd
)

data = data %>%
  group_by(GID_0, iteration, tech, sharing_scenario, 
           income, adb_region) %>%
  summarise(
    total_new_cost_usd = sum(total_new_cost_usd),
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

#### Emissions: income group
subset = select(data, iteration, income, tech, sharing_scenario,
                total_new_cost_usd)

subset$value = subset$total_new_cost_usd

subset$income = factor(
  subset$income,
  levels = c('LIC','LMIC','UMIC','HIC'),
  labels = c('Low Income','Lower-Middle Income',
             'Upper-Middle Income','High Income')
)

subset <- subset %>%
  group_by(iteration, income, tech, sharing_scenario) %>%
  summarize(
    value = sum(value)
  )

subset <- subset %>%
  ungroup() %>%
  group_by(income, tech, sharing_scenario) %>%
  mutate(
    value_mean = round(mean(value)/ 1e9,3), #convert kwh -> twh
    value_sd = round(sd(value)/ 1e9,3)      #convert kwh -> twh
  )

subset = select(subset, income, tech, sharing_scenario, value_mean, value_sd)
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
                y = value_mean + value_sd + (max_value * 0.03)),  
            size = 2, vjust = 0.5, hjust = -0.15,  
            position = position_dodge(.9), angle = 90) +
  theme(legend.position = 'bottom') +
    labs(title=expression(paste("(A) Financial Cost of Universal Broadband for Infrastructure Sharing by Income Group.")),
         fill=NULL,
         subtitle = "Ordered by magnitude and reported for developing Asia at 20 GB/Month.",
         x = NULL, y="Financial Cost (US$Bn)")  +
  scale_y_continuous(expand = c(0, 0), limits = c(0, max_value * 1.2)) +
  guides(fill=guide_legend(nrow=1)) +
  scale_fill_viridis_d(breaks=c('Low Income','Lower-Middle Income',
                                'Upper-Middle Income','High Income')) +
  facet_grid(~sharing_scenario)

# dir.create(file.path(folder, 'figures'), showWarnings = FALSE)
# path = file.path(folder, 'figures',  'energy.png')
# ggsave(path, units="in", width=8, height=5, dpi=300)
# while (!is.null(dev.list()))  dev.off()

#### Cost: regions
subset = select(data, iteration, adb_region, tech, sharing_scenario,
                # total_cost_equipment_usd,
                # total_cost_site_build_usd,
                # total_cost_installation_usd,
                # total_cost_operation_and_maintenance_usd,
                total_new_cost_usd)

subset$value = subset$total_new_cost_usd

subset$adb_region = factor(
  subset$adb_region,
  levels = c('Caucasus and Central Asia','East Asia',
             'South Asia','Southeast Asia','The Pacific'
  ),
  labels = c('Caucasus and Central Asia','East Asia',
             'South Asia','Southeast Asia','The Pacific')
)

subset <- subset %>%
  group_by(iteration, adb_region, tech, sharing_scenario) %>%
  summarize(
    value = sum(value)
  )

subset <- subset %>%
  ungroup() %>%
  group_by(adb_region, tech, sharing_scenario) %>%
  mutate(
    value_mean = round(mean(value)/ 1e9,3), #convert kwh -> twh
    value_sd = round(sd(value)/ 1e9,3)      #convert kwh -> twh
  )

subset = select(subset, adb_region, tech, sharing_scenario, value_mean, value_sd)
subset = unique(subset)         

max_value = max(round(subset$value_mean,3)) + (max(round(subset$value_mean,3))/4)

plot2 =
  ggplot(subset, aes(x = tech, y = value_mean, fill=reorder(adb_region, -value_mean))) +
  geom_bar(stat="identity", position='dodge') +
  geom_errorbar(data = subset,
                aes(y = value_mean, ymin = value_mean-value_sd, ymax =  value_mean+value_sd),
                position = position_dodge(width = .9),lwd = 0.5,show.legend = FALSE,
                width = 0.1, color = "#FF0000FF") +
  geom_text(aes(label = paste(round(value_mean, 1), ""), 
                y = value_mean + value_sd + (max_value * 0.03)),  
            size = 2, vjust = 0.5, hjust = -0.15,  
            position = position_dodge(.9), angle = 90) +
  theme(legend.position = 'bottom') +
  labs(title=expression(paste("(B) Financial Cost of Universal Broadband for Infrastructure Sharing by Region.")),
       fill=NULL,
       subtitle = "Ordered by magnitude and reported for developing Asia at 20 GB/Month.",
       x = NULL, y="Financial Cost (US$Bn)")  +
  scale_y_continuous(expand = c(0, 0), limits = c(0, max_value * 1.2)) +
  scale_fill_viridis_d(breaks=c('Caucasus and Central Asia','East Asia',
                                'South Asia','Southeast Asia','The Pacific')) +
  facet_grid(~sharing_scenario)


#### Cost: countries
subset = select(data, iteration, GID_0, tech, sharing_scenario,
                # total_cost_equipment_usd,
                # total_cost_site_build_usd,
                # total_cost_installation_usd,
                # total_cost_operation_and_maintenance_usd,
                total_new_cost_usd)

subset$value = subset$total_new_cost_usd

top_countries <- c("CHN", "IND", "IDN", "PAK")
subset = subset %>%
  filter(GID_0 %in% top_countries) 

subset$GID_0 = factor(
  subset$GID_0,
  levels = c('CHN', 'IND', 'IDN', 'PAK'),
  labels = c('China', 'India', 'Indonesia', 'Pakistan')
)

subset <- subset %>%
  group_by(iteration, GID_0, tech, sharing_scenario) %>%
  summarize(
    value = sum(value)
  )

subset <- subset %>%
  ungroup() %>%
  group_by(GID_0, tech, sharing_scenario) %>%
  mutate(
    value_mean = round(mean(value)/ 1e9,3), #convert kwh -> twh
    value_sd = round(sd(value)/ 1e9,3)      #convert kwh -> twh
  )

subset = select(subset, GID_0, tech, sharing_scenario, value_mean, value_sd)
subset = unique(subset)         

max_value = max(round(subset$value_mean,3)) + (max(round(subset$value_mean,3))/4)
top_countries <- c('China', 'India', 'Indonesia', 'Pakistan')

plot3 =
  ggplot(subset, aes(x = tech, y = value_mean, fill=reorder(GID_0, -value_mean))) +
  geom_bar(stat="identity", position='dodge') +
  geom_errorbar(data = subset,
                aes(y = value_mean, ymin = value_mean-value_sd, ymax =  value_mean+value_sd),
                position = position_dodge(width = .9),lwd = 0.5,show.legend = FALSE,
                width = 0.1, color = "#FF0000FF") +
  geom_text(aes(label = paste(round(value_mean, 1), ""), 
                y = value_mean + value_sd + (max_value * 0.03)),  
            size = 2, vjust = 0.5, hjust = -0.15,  
            position = position_dodge(.9), angle = 90) +
  theme(legend.position = 'bottom') +
  labs(title=expression(paste("(C) Financial Cost of Universal Broadband for Infrastructure Sharing by Top Four Countries.")),
       fill=NULL,
       subtitle = "Ordered by magnitude and reported for developing Asia at 20 GB/Month.",
       x = NULL, y="Financial Cost (US$Bn)")  +
  scale_y_continuous(expand = c(0, 0), limits = c(0, max_value * 1.25)) +
  scale_fill_viridis_d(breaks=top_countries) +
  facet_grid(~sharing_scenario)

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
path = file.path(folder, 'figures', 'h_cost_panel_sharing.png')
ggsave(path, units="in", width=8, height=8, dpi=300)
while (!is.null(dev.list()))  dev.off()
