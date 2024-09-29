###VISUALISE MODEL INPUTS###
library(tidyverse)
library(ggpubr)

folder <- dirname(rstudioapi::getSourceEditorContext()$path)

filename = 'capacity_lut_by_frequency.csv'
folder_in = file.path(folder,'..','..','data','intermediate','luts')
data <- read.csv(file.path(folder_in, filename))
data$tech = paste(data$frequency_GHz, ' GHz (',data$generation,")", sep = "") #data$bandwidth_MHz, 
data = data[(data$confidence_interval == 50),]
data = select(data, inter_site_distance_m, tech, 
              path_loss_dB, received_power_dBm, interference_dBm, 
              # noise_dB,sinr_dB, spectral_efficiency_bps_hz, capacity_mbps, 
              capacity_mbps_km2)

data = data[(data$inter_site_distance_m < 20000),]

data1 = select(data, inter_site_distance_m, path_loss_dB, tech)
plot1 = ggplot(data1, aes(x = inter_site_distance_m, y = path_loss_dB, color=tech)) +
  geom_point() +
  geom_line() +
  theme(legend.position = 'bottom',
        axis.text.x = element_text(angle = 0, hjust=.5, size =8,vjust=1)) +
  labs(title="(A) Path Loss by Inter-Dite Distance",
       color=NULL,
       x = 'Inter-Side Distance (m)', y="Path Loss (dB)")  +
  scale_color_viridis_d() +
scale_x_continuous(breaks = seq(0, 20000, by = 2000)) 


data2 = select(data, inter_site_distance_m, received_power_dBm, tech)
plot2 = ggplot(data2, aes(x = inter_site_distance_m, y = received_power_dBm, color=tech)) +
  geom_point() +
  geom_line() +
  theme(legend.position = 'bottom',
        axis.text.x = element_text(angle = 0, hjust=.5, size =8,vjust=1)) +
  labs(title="(B) Received Power by Inter-Dite Distance",
       color=NULL,
       x = 'Inter-Side Distance (m)', y="Received Power (dBm)")  +
  scale_color_viridis_d() +
  scale_x_continuous(breaks = seq(0, 20000, by = 2000)) 


data3 = select(data, inter_site_distance_m, interference_dBm, tech)
plot3 = ggplot(data3, aes(x = inter_site_distance_m, y = interference_dBm, color=tech)) +
  geom_point() +
  geom_line() +
  theme(legend.position = 'bottom',
        axis.text.x = element_text(angle = 0, hjust=.5, size =8,vjust=1)) +
  labs(title="(C) Interference by Inter-Dite Distance",
       color=NULL,
       x = 'Inter-Side Distance (m)', y="Received Interference (dB)")  +
  scale_color_viridis_d() +
  scale_x_continuous(breaks = seq(0, 20000, by = 2000)) 


data4 = select(data, inter_site_distance_m, capacity_mbps_km2, tech)
plot4 = ggplot(data4, aes(x = inter_site_distance_m, y = capacity_mbps_km2, color=tech)) +
  geom_point() +
  geom_line() +
  theme(legend.position = 'bottom',
        axis.text.x = element_text(angle = 0, hjust=.5, size =8,vjust=1)) +
  labs(title="(D) Capacity by Inter-Dite Distance",
       color=NULL,
       x = 'Inter-Side Distance (m)', y="Capacity (Mbps/km^2)")  +
  scale_color_viridis_d() +
  # scale_y_continuous(limits = c(0, 700)) +
  scale_x_continuous(breaks = seq(0, 20000, by = 2000)) 

panel = ggarrange(
  plot1, plot2, plot3, plot4,
  nrow = 2,
  ncol = 2,
  common.legend = TRUE, legend="bottom"
)

dir.create(file.path(folder, 'figures'), showWarnings = FALSE)
path = file.path(folder, 'figures', 'capacity_panel.png')
ggsave(path, units="in", width=8, height=8, dpi=300)
while (!is.null(dev.list()))  dev.off()
