###VISUALISE MODEL OUTPUTS###
library(tidyverse)
library(ggpubr)

folder <- dirname(rstudioapi::getSourceEditorContext()$path)
filename = 'cisco-dri-2021-33f5231a8c25.csv'
data <- read.csv(file.path(folder, 'data', filename))
data = data[1:12]
data = data[(data['adb_region'] != '-'),]

data = select(data, Country, adb_region, #Basic.Needs, 
              Business...Government.Investment,
              Ease.of.Doing.Business, Human.Capital, Start.Up.Environment,
              Technology.Adoption, Technology.Infrastructure)

data = data %>%
  pivot_longer(!c(Country, adb_region), names_to = "metric", values_to = "value")

data$metric = factor(
  data$metric,
  levels = c('Business...Government.Investment',
             'Ease.of.Doing.Business', 'Human.Capital', 'Start.Up.Environment',
             'Technology.Adoption', 'Technology.Infrastructure'
  ),
  labels = c('Business & Govt. Investment',
             'Ease of Doing Business', 'Human Capital', 'Start-Up Environment',
             'Technology Adoption', 'Technology Infrastructure')
)

plot1 = 
  ggplot(data,
         aes(x = reorder(Country,value), y = value, fill=adb_region)) +
  geom_bar(stat="identity", position='dodge') + coord_flip() +
  geom_text(aes(label = paste(value, ""),
                hjust = ifelse(value >= 0, -.2, 1)), size=2.2) + #, vjust=.4,hjust=1) +
  theme(legend.position = 'bottom',
        axis.text.x = element_text(angle = 0, hjust=.7, size=8,vjust=1)) +
  labs(title="Digital Readiness Index for Developing Asia.",
       fill=NULL,
       subtitle = "Reported for standardized scores from Cisco (2021) by region.",
       x = NULL, y="Standardized digital readiness score")  +
  scale_y_continuous(expand = c(0, 0), limits = c(-3, 5)) +
  scale_fill_viridis_d() +
  facet_wrap(~metric,ncol=3, nrow=2)


dir.create(file.path(folder, 'figures'), showWarnings = FALSE)
path = file.path(folder, 'figures', 'digital_readiness.png')
ggsave(path, units="in", width=8, height=10, dpi=300)
while (!is.null(dev.list()))  dev.off()
