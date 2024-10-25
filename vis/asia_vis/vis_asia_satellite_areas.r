###VISUALISE MODEL OUTPUTS###
library(tidyverse)
library(ggpubr)

folder <- dirname(rstudioapi::getSourceEditorContext()$path)
filename = 'satellite_areas.csv'
data <- read.csv(file.path(folder, '..', '..', 'results', 'global_results', filename))
ls = c("ARM","AZE","GEO","KAZ","KGZ","TJK","TKM","UZB","CHN","HKG","KOR","MNG",
       "TWN","BTN","NPL","MDV","AFG","BGD","IND","PAK","LKA","BRN","KHM","IDN",
       "LAO","MYS","MMR","PHL","SGP","THA","TLS","VNM","FJI","PNG","VUT","COK",
       "KIR","MHL","FSM","NRU",#"NIU",
       "PLW","WSM","SLB","TON","TUV")
data = data%>% filter(GID_0 %in% ls)
data = select(data, GID_0, country_name, adb_region, 
              population, area_km2, satellite)

data$country_name = replace(data$country_name, 
                            data$country_name == "Lao People's Democratic Republic (the)", 
                            "Laos") 

satellite_areas = data[(data$satellite == 1),]
satellite_areas = satellite_areas %>%
  group_by(country_name, adb_region, satellite) %>%
  summarise(
    population = round(sum(population, na.rm=TRUE),0),
    area_km2 = round(sum(area_km2, na.rm=TRUE),0)
)

totals = data %>%
  group_by(country_name) %>%
  summarise(
    population_total = round(sum(population, na.rm=TRUE),0),
    area_km2_total = round(sum(area_km2, na.rm=TRUE),0)
  )

satellite_areas = merge(satellite_areas, totals, by="country_name")

satellite_areas = satellite_areas %>%
  group_by(country_name, adb_region) %>%
  summarise(
    population_perc = round(population/population_total*100,2),
    area_km2_perc = round(area_km2/area_km2_total*100,2)
)

max_value = max(
  round(satellite_areas$population_perc,3)) + 
  (max(round(satellite_areas$population_perc,3))/5
)

plot1 =
  ggplot(satellite_areas, 
         aes(x = reorder(country_name,population_perc), y = population_perc,
             fill = adb_region)) +
  geom_bar(stat="identity", position='dodge') + coord_flip() +
  geom_text(aes(label = paste(round(population_perc,1),"%")), size=1.8, vjust=.4,hjust=-.2,
              position = position_dodge(.9), angle=0) +
  theme(legend.position = 'bottom',
        axis.text.x = element_text(angle = 0, hjust=.5, size =8,vjust=1)) +
  labs(title="(A) Population Requiring Satellite.",
       fill=NULL,
       subtitle = "Population density <5 km^2.",
       x = NULL, y="Population (%)")  +
  scale_y_continuous(expand = c(0, 0), limits = c(0, 110)) +
  guides(fill=guide_legend(nrow=1)) +
  scale_fill_viridis_d() 

plot2 =
  ggplot(satellite_areas, 
         aes(x = reorder(country_name,area_km2_perc), y = area_km2_perc,
             fill=adb_region)) +
  geom_bar(stat="identity", position='dodge') + coord_flip() +
  geom_text(aes(label = paste(round(area_km2_perc,1),"%")), size=1.8, vjust=.4,hjust=-.2,
            position = position_dodge(.9), angle=0) +
  theme(legend.position = 'bottom',
        axis.text.x = element_text(angle = 0, hjust=0.5, size =8,vjust=1)) +
  labs(title="(B) Area Requiring Satellite.",
       fill=NULL,
       subtitle = "Population density <5 km^2.",
       x = NULL, y="Geographic Area (%)")  +
  scale_y_continuous(expand = c(0, 0), limits = c(0, 110)) +
  guides(fill=guide_legend(nrow=1)) +
  scale_fill_viridis_d() 

panel = ggarrange(
  plot1,
  plot2,
  # labels = c("A", "B", "C"),
  ncol = 2, nrow = 1,
  common.legend = TRUE,
  legend = 'bottom')

dir.create(file.path(folder, 'figures'), showWarnings = FALSE)
path = file.path(folder, 'figures', 'satellite_areas.png')
ggsave(path, units="in", width=8, height=6, dpi=300)
while (!is.null(dev.list()))  dev.off()
