###VISUALISE MODEL INPUTS###
library(tidyverse)
library(ggpubr)

folder <- dirname(rstudioapi::getSourceEditorContext()$path)

filename = 'capacity_lut_by_frequency.csv'
folder_in = file.path(folder,'..','..','data','intermediate','luts')
data <- read.csv(file.path(folder_in, filename))
data$tech = paste(data$frequency_GHz, ' GHz (',data$generation,")", sep = "") #data$bandwidth_MHz, 
data = data[(data$confidence_interval == 50),]
data = select(data, inter_site_distance_m, tech, environment, 
              path_loss_dB, received_power_dBm, interference_dBm, 
              # noise_dB,
              sinr_dB, spectral_efficiency_bps_hz, capacity_mbps,
              capacity_mbps_km2)

data$inter_site_distance_km = round(data$inter_site_distance_m / 1e3,1)

max_distance = 10
data = data[(data$inter_site_distance_km < max_distance),]

data$environment = factor(
  data$environment,
  levels = c('urban','suburban','rural'),
  labels = c('Urban','Suburban','Rural'),
)
unique(data$tech)
data$tech = factor(
  data$tech,
  levels = c('0.7 GHz (5G)','0.8 GHz (4G)','1.8 GHz (4G)','2.6 GHz (4G)','3.5 GHz (5G)'),
  labels = c('0.7 GHz (5G)','0.8 GHz (4G)','1.8 GHz (4G)','2.6 GHz (4G)','3.5 GHz (5G)'),
)

data1 = select(data, inter_site_distance_km, path_loss_dB, tech, environment)
plot1 = ggplot(data1, aes(x = inter_site_distance_km, y = path_loss_dB, 
                          color=tech, shape=tech)) +
  geom_point() +
  geom_line() +
  theme(legend.position = 'bottom',
        axis.text.x = element_text(angle = 0, hjust=.5, size =8,vjust=1)) +
  labs(title="(A) Path Loss by Inter-Dite Distance",
       color=NULL, shape=NULL,
       x = 'Inter-Side Distance (km)', y="Path Loss (dB)")  +
  scale_color_viridis_d() +
  scale_x_continuous(breaks = seq(0, max_distance, by = 2)) +
  facet_grid(~environment)


data2 = select(data, inter_site_distance_km, received_power_dBm, tech, environment)
plot2 = ggplot(data2, aes(x = inter_site_distance_km, y = received_power_dBm, 
                          color=tech, shape=tech)) +
  geom_point() +
  geom_line() +
  theme(legend.position = 'bottom',
        axis.text.x = element_text(angle = 0, hjust=.5, size =8,vjust=1)) +
  labs(title="(B) Received Power by Inter-Dite Distance",
       color=NULL, shape=NULL,
       x = 'Inter-Side Distance (km)', y="Received Power (dBm)")  +
  scale_color_viridis_d() +
  scale_x_continuous(breaks = seq(0, max_distance, by = 2)) +
  facet_grid(~environment)


data3 = select(data, inter_site_distance_km, interference_dBm, tech, environment)
plot3 = ggplot(data3, aes(x = inter_site_distance_km, y = interference_dBm, 
                          color=tech, shape=tech)) +
  geom_point() +
  geom_line() +
  theme(legend.position = 'bottom',
        axis.text.x = element_text(angle = 0, hjust=.5, size =8,vjust=1)) +
  labs(title="(C) Interference by Inter-Dite Distance",
       color=NULL, shape=NULL,
       x = 'Inter-Side Distance (km)', y="Received Interference (dB)")  +
  scale_color_viridis_d() +
  scale_x_continuous(breaks = seq(0, max_distance, by = 2)) +
  facet_grid(~environment)


data4 = select(data, inter_site_distance_km, capacity_mbps_km2, tech, environment)
plot4 = ggplot(data4, aes(x = inter_site_distance_km, y = capacity_mbps_km2, 
                          color=tech, shape=tech)) +
  geom_point() +
  geom_line() +
  theme(legend.position = 'bottom',
        axis.text.x = element_text(angle = 0, hjust=.5, size =8,vjust=1)) +
  labs(title="(D) Capacity by Inter-Dite Distance",
       color=NULL, shape=NULL,
       x = 'Inter-Side Distance (km)', y="Capacity (Mbps/km^2)")  +
  scale_color_viridis_d() +
  # scale_y_continuous(limits = c(0, 700)) +
  scale_x_continuous(breaks = seq(0, max_distance, by = 2)) +
  facet_grid(~environment)

panel = ggarrange(
  plot1, plot2, plot3, plot4,
  nrow = 4,
  ncol = 1,
  common.legend = TRUE, legend="bottom"
)

dir.create(file.path(folder, 'figures'), showWarnings = FALSE)
path = file.path(folder, 'figures', 'capacity_panel.png')
ggsave(path, units="in", width=8, height=10, dpi=300)
while (!is.null(dev.list()))  dev.off()
