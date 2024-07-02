###VISUALISE MODEL OUTPUTS###
library(tidyverse)
library(ggpubr)
library("viridis") 

#############
folder <- dirname(rstudioapi::getSourceEditorContext()$path)
filename = 'ericsson_mr_data_per_sub.csv'
data <- read.csv(file.path(folder, 'plot1_data', filename))
unique(data$region)

data$region_name = factor(data$region,
                     levels = c(
                       'CEE',
                       'INB',
                       'LATAM',
                       'MENA',
                       'NAM',
                       'NEA',
                       'SEAO',
                       'SSA',
                       'WE'
                     ),
                     labels = c(
                       'Central Eastern Europe',
                       'India, Nepal, Bhutan',
                       'LATAM',
                       'MENA',
                       'North America',
                       'North East Asia',
                       'South East Asia and Oceania',
                       'Sub-Saharan Africa',
                       'Western Europe'
                     )
)

plot1 = ggplot(data, aes(x=year, y=value, group=region_name, 
                         color=region_name)) +
  geom_line(aes(linetype=region_name)) +
  labs(title="(A) Global Monthly Data Traffic.",
       subtitle="Reported annually by region.",
       x=NULL,
       y = "Monthly Traffic (GB/Smartphone)",
       color='', linetype='', group='')+
  theme_bw() +
  scale_x_continuous(expand = c(0, 0), limits=c(2016,2023)) +
  scale_y_continuous(expand = c(0, 0), limits=c(0,35)) +
  scale_color_viridis(discrete = TRUE, option = "C")+
  # scale_fill_viridis(discrete = TRUE) +
  theme(legend.position = "bottom",
        axis.text.x = element_text(angle = 0, hjust=.2),
  ) +
  guides(color = guide_legend(ncol = 5, nrow = 2),
         linetype = guide_legend(ncol = 5, nrow = 2),
         group = guide_legend(ncol = 5, nrow = 2),
  )

#############
folder <- dirname(rstudioapi::getSourceEditorContext()$path)
filename = 'ericsson_mr_smartphone_subs.csv'
data <- read.csv(file.path(folder, 'plot1_data', filename))

data$region_name = factor(data$region,
                          levels = c(
                            'CEE',
                            'INB',
                            'LATAM',
                            'MENA',
                            'NAM',
                            'NEA',
                            'SEAO',
                            'SSA',
                            'WE'
                          ),
                          labels = c(
                            'Central Eastern Europe',
                            'India, Nepal, Bhutan',
                            'Latin America',
                            'Middle East and North Africa',
                            'North America',
                            'North East Asia',
                            'South East Asia and Oceania',
                            'Sub-Saharan Africa',
                            'Western Europe'
                          )
)

plot2 = ggplot(data, aes(x=year, y=value/1e3, group=region_name, 
                         color=region_name))+
  geom_line(aes(linetype=region_name)) +
  labs(title="(B) Global Smartphone Subscriptions.",
       subtitle="Reported annually as the total by region.",
       x=NULL,
       y = "Smartphones (Billions)",
       color='', linetype='', group='')+
  theme_bw() +
  scale_x_continuous(expand = c(0, 0), limits=c(2016,2023)) +
  scale_y_continuous(expand = c(0, 0), limits=c(0,1)) +
  scale_color_viridis(discrete = TRUE, option = "C")+
  theme(legend.position = "bottom",
        axis.text.x = element_text(angle = 0, hjust=0.2),
        # legend.text = element_text(size = 6),
        # panel.grid.minor.x = element_line(color = 'black')
        # panel.background = element_rect(fill = "white"),
        # panel.grid.major = element_line(colour="grey90",size = rel(0.5)),         
        # panel.grid.minor = element_line(colour="grey95",size = rel(0.25))
  ) +
  guides(color = guide_legend(ncol = 5, nrow = 2),
         linetype = guide_legend(ncol = 5, nrow = 2),
         group = guide_legend(ncol = 5, nrow = 2),
  )


#############
folder <- dirname(rstudioapi::getSourceEditorContext()$path)
filename = 'mobile_connectivity_by_country_groups.csv'
data <- read.csv(file.path(folder, 'plot1_data', filename))

data = data[(data$year != 2021),]
# data = data[(data$year == 2022),]
data = data[(data$group != 'connected'),]

data$income_year = paste(data$income, data$year)


data$income_year = factor(data$income_year,
                          levels = c(
                            'LDCs 2020','LDCs 2021','LDCs 2022',
                            'LMIC 2020','LMIC 2021','LMIC 2022',
                            'LMIC_ex_LDC 2020','LMIC_ex_LDC 2021','LMIC_ex_LDC 2022',
                            'HIC 2020','HIC 2021','HIC 2022'
                          ),
                          labels = c(
                'LDC 2020','LDC 2021','LDC 2022',
                'LMIC 2020','LMIC 2021','LMIC 2022',
                'UMIC 2020','UMIC 2021','UMIC 2022',  
                'HIC 2020','HIC 2021','HIC 2022'
                          )
)

data$group = factor(data$group,
                    levels = c('coverage_gap','usage_gap','connected'),
                    labels = c('Uncovered','Covered Without Smartphone','Connected')
)

