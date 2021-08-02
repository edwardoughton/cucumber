###VISUALISE MODEL OUTPUTS###
library(tidyverse)
library(ggpubr)

folder <- dirname(rstudioapi::getSourceEditorContext()$path)

filename = 'energy_forecast.csv'
data <- read.csv(file.path(folder, '..', 'data', 'intermediate', 'CHL', 'energy_forecast', filename))


data %>% 
  ggplot(aes(x = year, y = share, fill = type)) +
  geom_area()

path = file.path(folder, 'figures', 'energy_forecast.png')
ggsave(path, units="in", width=8, height=6, dpi=300)
path = file.path(folder, '..', 'reports', 'images', 'CHL', 'energy_forecast')
ggsave(path, units="in", width=8, height=6, dpi=300)
dev.off()
