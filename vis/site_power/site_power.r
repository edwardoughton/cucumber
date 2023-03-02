library(tidyverse)
library(ggpubr)

folder = dirname(rstudioapi::getSourceEditorContext()$path)
filename = 'gsma_site_power.csv'
data_directory = file.path(folder, '..', '..', 'data', 'raw', 'gsma')
setwd(data_directory)

data = read_csv(file.path(data_directory, filename), show_col_types = FALSE)

sample = data[, c(1,2,3,4)] 

sample = pivot_longer(sample, c(2,3,4))

sample$name = factor(sample$name,
                        levels=c(
                          "Number of on-grid towers",
                          "Number of off-grid towers",
                          "Number bad-grid towers"
                          ),
                        labels=c(
                          "On-grid", "Off-grid", "Bad-grid"
                          )
)

sample$country = factor(sample$country,
                     levels=c(
                       "Vanuatu",
                       "Uruguay",
                       "Uganda",
                       "Tonga",      
                       "Thailand",
                       "Sri Lanka",
                       "Samoa",
                       "Philippines",
                       "Peru",
                       "Pakistan",
                       "Myanmar",
                       "Mali",
                       "Malaysia",
                       "Indonesia",
                       "Fiji",
                       "Congo; Democratic Republic",
                       "Colombia",
                       "Chile",  
                       "Bangladesh",
                       "Argentina"
                     ),
                     labels=c(
                       "Vanuatu",
                       "Uruguay",
                       "Uganda",
                       "Tonga",      
                       "Thailand",
                       "Sri Lanka",
                       "Samoa",
                       "Philippines",
                       "Peru",
                       "Pakistan",
                       "Myanmar",
                       "Mali",
                       "Malaysia",
                       "Indonesia",
                       "Fiji",
                       "DRC",
                       "Colombia",
                       "Chile",  
                       "Bangladesh",
                       "Argentina"
                     )
)

plot1 = ggplot(sample, aes(x=country, y=value, fill=name)) + 
  geom_bar(stat="identity") + coord_flip() +
  theme(legend.position = 'bottom',
        axis.text.x = element_text(angle=0, hjust=0.5)) +
  labs(colour=NULL,
       title = "(A) Total Sites Per Country by Power Source",
       subtitle = "Representing 20 countries. Data sourced from GSMA (2021)", 
       x = "", y = "Total Sites", fill=NULL) +
  theme(panel.spacing = unit(0.6, "lines")) + 
  expand_limits(y=0) +
  guides(fill=guide_legend(ncol=3, title='Power Source')) +
  scale_fill_viridis_d(direction=1) +
  scale_x_discrete(expand = c(0, 0.15)) +
  scale_y_continuous(expand = c(0, 0), limits=c(0, 98000),
                     breaks = seq(0, 100000, by = 20000)) 

sample = sample %>%
  group_by(country) %>%
  mutate(percentage = round(value/sum(value)*100,1))

plot2 = ggplot(sample, aes(x=country, y=percentage, fill=name)) + 
  geom_bar(stat="identity") + coord_flip() +
  theme(legend.position = 'bottom',
        axis.text.x = element_text(angle=0, hjust=.7)) +
  labs(colour=NULL,
       title = "(B) Composition of Total Sites Per Country by Power Source",
       subtitle = "Representing 20 countries. Data sourced from GSMA (2021)", 
       x = "", y = "Percentage Composition of Total Sites (%)", fill=NULL) +
  theme(panel.spacing = unit(0.6, "lines")) + 
  expand_limits(y=0) +
  guides(fill=guide_legend(ncol=3, title='Power Source')) +
  scale_fill_viridis_d(direction=1) +
  scale_x_discrete(expand = c(0, 0.15)) +
  scale_y_continuous(expand = c(0, 0), limits=c(0, 100),
                     breaks = seq(0, 100, by = 10)) 

output = ggarrange(
  plot1, 
  plot2, 
  # labels = c("A", "B"),
  common.legend = TRUE,
  legend = 'bottom',
  ncol = 1, nrow = 2)

path = file.path(folder, '..', 'figures', 'site_power_source.png')
ggsave(path, units="in", width=7, height=7, dpi=300)