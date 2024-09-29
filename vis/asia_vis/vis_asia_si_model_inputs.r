###VISUALISE MODEL INPUTS###
library(tidyverse)
library(ggpubr)

folder <- dirname(rstudioapi::getSourceEditorContext()$path)

filename = 'iea_electricity_emissions_factors.csv'
folder_in = file.path(folder,'..','..','..','data_raw','IEA_data','WEO2023 extended data')
data <- read.csv(file.path(folder_in, filename))
ls = c("Asia Pacific","China","Eurasia","India","Japan","Middle East","")
data = data%>% filter(region %in% ls)
data = select(data, region, generation_twh, scenario, co2_g_kwh)

data = data %>%
  filter_at(vars(scenario),
            all_vars(!. %in% c(
              "historical",
              ""))
  )

data$generation_twh = factor(
  data$generation_twh,
  levels = c("Wind","Unabated natural gas",
             "Unabated coal","Solar PV","Oil",
             "Nuclear","Hydrogen and ammonia",
             "Hydro","Fossil fuels with CCUS",
             "Bioenergy"
  ),
  labels = c("Wind","Unabated natural gas",
             "Unabated coal","Solar PV","Oil",
             "Nuclear","Hydrogen and ammonia",
             "Hydro","Fossil fuels with CCUS",
             "Bioenergy")
)

data$scenario = factor(
  data$scenario,
  levels = c("aps-2030","sps-2030","sps-2022"),
  labels = c("Announced Pledges Scenario (2030)",
             "Stated Policies Scenario (2030)",
             "Stated Policies Scenario (2022)")
)

co2_kg_kwh <- data$co2_g_kwh / 1e3

max_value = max(round(co2_kg_kwh,3)) + 4

ggplot(data, aes(x = generation_twh, y = co2_g_kwh/1e3, fill=scenario)) +
  geom_bar(stat="identity", position='dodge') +
  coord_flip() +
  geom_text(aes(label = paste(round(co2_g_kwh/1e3,1),"")), size=2, vjust=.4,hjust=-.3,
            position = position_dodge(1.05), angle=0) +
  theme(legend.position = 'bottom',
        axis.text.x = element_text(angle = 0, hjust=1, size =8,vjust=1)) +
  labs(title=expression(paste("IEA Emissions by Electricity Generation Source (", CO[2], ").")),
       fill=NULL,
       subtitle = "Reported by IEA regions for Asia.",
       x = NULL, y=expression(paste("Kilograms ", CO[2], " Per kWh")), sep="")  +
  scale_y_continuous(expand = c(0, 0), limits = c(0, 5.8)) +
  guides(fill = guide_legend(reverse = TRUE)) +
  scale_fill_viridis_d() +
  facet_wrap(~region, ncol=2)

dir.create(file.path(folder, 'figures'), showWarnings = FALSE)
path = file.path(folder, 'figures', 'iea_emissions_factors.png')
ggsave(path, units="in", width=8, height=9, dpi=300)
while (!is.null(dev.list()))  dev.off()

#####################

folder <- dirname(rstudioapi::getSourceEditorContext()$path)

filename = 'WEO2023_Extended_Data_Regions.csv'
folder_in = file.path(folder,'..','..','..','data_raw','IEA_data','WEO2023 extended data')
data <- read.csv(file.path(folder_in, filename))
ls = c("Asia Pacific","China","Eurasia","India","Japan","Middle East","")
data = data%>% filter(REGION %in% ls)

data = data %>% filter_at(vars(YEAR),
                          all_vars(. %in% c(2022, 2030)))

data = data %>% filter_at(vars(FLOW),
            all_vars(. %in% c("Electricity generation","")))

data = data %>% filter_at(vars(CATEGORY),
                          all_vars(. %in% c("Energy","")))

data = data %>% filter_at(vars(PRODUCT),
                          all_vars(!. %in% c("Total","Solar PV","Wind","Hydro",
                                             "Modern bioenergy and renewable waste",
                                             "Hydrogen and H2-based fuels",
                                             "Fossil fuels: with CCUS")))

data = data %>% filter_at(vars(REGION),
                          all_vars(!. %in% c(
                            "World","OECD","Non-OECD",
                            "Emerging market and developing economies",
                            "Advanced economies")))

data = data %>% filter_at(vars(SCENARIO),
                          all_vars(!. %in% c("Net Zero Emissions by 2050 Scenario","")))

data$SCENARIO = paste(data$SCENARIO, data$YEAR)

data = select(data, 'SCENARIO', 'PRODUCT','REGION','VALUE')

data <- data %>%
  group_by(SCENARIO, PRODUCT, REGION) %>%
  reframe(
    value = sum(VALUE)
    )

data <- data %>%
  group_by(SCENARIO, REGION) %>%
  reframe(
    product = PRODUCT,
    value = value/1e3,
    share = round((value / sum(value)) * 100, 2)
  )

data$SCENARIO = factor(
  data$SCENARIO,
  levels = c("Stated Policies Scenario 2022",
             "Stated Policies Scenario 2030",
             "Announced Pledges Scenario 2030"),
  labels = c("Stated Policies Scenario (2022)",
             "Stated Policies Scenario (2030)",
             "Announced Pledges Scenario (2030)")
)

data$REGION = factor(
  data$REGION,
  levels = c("United States" ,"Southeast Asia","Russia","North America", 
              "Middle East","Japan","India","European Union",
             "Europe","Eurasia","China","Central and South America",
             "Brazil","Asia Pacific","Africa"),
  labels = c("United States" ,"Southeast Asia","Russia","North America", 
             "Middle East","Japan","India","European Union",
             "Europe","Eurasia","China","Central/South America",
             "Brazil","Asia Pacific","Africa")
)

data$product = factor(
  data$product,
  levels = c("Nuclear","Oil","Coal: unabated","Natural gas: unabated","Renewables"),
  labels = c("Nuclear","Oil","Unabated Coal","Unabated Natural Gas","Renewables")
)

df_errorbar <-
  data |>
  group_by(SCENARIO, product, REGION) |>
  summarize(
    # low = sum(low),
    value = sum(value)#,
    # high = sum(high)
  ) |>
  group_by(SCENARIO, REGION) |>
  summarize(
    product = 'Renewables',
    # low = sum(low),
    value = sum(value)#,
    # high = sum(high)
  )

max_value = max(round(df_errorbar$value,3)) + 2

ggplot(data, aes(x = REGION, y = value, fill=product)) +
  geom_bar(position = "stack", stat = "identity") +
  coord_flip() +
  geom_text(data = df_errorbar,
            aes(label = paste(round(value,1),"")), size = 2, #angle=0,
            vjust =.3, hjust =-.2, angle = 0)+
  theme(legend.position = 'bottom',
        axis.text.x = element_text(angle = 0, hjust=.5, size =8, vjust=0)) +
  labs(title=expression("Electricity Generation by Technology Source"),
       fill=NULL,
       subtitle = "Reported by IEA regions for Asia.",
       x = NULL, y=expression("Petawatt Hours (pWh)"), sep="")  +
  scale_y_continuous(expand = c(0, 0), limits = c(0, max_value)) +
  # guides(fill=guide_legend(nrow=1)) +
  guides(fill = guide_legend(reverse = FALSE,nrow=1)) +
  scale_fill_viridis_d() +
  facet_wrap(~SCENARIO, ncol=3)

dir.create(file.path(folder, 'figures'), showWarnings = FALSE)
path = file.path(folder, 'figures', 'iea_generation_mix.png')
ggsave(path, units="in", width=8, height=4, dpi=300)
while (!is.null(dev.list()))  dev.off()