plot3 = ggplot(data, aes(x=income_year, y=value, group=group, 
                 fill=group)) + #coord_flip() +
  geom_bar(position="dodge", stat="identity") +
  geom_text(aes(label = paste(round(value,0),"%")),vjust=.5,hjust=-.2, size=3,
            position = position_dodge(.9), angle=90) +
  labs(title="(C) Mobile Connectivity by Country Group.",
       subtitle="Reported annually by coverage type.",
       x=NULL,
       y = "Coverage (%)",
       color='', linetype='Coverage Type', group='Coverage Type', fill='Coverage Type') +
  theme_bw() +
  # scale_x_continuous(expand = c(0, 0), limits=c(2016,2023)) +
  scale_y_continuous(expand = c(0, 0), limits=c(0,100)) +
  scale_color_viridis(discrete = TRUE, option = "C") +
  scale_fill_viridis(discrete = TRUE, option = "D", direction=-1, alpha=.85) +
  theme(legend.position = "bottom",
        axis.text.x = element_text(angle = 65, hjust=1),
        legend.text = element_text(size = 8),
        # panel.grid.minor.x = element_line(color = 'black')
        # panel.background = element_rect(fill = "white"),
        # panel.grid.major = element_line(colour="grey90",size = rel(0.5)),
        # panel.grid.minor = element_line(colour="grey95",size = rel(0.25))
  ) +
  guides(color = guide_legend(ncol = 5, nrow = 2),
         linetype = guide_legend(ncol = 5, nrow = 2),
         group = guide_legend(ncol = 5, nrow = 2),
  )

#############
folder <- dirname(rstudioapi::getSourceEditorContext()$path)
filename = 'mobile_internet_connectivity_by_region.csv'
data <- read.csv(file.path(folder, 'plot1_data', filename))

data = data[(data$year != 2021),]
# data = data[(data$year == 2022),]
data = data[(data$group != 'connected'),]

data$region_year = paste(data$region, data$year)

data$region_year = factor(data$region_year,
                          levels = c(
            "Europe & Central Asia 2020","Europe & Central Asia 2021", "Europe & Central Asia 2022",
            "East Asia & Pacific 2020","East Asia & Pacific 2021", "East Asia & Pacific 2022",
            "Latin America & Caribbean 2020","Latin America & Caribbean 2021", "Latin America & Caribbean 2022",
            "Middle East & North Africa 2020","Middle East & North Africa 2021", "Middle East & North Africa 2022",
            "North America 2020","North America 2021", "North America 2022",
            "South Asia 2020","South Asia 2021", "South Asia 2022",
            "Sub-Saharan Africa 2020","Sub-Saharan Africa 2021", "Sub-Saharan Africa 2022"
                          ),
                          labels = c(
                            "ECA 2020","ECA 2021", "ECA 2022",
                            "East Asia 2020","East Asia 2021", "East Asia 2022",
                            "LATAM 2020","LATAM 2021", "LATAM 2022",
                            "MENA 2020","MENA 2021", "MENA 2022",
                            "North America 2020","North America 2021", "North America 2022",
                            "South Asia 2020","South Asia 2021", "South Asia 2022",
                            "SSA 2020","SSA 2021", "SSA 2022"
                          )
)

data$group = factor(data$group,
                    levels = c('coverage_gap','usage_gap','connected'),
                    labels = c('Coverage Gap','Usage Gap','Connected')
)
plot4 = ggplot(data, aes(x=region_year, y=value, group=group, 
                           fill=group)) + #coord_flip() +
  geom_bar(position="dodge", stat="identity") +
  geom_text(aes(label = paste(round(value,0),"%")),vjust=.5,hjust=-.2, size=3,
            position = position_dodge(.9), angle=90) +
  labs(title="(D) Mobile Internet Connectivity by Region.",
       subtitle="Reported annually by coverage type.",
       x=NULL,
       y = "Coverage (%)",
       color='', linetype='Coverage Type', group='Coverage Type', fill='Coverage Type')+
  theme_bw() +
  # scale_x_continuous(expand = c(0, 0), limits=c(2016,2023)) +
  scale_y_continuous(expand = c(0, 0), limits=c(0,100)) +
  # scale_color_viridis(discrete = TRUE, option = "C") +
  scale_fill_viridis(discrete = TRUE, option = "D", direction=-1, alpha=.85) +
  theme(legend.position = "bottom",
        axis.text.x = element_text(angle = 65, hjust=1),
        legend.text = element_text(size = 8),
        # panel.grid.minor.x = element_line(color = 'black')
        # panel.background = element_rect(fill = "white"),
        # panel.grid.major = element_line(colour="grey90",size = rel(0.5)),
        # panel.grid.minor = element_line(colour="grey95",size = rel(0.25))
  ) +
  guides(color = guide_legend(ncol = 5, nrow = 2),
         linetype = guide_legend(ncol = 5, nrow = 2),
         group = guide_legend(ncol = 5, nrow = 2),
  )

panel1 <- ggarrange(plot1, plot2, 
                   ncol = 2, nrow = 1, align = c("hv"),
                   common.legend = TRUE,
                   legend='bottom'#,
                   # heights=c(1,1,.85)
                   )

panel2 <- ggarrange(plot3, plot4,
                   ncol = 2, nrow = 1, align = c("h"),
                   common.legend = TRUE,
                   legend='bottom'#,
                   # heights=c(1,1,.85)
)

output <- ggarrange(panel1, panel2,
                    ncol = 1, nrow = 2, align = c("hv"),
                    common.legend = FALSE,
                    legend='bottom'#,
                    # heights=c(1,1,.85)
)

path = file.path(folder, 'figures', 'plot1.png')
dir.create(file.path(folder, 'figures'), showWarnings = FALSE)

ggsave(
  'panel.png',
  plot = last_plot(),
  device = "png",
  path=file.path(folder, 'figures'),
  units = c("in"),
  width = 9,
  height = 9,
  bg="white"
)
